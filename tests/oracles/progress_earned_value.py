"""Oracles of progress-earned-value: P6's TASK, TASKRSRC, RSRC, PROJWBS, PROJECT, PREFER and CALENDAR rows read
with SQL; the spread of the assignment quantities, the earned value, the periods and the WBS rollups worked out
here. Values at the data date spread linearly over calendar time between the dates (the app's planned value
definition); the periods (since 3.5.0) spread each assignment over the working time of its calendar (the
resource's calendar for a resource dependent activity, else the activity's; calendar time when the span has no
working time), counted on the calendar parser of oracles.export_dashboard. Resource curves and stored period
actuals (TRSRCFIN) are not modeled: the demo has neither, and the periods table is Unchecked when a project
has them. baseline-variance imports the earned value helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from oracles import Contains, Unchecked
from oracles.export_dashboard import cal

LABOR = ("RT_Labor", "RT_Equip")  # labor and nonlabor: the units measure


def dt(v):
    """A database date as datetime (None stays None)."""
    if v in (None, ""):
        return None
    return datetime.fromisoformat(str(v).replace("T", " ")[:19])


def _n(v) -> float:
    return float(v or 0)


def baseline_pid(o):
    """The baseline compared with: the baseline argument, else PROJECT.sum_base_proj_id."""
    name = o.args.get("baseline")
    if name:
        return o.one("SELECT proj_id FROM PROJECT WHERE proj_short_name = ?", name)
    return o.one("SELECT sum_base_proj_id FROM PROJECT WHERE proj_id = ?", o.pid)


def data_date(o, pid=None):
    return dt(o.one("SELECT last_recalc_date FROM PROJECT WHERE proj_id = ?", o.pid if pid is None else pid))


def assignments(o, pid):
    """Labor and nonlabor assignments of a project with the activity fields of its % complete and the calendar
    its quantities are spread on (spread_clndr_id)."""
    return o.sql("SELECT CASE WHEN t.task_type = 'TT_Rsrc' AND r.clndr_id IS NOT NULL THEN r.clndr_id ELSE t.clndr_id "
                 "END AS spread_clndr_id, tr.target_qty, COALESCE(tr.act_reg_qty, 0) + COALESCE(tr.act_ot_qty, 0) AS actual, tr.remain_qty, "
                 "tr.target_start_date, tr.target_end_date, tr.act_start_date, tr.act_end_date, tr.restart_date, "
                 "tr.reend_date, t.task_code, t.status_code, t.complete_pct_type, t.phys_complete_pct, "
                 "t.target_drtn_hr_cnt, t.remain_drtn_hr_cnt, "
                 "COALESCE(t.act_work_qty, 0) + COALESCE(t.act_equip_qty, 0) AS t_act, "
                 "COALESCE(t.remain_work_qty, 0) + COALESCE(t.remain_equip_qty, 0) AS t_rem "
                 "FROM TASKRSRC tr JOIN TASK t ON t.task_id = tr.task_id LEFT JOIN RSRC r ON r.rsrc_id = tr.rsrc_id "
                 "WHERE t.proj_id = ? AND COALESCE(tr.rsrc_type, r.rsrc_type) IN ('RT_Labor', 'RT_Equip') "
                 "AND tr.delete_session_id IS NULL AND t.delete_session_id IS NULL ORDER BY tr.taskrsrc_id", pid)


def activity_pct(r) -> float:
    """Activity % complete by its percent complete type (P6 earned value with activity % complete)."""
    kind, done = r["complete_pct_type"], 100.0 if r["status_code"] == "TK_Complete" else 0.0
    if kind == "CP_Drtn":
        od = _n(r["target_drtn_hr_cnt"])
        v = 100 * (od - _n(r["remain_drtn_hr_cnt"])) / od if od else done
    elif kind == "CP_Units":
        at = _n(r["t_act"]) + _n(r["t_rem"])
        v = 100 * _n(r["t_act"]) / at if at else done
    else:
        v = _n(r["phys_complete_pct"])
    return min(100.0, max(0.0, v))


def value_at(q: float, s: datetime, e: datetime, t: datetime) -> float:
    """Quantity q spread linearly from s to e, cumulated at t (a zero-length item counts after s)."""
    if t <= s:
        return 0.0
    if t >= e:
        return q
    return q * (t - s).total_seconds() / (e - s).total_seconds()


def curves(rows, dd: datetime) -> dict:
    """Items (q, start, end, clndr_id) of the planned, actual and remaining curves and the totals of assignment
    rows."""
    out = {"planned": [], "actual": [], "remaining": [], "budget": 0.0, "actual_qty": 0.0, "remain_qty": 0.0,
           "earned": 0.0, "clipped": 0, "clamped": 0, "unspread": 0.0}
    for r in rows:
        q, a, rem = _n(r["target_qty"]), _n(r["actual"]), _n(r["remain_qty"])
        out["budget"] += q
        out["actual_qty"] += a
        out["remain_qty"] += rem
        out["earned"] += q * activity_pct(r) / 100
        s, e = dt(r["target_start_date"]), dt(r["target_end_date"])
        if q and s and e:
            out["planned"].append((q, s, max(s, e), r["spread_clndr_id"]))
        elif q:
            out["unspread"] += q
        if a:
            s, e = dt(r["act_start_date"]), dt(r["act_end_date"])
            out["clipped"] += bool((s and s > dd) or (e and e > dd))
            e = min(e or dd, dd)
            out["actual"].append((a, min(s or e, e), e, r["spread_clndr_id"]))
        if rem:
            s = dt(r["restart_date"]) or dd
            out["clamped"] += s < dd
            s = max(s, dd)
            out["remaining"].append((rem, s, max(dt(r["reend_date"]) or s, s), r["spread_clndr_id"]))
    return out


def cum(items, t: datetime) -> float:
    """Cumulative quantity at t, linear over calendar time (values at the data date)."""
    return sum(value_at(q, s, e, t) for q, s, e, _c in items)


def work_at(o, q: float, s: datetime, e: datetime, clndr_id, t: datetime) -> float:
    """Quantity q spread over the working time of the calendar from s to e, cumulated at t: working hours from s
    to t / working hours from s to e; calendar time when the calendar is missing or unreadable or the span has
    no working time (a zero-length item counts after s)."""
    if t <= s:
        return 0.0
    if t >= e:
        return q
    c = cal(o, clndr_id)
    wh = 0.0 if c.error else c.work_hours(s, e)
    if wh <= 0:
        return value_at(q, s, e, t)
    return q * c.work_hours(s, t) / wh


def cum_work(o, items, t: datetime) -> float:
    return sum(work_at(o, q, s, e, c, t) for q, s, e, c in items)


def earned_value(o) -> dict:
    """to_date of the progress curve, recomputed: baseline planned (baseline assignments at the data date),
    planned, actual, earned, variance, spi, spi_actual."""
    dd = data_date(o)
    cur = curves(assignments(o, o.pid), dd)
    bid = baseline_pid(o)
    bp = cum(curves(assignments(o, bid), data_date(o, bid) or dd)["planned"], dd) if bid else None
    ev, act = cur["earned"], cur["actual_qty"]
    return {"baseline_planned": bp, "planned": cum(cur["planned"], dd), "actual": act,
            "actual_pct": 100 * act / cur["budget"], "earned": ev, "earned_pct": 100 * ev / cur["budget"],
            "variance": None if bp is None else ev - bp, "spi": ev / bp if bp else None,
            "spi_actual": act / bp if bp else None, "budget": cur["budget"],
            "at_completion": act + cur["remain_qty"], "cur": cur}


# ----------------------------------------------------------------- periods

def _edges(lo: datetime, hi: datetime, period: str, week_day: int) -> list[datetime]:
    if period == "month":
        d = datetime(lo.year, lo.month, 1)

        def nxt(x):
            return datetime(x.year + (x.month == 12), x.month % 12 + 1, 1)
    else:
        py = (week_day + 5) % 7  # P6 day 1 = Sunday; Python Monday = 0
        d = datetime.combine(lo.date() - timedelta(days=(lo.weekday() - py) % 7), datetime.min.time())

        def nxt(x):
            return x + timedelta(days=7)
    out = [d]
    while out[-1] <= hi:
        out.append(nxt(out[-1]))
    return out


def _not_modeled(o) -> bool:
    """Resource curves or stored period actuals in the database: the period spread is not recomputed here."""
    def has(table, col=None):
        cols = {str(c["name"]).lower() for c in o.sql(f"PRAGMA table_info({table})")}
        return bool(cols) and (col is None or col in cols)
    if has("TASKRSRC", "curv_id") and o.one("SELECT COUNT(*) FROM TASKRSRC WHERE curv_id IS NOT NULL"):
        return True
    return has("TRSRCFIN") and bool(o.one("SELECT COUNT(*) FROM TRSRCFIN"))


def periods(o) -> list[dict]:
    period = o.args.get("period") or "month"
    dd = data_date(o)
    cur = curves(assignments(o, o.pid), dd)
    bid = baseline_pid(o)
    base = curves(assignments(o, bid), data_date(o, bid) or dd) if bid else None
    cv = {**({"baseline": base["planned"]} if base else {}), "planned": cur["planned"], "actual": cur["actual"],
          "forecast": cur["actual"] + cur["remaining"]}
    dates = [d for items in cv.values() for _q, s, e, _c in items for d in (s, e)]
    week_day = o.one("SELECT week_start_day_num FROM PREFER") or 1
    edges = _edges(min(dates), max(dates), period, int(week_day))
    budget = {k: base["budget"] if k == "baseline" else cur["budget"] for k in cv}
    out = []
    for i, a in enumerate(edges[:-1]):
        row = {"period": a.strftime("%Y-%m") if period == "month" else a.strftime("%Y-%m-%d")}
        for k, items in cv.items():
            done = k != "actual" or a <= dd
            c0, c1 = cum_work(o, items, a), cum_work(o, items, edges[i + 1])
            row[k] = c1 - c0 if done else None
            row[f"{k}_pct"] = 100 * c1 / budget[k] if done and budget[k] else None
        out.append(row)
    return out


# ----------------------------------------------------------------- % complete (TASK units)

def _tasks(o):
    return o.sql("SELECT task_id, task_code, wbs_id, status_code, task_type, phys_complete_pct, target_drtn_hr_cnt, "
                 "remain_drtn_hr_cnt, act_start_date, early_start_date, "
                 "COALESCE(act_end_date, early_end_date) AS finish, "
                 "COALESCE(target_work_qty, 0) + COALESCE(target_equip_qty, 0) AS budget, "
                 "COALESCE(act_work_qty, 0) + COALESCE(act_equip_qty, 0) AS actual, "
                 "COALESCE(remain_work_qty, 0) + COALESCE(remain_equip_qty, 0) AS remain "
                 "FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL", o.pid)


def percent(o) -> dict:
    ts = _tasks(o)
    budget, actual, remain = (sum(_n(t[k]) for t in ts) for k in ("budget", "actual", "remain"))
    dur = [t for t in ts if t["task_type"] not in ("TT_Mile", "TT_FinMile", "TT_LOE", "TT_WBS")]
    od = sum(_n(t["target_drtn_hr_cnt"]) for t in dur)
    done = sum(_n(t["target_drtn_hr_cnt"]) - _n(t["remain_drtn_hr_cnt"]) for t in dur)
    mism = sum(1 for t in ts if _n(t["actual"]) + _n(t["remain"]) > 0 and abs(
        _n(t["phys_complete_pct"]) - 100 * _n(t["actual"]) / (_n(t["actual"]) + _n(t["remain"]))) > 0.01)
    return {"units": 100 * actual / (actual + remain) if actual + remain else None,
            "physical": 100 * sum(_n(t["phys_complete_pct"]) / 100 * _n(t["budget"]) for t in ts) / budget
            if budget else None,
            "duration": 100 * done / od if od else None,
            "completed": 100 * sum(t["status_code"] == "TK_Complete" for t in ts) / len(ts) if ts else None,
            "budget": budget, "actual": actual, "remain": remain, "mismatch": mism}


def bl_planned_pct(o):
    """Baseline planned units at the data date / baseline budget units, x 100, of the baseline's own
    labor and nonlabor assignments (p6_project_summary)."""
    bid = baseline_pid(o)
    if not bid:
        return None
    dd = data_date(o)
    b = curves(assignments(o, bid), data_date(o, bid) or dd)
    return 100 * cum(b["planned"], dd) / b["budget"] if b["budget"] else None


# ----------------------------------------------------------------- WBS (level 1 and the project node)

def wbs(o) -> list[dict]:
    rows = o.sql("SELECT wbs_id, parent_wbs_id, seq_num, proj_node_flag, wbs_short_name, wbs_name FROM PROJWBS "
                 "WHERE proj_id = ? AND delete_session_id IS NULL", o.pid)
    sep = o.one("SELECT name_sep_char FROM PREFER") or "."
    kids = {}
    for r in rows:
        kids.setdefault(r["parent_wbs_id"], []).append(r)
    top = next(r for r in rows if r["proj_node_flag"] == "Y")
    order = []

    def walk(r, depth, code):
        order.append((r["wbs_id"], depth, code, r["wbs_name"]))
        for k in sorted(kids.get(r["wbs_id"], []), key=lambda x: (x["seq_num"] or 0, x["wbs_id"])):
            walk(k, depth + 1, code + sep + k["wbs_short_name"])
    walk(top, 0, top["wbs_short_name"])
    parent = {r["wbs_id"]: r["parent_wbs_id"] for r in rows}

    def under(w, node):  # w in the subtree of node
        while w is not None:
            if w == node:
                return True
            w = parent.get(w)
        return False
    ts = _tasks(o)
    # baseline assignments placed by Activity ID on the current WBS (the last activity of the order wins)
    where = {}
    for t in sorted(ts, key=lambda t: (t["act_start_date"] or t["early_start_date"] or "", t["task_code"], t["task_id"])):
        where[t["task_code"]] = t["wbs_id"]
    bid, dd = baseline_pid(o), data_date(o)
    placed = []
    if bid and dd:
        for r in assignments(o, bid):
            q = _n(r["target_qty"])
            w = where.get(r["task_code"])
            if w is None or not q:
                continue
            s, e = dt(r["target_start_date"]), dt(r["target_end_date"])
            placed.append((w, q, value_at(q, s, max(s, e), dd) if s and e else 0.0))
    out = []
    for w, depth, code, name in order:
        if depth > 1:
            continue
        sub = [t for t in ts if under(t["wbs_id"], w)]
        a, rm = sum(_n(t["actual"]) for t in sub), sum(_n(t["remain"]) for t in sub)
        bb = sum(q for x, q, _p in placed if under(x, w))
        bp = sum(p for x, _q, p in placed if under(x, w))
        out.append({"wbs": (code, name), "units_pct": 100 * a / (a + rm) if a + rm else None,
                    "bl_planned_pct": 100 * bp / bb if bb else None, "budget": sum(_n(t["budget"]) for t in sub),
                    "actual": a, "finish": max((t["finish"] for t in sub if t["finish"]), default=None)})
    return out[:30]


# ----------------------------------------------------------------- cost earned value (p6_project_summary cost)

def _cost_rows(o, pid):
    """Every assignment's costs and every expense (PROJCOST) of a project, with the activity fields of its %
    complete; an expense lies at its activity's planned start (CL_Start), finish (CL_End), else over them."""
    act = "COALESCE(t.act_work_qty, 0) + COALESCE(t.act_equip_qty, 0) AS t_act, " \
          "COALESCE(t.remain_work_qty, 0) + COALESCE(t.remain_equip_qty, 0) AS t_rem "
    out = [dict(r) for r in o.sql(
        "SELECT tr.target_cost AS target_qty, COALESCE(tr.act_reg_cost, 0) + COALESCE(tr.act_ot_cost, 0) AS actual, "
        "tr.remain_cost AS remain_qty, tr.target_start_date, tr.target_end_date, tr.act_start_date, tr.act_end_date, "
        "tr.restart_date, tr.reend_date, NULL AS spread_clndr_id, t.task_code, t.status_code, t.complete_pct_type, "
        "t.phys_complete_pct, t.target_drtn_hr_cnt, t.remain_drtn_hr_cnt, " + act +
        "FROM TASKRSRC tr JOIN TASK t ON t.task_id = tr.task_id WHERE t.proj_id = ? AND tr.delete_session_id IS NULL "
        "AND t.delete_session_id IS NULL ORDER BY tr.taskrsrc_id", pid)]
    cols = {str(c["name"]).lower() for c in o.sql("PRAGMA table_info(PROJCOST)")}
    if {"task_id", "target_cost"} <= cols:
        for r in o.sql("SELECT e.target_cost AS target_qty, COALESCE(e.act_cost, 0) AS actual, e.remain_cost AS "
                       "remain_qty, e.cost_load_type, t.target_start_date AS ts, t.target_end_date AS te, t.task_code, "
                       "t.status_code, t.complete_pct_type, t.phys_complete_pct, t.target_drtn_hr_cnt, "
                       "t.remain_drtn_hr_cnt, " + act + "FROM PROJCOST e JOIN TASK t ON t.task_id = e.task_id "
                       "WHERE t.proj_id = ? AND e.delete_session_id IS NULL AND t.delete_session_id IS NULL", pid):
            d = dict(r)
            s, e = {"CL_Start": (d["ts"], d["ts"]), "CL_End": (d["te"], d["te"])}.get(d["cost_load_type"],
                                                                                    (d["ts"], d["te"]))
            d.update(target_start_date=s, target_end_date=e, act_start_date=None, act_end_date=None, restart_date=None,
                     reend_date=None, spread_clndr_id=None)
            out.append(d)
    return out


