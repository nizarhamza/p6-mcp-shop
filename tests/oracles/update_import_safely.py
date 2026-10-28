"""Oracles of update-import-safely: the XER file parsed here (tab separated ERMHDR, %T, %F, %R and %E lines,
UTF-8 else cp1252) and matched with SQL on the database the way an update import documents it: the rows of
the file's project plus global rows (codes of kept code types only), global items by name (currencies, OBS,
UDF types, calendars, resources, code types), project calendars and code types by name in the project,
codes by type, short name and parent, WBS nodes by path under the project node, activities by Activity ID,
relationships by (predecessor, successor, type), assignments by activity and resource, activity code
assignments by (activity, code type), UDF values by (type, item), the schedule options written to PROJPROP
'scheduling' when they differ. Nothing here runs the import: the dry run's counts, missing rows and
pre-flight lists are counted again from the file and the database."""

from __future__ import annotations

import os
import re
from collections import Counter

from oracles import Contains, Unchecked
from oracles.export_dashboard import _tree

# tables an import writes row by row, in P6's XER order (SCHEDOPTIONS goes to PROJPROP)
IMPORTED = ("CURRTYPE", "FINTMPL", "OBS", "UDFTYPE", "PROJECT", "CALENDAR", "PROJWBS", "RSRC", "ACTVTYPE",
            "RSRCRATE", "TASK", "ACTVCODE", "TASKPRED", "TASKRSRC", "TASKACTV", "UDFVALUE")
PK = {"CURRTYPE": "curr_id", "FINTMPL": "fintmpl_id", "OBS": "obs_id", "UDFTYPE": "udf_type_id", "PROJECT": "proj_id",
      "CALENDAR": "clndr_id", "PROJWBS": "wbs_id", "RSRC": "rsrc_id", "ACTVTYPE": "actv_code_type_id",
      "RSRCRATE": "rsrc_rate_id", "TASK": "task_id", "ACTVCODE": "actv_code_id", "TASKPRED": "task_pred_id",
      "TASKRSRC": "taskrsrc_id"}
CARRIED = {"proj_id", "pred_proj_id", "orig_proj_id", "sum_base_proj_id", "source_proj_id", "wbs_id", "parent_wbs_id",
           "obs_id", "parent_obs_id", "clndr_id", "base_clndr_id", "rsrc_id", "parent_rsrc_id", "curr_id", "fintmpl_id",
           "actv_code_type_id", "actv_code_id", "parent_actv_code_id", "udf_type_id", "task_id", "pred_task_id"}
STAMPS = {"create_date", "create_user", "update_date", "update_user", "delete_session_id", "delete_date", "guid"}
UDF_SUBJECTS = ("PROJECT", "PROJWBS", "TASK", "RSRC", "TASKRSRC")  # tables a UDF value can point to
# global items matched by name: (table, key columns, extra condition)
GLOBAL = (("CURRTYPE", ("curr_short_name",), ""), ("FINTMPL", ("fintmpl_name",), ""), ("OBS", ("obs_name",), ""),
          ("UDFTYPE", ("table_name", "udf_type_label"), ""), ("CALENDAR", ("clndr_type", "clndr_name"), "proj_id IS NULL"),
          ("RSRC", ("rsrc_short_name",), ""), ("ACTVTYPE", ("actv_code_type_scope", "actv_code_type"), "proj_id IS NULL"))
ACTIONS = ("matched", "inserted", "updated", "unchanged", "restored", "deleted", "kept_existing", "skipped_external",
           "skipped_duplicate", "skipped_unmapped")
COLUMN = {"matched": "matched", "inserted": "inserted", "updated": "updated", "unchanged": "unchanged",
          "restored": "restored", "deleted": "deleted", "kept_existing": "kept", "skipped_external": "external",
          "skipped_duplicate": "duplicate", "skipped_unmapped": "unmapped"}


# ----------------------------------------------------------------- the XER file

