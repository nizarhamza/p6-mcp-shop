"""Independent oracles of the core skills: for every slot and every table of a skill's spec.json, the value
computed again on the demo database with SQL on P6's own tables (and the edit log files), never through
the app's code. tests/test_oracles.py (and python tools/golden.py verify <name>) compare them with what the
golden harness reads from the tools.

A skill's module is tests/oracles/<name with _ for ->.py and defines:
    SLOTS   {slot: fn(o) -> value}: the raw value the slot's field should hold, or a predicate
            fn(value) -> bool for a text whose wording is the tool's (see Contains)
    TABLES  {table: fn(o) -> rows}: the rows the table should show, in order, each {column key: value}
            (an id_name column takes the pair (id, name)); a totals row is {"_label": label, key: value...};
            a table of a failed or skipped call has no rows ([]); Unchecked(reason) for a whole table the
            oracle cannot recompute in that case
o is an Oracle: o.sql(query, *args) -> rows (sqlite3.Row), o.one(query, *args) -> first value, o.pid (the
project of the example, None for a skill without a project argument), o.args (the example arguments, {work}
resolved), o.work (the folder of the database: edit log, XER files, output files), o.db (its path).
Numbers the tools round to 2 decimals are compared within 0.0051 and once formatted.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3

STATUS_NAMES = {"TK_NotStart": "Not Started", "TK_Active": "In Progress", "TK_Complete": "Completed"}
STATUS_ORDER = ("TK_NotStart", "TK_Active", "TK_Complete")
SUMMARY_TYPES = ("TT_LOE", "TT_WBS")
HPD = "COALESCE(NULLIF(c.day_hr_cnt, 0), 8)"  # hours per day of an activity calendar c (0 or NULL: 8)
TOL = 0.0051  # the tools round to 2 decimals


class Contains:
    """Predicate oracle for a text slot: every part must appear in the value."""

    def __init__(self, *parts):
        self.parts = parts

    def __call__(self, value) -> bool:
        return isinstance(value, str) and all(str(p) in value for p in self.parts)

    def __repr__(self):
        return f"Contains{self.parts!r}"


UNCHECKED: list[str] = []  # reasons of every Unchecked value created in this process


class Unchecked:
    """An oracle value for a case the oracle cannot recompute independently (real P6 data the demo does not
    have, such as a feature the oracle does not model): it passes the comparison and records its reason in
    UNCHECKED. Never a way to hide a difference the oracle could compute."""

    def __init__(self, reason: str):
        self.reason = reason
        UNCHECKED.append(reason)

    def __call__(self, value) -> bool:
        return True

    def __repr__(self):
        return f"Unchecked({self.reason!r})"


class Oracle:
    def __init__(self, db: str, work: str, args: dict):
        self.db, self.work, self.args = db, work, args
        self.con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        self.con.row_factory = sqlite3.Row
        project = args.get("project")
        self.pid = self.one("SELECT proj_id FROM PROJECT WHERE proj_short_name = ?", project) if project else None

    def sql(self, query: str, *args) -> list[sqlite3.Row]:
        return self.con.execute(query, args).fetchall()

    def one(self, query: str, *args):
        row = self.con.execute(query, args).fetchone()
        return None if row is None else row[0]

    def close(self) -> None:
        self.con.close()

    def stale(self) -> bool:
        """An edit log entry of this database recorded under the project's current last_schedule_date (the
        server's 'changed since the last F9'); restores are not used by the fixtures."""
        last = self.one("SELECT last_schedule_date FROM PROJECT WHERE proj_id = ?", self.pid)
        folder = os.path.join(self.work, "editlog")
        db = os.path.basename(self.db).lower()
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                for line in fh:
                    e = json.loads(line)
                    if str(e.get("db", "")).lower() == db and (e.get("stale") or {}).get(str(self.pid)) == last:
                        return True
        return False

    def critical_sql(self, alias: str = "t") -> tuple[str, tuple]:
        """SQL condition of a critical activity under the project's setting (PROJECT.critical_path_type):
        total float at or below critical_drtn_hr_cnt hours, or on the longest path (driving_path_flag)."""
        r = self.sql("SELECT critical_path_type, critical_drtn_hr_cnt FROM PROJECT WHERE proj_id = ?", self.pid)[0]
        if r["critical_path_type"] == "CT_DrivPath":
            return f"{alias}.driving_path_flag = 'Y'", ()
        return f"{alias}.total_float_hr_cnt <= ?", (float(r["critical_drtn_hr_cnt"] or 0),)


