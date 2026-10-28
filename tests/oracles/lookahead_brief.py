"""Oracles of lookahead-brief: P6's TASK, CALENDAR and PROJECT rows read with SQL; the window, its weeks, the
categories, the forecast dates and the week of each date worked out here in Python."""

from __future__ import annotations

from datetime import datetime, timedelta

from oracles import HPD, SUMMARY_TYPES, Contains

FMT = "%Y-%m-%d %H:%M:%S"
CATEGORIES = ("in_progress", "starting", "finishing", "spanning")  # the documented order of row.window


def _dt(v):
    if v is None:
        return None
    s = str(v).replace("T", " ")
    for f in (FMT, "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:len(datetime(2000, 1, 1).strftime(f))], f)
        except ValueError:
            continue
    raise ValueError(f"not a date: {v!r}")


def _window(o):
    """(from, to, days): from the data date, weeks x 7 calendar days, end excluded."""
    frm = _dt(o.one("SELECT last_recalc_date FROM PROJECT WHERE proj_id = ?", o.pid))
    days = 7 * int(o.args["weeks"])
    return frm, frm + timedelta(days=days), days


def _week(d, frm, to):
    return int((d - frm).total_seconds() // (7 * 86400)) + 1 if d is not None and frm <= d < to else None


def _rows(o, critical_only=False):
    """The activities of the window in the documented order (forecast start, remaining finish, Activity ID)."""
    frm, to, _days = _window(o)
    crit, cargs = o.critical_sql("t")
    acts = o.sql(f"SELECT t.task_id, t.task_code, t.task_name, t.status_code, t.restart_date, t.early_start_date, "
                 "t.reend_date, t.early_end_date, t.act_start_date, t.act_end_date, "
                 f"t.total_float_hr_cnt / {HPD} AS tf_d, ({crit}) AS crit "
                 "FROM TASK t LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id "
                 "WHERE t.proj_id = ? AND t.delete_session_id IS NULL AND t.task_type NOT IN (?, ?)",
                 *cargs, o.pid, *SUMMARY_TYPES)
    out = []
    for a in acts:
        st = a["status_code"]
        rs_raw = a["restart_date"] or a["early_start_date"]
        rf_raw = a["reend_date"] or a["early_end_date"]
        rs, rf = _dt(rs_raw), _dt(rf_raw)
        cats = {
            "in_progress": st == "TK_Active",
            "starting": st == "TK_NotStart" and rs is not None and frm <= rs < to,
            "finishing": st != "TK_Complete" and rf is not None and frm <= rf < to,
            "spanning": st == "TK_NotStart" and rs is not None and rf is not None and rs < frm and rf >= to,
        }
        if not any(cats.values()):
            continue
        is_crit = st != "TK_Complete" and bool(a["crit"])
        if critical_only and not is_crit:
            continue
        f_st = a["act_start_date"] or rs_raw
        f_fin = a["act_end_date"] if st == "TK_Complete" else rf_raw
        key = (_dt(f_st) or datetime.max, rf or datetime.max, a["task_code"], a["task_id"])
        out.append((key, {"activity": (a["task_code"], a["task_name"]), "status": st, "start": f_st, "finish": f_fin,
                          "start_week": _week(_dt(f_st), frm, to), "finish_week": _week(_dt(f_fin), frm, to),
                          "tf": a["tf_d"], "critical": is_crit, "_cats": cats,
                          "categories": [k for k in CATEGORIES if cats[k]]}))
    return [r for _k, r in sorted(out, key=lambda x: x[0])]


def _table(rows, cap):
    return [{k: v for k, v in r.items() if k != "_cats"} for r in rows[:cap]]


def _count(o, cat):
    rows = _rows(o)
    if cat == "critical":
        return sum(r["critical"] for r in rows)
    return sum(r["_cats"][cat] for r in rows)


def weeks(o):
    frm, to, days = _window(o)
    return [{"week": k + 1, "from": (frm + timedelta(days=7 * k)).strftime(FMT),
             "to": min(to, frm + timedelta(days=7 * k + 7)).strftime(FMT)} for k in range((days + 6) // 7)][:13]


def _project(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _crit_definition(o):
    r = o.sql("SELECT critical_path_type, critical_drtn_hr_cnt FROM PROJECT WHERE proj_id = ?", o.pid)[0]
    if r["critical_path_type"] == "CT_DrivPath":
        return Contains("CT_DrivPath", "longest path", "open activities")
    return Contains(r["critical_path_type"], f"total float <= {float(r['critical_drtn_hr_cnt'] or 0):g} h",
                    "open activities")


SLOTS = {
    "data_date": lambda o: _project(o, "last_recalc_date"),
    "last_f9": lambda o: _project(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "window_from": lambda o: _window(o)[0].strftime(FMT),
    "window_to": lambda o: _window(o)[1].strftime(FMT),
    "window_days": lambda o: _window(o)[2],
    "listed": lambda o: len(_rows(o)),
    "in_progress": lambda o: _count(o, "in_progress"),
    "starting": lambda o: _count(o, "starting"),
    "finishing": lambda o: _count(o, "finishing"),
    "spanning": lambda o: _count(o, "spanning"),
    "critical": lambda o: _count(o, "critical"),
    "critical_definition": _crit_definition,
}
TABLES = {
    "weeks": weeks,
    "critical": lambda o: _table(_rows(o, critical_only=True), 30),
    "all": lambda o: _table(_rows(o), 50),
}