def read_xer(path: str) -> dict:
    with open(path, "rb") as fh:
        raw = fh.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    try:
        text, enc = body.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        text, enc = body.decode("cp1252", errors="replace"), "cp1252"
    out = {"bytes": len(raw), "bom": bom, "encoding": enc, "bad": text.count("�"), "header": [], "tables": {},
           "end": False, "mismatch": Counter(), "before": Counter(), "blocks": Counter()}
    cur = fields = None
    for line in text.split("\n"):
        parts = line.rstrip("\r").split("\t")
        tag = parts[0]
        if tag == "ERMHDR":
            out["header"] = parts
        elif tag == "%T":
            cur, fields = parts[1], None
            out["blocks"][cur] += 1
            out["tables"].setdefault(cur, [])
        elif tag == "%F":
            fields = parts[1:]
        elif tag == "%R":
            if fields is None:
                out["before"][cur] += 1
                continue
            vals = parts[1:]
            if len(vals) != len(fields):
                out["mismatch"][cur] += 1
            vals = (vals + [""] * len(fields))[:len(fields)]
            out["tables"][cur].append({f: _decode(v) for f, v in zip(fields, vals, strict=True)})
        elif tag == "%E":
            out["end"] = True
    return out


def _decode(v: str):
    if v == "":
        return None
    v = v.replace("\x7f\x7f", "\n").replace('""', '"')
    if len(v) == 16 and v[4] == "-" and v[10] == " " and v[13] == ":":
        return v + ":00"  # XER dates have no seconds
    return v


_XER: dict = {}


def xer(o) -> dict:
    path = o.args["xer_path"]
    if path not in _XER:
        _XER[path] = read_xer(path)
    return _XER[path]


def _xp(o):
    """The file's project row when the file holds one project (else None: the pre-flight needs a choice)."""
    p = xer(o)["tables"].get("PROJECT", [])
    return p[0] if len(p) == 1 else None


def _x(o) -> dict:
    """Rows of the file's project plus global rows (no proj_id); codes of a kept code type only."""
    if getattr(o, "_uis_x", None) is None:
        o._uis_x = _only(o)
    return o._uis_x


def _only(o) -> dict:
    raw, xp = xer(o)["tables"], _xp(o)
    if xp is None:
        return raw
    out = {t: [r for r in rows if r.get("proj_id") in (None, xp["proj_id"])] for t, rows in raw.items()}
    if "ACTVCODE" in out:
        kept = {r.get("actv_code_type_id") for r in out.get("ACTVTYPE", [])}
        out["ACTVCODE"] = [r for r in out["ACTVCODE"] if r.get("actv_code_type_id") in kept]
    return out


def _rows(o, table):
    return _x(o).get(table, [])


def _alive(o, table, alias=""):
    cols = {str(r[1]).lower() for r in o.sql(f"PRAGMA table_info({table})")}
    return f" AND {alias}delete_session_id IS NULL" if "delete_session_id" in cols else ""


def _cached(name):
    def wrap(fn):
        def run(o):
            key = f"_uis_{name}"
            if getattr(o, key, None) is None:
                setattr(o, key, fn(o))
            return getattr(o, key)
        return run
    return wrap


# ----------------------------------------------------------------- pre-flight