def module(skill_name: str):
    return importlib.import_module(f"oracles.{skill_name.replace('-', '_')}")


def pct(actual, remaining):
    """Units % complete: actual / (actual + remaining) x 100, None without units."""
    a, r = float(actual or 0), float(remaining or 0)
    return 100 * a / (a + r) if a + r else None


def same(got, want, form: str):
    """Why got (harness) differs from want (oracle), None when they agree."""
    import golden
    if callable(want):
        return None if want(got) else f"{got!r} does not satisfy {want!r}"
    if form == "id_name":
        return None if tuple(got) == tuple(want) else f"{tuple(got)!r} != {tuple(want)!r}"
    nums = (int, float)
    if isinstance(got, nums) and isinstance(want, nums) and not isinstance(got, bool) and not isinstance(want, bool):
        if abs(got - want) > TOL + 1e-9 * abs(want):
            return f"{got!r} != {want!r}"
        shown, expected = golden.fmt(got, form), golden.fmt(round(want, 2), form)
        return None if shown == expected else f"written {shown!r}, oracle gives {expected!r}"
    if got != want:
        return f"{got!r} != {want!r}"
    return None


def compare(name: str, skill: dict, results: dict, raw: dict, args: dict, demo: dict) -> list[str]:
    """Every slot and table cell of a skill that differs from its oracle (and every one without an oracle)."""
    import golden
    spec = skill["spec"]
    try:
        mod = module(name)
    except ModuleNotFoundError:
        return [f"no oracle module tests/oracles/{name.replace('-', '_')}.py"]
    bad = [f"no oracle for slot {s}" for s in sorted(set(spec.get("slots", {})) - set(mod.SLOTS))]
    bad += [f"oracle of an unknown slot {s}" for s in sorted(set(mod.SLOTS) - set(spec.get("slots", {})))]
    bad += [f"no oracle for table {t}" for t in sorted(set(spec.get("tables", {})) - set(mod.TABLES))]
    bad += [f"oracle of an unknown table {t}" for t in sorted(set(mod.TABLES) - set(spec.get("tables", {})))]
    rows = golden.table_rows(spec, results)
    o = Oracle(demo["db"], demo["work"], args)
    try:
        for slot, fn in mod.SLOTS.items():
            if slot in raw:
                why = same(raw[slot], fn(o), spec["slots"][slot]["format"])
                if why:
                    bad.append(f"slot {slot}: {why}")
        for table, fn in mod.TABLES.items():
            if table not in rows:
                continue
            want, got = fn(o), rows[table]
            if isinstance(want, Unchecked):  # a whole table the oracle cannot recompute in this case
                continue
            cols = spec["tables"][table]["columns"]
            if len(want) != len(got):
                bad.append(f"table {table}: {len(got)} rows, oracle {len(want)}")
                continue
            for i, (g, w) in enumerate(zip(got, want, strict=True)):
                if g.get("_label") != w.get("_label"):
                    bad.append(f"table {table} row {i}: label {g.get('_label')!r} != {w.get('_label')!r}")
                for c in cols:
                    if c["key"] not in g and c["key"] not in w:
                        continue  # blank cell of a totals row
                    if (c["key"] in g) != (c["key"] in w):
                        bad.append(f"table {table} row {i} {c['key']}: present in one side only")
                        continue
                    why = same(g[c["key"]], w[c["key"]], c["format"])
                    if why:
                        bad.append(f"table {table} row {i} {c['key']}: {why}")
    finally:
        o.close()
    return bad
