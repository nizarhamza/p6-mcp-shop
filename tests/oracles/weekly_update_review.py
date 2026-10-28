"""Oracles of weekly-update-review: P6's PROJECT, TASK, TASKPRED, TASKRSRC, RSRC, CALENDAR and PROJPROP rows
read with SQL; percentages, working days (own parser of CALENDAR.clndr_data), the look-ahead window, the
baseline comparison, the out of sequence links and the linear baseline spread computed here."""

from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime, timedelta

from oracles import HPD, SUMMARY_TYPES, Contains

LABOR = ("RT_Labor", "RT_Equip")  # labor and nonlabor: the unit totals
TOL_H = 5 / 60  # a finish variance within 5 minutes is on time
CAUSES = ("late_start", "longer_duration", "late_start_and_longer_duration", "on_time", "earlier")  # documented order
SERIAL0 = date(1899, 12, 30)


# ----------------------------------------------------------------- dates and calendars

def _dt(v):
    if v is None:
        return None
    s = str(v).replace("T", " ")
    for f, n in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16), ("%Y-%m-%d", 10)):
        try:
            return datetime.strptime(s[:n], f)
        except ValueError:
            continue
    raise ValueError(f"date {v!r}")


def _tree(text: str):
    """P6 text tree (0||name(attrs)(children)) as (name, attrs, [children])."""
    s = re.sub(r"\s+", "", text)

    def node(i):  # i: just after the opening parenthesis
        i = s.index("||", i) + 2
        k = s.index("(", i)
        name, i = s[i:k], k + 1
        k = s.index(")", i)
        attrs, i = s[i:k], k + 2  # past ")("
        kids = []
        while s[i] == "(":
            kid, i = node(i + 1)
            kids.append(kid)
        return (name, attrs, kids), i + 2  # past "))"
    return node(1)[0]


def _minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _shifts(nodes) -> list:
    out = []
    for _name, attrs, _kids in nodes:
        p = attrs.split("|")
        kv = dict(zip(p[::2], p[1::2], strict=False))
        out.append((_minutes(kv["s"]), _minutes(kv["f"]) or 1440))  # f 00:00 = 24:00
    return sorted(out)


class Cal:
    """Working week (P6 day 1 = Sunday) and exceptions (serial days from 1899-12-30; no shift = holiday)."""

    def __init__(self, data, hpd: float):
        text = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
        self.hpd, self.week, self.exc = float(hpd), {}, {}
        for name, _attrs, kids in _tree(text)[2]:
            if name == "DaysOfWeek":
                for day, _x, sh in kids:
                    self.week[(int(day) + 5) % 7] = _shifts(sh)
            elif name == "Exceptions":
                for _e, attrs, sh in kids:
                    self.exc[SERIAL0 + timedelta(days=int(attrs.split("|")[1]))] = _shifts(sh)

    def day(self, d: date) -> list:
        return self.exc[d] if d in self.exc else self.week.get(d.weekday(), [])

    def hours(self, a: datetime, b: datetime) -> float:
        """Working hours from a to b (negative when b is before a)."""
        if b < a:
            return -self.hours(b, a)
        secs, d = 0.0, a.date()
        while d <= b.date():
            day0 = datetime.combine(d, datetime.min.time())
            for s, f in self.day(d):
                lo, hi = max(a, day0 + timedelta(minutes=s)), min(b, day0 + timedelta(minutes=f))
                if hi > lo:
                    secs += (hi - lo).total_seconds()
            d += timedelta(days=1)
        return secs / 3600


def _cals(o) -> dict:
    return {r["clndr_id"]: Cal(r["clndr_data"], r["hpd"])
            for r in o.sql(f"SELECT c.clndr_id, c.clndr_data, {HPD} AS hpd FROM CALENDAR c")}


# ----------------------------------------------------------------- project and activities

def _project(o, col, pid=None):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", pid or o.pid)


def _bid(o):
    return _project(o, "sum_base_proj_id")


def _tasks(o, pid=None):
    return o.sql(f"SELECT t.*, {HPD} AS hpd FROM TASK t LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id "
                 "WHERE t.proj_id = ? AND t.delete_session_id IS NULL", pid or o.pid)


def _n(v):
    return float(v or 0)


def _units(t, kind):
    return _n(t[f"{kind}_work_qty"]) + _n(t[f"{kind}_equip_qty"])


def _is_open(t):
    return t["status_code"] != "TK_Complete" and t["task_type"] not in SUMMARY_TYPES


def _crit_h(o):
    return float(_project(o, "critical_drtn_hr_cnt") or 0)


