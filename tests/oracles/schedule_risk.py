"""Oracles of schedule-risk: the Monte Carlo run again here, independently of P6 MCP's engine, from P6's rows
read with SQL. The draws follow the rule p6_schedule_risk documents: random.Random(seed), the open activities
that are not milestones, LOE or WBS summary in task_id order, triangular(85 %, 135 %, mode 100 %) of the
remaining duration, rounded to whole minutes as P6 works. Each iteration is a forward pass written here (the
rules of the delay-whatif CPM: retained logic, lags on the lag calendar less the part elapsed since an actual
date, early start not before the data date, start or finish on or after constraints), the project finish is
the latest early finish, and the critical path is walked back from it through the links whose bound sets each
date. Values that depend on a feature this pass does not model are Unchecked with the reason."""

from __future__ import annotations

import math
import random
from datetime import timedelta

from oracles import SUMMARY_TYPES, Contains, Unchecked
from oracles.delay_whatif import EARLY_FINISH, EARLY_START, _cstr, _finish_activity, _order, _stored, limits
from oracles.logic_date_integrity import ENGINE_VERSION, engine
from oracles.milestone_tracker import anchor, days, network, text

DEFAULT = (85.0, 100.0, 135.0)
WORK = 1_500_000  # activity passes per run at most (iterations are capped below it)
MINUTE = timedelta(minutes=1)
MILESTONES = ("TT_Mile", "TT_FinMile")