@_cached("preflight")
def _preflight(o) -> dict:
    f, x, proj = xer(o), _x(o), _xp(o)
    all_codes = f["tables"].get("ACTVCODE", [])

    def ids(t):
        return {r.get(PK.get(t, "")) for r in x.get(t, [])} - {None}
    tasks, wbs, cals, rsrc, asg = (x.get(t, []) for t in ("TASK", "PROJWBS", "CALENDAR", "RSRC", "TASKRSRC"))
    wbs_ids, cal_ids, task_ids, rsrc_ids = ids("PROJWBS"), ids("CALENDAR"), ids("TASK"), ids("RSRC")
    code = {t.get("task_id"): t.get("task_code") for t in tasks}
    nodes = {w.get("wbs_id") for w in wbs if w.get("proj_node_flag") == "Y"}
    out = {"errors": [], "warnings": [], "info": []}

    def add(level, check, items):
        if items:
            out[level].append({"check": check, "count": len(items), "first": str(items[0])})
    add("errors", "project_wbs_node_missing", [] if nodes else [proj["proj_short_name"]])
    add("errors", "task_wbs_missing", [t["task_code"] for t in tasks if t.get("wbs_id") not in wbs_ids])
    add("errors", "task_calendar_missing", [t["task_code"] for t in tasks if t.get("clndr_id") not in cal_ids])
    add("errors", "duplicate_task_code", sorted(str(c) for c, n in Counter(code.values()).items() if n > 1))
    add("errors", "taskrsrc_task_missing", [f"taskrsrc {r.get('taskrsrc_id')}: task {r.get('task_id')}" for r in asg
                                            if r.get("task_id") not in task_ids])
    add("errors", "field_count_mismatch", [f"{t}: {n} rows" for t, n in f["mismatch"].items() if t in IMPORTED])
    add("warnings", "field_count_mismatch_not_imported", [f"{t}: {n} rows" for t, n in f["mismatch"].items()
                                                          if t not in IMPORTED])
    add("warnings", "rows_before_fields", [f"{t}: {n} rows" for t, n in f["before"].items()])
    add("warnings", "duplicate_table_blocks", [t for t, n in f["blocks"].items() if n > 1])
    add("warnings", "end_marker_missing", [] if f["end"] else ["%E"])
    add("warnings", "undecodable_bytes", [f["bad"]] if f["bad"] else [])
    add("warnings", "resource_missing",
        [f"activity {t['task_code']}" for t in tasks if t.get("rsrc_id") is not None and t["rsrc_id"] not in rsrc_ids]
        + [f"taskrsrc {r.get('taskrsrc_id')}" for r in asg if r.get("rsrc_id") is not None
           and r["rsrc_id"] not in rsrc_ids])
    add("warnings", "wbs_parent_missing", [w.get("wbs_short_name") for w in wbs if w.get("wbs_id") not in nodes
                                           and w.get("parent_wbs_id") not in wbs_ids])
    ok = cal_ids | {None}
    add("warnings", "calendar_missing", [f"base of {c.get('clndr_name')}" for c in cals if c.get("base_clndr_id") not in ok]
        + [f"resource {r.get('rsrc_short_name')}" for r in rsrc if r.get("clndr_id") not in ok]
        + (["project"] if proj.get("clndr_id") not in ok else []))
    links = Counter((r.get("pred_task_id"), r.get("task_id"), r.get("pred_type")) for r in x.get("TASKPRED", []))
    add("warnings", "duplicate_link", [f"{code.get(p, p)} -> {code.get(s, s)}" for (p, s, _k), n in links.items() if n > 1])
    cleared = []
    for t in IMPORTED:
        for k in sorted(set().union(*x[t]) if x.get(t) else ()):
            if k.endswith("_id") and k not in CARRIED and k not in STAMPS and k not in ("fk_id", PK.get(t)):
                n = sum(1 for r in x[t] if r.get(k) is not None)
                if n:
                    cleared.append(f"{t}.{k}: {n}")
    add("warnings", "foreign_ids_cleared", cleared)
    add("warnings", "tables_not_imported", [f"{t}: {len(r)} rows" for t, r in x.items()
                                            if t not in IMPORTED and t != "SCHEDOPTIONS"])
    kept = {id(r) for r in x.get("ACTVCODE", [])}
    add("info", "activity_codes_other_types", [f"{c.get('short_name')} (type {c.get('actv_code_type_id')})"
                                               for c in all_codes if id(c) not in kept])
    add("info", "schedule_options", ["SCHEDOPTIONS"] if x.get("SCHEDOPTIONS") else [])
    add("info", "external_links", [f"{code.get(r.get('pred_task_id'), r.get('pred_task_id'))} -> "
                                   f"{code.get(r.get('task_id'), r.get('task_id'))}" for r in x.get("TASKPRED", [])
                                   if r.get("task_id") not in task_ids or r.get("pred_task_id") not in task_ids])
    types, codes = ids("ACTVTYPE"), ids("ACTVCODE")
    add("info", "activity_codes_unmapped", [f"task {r.get('task_id')}" for r in x.get("TASKACTV", [])
                                            if r.get("task_id") not in task_ids or r.get("actv_code_type_id") not in types
                                            or r.get("actv_code_id") not in codes])
    utab = {u.get("udf_type_id"): u.get("table_name") for u in x.get("UDFTYPE", [])}
    pks = {t: ids(t) for t in UDF_SUBJECTS}
    add("info", "udf_values_unmapped", [f"{utab.get(v.get('udf_type_id'))} {v.get('fk_id')}" for v in x.get("UDFVALUE", [])
                                        if v.get("fk_id") not in pks.get(utab.get(v.get("udf_type_id")), ())])
    add("info", "project_baseline_not_imported", [] if proj.get("sum_base_proj_id") is None else [proj["sum_base_proj_id"]])
    add("info", "encoding", [] if f["encoding"] == "utf-8" else [f"{f['encoding']}, first non UTF-8 byte"])
    pref = {str(k).lower(): v for k, v in dict(o.sql("SELECT * FROM PREFER")[0]).items()}
    long = []
    for key, rows, col in (("task_code_len", tasks, "task_code"), ("proj_short_len", [proj], "proj_short_name"),
                           ("wbs_short_len", [w for w in wbs if w.get("wbs_id") not in nodes], "wbs_short_name"),
                           ("rsrc_short_len", rsrc, "rsrc_short_name")):
        n = pref.get(key)
        long += [f"{col} {r.get(col)!r}" for r in rows if n and len(r.get(col) or "") > int(n)]
    add("warnings", "codes_too_long", long)  # checked last, with the database
    return out


