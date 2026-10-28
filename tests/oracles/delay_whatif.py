"""Oracles of delay-whatif: P6's TASK, TASKPRED, PROJECT, PROJPROP and CALENDAR rows read with SQL. The
activity and its float origin come from the stored F9 values (late gaps traced here); the what-if comes
from a small CPM written here (forward and backward pass on the calendars parsed by the milestone-tracker
oracles, retained logic: every activity placed, completed ones too). The CPM must give back the stored F9
of every open activity of the project; when it does not, or when the project uses a feature it does not
model, every value that depends on the what-if is Unchecked with the reason."""

from __future__ import annotations

from oracles import SUMMARY_TYPES, Contains, Unchecked
from oracles.milestone_tracker import (
    START_CSTR,
    TOL_H,
    anchor,
    days,
    driving_path,
    dt,
    network,
    text,
)

TF_TOL_H = 0.05  # total float equal within 3 minutes
EARLY_START = ("CS_MSO", "CS_MSOA")  # early start on or after the date
EARLY_FINISH = ("CS_MEO", "CS_MEOA")
LATE_START = ("CS_MSO", "CS_MSOB")  # late start on or before the date
LATE_FINISH = ("CS_MEO", "CS_MEOB")
LATE_CSTR = LATE_START + LATE_FINISH + ("CS_MANDSTART", "CS_MANDFIN")
NOT_MODELLED = ("CS_MANDSTART", "CS_MANDFIN", "CS_ALAP")


def _delay(o) -> float:
    return float(o.args["delay_days"])


# ----------------------------------------------------------------- CPM

def limits(net) -> list[str]:
    """Features of the project this CPM does not model (the what-if values are then Unchecked)."""
    own = [a for a in net["acts"].values() if not a["ext"]]
    opn = [a for a in own if a["status_code"] != "TK_Complete"]
    opt, out = net["opt"], []
    if any(a["task_type"] in SUMMARY_TYPES for a in own):
        out.append("LOE or WBS summary activities (spans not modelled)")
    if any(t in NOT_MODELLED for a in opn for t in (a["cstr_type"], a.get("cstr_type2"))):
        out.append("mandatory or as late as possible constraints")
    if opt.get("sched_use_expect_end_flag") != "N" and any(a["expect_end_date"] for a in opn):
        out.append("expected finish dates in use")
    if opt.get("sched_float_type", "FT_FF") != "FT_FF":
        out.append("total float other than finish float (sched_float_type)")
    if opt.get("sched_retained_logic") == "N" or opt.get("sched_progress_override") == "Y":
        out.append("progress override instead of retained logic")
    if any(a["cal"].error for a in own):
        out.append("an unreadable calendar")
    if any(a["ext"] for a in net["acts"].values()):
        out.append("links to other projects")
    return out


def _order(net) -> list:
    """Activities in an order where every predecessor comes first."""
    seen, out = set(), []
    for n0 in sorted(net["acts"]):
        if n0 in seen:
            continue
        seen.add(n0)
        stack = [(n0, iter(net["preds"].get(n0, [])))]
        while stack:
            m, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                stack.pop()
                out.append(m)
            elif nxt["pred"] not in seen:
                seen.add(nxt["pred"])
                stack.append((nxt["pred"], iter(net["preds"].get(nxt["pred"], []))))
    return out


def _cstr(a, kinds):
    return [d for ty, d in ((a["cstr_type"], a["cstr_date"]), (a.get("cstr_type2"), a.get("cstr_date2")))
            if ty in kinds and d is not None]


