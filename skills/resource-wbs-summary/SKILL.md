---
name: p6-resource-wbs-summary
description: "Units and costs of a P6 project by resource, then activities and units by WBS and by activity status, with totals. Use when the user asks how hours, units or costs are spread over resources, WBS or status."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md", "reference/example.md"] -->

# Resource and WBS summary

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- wbs_level: WBS level of the WBS table (1 = the level below the project node) (default 1)

Resource and WBS summary of project <project>: quantities and costs by resource, then activities and units by WBS (level <wbs_level>) and by activity status, with totals. Nothing is written to the database.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Each call is one page: the report shows that page and says when there are more,
so do not read further pages.
1. res = p6_resource_summary(project="<project>", limit=10): quantities and costs per resource, totals.
2. wbs = p6_group_summary(project="<project>", by="wbs", wbs_level=<wbs_level>, limit=30): activities and units per WBS node, totals, data date.
3. status = p6_group_summary(project="<project>", by="status", limit=10): activities and units per status.

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