def _is_crit(o, t):
    """Open and critical: the demo is CT_TotFloat (total float at or below critical_drtn_hr_cnt hours)."""
    assert _project(o, "critical_path_type") == "CT_TotFloat"
    return _is_open(t) and t["total_float_hr_cnt"] is not None and t["total_float_hr_cnt"] <= _crit_h(o)


def _pct(o):
    ts = _tasks(o)
    act, rem = sum(_units(t, "act") for t in ts), sum(_units(t, "remain") for t in ts)
    budget = sum(_units(t, "target") for t in ts)
    dur = [t for t in ts if t["task_type"] not in ("TT_Mile", "TT_FinMile", "TT_LOE", "TT_WBS")]
    orig = sum(_n(t["target_drtn_hr_cnt"]) for t in dur)
    done = sum(_n(t["target_drtn_hr_cnt"]) - _n(t["remain_drtn_hr_cnt"]) for t in dur)
    mismatch = 0
    for t in ts:
        at = _units(t, "act") + _units(t, "remain")
        if at > 0 and abs(_n(t["phys_complete_pct"]) - 100 * _units(t, "act") / at) > 0.01:
            mismatch += 1
    phys = sum(_n(t["phys_complete_pct"]) / 100 * _units(t, "target") for t in ts)
    return {"units": _ratio(act, act + rem), "physical": _ratio(phys, budget), "duration": _ratio(done, orig),
            "completed": _ratio(sum(t["status_code"] == "TK_Complete" for t in ts), len(ts)), "mismatch": mismatch}


def _ratio(a, b):
    """100 x a / b, None without a denominator."""
    return 100 * a / b if b else None


def _proj_wd(o, a, b):
    """Working days of the project calendar from a to b (None when a date is missing)."""
    if a is None or b is None:
        return None
    cal = _cals(o)[_project(o, "clndr_id")]
    return cal.hours(_dt(a), _dt(b)) / cal.hpd


def _cd(a, b):
    return None if a is None or b is None else (_dt(b) - _dt(a)).total_seconds() / 86400


def _bl_finish(o):
    return _project(o, "scd_end_date", _bid(o)) if _bid(o) else None


# ----------------------------------------------------------------- baseline spread and earned units

def _asg(o, pid):
    return o.sql("SELECT tr.target_qty, tr.target_start_date, tr.target_end_date, t.phys_complete_pct, t.status_code, "
                 "t.complete_pct_type, t.target_drtn_hr_cnt, t.remain_drtn_hr_cnt, t.act_work_qty, t.act_equip_qty, "
                 "t.remain_work_qty, t.remain_equip_qty FROM TASKRSRC tr JOIN TASK t ON t.task_id = tr.task_id "
                 "LEFT JOIN RSRC r ON r.rsrc_id = tr.rsrc_id WHERE t.proj_id = ? AND tr.delete_session_id IS NULL "
                 "AND t.delete_session_id IS NULL AND COALESCE(tr.rsrc_type, r.rsrc_type) IN (?, ?)", pid, *LABOR)


def _perf(r) -> float:
    """Activity % complete by its percent complete type (P6 earned value with activity percent complete)."""
    done = 100.0 * (r["status_code"] == "TK_Complete")
    if r["complete_pct_type"] == "CP_Drtn":
        od = _n(r["target_drtn_hr_cnt"])
        v = 100 * (od - _n(r["remain_drtn_hr_cnt"])) / od if od else done
    elif r["complete_pct_type"] == "CP_Units":
        a, at = _units(r, "act"), _units(r, "act") + _units(r, "remain")
        v = 100 * a / at if at else done
    else:
        v = _n(r["phys_complete_pct"])
    return min(100.0, max(0.0, v))


def _linear(q, s, e, t) -> float:
    """Quantity q spread linearly from s to e, cumulated at t (a zero-length item counts after its start)."""
    if t <= s:
        return 0.0
    if t >= e:
        return q
    return q * (t - s).total_seconds() / (e - s).total_seconds()


def _baseline_at_dd(o):
    """Baseline planned units % at the data date and earned units / baseline planned units (labor, nonlabor);
    None without a baseline."""
    if not _bid(o):
        return {"pct": None, "spi": None}
    dd = _dt(_project(o, "last_recalc_date"))
    rows = _asg(o, _bid(o))
    budget = sum(_n(r["target_qty"]) for r in rows)
    planned = 0.0
    for r in rows:
        s, e = _dt(r["target_start_date"]), _dt(r["target_end_date"])
        if _n(r["target_qty"]) and s and e:
            planned += _linear(_n(r["target_qty"]), s, max(s, e), dd)
    earned = sum(_n(r["target_qty"]) * _perf(r) / 100 for r in _asg(o, o.pid))
    return {"pct": _ratio(planned, budget), "spi": earned / planned if planned else None}