def _etc_token(o):
    """The estimate to complete technique stored on the project WBS node or in PREFER (None: remaining cost)."""
    for table, where in (("PROJWBS", f"proj_id = {int(o.pid)} AND proj_node_flag = 'Y'"), ("PREFER", "1 = 1")):
        cols = {str(c["name"]).lower() for c in o.sql(f"PRAGMA table_info({table})")}
        if "ev_etc_compute_type" in cols:
            tok = o.one(f"SELECT ev_etc_compute_type FROM {table} WHERE {where}")
            if tok:
                return tok
    return None


def cost(o) -> dict:
    """BAC, PV, EV, AC, CPI, SPI, EAC (AC + remaining cost: no technique stored), VAC and the currency."""
    dd = data_date(o)
    cur = curves(_cost_rows(o, o.pid), dd)
    bid = baseline_pid(o)
    pv = cum(curves(_cost_rows(o, bid), dd)["planned"], dd) if bid and dd else None
    bac, ev, ac, rem = cur["budget"], cur["earned"], cur["actual_qty"], cur["remain_qty"]
    has = any(abs(v) > 1e-9 for v in (bac, ac, rem))
    wbs_other = o.one("SELECT COUNT(*) FROM PROJWBS WHERE proj_id = ? AND ev_compute_type <> 'EC_Cmp_pct' "
                      "AND delete_session_id IS NULL", o.pid)
    why = None if not wbs_other else "earned value under other WBS techniques is not modeled"
    tok = _etc_token(o)
    eac = ac + rem if tok is None else Unchecked(f"estimate to complete technique {tok} is not modeled")
    currency = o.one("SELECT curr_short_name FROM CURRTYPE WHERE base_exch_rate = 1 AND delete_session_id IS NULL")
    if not has:
        return {"available": False, "currency": currency, **dict.fromkeys(("bac", "pv", "ev", "ac", "cpi", "spi",
                                                                           "eac", "vac"))}
    out = {"available": True, "currency": currency, "bac": bac, "pv": pv, "ev": ev, "ac": ac,
           "cpi": ev / ac if ac else None, "spi": ev / pv if pv else None, "eac": eac,
           "vac": bac - eac if not isinstance(eac, Unchecked) else eac}
    if why:
        out.update({k: Unchecked(why) for k in ("ev", "cpi", "spi")})
    return out


