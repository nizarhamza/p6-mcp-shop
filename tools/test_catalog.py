"""Tests of tools/catalog.py (run by check.yml with P6 MCP's checkout on PYTHONPATH)."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import catalog  # noqa: E402
from p6mcp import shop  # noqa: E402

SKILL = {"name": "float-watch", "title": "Float watch", "description": "Activities losing float. Use when asked.",
         "args": [{"name": "project", "description": "Project ID", "default": None}],
         "template": "Run p6_float_analysis(project=\"{project}\") and read reference/limits.md.",
         "files": [{"path": "reference/limits.md", "text": "Near critical: under 10 days."}]}


def event(item, author="planner1", number=7, fence=True, raw=None):
    text = raw if raw is not None else json.dumps(shop.meta(item), indent=2)
    field = f"```json\n{text}\n```" if fence else text
    body = f"### Skill\n\n{field}\n\n### Notes for the reviewer\n\n_No response_\n\n### License\n\n- [X] I wrote it"
    return {"issue": {"number": number, "body": body, "user": {"login": author}}}


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def read(self, *parts):
        with open(os.path.join(self.root, *parts), encoding="utf-8") as fh:
            return fh.read()

    def test_parse_issue(self):
        self.assertEqual(catalog.parse_issue(event(SKILL)["issue"]["body"])["name"], "float-watch")
        self.assertEqual(catalog.parse_issue(event(SKILL, fence=False)["issue"]["body"])["name"], "float-watch")
        for raw, why in (("_No response_", "empty"), ("{not json", "not valid JSON"), ("[1]", "one JSON object")):
            with self.assertRaisesRegex(catalog.Refused, why):
                catalog.parse_issue(event(SKILL, raw=raw)["issue"]["body"])
        with self.assertRaisesRegex(catalog.Refused, "no 'Skill' section"):
            catalog.parse_issue("Hello")

    def test_publish_new_version_and_other_author(self):
        res = catalog.publish(event(SKILL), self.root, now="2026-10-28T10:00:00Z")
        self.assertEqual((res["name"], res["version"], res["commit"]), ("float-watch", 1, "Publish float-watch v1 (#7)"))
        meta = json.loads(self.read("skills", "float-watch", "p6mcp.json"))
        self.assertEqual((meta["author"], meta["issue"], meta["license"]), ("planner1", 7, "Apache-2.0"))
        self.assertTrue(self.read("skills", "float-watch", "SKILL.md").startswith("---\nname: p6-float-watch\n"))
        self.assertEqual(self.read("skills", "float-watch", "reference", "limits.md"), "Near critical: under 10 days.")
        index = json.loads(self.read("index.json"))
        self.assertEqual([e["name"] for e in index["skills"]], ["float-watch"])
        self.assertNotIn("template", index["skills"][0])
        self.assertEqual(catalog.check(self.root), [])

        before = self.read("index.json")
        res = catalog.publish(event(SKILL, number=8), self.root)  # the same content approved again
        self.assertEqual((res["version"], res["commit"], res["unchanged"]), (1, None, True))
        self.assertEqual(self.read("index.json"), before)  # nothing rewritten: nothing to commit

        v2 = dict(SKILL, files=[], description="Newer. Use when asked.")
        res = catalog.publish(event(v2, number=9), self.root)
        self.assertEqual(res["version"], 2)
        self.assertFalse(os.path.exists(os.path.join(self.root, "skills", "float-watch", "reference")))
        with self.assertRaisesRegex(catalog.Refused, "already published by @planner1"):
            catalog.publish(event(SKILL, author="someone"), self.root)
        self.assertEqual(catalog.check(self.root), [])

    def test_refusals_and_check(self):
        os.makedirs(os.path.join(self.root, "src", "float-core"))  # a core skill's source (built by build)
        for bad, why in ((dict(SKILL, template="Use p6_nope."), "unknown tools"),
                         (dict(SKILL, name="float-core"), "core skill of the catalog"),
                         (dict(SKILL, files=[{"path": "run.ps1", "text": "x"}]), "reference file"),
                         (dict(SKILL, name="../escape"), "name")):
            with self.assertRaisesRegex(catalog.Refused, why):
                catalog.publish(event(bad), self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, "skills")))
        catalog.publish(event(SKILL), self.root)
        with open(os.path.join(self.root, "skills", "float-watch", "p6mcp.json"), "a", encoding="utf-8") as fh:
            fh.write(" ")
        self.assertIn("index.json is out of date: run python tools/catalog.py index", catalog.check(self.root))
        catalog.write_index(self.root)
        self.assertEqual(catalog.check(self.root), [])

    def test_builtin_entries_and_core_flags(self):
        catalog.publish(event(SKILL), self.root)
        old = os.path.join(self.root, "skills", "delay-whatif")  # a built-in entry of an older catalog
        os.makedirs(old)
        with open(os.path.join(old, "p6mcp.json"), "w", encoding="utf-8") as fh:
            json.dump({"builtin": True, "name": "delay-whatif"}, fh)
        catalog.write_index(self.root)
        self.assertIn("skills/delay-whatif: a built-in entry (P6 MCP has none since 1.9.0): run python "
                      "tools/catalog.py build", catalog.check(self.root))
        shutil.rmtree(old)
        catalog.write_index(self.root)
        self.assertEqual(catalog.check(self.root), [])
        with open(os.path.join(self.root, "core.json"), "w", encoding="utf-8") as fh:
            json.dump(["float-watch"], fh)  # a core name needs its source
        self.assertIn("core.json: 'float-watch' needs src/float-watch and skills/float-watch (run python "
                      "tools/catalog.py build)", catalog.check(self.root))
        self.assertIn("index.json is out of date: run python tools/catalog.py index", catalog.check(self.root))
        before = self.read("index.json")
        self.assertTrue(catalog.write_index(self.root))
        self.assertTrue(json.loads(self.read("index.json"))["skills"][0]["core"])
        self.assertFalse(catalog.write_index(self.root))  # same entries: generated_at kept, nothing rewritten
        self.assertNotEqual(self.read("index.json"), before)

    def test_main_writes_the_result(self):
        path = os.path.join(self.root, "event.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(event(dict(SKILL, template="Use p6_nope.")), fh)
        out = os.path.join(self.root, "result.json")
        self.assertEqual(catalog.main(["publish", "--event", path, "--out", out]), 1)
        with open(out, encoding="utf-8") as fh:
            res = json.load(fh)
        self.assertFalse(res["ok"])
        self.assertIn("unknown tools p6_nope", res["message"])


if __name__ == "__main__":
    unittest.main()
