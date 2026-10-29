"""Oracles of update-integrity-audit: every flag of p6_update_integrity computed again from P6's TASK, TASKPRED,
PROJECT, PROJPROP and CALENDAR rows of the update (o.pid) and the previous update (argument previous), read with
SQL: activities matched by Activity ID, links by (predecessor, successor, type, predecessor project); open = not
completed, LOE and WBS summary left out; critical = open and critical under each project's own setting. The
source of a negative float is traced on the previous update's stored late dates (late gaps of 0, as the
delay-whatif oracles do)."""

from __future__ import annotations

from oracles import SUMMARY_TYPES, Contains
from oracles.delay_whatif import _late_cstr, _late_gap, _zero
from oracles.logic_date_integrity import sched_tree
from oracles.milestone_tracker import TOL_H, calendars, dt, network, text

FLAGS = ("open_end_to_finish", "negative_float_cleared_by_constraint", "must_finish_moved", "actuals_changed",
         "duration_cut", "links_removed_on_critical", "rel_type_or_lag_changed", "schedule_options_changed",
         "calendars_changed", "deleted_in_progress_or_critical", "data_date")
TF_TOL = 0.05  # hours
NEAR_D = 10.0  # near_critical_days of the call (the tool's default)
REL = {"PR_FS": "FS", "PR_SS": "SS", "PR_FF": "FF", "PR_SF": "SF"}
CSTR = {"CS_MSO": "Start On", "CS_MSOA": "Start On or After", "CS_MSOB": "Start On or Before", "CS_MEO": "Finish On",
        "CS_MEOA": "Finish On or After", "CS_MEOB": "Finish On or Before", "CS_MANDSTART": "Mandatory Start",
        "CS_MANDFIN": "Mandatory Finish", "CS_ALAP": "As Late As Possible"}

_CACHE: dict = {}


def _side(o, pid) -> dict:
    """The project's activities (by Activity ID, the lowest task_id), links, critical setting and calendars."""
    prj = o.sql("SELECT * FROM PROJECT WHERE proj_id = ?", pid)[0]
    cals = calendars(o)
    acts = {}
    for r in o.sql("SELECT t.*, COALESCE(NULLIF(c.day_hr_cnt, 0), 8) AS hpd, c.clndr_name FROM TASK t "
                   "LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id WHERE t.proj_id = ? "
                   "AND t.delete_session_id IS NULL ORDER BY t.task_id", pid):
        acts.setdefault(r["task_code"], dict(r))
    for a in acts.values():
        a["op"] = a["status_code"] != "TK_Complete" and a["task_type"] not in SUMMARY_TYPES
        tf = a["total_float_hr_cnt"]
        if prj["critical_path_type"] == "CT_DrivPath":
            a["crit"] = a["op"] and a["driving_path_flag"] == "Y"
        else:
            a["crit"] = a["op"] and tf is not None and tf <= float(prj["critical_drtn_hr_cnt"] or 0)
    links = {}
    for r in o.sql("SELECT r.task_pred_id, r.pred_type, r.lag_hr_cnt, pt.task_code AS pc, pt.task_name AS pn, "
                   "st.task_code AS sc, st.task_name AS sn, CASE WHEN pt.proj_id = ? THEN NULL ELSE pp.proj_short_name "
                   "END AS pproj, COALESCE(NULLIF(cp.day_hr_cnt, 0), 8) AS phpd FROM TASKPRED r "
                   "JOIN TASK st ON st.task_id = r.task_id JOIN TASK pt ON pt.task_id = r.pred_task_id "
                   "LEFT JOIN PROJECT pp ON pp.proj_id = pt.proj_id LEFT JOIN CALENDAR cp ON cp.clndr_id = pt.clndr_id "
                   "WHERE st.proj_id = ? AND r.delete_session_id IS NULL AND st.delete_session_id IS NULL "
                   "AND pt.delete_session_id IS NULL ORDER BY r.task_pred_id", pid, pid):
        links.setdefault((r["pc"], r["sc"], r["pred_type"], r["pproj"]), dict(r))
    return {"pid": pid, "prj": dict(prj), "acts": acts, "links": links, "cals": cals}