# ----------------------------------------------------------------- critical path

def critical(o):
    ts = sorted((t for t in _tasks(o) if _is_crit(o, t)),
                key=lambda t: (t["total_float_hr_cnt"], _dt(t["act_start_date"] or t["early_start_date"]),
                               t["task_code"], t["task_id"]))
    return [{"activity": (t["task_code"], t["task_name"]), "status": t["status_code"], "start": t["early_start_date"],
             "finish": t["early_end_date"], "rem": _n(t["remain_drtn_hr_cnt"]) / t["hpd"],
             "tf": t["total_float_hr_cnt"] / t["hpd"]} for t in ts][:15]


# ----------------------------------------------------------------- look-ahead (critical only)

def _window(o):
    frm = _dt(_project(o, "last_recalc_date"))
    return frm, frm + timedelta(days=7 * int(o.args["weeks"]))


def _rem_start(t):
    return t["restart_date"] or t["early_start_date"]


def _rem_finish(t):
    return t["reend_date"] or t["early_end_date"]


def _la(o):
    """[(activity, categories)] of the open critical activities in the window, by forecast start."""
    frm, to = _window(o)
    out = []
    for t in _tasks(o):
        if not _is_crit(o, t):
            continue
        rs, rf = _dt(_rem_start(t)), _dt(_rem_finish(t))
        cats = {"in_progress": t["status_code"] == "TK_Active",
                "starting": t["status_code"] == "TK_NotStart" and frm <= rs < to,
                "finishing": frm <= rf < to,
                "spanning": t["status_code"] == "TK_NotStart" and rs < frm and rf >= to}
        if any(cats.values()):
            out.append((t, cats))
    out.sort(key=lambda x: (_dt(x[0]["act_start_date"] or _rem_start(x[0])), _dt(_rem_finish(x[0])),
                            x[0]["task_code"], x[0]["task_id"]))
    return out


