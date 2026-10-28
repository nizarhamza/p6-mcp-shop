---
name: p6-export-dashboard
description: "Excel project controls dashboard of a project (one A3 page and detail sheets), then a short summary of its figures (the database is never written). Use when the user asks for an Excel dashboard or a one-page project report."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Excel dashboard

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- path: Full path of the .xlsx file to write
- baseline: Project ID of the baseline (empty = the project baseline) (may be empty)
- prepared_by: Name printed under the title (may be empty)
- revision: Revision printed under the title (may be empty)
- company: Company name in the sidebar (may be empty)
- colors: Colors 'primary,accent' in hex, for example 1F3864,C00000 (may be empty)

Excel dashboard of project <project>, written to <path>.

Optional values: baseline "<baseline>" (empty = the project baseline), prepared_by "<prepared_by>",
revision "<revision>", company "<company>", colors "<colors>". Leave every empty one out of the calls
below.

Steps:
1. p6_project_summary(project="<project>", baseline="<baseline>"): data date, last schedule run,
   baseline and schedule_state. If the schedule is stale or was edited since the last schedule, say so
   and ask the user whether to export anyway or to press F9 in P6 first; wait for the answer. Without a
   baseline, say that the delayed count, the variance cards and the baseline bars will stay empty.
2. p6_export_dashboard(project="<project>", path="<path>", baseline="<baseline>",
   prepared_by="<prepared_by>", revision="<revision>", company="<company>", colors="<colors>"): writes
   the workbook (the database is never written). If a file already exists at that path the call is
   refused: ask the user whether to replace it, and only on a yes repeat it with overwrite=true. If the
   file is open in Excel, ask the user to close it, then run this step again.
3. Read the result: path, sheets (rows per sheet), counts, cards, dcma_failed, warnings.

Report: the file path; the 7 cards with their value and detail, as written on the Dashboard; the
numbers of activities, WBS nodes, milestones and critical activities; the DCMA checks that fail (or
that all pass); every warning. End with how to use the file: the Dashboard prints on one A3 landscape
page and is protected without a password; the Schedule Overview opens folded to WBS level 2 (outline
buttons unfold it); the Critical Path sheet lists the P6 float paths of the last F9 (when P6 stored
none, the near critical activities grouped by total float).

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