def _iterations(o, recomputed: int) -> int:
    asked = min(max(int(o.args["iterations"]), 100), 5000)
    return min(asked, max(100, WORK // max(1, recomputed)))


def forward(net, order, rem) -> tuple[dict, dict]:
    """({task_id: {es, ef}}, {task_id: [predecessors whose bound sets its dates]})."""
    acts, dd = net["acts"], net["dd"]
    res, drv = {}, {}
    for n in order:
        a = acts[n]
        if a["ext"]:
            res[n] = _stored(a)
            continue
        done = a["status_code"] == "TK_Complete"
        cal, starts, finishes = a["cal"], [(dd, None)], []
        for lk in net["preds"].get(n, []):
            pr = res[lk["pred"]]
            base = pr["es"] if lk["type"] in ("SS", "SF") else pr["ef"]
            if base is None:
                continue
            p_done = acts[lk["pred"]]["status_code"] == "TK_Complete"
            anc = base if done and p_done else anchor(net, lk, base)
            (starts if lk["type"] in ("FS", "SS") else finishes).append((anc, lk["pred"]))
        starts += [(d, None) for d in _cstr(a, EARLY_START)]
        finishes += [(d, None) for d in _cstr(a, EARLY_FINISH)]
        if done or a["task_type"] == "TT_FinMile":
            ef = max(x for x, _p in starts + finishes)
            res[n] = {"es": ef, "ef": ef}
            drv[n] = [p for x, p in starts + finishes if p is not None and abs(x - ef) <= MINUTE]
            continue
        es = cal.next_start(max(x for x, _p in starts))
        tie = [p for x, p in starts if p is not None and (abs(x - es) <= MINUTE or cal.next_start(x) == es)]
        for f, p in finishes:
            e2 = cal.next_start(cal.sub(f, rem[n]))
            if e2 > es:
                es, tie = e2, [p] if p is not None else []
            elif e2 == es and finishes and tie and p is not None and p not in tie:
                pass  # a start already sets it
        ef = es if a["task_type"] == "TT_Mile" else cal.add(es, rem[n])
        res[n] = {"es": es, "ef": ef}
        drv[n] = tie
    return res, drv


_CACHE: dict = {}


def run(o) -> dict:
    """The whole simulation, once per (database, project, iterations, seed)."""
    key = (o.db, o.pid, o.args["iterations"], o.args["seed"])
    if key in _CACHE:
        return _CACHE[key]
    net = network(o)
    acts = net["acts"]
    own = {n: a for n, a in acts.items() if not a["ext"]}
    why = limits(net)
    order = _order(net)
    stored = {n: 0.0 if a["status_code"] == "TK_Complete" or a["task_type"] in MILESTONES
              else float(a["remain_drtn_hr_cnt"] or 0) for n, a in own.items()}
    drawn = [n for n in sorted(own) if own[n]["status_code"] != "TK_Complete"
             and own[n]["task_type"] not in SUMMARY_TYPES + MILESTONES]
    dist = {n: tuple(stored[n] * x / 100 for x in DEFAULT) for n in drawn}  # (min, mode, max) hours
    affected, stack = set(drawn), list(drawn)
    while stack:
        for lk in net["succs"].get(stack.pop(), []):
            if lk["succ"] not in affected and not acts[lk["succ"]]["ext"]:
                affected.add(lk["succ"])
                stack.append(lk["succ"])
    n_iter = _iterations(o, len(affected))
    tasks = [n for n in own if own[n]["task_type"] not in SUMMARY_TYPES]
    counted = {n for n in tasks if own[n]["status_code"] != "TK_Complete"}

    def path(res, drv, end):
        stack = [n for n in tasks if res[n]["ef"] >= end - MINUTE]
        seen = set(stack)
        while stack:
            for q in drv.get(stack.pop(), []):
                if q not in seen and acts[q]["status_code"] != "TK_Complete":
                    seen.add(q)
                    stack.append(q)
        return seen & counted
    base, base_drv = forward(net, order, stored)
    det_end = max(base[n]["ef"] for n in tasks)
    det_path = path(base, base_drv, det_end)
    rng = random.Random(int(o.args["seed"]))
    ends, crit, fin_act = [], {}, _finish_activity(net, base)
    ms = [fin_act] if fin_act is not None else []
    ms += sorted((n for n, a in own.items() if a["cstr_type"] and a["status_code"] != "TK_Complete"
                  and n not in ms), key=lambda n: own[n]["task_code"])
    ms_ef = {m: [] for m in ms}
    for _ in range(n_iter):
        rem = dict(stored)
        for n in drawn:
            lo, mo, hi = dist[n]
            rem[n] = round(rng.triangular(lo, hi, mo) * 60) / 60  # whole minutes
        res, drv = forward(net, order, rem)
        end = max(res[n]["ef"] for n in tasks)
        ends.append(end)
        for n in path(res, drv, end):
            crit[n] = crit.get(n, 0) + 1
        for m in ms:
            ms_ef[m].append(res[m]["ef"])
    ends.sort()
    _CACHE[key] = {"net": net, "own": own, "why": why, "n_iter": n_iter, "dist": dist, "drawn": drawn,
                   "base": base, "det_end": det_end, "det_path": det_path, "ends": ends, "crit": crit,
                   "ms": ms, "ms_ef": ms_ef, "fin_act": fin_act}
    return _CACHE[key]


def checked(fn):
    def wrapped(o):
        why = run(o)["why"] + engine(o)["why"]
        return Unchecked("schedule-risk simulation: " + "; ".join(why)) if why else fn(o)
    return wrapped


def pctl(vals, p):
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def _pct(k, n):
    return round(100 * k / n, 2)


def _wd(cal, a, b):
    return None if cal is None or cal.error else round(cal.work_hours(a, b) / cal.hpd, 2)


def milestones(o):
    r = run(o)
    rows = []
    for m in r["ms"][:10]:
        a, fins = r["own"][m], sorted(r["ms_ef"][m])
        det = r["base"][m]["ef"]
        cdate = a["cstr_date"] if a["cstr_type"] else None
        rows.append({"activity": (a["task_code"], a["task_name"]), "det": text(det), "p50": text(pctl(fins, 50)),
                     "p80": text(pctl(fins, 80)), "p90": text(pctl(fins, 90)),
                     "on_time": _pct(sum(x <= det + MINUTE for x in fins), len(fins)), "cdate": text(cdate),
                     "by_cstr": None if cdate is None else Unchecked("constraint dates: none in the demo"),
                     "buffer": _wd(a["cal"], det, pctl(fins, 80))})
    return rows


def drivers(o):
    r = run(o)
    rows = []
    for n, k in sorted(r["crit"].items(), key=lambda e: (-e[1], r["own"][e[0]]["task_code"], e[0]))[:15]:
        a = r["own"][n]
        lo, _mo, hi = r["dist"].get(n, (None, None, None))
        rows.append({"activity": (a["task_code"], a["task_name"]), "crit": _pct(k, r["n_iter"]),
                     "det": n in r["det_path"], "tf": days(a["total_float_hr_cnt"], a),
                     "rem": days(a["remain_drtn_hr_cnt"], a), "min": None if lo is None else days(lo, a),
                     "max": None if hi is None else days(hi, a)})
    return rows


def weeks(o):
    r = run(o)
    first = int(o.one("SELECT week_start_day_num FROM PREFER") or 1)  # 1 = Sunday
    start = lambda d: d - timedelta(days=(d.weekday() - (first + 5) % 7) % 7)  # noqa: E731
    w, last, rows, cum = start(r["ends"][0].date()), start(r["ends"][-1].date()), [], 0
    while w <= last:
        k = sum(1 for e in r["ends"] if w <= e.date() < w + timedelta(days=7))
        cum += k
        rows.append({"from": w.isoformat(), "to": (w + timedelta(days=6)).isoformat(), "n": k,
                     "pct": _pct(k, r["n_iter"]), "cum": _pct(cum, r["n_iter"])})
        w += timedelta(days=7)
    return rows[:20]


def _prj(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _must(o, fn):
    must = _prj(o, "plan_end_date")
    return None if must is None else fn(must)


SLOTS = {
    "data_date": lambda o: _prj(o, "last_recalc_date"),
    "last_f9": lambda o: _prj(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "match_rate": checked(lambda o: round(1 - engine(o)["bad_open"] / engine(o)["open"], 4)),
    "trusted": checked(lambda o: engine(o)["bad_open"] / engine(o)["open"] <= 0.01),
    "det_finish": checked(lambda o: text(run(o)["det_end"])),
    "det_activity": lambda o: (run(o)["own"][run(o)["fin_act"]]["task_code"], run(o)["own"][run(o)["fin_act"]]["task_name"]),
    "stored_finish": lambda o: _prj(o, "scd_end_date"),
    "p10": checked(lambda o: text(pctl(run(o)["ends"], 10))),
    "p50": checked(lambda o: text(pctl(run(o)["ends"], 50))),
    "p80": checked(lambda o: text(pctl(run(o)["ends"], 80))),
    "p90": checked(lambda o: text(pctl(run(o)["ends"], 90))),
    "must_finish": lambda o: _prj(o, "plan_end_date"),
    "on_time_det": checked(lambda o: _pct(sum(e <= run(o)["det_end"] + MINUTE for e in run(o)["ends"]), run(o)["n_iter"])),
    "on_time_must": checked(lambda o: _must(o, lambda m: _pct(sum(text(e) <= m for e in run(o)["ends"]), run(o)["n_iter"]))),
    "p80_buffer": checked(lambda o: _wd(run(o)["net"]["pcal"], run(o)["det_end"], pctl(run(o)["ends"], 80))),
    "iterations_run": lambda o: run(o)["n_iter"],
    "iterations_note": lambda o: None if run(o)["n_iter"] == int(o.args["iterations"]) else Contains("iterations"),
    "seed_used": lambda o: int(o.args["seed"]),
    "engine_version": lambda o: ENGINE_VERSION,
    "d_min": lambda o: DEFAULT[0],
    "d_mode": lambda o: DEFAULT[1],
    "d_max": lambda o: DEFAULT[2],
    "n_drawn": lambda o: len(run(o)["drawn"]),
    "caveat": lambda o: Contains("not a forecast", "no correlation between activities", "last F9"),
}
TABLES = {"milestones": checked(milestones), "drivers": checked(drivers), "weeks": checked(weeks)}