# what each check's note is about (the note's wording is the tool's); None: the check has no note
NOTE = {"project_wbs_node_missing": "project WBS node", "task_wbs_missing": "without a WBS",
        "task_calendar_missing": "without a calendar", "duplicate_task_code": "unique",
        "taskrsrc_task_missing": "not in the file", "field_count_mismatch": "values than fields",
        "field_count_mismatch_not_imported": None, "rows_before_fields": "%F", "duplicate_table_blocks": "block",
        "end_marker_missing": "truncated", "undecodable_bytes": "not readable", "resource_missing": "cleared",
        "wbs_parent_missing": "project node", "calendar_missing": "cleared", "duplicate_link": "one link per type",
        "foreign_ids_cleared": "cleared", "tables_not_imported": None, "codes_too_long": "PREFER",
        "activity_codes_other_types": "not imported", "schedule_options": "PROJPROP scheduling",
        "external_links": "skipped", "activity_codes_unmapped": "skipped", "udf_values_unmapped": "skipped",
        "project_baseline_not_imported": "sum_base_proj_id", "encoding": "UTF-8"}
SAMPLE_PART = {"duplicate_link", "codes_too_long"}  # first items whose wording carries more than the oracle's part


def _check_rows(level):
    def fn(o):
        if _xp(o) is None:
            return []  # several projects in the file: no pre-flight without a choice
        return [{"check": r["check"], "count": r["count"],
                 "first": Contains(r["first"]) if r["check"] in SAMPLE_PART else r["first"],
                 "note": NOTE[r["check"]] and Contains(NOTE[r["check"]])} for r in _preflight(o)[level]]
    return fn


def global_items(o):
    out = []
    for t, keys, extra in GLOBAL:
        rows = [r for r in _rows(o, t) if r.get("proj_id") is None]
        if not rows:
            continue
        where = " AND ".join(f"{k} = ?" for k in keys) + (f" AND {extra}" if extra else "") + _alive(o, t)
        hit = sum(1 for r in rows if o.sql(f"SELECT 1 FROM {t} WHERE {where}", *[r.get(k) for k in keys]))
        out.append({"table": t, "matched": hit, "created": len(rows) - hit})
    return out


# ----------------------------------------------------------------- the update, matched again

