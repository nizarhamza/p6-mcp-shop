"""Oracles of resource-loading-review: P6's TASKRSRC, TASK, RSRC, RSRCRATE, PREFER and CALENDAR rows read with
SQL. Every assignment of the project (labor, nonlabor and material) is spread here over the working time of its
calendar (the resource's for a resource dependent activity, else the activity's; calendar time when the span has
no working time), with the curves and periods of the progress-earned-value oracle: budget on the planned dates,
actual from the actual start to the actual finish or the data date, remaining from the remaining dates. A
resource's rows run from its first to its last loaded period; its peak is the first period of highest load.
Available = working hours of the resource's calendar x its max units per hour (RSRCRATE by effective date, the
first rate also before its date, else RSRC.max_qty_per_hr), labor and nonlabor only, and only with a resource
calendar; over = load above available, both rounded to 2 decimals. The demo resources have no max units and no
calendar: what the demo proves is the quantities, the totals, the peaks, the absence of a limit (no_limit, over
and available n/a) and no over-allocated period. Resource curves and stored period actuals (TRSRCFIN) are not
modeled (Unchecked when the database has them)."""

from __future__ import annotations

from datetime import datetime

from oracles import Unchecked
from oracles import progress_earned_value as pev
from oracles.export_dashboard import cal

KINDS = {"RT_Labor": "labor", "RT_Equip": "nonlabor", "RT_Mat": "material"}
ORDER = {"labor": 0, "nonlabor": 0, "material": 1}


def _cached(o, key, fn):
    cache = o.__dict__.setdefault("_rl_cache", {})
    if key not in cache:
        cache[key] = fn()
    return cache[key]


def _cols(o, table) -> set:
    return {str(c["name"]).lower() for c in o.sql(f"PRAGMA table_info({table})")}


def _assignments(o):
    """Every assignment of the project with what pev.curves needs, its resource and its spread calendar."""
    res = o.args.get("resource")
    return o.sql("SELECT tr.rsrc_id, r.rsrc_short_name, r.rsrc_name, COALESCE(tr.rsrc_type, r.rsrc_type) AS rsrc_type, "
                 "r.clndr_id AS rsrc_clndr_id, CASE WHEN t.task_type = 'TT_Rsrc' AND r.clndr_id IS NOT NULL "
                 "THEN r.clndr_id ELSE t.clndr_id END AS spread_clndr_id, tr.target_qty, "
                 "COALESCE(tr.act_reg_qty, 0) + COALESCE(tr.act_ot_qty, 0) AS actual, tr.remain_qty, "
                 "tr.target_start_date, tr.target_end_date, tr.act_start_date, tr.act_end_date, tr.restart_date, "
                 "tr.reend_date, t.task_code, t.status_code, t.complete_pct_type, t.phys_complete_pct, "
                 "t.target_drtn_hr_cnt, t.remain_drtn_hr_cnt, "
                 "COALESCE(t.act_work_qty, 0) + COALESCE(t.act_equip_qty, 0) AS t_act, "
                 "COALESCE(t.remain_work_qty, 0) + COALESCE(t.remain_equip_qty, 0) AS t_rem "
                 "FROM TASKRSRC tr JOIN TASK t ON t.task_id = tr.task_id LEFT JOIN RSRC r ON r.rsrc_id = tr.rsrc_id "
                 "WHERE t.proj_id = ? AND tr.delete_session_id IS NULL AND t.delete_session_id IS NULL"
                 + (" AND r.rsrc_short_name = ?" if res else "") + " ORDER BY tr.taskrsrc_id",
                 *((o.pid, res) if res else (o.pid,)))


def _limits(o, rid):
    """[(effective date or None, max units per hour)] of a resource, [] without a limit."""
    out = {}
    if {"rsrc_id", "max_qty_per_hr"} <= _cols(o, "RSRCRATE"):
        date = "start_date" if "start_date" in _cols(o, "RSRCRATE") else "NULL"
        for r in o.sql(f"SELECT {date} AS d, max_qty_per_hr AS m FROM RSRCRATE WHERE rsrc_id = ? "
                       "AND max_qty_per_hr IS NOT NULL AND delete_session_id IS NULL ORDER BY rsrc_rate_id", rid):
            out[pev.dt(r["d"])] = float(r["m"])
    if out:
        return sorted(out.items(), key=lambda x: (x[0] is not None, x[0] or datetime.min))
    if "max_qty_per_hr" in _cols(o, "RSRC"):
        m = o.one("SELECT max_qty_per_hr FROM RSRC WHERE rsrc_id = ?", rid)
        if m is not None:
            return [(None, float(m))]
    return []


def _available(c, segs, a, b):
    tot = 0.0
    for k, (_d, m) in enumerate(segs):
        lo = a if k == 0 else max(a, segs[k][0])
        hi = b if k + 1 == len(segs) else min(b, segs[k + 1][0])
        if hi > lo:
            tot += c.work_hours(lo, hi) * m
    return tot


def _r2(v):
    return None if v is None else round(v, 2)