def _lag_d(lk) -> float:
    return round(float(lk["lag_hr_cnt"] or 0) / lk["phpd"], 2)  # the demo's lag rule: the predecessor calendar


def _sources(net, code) -> list:
    """Late date sources of an activity of net (constraints, must finish, open end, unexplained)."""
    acts, t0 = net["acts"], net["code"][code]
    must, end = dt(net["prj"]["plan_end_date"]), dt(net["prj"]["scd_end_date"])
    seen, order, out = {t0}, [t0], []
    while order:
        n = order.pop(0)
        a = acts[n]
        ctl = [lk["succ"] for lk in net["succs"].get(n, []) if abs(_late_gap(net, lk)) <= TOL_H]
        own = [("activity_constraint", a["task_code"]) for _ty, _d in _late_cstr(a)]
        out += own
        if not ctl and not own:
            if _zero(a, a["late_end_date"], must):
                out.append(("project_must_finish", None))
            elif _zero(a, a["late_end_date"], end) or _zero(a, a["late_end_date"], a["early_end_date"]):
                out.append(("open_end", None))
            else:
                out.append(("unexplained", None))
        for s in ctl:
            if s not in seen:
                seen.add(s)
                order.append(s)
    return out


def flags(o) -> dict:
    key = (o.db, o.pid, o.args["previous"])
    if key in _CACHE:
        return _CACHE[key]
    oid = o.one("SELECT proj_id FROM PROJECT WHERE proj_short_name = ?", o.args["previous"])
    A, B = _side(o, o.pid), _side(o, oid)
    a_, b_ = A["acts"], B["acts"]
    both = sorted(set(a_) & set(b_))
    summ = lambda x: x["task_type"] in SUMMARY_TYPES  # noqa: E731
    out = {f: [] for f in FLAGS}

    def ends(S):
        succ, pred = {}, {}
        for k in S["links"]:
            p, s, _t, pp = k
            if pp is None and p in S["acts"] and s in S["acts"] and not summ(S["acts"][p]) and not summ(S["acts"][s]):
                succ.setdefault(p, []).append(k)
                pred.setdefault(s, []).append(k)
        return succ, pred
    sa, pa = ends(A)
    sb, pb = ends(B)
    own = [c for c, x in a_.items() if not summ(x)]
    fin = lambda c: a_[c]["act_end_date"] or a_[c]["early_end_date"] or ""  # noqa: E731
    st = lambda c: a_[c]["act_start_date"] or a_[c]["early_start_date"] or "9999"  # noqa: E731
    fin_a = max(own, key=lambda c: (fin(c), a_[c]["task_type"] == "TT_FinMile", c))
    st_a = min(own, key=lambda c: (st(c), a_[c]["task_type"] != "TT_Mile", c))
    targets = {"successor": {c for c in own if a_[c]["task_type"] == "TT_FinMile" and c not in sa} | {fin_a},
               "predecessor": {c for c in own if a_[c]["task_type"] == "TT_Mile" and c not in pa} | {st_a}}
    for c in both:
        if summ(a_[c]):
            continue
        for side, before, now, end in (("successor", sb, sa, 1), ("predecessor", pb, pa, 0)):
            if c in before or len(now.get(c, [])) != 1 or now[c][0] in B["links"] or now[c][0][end] not in targets[side]:
                continue
            o_ = now[c][0][end]
            out["open_end_to_finish"].append({"act": (c, a_[c]["task_name"]), "side": side,
                                              "to": (o_, a_[o_]["task_name"])})
    cst = lambda x: (x["cstr_type"], x["cstr_date"], x["cstr_type2"], x["cstr_date2"])  # noqa: E731
    must_a, must_b = A["prj"]["plan_end_date"], B["prj"]["plan_end_date"]
    net_b = network(o, oid)
    for c in both:
        a, b = a_[c], b_[c]
        if not (a["op"] and b["op"]) or a["total_float_hr_cnt"] is None or b["total_float_hr_cnt"] is None:
            continue
        if not float(b["total_float_hr_cnt"]) < -TF_TOL <= float(a["total_float_hr_cnt"]):
            continue
        causes = []
        if cst(a) != cst(b):
            causes.append("its own constraint")
        for kind, src in _sources(net_b, c):
            if kind == "activity_constraint" and src != c and (src not in a_ or cst(a_[src]) != cst(b_[src])):
                causes.append(f"the constraint of {src}")
            elif kind == "project_must_finish" and must_b and (must_a is None or must_a > must_b):
                causes.append("the must finish by date")
        if causes:
            out["negative_float_cleared_by_constraint"].append({
                "act": (c, a["task_name"]), "tf0": round(float(b["total_float_hr_cnt"]) / b["hpd"], 2),
                "tf1": round(float(a["total_float_hr_cnt"]) / a["hpd"], 2), "cause": Contains(*causes)})
    if must_a != must_b:
        out["must_finish_moved"].append({"before": must_b, "after": must_a})
    for c in both:
        for col, name in (("act_start_date", "actual_start"), ("act_end_date", "actual_finish")):
            vb, va = dt(b_[c][col]), dt(a_[c][col])
            if vb is not None and (va is None or abs((va - vb).total_seconds()) > 60):
                out["actuals_changed"].append({"act": (c, a_[c]["task_name"]), "f": name, "b": text(vb), "a": text(va)})
    for c in both:
        a, b = a_[c], b_[c]
        if summ(a) or a["task_type"] in ("TT_Mile", "TT_FinMile") or a["status_code"] != "TK_NotStart" \
                or b["status_code"] != "TK_NotStart":
            continue
        if float(b["target_drtn_hr_cnt"] or 0) - float(a["target_drtn_hr_cnt"] or 0) > TF_TOL or \
                float(b["remain_drtn_hr_cnt"] or 0) - float(a["remain_drtn_hr_cnt"] or 0) > TF_TOL:
            d = lambda h, x: round(float(h) / x["hpd"], 2) if h is not None else None  # noqa: E731
            out["duration_cut"].append({"act": (c, a["task_name"]), "o0": d(b["target_drtn_hr_cnt"], b),
                                        "o1": d(a["target_drtn_hr_cnt"], a), "r0": d(b["remain_drtn_hr_cnt"], b),
                                        "r1": d(a["remain_drtn_hr_cnt"], a), "_crit": b["crit"]})
    pairs_a = {(k[0], k[1], k[3]) for k in A["links"]}
    for k in sorted(set(B["links"]) - set(A["links"]), key=lambda k: (k[1], k[0], k[2], k[3] or "")):
        p, s, _t, pp = k
        if s not in a_ or (pp is None and p not in a_) or s not in b_ or not b_[s]["op"] or (p, s, pp) in pairs_a:
            continue
        sb_ = b_[s]
        near = sb_["total_float_hr_cnt"] is not None and float(sb_["total_float_hr_cnt"]) <= NEAR_D * sb_["hpd"]
        if sb_["crit"] or near:
            lk = B["links"][k]
            out["links_removed_on_critical"].append({"p": (p, lk["pn"]), "s": (s, lk["sn"]), "t": REL[k[2]],
                                                     "tf": round(float(sb_["total_float_hr_cnt"]) / sb_["hpd"], 2)})
    by_pair = lambda S: {pk: {k[2]: S["links"][k] for k in S["links"] if (k[0], k[1], k[3]) == pk}  # noqa: E731
                         for pk in {(k[0], k[1], k[3]) for k in S["links"]}}
    pa_, pb_ = by_pair(A), by_pair(B)
    txt = lambda ts: ", ".join(f"{REL[t]} {_lag_d(ts[t]):g} d" for t in sorted(ts))  # noqa: E731
    for pk in sorted(set(pa_) & set(pb_), key=lambda x: (x[1], x[0], x[2] or "")):
        ta, tb = pa_[pk], pb_[pk]
        first = next(iter(ta.values()))
        row = {"p": (pk[0], first["pn"]), "s": (pk[1], first["sn"])}
        if set(ta) != set(tb):
            out["rel_type_or_lag_changed"].append({**row, "c": "type", "b": txt(tb), "a": txt(ta)})
        for t in sorted(set(ta) & set(tb)):
            if abs(float(ta[t]["lag_hr_cnt"] or 0) - float(tb[t]["lag_hr_cnt"] or 0)) > 0.01:
                out["rel_type_or_lag_changed"].append({**row, "c": "lag", "b": txt({t: tb[t]}), "a": txt({t: ta[t]})})
    out["schedule_options_changed"] = _options(o, o.pid, oid, A["prj"], B["prj"])
    name = lambda cid: o.one("SELECT clndr_name FROM CALENDAR WHERE clndr_id = ?", cid)  # noqa: E731
    for c in both:
        if a_[c]["op"] and a_[c]["clndr_name"] != b_[c]["clndr_name"]:
            out["calendars_changed"].append({"i": (c, a_[c]["task_name"]), "b": b_[c]["clndr_name"],
                                             "a": a_[c]["clndr_name"], "d": "the activity is on another calendar"})
    used_a, used_b = {}, {}
    for X, U, op_only in ((a_, used_a, True), (b_, used_b, False)):
        for x in sorted(X.values(), key=lambda x: x["task_id"]):
            if x["op"] or not op_only:
                U.setdefault(name(x["clndr_id"]), x["clndr_id"])
    for nm in sorted(set(used_a) & set(used_b)):
        ca, cb = A["cals"][used_a[nm]], B["cals"][used_b[nm]]
        if used_a[nm] == used_b[nm]:
            continue
        if ca.week != cb.week:
            out["calendars_changed"].append({"i": (nm, None), "b": Contains("h a week"), "a": Contains("h a week"),
                                             "d": Contains("work week changed")})
        added = sorted(d for d in ca.exc if cb.exc.get(d) != ca.exc[d])
        removed = sorted(d for d in cb.exc if d not in ca.exc)
        if added or removed:
            out["calendars_changed"].append({
                "i": (nm, None), "b": f"{len(cb.exc)} exceptions", "a": f"{len(ca.exc)} exceptions",
                "d": Contains(*([f"{len(added)} added or changed"] if added else []),
                              *([f"{len(removed)} removed"] if removed else []), *(d.isoformat() for d in added[:5]))})
    for c in sorted(set(b_) - set(a_)):
        b = b_[c]
        if not summ(b) and (b["status_code"] == "TK_Active" or b["crit"]):
            out["deleted_in_progress_or_critical"].append({
                "act": (c, b["task_name"]), "st": b["status_code"],
                "tf": None if b["total_float_hr_cnt"] is None else round(float(b["total_float_hr_cnt"]) / b["hpd"], 2),
                "c": b["crit"]})
    if not (A["prj"]["last_recalc_date"] and B["prj"]["last_recalc_date"]
            and dt(A["prj"]["last_recalc_date"]) > dt(B["prj"]["last_recalc_date"])):
        out["data_date"].append({})
    _CACHE[key] = {"A": A, "B": B, "out": out}
    return _CACHE[key]