def cpm(net, extra_h: dict | None = None) -> dict:
    """{task_id: {es, ef, ls, lf, tf}} of every activity (tf None when completed). Retained logic: every
    activity is placed, a completed one at the latest of the data date and its predecessors' bounds
    (lag ignored between two completed activities); lags on the lag calendar, the lag elapsed since an
    actual date dropped; early start not before the data date; start or finish on or after constraints
    bound the early dates, on or before ones the late dates; open ends at the must finish date; total float
    = late finish - early finish. Activities of other projects keep their stored dates."""
    acts, dd, extra_h = net["acts"], net["dd"], extra_h or {}
    order = _order(net)
    done = {n: a["status_code"] == "TK_Complete" for n, a in acts.items()}
    rem = {n: 0.0 if done[n] else float(a["remain_drtn_hr_cnt"] or 0) + extra_h.get(n, 0) for n, a in acts.items()}
    res = {}
    for n in order:
        a = acts[n]
        if a["ext"]:
            res[n] = _stored(a)
            continue
        cal, starts, finishes = a["cal"], [dd], []
        for lk in net["preds"].get(n, []):
            pr = res[lk["pred"]]
            base = pr["es"] if lk["type"] in ("SS", "SF") else pr["ef"]
            if base is None:
                continue
            anc = base if done[n] and done[lk["pred"]] else anchor(net, lk, base)
            (starts if lk["type"] in ("FS", "SS") else finishes).append(anc)
        starts += _cstr(a, EARLY_START)
        finishes += _cstr(a, EARLY_FINISH)
        if done[n] or a["task_type"] == "TT_FinMile":
            ef = max(starts + finishes)
            res[n] = {"es": ef, "ef": ef}
            continue
        es = cal.next_start(max(starts))
        for f in finishes:
            es = max(es, cal.next_start(cal.sub(f, rem[n])))
        res[n] = {"es": es, "ef": es if a["task_type"] == "TT_Mile" else cal.add(es, rem[n])}
    own = [n for n in res if not acts[n]["ext"]]
    use_must = net["opt"].get("sched_use_project_end_date_for_float") != "N"
    end = (use_must and dt(net["prj"]["plan_end_date"])) or max(res[n]["ef"] for n in own)
    for n in reversed(order):
        a = acts[n]
        if a["ext"]:
            continue
        cal, bounds = a["cal"], []
        for lk in net["succs"].get(n, []):
            sr = res[lk["succ"]]
            date = sr["ls"] if lk["type"] in ("FS", "SS") else sr["lf"]
            if date is None:
                continue
            b = date if done[n] and done[lk["succ"]] else anchor(net, lk, date, late=True)
            bounds.append(b if lk["type"] in ("FS", "FF") else cal.add(b, rem[n]))
        bounds += [cal.add(d, rem[n]) for d in _cstr(a, LATE_START)] + _cstr(a, LATE_FINISH)
        lf = cal.prev_end(min(bounds) if bounds else end)
        flat = done[n] or a["task_type"] in ("TT_FinMile", "TT_Mile")
        res[n].update(ls=lf if flat else cal.sub(lf, rem[n]), lf=lf,
                      tf=None if done[n] else cal.work_hours(res[n]["ef"], lf))
    return res


def _stored(a) -> dict:
    return {"es": a["early_start_date"], "ef": a["early_end_date"], "ls": a["late_start_date"],
            "lf": a["late_end_date"], "tf": None if a["total_float_hr_cnt"] is None else float(a["total_float_hr_cnt"])}


def _open(net):
    return [n for n, a in net["acts"].items() if not a["ext"] and a["status_code"] != "TK_Complete"]


def _mismatched(net, r0) -> int:
    """Open activities whose CPM values differ from the stored F9 (dates within a minute, float 3 minutes)."""
    bad = 0
    for n in _open(net):
        r, s = r0[n], _stored(net["acts"][n])
        if any(s[k] is None or abs((r[k] - s[k]).total_seconds()) > 60 for k in ("es", "ef", "ls", "lf")) or \
                s["tf"] is None or abs(r["tf"] - s["tf"]) > TF_TOL_H:
            bad += 1
    return bad


_CACHE: dict = {}


def whatif(o) -> dict:
    """{net, before (stored), r0 (CPM unchanged), after (CPM with the delay), why (reasons the CPM values
    cannot be checked: empty when it reproduces the stored F9)}, computed once per oracle run."""
    key = (o.db, o.pid, o.args["task_code"], o.args["delay_days"])
    if key not in _CACHE:
        net = network(o)
        n = net["code"][o.args["task_code"]]
        why = limits(net)
        r0 = after = {}
        try:
            r0 = cpm(net)
            after = cpm(net, {n: _delay(o) * net["acts"][n]["cal"].hpd})
            bad = _mismatched(net, r0)
            if bad:
                why.append(f"the oracle CPM does not reproduce the stored F9 ({bad} open activities differ)")
        except ValueError as e:
            why.append(f"the oracle CPM failed: {e}")
        _CACHE[key] = {"net": net, "r0": r0, "after": after, "why": why,
                       "before": {m: _stored(a) for m, a in net["acts"].items()}}
    return _CACHE[key]


