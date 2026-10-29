"""Oracles of logic-date-integrity: P6's PROJECT, TASK, TASKPRED, CALENDAR and PROJPROP rows read with SQL; the
engine's values from the small CPM of the delay-whatif oracles (forward and backward pass on the parsed
calendars), compared with the stored F9 as p6_cpm_validate does (dates within a minute, total float within 3
minutes); the schedule options parsed from PROJPROP 'scheduling'."""

from __future__ import annotations

from oracles import SUMMARY_TYPES, Contains, Unchecked
from oracles.delay_whatif import TF_TOL_H, _stored, cpm, limits
from oracles.milestone_tracker import _tree, network, text

ENGINE_VERSION = 1  # the version P6 MCP 1.10.0 documents for its CPM rules (bumped with them)
FIELDS = (("es", "early start"), ("ef", "early finish"), ("ls", "late start"), ("lf", "late finish"))

_CACHE: dict = {}


def engine(o) -> dict:
    """{net, res, open, done, bad_open, bad_done, rows, why} of the project, computed once."""
    key = (o.db, o.pid)
    if key not in _CACHE:
        net = network(o)
        why = limits(net)
        own = {n: a for n, a in net["acts"].items() if not a["ext"]}
        res = {}
        try:
            res = cpm(net)
        except ValueError as e:
            why.append(f"the oracle CPM failed: {e}")
        rows, bad_open, bad_done = [], 0, 0
        for n, a in sorted(own.items(), key=lambda e: (e[1]["status_code"] == "TK_Complete", e[1]["task_code"])):
            if n not in res:
                continue
            s, r, done = _stored(a), res[n], a["status_code"] == "TK_Complete"
            diff = [label for k, label in FIELDS if not (done and k in ("ls", "lf"))
                    and (s[k] is None or abs((r[k] - s[k]).total_seconds()) > 60)]
            if not done and (s["tf"] is None or abs(r["tf"] - s["tf"]) > TF_TOL_H):
                diff.append("total float (d)")
            if diff:
                bad_done += done
                bad_open += not done
                rows.append({"activity": (a["task_code"], a["task_name"]), "status": a["status_code"],
                             "diff": Contains(*diff), "cause": lambda v: isinstance(v, str) and bool(v)})
        n_open = sum(a["status_code"] != "TK_Complete" for a in own.values())
        _CACHE[key] = {"net": net, "res": res, "open": n_open, "done": len(own) - n_open, "bad_open": bad_open,
                       "bad_done": bad_done, "rows": rows, "why": why}
    return _CACHE[key]


def checked(fn):
    def wrapped(o):
        why = engine(o)["why"]
        return Unchecked("logic-date-integrity engine: " + "; ".join(why)) if why else fn(o)
    return wrapped


def _rate(bad, total):
    return None if not total else round(1 - bad / total, 4)


def _finish(o):
    e = engine(o)
    own = [n for n, a in e["net"]["acts"].items() if not a["ext"] and a["task_type"] not in SUMMARY_TYPES]
    return text(max(e["res"][n]["ef"] for n in own))


def _prj(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def sched_tree(o, pid):
    """(attributes, children) of the project's PROJPROP 'scheduling' row, None when there is none."""
    row = o.sql("SELECT prop_value FROM PROJPROP WHERE proj_id = ? AND prop_name = 'scheduling' "
                "AND delete_session_id IS NULL", pid)
    if not row:
        return None
    v = row[0]["prop_value"]
    _name, attrs, kids = _tree(v.decode("utf-8", "replace") if isinstance(v, bytes) else v or "")
    return dict(zip(attrs[::2], attrs[1::2], strict=False)), kids


def sched_rows(o, pid) -> list:
    """The stored options as p6_schedule_options lists them for a project alone: every key by name, the key
    activity as an Activity ID ('(none)' for -99 or empty), the level priority list last ('field:ORDER')."""
    tree = sched_tree(o, pid)
    if tree is None:
        return []
    kv, kids = tree
    rows = []
    for k in sorted(kv):
        v = kv[k]
        if k == "key_activity_for_multiple_longest_paths":
            code = None if v.strip() in ("", "-99") else o.one("SELECT task_code FROM TASK WHERE task_id = ?", int(v))
            v = "(none)" if v.strip() in ("", "-99") else code or f"{v} (not in this database: none)"
        rows.append({"option": k, "value": v})
    for name, _a, sub in kids:
        if name == "LevelPriorityList":
            rows.append({"option": "levelprioritylist",
                         "value": ";".join(f"{n}:{(a[1::2] or ['ASC'])[-1]}" for n, a, _k in sub)})
    return rows


SLOTS = {
    "data_date": lambda o: _prj(o, "last_recalc_date"),
    "last_f9": lambda o: _prj(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "match_rate": checked(lambda o: _rate(engine(o)["bad_open"], engine(o)["open"])),
    "match_done": checked(lambda o: _rate(engine(o)["bad_done"], engine(o)["done"])),
    "trusted": checked(lambda o: (_rate(engine(o)["bad_open"], engine(o)["open"]) or 0) >= 0.99),
    "n_open": lambda o: engine(o)["open"],
    "n_open_bad": checked(lambda o: engine(o)["bad_open"]),
    "n_done": lambda o: engine(o)["done"],
    "n_done_bad": checked(lambda o: engine(o)["bad_done"]),
    "finish_engine": checked(_finish),
    "finish_stored": lambda o: _prj(o, "scd_end_date"),
    "rules": lambda o: Contains("retained logic", "lag rule calendar", "must finish date", "leveling not modelled"),
    "engine_version": lambda o: ENGINE_VERSION,
    "opt_source": lambda o: "PROJPROP scheduling" if sched_tree(o, o.pid) is not None else Contains("none stored"),
    "lag_rule": lambda o: (sched_tree(o, o.pid) or ({}, []))[0].get("sched_calendar_on_relationship_lag",
                                                                         "rcal_Predecessor"),
}
TABLES = {
    "mismatched": checked(lambda o: engine(o)["rows"][:15]),
    "options": lambda o: sched_rows(o, o.pid)[:40],
}