@_cached("update")
def _update(o) -> dict:
    """counts per table in the order the import meets them, touched link and assignment ids, mapped
    activities, the schedule options action."""
    counts: dict = {}

    def count(t, what):
        counts.setdefault(t, {}).setdefault(what, 0)
        counts[t][what] += 1
    fresh = iter(range(-1, -10 ** 9, -1))  # ids of rows the import would insert
    pid, xp = o.pid, _xp(o)
    idmap: dict = {t: {} for t in IMPORTED}
    created: dict = {t: set() for t in IMPORTED}
    idmap["PROJECT"][xp["proj_id"]] = pid

    def match(t, rows, key, sql, parent_col=None):
        """Reuse the row sql finds for key(row), else insert; a row whose parent is in the same list after it."""
        pk, pending = PK[t], list(rows)
        while pending:
            progressed, later = False, []
            for r in pending:
                par = r.get(parent_col) if parent_col else None
                if par is not None and par not in idmap[t] and any(p[pk] == par for p in pending if p is not r):
                    later.append(r)
                    continue
                hit = o.one(sql + _alive(o, t), *key(r)) if sql else None
                if hit is None:
                    hit = next(fresh)
                    created[t].add(r[pk])
                idmap[t][r[pk]] = hit
                count(t, "inserted" if hit < 0 else "matched")
                progressed = True
            if not progressed:  # parent cycle: the rest inserted
                for r in later:
                    idmap[t][r[pk]] = next(fresh)
                    created[t].add(r[pk])
                    count(t, "inserted")
                break
            pending = later

    def match_global(t, rows, parent_col=None):
        cols, extra = next((k, e) for g, k, e in GLOBAL if g == t)
        sql = f"SELECT {PK[t]} FROM {t} WHERE " + " AND ".join(f"{c} = ?" for c in cols) + (f" AND {extra}" if extra else "")
        match(t, rows, lambda r: [r.get(c) for c in cols], sql, parent_col)
    match_global("CURRTYPE", _rows(o, "CURRTYPE"))
    match_global("FINTMPL", _rows(o, "FINTMPL"))
    match_global("OBS", _rows(o, "OBS"), "parent_obs_id")
    match_global("UDFTYPE", _rows(o, "UDFTYPE"))
    cals = _rows(o, "CALENDAR")
    match_global("CALENDAR", [c for c in cals if c.get("proj_id") is None], "base_clndr_id")
    match("CALENDAR", [c for c in cals if c.get("proj_id") is not None], lambda r: (pid, r.get("clndr_name")),
          "SELECT clndr_id FROM CALENDAR WHERE proj_id = ? AND clndr_name = ?", "base_clndr_id")
    count("PROJECT", "updated")
    match_global("RSRC", _rows(o, "RSRC"), "parent_rsrc_id")
    types = _rows(o, "ACTVTYPE")
    match_global("ACTVTYPE", [t for t in types if t.get("proj_id") is None])
    match("ACTVTYPE", [t for t in types if t.get("proj_id") is not None], lambda r: (pid, r.get("actv_code_type")),
          "SELECT actv_code_type_id FROM ACTVTYPE WHERE proj_id = ? AND actv_code_type = ?")
    match("ACTVCODE", _rows(o, "ACTVCODE"),
          lambda r: (idmap["ACTVTYPE"].get(r.get("actv_code_type_id")), r.get("short_name"),
                     idmap["ACTVCODE"].get(r.get("parent_actv_code_id"))),
          "SELECT actv_code_id FROM ACTVCODE WHERE actv_code_type_id = ? AND short_name = ? AND parent_actv_code_id IS ?",
          "parent_actv_code_id")
    for r in _rows(o, "RSRCRATE"):  # rates only for new resources
        count("RSRCRATE", "inserted" if r.get("rsrc_id") in created["RSRC"] else "kept_existing")
    wbs = _rows(o, "PROJWBS")
    by_id = {w["wbs_id"]: w for w in wbs}
    node = next(w for w in wbs if w.get("proj_node_flag") == "Y")
    wmap = idmap["PROJWBS"]
    wmap[node["wbs_id"]] = o.one("SELECT wbs_id FROM PROJWBS WHERE proj_id = ? AND proj_node_flag = 'Y'"
                                 + _alive(o, "PROJWBS"), pid)
    count("PROJWBS", "matched")

    def depth(w, n=0):
        p = by_id.get(w.get("parent_wbs_id"))
        return n if p is None or n > 100 else depth(p, n + 1)
    for w in sorted((w for w in wbs if w is not node), key=depth):
        parent = wmap.get(w.get("parent_wbs_id"), wmap[node["wbs_id"]])
        hit = o.one("SELECT wbs_id FROM PROJWBS WHERE proj_id = ? AND parent_wbs_id = ? AND wbs_short_name = ?"
                    + _alive(o, "PROJWBS"), pid, parent, w["wbs_short_name"])
        wmap[w["wbs_id"]] = hit if hit is not None else next(fresh)
        count("PROJWBS", "updated" if hit is not None else "inserted")
    tmap = idmap["TASK"]
    for t in _rows(o, "TASK"):
        hit = o.one("SELECT task_id FROM TASK WHERE proj_id = ? AND task_code = ?" + _alive(o, "TASK"), pid, t["task_code"])
        tmap[t["task_id"]] = hit if hit is not None else next(fresh)
        count("TASK", "updated" if hit is not None else "inserted")
    touched_links, seen = set(), set()
    for r in _rows(o, "TASKPRED"):
        succ, pred = tmap.get(r["task_id"]), tmap.get(r["pred_task_id"])
        if succ is None or pred is None:
            count("TASKPRED", "skipped_external")
            continue
        if (succ, pred, r.get("pred_type")) in seen:
            count("TASKPRED", "skipped_duplicate")
            continue
        seen.add((succ, pred, r.get("pred_type")))
        hit = o.one("SELECT task_pred_id FROM TASKPRED WHERE task_id = ? AND pred_task_id = ? AND pred_type = ?"
                    + _alive(o, "TASKPRED"), succ, pred, r["pred_type"])
        count("TASKPRED", "updated" if hit is not None else "inserted")
        if hit is not None:
            touched_links.add(hit)
    used = set()
    for r in _rows(o, "TASKRSRC"):
        task, rsrc = tmap.get(r["task_id"]), idmap["RSRC"].get(r.get("rsrc_id"))
        if task is None:
            count("TASKRSRC", "skipped_unmapped")
            continue
        hit = next((h["taskrsrc_id"] for h in o.sql("SELECT taskrsrc_id FROM TASKRSRC WHERE task_id = ? AND rsrc_id IS ?"
                                                    + _alive(o, "TASKRSRC") + " ORDER BY taskrsrc_id", task, rsrc)
                    if h["taskrsrc_id"] not in used), None)
        count("TASKRSRC", "updated" if hit is not None else "inserted")
        hit = hit if hit is not None else next(fresh)
        idmap["TASKRSRC"][r["taskrsrc_id"]] = hit
        used.add(hit)
    _upserts(o, count, idmap)
    so = [r for r in _rows(o, "SCHEDOPTIONS") if r.get("proj_id") in (None, xp["proj_id"])]
    if so:  # update mode writes the XER schedule options to PROJPROP 'scheduling'
        count("PROJPROP", _sched_action(o, so[0], tmap))
    return {"counts": counts, "links": touched_links, "asg": used, "tasks": set(tmap.values())}


