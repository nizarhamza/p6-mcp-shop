"""Oracles of trend-report: each update's PROJECT, TASK, TASKPRED, TASKRSRC and CALENDAR rows read with SQL. The
series is ordered here (data date, last F9, Project ID); finish variances are working days of each update's
project calendar (the calendar parser of oracles.export_dashboard); units %, baseline planned % and SPI come from
the progress-earned-value oracle, the DCMA weighted score, failed checks and BEI from the schedule-quality-audit
oracle, both run on an Oracle of each update; float counts, the milestones followed and the changes since the
previous update (activities by Activity ID, links by predecessor, successor, type and predecessor project,
durations cut) are counted again here."""

from __future__ import annotations

import statistics
from datetime import datetime

from oracles import SUMMARY_TYPES, Oracle, Unchecked
from oracles import progress_earned_value as pev
from oracles import schedule_quality_audit as sqa
from oracles.export_dashboard import cal

MILESTONES = ("TT_Mile", "TT_FinMile")
MS_CAP = 20  # milestones followed without codes=
CUT_TOL_H = 0.05  # a duration shorter by more than 3 minutes is cut


def _cached(o, key, fn):
    cache = o.__dict__.setdefault("_trend_cache", {})
    if key not in cache:
        cache[key] = fn()
    return cache[key]


def _names(o) -> list[str]:
    """The Project IDs of the series: updates= (values separated by commas), else the projects of the EPS eps=
    and of the EPS below it (baselines and templates left out)."""
    given = [p.strip() for p in (o.args.get("updates") or "").split(",") if p.strip()]
    if given:
        return given
    eps = o.args.get("eps")
    nodes = {o.one("SELECT w.wbs_id FROM PROJWBS w JOIN PROJECT p ON p.proj_id = w.proj_id WHERE p.proj_short_name = ? "
                   "AND w.proj_node_flag = 'Y'", eps)}
    rows = o.sql("SELECT w.wbs_id, w.parent_wbs_id, p.proj_short_name, p.project_flag, p.orig_proj_id, p.status_code "
                 "FROM PROJWBS w JOIN PROJECT p ON p.proj_id = w.proj_id WHERE w.proj_node_flag = 'Y'")
    grew = True
    while grew:
        more = {r["wbs_id"] for r in rows if r["project_flag"] == "N" and r["parent_wbs_id"] in nodes}
        grew = not more <= nodes
        nodes |= more
    return sorted(r["proj_short_name"] for r in rows if r["project_flag"] == "Y" and r["parent_wbs_id"] in nodes
                  and r["orig_proj_id"] is None and (r["status_code"] or "") != "WS_Template")


def updates(o) -> list[Oracle]:
    """An Oracle per update, ordered by data date, then last F9, then Project ID."""
    def load():
        out = [Oracle(o.db, o.work, {"project": n}) for n in _names(o)]
        return sorted(out, key=lambda u: (pev.dt(_p(u, "last_recalc_date")),
                                          pev.dt(_p(u, "last_schedule_date")) or datetime.min, u.args["project"]))
    return _cached(o, "updates", load)


def _p(u, col):
    return u.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", u.pid)


def _wd(c, a, b):
    """Working days of calendar c from a to b (None without both dates or a readable calendar)."""
    a, b = pev.dt(a), pev.dt(b)
    if a is None or b is None or c.error:
        return None
    return c.work_hours(a, b) / c.hpd


def _open_tasks(u):
    return u.sql(f"SELECT t.*, {sqa.HPD} AS hpd FROM TASK t LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id "
                 f"WHERE t.proj_id = ? AND t.delete_session_id IS NULL AND t.status_code <> 'TK_Complete' "
                 f"AND t.task_type NOT IN {SUMMARY_TYPES}", u.pid)


def _dcma(u) -> dict:
    checks = sqa._dcma(u)
    w = sqa._weighted(u)
    if isinstance(checks["critical_path_test"]["pass"], Unchecked):
        why = "failed checks: the critical path test's pass is not recomputed here"
        failed = Unchecked(why)
    else:
        failed = [k for k, v in checks.items() if k not in (*sqa.UNSCORED, "key_dates") and v["pass"] is False]
    return {"points": w["points"], "grade": w["grade"], "failed": failed, "bei": checks["bei"]["value"],
            "bei_pass": checks["bei"]["pass"]}


def _acts(u) -> dict:
    """Activity ID -> the activity of the lowest task_id."""
    out = {}
    for r in u.sql("SELECT task_code, task_type, status_code, target_drtn_hr_cnt, remain_drtn_hr_cnt FROM TASK "
                   "WHERE proj_id = ? AND delete_session_id IS NULL ORDER BY task_id", u.pid):
        out.setdefault(r["task_code"], r)
    return out