def load(o) -> dict:
    def build():
        dd = pev.data_date(o)
        groups = {}
        for r in _assignments(o):
            groups.setdefault(r["rsrc_id"], []).append(r)
        items = {rid: pev.curves(g, dd) for rid, g in groups.items()}
        dates = [d for c in items.values() for k in ("planned", "actual", "remaining") for it in c[k] for d in it[1:3]]
        week_day = int(o.one("SELECT week_start_day_num FROM PREFER") or 1)
        period = o.args.get("period") or "month"
        edges = pev._edges(min(dates), max(dates), period, week_day) if dates else []
        meta = []
        for rid, g in groups.items():
            kind = KINDS.get(g[0]["rsrc_type"], "other")
            meta.append((ORDER.get(kind, 2), rid is None, g[0]["rsrc_short_name"] or "(no resource)", rid or 0, rid,
                         kind))
        rows, resources, no_limit = [], [], []
        for *_k, rid, kind in sorted(meta):
            g, c = groups[rid], items[rid]
            first = g[0]
            rc = cal(o, first["rsrc_clndr_id"]) if first["rsrc_clndr_id"] is not None else None
            segs = _limits(o, rid) if kind in ("labor", "nonlabor") and rid is not None else []
            cap = rc is not None and not rc.error and bool(segs)
            if kind in ("labor", "nonlabor") and not cap:
                no_limit.append(first["rsrc_short_name"])
            per = []
            for a, b in zip(edges, edges[1:], strict=False):
                per.append({k: pev.cum_work(o, c[k], b) - pev.cum_work(o, c[k], a)
                            for k in ("planned", "actual", "remaining")})
            used = [i for i, p in enumerate(per) if any(abs(v) > 1e-9 for v in p.values())]
            mine, peak, n_over = [], None, 0
            for i in range(used[0], used[-1] + 1) if used else ():
                a, b, p = edges[i], edges[i + 1], per[i]
                act = p["actual"] if a <= dd else None
                ld = (act or 0.0) + p["remaining"]
                avail = _available(rc, segs, a, b) if cap else None
                over = None if avail is None else round(ld, 2) > round(avail, 2)
                n_over += bool(over)
                row = {"resource": (first["rsrc_short_name"], first["rsrc_name"]),
                       "period": a.strftime("%Y-%m") if period == "month" else a.strftime("%Y-%m-%d"),
                       "load": ld, "available": avail, "load_pct": 100 * ld / avail if avail else None, "over": over,
                       "over_by": ld - avail if over else (None if over is None else 0.0)}
                mine.append(row)
                if peak is None or ld > peak["load"] + 1e-9:
                    peak = row
            rows += mine

            def q(k, g=g):
                return sum(float(r[k] or 0) for r in g)
            now = next((m for d, m in reversed(segs) if d is None or d <= dd), segs[0][1]) if segs else None
            unit = o.one("SELECT u.unit_abbrev FROM RSRC r JOIN UMEASURE u ON u.unit_id = r.unit_id WHERE r.rsrc_id = ?",
                         rid) if {"unit_id"} <= _cols(o, "RSRC") and {"unit_id", "unit_abbrev"} <= _cols(o, "UMEASURE")                 else None
            resources.append({"resource": (first["rsrc_short_name"], first["rsrc_name"]), "kind": kind,
                              "unit": unit or ("h" if kind in ("labor", "nonlabor") else None),
                              "budget": q("target_qty"), "actual": q("actual"), "remaining": q("remain_qty"),
                              "at_completion": q("actual") + q("remain_qty"), "max_units": now,
                              "peak_period": peak and peak["period"], "peak_load": peak and _r2(peak["load"]),
                              "peak_available": peak and peak["available"], "peak_pct": peak and peak["load_pct"],
                              "over_periods": n_over if cap else None})
        return {"rows": rows, "resources": resources, "no_limit": no_limit,
                "over_periods": sum(r["over_periods"] or 0 for r in resources),
                "resources_over": sum(bool(r["over_periods"]) for r in resources),
                "material": sum(r["kind"] == "material" for r in resources)}
    return _cached(o, "load", build)


def t_resources(o):
    if pev._not_modeled(o):
        return Unchecked("resource curves or period actuals (TRSRCFIN) are not modeled")
    keys = ("resource", "kind", "unit", "budget", "actual", "remaining", "at_completion", "max_units", "peak_period",
            "peak_load", "peak_available", "peak_pct", "over_periods")
    return [{k: r[k] for k in keys} for r in load(o)["resources"]][:30]


def t_over(o):
    """Over-allocated periods among the first page of 200 resource periods (the call's page)."""
    if pev._not_modeled(o):
        return Unchecked("resource curves or period actuals (TRSRCFIN) are not modeled")
    return [{k: r[k] for k in ("resource", "period", "load", "available", "load_pct", "over_by")}
            for r in load(o)["rows"][:200] if r["over"]][:30]


SLOTS = {
    "data_date": lambda o: o.one("SELECT last_recalc_date FROM PROJECT WHERE proj_id = ?", o.pid),
    "last_f9": lambda o: o.one("SELECT last_schedule_date FROM PROJECT WHERE proj_id = ?", o.pid),
    "stale": lambda o: o.stale(),
    "total_rows": lambda o: len(load(o)["rows"]),
    "res_count": lambda o: len(load(o)["resources"]),
    "over_periods": lambda o: load(o)["over_periods"],
    "res_over": lambda o: load(o)["resources_over"],
    "material": lambda o: load(o)["material"],
    "no_limit": lambda o: load(o)["no_limit"],
}
TABLES = {"resources": t_resources, "over": t_over}