def _upserts(o, count, idmap) -> None:
    """Activity code assignments keyed (activity, code type) and UDF values keyed (type, item): updated when the
    database (soft-deleted rows included) or an earlier row of the file has the key, else inserted; a key
    that cannot be mapped is skipped_unmapped."""
    done: set = set()
    for r in _rows(o, "TASKACTV"):
        key = (idmap["TASK"].get(r.get("task_id")), idmap["ACTVTYPE"].get(r.get("actv_code_type_id")))
        if None in key or idmap["ACTVCODE"].get(r.get("actv_code_id")) is None:
            count("TASKACTV", "skipped_unmapped")
            continue
        there = ("TASKACTV", key) in done or o.one("SELECT 1 FROM TASKACTV WHERE task_id = ? AND actv_code_type_id = ?",
                                                   *key)
        count("TASKACTV", "updated" if there else "inserted")
        done.add(("TASKACTV", key))
    subject = {u.get("udf_type_id"): u.get("table_name") for u in _rows(o, "UDFTYPE")}
    for r in _rows(o, "UDFVALUE"):
        tbl = subject.get(r.get("udf_type_id"))
        key = (idmap["UDFTYPE"].get(r.get("udf_type_id")),
               idmap.get(tbl, {}).get(r.get("fk_id")) if tbl in UDF_SUBJECTS else None)
        if None in key:
            count("UDFVALUE", "skipped_unmapped")
            continue
        there = ("UDFVALUE", key) in done or o.one("SELECT 1 FROM UDFVALUE WHERE udf_type_id = ? AND fk_id = ?", *key)
        count("UDFVALUE", "updated" if there else "inserted")
        done.add(("UDFVALUE", key))


FLOAT_OPTIONS = {"level_over_alloc_pct"}  # a percentage P6 stores with a decimal (25.0); other numbers are whole


def _written(key: str, v) -> str:
    """An XER option value as the schedule options text stores it: Y/N flags upper case, numbers in their
    stored form (a decimal for FLOAT_OPTIONS, a whole number when whole), tokens as they are."""
    s = str(v).strip()
    try:
        f = float(s)
    except ValueError:
        return s.upper() if s.upper() in ("Y", "N") else s
    return repr(f) if key in FLOAT_OPTIONS or not f.is_integer() else str(int(f))


