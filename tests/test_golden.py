"""The golden harness: spec checks, formats, rendering rules, and skills/ up to date with src/ (the committed
example.md is the harness rendering on the demo project)."""

from __future__ import annotations

import copy
import json
import os

import catalog
import golden
import pytest
from p6mcp import skills

ROOT = golden.ROOT


@pytest.mark.parametrize("name", golden.names())
def test_source_has_no_problem(name, demo):
    assert golden.problems(golden.load(name), demo["params"]) == []


@pytest.mark.parametrize("name", golden.names())
def test_skills_folder_is_the_build_of_src(name, rendered):
    """skills/<name> holds what build writes: same template, same reference files, example.md = rendering."""
    skill, text, _results, _raw, _args = rendered[name]
    with open(os.path.join(ROOT, "skills", name, "p6mcp.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    item = catalog.core_item(skill, text)
    assert meta["template"] == item["template"], "template.md changed: run python tools/catalog.py build"
    assert meta["files"] == item["files"], "a reference file changed: run python tools/catalog.py build"
    with open(os.path.join(ROOT, "skills", name, "reference", "example.md"), encoding="utf-8") as fh:
        assert fh.read() == text
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as fh:
        assert fh.read() == skills.skill_md(skills.from_config(meta))
    assert skills.check_skill(item, strict=True) == []
    assert len(item["template"]) <= skills.MAX_TEXT and len(item["files"]) <= skills.MAX_FILES


def test_formats():
    f = golden.fmt
    assert f(12345.65, "n1") == "12,345.7" and f(0.05, "n1") == "0.1" and f(2.5, "n0") == "3"  # halves up
    assert f(-0.04, "n1") == "0.0" and f(-36.0, "n1") == "-36.0" and f(1234567.891, "n2") == "1,234,567.89"
    assert f(49.6677, "pct1") == "49.7%" and f(None, "pct1") == "n/a" and f(None, "n1", "none") == "none"
    assert f("2026-10-26 08:00:00", "date") == "2026-10-26"
    assert f("2026-10-26 17:30:00", "datetime") == "2026-10-26 17:30"
    assert f(("A1000", "Excavation"), "id_name") == "A1000 - Excavation" and f(("A1000", None), "id_name") == "A1000"
    assert f(True, "flag") == "yes" and f(214, "int") == "214" and f(3.0, "int") == "3" and f(1227, "int") == "1,227"
    assert f(-104274.95, "n1") == "-104,275.0" and f(-0.05, "n1") == "-0.1"  # halves away from zero
    with pytest.raises(ValueError):
        f(2.5, "int")
    with pytest.raises(ValueError):
        f(1, "flag")
    assert f(["in_progress", "finishing"], "list") == "in_progress, finishing" and f([], "list") == "n/a"
    with pytest.raises(ValueError, match="needs the list format"):
        f(["a"], "text")


SPEC = {
    "spec": 1,
    "steps": [{"id": "a", "tool": "p6_x", "args": {"project": "{project}", "limit": 2}}],
    "slots": {"dd": {"step": "a", "path": "info.dd", "format": "date", "meaning": "data date"},
              "late": {"step": "a", "path": "info.late", "format": "flag", "meaning": "late"},
              "first": {"step": "a", "path": "rows.0.code", "format": "text", "meaning": "first code"}},
    "tables": {"t": {"step": "a", "rows": "rows", "cap": 2, "noun": "rows", "empty": "Nothing.",
                     "totals": {"path": "tot", "label": "Total"},
                     "columns": [{"key": "act", "head": "Activity", "path": ["code", "name"], "format": "id_name"},
                                 {"key": "d", "head": "Float (d)", "path": "tf", "format": "n1", "unit": "d"},
                                 {"key": "n", "head": "Note", "path": "note", "format": "text", "in_totals": False}]}},
}
REPORT = ("# {project}\n\nDD {dd}, first {first}.\n\n[if: late]\nLate!\n[end if]\n[if not: late]\nOn time.\n"
          "[end if]\n\n[table: t]\n")
RESULT = {"info": {"dd": "2026-10-26 08:00:00", "late": False}, "total": 5, "returned": 2, "next_offset": 2,
          "rows": [{"code": "A1", "name": "One", "tf": -1.25, "note": None},
                   {"code": "A2", "name": "Two", "tf": 3, "note": "x|y"}], "tot": {"tf": -1.25}}


def skill(spec=SPEC, report=REPORT):
    return {"name": "x", "meta": {"name": "x", "title": "X", "args": [{"name": "project", "description": "P"}]},
            "template": "Run:\n[steps]\n\n[rules]\n", "report": report, "checks": "", "spec": copy.deepcopy(spec),
            "spec_text": json.dumps(spec)}


def test_render_slots_blocks_tables_and_more_line():
    out = golden.render(skill(), {"a": RESULT}, {"project": "DEMO"})
    assert out == ("# DEMO\n\nDD 2026-10-26, first A1.\n\nOn time.\n\n| Activity | Float (d) | Note |\n|-|-|-|\n"
                   "| A1 - One | -1.3 | n/a |\n| A2 - Two | 3.0 | x/y |\n| Total | -1.3 |  |\n\n"
                   "Showing the first 2 of 5 rows.\n")
    last = dict(RESULT, next_offset=None, rows=[], info={"dd": None, "late": True})
    out = golden.render(skill(dict(SPEC, slots={k: v for k, v in SPEC["slots"].items() if k != "first"}),
                              REPORT.replace(", first {first}", "")), {"a": last}, {"project": "DEMO"})
    assert "DD n/a." in out and "Late!" in out and "On time" not in out and "Nothing." in out and "Showing" not in out


def test_a_missing_field_fails():
    bad = copy.deepcopy(SPEC)
    bad["slots"]["dd"]["path"] = "info.data_date"
    with pytest.raises(golden.Missing, match="info.data_date"):
        golden.render(skill(bad), {"a": RESULT}, {"project": "DEMO"})
    bad = copy.deepcopy(SPEC)
    bad["tables"]["t"]["columns"][1]["path"] = "total_float"
    with pytest.raises(golden.Missing, match="total_float"):
        golden.table_rows(bad, {"a": RESULT})
    assert golden.get({"suggestion": None}, "suggestion.reason") is None  # under a null field: null
    some = dict(RESULT, rows=[{"code": "A1", "name": "One", "note": None}, RESULT["rows"][1]])
    assert [r["d"] for r in golden.table_rows(SPEC, {"a": some})["t"]] == [None, 3, -1.25]  # one row has tf


def test_problems_found():
    assert golden.problems(skill(), {"p6_x": {"project", "limit"}}) == []
    bad = copy.deepcopy(SPEC)
    bad["steps"][0]["args"].update(weeks="{weeks}", limit=3)
    bad["slots"]["unused"] = {"step": "b", "path": "x", "format": "pct", "meaning": "m"}
    bad["tables"]["t"]["columns"][1]["head"] = "Float"
    report = REPORT.replace("{dd}", "{dd} {nope}").replace("[end if]\n[if not", "[if not")
    errs = golden.problems(skill(bad, report), {"p6_x": {"project"}})
    for part in ("p6_x has no parameter 'limit'", "{weeks} is not an argument", "slot unused: unknown step 'b'",
                 "format 'pct'", "cap 2 must equal the limit", "must end with (d)", "{nope} is not a slot",
                 "[if] blocks do not nest", "slot unused is not used"):
        assert any(part in e for e in errs), (part, errs)


def test_cross_checks():
    spec = dict(SPEC, checks=[{"equal": ["a.info.dd", "b.info.dd"], "text": "same data date"}])
    res = {"a": RESULT, "b": {"info": {"dd": "2026-10-19 08:00:00"}}}
    assert golden.check_results(spec, res) == [
        "check failed: same data date (a.info.dd='2026-10-26 08:00:00', b.info.dd='2026-10-19 08:00:00')"]
    assert golden.check_results(spec, {"a": RESULT, "b": RESULT}) == []


def test_write_rules_are_one_shared_text():
    rules = golden.WRITE_RULES
    assert rules.isascii() and "--" not in rules and "{" not in rules and "Showing the first" in rules
    s = skill()
    assert not any("[rules]" in e for e in golden.problems(s))
    assert any("[rules] once" in e for e in golden.problems(dict(s, template="Run:\n[steps]\n")))


def test_steps_text():
    spec = {"steps": [{"id": "a", "tool": "p6_x", "args": {"project": "{project}", "weeks": "{weeks}", "limit": 5,
                                                          "include_completed": False}, "why": "w"}]}
    assert golden.steps_text(spec, {"weeks"}) == \
        '1. a = p6_x(project="{project}", weeks={weeks}, limit=5, include_completed=false): w.'
    assert golden.call_args(spec["steps"][0], {"project": "P", "weeks": "3"}, {"weeks"}) == \
        {"project": "P", "weeks": 3, "limit": 5, "include_completed": False}
