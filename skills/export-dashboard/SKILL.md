---
name: p6-export-dashboard
description: "Excel project controls dashboard of a P6 project (one A3 page and detail sheets), then a short summary of its cards, counts, failed DCMA checks and warnings (the database is never written). Use when the user asks for an Excel dashboard or a one-page project report."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md", "reference/example.md"] -->

# Excel dashboard

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- path: Full path of the .xlsx file to write
- baseline: Project ID of the baseline (empty = the project baseline) (may be empty)
- prepared_by: Name printed under the title (may be empty) (may be empty)
- revision: Revision printed under the title (may be empty) (may be empty)
- company: Company name in the sidebar (may be empty) (may be empty)
- colors: Colors 'primary,accent' in hex, for example 1F3864,C00000 (may be empty) (may be empty)

Excel project controls dashboard of project <project>, written to <path>, then a short summary of its cards, counts, failed DCMA checks and warnings. The P6 database is never written.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order:
1. sum = p6_project_summary(project="<project>", baseline="<baseline>"): data date, last F9, schedule state and the baseline used, before the file is written.
2. dash = p6_export_dashboard(project="<project>", path="<path>", baseline="<baseline>", prepared_by="<prepared_by>", revision="<revision>", company="<company>", colors="<colors>"): writes the workbook (never the database): the 7 cards as written, counts, failed DCMA checks, warnings.
Leave out an argument whose value is empty (baseline, colors, company, prepared_by, revision).

Between the two calls and around call 2:
- After call 1, if sum.schedule_state.stale is true or edited_since_last_schedule is not null, say so and
  ask the user whether to export anyway or to press F9 in P6 first; wait for the answer. If
  sum.baseline.used is null, say that the delayed count, the variance cards and the baseline bars will
  stay empty.
- If a file already exists at <path>, call 2 is refused: ask the user whether to replace it, and only on
  a yes repeat call 2 with the same arguments and overwrite=true.
- If the file is open in Excel, call 2 is refused: ask the user to close it, then run call 2 again.

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
- The card values (their text) and details are copied as returned; a | inside a cell is written /.
- File paths are written exactly as returned.

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
