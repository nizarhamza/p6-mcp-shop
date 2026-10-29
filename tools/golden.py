"""Golden harness of the catalog's core skills (src/<name>/): run the calls of reference/spec.json through
P6 MCP's own tools on the public demo database, resolve every slot and table, render reference/report.md.

The rendering is what the skill asks the model to write, figure for figure; the catalog build saves it as
reference/example.md and the tests compare every slot and table cell with an independent oracle
(tests/oracles). Needs a P6 MCP checkout on PYTHONPATH with its test fixtures (tests/fixtures/make_demo.py
builds the demo database; P6MCP_SRC names the checkout when p6mcp is installed elsewhere) and its
dependencies installed. The server is pointed at a throwaway config and database: never at the user's
settings. Write tools only run as dry runs (the database file stays byte-identical).

    python tools/golden.py render <name>    # print the rendering of src/<name> on the demo project
    python tools/golden.py verify <name>    # render, limits, house rules and the oracles of one skill
    python tools/golden.py check            # every example.md equal to its rendering (exit 1 otherwise)

spec.json (the format is documented in docs/AUTHORING.md):
    steps   [{id, tool, args, why, optional, when}]: args (nested lists and dicts too) may hold {arg} (a skill
            argument; an empty one is left out) and {=step.path} (a field of an earlier result; a null one
            skips the step); optional: an error of the call is kept as {error}, its slots are null; when:
            an optional argument (default "") that must be given, else the step is skipped
    slots   {name: {step, path, format, unit, none, meaning}}: path = dotted keys (and list indexes)
    tables  {name: {step, rows, cap, noun, empty, filter, totals, meaning, columns [{key, head, path, format,
            unit, none, in_totals}]}}: rows names a list (or a dict: one row per item, its key in _key, a
            plain value in _value); a column path "" is the row itself (lists of texts)
    checks  [{equal: ["step.path", ...], text}]
report.md: {slot} and {arg} placeholders, a line [table: name], blocks [if: slot] ... [end if] and
[if not: slot] ... [end if] (kept when the slot's value is true, resp. false: true, a number other than 0,
a text or list that is not empty).
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
from decimal import ROUND_HALF_UP, Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
SPEC_VERSION = 1
WORK_SHOWN = "C:\\P6\\demo"  # the harness work folder as example.md shows it ({work} of example_args)

FORMATS = {
    "text": "the value as returned",
    "int": "the whole number, a comma between thousands: 1,227",
    "date": "the first 10 characters: YYYY-MM-DD",
    "datetime": "the first 16 characters: YYYY-MM-DD HH:MM",
    "n0": "the number as written in the result rounded to a whole number, halves away from zero, a comma between "
          "thousands: 12,345",
    "n1": "the same to 1 decimal: 12,345.6 (-104274.95 gives -104,275.0)",
    "n2": "the same to 2 decimals: 12,345.67",
    "pct1": "the same to 1 decimal, then %: 49.7%",
    "flag": "yes for true, no for false",
    "id_name": "the two fields joined: ID - Name (the ID alone when the name is null, the none text when the ID is "
               "null)",
    "list": "the items of the list in their order, joined by a comma and a space: in_progress, finishing",
}
# unit -> what it means; the column heads of the time units end with "(<unit>)"
UNITS = {
    "wd": "working days of each activity's calendar", "wd proj": "working days of the project calendar",
    "cd": "calendar days", "d": "days of each activity's calendar (hours / hours per day)", "h": "hours",
    "qty": "resource units: hours for labor and nonlabor, the material's own unit for material",
    "cost": "cost in the database currency", "%": "percent", "count": "a count",
}
HEAD_UNITS = ("wd", "wd proj", "cd", "d", "h")
NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SLOT_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")
ARG_ONLY = re.compile(r"\{([a-z][a-z0-9_]*)\}")
REF_ONLY = re.compile(r"\{=([a-z][a-z0-9_]*)\.([A-Za-z0-9_.]+)\}")
TABLE_RE = re.compile(r"^\[table: ([a-z][a-z0-9_]*)\]$")
IF_RE = re.compile(r"^\[if( not)?: ([a-z][a-z0-9_]*)\]$")
END_IF = "[end if]"
STEPS_MARK = "[steps]"
RULES_MARK = "[rules]"  # template.md: the writing rules every core skill shares (WRITE_RULES)
WRITE_RULES = """Write the report:
1. Start from reference/report.md. Replace each slot placeholder (a slot name in curly braces) by the field
   named in spec.json slots (call and path), written in the slot's format (reference/fields.md). An argument
   written <name> in these instructions is the placeholder of that name in curly braces in report.md and
   checks.md: the value given (an empty optional argument is left out of the calls).