def _week(o, v):
    frm, to = _window(o)
    d = _dt(v)
    return int((d - frm).total_seconds() // (7 * 86400)) + 1 if frm <= d < to else None


def lookahead(o):
    rows = []
    for t, cats in _la(o)[:20]:
        st, fin = t["act_start_date"] or _rem_start(t), _rem_finish(t)
        rows.append({"activity": (t["task_code"], t["task_name"]), "window": [k for k, v in cats.items() if v],
                     "start": st, "finish": fin, "sw": _week(o, st), "fw": _week(o, fin),
                     "tf": t["total_float_hr_cnt"] / t["hpd"]})
    return rows


def _la_count(o, cat):
    return sum(bool(c[cat]) for _t, c in _la(o))


# ----------------------------------------------------------------- comparison with the project baseline

SIDE = ("SELECT t.task_id, t.task_code, t.task_name, t.clndr_id, COALESCE(t.act_start_date, t.early_start_date) AS st, "
        "COALESCE(t.act_end_date, t.early_end_date) AS fin FROM TASK t WHERE t.proj_id = ? AND t.delete_session_id IS NULL")


def _cmp(o):
    """(current activities with their baseline match and julianday finish variance, baseline-only activities);
    dates of both sides: actual, else early."""
    bid = _bid(o)
    rows = o.sql(f"WITH a AS ({SIDE}), b AS ({SIDE}) SELECT a.*, b.task_id AS b_id, b.st AS b_st, b.fin AS b_fin, "
                 "julianday(a.fin) - julianday(b.fin) AS v FROM a LEFT JOIN b ON b.task_code = a.task_code", o.pid, bid)
    removed = o.sql(f"WITH a AS ({SIDE}), b AS ({SIDE}) SELECT b.* FROM b WHERE NOT EXISTS "
                    "(SELECT 1 FROM a WHERE a.task_code = b.task_code)", o.pid, bid)
    return rows, removed


def _slip(cal, s, f, bs, bf):
    """(start variance, duration delta, finish variance) in working days of the activity calendar, and the cause."""
    sv, fv = cal.hours(_dt(bs), _dt(s)), cal.hours(_dt(bf), _dt(f))
    dv = fv - sv
    if fv > TOL_H:
        late, longer = sv > TOL_H, dv > TOL_H
        cause = ("late_start_and_longer_duration" if late and longer else "late_start" if late else
                 "longer_duration" if longer else "late_start" if sv >= dv else "longer_duration")
    else:
        cause = "on_time" if fv >= -TOL_H else "earlier"
    return sv / cal.hpd, dv / cal.hpd, fv / cal.hpd, cause


def slipped(o):
    """Added and removed first, then matched ones moved by 5 calendar days or more, by absolute variance
    (no rows without a baseline: the call fails)."""
    if not _bid(o):
        return []
    rows, removed = _cmp(o)
    cals = _cals(o)
    out = []
    blank = {"var": None, "start_var": None, "dur": None, "cause": None}
    for r in rows:
        if r["b_id"] is None:
            out.append(((0, 0.0, r["task_code"], r["task_id"]),
                        {"activity": (r["task_code"], r["task_name"]), "change": "added", "finish": r["fin"],
                         "bl_finish": None, **blank}))
        elif abs(r["v"]) >= 5:
            sv, dv, fv, cause = _slip(cals[r["clndr_id"]], r["st"], r["fin"], r["b_st"], r["b_fin"])
            out.append(((1, -round(abs(r["v"]), 6), r["task_code"], r["task_id"]),
                        {"activity": (r["task_code"], r["task_name"]), "change": "matched", "finish": r["fin"],
                         "bl_finish": r["b_fin"], "var": fv, "start_var": sv, "dur": dv, "cause": cause}))
    for r in removed:
        out.append(((0, 0.0, r["task_code"], r["task_id"]),
                    {"activity": (r["task_code"], r["task_name"]), "change": "removed", "finish": None,
                     "bl_finish": r["fin"], **blank}))  # a removed activity keeps its baseline name
    return [row for _k, row in sorted(out, key=lambda x: x[0])][:15]


def slip_causes(o):
    if not _bid(o):
        return []
    rows, _removed = _cmp(o)
    cals = _cals(o)
    n = Counter(_slip(cals[r["clndr_id"]], r["st"], r["fin"], r["b_st"], r["b_fin"])[3]
                for r in rows if r["b_id"] is not None)
    return [{"cause": c, "n": n.get(c, 0)} for c in CAUSES]


def _moved(o, sign):
    if not _bid(o):
        return None
    rows, _removed = _cmp(o)
    return sum(r["b_id"] is not None and r["v"] * sign > 0 for r in rows)


# ----------------------------------------------------------------- progress checks

OOS = {"FS": "r.pred_type = 'PR_FS' AND COALESCE(r.lag_hr_cnt, 0) >= 0 AND s.act_start_date IS NOT NULL "
             "AND p.status_code <> 'TK_Complete'",
       "FS_lead": "r.pred_type = 'PR_FS' AND r.lag_hr_cnt < 0 AND s.act_start_date IS NOT NULL "
                  "AND p.status_code <> 'TK_Complete'",
       "SS": "r.pred_type = 'PR_SS' AND s.act_start_date IS NOT NULL AND p.act_start_date IS NULL",
       "FF": "r.pred_type = 'PR_FF' AND s.status_code = 'TK_Complete' AND p.status_code <> 'TK_Complete'",
       "SF": "r.pred_type = 'PR_SF' AND s.status_code = 'TK_Complete' AND p.act_start_date IS NULL"}


def _links(o, cond):
    """Links whose successor is in the project (LOE and WBS summary at neither end) meeting cond."""
    return o.sql("SELECT r.task_pred_id, s.task_id FROM TASKPRED r JOIN TASK s ON s.task_id = r.task_id "
                 "JOIN TASK p ON p.task_id = r.pred_task_id WHERE s.proj_id = ? AND s.task_type NOT IN (?, ?) "
                 "AND p.task_type NOT IN (?, ?) AND r.delete_session_id IS NULL AND s.delete_session_id IS NULL "
                 f"AND p.delete_session_id IS NULL AND ({cond})", o.pid, *SUMMARY_TYPES, *SUMMARY_TYPES)


def oos(o):
    out = []
    for name, cond in OOS.items():
        rows = _links(o, cond)
        out.append({"type": name, "links": len(rows), "succ": len({r[1] for r in rows})})
    return out


def _status_checks(o):
    dd = _dt(_project(o, "last_recalc_date"))

    def after(v):
        return v is not None and _dt(v) > dd
    checks = {  # the documented order
        "active_without_start": lambda t: t["status_code"] == "TK_Active" and t["act_start_date"] is None,
        "complete_with_remaining_or_no_finish": lambda t: t["status_code"] == "TK_Complete" and (
            _n(t["remain_drtn_hr_cnt"]) > 0 or t["act_end_date"] is None),
        "pct_100_not_complete": lambda t: _n(t["phys_complete_pct"]) >= 100 and t["status_code"] != "TK_Complete",
        "not_started_with_actuals": lambda t: t["status_code"] == "TK_NotStart" and (
            t["act_start_date"] is not None or t["act_end_date"] is not None or _n(t["phys_complete_pct"]) > 0),
        "finish_before_start": lambda t: bool(t["act_start_date"] and t["act_end_date"]
                                              and _dt(t["act_end_date"]) < _dt(t["act_start_date"])),
        "suspended_without_resume": lambda t: t["suspend_date"] is not None and t["resume_date"] is None,
        "actual_after_data_date": lambda t: after(t["act_start_date"]) or after(t["act_end_date"]),
    }
    ts = _tasks(o)
    return {k: sum(bool(f(t)) for t in ts) for k, f in checks.items()}


def status_checks(o):
    return [{"check": k, "count": v} for k, v in _status_checks(o).items()]


def _logic_mode(o):
    """The out of sequence option from PROJPROP 'scheduling' (retained logic, progress override, actual dates)."""
    text = o.one("SELECT prop_value FROM PROJPROP WHERE proj_id = ? AND prop_name = 'scheduling'", o.pid) or ""
    text = text.decode() if isinstance(text, bytes) else text

    def flag(key):
        m = re.search(rf"\|{key}\|([YN])\|", text)
        return m.group(1) if m else None
    rl, po = flag("sched_retained_logic"), flag("sched_progress_override")
    want = "retained logic" if rl == "Y" else "progress override" if po == "Y" else "actual dates"
    return lambda v: v == want


# ----------------------------------------------------------------- slots and tables

SLOTS = {
    "data_date": lambda o: _project(o, "last_recalc_date"),
    "last_f9": lambda o: _project(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "units_pct": lambda o: _pct(o)["units"],
    "physical_pct": lambda o: _pct(o)["physical"],
    "duration_pct": lambda o: _pct(o)["duration"],
    "completed_pct": lambda o: _pct(o)["completed"],
    "mismatch": lambda o: _pct(o)["mismatch"],
    "bl_planned_pct": lambda o: _baseline_at_dd(o)["pct"],
    "spi_units": lambda o: _baseline_at_dd(o)["spi"],
    "scheduled_finish": lambda o: _project(o, "scd_end_date"),
    "must_finish": lambda o: _project(o, "plan_end_date"),
    "vs_must_cd": lambda o: _cd(_project(o, "plan_end_date"), _project(o, "scd_end_date")),
    "vs_must_wd": lambda o: _proj_wd(o, _project(o, "plan_end_date"), _project(o, "scd_end_date")),
    "baseline_used": lambda o: _project(o, "proj_short_name", _bid(o)) if _bid(o) else None,
    "vs_bl_cd": lambda o: _cd(_bl_finish(o), _project(o, "scd_end_date")),
    "vs_bl_wd": lambda o: _proj_wd(o, _bl_finish(o), _project(o, "scd_end_date")),
    "cp_definition": lambda o: Contains(_project(o, "critical_path_type"), f"total float <= {_crit_h(o):g} h",
                                        "LOE and WBS summary"),
    "critical": lambda o: sum(_is_crit(o, t) for t in _tasks(o)),
    "neg_float": lambda o: sum(_is_open(t) and _n(t["total_float_hr_cnt"]) < 0 for t in _tasks(o)),
    "cmp_error": lambda o: None if _bid(o) else Contains("has no project baseline"),
    "later": lambda o: _moved(o, 1),
    "earlier": lambda o: _moved(o, -1),
    "oos_links": lambda o: len(_links(o, " OR ".join(f"({c})" for c in OOS.values()))),
    "logic_mode": _logic_mode,
    "chk_active": lambda o: _status_checks(o)["active_without_start"],
    "chk_complete": lambda o: _status_checks(o)["complete_with_remaining_or_no_finish"],
    "chk_after_dd": lambda o: _status_checks(o)["actual_after_data_date"],
    "la_from": lambda o: _window(o)[0].strftime("%Y-%m-%d %H:%M:%S"),
    "la_to": lambda o: _window(o)[1].strftime("%Y-%m-%d %H:%M:%S"),
    "la_critical": lambda o: len(_la(o)),
    "la_in_progress": lambda o: _la_count(o, "in_progress"),
    "la_starting": lambda o: _la_count(o, "starting"),
    "la_finishing": lambda o: _la_count(o, "finishing"),
}
TABLES = {"critical": critical, "slip_causes": slip_causes, "slipped": slipped, "oos": oos,
          "status_checks": status_checks, "lookahead": lookahead}
