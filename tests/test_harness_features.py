"""Harness features the core skills rely on (docs/AUTHORING.md): empty arguments left out (H1), nested
arguments (H2), {work} (H3), optional steps (H4), dict tables (H5), scalar rows (H6), {=step.path} arguments
(H7), skills without a project (H8), write tools as dry runs only (H9), no state between skills (H10), [if:]
on numbers (H11), steps made only when an optional argument is given (H12)."""

from __future__ import annotations

import copy
import hashlib
import json
import os

import golden
import pytest
from oracles import Oracle

META = {"name": "x", "title": "X", "args": [{"name": "project", "description": "P"},
                                             {"name": "baseline", "description": "B", "default": ""},
                                             {"name": "task_code", "description": "A"},
                                             {"name": "delay_days", "description": "D", "default": "10"}]}


def skill(spec, report, meta=META):
    return {"name": "x", "meta": copy.deepcopy(meta), "template": "Run:\n[steps]\n\n[rules]\n", "report": report,
            "checks": "", "spec": copy.deepcopy(spec), "spec_text": json.dumps(spec)}


def fake(results: dict, errors: dict | None = None):
    """A call(tool, **kw) that returns results[tool] (and records the calls), or raises errors[tool]."""
    calls = []

    def call(tool, **kw):
        calls.append((tool, kw))
        if errors and tool in errors:
            raise errors[tool]
        return copy.deepcopy(results[tool])
    return call, calls


def test_h1_h2_empty_and_nested_arguments():
    step = {"id": "wi", "tool": "p6_schedule_whatif",
            "args": {"project": "{project}", "baseline": "{baseline}",
                     "edits": [{"op": "duration", "task_code": "{task_code}", "add_remaining_days": "{delay_days}",
                                "note": "{baseline}"}]}}
    args = {"project": "P", "baseline": "", "task_code": "A1", "delay_days": "10"}
    assert golden.call_args(step, args, golden.numeric_args(META)) == \
        {"project": "P", "edits": [{"op": "duration", "task_code": "A1", "add_remaining_days": 10}]}
    text = golden.steps_text({"steps": [step]}, golden.numeric_args(META), golden.optional_args(META))
    assert text == ('1. wi = p6_schedule_whatif(project="{project}", baseline="{baseline}", edits=[{"op": "duration", '
                    '"task_code": "{task_code}", "add_remaining_days": {delay_days}, "note": "{baseline}"}]).\n'
                    "Leave out an argument whose value is empty (baseline).")
    bad = copy.deepcopy(step)
    bad["args"]["edits"][0]["x"] = "{nope}"
    errs = golden.problems(skill({"spec": 1, "steps": [bad]}, "Run.\n"))
    assert "step wi: {nope} is not an argument of the skill" in errs


def test_h3_work_folder(demo):
    s = skill({"spec": 1, "steps": []}, "", dict(META, example_args={"path": "{work}/DEMO-SS225.xlsx"}))
    path = golden.example_args(s)["path"]
    assert path == os.path.join(demo["work"], "DEMO-SS225.xlsx")
    assert golden.mask(f"File {path} written.") == f"File {golden.WORK_SHOWN}\\DEMO-SS225.xlsx written."


SPEC = {"spec": 1,
        "steps": [{"id": "a", "tool": "t_a", "args": {"project": "{project}"}},
                  {"id": "cmp", "tool": "t_cmp", "args": {"project": "{project}", "limit": 5}, "optional": True},
                  {"id": "drv", "tool": "t_drv", "args": {"target": "{=a.rows.0.code}"}}],
        "slots": {"dd": {"step": "a", "path": "dd", "format": "date", "meaning": "m"},
                  "a_error": {"step": "a", "path": "error", "format": "text", "meaning": "m"},
                  "cmp_error": {"step": "cmp", "path": "error", "format": "text", "meaning": "m"},
                  "cmp_n": {"step": "cmp", "path": "summary.n", "format": "int", "meaning": "m"},
                  "drv_error": {"step": "drv", "path": "error", "format": "text", "meaning": "m"},
                  "n": {"step": "a", "path": "n", "format": "int", "meaning": "m"}},
        "tables": {"counts": {"step": "a", "rows": "counts", "cap": 2, "noun": "tables", "empty": "None.",
                              "columns": [{"key": "t", "head": "Table", "path": "_key", "format": "text"},
                                          {"key": "i", "head": "Inserted", "path": "inserted", "format": "int"}]},
                   "causes": {"step": "a", "rows": "causes", "cap": 5, "noun": "causes", "empty": "None.",
                              "columns": [{"key": "c", "head": "Cause", "path": "_key", "format": "text"},
                                          {"key": "n", "head": "Activities", "path": "_value", "format": "int"}]},
                   "warn": {"step": "a", "rows": "warnings", "cap": 5, "noun": "warnings", "empty": "No warning.",
                            "columns": [{"key": "w", "head": "Warning", "path": "", "format": "text"}]},
                   "slipped": {"step": "cmp", "rows": "rows", "cap": 5, "noun": "activities", "empty": "No slip.",
                               "columns": [{"key": "c", "head": "Activity", "path": "code", "format": "text"}]}}}
