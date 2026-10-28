"""P6 MCP skill shop catalog: publish an approved issue, rebuild index.json, check the whole catalog.

The rules are P6 MCP's own: p6mcp.shop.check_shared, imported from a checkout of nizarhamza/p6-mcp at the
tag pinned in the workflows (P6MCP_REF, put on PYTHONPATH). Standard library only.

    python tools/catalog.py publish --event "$GITHUB_EVENT_PATH" --out result.json
    python tools/catalog.py index      # rebuild index.json (after removing a skill by hand)
    python tools/catalog.py builtins   # write the built-in skills of that P6 MCP (after bumping P6MCP_REF)
    python tools/catalog.py check      # every skill valid and index.json up to date (exit 1 otherwise)

The issue body is untrusted text: it is only parsed as JSON and checked, never run or passed to a shell.
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
MAINTAINER = shop.REPO.split("/")[0]  # author of the built-in skills


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
        raise Refused("the Skill field is empty: paste the text P6 MCP copied to the clipboard")
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
    """skills/<name>/: p6mcp.json (what P6 MCP installs) plus SKILL.md and the reference files to browse
    (a built-in skill: SKILL.md as P6 MCP writes it for the clients). The folder is rewritten: files of an
    earlier version that are gone are removed."""
    folder = os.path.join(root, "skills", meta["name"])
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    skill = skills.BY_NAME[meta["name"]] if meta.get("builtin") else skills.from_config(shop.to_stored(meta))
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
    old = _read_meta(root, name)
    if old is not None:
        if old.get("builtin"):
            raise Refused(f"the name {name!r} is a built-in skill of P6 MCP: rename the skill and share it again")
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
            "message": f"Published **{name}** version {version}. P6 MCP users see it on the Skill shop page in a "
                       f"few minutes (`skills/{name}`)."}


def write_builtins(root: str = ROOT, now: str | None = None) -> dict:
    """skills/<name>/ of every built-in skill of the P6 MCP on PYTHONPATH (flag builtin: P6 MCP lists it and
    never installs it), a new version when its definition changed; built-in folders that release no longer
    has are removed. Returns {written, removed}; index.json is rebuilt when anything changed."""
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    written, removed = [], []
    for skill in skills.BUILTIN:
        meta = shop.builtin_meta(skill)
        old = _read_meta(root, skill.name)
        if old is not None and not old.get("builtin"):
            raise Refused(f"skills/{skill.name} holds a shared skill, not the built-in one")
        if old is not None and {k: old.get(k) for k in meta} == meta:
            continue
        meta.update(version=int(old.get("version") or 1) + 1 if old else 1, author=MAINTAINER,
                    license=shop.LICENSE, published_at=now)
        write_skill(root, meta)
        written.append(skill.name)
    base = os.path.join(root, "skills")
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        old = _read_meta(root, name) if os.path.isfile(_meta_path(root, name)) else None
        if old is not None and old.get("builtin") and name not in skills.BY_NAME:
            shutil.rmtree(os.path.join(base, name))
            removed.append(name)
    if written or removed:
        write_index(root, now)
    return {"written": written, "removed": removed}


def build_index(root: str = ROOT, now: str | None = None) -> dict:
    entries = []
    base = os.path.join(root, "skills")
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = _meta_path(root, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            raw = fh.read()
        meta = json.loads(raw.decode("utf-8"))
        entry = {k: v for k, v in meta.items() if k not in ("args", "template", "files")}
        entry["sha256"] = hashlib.sha256(raw).hexdigest()
        entries.append(entry)
    return {"schema": shop.SCHEMA, "generated_at": now, "skills": entries}


def write_index(root: str = ROOT, now: str | None = None) -> None:
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write(os.path.join(root, shop.INDEX), json.dumps(build_index(root, now), indent=2, ensure_ascii=False) + "\n")


def check(root: str = ROOT) -> list[str]:
    """Problems of the catalog: invalid skills, built-in skills that differ from the P6 MCP release, a folder
    name that differs from its skill, a stale index."""
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
            errs += [f"skills/{name}: {e} (run python tools/catalog.py builtins)" for e in shop.check_builtin(meta)]
        else:
            errs += [f"skills/{name}: {e}" for e in shop.check_shared(meta)]
        if meta.get("name") != name:
            errs.append(f"skills/{name}: holds the skill {meta.get('name')!r}")
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
    sub.add_parser("builtins")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    if a.cmd == "index":
        write_index()
        return 0
    if a.cmd == "builtins":
        res = write_builtins()
        print(f"written: {', '.join(res['written']) or 'none'}; removed: {', '.join(res['removed']) or 'none'}")
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
        res = {"ok": False, "message": f"This skill cannot be published yet: {e}. Fix it in P6 MCP and share it "
                                       "again (or edit the Skill field of this issue), then ask for a new review."}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh)
    print(res["message"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