2. Replace each line [table: name] by that table: one row per item of its list, in the order returned, at
   most its cap, every cell in its column's format, the heads as in spec.json. A table with a totals entry
   ends with its Total row, taken from the totals of its call, never from adding the rows. Only a table
   built from the rows list of its call ends, when that call has more pages (next_offset not null), with
   the line "Showing the first <returned> of <total> <noun>." (returned and total of that call). A table
   built from another list or dict of the call (weeks, paths, roots, causes, counts...) ends with "Only the
   first <cap> <noun> are shown." when that list is longer than the cap, and never with a Showing line. An
   empty list gives the table's empty text; a call that failed or was skipped gives no table.
3. Keep the lines between [if: slot] and [end if] only when the slot is true (true, a number other than 0,
   a text or list that is not empty, an ID - name whose ID is not null), the lines between [if not: slot]
   and [end if] only when it is not; remove the markers.
4. Numbers: take the number as written in the result and round it, halves away from zero, to the decimals
   of its format (-104274.95 in n1 is -104,275.0); whole numbers and counts take a comma between thousands
   (1,227), also in the Showing lines. A null value is written as the slot's or column's none text, and so
   is an ID - name whose ID is null.
5. Never add, subtract, divide, count rows or match rows of two results: a figure that is not a slot or a
   table cell is left out. Ignore the note fields of the tools unless a slot names them.
6. Write the headings and sentences in the user's language; keep values, IDs, names and number formats
   exactly as formatted.