def _lpl(text: str):
    """XER level priority list 'field,ASC_BY_FIELD/ORDER' per line (or ';') -> [(field, ORDER)], None if unreadable."""
    out = []
    for part in (p.strip() for p in re.split(r"[;\r\n]+", str(text))):
        if not part:
            continue
        field, s, rest = part.partition(",")
        order = (rest.rsplit("/", 1)[-1] if s else "ASC").strip().upper()
        if not re.fullmatch(r"\w+", field.strip()) or order not in ("ASC", "DESC"):
            return None
        out.append((field.strip(), order))
    return out or None


def _find(node, name):
    if node[0] == name:
        return node
    return next((f for f in (_find(k, name) for k in node[2]) if f), None)


def _sched_action(o, xs: dict, tmap: dict) -> str:
    """inserted without a stored row, restored for a soft-deleted one; else unchanged when the stored options
    already hold every XER value (numbers compared by value, an empty value keeps the stored one, no key
    activity = -99, a readable XER level priority list replaces the stored one), else updated."""
    rows = o.sql("SELECT * FROM PROJPROP WHERE proj_id = ? AND prop_name = 'scheduling'", o.pid)
    if not rows:
        return "inserted"
    if "delete_session_id" in {str(k).lower() for k in rows[0].keys()} and rows[0]["delete_session_id"]:  # noqa: SIM118
        return "restored"
    text = rows[0]["prop_value"]
    tree = _tree(text.decode("utf-8", "replace").rstrip("\x00") if isinstance(text, bytes) else text)
    stored = dict(zip(tree[1][::2], tree[1][1::2], strict=False))
    vals = {str(k).lower(): v for k, v in xs.items() if str(k).lower() not in ("schedoptions_id", "proj_id")}
    changed = []
    for k, v in vals.items():
        if k == "levelprioritylist":
            want = _lpl(v) if v else None
            node = _find(tree, "LevelPriorityList")
            got = [(n[0], dict(zip(n[1][::2], n[1][1::2], strict=False)).get("sort_type")) for n in node[2]] if node else None
            if want is not None and want != got:
                changed.append(k)
            continue
        if k == "key_activity_for_multiple_longest_paths":
            tid = None if (v or "").strip() in ("", "-99") else tmap.get(v.strip())
            new = "-99" if tid is None else str(tid)
        elif v is None:
            continue  # an empty XER value keeps the stored one
        else:
            new = _written(k, v)
        if stored.get(k) != new:  # the stored text changes
            changed.append(k)
    return "updated" if changed else "unchanged"


def counts(o):
    """One row per table of the counts, every action (0 when none)."""
    return [{"table": t, **{COLUMN[a]: c.get(a, 0) for a in ACTIONS}} for t, c in _update(o)["counts"].items()][:20]


@_cached("missing")
def _missing(o) -> dict:
    u = _update(o)
    acts = o.sql("SELECT task_id FROM TASK WHERE proj_id = ?" + _alive(o, "TASK"), o.pid)
    gone = {a["task_id"] for a in acts if a["task_id"] not in u["tasks"]}
    links = [r for r in o.sql("SELECT r.task_pred_id, r.task_id, r.pred_task_id FROM TASKPRED r JOIN TASK s ON "
                              "s.task_id = r.task_id JOIN TASK p ON p.task_id = r.pred_task_id WHERE s.proj_id = ? AND "
                              "p.proj_id = ?" + _alive(o, "TASKPRED", "r.") + _alive(o, "TASK", "s.")
                              + _alive(o, "TASK", "p.") + " ORDER BY r.task_pred_id", o.pid, o.pid)
             if r["task_pred_id"] not in u["links"]]
    rels = [r for r in links if not {r["task_id"], r["pred_task_id"]} & gone]
    asg = [r for r in o.sql("SELECT a.taskrsrc_id, a.task_id FROM TASKRSRC a JOIN TASK t ON t.task_id = a.task_id"
                            + _alive(o, "TASK", "t.") + " WHERE a.proj_id = ?" + _alive(o, "TASKRSRC", "a.")
                            + " ORDER BY a.taskrsrc_id", o.pid)
           if r["taskrsrc_id"] not in u["asg"]]
    kept = [r for r in asg if r["task_id"] not in gone]
    return {"acts": len(gone), "links": len(rels), "links_on": len(links) - len(rels), "asg": len(kept),
            "asg_on": len(asg) - len(kept)}