def _options(o, pid, oid, pa, pb) -> list:
    """Options that differ, in the order p6_schedule_options compares them (different, only before, only now)."""
    ta, tb = sched_tree(o, pid), sched_tree(o, oid)
    va, vb = (ta or ({}, []))[0], (tb or ({}, []))[0]
    def same(x, y):
        try:
            return float(x) == float(y)
        except (TypeError, ValueError):
            return x == y
    ranked = []
    for k in sorted(set(va) | set(vb)):
        if k in va and k in vb:
            if not same(va[k], vb[k]):
                ranked.append((0, {"o": k, "b": vb[k], "a": va[k]}))
        else:
            ranked.append((1 if k in vb else 2, {"o": k, "b": vb.get(k), "a": va.get(k)}))
    rows = [r for _rank, r in sorted(ranked, key=lambda e: e[0])]
    for col in ("critical_path_type", "critical_drtn_hr_cnt"):
        if not same(pa[col], pb[col]):
            rows.append({"o": f"PROJECT.{col}", "b": pb[col], "a": pa[col]})
    return rows


def _out(o, flag):
    return flags(o)["out"][flag]


def _rows(flag, keys):
    return lambda o: [{k: r[k] for k in keys} for r in _out(o, flag)[:10]]


def _must_wd(o):
    f = flags(o)
    a, b = dt(f["A"]["prj"]["plan_end_date"]), dt(f["B"]["prj"]["plan_end_date"])
    cal = f["A"]["cals"].get(f["A"]["prj"]["clndr_id"])
    return round(cal.work_hours(b, a) / cal.hpd, 2) if a and b and cal is not None and not cal.error else None


