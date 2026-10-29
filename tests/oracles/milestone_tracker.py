"""Oracles of milestone-tracker: P6's TASK rows of the project and of its baseline read with SQL, the calendar
of each milestone parsed from CALENDAR.clndr_data here, working time counted here, and the driving
predecessors traced again here from the stored early dates and TASKPRED (gap = working time from the
predecessor's date plus lag to the successor's date). The calendar and network helpers are shared with
the delay-whatif oracles."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from oracles import Contains

TOL_H = 5 / 60  # a gap within 5 minutes of working time counts as 0
MILESTONES = ("TT_Mile", "TT_FinMile")
SERIAL0 = date(1899, 12, 30)


# ----------------------------------------------------------------- dates and calendars

def dt(v):
    return None if v in (None, "") else datetime.fromisoformat(str(v).replace("T", " "))


def text(v):
    """A date as the database stores it (YYYY-MM-DD HH:MM:SS), None kept."""
    return None if v is None else v.strftime("%Y-%m-%d %H:%M:%S")


def _tree(text: str):
    """P6 text tree (0||name(attrs)(children)), white space allowed between nodes -> (name, [attr tokens],
    [children]); ValueError when the text is not such a tree."""
    pos, n = 0, len(text)

    def skip():
        nonlocal pos
        while pos < n and text[pos] in " \t\r\n":
            pos += 1

    def expect(ch):
        nonlocal pos
        skip()
        if pos >= n or text[pos] != ch:
            raise ValueError(f"calendar text: {ch!r} expected at {pos}")
        pos += 1

    def node():
        nonlocal pos
        expect("(")
        j = text.find("||", pos)
        k = text.find("(", j + 2)
        e = text.find(")", k + 1)
        if j < 0 or k < 0 or e < 0:
            raise ValueError(f"calendar text: node expected at {pos}")
        name, raw, pos = text[j + 2:k].strip(), text[k + 1:e], e + 1
        attrs = [a.strip() for a in raw.split("|")] if raw.strip() else []
        expect("(")
        kids = []
        skip()
        while pos < n and text[pos] == "(":
            kids.append(node())
            skip()
        expect(")")
        expect(")")
        return name, attrs, kids
    return node()


def _minutes(hhmm: str, finish: bool) -> int:
    h, m = (int(x) for x in hhmm.strip().split(":")[:2])
    v = h * 60 + m
    return 1440 if finish and v == 0 else v  # f|00:00 = the next midnight


def _shifts(kids) -> list:
    out = []
    for _n, attrs, _k in kids:
        kv = dict(zip(attrs[::2], attrs[1::2], strict=False))  # s and f in either order
        out.append((_minutes(kv["s"], False), _minutes(kv["f"], True)))
    return sorted(out)


def _parse(data):
    """(week {python weekday: shifts} or None without a DaysOfWeek node, exceptions {date: shifts})."""
    if isinstance(data, bytes):
        data = data.decode("utf-8", "replace")
    week, exc = None, {}
    for name, _a, kids in _tree(data or "")[2]:
        if name == "DaysOfWeek":
            week = {(int(day) + 5) % 7: _shifts(shifts) for day, _x, shifts in kids}
        elif name == "Exceptions":
            for _n, attrs, shifts in kids:
                kv = dict(zip(attrs[::2], attrs[1::2], strict=False))
                exc[SERIAL0 + timedelta(days=int(float(kv["d"])))] = _shifts(shifts)
    return week, exc


MAX_DAYS = 36600  # a search through 100 years of a calendar without working time stops


class Cal:
    """Working time of one P6 calendar: DaysOfWeek (day '1' = Sunday) and Exceptions (d|serial from
    1899-12-30; no shift = non-work day, shifts = that day's hours). error: why it is unreadable (then it
    has no working time)."""

    def __init__(self, week, exc, hpd, error=None):
        self.week, self.exc, self.error = week or {}, exc or {}, error
        self.hpd = float(hpd or 8) or 8.0

    def day(self, d: date) -> list:
        base = datetime(d.year, d.month, d.day)
        sh = self.exc[d] if d in self.exc else self.week.get(d.weekday(), [])
        return [(base + timedelta(minutes=s), base + timedelta(minutes=f)) for s, f in sh]

    @staticmethod
    def _days(d: date, step: int):
        for _ in range(MAX_DAYS):
            yield d
            d += timedelta(days=step)
        raise ValueError("calendar without working time")

    def work_hours(self, a: datetime, b: datetime) -> float:
        if b < a:
            return -self.work_hours(b, a)
        total, d = 0.0, a.date()
        while d <= b.date():
            for s, f in self.day(d):
                lo, hi = max(s, a), min(f, b)
                if hi > lo:
                    total += (hi - lo).total_seconds() / 3600
            d += timedelta(days=1)
        return total

    def add(self, t: datetime, h: float) -> datetime:
        """t plus h working hours (a finish lands on a shift end; negative h: sub)."""
        if h <= 0:
            return t if h == 0 else self.sub(t, -h)
        for d in self._days(t.date(), 1):
            for s, f in self.day(d):
                if f <= t:
                    continue
                lo = max(s, t)
                avail = (f - lo).total_seconds() / 3600
                if avail >= h - 1e-9:
                    return lo + timedelta(hours=h)
                h -= avail
        raise ValueError("calendar without working time")

    def sub(self, t: datetime, h: float) -> datetime:
        """t minus h working hours (backward: lands on a shift start)."""
        if h <= 0:
            return t if h == 0 else self.add(t, -h)
        for d in self._days(t.date(), -1):
            for s, f in reversed(self.day(d)):
                if s >= t:
                    continue
                hi = min(f, t)
                avail = (hi - s).total_seconds() / 3600
                if avail >= h - 1e-9:
                    return hi - timedelta(hours=h)
                h -= avail
        raise ValueError("calendar without working time")

    def next_start(self, t: datetime) -> datetime:
        for d in self._days(t.date(), 1):
            for s, f in self.day(d):
                if f > t:
                    return max(s, t)
        raise ValueError("calendar without working time")

    def prev_end(self, t: datetime) -> datetime:
        for d in self._days(t.date(), -1):
            for s, f in reversed(self.day(d)):
                if s < t:
                    return min(f, t)
        raise ValueError("calendar without working time")


def low(row) -> dict:
    """A row as a dict with lower case keys (real P6 databases name their columns in upper case)."""
    return {k.lower(): row[k] for k in row.keys()}  # noqa: SIM118 (iterating a sqlite3.Row gives its values)


def calendars(o) -> dict:
    """{clndr_id: Cal}. A calendar without DaysOfWeek takes its base calendar's week; the base exceptions
    are merged under its own (its own dates win); depth capped at 10. An unreadable calendar keeps error."""
    rows = {r["clndr_id"]: r for r in o.sql("SELECT clndr_id, base_clndr_id, day_hr_cnt, clndr_data FROM CALENDAR")}
    parsed = {}
    for cid, r in rows.items():
        try:
            parsed[cid] = _parse(r["clndr_data"])
        except (ValueError, KeyError, IndexError) as e:
            parsed[cid] = e

    def resolve(cid, depth=0):
        p = parsed.get(cid)
        if isinstance(p, Exception) or p is None:
            return None, {}, f"calendar {cid} unreadable: {p}"
        week, exc = p
        base = rows[cid]["base_clndr_id"]
        if base is not None and base != cid and base in rows and depth < 10:
            bweek, bexc, berr = resolve(base, depth + 1)
            if not berr:
                week = week if week is not None else bweek
                exc = {**bexc, **exc}
        return week, exc, None
    out = {}
    for cid, r in rows.items():
        week, exc, err = resolve(cid)
        out[cid] = Cal(week, exc, r["day_hr_cnt"], err)
    return out


# ----------------------------------------------------------------- the project network (stored F9 values)

H24 = Cal({wd: [(0, 1440)] for wd in range(7)}, {}, 24)  # the 24 hour lag calendar (rcal_24Hour)
DATES = ("act_start_date", "act_end_date", "early_start_date", "early_end_date", "late_start_date", "late_end_date",
         "cstr_date", "cstr_date2", "expect_end_date")


def _activity(r, cals, pid) -> dict:
    a = low(r)
    a["cal"] = cals.get(a["clndr_id"]) or Cal({}, {}, 8, f"calendar {a['clndr_id']} not found")
    for k in DATES:
        a[k] = dt(a.get(k))
    a["ext"] = a["proj_id"] != pid
    return a


def options(o, pid) -> dict:
    """The project's schedule options (PROJPROP 'scheduling': key|value pairs of the root node)."""
    row = o.sql("SELECT prop_value FROM PROJPROP WHERE proj_id = ? AND prop_name = 'scheduling' "
                "AND delete_session_id IS NULL", pid)
    if not row:
        return {}
    v = row[0]["prop_value"]
    try:
        attrs = _tree(v.decode("utf-8", "replace") if isinstance(v, bytes) else v or "")[1]
    except ValueError:
        return {}
    return dict(zip(attrs[::2], attrs[1::2], strict=False))