def _links(u) -> set:
    """(predecessor, successor, type, predecessor project or None inside the project) of links into the update."""
    return {(r["pred"], r["succ"], r["pred_type"], None if r["pp"] == u.pid else r["pname"]) for r in u.sql(
        "SELECT pt.task_code AS pred, st.task_code AS succ, r.pred_type, pt.proj_id AS pp, p.proj_short_name AS pname "
        "FROM TASKPRED r JOIN TASK st ON st.task_id = r.task_id JOIN TASK pt ON pt.task_id = r.pred_task_id "
        "JOIN PROJECT p ON p.proj_id = pt.proj_id WHERE st.proj_id = ? AND r.delete_session_id IS NULL "
        "AND st.delete_session_id IS NULL AND pt.delete_session_id IS NULL", u.pid)}


def _changes(u, prev) -> dict:
    a, b = _acts(u), _acts(prev)
    cut = 0
    for c in set(a) & set(b):
        x, y = a[c], b[c]
        if x["task_type"] in (*SUMMARY_TYPES, *MILESTONES) or "TK_NotStart" != x["status_code"] \
                or y["status_code"] != "TK_NotStart":
            continue
        if (y["target_drtn_hr_cnt"] or 0) - (x["target_drtn_hr_cnt"] or 0) > CUT_TOL_H \
                or (y["remain_drtn_hr_cnt"] or 0) - (x["remain_drtn_hr_cnt"] or 0) > CUT_TOL_H:
            cut += 1
    la, lb = _links(u), _links(prev)
    return {"since": prev.args["project"], "activities_added": len(set(a) - set(b)),
            "activities_removed": len(set(b) - set(a)), "links_added": len(la - lb), "links_removed": len(lb - la),
            "durations_cut": cut}


def _milestones(u) -> dict:
    """Activity ID -> (date, kind, status, name, type, clndr_id) of the update's milestones (lowest task_id)."""
    out = {}
    for r in u.sql("SELECT * FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL AND task_type IN "
                   "('TT_Mile', 'TT_FinMile') ORDER BY task_id", u.pid):
        k = "start" if r["task_type"] == "TT_Mile" else "end"
        date, kind = (r[f"act_{k}_date"], "actual") if r[f"act_{k}_date"] else (r[f"early_{k}_date"], "forecast")
        out.setdefault(r["task_code"], (date, kind, r["status_code"], r["task_name"], r["task_type"], r["clndr_id"]))
    return out


def followed(o) -> list[str]:
    """Milestones in every update, by date in the latest update, then Activity ID; the first MS_CAP."""
    ups = updates(o)
    present = [_milestones(u) for u in ups]
    pool = set.intersection(*(set(p) for p in present))
    return sorted(pool, key=lambda c: (pev.dt(present[-1][c][0]) or datetime.max, c))[:MS_CAP]


def rows(o) -> list[dict]:
    def load():
        ups, out = updates(o), []
        near = float(o.args.get("near_days") or 10)
        first_f = _p(ups[0], "scd_end_date")
        keys = followed(o)
        for i, u in enumerate(ups):
            pc = cal(u, _p(u, "clndr_id"))
            fin, prev = _p(u, "scd_end_date"), ups[i - 1] if i else None
            bid = _p(u, "sum_base_proj_id")
            bl_fin = u.one("SELECT scd_end_date FROM PROJECT WHERE proj_id = ?", bid) if bid else None
            ts = _open_tasks(u)
            cond, args = u.critical_sql("t")
            crit = {r["task_id"] for r in u.sql(f"SELECT t.task_id FROM TASK t WHERE t.proj_id = ? AND {cond}",
                                                u.pid, *args)}
            days = sorted(t["total_float_hr_cnt"] / t["hpd"] for t in ts if t["total_float_hr_cnt"] is not None)
            ms, ms_prev, ms_first = _milestones(u), _milestones(prev) if prev else {}, _milestones(ups[0])
            items = []
            for c in keys:
                date, kind, status, *_x, clndr = ms[c]
                mc = cal(u, clndr)
                items.append({"task_code": c, "date": date, "date_kind": kind, "status_code": status,
                              "slip_wd": _wd(mc, ms_prev[c][0], date) if prev else None,
                              "variance_first_wd": _wd(mc, ms_first[c][0], date)})
            ev = pev.earned_value(u)
            out.append({
                "update": i + 1, "project": u.args["project"], "data_date": _p(u, "last_recalc_date"),
                "finish": fin, "must_finish": _p(u, "plan_end_date"), "stale": u.stale(),
                "finish_vs_must_finish_wd": _wd(pc, _p(u, "plan_end_date"), fin),
                "finish_variance_first_wd": _wd(pc, first_f, fin),
                "finish_variance_previous_wd": _wd(pc, _p(prev, "scd_end_date"), fin) if prev else None,
                "baseline_finish_variance_wd": _wd(pc, bl_fin, fin) if bid else None,
                "units_pct": pev.percent(u)["units"], "planned_units_pct": pev.bl_planned_pct(u),
                "spi_units": ev["spi"],
                "critical": sum(t["task_id"] in crit for t in ts),
                "near_critical": sum(t["task_id"] not in crit and t["total_float_hr_cnt"] is not None
                                     and t["total_float_hr_cnt"] <= near * t["hpd"] for t in ts),
                "negative_float": sum((t["total_float_hr_cnt"] or 0) < 0 for t in ts),
                "min_d": days[0] if days else None, "median_d": statistics.median(days) if days else None,
                "dcma": _dcma(u), "changes": _changes(u, prev) if prev else None, "milestones": items})
        return out
    return _cached(o, "rows", load)