def _count(flag):
    return lambda o: len(_out(o, flag))


SLOTS = {
    "data_date": lambda o: flags(o)["A"]["prj"]["last_recalc_date"],
    "last_f9": lambda o: flags(o)["A"]["prj"]["last_schedule_date"],
    "stale": lambda o: o.stale(),
    "dd_before": lambda o: flags(o)["B"]["prj"]["last_recalc_date"],
    "dd_delta": lambda o: round((dt(flags(o)["A"]["prj"]["last_recalc_date"])
                                 - dt(flags(o)["B"]["prj"]["last_recalc_date"])).total_seconds() / 86400, 2),
    "raised": lambda o: sum(1 for f in FLAGS if _out(o, f)),
    "n_open_end": _count("open_end_to_finish"),
    "n_neg": _count("negative_float_cleared_by_constraint"),
    "n_must": _count("must_finish_moved"),
    "n_act": _count("actuals_changed"),
    "n_cut": _count("duration_cut"),
    "n_cut_crit": lambda o: sum(r["_crit"] for r in _out(o, "duration_cut")),
    "n_links": _count("links_removed_on_critical"),
    "n_rel": _count("rel_type_or_lag_changed"),
    "n_opt": _count("schedule_options_changed"),
    "n_cal": _count("calendars_changed"),
    "n_del": _count("deleted_in_progress_or_critical"),
    "n_dd": _count("data_date"),
    "must_before": lambda o: flags(o)["B"]["prj"]["plan_end_date"],
    "must_after": lambda o: flags(o)["A"]["prj"]["plan_end_date"],
    "must_wd": _must_wd,
    "caveat": lambda o: Contains("question to raise", "not proof of manipulation"),
}
TABLES = {
    "summary": lambda o: [{"flag": f, "n": len(_out(o, f))} for f in FLAGS],
    "t_open_end": _rows("open_end_to_finish", ("act", "side", "to")),
    "t_neg": _rows("negative_float_cleared_by_constraint", ("act", "tf0", "tf1", "cause")),
    "t_act": _rows("actuals_changed", ("act", "f", "b", "a")),
    "t_cut": _rows("duration_cut", ("act", "o0", "o1", "r0", "r1")),
    "t_links": _rows("links_removed_on_critical", ("p", "s", "t", "tf")),
    "t_rel": _rows("rel_type_or_lag_changed", ("p", "s", "c", "b", "a")),
    "t_opt": _rows("schedule_options_changed", ("o", "b", "a")),
    "t_cal": _rows("calendars_changed", ("i", "b", "a", "d")),
    "t_del": _rows("deleted_in_progress_or_critical", ("act", "st", "tf", "c")),
}