def network(o, pid=None) -> dict:
    """{acts: {task_id: activity}, code: {task_code: task_id}, preds/succs: {task_id: [link]}, dd, prj, opt,
    lag_rule, pcal}. Links with one end in another project are kept with that activity (ext = True, its
    stored dates)."""
    pid = o.pid if pid is None else pid
    cals = calendars(o)
    acts = {}
    for r in o.sql("SELECT * FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL", pid):
        a = _activity(r, cals, pid)
        acts[a["task_id"]] = a
    links = o.sql("SELECT r.task_pred_id, r.task_id, r.pred_task_id, r.pred_type, r.lag_hr_cnt FROM TASKPRED r "
                  "JOIN TASK s ON s.task_id = r.task_id JOIN TASK p ON p.task_id = r.pred_task_id "
                  "WHERE (s.proj_id = ? OR p.proj_id = ?) AND r.delete_session_id IS NULL "
                  "AND s.delete_session_id IS NULL AND p.delete_session_id IS NULL ORDER BY r.task_pred_id", pid, pid)
    other = {x for r in links for x in (r["task_id"], r["pred_task_id"]) if x not in acts}
    for tid in sorted(other):
        acts[tid] = _activity(o.sql("SELECT * FROM TASK WHERE task_id = ?", tid)[0], cals, pid)
    preds, succs = {}, {}
    for r in links:
        lk = {"id": r["task_pred_id"], "pred": r["pred_task_id"], "succ": r["task_id"],
              "type": r["pred_type"][3:], "lag": float(r["lag_hr_cnt"] or 0)}
        preds.setdefault(lk["succ"], []).append(lk)
        succs.setdefault(lk["pred"], []).append(lk)
    prj = low(o.sql("SELECT * FROM PROJECT WHERE proj_id = ?", pid)[0])
    opt = options(o, pid)
    return {"acts": acts, "code": {a["task_code"]: n for n, a in acts.items() if not a["ext"]}, "preds": preds,
            "succs": succs, "dd": dt(prj["last_recalc_date"]), "prj": prj, "opt": opt, "pid": pid,
            "lag_rule": opt.get("sched_calendar_on_relationship_lag") or "rcal_Predecessor",
            "pcal": cals.get(prj["clndr_id"])}


