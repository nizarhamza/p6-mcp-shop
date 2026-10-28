"""Oracles of baseline-variance: P6's TASK, TASKPRED, TASKRSRC, CALENDAR, PROJECT and PROJPROP rows of the project
and of its baseline read with SQL; activities and links matched here, working time counted with an own parser
of CALENDAR.clndr_data, earned value from the linear spread of the assignments (oracles.progress_earned_value)."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from oracles import Contains
from oracles.progress_earned_value import baseline_pid, dt, earned_value

TOL_H = 5 / 60  # a variance within 5 minutes of work is on time
CAUSES = ("late_start", "longer_duration", "late_start_and_longer_duration", "on_time", "earlier")
SERIAL0 = date(1899, 12, 30)


# ----------------------------------------------------------------- calendars

def _node(s: str, i: int):
    """One node of a P6 text tree at s[i] == '(': ((name, attrs, children), next index)."""
    j = s.index("(", i + 1)
    k = s.index(")", j + 1)
    name, attrs, kids, n = s[i + 1:j].split("||")[-1], s[j + 1:k], [], k + 2
    while s[n] == "(":
        kid, n = _node(s, n)
        kids.append(kid)
    return (name, attrs, kids), n + 2


def _find(node, name):
    if node[0] == name:
        return node
    for kid in node[2]:
        hit = _find(kid, name)
        if hit:
            return hit
    return None


def _shifts(kids) -> list[tuple[int, int]]:
    out = []
    for _name, attrs, _k in kids:
        p = attrs.split("|")
        kv = dict(zip(p[::2], p[1::2], strict=False))
        if "s" in kv and "f" in kv:
            s = int(kv["s"][:-3]) * 60 + int(kv["s"][-2:])
            f = int(kv["f"][:-3]) * 60 + int(kv["f"][-2:]) or 24 * 60
            out.append((s, f))
    return sorted(out)


class Cal:
    """Working time of one calendar: week[python weekday] = shifts in minutes, exceptions by date."""

    def __init__(self, o, clndr_id: int, depth: int = 0):
        r = o.sql("SELECT clndr_data, day_hr_cnt, base_clndr_id FROM CALENDAR WHERE clndr_id = ?", clndr_id)[0]
        self.hpd = float(r["day_hr_cnt"] or 8)
        data = r["clndr_data"]
        data = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
        root = _node(re.sub(r"\s", "", data), 0)[0]
        base = Cal(o, r["base_clndr_id"], depth + 1) if r["base_clndr_id"] and depth < 10 else None
        dow = _find(root, "DaysOfWeek")
        if dow is None and base is not None:
            self.week = base.week
        else:
            self.week = {(int(n) + 5) % 7: _shifts(kids) for n, _a, kids in (dow[2] if dow else [])}
        self.exc = dict(base.exc) if base else {}
        exc = _find(root, "Exceptions")
        for _n, attrs, kids in exc[2] if exc else []:
            p = attrs.split("|")
            kv = dict(zip(p[::2], p[1::2], strict=False))
            if "d" in kv:
                self.exc[SERIAL0 + timedelta(days=int(float(kv["d"])))] = _shifts(kids)

    def day(self, d: date):
        return self.exc[d] if d in self.exc else self.week.get(d.weekday(), [])

    def hours(self, a: datetime, b: datetime) -> float:
        """Working hours from a to b (negative when b is before a)."""
        if b < a:
            return -self.hours(b, a)
        total, d = 0.0, a.date()
        while d <= b.date():
            day0 = datetime.combine(d, datetime.min.time())
            for s, f in self.day(d):
                lo, hi = max(a, day0 + timedelta(minutes=s)), min(b, day0 + timedelta(minutes=f))
                if hi > lo:
                    total += (hi - lo).total_seconds() / 3600
            d += timedelta(days=1)
        return total


_CALS: dict = {}


def cal(o, clndr_id):
    key = (o.db, clndr_id)
    if key not in _CALS:
        _CALS[key] = Cal(o, clndr_id)
    return _CALS[key]


# ----------------------------------------------------------------- activities

def _acts(o, pid):
    return {r["task_code"]: r for r in o.sql(
        "SELECT task_id, task_code, task_name, status_code, clndr_id, target_drtn_hr_cnt, total_float_hr_cnt, "
        "COALESCE(act_start_date, early_start_date) AS st, COALESCE(act_end_date, early_end_date) AS fin, "
        "julianday(COALESCE(act_start_date, early_start_date)) AS jst, "
        "julianday(COALESCE(act_end_date, early_end_date)) AS jfin "
        "FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL ORDER BY task_id DESC", pid)}


def slip(o, a, b):
    """(start variance wd, duration delta wd, cause) of a matched activity, its own calendar."""
    c = cal(o, a["clndr_id"])
    s, f, bs, bf = dt(a["st"]), dt(a["fin"]), dt(b["st"]), dt(b["fin"])
    if not (s and f and bs and bf):
        return None, None, None
    sv, fv = c.hours(bs, s), c.hours(bf, f)
    dv = fv - sv
    if fv > TOL_H:
        late, longer = sv > TOL_H, dv > TOL_H
        cause = ("late_start_and_longer_duration" if late and longer else "late_start" if late else
                 "longer_duration" if longer else "late_start" if sv >= dv else "longer_duration")
    else:
        cause = "on_time" if fv >= -TOL_H else "earlier"
    return sv / c.hpd, dv / c.hpd, cause


def _compare(o):
    bid = baseline_pid(o)
    return _acts(o, o.pid), _acts(o, bid)


def summary(o) -> dict:
    a, b = _compare(o)
    m = [(x, b[k]) for k, x in a.items() if k in b]
    v = [x["jfin"] - y["jfin"] for x, y in m]
    later = [d for d in v if d > 0]
    causes = [slip(o, x, y)[2] for x, y in m]
    return {"matched": len(m), "added": len(a) - len(m), "removed": sum(k not in a for k in b),
            "later": len(later), "earlier": sum(d < 0 for d in v), "same_finish": sum(d == 0 for d in v),
            "later_avg_cd": sum(later) / len(later) if later else None, "later_max_cd": max(later, default=None),
            "earlier_max_cd": min((d for d in v if d < 0), default=None),
            "name_changed": sum(x["task_name"] != y["task_name"] for x, y in m),
            "status_changed": sum(x["status_code"] != y["status_code"] for x, y in m),
            "dur_changed": sum((x["target_drtn_hr_cnt"] or 0) != (y["target_drtn_hr_cnt"] or 0) for x, y in m),
            "slip_unknown": causes.count(None), "causes": {c: causes.count(c) for c in CAUSES}}


def moved(o) -> list[dict]:
    """First page (cap 20): added and removed first, then matched ones with |variance| >= 1 cd, largest first."""
    a, b = _compare(o)
    rows = []
    for k, x in a.items():
        y = b.get(k)
        hpd = cal(o, x["clndr_id"]).hpd
        if y is None:
            rows.append(((0, 0, k, x["task_id"]), {"activity": (k, x["task_name"]), "change": "added",
                                                   "status": x["status_code"], "bl_start": None, "start": x["st"],
                                                   "start_var": None, "bl_finish": None, "finish": x["fin"],
                                                   "var_cd": None, "var_wd": None, "dur": None, "cause": None,
                                                   "tf": None if x["total_float_hr_cnt"] is None
                                                   else x["total_float_hr_cnt"] / hpd}))
            continue
        v = x["jfin"] - y["jfin"]
        if abs(v) < 1:
            continue
        sv, dv, cause = slip(o, x, y)
        c = cal(o, x["clndr_id"])
        rows.append(((1, -round(abs(v), 6), k, x["task_id"]), {
            "activity": (k, x["task_name"]), "change": "matched", "status": x["status_code"], "bl_start": y["st"],
            "start": x["st"], "start_var": sv, "bl_finish": y["fin"], "finish": x["fin"], "var_cd": v,
            "var_wd": c.hours(dt(y["fin"]), dt(x["fin"])) / c.hpd, "dur": dv, "cause": cause,
            "tf": None if x["total_float_hr_cnt"] is None else x["total_float_hr_cnt"] / hpd}))
    for k, y in b.items():
        if k not in a:
            rows.append(((0, 0, k, y["task_id"]), {"activity": (k, y["task_name"]), "change": "removed", "status": None,
                                                   "bl_start": y["st"], "start": None, "start_var": None,
                                                   "bl_finish": y["fin"], "finish": None, "var_cd": None,
                                                   "var_wd": None, "dur": None, "cause": None, "tf": None}))
    return [r for _k, r in sorted(rows, key=lambda x: x[0])][:20]


# ----------------------------------------------------------------- relationships

def _lag_rule(o, pid) -> str:
    v = o.one("SELECT prop_value FROM PROJPROP WHERE proj_id = ? AND prop_name = 'scheduling'", pid)
    v = v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")
    m = re.search(r"sched_calendar_on_relationship_lag\|(\w+)", v)
    rule = m.group(1) if m else "rcal_Predecessor"
    return rule if rule in ("rcal_Successor", "rcal_24Hour", "rcal_ProjDefault") else "rcal_Predecessor"


def _links(o, pid) -> dict:
    """{(pred, succ, type, pred project or None): (lag days under pid's lag rule, lag hours)}, the lowest id."""
    rule = _lag_rule(o, pid)
    proj_hpd = o.one("SELECT COALESCE(NULLIF(c.day_hr_cnt, 0), 8) FROM PROJECT p LEFT JOIN CALENDAR c "
                     "ON c.clndr_id = p.clndr_id WHERE p.proj_id = ?", pid)
    out = {}
    for r in o.sql("SELECT r.task_pred_id, pt.task_code AS pred, st.task_code AS succ, pt.task_name AS pn, st.task_name AS sn, r.pred_type, pt.proj_id AS pp, "
                   "pp.proj_short_name AS pname, r.lag_hr_cnt, COALESCE(NULLIF(cp.day_hr_cnt, 0), 8) AS ph, "
                   "COALESCE(NULLIF(cs.day_hr_cnt, 0), 8) AS sh FROM TASKPRED r JOIN TASK st ON st.task_id = r.task_id "
                   "JOIN TASK pt ON pt.task_id = r.pred_task_id LEFT JOIN PROJECT pp ON pp.proj_id = pt.proj_id "
                   "LEFT JOIN CALENDAR cp ON cp.clndr_id = pt.clndr_id LEFT JOIN CALENDAR cs ON cs.clndr_id = st.clndr_id "
                   "WHERE st.proj_id = ? AND r.delete_session_id IS NULL AND st.delete_session_id IS NULL "
                   "AND pt.delete_session_id IS NULL ORDER BY r.task_pred_id DESC", pid):
        key = (r["pred"], r["succ"], r["pred_type"], None if r["pp"] == pid else r["pname"])
        hpd = {"rcal_Successor": r["sh"], "rcal_24Hour": 24, "rcal_ProjDefault": proj_hpd}.get(rule, r["ph"])
        out[key] = ((r["lag_hr_cnt"] or 0) / hpd, r["lag_hr_cnt"], r["task_pred_id"], r["pn"], r["sn"])
    return out


def _link_sets(o):
    return _links(o, o.pid), _links(o, baseline_pid(o))


def link_summary(o) -> dict:
    la, lb = _link_sets(o)
    both = [k for k in la if k in lb]
    return {"matched": len(both), "added": len(la) - len(both), "removed": sum(k not in la for k in lb),
            "lag_changed": sum((la[k][1] or 0) != (lb[k][1] or 0) for k in both)}


def links(o) -> list[dict]:
    la, lb = _link_sets(o)
    rows = []
    for k, (d, h, rid, pn, sn) in la.items():  # names of the project, of the baseline for a removed link
        if k not in lb or (h or 0) != (lb[k][1] or 0):
            rows.append(("added" if k not in lb else "lag_changed", k, d, lb[k][0] if k in lb else None, rid, pn, sn))
    rows += [("removed", k, None, d, rid, pn, sn) for k, (d, h, rid, pn, sn) in lb.items() if k not in la]
    rows.sort(key=lambda r: (r[0], r[1][1], r[1][0], r[1][2], r[4]))
    types = {"PR_FS": "FS", "PR_SS": "SS", "PR_FF": "FF", "PR_SF": "SF"}
    return [{"change": c, "pred": (k[0], pn), "succ": (k[1], sn), "type": types.get(k[2], k[2]), "pred_project": k[3],
             "lag": d, "bl_lag": bd} for c, k, d, bd, _rid, pn, sn in rows][:20]


# ----------------------------------------------------------------- project dates

def _proj(o, col, pid=0):
    """A PROJECT column of the project (pid omitted) or of pid (None: no baseline, None)."""
    pid = o.pid if pid == 0 else pid
    return None if pid is None else o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", pid)


def _proj_cal(o):
    return cal(o, _proj(o, "clndr_id"))


def _fv(o, other, unit):
    a, b = dt(_proj(o, "scd_end_date")), dt(other)
    if not (a and b):
        return None
    if unit == "cd":
        return (a - b).total_seconds() / 86400
    c = _proj_cal(o)
    return c.hours(b, a) / c.hpd


def _sum(key):
    return lambda o: summary(o)[key]


def _lsum(key):
    return lambda o: link_summary(o)[key]


def _ev(key):
    return lambda o: earned_value(o)[key]


SLOTS = {
    "data_date": lambda o: _proj(o, "last_recalc_date"),
    "last_f9": lambda o: _proj(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "bl_used": lambda o: _proj(o, "proj_short_name", baseline_pid(o)),
    "bl_data_date": lambda o: _proj(o, "last_recalc_date", baseline_pid(o)),
    "finish": lambda o: _proj(o, "scd_end_date"),
    "bl_finish": lambda o: _proj(o, "scd_end_date", baseline_pid(o)),
    "fv_cd": lambda o: _fv(o, _proj(o, "scd_end_date", baseline_pid(o)), "cd"),
    "fv_wd": lambda o: _fv(o, _proj(o, "scd_end_date", baseline_pid(o)), "wd"),
    "must_finish": lambda o: _proj(o, "plan_end_date"),
    "mf_wd": lambda o: _fv(o, _proj(o, "plan_end_date"), "wd"),
    "bl_source": lambda o: "baseline=" if o.args.get("baseline") else Contains("project baseline", "sum_base_proj_id"),
    "mf_cd": lambda o: _fv(o, _proj(o, "plan_end_date"), "cd"),
    **{k: _sum(k) for k in ("matched", "added", "removed", "later", "earlier", "same_finish", "later_avg_cd",
                            "later_max_cd", "earlier_max_cd", "status_changed", "dur_changed", "name_changed",
                            "slip_unknown")},
    "rel_matched": _lsum("matched"),
    "rel_added": _lsum("added"),
    "rel_removed": _lsum("removed"),
    "rel_lag_changed": _lsum("lag_changed"),
    "bl_planned": _ev("baseline_planned"),
    "earned": _ev("earned"),
    "actual": _ev("actual"),
    "ev_variance": _ev("variance"),
    "spi": _ev("spi"),
    "spi_actual": _ev("spi_actual"),
    "act_error": lambda o: None,
    "rel_error": lambda o: None,
    "pc_error": lambda o: None,
}
TABLES = {
    "causes": lambda o: [{"cause": c, "activities": n} for c, n in summary(o)["causes"].items()],
    "moved": moved,
    "links": links,
}
