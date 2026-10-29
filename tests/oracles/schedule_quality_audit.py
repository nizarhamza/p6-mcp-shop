"""Oracles of schedule-quality-audit: P6's TASK, TASKPRED, TASKRSRC, PROJECT, PROJPROP and CALENDAR rows read
with SQL; the DCMA 14 rules, the key dates (a forward pass from each constraint date), the dangling ends, the
redundant links (with a P6 calendar parser for the link gaps), the float buckets and the CPLI recomputed here.
The critical path test needs a CPM pass with the delay: its pass is checked through CPM theory on the stored
F9 float when it can be (see _cpt_pass), else Unchecked.

Real P6 tables have upper case column names: rows are read through _d (lower case keys)."""

from __future__ import annotations

import glob
import json
import os
import re
from datetime import date, datetime, time, timedelta

from oracles import SUMMARY_TYPES, Contains, Unchecked

S = "('TT_LOE', 'TT_WBS')"
HPD = "COALESCE(NULLIF(c.day_hr_cnt, 0), 8)"
HARD = ("CS_MSO", "CS_MEO", "CS_MSOB", "CS_MEOB", "CS_MANDSTART", "CS_MANDFIN")  # DCMA hard constraints
FINISH_CSTR = ("CS_MEO", "CS_MEOA", "CS_MEOB", "CS_MANDFIN")  # constraints on the finish date
MILESTONES = ("TT_Mile", "TT_FinMile")
TOL_H = 5 / 60  # a gap within 5 minutes is no gap
TOL = timedelta(minutes=5)
LIMIT_DAYS = 44.0  # DCMA limit of high float, high duration and long lags (days of the calendar)
REL = {"PR_FS": "FS", "PR_SS": "SS", "PR_FF": "FF", "PR_SF": "SF"}
FROM = {"PR_FS": "f", "PR_SS": "s", "PR_FF": "f", "PR_SF": "s"}  # predecessor date a link starts from
TO = {"PR_FS": "s", "PR_SS": "s", "PR_FF": "f", "PR_SF": "f"}  # successor date it drives
CATEGORIES = ("completed_predecessor", "marked_deleted", "transitive", "duplicate")
EDGES = (-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 44.0)  # p6_float_analysis default edges (days)
CHAIN = 10  # links per FS chain of a transitive link

# DCMA defaults: check -> (threshold, rule, P6 schedule_check target key, limit key, enable flag key)
DCMA = {
    "logic": (5, "max", "logic_target", None, "check_logic"),
    "logic_density": (1.5, "ratio", None, None, None),  # links per open activity (no P6 setting)
    "leads": (0, "max", "negative_lag_target", None, "check_negative_lag"),
    "lags": (5, "max", "lag_target", None, "check_lag"),
    "long_lags": (None, "max", "long_lags_target", "long_lags_constraint", "check_long_lags"),
    "fs_links": (90, "min", "relationship_target", None, "check_relationships"),
    "hard_constraints": (5, "max", "hard_constraint_target", None, "check_hard_constraints"),
    "high_float": (5, "max", "large_float_target", "large_float_constraint", "check_large_float"),
    "negative_float": (0, "max", "negative_float_target", None, "check_negative_float"),
    "high_duration": (5, "max", "large_duration_target", "large_durations_constraint", "check_large_duration"),
    "invalid_dates": (0, "max", "progress_date_target", None, "check_progress_duration"),
    "resources": (None, "max", "resouces_target", None, "check_resources"),  # P6's spelling
    "missed_tasks": (5, "max", "late_activities_target", None, "check_late_activities"),
    "critical_path_test": (None, None, "cpt_target", None, "check_cpt"),
    "cpli": (0.95, "ratio", "cpli_target", None, "check_cpli"),
    "bei": (0.95, "ratio", "bei_target", None, "check_bei"),
}


def _d(row) -> dict:
    """A row as a dict with lower case keys (P6 column names are upper case)."""
    return {k.lower(): row[k] for k in row.keys()}


def _cached(o, key, fn):
    cache = o.__dict__.setdefault("_sqa_cache", {})
    if key not in cache:
        cache[key] = fn()
    return cache[key]


# ----------------------------------------------------------------- P6 text trees and calendars

def _text(v) -> str:
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")


def _tree(s: str):
    """Root of a P6 text tree (node = (num||name(k|v|...)(children))) as (name, attrs, children); white space
    around the parentheses is ignored. ValueError when malformed."""
    s = re.sub(r"\s*([()])\s*", r"\1", s.strip())

    def node(i):
        if i >= len(s) or s[i] != "(":
            raise ValueError("node expected")
        j = s.find("||", i)
        k = s.find("(", j)
        e = s.find(")", k)
        if min(j, k, e) < 0:
            raise ValueError("bad node")
        parts = s[k + 1:e].split("|")
        attrs = {parts[n].lower(): parts[n + 1] for n in range(0, len(parts) - 1, 2)}
        i = e + 1
        if i >= len(s) or s[i] != "(":
            raise ValueError("children expected")
        i += 1
        kids = []
        while i < len(s) and s[i] != ")":
            kid, i = node(i)
            kids.append(kid)
        if i + 1 >= len(s) or s[i + 1] != ")":
            raise ValueError("unclosed node")
        return (s[j + 2:k], attrs, kids), i + 2
    return node(0)[0]


def _find(n, name):
    if n[0] == name:
        return n
    for k in n[2]:
        hit = _find(k, name)
        if hit:
            return hit
    return None


def _minutes(hhmm: str, end: bool) -> int:
    h, m = (int(x) for x in hhmm.strip().split(":")[:2])
    v = 60 * h + m
    return 1440 if end and v == 0 else v  # f|00:00 is the next midnight


def _shifts(n) -> tuple:
    return tuple(sorted((_minutes(k[1]["s"], False), _minutes(k[1]["f"], True)) for k in n[2]
                        if "s" in k[1] and "f" in k[1]))


