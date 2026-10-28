"""Oracles of resource-wbs-summary: P6's TASKRSRC, RSRC, TASK, PROJWBS and PROJECT rows read with SQL; the
WBS tree walked and the groups added up here."""

from __future__ import annotations

from oracles import HPD, STATUS_NAMES, STATUS_ORDER, SUMMARY_TYPES, Contains, pct

LABOR = ("RT_Labor", "RT_Equip")  # labor and nonlabor: hours, in the unit totals


# ----------------------------------------------------------------- assignments

def _assignments(o):
    return o.sql("SELECT tr.rsrc_id, r.rsrc_short_name, r.rsrc_name, COALESCE(tr.rsrc_type, r.rsrc_type) AS typ, "
                 "r.rsrc_type AS rtype, tr.task_id, t.status_code, tr.target_qty, tr.act_reg_qty, tr.act_ot_qty, "
                 "tr.remain_qty, tr.target_cost, tr.act_reg_cost, tr.act_ot_cost, tr.remain_cost, "
                 "COALESCE(tr.act_start_date, tr.restart_date, tr.target_start_date) AS s, "
                 "COALESCE(tr.act_end_date, tr.reend_date, tr.target_end_date) AS f "
                 "FROM TASKRSRC tr JOIN TASK t ON t.task_id = tr.task_id LEFT JOIN RSRC r ON r.rsrc_id = tr.rsrc_id "
                 "WHERE t.proj_id = ? AND tr.delete_session_id IS NULL AND t.delete_session_id IS NULL", o.pid)


def _n(v):
    return float(v or 0)


def _totals(o):
    rows = _assignments(o)
    lab = [r for r in rows if r["typ"] in LABOR]
    act = sum(_n(r["act_reg_qty"]) + _n(r["act_ot_qty"]) for r in lab)
    rem = sum(_n(r["remain_qty"]) for r in lab)
    ac = sum(_n(r["act_reg_cost"]) + _n(r["act_ot_cost"]) for r in rows)
    rc = sum(_n(r["remain_cost"]) for r in rows)
    return {"resources": len({r["rsrc_id"] for r in rows if r["rsrc_id"] is not None}), "assignments": len(rows),
            "activities": len({r["task_id"] for r in rows}), "planned_qty": sum(_n(r["target_qty"]) for r in lab),
            "actual_qty": act, "remaining_qty": rem, "at_completion_qty": act + rem, "units_pct": pct(act, rem),
            "planned_cost": sum(_n(r["target_cost"]) for r in rows), "actual_cost": ac, "remaining_cost": rc,
            "at_completion_cost": ac + rc, "other": len(rows) - len(lab)}


def resources(o):
    """First page (cap 10) of the documented order: labor and nonlabor first, then by planned quantity
    (largest first), assignments, Resource ID, rsrc_id."""
    groups = {}
    for r in _assignments(o):
        g = groups.setdefault(r["rsrc_id"], {"rows": [], "short": r["rsrc_short_name"], "name": r["rsrc_name"],
                                             "rtype": r["rtype"], "types": set()})
        g["rows"].append(r)
        g["types"].add(r["typ"])
    out = []
    for rid, g in groups.items():
        rows = g["rows"]
        typ = g["rtype"] or max(t for t in g["types"] if t)
        act = sum(_n(r["act_reg_qty"]) + _n(r["act_ot_qty"]) for r in rows)
        rem = sum(_n(r["remain_qty"]) for r in rows)
        planned = sum(_n(r["target_qty"]) for r in rows)
        cost = sum(_n(r["act_reg_cost"]) + _n(r["act_ot_cost"]) + _n(r["remain_cost"]) for r in rows)
        out.append(((0 if typ in LABOR else 1, -planned, -len(rows), g["short"] or "", rid if rid is not None else -1),
                    {"resource": (g["short"] if rid is not None else "(no resource)", g["name"]), "type": typ,
                     "activities": len({r["task_id"] for r in rows}), "planned": planned, "actual": act,
                     "remaining": rem, "units_pct": pct(act, rem), "cost": cost,
                     "start": min(r["s"] for r in rows if r["s"]), "finish": max(r["f"] for r in rows if r["f"])}))
    return [row for _k, row in sorted(out, key=lambda x: x[0])][:10]


# ----------------------------------------------------------------- activities by WBS and status

def _activities(o):
    crit, args = o.critical_sql("t")
    return o.sql(f"SELECT t.task_id, t.wbs_id, t.status_code, t.task_type, t.total_float_hr_cnt / {HPD} AS tf_d, "
                 f"t.remain_drtn_hr_cnt / {HPD} AS rem_d, "
                 "COALESCE(t.target_work_qty, 0) + COALESCE(t.target_equip_qty, 0) AS budget, "
                 "COALESCE(t.act_work_qty, 0) + COALESCE(t.act_equip_qty, 0) AS actual, "
                 "COALESCE(t.remain_work_qty, 0) + COALESCE(t.remain_equip_qty, 0) AS remain, "
                 f"COALESCE(t.act_end_date, t.early_end_date) AS finish, ({crit}) AS crit "
                 "FROM TASK t LEFT JOIN CALENDAR c ON c.clndr_id = t.clndr_id "
                 "WHERE t.proj_id = ? AND t.delete_session_id IS NULL", *args, o.pid)