def checked(fn):
    """fn(o) when the oracle CPM reproduces the project's F9, else Unchecked with the reasons."""
    def wrapped(o):
        why = whatif(o)["why"]
        return Unchecked("delay-whatif what-if: " + "; ".join(why)) if why else fn(o)
    return wrapped


def _own(net, res):
    return [n for n in res if not net["acts"][n]["ext"] and net["acts"][n]["task_type"] not in SUMMARY_TYPES]


def _finish_activity(net, res):
    """The finish activity: an open activity without successor in the project (else any), latest early
    finish, a finish milestone first, then the highest Activity ID."""
    acts = net["acts"]
    own = _own(net, res)
    ends = [n for n in own if acts[n]["status_code"] != "TK_Complete"
            and not any(not acts[lk["succ"]]["ext"] for lk in net["succs"].get(n, []))] or own
    return max(ends, key=lambda n: (res[n]["ef"], acts[n]["task_type"] == "TT_FinMile", acts[n]["task_code"]))


def _finish(o):
    w = whatif(o)
    net = w["net"]
    fa = _finish_activity(net, w["after"])
    before = dt(net["prj"]["scd_end_date"])
    after = max(w["after"][n]["ef"] for n in _own(net, w["after"]))
    cal = net["acts"][fa]["cal"]
    return {"before": before, "after": after, "cd": (after - before).total_seconds() / 86400,
            "wd": cal.work_hours(before, after) / cal.hpd}


def _float_change(o) -> dict:
    w = whatif(o)
    net, before, after = w["net"], w["before"], w["after"]
    lim = float(net["prj"]["critical_drtn_hr_cnt"] or 0) if net["prj"]["critical_path_type"] != "CT_DrivPath" else 0.0
    crit = lambda tf: tf is not None and tf <= lim + TF_TOL_H
    neg = lambda tf: tf is not None and tf < -TF_TOL_H
    opn = [n for n in _open(net) if net["acts"][n]["task_type"] not in SUMMARY_TYPES]
    acts = net["acts"]
    became = sorted((n for n in opn if crit(after[n]["tf"]) and not crit(before[n]["tf"])),
                    key=lambda n: (round(after[n]["tf"] / acts[n]["cal"].hpd, 2), acts[n]["task_code"]))
    return {"critical_before": sum(crit(before[n]["tf"]) for n in opn),
            "critical_after": sum(crit(after[n]["tf"]) for n in opn),
            "negative_before": sum(neg(before[n]["tf"]) for n in opn),
            "negative_after": sum(neg(after[n]["tf"]) for n in opn),
            "became": became, "no_longer": sum(crit(before[n]["tf"]) and not crit(after[n]["tf"]) for n in opn)}


def _before_counts(o) -> dict:
    """Critical and negative float open activities of the stored F9 (no CPM needed)."""
    w = whatif(o)
    net, before = w["net"], w["before"]
    lim = float(net["prj"]["critical_drtn_hr_cnt"] or 0) if net["prj"]["critical_path_type"] != "CT_DrivPath" else 0.0
    opn = [n for n in _open(net) if net["acts"][n]["task_type"] not in SUMMARY_TYPES]
    tfs = [before[n]["tf"] for n in opn if before[n]["tf"] is not None]
    return {"critical": sum(tf <= lim + TF_TOL_H for tf in tfs), "negative": sum(tf < -TF_TOL_H for tf in tfs)}


def became_critical(o):
    w = whatif(o)
    acts = w["net"]["acts"]
    return [{"activity": (acts[n]["task_code"], acts[n]["task_name"]),
             "tf_before": days(w["before"][n]["tf"], acts[n]), "tf_after": days(w["after"][n]["tf"], acts[n])}
            for n in _float_change(o)["became"]][:15]


