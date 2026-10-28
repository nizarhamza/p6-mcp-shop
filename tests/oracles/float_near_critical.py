"""Oracles of float-near-critical: P6's TASK, CALENDAR and PROJECT rows read with SQL; the float statistics,
the ranges (compared in hours, never rounded), the float path summary and the near-critical order worked out
here in Python."""

from __future__ import annotations

import statistics

from oracles import HPD, SUMMARY_TYPES, Contains

EDGES = (-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 44.0)  # the default ranges of the float analysis, in days


def _open(o):
    """Open activities (not completed, LOE and WBS summary left out) with their floats in hours and days."""
    crit, cargs = o.critical_sql("t")
    return o.sql(f"SELECT t.task_id, t.task_code, t.task_name, t.status_code, t.total_float_hr_cnt AS tf_h, "
                 f"t.free_float_hr_cnt AS ff_h, {HPD} AS hpd, t.total_float_hr_cnt / {HPD} AS tf_d, "
                 f"t.free_float_hr_cnt / {HPD} AS ff_d, t.remain_drtn_hr_cnt / {HPD} AS rem_d, "
                 "t.early_start_date, t.early_end_date, t.act_start_date, t.float_path, t.driving_path_flag, "
                 f"({crit}) AS crit FROM TASK t LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id "
                 "WHERE t.proj_id = ? AND t.delete_session_id IS NULL AND t.status_code <> 'TK_Complete' "
                 "AND t.task_type NOT IN (?, ?)", *cargs, o.pid, *SUMMARY_TYPES)


def _tf_days(o):
    return [r["tf_d"] for r in _open(o) if r["tf_h"] is not None]


def _label(hours, hpd):
    """The range of a float in hours: below the first edge, [a, b) below zero, = 0, (a, b] above zero,
    above the last edge."""
    if hours is None:
        return None
    h = float(hours)
    if h == 0:
        return "= 0"
    if h < EDGES[0] * hpd:
        return f"< {EDGES[0]:g}"
    if h > EDGES[-1] * hpd:
        return f"> {EDGES[-1]:g}"
    for a, b in zip(EDGES, EDGES[1:], strict=False):
        if b <= 0 and a * hpd <= h < b * hpd:
            return f"[{a:g}, {b:g})"
        if a >= 0 and a * hpd < h <= b * hpd:
            return f"({a:g}, {b:g}]"
    raise AssertionError(hours)


def _labels():
    pairs = list(zip(EDGES, EDGES[1:], strict=False))
    return ([f"< {EDGES[0]:g}"] + [f"[{a:g}, {b:g})" for a, b in pairs if b <= 0] + ["= 0"]
            + [f"({a:g}, {b:g}]" for a, b in pairs if a >= 0] + [f"> {EDGES[-1]:g}"])


def buckets(o):
    acts = _open(o)
    n = len(acts)
    tf = [_label(a["tf_h"], a["hpd"]) for a in acts]
    ff = [_label(a["ff_h"], a["hpd"]) for a in acts]
    out = []
    for lab in _labels():
        t, f = tf.count(lab), ff.count(lab)
        out.append({"range": lab, "tf": t, "tf_pct": 100 * t / n if n else None, "ff": f,
                    "ff_pct": 100 * f / n if n else None})
    return out[:12]


def _covered(o):
    acts = _open(o)
    n = len(acts)
    return all(sum(1 for a in acts if _label(a[k], a["hpd"]) in _labels()) + sum(a[k] is None for a in acts) == n
               for k in ("tf_h", "ff_h"))


def _path_acts(o):
    """Open activities on a stored float path, in P6 order (path, order on the path, task_id)."""
    return o.sql(f"SELECT t.task_id, t.task_code, t.task_name, t.float_path, t.float_path_order, "
                 f"t.total_float_hr_cnt / {HPD} AS tf_d, t.early_start_date, t.early_end_date, "
                 "COALESCE(t.act_end_date, t.early_end_date) AS fin FROM TASK t "
                 "LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id WHERE t.proj_id = ? AND t.delete_session_id IS NULL "
                 "AND t.status_code <> 'TK_Complete' AND t.float_path IS NOT NULL "
                 "ORDER BY t.float_path, t.float_path_order, t.task_id", o.pid)