# ----------------------------------------------------------------- data date and refusal

def _data_dates(o) -> dict:
    db = o.one("SELECT last_recalc_date FROM PROJECT WHERE proj_id = ?", o.pid)
    xd = _xp(o)["last_recalc_date"]
    return {"database": db, "xer": xd, "older": bool(db and xd and xd < db)}


def _reasons(o) -> list:
    out = []
    errs = _preflight(o)["errors"]
    if errs:
        out.append(Contains("pre-flight failed", *(f"{e['check']} {e['count']}" for e in errs)))
    d = _data_dates(o)
    if d["older"]:
        out.append(Contains(d["xer"], "older", d["database"]))
    return out


def _dry_warnings(o) -> list:
    """Warnings of the import: an unmatched key activity, tables not handled. A schedule option token the
    server does not know is also reported there: such rows are not checked here."""
    out = []
    so = {str(k).lower(): v for k, v in (_rows(o, "SCHEDOPTIONS") or [{}])[0].items()}
    key = (so.get("key_activity_for_multiple_longest_paths") or "").strip()
    if key not in ("", "-99") and key not in {t["task_id"] for t in _rows(o, "TASK")}:
        out.append(Contains("key_activity_for_multiple_longest_paths", key))
    if so.get("levelprioritylist") and _lpl(so["levelprioritylist"]) is None:
        out.append(Contains("level priority list"))
    if any(t not in IMPORTED and t != "SCHEDOPTIONS" for t in _x(o)):
        out.append(Contains("Tables not handled"))
    return out


def _projects(o):
    tasks = xer(o)["tables"].get("TASK", [])
    return [{"project": p["proj_short_name"], "data_date": p.get("last_recalc_date"),
             "activities": sum(1 for t in tasks if t.get("proj_id") == p.get("proj_id"))}
            for p in xer(o)["tables"].get("PROJECT", [])]


def _needs_project(fn):
    """A value that needs the file's one project (several projects: the tool asks for a choice)."""
    return lambda o: fn(o) if _xp(o) is not None else Unchecked("the XER file holds several projects")


SLOTS = {
    "file_version": lambda o: xer(o)["header"][1],
    "file_date": lambda o: xer(o)["header"][2],
    "file_bytes": lambda o: os.path.getsize(o.args["xer_path"]),
    "encoding": lambda o: xer(o)["encoding"],
    "end_marker": lambda o: xer(o)["end"],
    "bad_chars": lambda o: xer(o)["bad"],
    "xer_project": _needs_project(lambda o: _xp(o)["proj_short_name"]),
    "dd_database": lambda o: _data_dates(o)["database"] if _xp(o) else Unchecked("several projects"),
    "dd_xer": _needs_project(lambda o: _data_dates(o)["xer"]),
    "dd_older": _needs_project(lambda o: _data_dates(o)["older"]),
    "would_refuse": _needs_project(lambda o: bool(_reasons(o))),
    "miss_acts": _needs_project(lambda o: _missing(o)["acts"]),
    "miss_links": _needs_project(lambda o: _missing(o)["links"]),
    "miss_links_on": _needs_project(lambda o: _missing(o)["links_on"]),
    "miss_asg": _needs_project(lambda o: _missing(o)["asg"]),
    "miss_asg_on": _needs_project(lambda o: _missing(o)["asg_on"]),
}
TABLES = {
    "xer_projects": lambda o: _projects(o)[:10],
    "file_tables": lambda o: [{"table": t, "rows": len(r)} for t, r in xer(o)["tables"].items()][:30],
    "pf_errors": _check_rows("errors"),
    "pf_warnings": _check_rows("warnings"),
    "pf_info": _check_rows("info"),
    "global_items": lambda o: global_items(o) if _xp(o) else [],
    "refuse": lambda o: [{"reason": r} for r in _reasons(o)] if _xp(o) else [],
    "counts": lambda o: counts(o) if _xp(o) else [],
    "dry_warnings": lambda o: [{"warning": w} for w in _dry_warnings(o)] if _xp(o) else [],
}