REPORT = """DD {dd}, n {n}.
[if: n]
Some.
[end if]
[if: cmp_error]
No baseline: {cmp_error}
[end if]
[if not: a_error]
A ran.
[end if]
[if: drv_error]
Drivers skipped.
[end if]
Compared {cmp_n}.
[table: counts]
[table: causes]
[table: warn]
[table: slipped]
"""
A = {"dd": "2026-10-26 08:00:00", "n": 0, "rows": [{"code": None}],
     "counts": {"TASK": {"inserted": 3}, "TASKPRED": {"inserted": 0}, "TASKRSRC": {"inserted": 1}},
     "causes": {"late_start": 4, "on_time": 0}, "warnings": ["first", "second"]}


def test_h4_to_h7_and_h11_optional_steps_dict_tables_scalar_rows_references_numbers():
    s = skill(SPEC, REPORT)
    assert golden.problems(s) == []
    call, calls = fake({"t_a": A}, {"t_cmp": ValueError("DEMO has no baseline")})
    res = golden.run_steps(s["spec"], {"project": "DEMO"}, call)
    assert [c[0] for c in calls] == ["t_a", "t_cmp"]  # drv skipped: a.rows.0.code is null
    assert res["cmp"] == {"error": "DEMO has no baseline", "_failed": True} and res["drv"]["_failed"]
    raw = golden.slot_values(s["spec"], res)
    assert (raw["cmp_error"], raw["cmp_n"], raw["a_error"], raw["n"]) == ("DEMO has no baseline", None, None, 0)
    assert golden.table_rows(s["spec"], res)["slipped"] == []
    out = golden.render(s, res, {"project": "DEMO"})
    assert out == ("DD 2026-10-26, n 0.\nNo baseline: DEMO has no baseline\nA ran.\nDrivers skipped.\nCompared n/a.\n"
                   "| Table | Inserted |\n|-|-|\n| TASK | 3 |\n| TASKPRED | 0 |\n\nOnly the first 2 tables are shown.\n"
                   "| Cause | Activities |\n|-|-|\n| late_start | 4 |\n| on_time | 0 |\n"
                   "| Warning |\n|-|\n| first |\n| second |\n")
    a = dict(A, n=3, rows=[{"code": "A1"}])  # H11: a number other than 0 is true; H7: the field is passed on
    call, calls = fake({"t_a": a, "t_cmp": {"summary": {"n": 7}, "rows": [], "next_offset": None},
                        "t_drv": {"rows": []}})
    res = golden.run_steps(s["spec"], {"project": "DEMO"}, call)
    assert calls[2] == ("t_drv", {"target": "A1"})
    out = golden.render(s, res, {"project": "DEMO"})
    assert "Some." in out and "No baseline" not in out and "Compared 7." in out and "No slip." in out
    with pytest.raises(ValueError, match="boom"):  # a call that is not optional fails the run
        golden.run_steps(s["spec"], {"project": "DEMO"}, fake({}, {"t_a": ValueError("boom")})[0])
    text = golden.steps_text(s["spec"])
    assert '3. drv = t_drv(target=<a.rows.0.code>). <a.rows.0.code> is the field rows.0.code of the result of a' in text
    assert "{=" not in text
    assert any("a brace that is not an argument" in e for e in golden.problems(dict(s, template="[steps] {slot}")))
    bad = copy.deepcopy(SPEC)
    bad["steps"][0]["args"]["x"] = "{=drv.rows.0.code}"
    assert "step a: {=drv...} must name an earlier step" in golden.problems(skill(bad, REPORT))
    assert [golden.truthy(v) for v in (0, 0.0, None, "", [], 3, -1.5, "x", [0], True)] == \
        [False] * 5 + [True] * 5


def test_id_name_slot():
    spec = {"spec": 1, "steps": [{"id": "a", "tool": "t", "args": {}}, {"id": "b", "tool": "t", "args": {},
                                                                       "optional": True}],
            "slots": {"act": {"step": "a", "path": ["act.code", "act.name"], "format": "id_name", "meaning": "m"},
                      "other": {"step": "b", "path": ["act.code", "act.name"], "format": "id_name", "meaning": "m"}}}
    s = skill(spec, "{act}; {other}\n", {"name": "x", "title": "X", "args": []})
    assert golden.problems(s) == []
    res = {"a": {"act": {"code": "A1", "name": "Dig"}}, "b": {"error": "no", "_failed": True}}
    assert golden.slot_values(spec, res) == {"act": ("A1", "Dig"), "other": (None, None)}
    assert golden.render(s, res, {}) == "A1 - Dig; n/a\n"
    assert golden.truthy(("A1", None)) and not golden.truthy((None, None))  # [if:] on an id_name slot