def _stored(o):
    return o.one("SELECT COUNT(*) FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL "
                 "AND float_path IS NOT NULL", o.pid) > 0


def paths(o):
    if not _stored(o):
        return []
    groups = {}
    for r in _path_acts(o):
        groups.setdefault(r["float_path"], []).append(r)
    return [{"path": p, "activities": len(g), "min_tf": min(r["tf_d"] for r in g if r["tf_d"] is not None),
             "max_tf": max(r["tf_d"] for r in g if r["tf_d"] is not None), "finish": max(r["fin"] for r in g)}
            for p, g in sorted(groups.items())][:10]


def path_rows(o):
    if _stored(o):
        rows = _path_acts(o)
    else:  # no float path stored: the longest path activities by start
        rows = sorted((r for r in _open(o) if r["driving_path_flag"] == "Y"),
                      key=lambda r: (r["act_start_date"] or r["early_start_date"], r["task_code"], r["task_id"]))
    return [{"path": r["float_path"], "order": r["float_path_order"] if _stored(o) else None,
             "activity": (r["task_code"], r["task_name"]), "tf": r["tf_d"], "start": r["early_start_date"],
             "finish": r["early_end_date"]} for r in rows][:30]


def _near(o):
    """Near-critical: open activities with total float above 0 and at or below near_days days of their
    calendar, by total float, then start (actual, else early), Activity ID."""
    rows = [r for r in _within(o) if r["tf_h"] > 0]
    return sorted(rows, key=lambda r: (r["tf_h"], r["act_start_date"] or r["early_start_date"], r["task_code"],
                                       r["task_id"]))


def _within(o):
    """Open activities with total float at or below near_days days of their calendar (critical included)."""
    days = float(o.args["near_days"])
    return [r for r in _open(o) if r["tf_h"] is not None and r["tf_h"] <= days * r["hpd"]]


def near(o):
    return [{"activity": (r["task_code"], r["task_name"]), "status": r["status_code"], "tf": r["tf_d"],
             "ff": r["ff_d"], "rem": r["rem_d"], "finish": r["early_end_date"], "path": r["float_path"]}
            for r in _near(o)][:30]


def _project(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _crit_definition(o):
    r = o.sql("SELECT critical_path_type, critical_drtn_hr_cnt FROM PROJECT WHERE proj_id = ?", o.pid)[0]
    if r["critical_path_type"] == "CT_DrivPath":
        return Contains("CT_DrivPath", "longest path")
    return Contains(r["critical_path_type"], f"total float <= {float(r['critical_drtn_hr_cnt'] or 0):g} h")


SLOTS = {
    "data_date": lambda o: _project(o, "last_recalc_date"),
    "last_f9": lambda o: _project(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "activities": lambda o: len(_open(o)),
    "no_tf": lambda o: sum(r["tf_h"] is None for r in _open(o)),
    "tf_min": lambda o: min(_tf_days(o)),
    "tf_max": lambda o: max(_tf_days(o)),
    "tf_mean": lambda o: statistics.fmean(_tf_days(o)),
    "tf_median": lambda o: statistics.median(_tf_days(o)),
    "negative": lambda o: sum(1 for v in _tf_days(o) if v < 0),
    "zero": lambda o: sum(1 for r in _open(o) if r["tf_h"] is not None and float(r["tf_h"]) == 0),
    "critical": lambda o: sum(1 for r in _open(o) if r["crit"]),
    "critical_definition": _crit_definition,
    "tf_not_whole": lambda o: sum(1 for r in _open(o) if r["tf_h"] is not None and float(r["tf_h"]) % float(r["hpd"])),
    "ranges_covered": _covered,
    "fp_source": lambda o: "float_path" if _stored(o) else "driving_path_flag",
    "longest_path": lambda o: sum(1 for r in _open(o) if r["driving_path_flag"] == "Y"),
    "within_near": lambda o: len(_within(o)),
    "near_total": lambda o: len(_near(o)),
    "near_definition": lambda o: Contains(f"total float <= {float(o.args['near_days']):g} d", "total float > 0 d"),
}
TABLES = {"buckets": buckets, "paths": paths, "path_rows": path_rows, "near": near}