def _changed(o) -> list:
    """Activities of the project whose early dates (a minute) or total float (3 minutes) move."""
    w = whatif(o)
    acts, before, after = w["net"]["acts"], w["before"], w["after"]
    out = []
    for n, a in after.items():
        if acts[n]["ext"]:
            continue
        b = before[n]
        moved = any(b[k] is None or abs((a[k] - b[k]).total_seconds()) > 60 for k in ("es", "ef"))
        tfm = (b["tf"] is None) != (a["tf"] is None) or (b["tf"] is not None and abs(a["tf"] - b["tf"]) > TF_TOL_H)
        if moved or tfm:
            d = acts[n]
            delta = None if b["ef"] is None else round((a["ef"] - b["ef"]).total_seconds() / 86400, 2)
            out.append({"activity": (d["task_code"], d["task_name"]), "ef_before": text(b["ef"]),
                        "ef_after": text(a["ef"]), "delta_cd": delta,
                        "tf_before": days(b["tf"], d), "tf_after": days(a["tf"], d)})
    out.sort(key=lambda r: (-abs(r["delta_cd"] or 0), r["activity"][0]))
    return out


def changed(o):
    return _changed(o)[:15]


def ms_table(o):
    """The finish activity before and after, then every open constrained activity (by Activity ID)."""
    w = whatif(o)
    net, before, after = w["net"], w["before"], w["after"]
    acts = net["acts"]
    cstr = sorted((n for n in _own(net, after) if acts[n]["cstr_type"] and acts[n]["status_code"] != "TK_Complete"),
                  key=lambda n: acts[n]["task_code"])
    keys = list(dict.fromkeys([_finish_activity(net, w["r0"]), _finish_activity(net, after)] + cstr))
    return [{"activity": (acts[n]["task_code"], acts[n]["task_name"]), "before": text(before[n]["ef"]),
             "after": text(after[n]["ef"]), "delta_cd": (after[n]["ef"] - before[n]["ef"]).total_seconds() / 86400,
             "tf_before": days(before[n]["tf"], acts[n]), "tf_after": days(after[n]["tf"], acts[n])} for n in keys]


# ----------------------------------------------------------------- float origin (late gaps on the stored F9)

def _late_gap(net, lk) -> float:
    p, s = net["acts"][lk["pred"]], net["acts"][lk["succ"]]
    a = p["late_start_date"] if lk["type"] in ("SS", "SF") else p["late_end_date"]
    b = s["late_start_date"] if lk["type"] in ("FS", "SS") else s["late_end_date"]
    if a is None or b is None:
        return float("inf")
    return p["cal"].work_hours(anchor(net, lk, a), b)


def _zero(a, x, y) -> bool:
    return x is not None and y is not None and abs(a["cal"].work_hours(x, y)) <= TOL_H


def _late_cstr(a) -> list:
    """Late date constraints of a binding on its late dates: [(type, date)]."""
    out = []
    for ty, d in ((a["cstr_type"], a["cstr_date"]), (a.get("cstr_type2"), a.get("cstr_date2"))):
        if ty in LATE_CSTR and d is not None:
            own = a["late_start_date"] if ty in START_CSTR + ("CS_MSOB",) else a["late_end_date"]
            if _zero(a, d, own):
                out.append((ty, d))
    return out


def float_origin(o) -> dict:
    """Walks forward along the successor links whose late gap is 0 from the activity; a binding late
    constraint on the chain is a source, and an activity without controlling successor ends at the project
    must finish date, the project finish (open end) or an unexplained date."""
    net = network(o)
    acts, t0 = net["acts"], net["code"][o.args["task_code"]]
    must, end = dt(net["prj"]["plan_end_date"]), dt(net["prj"]["scd_end_date"])
    level, order, sources, i = {t0: 0}, [t0], [], 0
    while i < len(order):
        n = order[i]
        i += 1
        a = acts[n]
        ctl = [lk["succ"] for lk in net["succs"].get(n, []) if abs(_late_gap(net, lk)) <= TOL_H]
        own = [{"type": "activity_constraint", "activity": (a["task_code"], a["task_name"]), "date": text(d)}
               for _ty, d in _late_cstr(a)]
        sources += own
        if not ctl and not own:
            if _zero(a, a["late_end_date"], must):
                kind, date = "project_must_finish", net["prj"]["plan_end_date"]
            elif _zero(a, a["late_end_date"], end) or _zero(a, a["late_end_date"], a["early_end_date"]):
                kind, date = "open_end", text(a["late_end_date"])
            else:
                kind, date = "unexplained", text(a["late_end_date"])
            sources.append({"type": kind, "activity": (a["task_code"], a["task_name"]), "date": date})
        for s in ctl:
            if s not in level:
                level[s] = level[n] + 1
                order.append(s)
    kinds = sorted({s["type"] for s in sources})
    one = sources[0] if len(sources) == 1 else {"activity": (None, None), "date": None}
    return {"type": kinds[0] if len(kinds) == 1 else "mixed" if kinds else "none",
            "activity": one["activity"], "date": one["date"]}


