---
name: p6-list
description: "List the projects of the database grouped by EPS, with status, data date and finish."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# List projects by EPS

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- eps: EPS ID to show (empty = every EPS) (may be empty)

List the projects of the database grouped by EPS. EPS filter: "<eps>" (empty = every EPS).

Steps:
1. p6_list_eps(): every EPS node with eps_id, eps_name, wbs_id and parent_wbs_id, to build the EPS tree (read every page).
2. p6_sql_select(query="SELECT e.wbs_short_name AS eps_id, e.wbs_name AS eps_name, p.proj_short_name AS project_id, w.wbs_name AS project_name, w.status_code AS status, p.last_recalc_date AS data_date, p.scd_end_date AS finish FROM PROJECT p JOIN PROJWBS w ON w.proj_id = p.proj_id AND w.proj_node_flag = 'Y' AND w.delete_session_id IS NULL LEFT JOIN PROJWBS e ON e.wbs_id = w.parent_wbs_id WHERE COALESCE(p.project_flag, 'Y') = 'Y' AND p.orig_proj_id IS NULL AND p.delete_session_id IS NULL AND w.status_code <> 'WS_Template' ORDER BY e.wbs_short_name, p.proj_short_name"): one row per project with its EPS (read every page).

Report: one section per EPS, in the order of the EPS tree, with its full path (parent EPS > child EPS) as heading. Under each EPS, a table with Project ID - Project name, status, data date and finish date. If an EPS filter is given, show only that EPS and its child EPS. Projects without an EPS (eps_id empty) go last under "(no EPS)". End with the number of projects per EPS and the total. Baselines are not listed.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