def _cost(key):
    return lambda o: cost(o)[key]

# ----------------------------------------------------------------- slots

def _ev(key):
    return lambda o: earned_value(o)[key]


def _pct(key):
    return lambda o: percent(o)[key]


def _bl_name(o):
    bid = baseline_pid(o)
    return bid and o.one("SELECT proj_short_name FROM PROJECT WHERE proj_id = ?", bid)


def _checks(o, key):
    dd = data_date(o)
    cur = curves(assignments(o, o.pid), dd)
    return cur[key]


SLOTS = {
    "data_date": lambda o: o.one("SELECT last_recalc_date FROM PROJECT WHERE proj_id = ?", o.pid),
    "last_f9": lambda o: o.one("SELECT last_schedule_date FROM PROJECT WHERE proj_id = ?", o.pid),
    "stale": lambda o: o.stale(),
    "bl_used": _bl_name,
    "units_pct": _pct("units"),
    "physical_pct": _pct("physical"),
    "duration_pct": _pct("duration"),
    "completed_pct": _pct("completed"),
    "budget_units": _pct("budget"),
    "actual_units": _pct("actual"),
    "remaining_units": _pct("remain"),
    "mismatch": _pct("mismatch"),
    "pct_type": lambda o: o.one("SELECT def_complete_pct_type FROM PROJECT WHERE proj_id = ?", o.pid),
    "bl_planned_pct": bl_planned_pct,
    "bl_planned": _ev("baseline_planned"),
    "planned": _ev("planned"),
    "actual": _ev("actual"),
    "actual_pct": _ev("actual_pct"),
    "earned": _ev("earned"),
    "earned_pct": _ev("earned_pct"),
    "ev_variance": _ev("variance"),
    "spi": _ev("spi"),
    "spi_actual": _ev("spi_actual"),
    "budget": _ev("budget"),
    "at_completion": _ev("at_completion"),
    "period_count": lambda o: len(periods(o)),
    "clipped": lambda o: _checks(o, "clipped"),
    "clamped": lambda o: _checks(o, "clamped"),
    "ev_other": lambda o: o.one("SELECT COUNT(*) FROM PROJWBS WHERE proj_id = ? AND ev_compute_type <> 'EC_Cmp_pct' "
                                "AND delete_session_id IS NULL", o.pid),
    "pc_error": lambda o: None,
    "cost_available": _cost("available"),
    "currency": _cost("currency"),
    "cost_bac": _cost("bac"),
    "cost_pv": _cost("pv"),
    "cost_ev": _cost("ev"),
    "cost_ac": _cost("ac"),
    "cost_cpi": _cost("cpi"),
    "cost_spi": _cost("spi"),
    "cost_eac": _cost("eac"),
    "cost_vac": _cost("vac"),
    "eac_formula": lambda o: Contains("AC + remaining cost") if _etc_token(o) is None else Unchecked(
        "estimate to complete technique not modeled"),
}
TABLES = {"periods": lambda o: Unchecked("resource curves or period actuals (TRSRCFIN) are not modeled")
          if _not_modeled(o) else periods(o)[:36], "wbs": wbs}