# ----------------------------------------------------------------- slots

def _act(o):
    net = network(o)
    return net["acts"][net["code"][o.args["task_code"]]]


def _prj(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _edit(o):
    a = _act(o)
    rem, add = days(a["remain_drtn_hr_cnt"], a), _delay(o)
    return Contains(a["task_code"], f"remaining {rem:g} d", f"+{add:g} d", f"= {rem + add:g} d")


def _explanation(o):
    a, f = _act(o), float_origin(o)
    tf = days(a["total_float_hr_cnt"], a)
    return Contains(f"Total float {round(tf, 2) + 0.0} d of {a['task_code']}", *([str(f["date"])] if f["date"] else []))


def _fo_error(o):
    """p6_float_origin refuses a completed activity or one without late dates (null: it worked)."""
    a = _act(o)
    return Contains(a["task_code"], "completed") if a["status_code"] == "TK_Complete" or a["late_end_date"] is None \
        else None


def _crit_definition(o):
    return Contains(f"total float <= {float(_prj(o, 'critical_drtn_hr_cnt') or 0):g} h")


def drivers(o):
    keep = ("level", "activity", "es", "ef", "tf", "succ", "link", "lag")
    return [{k: r[k] for k in keep} for r in driving_path(o, o.args["task_code"])[0][:15]]


def roots(o):
    return driving_path(o, o.args["task_code"])[1]


SLOTS = {
    "data_date": lambda o: _prj(o, "last_recalc_date"),
    "last_f9": lambda o: _prj(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "act_name": lambda o: _act(o)["task_name"],
    "act_status": lambda o: _act(o)["status_code"],
    "act_wbs": lambda o: o.one("SELECT wbs_name FROM PROJWBS WHERE wbs_id = ?", _act(o)["wbs_id"]),
    "act_calendar": lambda o: o.one("SELECT clndr_name FROM CALENDAR WHERE clndr_id = ?", _act(o)["clndr_id"]),
    "act_actual_start": lambda o: text(_act(o)["act_start_date"]),
    "act_es": lambda o: text(_act(o)["early_start_date"]),
    "act_ef": lambda o: text(_act(o)["early_end_date"]),
    "act_lf": lambda o: text(_act(o)["late_end_date"]),
    "act_orig_d": lambda o: days(_act(o)["target_drtn_hr_cnt"], _act(o)),
    "act_rem_d": lambda o: days(_act(o)["remain_drtn_hr_cnt"], _act(o)),
    "act_pct": lambda o: _act(o)["phys_complete_pct"],
    "act_tf": lambda o: days(_act(o)["total_float_hr_cnt"], _act(o)),
    "act_ff": lambda o: days(_act(o)["free_float_hr_cnt"], _act(o)),
    "act_longest": lambda o: _act(o)["driving_path_flag"],
    "fo_error": _fo_error,
    "origin_type": lambda o: float_origin(o)["type"],
    "origin_activity": lambda o: float_origin(o)["activity"],
    "origin_date": lambda o: float_origin(o)["date"],
    "explanation": _explanation,
    "edit_applied": _edit,
    "finish_before": lambda o: _prj(o, "scd_end_date"),
    "finish_after": checked(lambda o: text(_finish(o)["after"])),
    "finish_delta_cd": checked(lambda o: _finish(o)["cd"]),
    "finish_delta_wd": checked(lambda o: _finish(o)["wd"]),
    "fc_definition": _crit_definition,
    "critical_before": lambda o: _before_counts(o)["critical"],
    "critical_after": checked(lambda o: _float_change(o)["critical_after"]),
    "negative_before": lambda o: _before_counts(o)["negative"],
    "negative_after": checked(lambda o: _float_change(o)["negative_after"]),
    "became_critical": checked(lambda o: len(_float_change(o)["became"])),
    "no_longer_critical": checked(lambda o: _float_change(o)["no_longer"]),
    "changed_total": checked(lambda o: len(_changed(o))),
    "engine_trusted": checked(lambda o: True),
    "engine_mismatched": checked(lambda o: 0),
}
TABLES = {"drivers": drivers, "roots": roots, "became": became_critical, "milestones": ms_table, "changed": changed}