def test_unchecked_slot_and_table(demo, rendered, monkeypatch):
    import oracles
    from oracles import Unchecked, compare
    name = "resource-wbs-summary"
    skill, _text, results, raw, args = rendered[name]
    mod = oracles.module(name)
    monkeypatch.setitem(mod.SLOTS, "resources", lambda o: Unchecked("not modelled"))
    monkeypatch.setitem(mod.TABLES, "wbs", lambda o: Unchecked("not modelled"))
    monkeypatch.setitem(mod.TABLES, "status", lambda o: [])  # a real difference is still reported
    bad = compare(name, skill, results, raw, args, demo)
    assert bad == [f"table status: {len(golden.table_rows(skill['spec'], results)['status'])} rows, oracle 0"]
    assert "not modelled" in oracles.UNCHECKED


def test_h8_oracle_without_a_project(demo):
    o = Oracle(demo["db"], demo["work"], {"eps": ""})
    try:
        assert o.pid is None and o.one("SELECT COUNT(*) FROM PROJECT") > 0
    finally:
        o.close()


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_h9_a_write_tool_runs_as_a_dry_run_and_its_token_is_never_shown(demo):
    before = sha(demo["db"])
    xer = os.path.join(demo["work"], "DEMO-SS225.xer")
    res = demo["call"]("p6_import_xer", path=xer, mode="update", project="DEMO-SS225")
    assert res["dry_run"] is True and res.get("confirmation_token")
    assert sha(demo["db"]) == before  # nothing written, nothing locked for good
    spec = {"spec": 1, "steps": [{"id": "dry", "tool": "p6_import_xer",
                                  "args": {"path": "{xer}", "mode": "update", "dry_run": False}}],
            "slots": {"tok": {"step": "dry", "path": "confirmation_token", "format": "text", "meaning": "m"},
                      "nxt": {"step": "dry", "path": "next", "format": "text", "meaning": "m"}}}
    meta = {"name": "x", "title": "X", "args": [{"name": "xer", "description": "X"}]}
    errs = golden.problems(skill(spec, "{tok} {nxt}\n", meta))
    assert "step dry: dry_run is never passed (write tools run as dry runs only)" in errs
    assert "slot tok: never show confirmation_token of a write dry run" in errs
    assert "slot nxt: never show next of a write dry run" in errs


def test_h10_no_state_left_between_skills(demo):
    health = os.path.join(demo["work"], "editlog", "health")
    os.makedirs(health, exist_ok=True)
    for path in (os.path.join(health, "snap.json"), os.path.join(demo["work"], "old.xlsx")):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{}")
    golden.reset_outputs()
    assert not os.path.exists(health) and not os.path.exists(os.path.join(demo["work"], "old.xlsx"))
    assert demo["keep"] <= set(os.listdir(demo["work"]))


def test_h12_a_step_only_when_its_argument_is_given():
    meta = {"name": "x", "title": "X", "args": [{"name": "project", "description": "P"},
                                                 {"name": "previous", "description": "Q", "default": ""}]}
    spec = {"spec": 1, "steps": [{"id": "a", "tool": "t_a", "args": {"project": "{project}"}},
                                 {"id": "prev", "tool": "t_cmp", "args": {"project": "{project}",
                                                                          "other": "{previous}"}, "when": "previous"}],
            "slots": {"n": {"step": "prev", "path": "summary.n", "format": "int", "meaning": "m"}}}
    report = "[if: n]\nSince {previous}: {n}.\n[end if]\nEnd.\n"
    s = skill(spec, report, meta)
    assert golden.problems(s) == []
    call, calls = fake({"t_a": {}, "t_cmp": {"summary": {"n": 4}}})
    res = golden.run_steps(spec, {"project": "P", "previous": ""}, call)
    assert [c[0] for c in calls] == ["t_a"] and res["prev"] == {"error": "skipped: previous is empty", "_failed": True}
    assert golden.render(s, res, {"project": "P", "previous": ""}) == "End.\n"  # the report without the argument
    res = golden.run_steps(spec, {"project": "P", "previous": "P0"}, call)
    assert calls[-1] == ("t_cmp", {"project": "P", "other": "P0"})
    assert golden.render(s, res, {"project": "P", "previous": "P0"}) == "Since P0: 4.\nEnd.\n"
    text = golden.steps_text(spec, set(), golden.optional_args(meta))
    assert "Make this call only when <previous> is given; when it is empty, skip it (its fields are null)" in text
    bad = copy.deepcopy(spec)
    bad["steps"][1]["when"] = "project"
    assert "step prev: when must name an optional argument (default \"\") of the skill" in golden.problems(
        skill(bad, report, meta))