7. Run reference/checks.md before answering. Report a failed cross-check, never hide it; say nothing about
   the checks that pass."""
STEP_KEYS = {"id", "tool", "args", "why", "optional", "when"}
SLOT_KEYS = {"step", "path", "format", "unit", "none", "meaning"}
TABLE_KEYS = {"step", "rows", "cap", "noun", "empty", "filter", "totals", "columns", "meaning"}
COLUMN_KEYS = {"key", "head", "path", "format", "unit", "none", "in_totals"}
# never shown: the two-step write flow's token (a dry run only shows the plan); never passed: what applies it
SECRET_FIELDS = {"confirmation_token", "token_expires_in_s", "confirmation_text_required", "next"}
APPLY_ARGS = {"dry_run", "confirmation_token", "confirmation_text", "confirm"}


class Missing(KeyError):
    """A slot or column path that the tool result does not have."""

    def __str__(self):
        return self.args[0]


class _Skip(Exception):
    """A {=step.path} argument whose value is null or missing: the step is skipped."""


_OMIT = object()  # an empty argument: the key is left out of the call


# ----------------------------------------------------------------- reading and checking a skill source

def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load(name: str, src: str = SRC) -> dict:
    """src/<name>: {meta, template, report, checks, spec, spec_text}."""
    base = os.path.join(src, name)
    spec_text = read_text(os.path.join(base, "reference", "spec.json"))
    return {"name": name, "meta": json.loads(read_text(os.path.join(base, "meta.json"))),
            "template": read_text(os.path.join(base, "template.md")),
            "report": read_text(os.path.join(base, "reference", "report.md")),
            "checks": read_text(os.path.join(base, "reference", "checks.md")),
            "spec": json.loads(spec_text), "spec_text": spec_text}


def names(src: str = SRC) -> list[str]:
    return sorted(n for n in os.listdir(src) if os.path.isfile(os.path.join(src, n, "meta.json"))) \
        if os.path.isdir(src) else []


def _ref(text: str) -> tuple[str, str]:
    step, _, path = text.partition(".")
    return step, path


def _strings(v):
    """Every string inside an argument value (lists and dicts walked)."""
    if isinstance(v, str):
        yield v
    elif isinstance(v, list):
        for x in v:
            yield from _strings(x)
    elif isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)


def _is_write(tool: str) -> bool:
    try:
        from p6mcp import policy
        return tool in policy.TOOL_KIND and policy.is_write(tool)
    except ImportError:
        return False


def problems(skill: dict, tool_params: dict | None = None) -> list[str]:
    """Errors of a skill source: spec shape, every name it uses defined, every slot and table used by
    report.md, units in column heads, no token of a write dry run shown. tool_params: {tool: parameter
    names} to check the step arguments."""
    spec, meta, errs = skill["spec"], skill["meta"], []
    args = {a["name"] for a in meta.get("args", [])}
    if spec.get("spec") != SPEC_VERSION:
        errs.append(f"spec must be {SPEC_VERSION}")
    steps = {}
    for st in spec.get("steps", []):
        if set(st) - STEP_KEYS or not {"id", "tool", "args"} <= set(st):
            errs.append(f"step {st.get('id')!r}: keys {sorted(STEP_KEYS)} (id, tool, args required)")
            continue
        if not NAME_RE.match(st["id"]) or st["id"] in steps:
            errs.append(f"step id {st['id']!r}: lowercase name, unique")
        if tool_params is not None:
            if st["tool"] not in tool_params:
                errs.append(f"step {st['id']}: unknown tool {st['tool']}")
            else:
                errs += [f"step {st['id']}: {st['tool']} has no parameter {k!r}" for k in st["args"]
                         if k not in tool_params[st["tool"]]]
        errs += [f"step {st['id']}: {k} is never passed (write tools run as dry runs only)" for k in st["args"]
                 if k in APPLY_ARGS]
        if "when" in st and st["when"] not in optional_args(meta):
            errs.append(f"step {st['id']}: when must name an optional argument (default \"\") of the skill")
        for text in _strings(st["args"]):
            for r in REF_ONLY.finditer(text):
                if r.group(1) not in steps:
                    errs.append(f"step {st['id']}: {{={r.group(1)}...}} must name an earlier step")
            errs += [f"step {st['id']}: {{{a}}} is not an argument of the skill" for a in SLOT_RE.findall(text)
                     if a not in args]
        steps[st["id"]] = st
    if not steps:
        errs.append("no steps")

    def secret(where: str, step: str, path) -> list[str]:
        st = steps.get(step)
        parts = [p for x in (path if isinstance(path, list) else [path]) for p in str(x).split(".")]
        if st and _is_write(st["tool"]) and SECRET_FIELDS & set(parts):
            return [f"{where}: never show {', '.join(sorted(SECRET_FIELDS & set(parts)))} of a write dry run"]
        return []
    slots = spec.get("slots", {})
    for name, sl in slots.items():
        where = f"slot {name}"
        if not NAME_RE.match(name):
            errs.append(f"{where}: lowercase name")
        if set(sl) - SLOT_KEYS or not {"step", "path", "format", "meaning"} <= set(sl):
            errs.append(f"{where}: keys {sorted(SLOT_KEYS)} (step, path, format, meaning required)")
            continue
        if sl["step"] not in steps:
            errs.append(f"{where}: unknown step {sl['step']!r}")
        errs += _format_problems(where, sl) + secret(where, sl["step"], sl["path"])
    tables = spec.get("tables", {})
    for name, tb in tables.items():
        where = f"table {name}"
        if set(tb) - TABLE_KEYS or not {"step", "rows", "cap", "columns", "empty", "noun"} <= set(tb):
            errs.append(f"{where}: keys {sorted(TABLE_KEYS)} (step, rows, cap, noun, columns, empty required)")
            continue
        st = steps.get(tb["step"])
        if st is None:
            errs.append(f"{where}: unknown step {tb['step']!r}")
        elif tb["rows"] == "rows" and not tb.get("filter") and st["args"].get("limit") != tb["cap"]:
            errs.append(f"{where}: cap {tb['cap']} must equal the limit of step {st['id']} (one page, no counting)")
        errs += secret(where, tb["step"], tb["rows"])
        keys = set()
        for col in tb["columns"]:
            cw = f"{where} column {col.get('key')!r}"
            if set(col) - COLUMN_KEYS or not {"key", "head", "path", "format"} <= set(col):
                errs.append(f"{cw}: keys {sorted(COLUMN_KEYS)} (key, head, path, format required)")
                continue
            if col["key"] in keys or not NAME_RE.match(col["key"]):
                errs.append(f"{cw}: lowercase key, unique in the table")
            keys.add(col["key"])
            errs += _format_problems(cw, col) + secret(cw, tb["step"], col["path"])
            unit = col.get("unit")
            if unit in HEAD_UNITS and not col["head"].endswith(f"({unit})"):
                errs.append(f"{cw}: the head must end with ({unit})")
            if unit == "%" and "%" not in col["head"]:
                errs.append(f"{cw}: the head must show %")
        tot = tb.get("totals")
        if tot is not None and not (isinstance(tot, dict) and set(tot) == {"path", "label"}):
            errs.append(f"{where}: totals must be {{path, label}}")
    for chk in spec.get("checks", []):
        refs = chk.get("equal")
        if not isinstance(refs, list) or len(refs) < 2 or not chk.get("text"):
            errs.append(f"check {chk!r}: {{equal: [two step.path or more], text}}")
            continue
        errs += [f"check {chk['text']!r}: unknown step in {r!r}" for r in refs if _ref(r)[0] not in steps]
    # report.md: every placeholder defined, every slot and table used, blocks closed
    report = skill["report"]
    used = set(SLOT_RE.findall(report))
    errs += [f"report.md: {{{s}}} is not a slot or an argument" for s in sorted(used - set(slots) - args)]
    errs += [f"slot {s}: the name of an argument" for s in sorted(set(slots) & args)]
    lines = report.splitlines()
    tables_used, open_if = set(), None
    for i, line in enumerate(lines, 1):
        t = line.strip()
        m, c = TABLE_RE.match(t), IF_RE.match(t)
        if m:
            tables_used.add(m.group(1))
            if m.group(1) not in tables:
                errs.append(f"report.md line {i}: unknown table {m.group(1)!r}")
        elif c:
            used.add(c.group(2))
            if open_if:
                errs.append(f"report.md line {i}: [if] blocks do not nest")
            open_if = i
            if c.group(2) not in slots:
                errs.append(f"report.md line {i}: {c.group(2)!r} is not a slot")
        elif t == END_IF:
            if not open_if:
                errs.append(f"report.md line {i}: [end if] without [if]")
            open_if = None
        elif t.startswith(("[table", "[if", "[end")):
            errs.append(f"report.md line {i}: malformed marker {t!r}")
    if open_if:
        errs.append(f"report.md line {open_if}: [if] without [end if]")
    errs += [f"slot {s} is not used by report.md" for s in sorted(set(slots) - used)]
    errs += [f"table {t} is not used by report.md" for t in sorted(set(tables) - tables_used)]
    if skill["template"].count(STEPS_MARK) != 1:
        errs.append(f"template.md must hold the line {STEPS_MARK} once (the calls of spec.json go there)")
    if skill["template"].count(RULES_MARK) != 1:
        errs.append(f"template.md must hold the line {RULES_MARK} once (the writing rules every core skill shares)")
    if "{" in SLOT_RE.sub(lambda m: "" if m.group(1) in args else m.group(0), skill["template"]):
        errs.append("template.md: a brace that is not an argument placeholder (P6 MCP leaves no field unfilled: "
                    "write 'a slot name in curly braces' instead of {slot})")
    return errs


def _format_problems(where: str, d: dict) -> list[str]:
    errs = []
    if d["format"] not in FORMATS:
        errs.append(f"{where}: format {d['format']!r} is not one of {', '.join(FORMATS)}")
    if (d["format"] == "id_name") != isinstance(d["path"], list):
        errs.append(f"{where}: id_name takes a path pair [id, name], the other formats one path")
    if d.get("unit") is not None and d["unit"] not in UNITS:
        errs.append(f"{where}: unit {d['unit']!r} is not one of {', '.join(UNITS)}")
    return errs


# ----------------------------------------------------------------- values

def get(obj, path: str):
    """Value at a dotted path (keys, list indexes; "" = obj itself); Missing when there is no such field. A
    field under a null one is null (suggestion.reason when suggestion is null)."""
    cur = obj
    for part in path.split(".") if path else []:
        if cur is None:
            return None
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise Missing(f"no field {path!r} (missing at {part!r})")
    return cur


def truthy(value) -> bool:
    """[if: slot]: true, a number other than 0, a text or list that is not empty (null is false); an id_name
    pair is true when its ID is not null."""
    if isinstance(value, tuple):
        return value[0] is not None
    return bool(value)


def _num(v, nd: int) -> str:
    d = Decimal(str(v)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    if d == 0:
        d = abs(d)  # never -0.0
    return f"{d:,.{nd}f}"


def fmt(value, form: str, none: str = "n/a") -> str:
    """value written in the format form (FORMATS); None gives the none text."""
    if form == "id_name":
        ident, name = value if value is not None else (None, None)
        if ident is None:
            return none
        return f"{ident} - {name}" if name not in (None, "") else str(ident)
    if value is None:
        return none
    if form == "text":
        if isinstance(value, (list, dict)):
            raise ValueError(f"{value!r}: a list or dict needs the list format or a table")
        return str(value)
    if form == "int":
        if isinstance(value, bool) or float(value) != int(float(value)):
            raise ValueError(f"{value!r} is not a whole number")
        return f"{int(float(value)):,}"
    if form == "date":
        return str(value)[:10]
    if form == "datetime":
        return str(value)[:16]
    if form in ("n0", "n1", "n2"):
        return _num(value, int(form[1]))
    if form == "pct1":
        return _num(value, 1) + "%"
    if form == "flag":
        if not isinstance(value, bool):
            raise ValueError(f"{value!r} is not true or false")
        return "yes" if value else "no"
    if form == "list":
        if not isinstance(value, list):
            raise ValueError(f"{value!r} is not a list")
        return ", ".join(str(x) for x in value) if value else none
    if isinstance(value, (list, dict)):
        raise ValueError(f"{value!r}: a list or dict needs the list format or a table")
    raise ValueError(f"unknown format {form!r}")


def _cell(row, col: dict):
    p = col["path"]
    return (get(row, p[0]), get(row, p[1])) if isinstance(p, list) else get(row, p)


def numeric_args(meta: dict) -> set:
    """Arguments whose default is a whole number: written and passed as numbers (weeks=3)."""
    return {a["name"] for a in meta.get("args", []) if re.fullmatch(r"\d+", str(a.get("default") or ""))}


def call_args(step: dict, args: dict, numeric: set = frozenset(), results: dict | None = None) -> dict:
    """The step's arguments filled in, lists and dicts too: "{arg}" alone gives the argument (a number for a
    numeric argument; an empty one leaves its key out), "{=step.path}" alone the field of an earlier result
    (null or missing: _Skip), other text has its {arg} fields replaced."""
    def fill(v):
        if isinstance(v, str):
            m = ARG_ONLY.fullmatch(v)
            if m:
                val = args.get(m.group(1))
                if val in (None, ""):
                    return _OMIT
                return int(val) if m.group(1) in numeric else val
            r = REF_ONLY.fullmatch(v)
            if r:
                try:
                    val = get((results or {})[r.group(1)], r.group(2))
                except (KeyError, Missing):
                    val = None
                if val is None or (results or {}).get(r.group(1), {}).get("_failed"):
                    raise _Skip(v)
                return val
            return SLOT_RE.sub(lambda mm: str(args.get(mm.group(1)) or ""), v)
        if isinstance(v, list):
            return [x for x in (fill(y) for y in v) if x is not _OMIT]
        if isinstance(v, dict):
            return {k: x for k, x in ((k, fill(y)) for k, y in v.items()) if x is not _OMIT}
        return v
    return fill(step["args"])


def run_steps(spec: dict, args: dict, call, numeric: set = frozenset()) -> dict:
    """{step id: tool result}; call(tool, **kwargs) runs one tool. A step whose {=step.path} argument is
    null, or whose when argument is empty, is skipped, and the ValueError of an optional step is kept: each
    gives {error, _failed: true}."""
    results = {}
    for st in spec["steps"]:
        if st.get("when") and args.get(st["when"]) in (None, ""):  # an optional call the user did not ask for
            results[st["id"]] = {"error": f"skipped: {st['when']} is empty", "_failed": True}
            continue
        try:
            kw = call_args(st, args, numeric, results)
        except _Skip as e:
            results[st["id"]] = {"error": f"skipped: {e.args[0]} is empty", "_failed": True}
            continue
        try:
            results[st["id"]] = call(st["tool"], **kw)
        except ValueError as e:
            if not st.get("optional"):
                raise
            results[st["id"]] = {"error": str(e), "_failed": True}
    return results


def _slot(res: dict, path):
    if isinstance(path, list):  # id_name: the pair (ID, name)
        return tuple(_slot(res, p) for p in path)
    if res.get("_failed"):
        return res["error"] if path == "error" else None
    try:
        return get(res, path)
    except Missing:
        if path == "error":
            return None
        raise


def slot_values(spec: dict, results: dict) -> dict:
    return {name: _slot(results[sl["step"]], sl["path"]) for name, sl in spec.get("slots", {}).items()}


def _source(tb: dict, res: dict) -> tuple[list, bool]:
    """(rows of a table, more items than its cap in a list that is not paged)."""
    if res.get("_failed"):
        return [], False
    rows = get(res, tb["rows"])
    if isinstance(rows, dict):
        rows = [dict(v, _key=k) if isinstance(v, dict) else {"_key": k, "_value": v} for k, v in rows.items()]
    if not isinstance(rows, list):
        raise Missing(f"{tb['rows']!r} is not a list or a dict")
    if tb.get("filter"):
        rows = [r for r in rows if get(r, tb["filter"])]
    return rows[:tb["cap"]], tb["rows"] != "rows" and len(rows) > tb["cap"]


def table_rows(spec: dict, results: dict) -> dict:
    """{table: [{key: raw value}]}, the totals row last (key '_label' holds its label)."""
    out = {}
    for name, tb in spec.get("tables", {}).items():
        res = results[tb["step"]]
        try:
            src = _source(tb, res)[0]
        except Missing as e:
            raise Missing(f"table {name}: {e}") from None
        rows = [{} for _ in src]
        for c in tb["columns"]:  # a field some rows lack is null there; one no row has is a mistake
            found, missing = False, None
            for row, r in zip(rows, src, strict=True):
                try:
                    row[c["key"]] = _cell(r, c)
                    found = True
                except Missing as e:
                    row[c["key"]], missing = None, e
            if missing is not None and not found:
                raise Missing(f"table {name}: {missing}")
        if rows and tb.get("totals"):
            tot = get(res, tb["totals"]["path"])
            first = tb["columns"][0]["key"]
            rows.append({"_label": tb["totals"]["label"],
                         **{c["key"]: _cell(tot, c) for c in tb["columns"] if c["key"] != first
                            and c.get("in_totals", True)}})
        out[name] = rows
    return out


def check_results(spec: dict, results: dict) -> list[str]:
    """The spec's cross-checks that fail on these results (a failed optional step is not checked)."""
    errs = []
    for chk in spec.get("checks", []):
        refs = [_ref(r) for r in chk["equal"]]
        if any(results[s].get("_failed") for s, _p in refs):
            continue
        vals = [get(results[s], p) for s, p in refs]
        if any(v != vals[0] for v in vals[1:]):
            pairs = ", ".join(f"{r}={v!r}" for r, v in zip(chk["equal"], vals, strict=True))
            errs.append(f"check failed: {chk['text']} ({pairs})")
    return errs