def lag_cal(net, p, s) -> Cal:
    """Calendar of a link's lag under the project's rule (the successor's project for a cross-project link):
    predecessor (P6 default), successor, 24 hours or the project calendar."""
    rule = net["lag_rule"]
    if rule == "rcal_Successor":
        return s["cal"]
    if rule == "rcal_24Hour":
        return H24
    if rule == "rcal_ProjDefault" and net["pcal"] is not None:
        return net["pcal"]
    return p["cal"]


def lag_left(net, p, lk, s=None) -> float:
    """Lag hours still to run at the data date: the part elapsed since the predecessor's actual date
    (start for SS and SF, finish for FS and FF) is dropped (lag counted from the actual date)."""
    actual = p["act_start_date"] if lk["type"] in ("SS", "SF") else p["act_end_date"]
    if lk["lag"] <= 0 or actual is None or actual >= net["dd"] or net["opt"].get("sched_lag_early_start_flag") == "N":
        return lk["lag"]
    cal = lag_cal(net, p, s or net["acts"][lk["succ"]])
    return max(0.0, lk["lag"] - cal.work_hours(actual, net["dd"]))


def anchor(net, lk, date, late=False) -> datetime:
    """date (of the predecessor, or of the successor on late dates) plus (minus) the lag left, on the lag
    calendar."""
    p, s = net["acts"][lk["pred"]], net["acts"][lk["succ"]]
    lag, cal = lag_left(net, p, lk, s), lag_cal(net, p, s)
    return cal.sub(date, lag) if late else cal.add(date, lag)


