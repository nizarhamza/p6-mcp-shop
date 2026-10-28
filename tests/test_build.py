"""catalog.py build on a copy of the catalog: one folder per src skill, a version only when the content
changes, core flags in index.json, built-in entries removed, shared skills kept, nothing written on errors."""

from __future__ import annotations

import hashlib
import json
import os
import shutil

import catalog
import golden
import pytest
from p6mcp import __version__, shop, skills

PILOT = "resource-wbs-summary"
SHARED = {"name": "float-watch", "title": "Float watch", "description": "Activities losing float. Use when asked.",
          "args": [{"name": "project", "description": "Project ID", "default": None}],
          "template": "Run p6_float_analysis(project=\"{project}\").", "files": []}


def event(item, number=7, author="planner1"):
    body = f"### Skill\n\n```json\n{json.dumps(shop.meta(item), indent=2)}\n```\n"
    return {"issue": {"number": number, "body": body, "user": {"login": author}}}


def snapshot(root) -> dict:
    """SHA256 of every file the build writes (skills/ and index.json)."""
    out = {}
    with open(os.path.join(root, "index.json"), "rb") as fh:
        out["index.json"] = hashlib.sha256(fh.read()).hexdigest()
    for base, _dirs, files in os.walk(os.path.join(root, "skills")):
        for f in files:
            path = os.path.join(base, f)
            with open(path, "rb") as fh:
                out[os.path.relpath(path, root)] = hashlib.sha256(fh.read()).hexdigest()
    return out


@pytest.fixture
def root(tmp_path, demo):
    root = tmp_path / "shop"
    shutil.copytree(os.path.join(golden.ROOT, "src", PILOT), root / "src" / PILOT)
    (root / "core.json").write_text(json.dumps([PILOT]), encoding="utf-8")
    old = root / "skills" / "weekly-update-review"  # a built-in entry of an older catalog
    old.mkdir(parents=True)
    (old / "p6mcp.json").write_text(json.dumps({"builtin": True, "name": "weekly-update-review", "version": 1}),
                                    encoding="utf-8")
    return str(root)


def read_json(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return json.load(fh)


def test_build_writes_versions_and_flags(root):
    catalog.publish(event(SHARED), root, now="2026-10-28T10:00:00Z")
    res = catalog.build(root, now="2026-10-28T12:00:00Z")
    assert res == {"written": [PILOT], "unchanged": [], "removed": ["weekly-update-review"]}
    meta = read_json(root, "skills", PILOT, "p6mcp.json")
    assert (meta["version"], meta["author"], meta["published_at"], meta["min_app_version"]) == \
        (1, catalog.MAINTAINER, "2026-10-28T12:00:00Z", "1.9.0")
    assert [f["path"] for f in meta["files"]] == list(catalog.REF_FILES)
    assert meta["tools"] == ["p6_group_summary", "p6_list_projects", "p6_resource_summary"]  # checks.md names one
    assert meta["writes"] is False
    assert "[steps]" not in meta["template"]
    assert 'p6_resource_summary(project="{project}", limit=10)' in meta["template"]
    with open(os.path.join(root, "skills", PILOT, "SKILL.md"), encoding="utf-8") as fh:
        assert fh.read() == skills.skill_md(skills.from_config(meta))
    index = {e["name"]: e for e in read_json(root, "index.json")["skills"]}
    assert sorted(index) == ["float-watch", PILOT]
    assert index[PILOT]["core"] is True and "core" not in index["float-watch"]
    errs = catalog.check(root)  # only the app version, while the P6 MCP checkout is older than 1.9.0
    assert all("needs P6 MCP 1.9.0" in e for e in errs) and (bool(errs) == (shop._version(__version__) < (1, 9, 0)))

    before = snapshot(root)
    res = catalog.build(root, now="2026-10-29T08:00:00Z")  # nothing changed: nothing rewritten
    assert res == {"written": [], "unchanged": [PILOT], "removed": []}
    assert snapshot(root) == before

    with open(os.path.join(root, "src", PILOT, "reference", "checks.md"), "a", encoding="utf-8") as fh:
        fh.write("\n- One more check.\n")
    assert catalog.build(root, now="2026-10-30T08:00:00Z")["written"] == [PILOT]
    meta = read_json(root, "skills", PILOT, "p6mcp.json")
    assert (meta["version"], meta["published_at"]) == (2, "2026-10-30T08:00:00Z")
    entry = next(e for e in read_json(root, "index.json")["skills"] if e["name"] == PILOT)
    assert entry["version"] == 2 and entry["core"] is True

    with pytest.raises(catalog.Refused, match="core skill of the catalog"):
        catalog.publish(event(dict(SHARED, name=PILOT), number=9), root)


def test_build_refuses_and_writes_nothing(root):
    catalog.build(root, now="2026-10-28T12:00:00Z")
    before = snapshot(root)
    spec_path = os.path.join(root, "src", PILOT, "reference", "spec.json")
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    spec["slots"]["data_date"]["path"] = "schedule_state.data_day"  # a field the tool does not return
    with open(spec_path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh)
    with pytest.raises(ValueError, match="no field 'schedule_state.data_day'"):
        catalog.build(root)
    with open(os.path.join(root, "src", PILOT, "template.md"), "a", encoding="utf-8") as fh:
        fh.write("x" * skills.MAX_TEXT + "\nNo -- here.\n")
    with pytest.raises(ValueError) as e:
        catalog.build(root)
    assert "no field" in str(e.value)  # every problem is listed
    spec["slots"]["data_date"]["path"] = "schedule_state.data_date"
    with open(spec_path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh)
    with pytest.raises(ValueError) as e:
        catalog.build(root)
    assert f"longer than {skills.MAX_TEXT} characters" in str(e.value) and "double hyphen" in str(e.value)
    assert snapshot(root) == before

    with open(os.path.join(root, "core.json"), "w", encoding="utf-8") as fh:
        json.dump([PILOT, "milestone-tracker"], fh)
    with pytest.raises(ValueError, match="'milestone-tracker' has no src/milestone-tracker"):
        catalog.build(root)


def test_a_core_name_held_by_another_author(root):
    item = dict(SHARED, name=PILOT)
    os.rename(os.path.join(root, "src", PILOT), os.path.join(root, "hold"))
    catalog.publish(event(item), root)  # published by someone else before the core skill existed
    os.rename(os.path.join(root, "hold"), os.path.join(root, "src", PILOT))
    with pytest.raises(ValueError, match="shared skill of @planner1"):
        catalog.build(root)
