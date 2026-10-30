"""MCP for Primavera P6 skill shop catalog: build the core skills from src/, publish an approved issue, rebuild
index.json, check the whole catalog.

The rules are the app's own: p6mcp.shop.check_shared and p6mcp.skills.check_skill, imported from a checkout
of nizarhamza/p6-mcp at the tag pinned in the workflows (P6MCP_REF, put on PYTHONPATH). Standard library
only, except build: it renders each example report through the golden harness (tools/golden.py), which
runs the app's tools on the demo database of that checkout's test fixtures.

    python tools/catalog.py build      # skills/<name>/ of every src/<name>/ (core skills), index.json
    python tools/catalog.py publish --event "$GITHUB_EVENT_PATH" --out result.json
    python tools/catalog.py index      # rebuild index.json (after removing a skill by hand)
    python tools/catalog.py check      # every skill valid and index.json up to date (exit 1 otherwise)

Core skills (src/<name>/, listed in core.json for the app's first install) are written by the maintainer
and built here; shared skills come from approved issues. The issue body is untrusted text: it is only
parsed as JSON and checked, never run or passed to a shell. There are no built-in skills any more (since
1.9.0): build removes the built-in entries older catalogs listed.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

from p6mcp import shop, skills

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = "Skill"  # label of the issue form's JSON field (id: skill)
MAINTAINER = shop.REPO.split("/")[0]  # author of the core skills
SRC = "src"  # core skill sources: src/<name>/ (see docs/AUTHORING.md)
CORE = "core.json"  # names of the core skills (installed by the app on first start)
OLD_FILE_TEXT = 10000  # reference file limit of the app before 1.10.0 (12,000 since)
REF_FILES = ("reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md",
             "reference/example.md")


class Refused(ValueError):
    """The issue cannot be published (the message goes back to the author)."""


def parse_issue(body: str) -> dict:
    """The skill JSON of an issue made from the share-skill form: the '### Skill' section, code fence or not."""
    m = re.search(rf"^###\s+{SECTION}\s*$(.*?)(?=^###\s|\Z)", body or "", re.M | re.S)
    if not m:
        raise Refused(f"the issue has no '{SECTION}' section: use the Share a P6 skill form")
    text = m.group(1).strip()
    fence = re.match(r"\A```[a-z]*\s*\n(.*?)\n```\s*\Z", text, re.S)
    if fence:
        text = fence.group(1)
    if not text or text == "_No response_":
        raise Refused("the Skill field is empty: paste the text MCP for Primavera P6 copied to the clipboard")
    try:
        item = json.loads(text)
    except ValueError as e:
        raise Refused(f"the Skill field is not valid JSON ({e})") from e
    if not isinstance(item, dict):
        raise Refused("the Skill field must hold one JSON object")
    return item


def _meta_path(root: str, name: str) -> str:
    return os.path.join(root, "skills", name, shop.META)


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _read_meta(root: str, name: str):
    path = _meta_path(root, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_skill(root: str, meta: dict) -> None:
    """skills/<name>/: p6mcp.json (what the app installs) plus SKILL.md (as the app writes it for the clients)
    and the reference files to browse. The folder is rewritten: files of an earlier version that are gone
    are removed."""
    folder = os.path.join(root, "skills", meta["name"])
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    skill = skills.from_config(shop.to_stored(meta))
    for rel, text in skills.skill_files(skill).items():
        _write(os.path.join(folder, *rel.split("/")), text)
    _write(os.path.join(folder, shop.META), json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def publish(event: dict, root: str = ROOT, now: str | None = None) -> dict:
    """Check the skill of an approved issue and write it (new, or a new version by the same author).
    Returns {name, version, commit, message}; raises Refused."""
    issue = event.get("issue") or {}
    author = (issue.get("user") or {}).get("login")
    if not author or not issue.get("number"):
        raise Refused("not an issue event")
    item = parse_issue(issue.get("body") or "")
    errs = shop.check_shared(item)
    if errs:
        raise Refused("; ".join(errs))
    name = item["name"]
    version = 1
    if os.path.isdir(os.path.join(root, SRC, name)):
        raise Refused(f"the name {name!r} is a core skill of the catalog: rename the skill and share it again")
    old = _read_meta(root, name)
    if old is not None:
        if old.get("builtin"):
            raise Refused(f"the name {name!r} is a built-in skill of the app: rename the skill and share it again")
        if old.get("author") != author:
            raise Refused(f"the name {name!r} is already published by @{old.get('author')}: rename the skill "
                          "(Skills page, Edit) and share it again")
        if skills.shared_item(old) == skills.shared_item(item):  # approved again, or shared twice: nothing new
            return {"name": name, "version": old.get("version"), "commit": None, "unchanged": True,
                    "message": f"**{name}** version {old.get('version')} is already published with this content: "
                               "nothing changed."}
        version = int(old.get("version") or 1) + 1
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = shop.meta(item, version=version, author=author, license=shop.LICENSE, issue=issue["number"],
                     published_at=now)
    meta.pop("exported_by", None)
    write_skill(root, meta)
    write_index(root, now)
    return {"name": name, "version": version, "commit": f"Publish {name} v{version} (#{issue['number']})",
            "message": f"Published **{name}** version {version}. MCP for Primavera P6 users see it on the Skill "
                       f"shop page in a few minutes (`skills/{name}`)."}


def core_names(root: str = ROOT) -> list[str]:
    """core.json: the names of the core skills (the app installs them on first start)."""
    path = os.path.join(root, CORE)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list) or not all(isinstance(n, str) for n in data):
        raise ValueError(f"{CORE} must be a list of skill names")
    return data


def text_problems(where: str, text: str) -> list[str]:
    """Skill texts are ASCII without double hyphens (the app's rule for its skills)."""
    errs = []
    if not text.isascii():
        errs.append(f"{where}: not ASCII")
    if "--" in text:
        errs.append(f"{where}: double hyphen")
    return errs


def _tool_params(tool: str):
    """Parameter names of a tool of the app checkout the golden harness runs."""
    import golden
    return golden.demo()["params"].get(tool, ())


def core_item(skill: dict, example: str) -> dict:
    """The shared item of a core skill: template.md with its calls, the 3 source reference files, fields.md
    generated from spec.json and the example report (min_app_version from meta.json)."""
    import golden
    meta = skill["meta"]
    calls = golden.steps_text(skill["spec"], golden.numeric_args(meta), golden.optional_args(meta))
    texts = {"reference/report.md": skill["report"], "reference/checks.md": skill["checks"],
             "reference/spec.json": skill["spec_text"], "reference/fields.md": golden.fields_md(skill),
             "reference/example.md": example}
    return {"name": meta["name"], "title": meta["title"], "description": meta["description"],
            "args": [{"name": a["name"], "description": a["description"], "default": a.get("default")}
                     for a in meta.get("args", [])],
            # stored as the app's Skills page stores a template (settings_logic.clean_skill: no leading or
            # trailing line break), so a restored core skill never reads as edited
            "template": skill["template"].replace(golden.STEPS_MARK, calls)
            .replace(golden.RULES_MARK, golden.WRITE_RULES).strip("\n"),
            "files": [{"path": p, "text": texts[p]} for p in REF_FILES],
            "min_app_version": meta["min_app_version"]}


def build(root: str = ROOT, now: str | None = None) -> dict:
    """skills/<name>/ of every core skill source src/<name>/ (example report rendered by the golden harness),
    a new version only when the content changed; built-in entries of older catalogs removed; index.json
    rewritten when an entry changed. Returns {written, unchanged, removed}; raises ValueError listing every
    problem (nothing is written then)."""
    import golden
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    src = os.path.join(root, SRC)
    names, errs, items = golden.names(src), [], {}
    errs += [f"{CORE}: {n!r} has no src/{n}" for n in core_names(root) if n not in names]
    for name in names:
        skill = golden.load(name, src)
        if skill["meta"].get("name") != name:
            errs.append(f"src/{name}/meta.json: name must be {name!r}")
            continue
        try:
            example = golden.golden(skill)[0]
        except (ValueError, golden.Missing) as e:
            errs.append(str(e))
            continue
        item = core_item(skill, example)
        errs += [f"src/{name}: {e}" for e in skills.check_skill(item, strict=True)]
        texts = [("template.md", item["template"]), ("description", item["description"])]
        texts += [(f["path"], f["text"]) for f in item["files"]]
        errs += [e for p, t in texts for e in text_problems(f"src/{name} {p}", t)]
        big = [f["path"] for f in item["files"] if len(f["text"]) > OLD_FILE_TEXT]
        if big and tuple(int(x) for x in item["min_app_version"].split(".")) < (1, 10, 0):
            errs.append(f"src/{name}: {', '.join(big)} longer than {OLD_FILE_TEXT} characters needs min_app_version "
                        "1.10.0 (older versions refuse it)")
        house = getattr(skills, "house_problems", None)  # 1.9: SKILL.md and files, p6_x(name=) checked
        if house is not None:
            errs += [f"src/{name}: {e}" for e in house(skills.from_config(shop.to_stored(item)), _tool_params)]
        old = _read_meta(root, name)
        if old is not None and not old.get("builtin") and old.get("author") != MAINTAINER:
            errs.append(f"src/{name}: skills/{name} is a shared skill of @{old.get('author')}: rename the core skill")
        items[name] = (item, old)
    if errs:
        raise ValueError("; ".join(errs))
    written, unchanged, removed = [], [], []
    for name, (item, old) in items.items():
        meta = shop.meta(item, author=MAINTAINER, license=shop.LICENSE)
        same = old is not None and not old.get("builtin") and {k: old.get(k) for k in meta} == meta
        if same:
            meta.update(version=old.get("version"), published_at=old.get("published_at"))
        else:
            meta.update(version=int(old.get("version") or 0) + 1 if old is not None else 1, published_at=now)
        write_skill(root, meta)
        (unchanged if same else written).append(name)
    base = os.path.join(root, "skills")
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        old = _read_meta(root, name) if os.path.isfile(_meta_path(root, name)) else None
        if old is not None and old.get("builtin") and name not in items:
            shutil.rmtree(os.path.join(base, name))
            removed.append(name)
    write_index(root, now)
    return {"written": written, "unchanged": unchanged, "removed": removed}


def build_index(root: str = ROOT, now: str | None = None) -> dict:
    entries = []
    core = set(core_names(root))
    base = os.path.join(root, "skills")
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = _meta_path(root, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            raw = fh.read()
        meta = json.loads(raw.decode("utf-8"))
        entry = {k: v for k, v in meta.items() if k not in ("args", "template", "files")}
        if name in core:
            entry["core"] = True
        entry["sha256"] = hashlib.sha256(raw).hexdigest()
        entries.append(entry)
    return {"schema": shop.SCHEMA, "generated_at": now, "skills": entries}


def write_index(root: str = ROOT, now: str | None = None) -> bool:
    """Rewrite index.json when its entries changed (generated_at kept otherwise). True when written."""
    path = os.path.join(root, shop.INDEX)
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new = build_index(root, now)
    try:
        with open(path, encoding="utf-8") as fh:
            if json.load(fh).get("skills") == new["skills"]:
                return False
    except (OSError, ValueError):
        pass
    _write(path, json.dumps(new, indent=2, ensure_ascii=False) + "\n")
    return True


def check(root: str = ROOT) -> list[str]:
    """Problems of the catalog: invalid skills, built-in entries left, a folder name that differs from its
    skill, core.json naming a skill without source or folder, a stale index. (Whether skills/ matches src/ is
    checked by running build and comparing: see .github/workflows/check.yml.)"""
    errs = []
    base = os.path.join(root, "skills")
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = _meta_path(root, name)
        if not os.path.isfile(path):
            errs.append(f"skills/{name}: no {shop.META}")
            continue
        with open(path, encoding="utf-8") as fh:
            meta = json.load(fh)
        if meta.get("builtin"):
            errs.append(f"skills/{name}: a built-in entry (the app has none since 1.9.0): run python "
                        "tools/catalog.py build")
        else:
            errs += [f"skills/{name}: {e}" for e in shop.check_shared(meta)]
        if meta.get("name") != name:
            errs.append(f"skills/{name}: holds the skill {meta.get('name')!r}")
    try:
        core = core_names(root)
    except (OSError, ValueError) as e:
        return errs + [f"{CORE}: {e}"]
    for n in core:
        if not os.path.isdir(os.path.join(root, SRC, n)) or not os.path.isfile(_meta_path(root, n)):
            errs.append(f"{CORE}: {n!r} needs src/{n} and skills/{n} (run python tools/catalog.py build)")
    try:
        with open(os.path.join(root, shop.INDEX), encoding="utf-8") as fh:
            current = json.load(fh)
    except (OSError, ValueError) as e:
        return errs + [f"{shop.INDEX}: {e}"]
    if current.get("skills") != build_index(root)["skills"]:
        errs.append(f"{shop.INDEX} is out of date: run python tools/catalog.py index")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="catalog")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("publish")
    p.add_argument("--event", required=True)
    p.add_argument("--out", required=True)
    sub.add_parser("index")
    sub.add_parser("build")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    if a.cmd == "index":
        write_index()
        return 0
    if a.cmd == "build":
        try:
            res = build()
        except ValueError as e:
            for line in str(e).split("; "):
                print(line, file=sys.stderr)
            return 1
        print(f"written: {', '.join(res['written']) or 'none'}; unchanged: {', '.join(res['unchanged']) or 'none'}; "
              f"removed: {', '.join(res['removed']) or 'none'}")
        return 0
    if a.cmd == "check":
        errs = check()
        for e in errs:
            print(e, file=sys.stderr)
        return 1 if errs else 0
    with open(a.event, encoding="utf-8") as fh:
        event = json.load(fh)
    try:
        res = dict(publish(event), ok=True)
    except Refused as e:
        res = {"ok": False, "message": f"This skill cannot be published yet: {e}. Fix it in the app and share it "
                                       "again (or edit the Skill field of this issue), then ask for a new review."}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh)
    print(res["message"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