def early_gap(net, lk) -> float:
    """Working hours (successor calendar) from the predecessor's early date plus lag (lag calendar) to the
    successor's early date."""
    p, s = net["acts"][lk["pred"]], net["acts"][lk["succ"]]
    a = p["early_start_date"] if lk["type"] in ("SS", "SF") else p["early_end_date"]
    b = s["early_start_date"] if lk["type"] in ("FS", "SS") else s["early_end_date"]
    if a is None or b is None:
        return float("inf")
    return s["cal"].work_hours(anchor(net, lk, a), b)


def driving_path(o, target: str) -> tuple[list, list]:
    """(rows, roots): the open activities that drive target (gap 0), by level then early finish then ID,
    each with the link it drives through (to the path activity of the lowest level, then lowest ID; lag
    in days of the predecessor calendar, the demo's lag rule), and what starts each chain."""
    net = network(o)
    acts, t0 = net["acts"], net["code"][target]
    level, order, roots, edges = {t0: 0}, [t0], [], {}
    i = 0
    while i < len(order):
        n = order[i]
        i += 1
        drv, hidden = [], []
        for lk in net["preds"].get(n, []):
            if abs(early_gap(net, lk)) > TOL_H:
                continue
            (hidden if acts[lk["pred"]]["status_code"] == "TK_Complete" else drv).append(lk)
        if not drv:
            roots.append(_root(net, acts[n], hidden))
        for lk in drv:
            edges.setdefault(lk["pred"], []).append(lk)
            if lk["pred"] not in level:
                level[lk["pred"]] = level[n] + 1
                order.append(lk["pred"])
    out = []
    for n in sorted(level, key=lambda n: (level[n], acts[n]["early_end_date"], acts[n]["task_code"])):
        links = sorted(edges.get(n, []), key=lambda lk: (level[lk["succ"]], acts[lk["succ"]]["task_code"]))
        lk = links[0] if links else None
        succ = acts[lk["succ"]] if lk else {"task_code": None, "task_name": None}
        lag = None if lk is None else lk["lag"] / lag_cal(net, acts[n], succ).hpd
        out.append({"level": level[n], **_view(acts[n]), "succ": (succ["task_code"], succ["task_name"]),
                    "link": lk and lk["type"], "lag": lag})
    return out, roots


def _binding(a) -> bool:
    """An early constraint (start or finish on, on or after, mandatory) on the activity's early date."""
    for ty, d in ((a["cstr_type"], a["cstr_date"]), (a.get("cstr_type2"), a.get("cstr_date2"))):
        if d is None:
            continue
        own = a["early_start_date"] if ty in START_CSTR else a["early_end_date"] if ty in FINISH_CSTR else None
        if own is not None and abs(a["cal"].work_hours(d, own)) <= TOL_H:
            return True
    return False


START_CSTR = ("CS_MSO", "CS_MSOA", "CS_MANDSTART")
FINISH_CSTR = ("CS_MEO", "CS_MEOA", "CS_MANDFIN")


def _root(net, a, hidden) -> dict:
    if _binding(a):
        kind = "constraint"
    elif abs(a["cal"].work_hours(net["dd"], a["early_start_date"])) <= TOL_H:
        kind = "data_date"
    elif hidden:
        kind = "completed_predecessor"
    elif a["act_start_date"] is not None and a["status_code"] != "TK_NotStart":
        kind = "actual_date"
    elif not net["preds"].get(a["task_id"]):
        kind = "open_start"
    else:
        kind = "unexplained"
    return {"activity": (a["task_code"], a["task_name"]), "date": text(a["early_start_date"]), "type": kind}


def days(h, a):
    return None if h is None else float(h) / a["cal"].hpd


def _view(a) -> dict:
    return {"activity": (a["task_code"], a["task_name"]), "status": a["status_code"],
            "es": text(a["early_start_date"]), "ef": text(a["early_end_date"]), "tf": days(a["total_float_hr_cnt"], a)}


