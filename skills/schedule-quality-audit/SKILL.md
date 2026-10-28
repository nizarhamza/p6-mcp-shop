---
name: p6-schedule-quality-audit
description: "DCMA 14 quality audit of a project with trend, dangling ends, redundant links and float profile; fixes proposed as dry runs only. Use when the user asks to audit, check or score the quality of a schedule."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Schedule quality audit

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6

Schedule quality audit of project <project>.

Steps:
1. p6_health_check(project="<project>"): full DCMA 14 run (it saves a snapshot).
2. p6_health_check_compare(project="<project>", before="previous", after="latest"): trend since the
   previous audit; skip it if there is no previous snapshot.
3. p6_dangling(project="<project>"): open starts and open finishes with suggested links.
4. p6_redundant_links(project="<project>"): links that are candidates for removal.
5. p6_float_analysis(project="<project>"): float distribution and high or negative float.

Report: a table of the DCMA checks (pass or fail, value, threshold, threshold source); what improved or
got worse since the previous audit; findings ranked by impact on the critical path and the finish date,
each with the Activity IDs concerned; proposed fixes. A fix that changes the database is shown as a dry
run only: do not apply it unless the user approves it explicitly.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
