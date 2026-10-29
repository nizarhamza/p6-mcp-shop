---
name: p6-weekly-update-review
description: "Weekly schedule update review of a P6 project: progress, finish dates, critical path, slippage against the baseline, changes since the previous update when given, progress issues and a critical look-ahead, with fixed actions (read only). Use when the user asks for a weekly update review, a status report or how a project is progressing."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md", "reference/example.md"] -->

# Weekly update review

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- weeks: Weeks of the critical look-ahead window from the data date (default 3)
- previous: Project ID of the previous update (empty: no comparison with it) (may be empty)

Weekly update review of project <project>: progress, finish dates, critical path, slippage against the baseline, changes since the previous update when one is given, progress issues, the critical activities of the next <weeks> weeks and the actions that apply. Read only: nothing is written to the database.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Each call is one page: the report shows that page and says when there are more,
so do not read further pages.
1. sum = p6_project_summary(project="<project>"): progress, finish, baseline.
2. prog = p6_progress_check(project="<project>", sample_size=5): out of sequence, status checks.
3. cp = p6_critical_path(project="<project>", limit=15): critical activities.
4. la = p6_lookahead(project="<project>", weeks=<weeks>, critical_only=true, limit=20): critical look-ahead.
5. cmp = p6_compare_projects(project="<project>", section="activities", min_variance_days=5, limit=15): slippage against the baseline. If this call returns an error, keep its message as cmp.error (its other fields are null).
6. prev = p6_compare_projects(project="<project>", other="<previous>", section="activities", min_variance_days=0, limit=15): changes since the previous update. Make this call only when <previous> is given; when it is empty, skip it (its fields are null).
Leave out an argument whose value is empty (previous).

Write the report:
1. Start from reference/report.md. Replace each slot placeholder (a slot name in curly braces) by the field
   named in spec.json slots (call and path), written in the slot's format (reference/fields.md). An argument
   written <name> in these instructions is the placeholder of that name in curly braces in report.md and
   checks.md: the value given (an empty optional argument is left out of the calls).
2. Replace each line [table: name] by that table: one row per item of its list, in the order returned, at
   most its cap, every cell in its column's format, the heads as in spec.json. A table with a totals entry
   ends with its Total row, taken from the totals of its call, never from adding the rows. Only a table
   built from the rows list of its call ends, when that call has more pages (next_offset not null), with
   the line "Showing the first <returned> of <total> <noun>." (returned and total of that call). A table
   built from another list or dict of the call (weeks, paths, roots, causes, counts...) ends with "Only the
   first <cap> <noun> are shown." when that list is longer than the cap, and never with a Showing line. An
   empty list gives the table's empty text; a call that failed or was skipped gives no table.
3. Keep the lines between [if: slot] and [end if] only when the slot is true (true, a number other than 0,
   a text or list that is not empty, an ID - name whose ID is not null), the lines between [if not: slot]
   and [end if] only when it is not; remove the markers.
4. Numbers: take the number as written in the result and round it, halves away from zero, to the decimals
   of its format (-104274.95 in n1 is -104,275.0); whole numbers and counts take a comma between thousands
   (1,227), also in the Showing lines. A null value is written as the slot's or column's none text, and so
   is an ID - name whose ID is null.
5. Never add, subtract, divide, count rows or match rows of two results: a figure that is not a slot or a
   table cell is left out. Ignore the note fields of the tools unless a slot names them.
6. Write the headings and sentences in the user's language; keep values, IDs, names and number formats
   exactly as formatted.
7. Run reference/checks.md before answering. Report a failed cross-check, never hide it; say nothing about
   the checks that pass.

For this skill:
- The actions are the fixed sentences of report.md only: add no other advice.
- previous is the Project ID of the previous update (a project or a saved baseline). Without it, call 6 is
  skipped and the report has no section Since the previous update.

Reference files in this skill's folder (read the ones the steps need):
- reference/report.md
- reference/checks.md
- reference/spec.json
- reference/fields.md
- reference/example.md

## Rules for every P6 skill

Name projects by Project ID and activities by Activity ID. Dates, float and the critical path come from the
last P6 schedule run (F9): when a result carries schedule_state and it says stale, warn the user (in the
skill's warning block when it has one). Durations and float are in days unless a column says otherwise. When
the skill shows one page of a list, keep to that page; otherwise read every page you rely on (offset =
next_offset). Only for a skill that writes: writes take two calls; the first one (dry_run=true, the default)
only returns the plan and a confirmation_token; repeat it with dry_run=false and that token only after the
user's explicit yes to that plan. After a write, ask the user to open P6 and press F9.
