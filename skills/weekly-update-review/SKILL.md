---
name: p6-weekly-update-review
description: "Weekly schedule update review of a project: progress, critical path, status issues, look-ahead and baseline variance. Use when the user asks for a weekly update review, a status report or how a project is progressing."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Weekly update review

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- weeks: Look-ahead length in weeks (default 3)

Weekly update review of project <project>.

Steps:
1. p6_project_summary(project="<project>"): data date, finish dates, % complete, SPI, schedule_state.
2. p6_progress_check(project="<project>"): out of sequence links and status inconsistencies.
3. p6_critical_path(project="<project>"): open critical activities and their float.
4. p6_lookahead(project="<project>", weeks=<weeks>): work in progress, starting and finishing.
5. If the project has a baseline: p6_compare_projects(project="<project>", section="activities",
   min_variance_days=5) for the finish variance and the most slipped activities.

Report, in this order: status and data date (with any stale warning); progress (units %, physical %,
SPI); forecast finish against the must finish date and the baseline; critical path and the activities
that slipped; progress issues to fix in the next update; look-ahead for the next <weeks> weeks; a short
numbered list of actions.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