def _last(key):
    return lambda o: rows(o)[-1][key]


def _ch(r, key):
    return None if r["changes"] is None else r["changes"][key]


def t_updates(o):
    return [{"update": r["update"], "project": r["project"], "data_date": r["data_date"], "finish": r["finish"],
             "must": r["must_finish"], "vs_must": r["finish_vs_must_finish_wd"], "vs_first": r["finish_variance_first_wd"],
             "vs_prev": r["finish_variance_previous_wd"], "vs_bl": r["baseline_finish_variance_wd"], "stale": r["stale"]}
            for r in rows(o)][:20]


def t_progress(o):
    return [{"project": r["project"], "units_pct": r["units_pct"], "planned_pct": r["planned_units_pct"],
             "spi": r["spi_units"], "critical": r["critical"], "near": r["near_critical"], "neg": r["negative_float"],
             "min_tf": r["min_d"], "median_tf": r["median_d"]} for r in rows(o)][:20]


def t_quality(o):
    return [{"project": r["project"], "points": r["dcma"]["points"], "grade": r["dcma"]["grade"],
             "failed": r["dcma"]["failed"], "bei": r["dcma"]["bei"], "bei_pass": r["dcma"]["bei_pass"]}
            for r in rows(o)][:20]


def t_changes(o):
    return [{"project": r["project"], "since": _ch(r, "since"), "added": _ch(r, "activities_added"),
             "removed": _ch(r, "activities_removed"), "links_added": _ch(r, "links_added"),
             "links_removed": _ch(r, "links_removed"), "cuts": _ch(r, "durations_cut")} for r in rows(o)][:20]


def t_milestones(o):
    ups = updates(o)
    present = [_milestones(u) for u in ups]
    out = []
    for c in followed(o):
        _d, _k, _s, name, typ, _c = next(p[c] for p in reversed(present) if c in p)
        out.append({"milestone": (c, name), "type": typ, "updates": sum(c in p for p in present)})
    return out


def t_ms_latest(o):
    return [{"code": m["task_code"], "date": m["date"], "kind": m["date_kind"], "status": m["status_code"],
             "slip": m["slip_wd"], "variance": m["variance_first_wd"]} for m in rows(o)[-1]["milestones"]]


def t_notes(o):
    """The tool's notes: Activity IDs of codes= not found, or more than MS_CAP milestones in every update."""
    ups = updates(o)
    pool = set.intersection(*(set(_milestones(u)) for u in ups))
    if len(pool) > MS_CAP:
        return Unchecked("more milestones than the cap: the note's wording is the tool's")
    return []


SLOTS = {
    "total": lambda o: len(updates(o)),
    "first_dd": lambda o: _p(updates(o)[0], "last_recalc_date"),
    "last_dd": lambda o: _p(updates(o)[-1], "last_recalc_date"),
    "near_d": lambda o: float(o.args.get("near_days") or 10),
    "last_project": _last("project"),
    "last_vs_prev": _last("finish_variance_previous_wd"),
    "last_neg": _last("negative_float"),
    "last_failed": lambda o: rows(o)[-1]["dcma"]["failed"],
    "last_cuts": lambda o: _ch(rows(o)[-1], "durations_cut"),
    "last_removed": lambda o: _ch(rows(o)[-1], "activities_removed"),
    "last_stale": _last("stale"),
}
TABLES = {"updates": t_updates, "progress": t_progress, "quality": t_quality, "changes": t_changes,
          "milestones": t_milestones, "ms_latest": t_ms_latest, "notes": t_notes}