# ----------------------------------------------------------------- rendering

def render_table(tb: dict, rows: list[dict], res: dict, overflow: bool = False) -> list[str]:
    if res.get("_failed"):
        return []  # the call failed (optional) or was skipped: an [if: ...error] block says why
    if not rows:
        return [tb["empty"]]
    cols = tb["columns"]
    out = ["| " + " | ".join(c["head"] for c in cols) + " |", "|" + "|".join("-" for _ in cols) + "|"]
    for r in rows:
        if "_label" in r:
            cells = [r["_label"]] + [fmt(r[c["key"]], c["format"], c.get("none", "n/a")) if c["key"] in r else ""
                                     for c in cols[1:]]
        else:
            cells = [fmt(r[c["key"]], c["format"], c.get("none", "n/a")) for c in cols]
        out.append("| " + " | ".join(x.replace("|", "/") for x in cells) + " |")
    if tb["rows"] == "rows" and res.get("next_offset") is not None:
        out += ["", f"Showing the first {res['returned']:,} of {res['total']:,} {tb['noun']}."]
    elif overflow:
        out += ["", f"Only the first {tb['cap']:,} {tb['noun']} are shown."]
    return out


def render(skill: dict, results: dict, args: dict) -> str:
    """report.md with every slot, argument, table and [if] block resolved (a missing field raises Missing)."""
    spec = skill["spec"]
    raw = slot_values(spec, results)
    slots = spec.get("slots", {})

    def put(m):
        name = m.group(1)
        if name in slots:
            return fmt(raw[name], slots[name]["format"], slots[name].get("none", "n/a"))
        return str(args.get(name) or "")
    rows = table_rows(spec, results)
    out, keep = [], True
    for line in skill["report"].splitlines():
        t = line.strip()
        m, c = TABLE_RE.match(t), IF_RE.match(t)
        if c:
            keep = truthy(raw[c.group(2)]) != bool(c.group(1))
            continue
        if t == END_IF:
            keep = True
            continue
        if not keep:
            continue
        if m:
            tb = spec["tables"][m.group(1)]
            res = results[tb["step"]]
            out += render_table(tb, rows[m.group(1)], res, _source(tb, res)[1])
            continue
        out.append(SLOT_RE.sub(put, line))
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def _lit(v, numeric: set) -> str:
    """An argument value as the call list writes it (JSON, a numeric {arg} without quotes)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        m = ARG_ONLY.fullmatch(v)
        r = REF_ONLY.fullmatch(v)
        if r:
            return f"<{r.group(1)}.{r.group(2)}>"  # a field of an earlier result (no brace: P6 MCP fills every field)
        return v if m and m.group(1) in numeric else json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(_lit(x, numeric) for x in v) + "]"
    return "{" + ", ".join(f"{json.dumps(k)}: {_lit(x, numeric)}" for k, x in v.items()) + "}"


def steps_text(spec: dict, numeric: set = frozenset(), optional: set = frozenset()) -> str:
    """The numbered calls of spec.json for template.md ([steps]): p6_tool(name="{arg}", limit=15), with
    what to do for an optional call, a {=step.path} argument and an empty argument."""
    lines, empty = [], set()
    for i, st in enumerate(spec["steps"], 1):
        parts = [f"{k}={_lit(v, numeric)}" for k, v in st["args"].items()]
        why = f": {st['why']}" if st.get("why") else ""
        line = f"{i}. {st['id']} = {st['tool']}({', '.join(parts)}){why}"
        refs = sorted({(m.group(1), m.group(2)) for s in _strings(st["args"]) for m in REF_ONLY.finditer(s)})
        for step, path in refs:
            line += (f". <{step}.{path}> is the field {path} of the result of {step}: when it is null or missing, "
                     "skip this call (its fields are null)")
        if st.get("when"):
            line += (f". Make this call only when <{st['when']}> is given; when it is empty, skip it (its fields are "
                     "null)")
        if st.get("optional"):
            line += f". If this call returns an error, keep its message as {st['id']}.error (its other fields are null)"
        lines.append(line + ("" if line.endswith(".") else "."))
        empty |= {a for s in _strings(st["args"]) for a in SLOT_RE.findall(s) if a in optional}
    if empty:
        lines.append(f"Leave out an argument whose value is empty ({', '.join(sorted(empty))}).")
    return "\n".join(lines)


def optional_args(meta: dict) -> set:
    """Arguments that may be empty (default ""): left out of the calls when empty."""
    return {a["name"] for a in meta.get("args", []) if a.get("default") == ""}


def fields_md(skill: dict) -> str:
    """reference/fields.md: what every slot and table column is, from spec.json."""
    spec, meta = skill["spec"], skill["meta"]
    out = [f"# Fields of {meta['title']}", "",
           ("Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied "
            "from one field of one call; write it in its format, never compute it."), "", "## Calls", "",
           steps_text(spec, numeric_args(meta), optional_args(meta)), "", "## Formats", ""]
    out += [f"- {k}: {v}" for k, v in FORMATS.items()]
    out += ["- A null value is written as the slot's or column's none text (n/a unless stated).",
            "- [if: slot] is true for true, a number other than 0, a text or list that is not empty.", "",
            "## Arguments", ""]
    out += [f"- {{{a['name']}}}: {a['description']}, as given" for a in meta.get("args", [])]
    out += ["", "## Units", ""]
    used = {d.get("unit") for d in spec.get("slots", {}).values()} | {
        c.get("unit") for tb in spec.get("tables", {}).values() for c in tb["columns"]}
    out += [f"- {k}: {v}" for k, v in UNITS.items() if k in used]
    out += ["", "## Slots", "", "| Slot | Field (call.path) | Unit | Format | None | Meaning |", "|-|-|-|-|-|-|"]
    for name, sl in spec.get("slots", {}).items():
        out.append(f"| {name} | {sl['step']}.{sl['path']} | {sl.get('unit') or ''} | {sl['format']} | "
                   f"{sl.get('none', 'n/a')} | {sl['meaning']} |")
    for name, tb in spec.get("tables", {}).items():
        out += ["", f"## Table {name}", ""]
        if tb.get("meaning"):
            out += [tb["meaning"], ""]
        src = f"{tb['step']}.{tb['rows']}"
        line = f"Rows: {src}, in the order returned, at most {tb['cap']}"
        if tb["rows"] != "rows":
            line += " (a dict gives one row per item: its key is _key, a plain value _value)"
        if tb.get("filter"):
            line += f", only the rows whose {tb['filter']} is true"
        out.append(line + ".")
        if tb.get("totals"):
            out.append(f"Last row: {tb['totals']['label']!r} in the first column, the other columns from "
                       f"{tb['step']}.{tb['totals']['path']} (same field names; blank where marked).")
        if tb["rows"] == "rows":
            out.append(f"When {tb['step']}.next_offset is not null, add the line: Showing the first <returned> of "
                       f"<total> {tb['noun']}. (returned and total of {tb['step']}).")
        else:
            out.append(f"When the list holds more than {tb['cap']} items, add the line: Only the first {tb['cap']} "
                       f"{tb['noun']} are shown.")
        out.append(f"No rows: write {tb['empty']!r} instead of the table (nothing when the call failed).")
        out += ["", "| Column | Field (row path) | Unit | Format | None | In totals row |", "|-|-|-|-|-|-|"]
        for c in tb["columns"]:
            p = " + ".join(c["path"]) if isinstance(c["path"], list) else (c["path"] or "(the row itself)")
            tot = "" if not tb.get("totals") else ("label" if c is tb["columns"][0] else
                                                   "yes" if c.get("in_totals", True) else "blank")
            none = c.get("none", "n/a")
            out.append(f"| {c['head']} | {p} | {c.get('unit') or ''} | {c['format']} | {none} | {tot} |")
    if spec.get("checks"):
        out += ["", "## Cross-checks (equal values)", ""]
        out += [f"- {chk['text']}: {' = '.join(chk['equal'])}" for chk in spec["checks"]]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------- the demo database and the server

_DEMO: dict = {}


def p6mcp_src() -> str:
    """The P6 MCP checkout that holds tests/fixtures/make_demo.py."""
    env = os.environ.get("P6MCP_SRC")
    if env:
        return os.path.abspath(env)
    import p6mcp
    return os.path.dirname(os.path.dirname(os.path.abspath(p6mcp.__file__)))


def demo() -> dict:
    """{server, db, work, call, params, keep}: the demo database (built once per process in a temp folder:
    demo.db and the two demo XER files) and the server pointed at it (writes allowed: dry runs)."""
    if _DEMO:
        return _DEMO
    fixtures = os.path.join(p6mcp_src(), "tests", "fixtures")
    if not os.path.isfile(os.path.join(fixtures, "make_demo.py")):
        raise RuntimeError(f"no tests/fixtures/make_demo.py in the P6 MCP checkout {p6mcp_src()}: put a checkout "
                           "of nizarhamza/p6-mcp with its tests on PYTHONPATH, or set P6MCP_SRC")
    sys.path.insert(0, fixtures)
    import make_demo
    work = tempfile.mkdtemp(prefix="p6shop_golden_")
    db = os.path.join(work, "demo.db")
    info = make_demo.build_db(db, work)
    s = make_demo.server()

    def call(tool: str, **kw):
        return s.REGISTERED[tool](**kw)
    params = {t: set(inspect.signature(f).parameters) for t, f in s.REGISTERED.items()}
    keep = {os.path.basename(p) for p in (db, info[make_demo.PROJ], info[make_demo.PROJ_BL])}
    _DEMO.update(server=s, db=db, work=work, call=call, params=params, info=info, make_demo=make_demo, keep=keep)
    return _DEMO


def reset_outputs() -> None:
    """Before each golden run: no health snapshot and no output file left by an earlier skill (the
    rendering never depends on the order skills run in)."""
    d = demo()
    shutil.rmtree(os.path.join(d["work"], "editlog", "health"), ignore_errors=True)
    for name in os.listdir(d["work"]):
        path = os.path.join(d["work"], name)
        if os.path.isfile(path) and name not in d["keep"]:
            os.remove(path)


def example_args(skill: dict) -> dict:
    """The skill's arguments on the demo: defaults, then meta.json example_args ({work} = the work folder)."""
    work = demo()["work"]
    args = {a["name"]: a.get("default") for a in skill["meta"].get("args", [])}
    for k, v in (skill["meta"].get("example_args") or {}).items():
        args[k] = v.replace("{work}/", work + os.sep).replace("{work}", work) if isinstance(v, str) else v
    return args