class Cal:
    """Working time of a P6 calendar: a week (day 1 = Sunday) and exception dates (no shift = holiday, shifts =
    that day's hours). error: unreadable clndr_data (no working time)."""

    def __init__(self, week, exc, hpd, error=False):
        self.week, self.exc, self.hpd, self.error = week or {}, exc, float(hpd or 8) or 8.0, error

    def day(self, d: date):
        return self.exc[d] if d in self.exc else self.week.get(d.weekday(), ())

    def work_hours(self, a: datetime, b: datetime) -> float:
        if b < a:
            return -self.work_hours(b, a)
        total, d = 0.0, a.date()
        while d <= b.date():
            base = datetime.combine(d, time())
            for s, f in self.day(d):
                lo, hi = max(a, base + timedelta(minutes=s)), min(b, base + timedelta(minutes=f))
                if hi > lo:
                    total += (hi - lo).total_seconds() / 3600
            d += timedelta(days=1)
        return total

    def add(self, a: datetime, h: float) -> datetime:
        """End of h hours of work begun at a (a shift end when it fills it); minutes rounded."""
        left, d = round(h * 60), a.date()
        if left <= 0:
            return a
        t0 = (a - datetime.combine(d, time())).total_seconds() / 60
        for _ in range(3660):
            for s, f in self.day(d):
                lo = max(s, t0)
                if f > lo:
                    if left <= f - lo:
                        return datetime.combine(d, time()) + timedelta(minutes=lo + left)
                    left -= f - lo
            d, t0 = d + timedelta(days=1), 0
        raise ValueError("calendar without working time")

    def sub(self, a: datetime, h: float) -> datetime:
        """Start of h hours of work that end at a (a shift start when it fills it); minutes rounded."""
        left, d = round(h * 60), a.date()
        if left <= 0:
            return a
        t1 = (a - datetime.combine(d, time())).total_seconds() / 60
        for _ in range(3660):
            for s, f in reversed(self.day(d)):
                hi = min(f, t1)
                if hi > s:
                    if left <= hi - s:
                        return datetime.combine(d, time()) + timedelta(minutes=hi - left)
                    left -= hi - s
            d, t1 = d - timedelta(days=1), 1440
        raise ValueError("calendar without working time")


def _cal_parse(data):
    """(week or None when there is no DaysOfWeek node, exceptions) of a clndr_data text."""
    root = _tree(_text(data))
    dow, exc = _find(root, "DaysOfWeek"), _find(root, "Exceptions")
    week = None if dow is None else {(int(n[0]) + 5) % 7: _shifts(n) for n in dow[2]}
    days = {}
    for e in (exc[2] if exc else []):
        if "d" in e[1]:
            days[date(1899, 12, 30) + timedelta(days=int(float(e[1]["d"])))] = _shifts(e)
    return week, days


def _cals(o) -> dict:
    """Live calendars by clndr_id; a base calendar gives its week when the calendar has none and its exception
    dates (the calendar's own dates win), 10 levels at most; an unreadable one has no working time."""
    def load():
        rows = {r["clndr_id"]: r for r in o.sql("SELECT clndr_id, base_clndr_id, day_hr_cnt, clndr_data FROM CALENDAR "
                                                "WHERE delete_session_id IS NULL")}
        out = {}

        def build(cid, depth=0):
            if cid in out:
                return out[cid]
            r = rows[cid]
            try:
                week, exc = _cal_parse(r["clndr_data"])
                err = False
            except (ValueError, IndexError, KeyError):
                week, exc, err = None, {}, True
            own = dict(exc)
            base = r["base_clndr_id"]
            if not err and base in rows and base != cid and depth < 10:
                b = build(base, depth + 1)
                if week is None:
                    week = b.week
                own = {**b.exc, **own}
            out[cid] = Cal(week, own, r["day_hr_cnt"], err)
            return out[cid]
        for cid in rows:
            build(cid)
        return out
    return _cached(o, "cals", load)


def _ok(cal) -> bool:
    return cal is not None and not cal.error


def _dt(v):
    return None if not v else datetime.fromisoformat(str(v).replace("T", " ")[:19])


# ----------------------------------------------------------------- project, options, thresholds

def _prj(o) -> dict:
    return _cached(o, "prj", lambda: _d(o.sql("SELECT * FROM PROJECT WHERE proj_id = ?", o.pid)[0]))


def _props(o, name) -> dict:
    """Root attributes (lower case keys) of the project's PROJPROP row name, {} when absent or unreadable."""
    def load():
        txt = _text(o.one("SELECT prop_value FROM PROJPROP WHERE proj_id = ? AND prop_name = ? "
                          "AND delete_session_id IS NULL", o.pid, name))
        try:
            return _tree(txt)[1] if txt.strip() else {}
        except ValueError:
            return {}
    return _cached(o, "prop " + name, load)


def _opt(o, key, default):
    return _props(o, "scheduling").get(key, default)


