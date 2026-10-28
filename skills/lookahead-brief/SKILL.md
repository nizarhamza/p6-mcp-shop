---
name: p6-lookahead-brief
description: "Short look-ahead of a P6 project: what starts, finishes and is in progress in the next weeks, critical work first. Use when the user asks what is coming up or for a short-term plan."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/format.md"] -->

# Look-ahead brief

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- weeks: Look-ahead length in weeks (default 2)

Look-ahead brief of project <project> for the next <weeks> weeks.

Steps:
1. p6_project_summary(project="<project>"): data date and schedule_state.
2. p6_lookahead(project="<project>", weeks=<weeks>): activities in the window.
3. p6_critical_path(project="<project>"): mark the critical ones.

Write the brief in the format of reference/format.md.

Reference files in this skill's folder (read the ones the steps need):
- reference/format.md

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