def _figures(acts) -> dict:
    """The group figures of a set of activities (open = not completed, LOE and WBS summary left out)."""
    opened = [a for a in acts if a["status_code"] != "TK_Complete" and a["task_type"] not in SUMMARY_TYPES]
    tf = [a["tf_d"] for a in opened if a["tf_d"] is not None]
    actual, remain = sum(a["actual"] for a in acts), sum(a["remain"] for a in acts)
    return {"activities": len(acts), "open": len(opened),
            "not_started": sum(a["status_code"] == "TK_NotStart" for a in acts),
            "in_progress": sum(a["status_code"] == "TK_Active" for a in acts),
            "completed": sum(a["status_code"] == "TK_Complete" for a in acts),
            "budget": sum(a["budget"] for a in acts), "actual": actual, "units_pct": pct(actual, remain),
            "critical": sum(bool(a["crit"]) for a in opened), "min_tf": min(tf) if tf else None,
            "rem_dur": sum(a["rem_d"] or 0 for a in acts), "finish": max(a["finish"] for a in acts if a["finish"])}


def _wbs_nodes(o):
    """Project WBS in P6 order (preorder, siblings by seq_num then wbs_id): [(wbs_id, depth, code, name)]."""
    rows = o.sql("SELECT wbs_id, parent_wbs_id, seq_num, proj_node_flag, wbs_short_name, wbs_name FROM PROJWBS "
                 "WHERE proj_id = ? AND delete_session_id IS NULL", o.pid)
    sep = o.one("SELECT name_sep_char FROM PROJECT WHERE proj_id = ?", o.pid) or \
        o.one("SELECT name_sep_char FROM PREFER") or "."
    kids = {}
    for r in rows:
        kids.setdefault(r["parent_wbs_id"], []).append(r)
    top = next(r for r in rows if r["proj_node_flag"] == "Y")
    out = []

    def walk(r, depth, code):
        out.append((r["wbs_id"], depth, code, r["wbs_name"], r["parent_wbs_id"]))
        for k in sorted(kids.get(r["wbs_id"], []), key=lambda x: (x["seq_num"] or 0, x["wbs_id"])):
            walk(k, depth + 1, code + sep + k["wbs_short_name"])
    walk(top, 0, top["wbs_short_name"])
    return out


def _total_row(f: dict, keys) -> dict:
    return {"_label": "Total", **{k: f[k] for k in keys}}


WBS_KEYS = ("activities", "not_started", "in_progress", "completed", "budget", "actual", "units_pct", "critical",
            "min_tf", "finish")


def wbs(o):
    level = int(o.args["wbs_level"])
    nodes = _wbs_nodes(o)
    info = {w: (i, d, code, name, parent) for i, (w, d, code, name, parent) in enumerate(nodes)}
    groups = {}
    acts = _activities(o)
    for a in acts:
        i, d, code, name, parent = info[a["wbs_id"]]
        while d > level:
            i, d, code, name, parent = info[parent]
        groups.setdefault((i, code, name), []).append(a)
    rows = [{"wbs": (code, name), **{k: _figures(g)[k] for k in WBS_KEYS}}
            for (i, code, name), g in sorted(groups.items())]
    return rows[:30] + [_total_row(_figures(acts), WBS_KEYS)]


STATUS_KEYS = ("activities", "budget", "actual", "units_pct", "rem_dur", "critical")


def status(o):
    acts = _activities(o)
    rows = [{"status": STATUS_NAMES[s], **{k: _figures([a for a in acts if a["status_code"] == s])[k]
                                           for k in STATUS_KEYS}}
            for s in STATUS_ORDER if any(a["status_code"] == s for a in acts)]
    return rows[:10] + [_total_row(_figures(acts), STATUS_KEYS)]


# ----------------------------------------------------------------- slots

def _project(o, col):
    return o.one(f"SELECT {col} FROM PROJECT WHERE proj_id = ?", o.pid)


def _crit_definition(o):
    r = o.sql("SELECT critical_path_type, critical_drtn_hr_cnt FROM PROJECT WHERE proj_id = ?", o.pid)[0]
    if r["critical_path_type"] == "CT_DrivPath":
        return Contains("CT_DrivPath", "longest path")
    return Contains(r["critical_path_type"], f"total float <= {float(r['critical_drtn_hr_cnt'] or 0):g} h",
                    "LOE and WBS summary left out")


SLOTS = {
    "data_date": lambda o: _project(o, "last_recalc_date"),
    "last_f9": lambda o: _project(o, "last_schedule_date"),
    "stale": lambda o: o.stale(),
    "resources": lambda o: _totals(o)["resources"],
    "assignments": lambda o: _totals(o)["assignments"],
    "asg_activities": lambda o: _totals(o)["activities"],
    "units_planned": lambda o: _totals(o)["planned_qty"],
    "units_actual": lambda o: _totals(o)["actual_qty"],
    "units_remaining": lambda o: _totals(o)["remaining_qty"],
    "units_at_completion": lambda o: _totals(o)["at_completion_qty"],
    "units_pct": lambda o: _totals(o)["units_pct"],
    "cost_planned": lambda o: _totals(o)["planned_cost"],
    "cost_actual": lambda o: _totals(o)["actual_cost"],
    "cost_remaining": lambda o: _totals(o)["remaining_cost"],
    "cost_at_completion": lambda o: _totals(o)["at_completion_cost"],
    "other_assignments": lambda o: _totals(o)["other"],
    "activities": lambda o: _figures(_activities(o))["activities"],
    "open_activities": lambda o: _figures(_activities(o))["open"],
    "critical": lambda o: _figures(_activities(o))["critical"],
    "critical_definition": _crit_definition,
    "level": lambda o: int(o.args["wbs_level"]),
}
TABLES = {"resources": resources, "wbs": wbs, "status": status}