def _settings(o) -> dict:
    """{source, threshold {check}, limit {check: (unit, value)}, disabled} from PROJPROP schedule_check, else
    the DCMA defaults."""
    def load():
        attrs = _props(o, "schedule_check")

        def num(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        out = {"source": "PROJPROP schedule_check" if attrs else "DCMA defaults", "threshold": {}, "limit": {},
               "disabled": set()}
        for name, (default, _rule, key, lim, flag) in DCMA.items():
            thr = default if num(attrs.get(key)) is None else num(attrs[key])
            if name == "cpli" and num(attrs.get(key)) is not None:
                thr = round(1 - thr / 100, 4)  # stored as a tolerance in %
            if attrs.get(flag) == "N":
                thr = None
                out["disabled"].add(name)
            out["threshold"][name] = thr
            if lim:
                out["limit"][name] = ("h", num(attrs[lim])) if num(attrs.get(lim)) is not None else ("d", LIMIT_DAYS)
        return out
    return _cached(o, "settings", load)


def _over(lim, hours, hpd) -> bool:
    return hours is not None and hours > (lim[1] if lim[0] == "h" else lim[1] * hpd)


# ----------------------------------------------------------------- activities and links

def _net(o):
    """(tasks by task_id: the project's and the other ends of its links, links with an end in the project
    (live, both ends live) by task_pred_id, links by successor, links by predecessor)."""
    def load():
        mine = f"SELECT task_id FROM TASK WHERE proj_id = {int(o.pid)}"
        links = [_d(r) for r in o.sql(
            "SELECT task_pred_id AS id, task_id AS succ, pred_task_id AS pred, pred_type AS type, "
            f"COALESCE(lag_hr_cnt, 0) AS lag FROM TASKPRED WHERE delete_session_id IS NULL AND (task_id IN ({mine}) "
            f"OR pred_task_id IN ({mine})) ORDER BY task_pred_id")]
        ids = {x[k] for x in links for k in ("succ", "pred")}
        t = {r["task_id"]: _d(r) for r in o.sql(
            f"SELECT t.*, {HPD} AS hpd, p.proj_short_name AS project FROM TASK t JOIN PROJECT p ON p.proj_id = t.proj_id "
            "LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id WHERE t.delete_session_id IS NULL AND t.proj_id = ?", o.pid)}
        other = sorted(ids - set(t))
        for i in range(0, len(other), 500):
            chunk = other[i:i + 500]
            t.update({r["task_id"]: _d(r) for r in o.sql(
                f"SELECT t.*, {HPD} AS hpd, p.proj_short_name AS project FROM TASK t JOIN PROJECT p ON "
                "p.proj_id = t.proj_id LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id WHERE t.delete_session_id IS NULL "
                f"AND t.task_id IN ({','.join('?' * len(chunk))})", *chunk)})
        for x in links:
            x["lag"] = float(x["lag"])
        links = [x for x in links if x["succ"] in t and x["pred"] in t]
        by_succ, by_pred = {}, {}
        for x in links:
            by_succ.setdefault(x["succ"], []).append(x)
            by_pred.setdefault(x["pred"], []).append(x)
        return t, links, by_succ, by_pred
    return _cached(o, "net", load)


def _summary(d) -> bool:
    return d["task_type"] in SUMMARY_TYPES


def _open(d) -> bool:
    return d["status_code"] != "TK_Complete" and not _summary(d)


def _mine(o):
    return [d for d in _net(o)[0].values() if d["proj_id"] == o.pid]


def _lag_rule(o):
    return _opt(o, "sched_calendar_on_relationship_lag", "rcal_Predecessor")


def _cal_of(o, d):
    return _cals(o).get(d["clndr_id"])


def _lag_cal(o, p, s):
    """Calendar of a lag under the project's lag rule; None for 24-hour days (or a missing calendar)."""
    rule = _lag_rule(o)
    if rule == "rcal_24Hour":
        return None
    cid = {"rcal_Successor": s["clndr_id"], "rcal_ProjDefault": _prj(o)["clndr_id"]}.get(rule, p["clndr_id"])
    return _cals(o).get(cid)


def _lag_hpd(o, p, s) -> float:
    rule = _lag_rule(o)
    if rule == "rcal_24Hour":
        return 24.0
    if rule == "rcal_ProjDefault":
        c = _cals(o).get(_prj(o)["clndr_id"])
        return c.hpd if c else 8.0
    return float((s if rule == "rcal_Successor" else p)["hpd"] or 8)


def _shift(cal, a: datetime, h: float) -> datetime:
    """a moved by h working hours on cal (elapsed hours without a readable calendar)."""
    if not _ok(cal):
        return a + timedelta(hours=h)
    return cal.add(a, h) if h >= 0 else cal.sub(a, -h)


# ----------------------------------------------------------------- DCMA checks

def _pct(n, d):
    return None if n is None or not d else 100 * n / d


def _row(count, denom, thr, rule, value=None):
    pct = _pct(count, denom)
    if thr is None:
        ok = None
    elif rule == "ratio":
        ok = None if value is None else value >= thr
    else:
        ok = None if pct is None else (pct >= thr if rule == "min" else pct <= thr)
    return {"count": count, "denominator": denom, "pct": pct, "threshold": thr, "pass": ok, "value": value}


def _cpli(o):
    prj = _prj(o)
    dd, end, must = (_dt(prj[k]) for k in ("last_recalc_date", "scd_end_date", "plan_end_date"))
    if not (dd and end and must) or end <= dd:
        return None
    cal = _cals(o).get(prj["clndr_id"])
    if _ok(cal) and cal.work_hours(dd, end) > 0:
        cpl, tf = cal.work_hours(dd, end) / cal.hpd, cal.work_hours(end, must) / cal.hpd
    else:
        cpl, tf = (end - dd).total_seconds() / 86400, (must - end).total_seconds() / 86400
    return (cpl + tf) / cpl


def _cpt_pick(o):
    """The task the critical path test delays: the earliest (early start, Activity ID) of the lowest-float open
    TT_Task / TT_Rsrc activities whose duration can move their finish (no mandatory finish, no expected finish
    in use), on the stored F9 float. None when the test does not run (disabled in schedule_check)."""
    if "critical_path_test" in _settings(o)["disabled"]:
        return None
    use_expect = _opt(o, "sched_use_expect_end_flag", "Y") == "Y"
    cand = [d for d in _mine(o) if d["status_code"] != "TK_Complete" and d["task_type"] in ("TT_Task", "TT_Rsrc")
            and d["total_float_hr_cnt"] is not None and "CS_MANDFIN" not in (d.get("cstr_type"), d.get("cstr_type2"))
            and not (use_expect and d.get("expect_end_date"))]
    if not cand:
        return None
    low = min(d["total_float_hr_cnt"] for d in cand)
    return sorted((d for d in cand if d["total_float_hr_cnt"] <= low + 1),
                  key=lambda d: (_dt(d["early_start_date"]) or datetime.max, d["task_code"]))[0]


def _cpt_pass(o):
    """The test delays the picked task by 100 working days and passes when the project finish moves by 90 %
    of the task's own shift or more. By CPM, when the task's total float equals the project finish's, it lies
    on the longest path and the finish moves by the same working time: pass. Any other case needs a CPM pass
    with the delay, which this oracle does not run: Unchecked."""
    t = _net(o)[0]
    pick = _cpt_pick(o)
    if pick is None:
        return None if "critical_path_test" in _settings(o)["disabled"] else Unchecked(
            "critical path test: no open task to delay (engine result not recomputed)")
    preds = {x["pred"] for x in _net(o)[1] if t[x["succ"]]["proj_id"] == o.pid and t[x["pred"]]["proj_id"] == o.pid}
    own = [d for d in _mine(o) if not _summary(d)]
    ends = [d for d in own if d["task_id"] not in preds and d["status_code"] != "TK_Complete"] or own
    fin = max(ends, key=lambda d: (_dt(d["early_end_date"]) or datetime.min, d["task_type"] == "TT_FinMile",
                                   d["task_code"]))
    if fin["total_float_hr_cnt"] is not None and abs(pick["total_float_hr_cnt"] - fin["total_float_hr_cnt"]) <= 1:
        return True
    return Unchecked("critical path test: the delayed task's total float differs from the project finish's, so "
                     "the result needs a CPM pass with the delay")


def _rem(d) -> float:
    if d["status_code"] == "TK_Complete" or d["task_type"] in MILESTONES:
        return 0.0
    return float(d["remain_drtn_hr_cnt"] or 0)


def _downstream(o, src, start: datetime, finish: datetime) -> dict:
    """Earliest finish of every activity src reaches (LOE and WBS summary left out) when src runs from start to
    finish and nothing else holds them: remaining durations on each activity's calendar, raw lags on the lag
    rule calendar."""
    t, _lk, _bs, by_pred = _net(o)
    seen, stack = {src}, [src]
    while stack:
        n = stack.pop()
        for x in by_pred.get(n, []):
            s = x["succ"]
            if s not in seen and not _summary(t[s]):
                seen.add(s)
                stack.append(s)
    indeg = dict.fromkeys(seen, 0)
    for n in seen:
        for x in by_pred.get(n, []):
            if x["succ"] in seen:
                indeg[x["succ"]] += 1
    order, ready = [], [n for n in seen if not indeg[n]]
    while ready:
        n = ready.pop()
        order.append(n)
        for x in by_pred.get(n, []):
            if x["succ"] in seen:
                indeg[x["succ"]] -= 1
                if not indeg[x["succ"]]:
                    ready.append(x["succ"])
    st, fin = {src: start}, {src: finish}
    for n in order:
        if n not in fin:
            continue
        p = t[n]
        for x in by_pred.get(n, []):
            s = x["succ"]
            if s not in seen:
                continue
            d = t[s]
            a = _shift(_lag_cal(o, p, d), fin[n] if FROM[x["type"]] == "f" else st[n], x["lag"])
            c = _cal_of(o, d)
            f = _shift(c, a, _rem(d)) if TO[x["type"]] == "s" else a
            if s not in fin or f > fin[s]:
                fin[s], st[s] = f, _shift(c, f, -_rem(d))
    return fin


def _key_dates(o):
    """key_dates: constraint dates of open activities against the must finish date (the date itself, then the
    work and lags after it up to the finish milestone), constrained milestones against each other, and the
    project finish against the must finish date."""
    t, _lk, _bs, by_pred = _net(o)
    prj = _prj(o)
    own = [d for d in _mine(o) if _open(d)]
    ends = sorted((d for d in own if not any(not _summary(t[x["succ"]]) for x in by_pred.get(d["task_id"], []))),
                  key=lambda d: (d["task_type"] == "TT_FinMile", _dt(d["early_end_date"]) or datetime.min, d["task_code"]))
    fm = ends[-1] if ends else None
    cons = [(d, ty, _dt(dt)) for d in own for ty, dt in ((d.get("cstr_type"), d.get("cstr_date")),
                                                        (d.get("cstr_type2"), d.get("cstr_date2")))
            if ty and ty != "CS_ALAP" and _dt(dt) is not None]
    must, end = _dt(prj["plan_end_date"]), _dt(prj["scd_end_date"])
    hits = []  # (task_code, constraint type) of each issue row
    for d, ty, dt in cons:
        c = _cal_of(o, d)
        start, fin = (_shift(c, dt, -_rem(d)), dt) if ty in FINISH_CSTR else (dt, _shift(c, dt, _rem(d)))
        if must and dt > must + TOL:
            hits.append((d["task_code"], ty))
        if fm is None or must is None:
            continue
        reach = _downstream(o, d["task_id"], start, fin)
        if fm["task_id"] in reach and reach[fm["task_id"]] > must + TOL:
            hits.append((d["task_code"], ty))
    miles = [(d, ty, dt) for d, ty, dt in cons if d["task_type"] in MILESTONES]
    for d, _ty, dt in miles:
        reach = _downstream(o, d["task_id"], dt, dt)
        for e, ty2, dt2 in miles:
            if e["task_id"] != d["task_id"] and e["task_id"] in reach and reach[e["task_id"]] > dt2 + TOL:
                hits.append((e["task_code"], ty2))
    if fm is not None and must and end and end > must + TOL:
        hits.append((fm["task_code"], None))
    denom = len(cons) + (1 if must else 0)
    return {"count": len(hits), "denominator": denom, "pct": 100 * len(set(hits)) / denom if denom else None,
            "threshold": None, "pass": None, "value": None}


def _dcma(o) -> dict:
    return _cached(o, "dcma", lambda: _dcma_load(o))


def _dcma_load(o) -> dict:
    """check -> {count, denominator, pct, threshold, pass, value} in the order of p6_health_check."""
    cfg, prj = _settings(o), _prj(o)
    thr, lim = cfg["threshold"], cfg["limit"]
    t, lk, by_succ, by_pred = _net(o)
    mine = _mine(o)
    acts = [d for d in mine if not _summary(d)]
    opened = [d for d in acts if d["status_code"] != "TK_Complete"]
    work = [d for d in opened if d["task_type"] in ("TT_Task", "TT_Rsrc")]
    dd = _dt(prj["last_recalc_date"])
    out = {}

    def rule(name):
        return DCMA[name][1]

    def has(d, side):  # a predecessor (side 'pred') or successor of d that is not LOE or WBS summary
        lst, other = (by_succ, "pred") if side == "pred" else (by_pred, "succ")
        return any(not _summary(t[x[other]]) for x in lst.get(d["task_id"], []))
    starts = sorted((d for d in mine if d["task_type"] == "TT_Mile" and not has(d, "pred")),
                    key=lambda d: (d["act_start_date"] or d["early_start_date"] or "9999", d["task_code"], d["task_id"]))
    finishes = sorted((d for d in mine if d["task_type"] == "TT_FinMile" and not has(d, "succ")),
                      key=lambda d: (d["act_end_date"] or d["early_end_date"] or "", d["task_code"], d["task_id"]))
    sms = starts[0]["task_id"] if starts else None
    fms = finishes[-1]["task_id"] if finishes else None
    logic = [d for d in opened if (not has(d, "pred") and d["task_id"] != sms) or (not has(d, "succ") and d["task_id"] != fms)]
    out["logic"] = _row(len(logic), len(opened), thr["logic"], rule("logic"))

    olinks = [x for x in lk if t[x["succ"]]["proj_id"] == o.pid and _open(t[x["succ"]]) and not _summary(t[x["pred"]])]
    n = len(olinks)
    out["leads"] = _row(sum(x["lag"] < 0 for x in olinks), n, thr["leads"], rule("leads"))
    out["lags"] = _row(sum(x["lag"] > 0 for x in olinks), n, thr["lags"], rule("lags"))
    ll = lim["long_lags"]
    out["long_lags"] = _row(sum(x["lag"] > (ll[1] if ll[0] == "h" else ll[1] * _lag_hpd(o, t[x["pred"]], t[x["succ"]]))
                                for x in olinks), n, thr["long_lags"], rule("long_lags"))
    out["fs_links"] = _row(sum(x["type"] == "PR_FS" for x in olinks), n, thr["fs_links"], rule("fs_links"))
    out["logic_density"] = _row(n, len(opened), thr["logic_density"], "ratio", n / len(opened) if opened else None)
    out["logic_density"]["pct"] = None  # a ratio: no share
    out["hard_constraints"] = _row(sum(d.get("cstr_type") in HARD or d.get("cstr_type2") in HARD for d in opened),
                                   len(opened), thr["hard_constraints"], rule("hard_constraints"))
    out["high_float"] = _row(sum(_over(lim["high_float"], d["total_float_hr_cnt"], d["hpd"]) for d in opened),
                             len(opened), thr["high_float"], rule("high_float"))
    out["negative_float"] = _row(sum((d["total_float_hr_cnt"] or 0) < 0 for d in opened), len(opened),
                                 thr["negative_float"], rule("negative_float"))
    out["high_duration"] = _row(sum(_over(lim["high_duration"], d["remain_drtn_hr_cnt"], d["hpd"]) for d in work),
                                len(work), thr["high_duration"], rule("high_duration"))
    if dd:
        def bad_dates(d):
            late = any(_dt(d[k]) and _dt(d[k]) > dd for k in ("act_start_date", "act_end_date"))
            early = d["status_code"] != "TK_Complete" and any(_dt(d[k]) and _dt(d[k]) < dd
                                                              for k in ("early_start_date", "early_end_date"))
            return late or early
        out["invalid_dates"] = _row(sum(bad_dates(d) for d in acts), len(acts), thr["invalid_dates"],
                                    rule("invalid_dates"))
    else:
        out["invalid_dates"] = _row(None, len(acts), thr["invalid_dates"], rule("invalid_dates"))
    assigned = {r["task_id"] for r in o.sql("SELECT a.task_id FROM TASKRSRC a JOIN TASK t ON t.task_id = a.task_id "
                                            "WHERE t.proj_id = ? AND a.delete_session_id IS NULL", o.pid)}
    out["resources"] = _row(sum((d["target_drtn_hr_cnt"] or 0) > 0 and d["task_id"] not in assigned for d in work),
                            len(work), thr["resources"], rule("resources"))
    bid = prj["sum_base_proj_id"]
    if bid is not None and dd:
        cur = {d["task_code"]: d for d in mine}
        due = []
        for b in o.sql(f"SELECT task_code, act_end_date, early_end_date FROM TASK WHERE proj_id = ? "
                       f"AND delete_session_id IS NULL AND task_type NOT IN {S}", bid):
            bf = _dt(b["act_end_date"] or b["early_end_date"])
            if bf and bf <= dd:
                due.append((b["task_code"], bf))

        def missed(code, bf):
            a = cur.get(code)
            if a is None or a["status_code"] != "TK_Complete":
                return True
            af = _dt(a["act_end_date"])
            return af is not None and af.date() > bf.date()  # compared by day; no actual finish: not later
        out["missed_tasks"] = _row(sum(missed(c, bf) for c, bf in due), len(due), thr["missed_tasks"],
                                   rule("missed_tasks"))
        done = sum(d["status_code"] == "TK_Complete" for d in acts)
        bei = _row(done, len(due), thr["bei"], "ratio", done / len(due) if due else None)
    else:
        out["missed_tasks"] = _row(None, None, thr["missed_tasks"], "max")
        bei = _row(None, None, thr["bei"], "ratio")
    out["critical_path_test"] = {"count": None, "denominator": None, "pct": None, "threshold": None,
                                 "pass": _cpt_pass(o), "value": None}
    cpli = _cpli(o)
    out["cpli"] = {"count": None, "denominator": None, "pct": None, "threshold": thr["cpli"], "value": cpli,
                   "pass": None if thr["cpli"] is None or cpli is None else cpli >= thr["cpli"]}
    out["bei"] = bei
    out["key_dates"] = _key_dates(o)
    return {k: out[k] for k in [*DCMA, "key_dates"]}  # the order of p6_health_check


def dcma(o):
    return [{"check": k, **{c: v[c] for c in ("count", "denominator", "pct", "value", "threshold", "pass")}}
            for k, v in _dcma(o).items()][:17]


def _score(o):
    passes = [v["pass"] for k, v in _dcma(o).items() if k not in UNSCORED]
    if any(isinstance(p, Unchecked) for p in passes):  # the critical path test was not recomputed
        why = "score: counts include the critical path test, whose pass is not recomputed here"
        return {k: Unchecked(why) for k in ("passed", "failed", "not_evaluated", "evaluated", "pct")}
    p, f = passes.count(True), passes.count(False)
    return {"passed": p, "failed": f, "not_evaluated": passes.count(None), "evaluated": p + f,
            "pct": round(100 * p / (p + f), 1) if p + f else None}  # the tool gives 1 decimal


# ----------------------------------------------------------------- trend (snapshots of earlier audits)

def _snapshots(o) -> list[dict]:
    out = []
    for path in sorted(glob.glob(os.path.join(o.work, "editlog", "health", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            s = json.load(fh)
        if s.get("project") == o.args["project"] and str(s.get("db", "")).lower() == os.path.basename(o.db).lower():
            out.append(s)
    return sorted(out, key=lambda s: s.get("id", ""))


def _trend_error(o):
    n = len(_snapshots(o))
    return Contains("before='previous'", f"{o.args['project']} has {n} health snapshot(s)") if n < 2 else None


def trend(o):
    snaps = _snapshots(o)
    if len(snaps) < 2:
        return []  # the compare call fails: no table
    a, b = snaps[-2]["checks"], snaps[-1]["checks"]
    rows = []
    for k in dict.fromkeys(list(a) + list(b)):
        ca, cb = a.get(k, {}).get("count"), b.get(k, {}).get("count")
        rows.append({"check": k, "before": ca, "after": cb, "delta": None if ca is None or cb is None else cb - ca,
                     "pass": b.get(k, {}).get("pass")})
    return rows[:17]


# ----------------------------------------------------------------- dangling ends

def _dangling(o) -> list[dict]:
    def load():
        t, _lk, by_succ, by_pred = _net(o)
        rows = []
        for d in sorted(_mine(o), key=lambda d: (d["task_code"], d["task_id"])):
            if not _open(d) or d["task_type"] in MILESTONES:
                continue
            for kind, lst, other, good in (("start", by_succ, "pred", ("PR_FS", "PR_SS")),
                                           ("finish", by_pred, "succ", ("PR_FS", "PR_FF"))):
                real = [x for x in lst.get(d["task_id"], []) if not _summary(t[x[other]])]
                if real and not any(x["type"] in good for x in real):
                    rows.append({"kind": kind, "activity": (d["task_code"], d["task_name"]),
                                 "tf": None if d["total_float_hr_cnt"] is None else d["total_float_hr_cnt"] / d["hpd"],
                                 "reason": _suggestion(o, d, kind, lst.get(d["task_id"], []), other)})
        return sorted(rows, key=lambda r: (r["kind"] != "start", r["activity"][0]))
    return _cached(o, "dangling", load)


def _suggestion(o, d, kind, links, other):
    """What p6_dangling proposes: the missing half of a ladder (an FF predecessor gives an SS, an SS successor
    an FF), else an FS from the latest-finishing (to the earliest-starting) other activity of the same WBS
    before its start (after its finish) that is not linked yet; None when there is none."""
    t = _net(o)[0]
    ladder = [t[x[other]]["task_code"] for x in sorted(links, key=lambda x: x["id"])
              if x["type"] == ("PR_FF" if kind == "start" else "PR_SS") and not _summary(t[x[other]])
              and t[x[other]]["proj_id"] == o.pid]
    if ladder:
        return Contains("ladder", ladder[0])
    linked = {x[other] for x in links}
    same = [x for x in _mine(o) if x["wbs_id"] == d["wbs_id"] and x["task_id"] != d["task_id"] and not _summary(x)
            and x["task_id"] not in linked]
    if kind == "start":
        es = _dt(d["early_start_date"])
        c = [x for x in same if es and _dt(x["early_end_date"]) and _dt(x["early_end_date"]) <= es]
        x = max(c, key=lambda x: (_dt(x["early_end_date"]), x["task_code"]), default=None)
        return x and Contains("closest activity of the same WBS finishing before", str(x["early_end_date"]))
    ef = _dt(d["early_end_date"])
    c = [x for x in same if x["status_code"] != "TK_Complete" and ef and _dt(x["early_start_date"])
         and _dt(x["early_start_date"]) >= ef]
    x = min(c, key=lambda x: (_dt(x["early_start_date"]), x["task_code"]), default=None)
    return x and Contains("closest activity of the same WBS starting after", str(x["early_start_date"]))


def dangling(o):
    return _dangling(o)[:15]


# ----------------------------------------------------------------- redundant links

def _gap(o, x):
    """Working hours from the predecessor's early date plus the lag left at the data date to the successor's
    early date (successor calendar); None when a date or a calendar is missing or unreadable."""
    t = _net(o)[0]
    p, s = t[x["pred"]], t[x["succ"]]
    a = _dt(p["early_start_date"] if FROM[x["type"]] == "s" else p["early_end_date"])
    b = _dt(s["early_start_date"] if TO[x["type"]] == "s" else s["early_end_date"])
    cal, lc = _cal_of(o, s), _lag_cal(o, p, s)
    if a is None or b is None or not _ok(cal) or (lc is not None and lc.error):
        return None
    lag = x["lag"]
    if _opt(o, "sched_lag_early_start_flag", "Y") != "N":
        ref = _dt(p["act_start_date"] if FROM[x["type"]] == "s" else p["act_end_date"])
        dd = _dt(_prj(o)["last_recalc_date"])
        if lag > 0 and ref and dd and ref < dd:
            lag = max(0.0, lag - (lc.work_hours(ref, dd) if lc else (dd - ref).total_seconds() / 3600))
    anchor = a + timedelta(hours=lag) if lc is None else (lc.add(a, lag) if lag >= 0 else lc.sub(a, -lag))
    return cal.work_hours(anchor, b)


def _transitive(o) -> set:
    """FS links A -> C (C open in the project, no summary end) implied by an FS chain of 2 to 10 links through
    non-summary activities whose lags add up to at least the direct lag; as the tool defines it, the search
    does not go through activities whose early start is after the latest early start of A's direct targets."""
    t, lk, _bs, _bp = _net(o)
    fs = {}
    for x in lk:
        if x["type"] == "PR_FS" and not _summary(t[x["pred"]]) and not _summary(t[x["succ"]]):
            fs.setdefault(x["pred"], []).append(x)
    out = set()
    for a, direct in fs.items():
        targets = [x for x in direct if t[x["succ"]]["proj_id"] == o.pid and t[x["succ"]]["status_code"] != "TK_Complete"]
        if not targets:
            continue
        horizon = max((_dt(t[x["succ"]]["early_start_date"]) for x in targets if t[x["succ"]]["early_start_date"]),
                      default=None)
        best2, layer = {}, {a: 0.0}  # layer: node -> max lag sum over paths of exactly k links
        for k in range(1, CHAIN + 1):
            nxt = {}
            for n, v in layer.items():
                for x in fs.get(n, []):
                    c = x["succ"]
                    es = _dt(t[c]["early_start_date"])
                    if c == a or (horizon and es and es > horizon):
                        continue
                    if c not in nxt or v + x["lag"] > nxt[c]:
                        nxt[c] = v + x["lag"]
            if k >= 2:
                for c, v in nxt.items():
                    best2[c] = max(best2.get(c, v), v)
            layer = nxt
            if not layer:
                break
        out |= {x["id"] for x in targets if x["succ"] in best2 and best2[x["succ"]] + TOL_H >= x["lag"]}
    return out


def _redundant(o):
    return _cached(o, "redundant", lambda: _redundant_load(o))


def _redundant_load(o):
    t, lk, by_succ, by_pred = _net(o)
    own = [x for x in lk if t[x["succ"]]["proj_id"] == o.pid]
    hit = {}
    for x in own:
        p, s = t[x["pred"]], t[x["succ"]]
        if p["status_code"] == "TK_Complete" and s["status_code"] != "TK_Complete":
            hit.setdefault(x["id"], set()).add("completed_predecessor")
        if any("(deleted)" in (d["task_name"] or "").lower() for d in (p, s)):
            hit.setdefault(x["id"], set()).add("marked_deleted")
    for i in _transitive(o):
        hit.setdefault(i, set()).add("transitive")
    seen = set()
    for x in own:
        key = (x["succ"], x["pred"], x["type"])
        if key in seen:
            hit.setdefault(x["id"], set()).add("duplicate")
        seen.add(key)
    byid = {x["id"]: x for x in own}
    rows = []
    for i, cs in hit.items():
        x = byid[i]
        p, s = t[x["pred"]], t[x["succ"]]
        g = _gap(o, x)
        rows.append({"id": i, "pred": (p["task_code"], p["task_name"]), "succ": (s["task_code"], s["task_name"]),
                     "type": REL.get(x["type"], x["type"]), "lag": x["lag"] / _lag_hpd(o, p, s),
                     "categories": [c for c in CATEGORIES if c in cs], "drives": g is not None and abs(g) <= TOL_H})
    rows.sort(key=lambda r: (CATEGORIES.index(r["categories"][0]), r["succ"][0], r["pred"][0], r["id"]))
    side = 0
    for ids, lst, other in (({byid[i]["succ"] for i in hit}, by_succ, "pred"),
                            ({byid[i]["pred"] for i in hit}, by_pred, "succ")):
        for n in ids:
            if _open(t[n]) and not [x for x in lst.get(n, []) if x["id"] not in hit and not _summary(t[x[other]])]:
                side += 1
    return rows, side


def redundant(o):
    return [{k: r[k] for k in ("pred", "succ", "type", "lag", "categories", "drives")} for r in _redundant(o)[0][:15]]


# ----------------------------------------------------------------- float

def _float_rows(o):
    return _cached(o, "float", lambda: [_d(r) for r in o.sql(
        f"SELECT t.total_float_hr_cnt AS tf, t.free_float_hr_cnt AS ff, {HPD} AS hpd FROM TASK t "
        "LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id WHERE t.proj_id = ? AND t.delete_session_id IS NULL "
        f"AND t.status_code <> 'TK_Complete' AND t.task_type NOT IN {S}", o.pid)])


def _g(v: float) -> str:
    return f"{v:g}"


def _buckets():
    """(label, test(hours, hpd)) in order: below the first edge, [a, b) under 0, = 0, (a, b] over 0, above."""
    out = [(f"< {_g(EDGES[0])}", lambda h, d: h < EDGES[0] * d)]
    for a, b in zip(EDGES, EDGES[1:]):
        if b <= 0:
            out.append((f"[{_g(a)}, {_g(b)})", lambda h, d, a=a, b=b: a * d <= h < b * d))
        else:
            if a == 0:
                out.append(("= 0", lambda h, d: h == 0))
            out.append((f"({_g(a)}, {_g(b)}]", lambda h, d, a=a, b=b: a * d < h <= b * d))
    out.append((f"> {_g(EDGES[-1])}", lambda h, d: h > EDGES[-1] * d))
    return out


def float_table(o):
    rows = _float_rows(o)
    n = len(rows)
    out = []
    for label, test in _buckets():
        tf = sum(r["tf"] is not None and test(r["tf"], r["hpd"]) for r in rows)
        ff = sum(r["ff"] is not None and test(r["ff"], r["hpd"]) for r in rows)
        out.append({"range": label, "tf": tf, "tf_pct": 100 * tf / n if n else None, "ff": ff,
                    "ff_pct": 100 * ff / n if n else None})
    return out[:10]


def _tf_days(o):
    return [r["tf"] / r["hpd"] for r in _float_rows(o) if r["tf"] is not None]


def _critical(o):
    crit, args = o.critical_sql("t")
    return o.one(f"SELECT COUNT(*) FROM TASK t WHERE t.proj_id = ? AND t.delete_session_id IS NULL AND "
                 f"t.status_code <> 'TK_Complete' AND t.task_type NOT IN {S} AND {crit}", o.pid, *args)


def _crit_definition(o):
    r = _prj(o)
    if r["critical_path_type"] == "CT_DrivPath":
        return Contains("CT_DrivPath")
    return Contains(r["critical_path_type"], f"total float <= {float(r['critical_drtn_hr_cnt'] or 0):g} h")


# ----------------------------------------------------------------- slots

def _base_name(o):
    bid = _prj(o)["sum_base_proj_id"]
    return None if bid is None else o.one("SELECT proj_short_name FROM PROJECT WHERE proj_id = ?", bid)


def _pick_field(o, field):
    pick = _cpt_pick(o)
    return None if pick is None else pick[field]


UNSCORED = ("logic_density",)  # in checks, outside score and summary
WEIGHTS = {"logic_density": 20, "logic": 20, "critical_path_test": 15, "negative_float": 15, "high_float": 10,
           "hard_constraints": 10, "high_duration": 5, "leads": 5, "lags": 5, "fs_links": 5}
GRADES = (("A", 90), ("B", 80), ("C", 70), ("D", 55))


def _status(name, c) -> str:
    """pass, warn (failed inside the band: at most up to 2 x the threshold, at least down to 0.9 x), fail or
    not_evaluated; no band for a zero or missing threshold."""
    if c["pass"] is None:
        return "not_evaluated"
    if c["pass"]:
        return "pass"
    thr, r = c["threshold"], DCMA[name][1]
    if not thr or r is None:
        return "fail"
    if r == "ratio":
        return "warn" if c["value"] is not None and c["value"] >= 0.9 * thr else "fail"
    return "warn" if (c["pct"] <= 2 * thr if r == "max" else c["pct"] >= 0.9 * thr) else "fail"


def _weighted(o) -> dict:
    d = _dcma(o)
    if isinstance(d["critical_path_test"]["pass"], Unchecked):
        why = "weighted score: the critical path test's pass is not recomputed here"
        return {"rows": Unchecked(why), "points": Unchecked(why), "grade": Unchecked(why)}
    rows, earned, top = [], 0.0, 0
    for k, w in WEIGHTS.items():
        st = _status(k, d[k])
        e = None if st == "not_evaluated" else w * {"pass": 1.0, "warn": 0.5, "fail": 0.0}[st]
        if e is not None:
            earned, top = earned + e, top + w
        rows.append({"check": k, "weight": w, "status": st, "earned": e})
    points = round(100 * earned / top, 1) if top else None
    grade = None if points is None else next((g for g, lo in GRADES if points >= lo), "F")
    return {"rows": rows, "points": points, "grade": grade}


def _worst(o, high: bool):
    """The open activity with the highest float above the high float limit (high) or the lowest negative float,
    by float in days, then Activity ID."""
    lim = _settings(o)["limit"]["high_float"]
    cand = [d for d in _mine(o) if _open(d) and d["total_float_hr_cnt"] is not None
            and (_over(lim, d["total_float_hr_cnt"], d["hpd"]) if high else d["total_float_hr_cnt"] < 0)]
    if not cand:
        return None
    return sorted(cand, key=lambda d: ((-1 if high else 1) * d["total_float_hr_cnt"] / d["hpd"], d["task_code"],
                                       d["task_id"]))[0]


def _expl(o, high: bool):
    from oracles.milestone_tracker import WORDS, network
    from oracles.update_integrity_audit import _sources
    d = _worst(o, high)
    if d is None:
        return None
    kinds = sorted({k for k, _s in _sources(network(o), d["task_code"])})
    tf = round(d["total_float_hr_cnt"] / d["hpd"], 2)
    return Contains(f"Total float {tf} d of {d['task_code']} comes from", *(WORDS[k] for k in kinds))


def _engine(o):
    from oracles.logic_date_integrity import engine
    return engine(o)


SLOTS = {
    "data_date": lambda o: _prj(o)["last_recalc_date"],
    "last_f9": lambda o: _prj(o)["last_schedule_date"],
    "stale": lambda o: o.stale(),
    "score_passed": lambda o: _score(o)["passed"],
    "score_failed": lambda o: _score(o)["failed"],
    "score_not_evaluated": lambda o: _score(o)["not_evaluated"],
    "score_evaluated": lambda o: _score(o)["evaluated"],
    "score_pct": lambda o: _score(o)["pct"],
    "threshold_source": lambda o: Contains(_settings(o)["source"]),
    "baseline": _base_name,
    "open_activities": lambda o: len(_float_rows(o)),
    "cpt_activity": lambda o: (_pick_field(o, "task_code"), _pick_field(o, "task_name")),
    "lags": lambda o: _dcma(o)["lags"]["count"],
    "high_float": lambda o: _dcma(o)["high_float"]["count"],
    "missed": lambda o: _dcma(o)["missed_tasks"]["count"],
    "trend_error": _trend_error,
    "dangling": lambda o: len(_dangling(o)),
    "redundant": lambda o: len(_redundant(o)[0]),
    "red_side_effects": lambda o: _redundant(o)[1],
    "tf_min": lambda o: min(_tf_days(o), default=None),
    "tf_max": lambda o: max(_tf_days(o), default=None),
    "tf_negative": lambda o: sum(v < 0 for v in _tf_days(o)),
    "critical": _critical,
    "critical_definition": _crit_definition,
    "match_rate": lambda o: round(1 - _engine(o)["bad_open"] / _engine(o)["open"], 4),
    "trusted": lambda o: _engine(o)["bad_open"] / _engine(o)["open"] <= 0.01,
    "w_points": lambda o: _weighted(o)["points"],
    "w_grade": lambda o: _weighted(o)["grade"],
    "logic_count": lambda o: _dcma(o)["logic"]["count"],
    "fs_pass": lambda o: _dcma(o)["fs_links"]["pass"],
    "neg_expl": lambda o: _expl(o, False),
    "high_expl": lambda o: _expl(o, True),
}
TABLES = {"dcma": dcma, "trend": trend, "dangling": dangling, "redundant": redundant, "float": float_table,
          "weighted": lambda o: _weighted(o)["rows"]}
