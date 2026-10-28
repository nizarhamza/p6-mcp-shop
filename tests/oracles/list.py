"""Oracles of list: P6's PROJECT and PROJWBS rows read with SQL; the EPS tree walked and the projects counted
here. An EPS node is a PROJECT row with project_flag 'N' and its project WBS node (proj_node_flag 'Y'); a
project's node has the EPS node as parent. Baselines (orig_proj_id set) and template projects (status
WS_Template, or no EPS node above them) are never listed or counted."""

from __future__ import annotations


def _eps_tree(o) -> list[dict]:
    """EPS nodes, each before its children; siblings by seq_num, EPS ID, wbs_id; path = names from the top."""
    rows = o.sql("SELECT w.wbs_id, w.parent_wbs_id, w.seq_num, w.wbs_short_name, w.wbs_name FROM PROJWBS w "
                 "JOIN PROJECT p ON p.proj_id = w.proj_id WHERE p.project_flag = 'N' AND w.proj_node_flag = 'Y' "
                 "AND w.delete_session_id IS NULL AND p.delete_session_id IS NULL")
    ids = {r["wbs_id"] for r in rows}
    kids: dict = {}
    for r in rows:
        kids.setdefault(r["parent_wbs_id"] if r["parent_wbs_id"] in ids else None, []).append(r)
    out: list[dict] = []

    def walk(parent, names):
        for r in sorted(kids.get(parent, []), key=lambda x: (x["seq_num"] or 0, x["wbs_short_name"], x["wbs_id"])):
            path = names + [r["wbs_name"] or r["wbs_short_name"]]
            out.append({"wbs_id": r["wbs_id"], "parent": r["parent_wbs_id"], "eps_id": r["wbs_short_name"],
                        "path": " > ".join(path)})
            walk(r["wbs_id"], path)
    walk(None, [])
    return out


def _projects(o) -> list:
    """Live projects (not EPS nodes, not baselines) with their project WBS node."""
    return o.sql("SELECT p.proj_short_name, p.last_recalc_date, p.scd_end_date, w.wbs_name, w.status_code, "
                 "w.parent_wbs_id FROM PROJECT p JOIN PROJWBS w ON w.proj_id = p.proj_id AND w.proj_node_flag = 'Y' "
                 "AND w.delete_session_id IS NULL WHERE COALESCE(p.project_flag, 'Y') = 'Y' AND p.orig_proj_id IS NULL "
                 "AND p.delete_session_id IS NULL")


def _counted(o) -> list:
    return [p for p in _projects(o) if p["status_code"] != "WS_Template"]


def eps(o):
    tree = _eps_tree(o)
    direct = {n["wbs_id"]: sum(p["parent_wbs_id"] == n["wbs_id"] for p in _counted(o)) for n in tree}
    sub = dict(direct)
    for n in reversed(tree):
        if n["parent"] in sub:
            sub[n["parent"]] += sub[n["wbs_id"]]
    return [{"path": n["path"], "eps_id": n["eps_id"], "projects": direct[n["wbs_id"]], "subtree": sub[n["wbs_id"]]}
            for n in tree][:200]


def _listed(o) -> list[dict]:
    tree = _eps_tree(o)
    order = {n["wbs_id"]: i for i, n in enumerate(tree)}
    keep = set(order)
    if o.args.get("eps"):
        top = next(n["wbs_id"] for n in tree if n["eps_id"] == o.args["eps"])
        keep = {top}
        for n in tree:  # parents come first
            if n["parent"] in keep:
                keep.add(n["wbs_id"])
    path = {n["wbs_id"]: n["path"] for n in tree}
    rows = [p for p in _counted(o) if p["parent_wbs_id"] in keep]  # no EPS node above it: a template
    rows.sort(key=lambda p: (order[p["parent_wbs_id"]], p["proj_short_name"]))
    return [{"eps": path[p["parent_wbs_id"]], "project": (p["proj_short_name"], p["wbs_name"]),
             "status": p["status_code"], "data_date": p["last_recalc_date"], "finish": p["scd_end_date"]}
            for p in rows]


SLOTS = {
    "eps_total": lambda o: len(_eps_tree(o)),
    "total": lambda o: len(_listed(o)),
}
TABLES = {"eps": eps, "projects": lambda o: _listed(o)[:200]}