def mask(text: str) -> str:
    """The work folder written as WORK_SHOWN (example.md must not depend on the temp folder)."""
    work = demo()["work"]
    for w in sorted({work, work.replace("\\", "/"), os.path.realpath(work)}, key=len, reverse=True):
        text = text.replace(w, WORK_SHOWN)
    return text.replace(WORK_SHOWN + "/", WORK_SHOWN + "\\")  # a file in it reads the same on Linux and Windows


def golden(skill: dict) -> tuple[str, dict, dict]:
    """(rendering, step results, raw slot values) of a skill on the demo project (example_args of meta.json)."""
    d = demo()
    errs = problems(skill, d["params"])
    if errs:
        raise ValueError(f"src/{skill['name']}: " + "; ".join(errs))
    reset_outputs()
    args = example_args(skill)
    results = run_steps(skill["spec"], args, d["call"], numeric_args(skill["meta"]))
    bad = check_results(skill["spec"], results)
    if bad:
        raise ValueError(f"src/{skill['name']}: " + "; ".join(bad))
    return mask(render(skill, results, args)), results, slot_values(skill["spec"], results)


def verify(name: str) -> list[str]:
    """Every problem of one skill: source, rendering, P6 MCP's limits and house rules, oracles."""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import catalog
    from oracles import compare
    from p6mcp import shop, skills
    skill = load(name)
    try:
        text, results, raw = golden(skill)
    except (ValueError, Missing) as e:
        return [str(e)]
    item = catalog.core_item(skill, text)
    errs = [f"limits: {e}" for e in skills.check_skill(item, strict=True)]
    errs += [e for p, t in [("template.md", item["template"])] + [(f["path"], f["text"]) for f in item["files"]]
             for e in catalog.text_problems(p, t)]
    house = getattr(skills, "house_problems", None)
    if house is not None:
        errs += house(skills.from_config(shop.to_stored(item)), lambda t: demo()["params"].get(t, ()))
    return errs + compare(name, skill, results, raw, example_args(skill), demo())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="golden")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render").add_argument("name")
    sub.add_parser("verify").add_argument("name")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    if a.cmd == "render":
        sys.stdout.write(golden(load(a.name))[0])
        return 0
    if a.cmd == "verify":
        errs = verify(a.name)
        for e in errs:
            print(e, file=sys.stderr)
        print(f"{a.name}: {'OK' if not errs else f'{len(errs)} problem(s)'}")
        return 1 if errs else 0
    bad = 0
    for name in names():
        text = golden(load(name))[0]
        path = os.path.join(ROOT, "skills", name, "reference", "example.md")
        current = read_text(path) if os.path.isfile(path) else None
        if current != text:
            bad += 1
            print(f"skills/{name}/reference/example.md differs from the rendering: run python tools/catalog.py build",
                  file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
