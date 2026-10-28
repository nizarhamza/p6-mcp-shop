"""Oracles of progress-earned-value: P6's TASK, TASKRSRC, RSRC, PROJWBS, PROJECT and PREFER rows read with SQL;
the linear spread of the assignment quantities, the earned value, the periods and the WBS rollups worked out
here. baseline-variance imports the earned value helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

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
    """Labor and nonlabor assignments of a project with the activity fields of its % complete."""
    return o.sql("SELECT tr.target_qty, COALESCE(tr.act_reg_qty, 0) + COALESCE(tr.act_ot_qty, 0) AS actual, tr.remain_qty, "
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
    """Items (q, start, end) of the planned, actual and remaining curves and the totals of assignment rows."""
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
            out["planned"].append((q, s, max(s, e)))
        elif q:
            out["unspread"] += q
        if a:
            s, e = dt(r["act_start_date"]), dt(r["act_end_date"])
            out["clipped"] += bool((s and s > dd) or (e and e > dd))
            e = min(e or dd, dd)
            out["actual"].append((a, min(s or e, e), e))
        if rem:
            s = dt(r["restart_date"]) or dd
            out["clamped"] += s < dd
            s = max(s, dd)
            out["remaining"].append((rem, s, max(dt(r["reend_date"]) or s, s)))
    return out


def cum(items, t: datetime) -> float:
    return sum(value_at(q, s, e, t) for q, s, e in items)


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


def periods(o) -> list[dict]:
    period = o.args.get("period") or "month"
    dd = data_date(o)
    cur = curves(assignments(o, o.pid), dd)
    bid = baseline_pid(o)
    base = curves(assignments(o, bid), data_date(o, bid) or dd) if bid else None
    cv = {**({"baseline": base["planned"]} if base else {}), "planned": cur["planned"], "actual": cur["actual"],
          "forecast": cur["actual"] + cur["remaining"]}
    dates = [d for items in cv.values() for _q, s, e in items for d in (s, e)]
    week_day = o.one("SELECT week_start_day_num FROM PREFER") or 1
    edges = _edges(min(dates), max(dates), period, int(week_day))
    budget = {k: base["budget"] if k == "baseline" else cur["budget"] for k in cv}
    out = []
    for i, a in enumerate(edges[:-1]):
        row = {"period": a.strftime("%Y-%m") if period == "month" else a.strftime("%Y-%m-%d")}
        for k, items in cv.items():
            done = k != "actual" or a <= dd
            c0, c1 = cum(items, a), cum(items, edges[i + 1])
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
}
TABLES = {"periods": lambda o: periods(o)[:36], "wbs": wbs}