# ----------------------------------------------------------------- milestones against the baseline

def _one(a, kind="current"):
    """The one date of a milestone: start of a start milestone, finish of a finish milestone, actual else
    early ('planned': the planned date)."""
    k = "start" if a["task_type"] == "TT_Mile" else "end"
    if kind == "planned":
        return dt(a[f"target_{k}_date"]), "planned"
    return (a[f"act_{k}_date"], "actual") if a[f"act_{k}_date"] else (a[f"early_{k}_date"], "forecast")


def milestones(o, open_only=False, order="date") -> list:
    net = network(o)
    bid = net["prj"]["sum_base_proj_id"]
    base = {}
    if bid is not None:
        bnet = network(o, bid)
        for n in sorted(bnet["acts"], reverse=True):  # the lowest task_id wins
            if not bnet["acts"][n]["ext"]:
                base[bnet["acts"][n]["task_code"]] = bnet["acts"][n]
    crit_h = float(net["prj"]["critical_drtn_hr_cnt"] or 0)
    longest = net["prj"]["critical_path_type"] == "CT_DrivPath"
    out = []
    for a in net["acts"].values():
        if a["ext"] or a["task_type"] not in MILESTONES or (open_only and a["status_code"] == "TK_Complete"):
            continue
        d, kind = _one(a)
        b = base.get(a["task_code"])
        bd = _one(b)[0] if b else None
        done = a["status_code"] == "TK_Complete"
        row = {"activity": (a["task_code"], a["task_name"]), "type": a["task_type"], "status": a["status_code"],
               "date": text(d), "kind": kind, "bl_date": text(bd), "var_cd": None, "var_wd": None, "vs": None,
               "tf": None if done else days(a["total_float_hr_cnt"], a),
               "critical": not done and (a["driving_path_flag"] == "Y" if longest else
                                         a["total_float_hr_cnt"] is not None and a["total_float_hr_cnt"] <= crit_h),
               "_code": a["task_code"]}
        if d and bd:
            wh = a["cal"].work_hours(bd, d)
            row.update(var_cd=(d - bd).total_seconds() / 86400, var_wd=wh / a["cal"].hpd,
                       vs="late" if wh > TOL_H else "early" if wh < -TOL_H else "on_time")
        out.append(row)
    out.sort(key=lambda r: (r["date"] or "9999", r["_code"]))
    if order == "variance":
        out.sort(key=lambda r: (r["var_cd"] is None, -(r["var_wd"] or 0)))
    return out


def _counts(rows) -> dict:
    opened = [r for r in rows if r["status"] != "TK_Complete"]
    return {"milestones": len(rows), "completed": len(rows) - len(opened), "open": len(opened),
            "critical": sum(r["critical"] for r in rows), "late": sum(r["vs"] == "late" for r in rows),
            "early": sum(r["vs"] == "early" for r in rows), "on_time": sum(r["vs"] == "on_time" for r in rows),
            "no_baseline": sum(r["vs"] is None for r in rows),
            "open_late": sum(r["vs"] == "late" for r in opened)}


ALL_KEYS = ("activity", "type", "status", "date", "kind", "bl_date", "var_wd", "var_cd", "vs", "tf", "critical")
LATE_KEYS = ("activity", "date", "bl_date", "var_wd", "var_cd", "vs", "tf", "critical")


def all_ms(o):
    return [{k: r[k] for k in ALL_KEYS} for r in milestones(o)][:30]


def late_ms(o):
    return [{k: r[k] for k in LATE_KEYS} for r in milestones(o, True, "variance")][:10]


def _target(o):
    rows = milestones(o, True, "variance")
    return rows[0]["_code"] if rows else None


def drivers(o):
    t = _target(o)
    return driving_path(o, t)[0][:15] if t else []


def roots(o):
    t = _target(o)
    return driving_path(o, t)[1] if t else []


def _target_row(o, key):
    t = _target(o)
    return None if t is None else driving_path(o, t)[0][0][key]


def _prj(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _crit_definition(o):
    r = o.sql("SELECT critical_path_type, critical_drtn_hr_cnt FROM PROJECT WHERE proj_id = ?", o.pid)[0]
    if r["critical_path_type"] == "CT_DrivPath":
        return Contains("CT_DrivPath")
    return Contains(r["critical_path_type"], f"total float <= {float(r['critical_drtn_hr_cnt'] or 0):g} h")


def _baseline(o):
    bid = _prj(o, "sum_base_proj_id")
    return None if bid is None else o.one("SELECT proj_short_name FROM PROJECT WHERE proj_id = ?", bid)


def _count(key):
    return lambda o: _counts(milestones(o))[key]


HARD = ("CS_MSO", "CS_MEO", "CS_MSOB", "CS_MEOB", "CS_MANDSTART", "CS_MANDFIN")  # DCMA hard constraints
CSTR_LABELS = {"CS_MSO": "Start On", "CS_MSOA": "Start On or After", "CS_MSOB": "Start On or Before",
               "CS_MEO": "Finish On", "CS_MEOA": "Finish On or After", "CS_MEOB": "Finish On or Before",
               "CS_MANDSTART": "Mandatory Start", "CS_MANDFIN": "Mandatory Finish", "CS_ALAP": "As Late As Possible"}
WORDS = {"activity_constraint": "a constraint", "project_must_finish": "the project must finish date",
         "open_end": "the project finish (open end)", "unexplained": "an unexplained source"}


def _wanted(o) -> list:
    return list(dict.fromkeys(c.strip() for c in (o.args.get("contract") or "").split(",") if c.strip()))


def contract(o) -> list:
    """The contract milestones given (any activity type), by their one date: constraint, hard flag, predecessor
    links, the date minus the constraint date in working days of its calendar, total float and the source of
    its float (late gaps traced on the stored F9)."""
    from oracles.update_integrity_audit import _sources
    if not _wanted(o):
        return []
    net = network(o)
    rows = []
    for code in _wanted(o):
        if code not in net["code"]:
            continue
        n = net["code"][code]
        a = net["acts"][n]
        d = _one(a)[0]
        cd = a["cstr_date"] if a["cstr_type"] else None
        done = a["status_code"] == "TK_Complete"
        tf = None if done else days(a["total_float_hr_cnt"], a)
        origin = None
        if not done and a["late_end_date"] is not None:
            kinds = sorted({k for k, _s in _sources(net, code)})
            origin = Contains(f"Total float {round(tf, 2)} d of {code} comes from", *(WORDS[k] for k in kinds))
        rows.append({"activity": (code, a["task_name"]), "cstr": CSTR_LABELS.get(a["cstr_type"]), "cdate": text(cd),
                     "hard": bool({a["cstr_type"], a.get("cstr_type2")} & set(HARD)),
                     "preds": len(net["preds"].get(n, [])), "date": text(d),
                     "vs_c": None if not (d and cd) else a["cal"].work_hours(cd, d) / a["cal"].hpd, "tf": tf,
                     "origin": origin, "_key": (text(d) or "9999", code, n)})
    rows.sort(key=lambda r: r.pop("_key"))
    return rows[:20]


def _not_found(o):
    if not _wanted(o):
        return None
    found = {r[0] for r in o.sql("SELECT task_code FROM TASK WHERE proj_id = ? AND delete_session_id IS NULL", o.pid)}
    return [c for c in _wanted(o) if c not in found]


SLOTS = {
    "data_date": lambda o: _prj(o, "last_recalc_date"),
    "last_f9": lambda o: _prj(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "baseline_project": _baseline,
    "baseline_dates": lambda o: "current",
    "must_finish": lambda o: _prj(o, "plan_end_date"),
    "critical_definition": _crit_definition,
    **{f"n_{k}": _count(k) for k in ("milestones", "completed", "open", "critical", "late", "early", "on_time",
                                      "no_baseline", "open_late")},
    "target_code": _target,
    "target_name": lambda o: (_target_row(o, "activity") or (None, None))[1],
    "target_tf": lambda o: _target_row(o, "tf"),
    "ct_def": lambda o: _crit_definition(o) if _wanted(o) else None,
    "ct_not_found": _not_found,
}
TABLES = {"all": all_ms, "late": late_ms, "drivers": drivers, "roots": roots, "contract": contract}
