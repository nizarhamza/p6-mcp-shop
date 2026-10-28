---
name: p6-update-import-safely
description: "Import an updated XER into an existing P6 project safely: inspect the file, dry run the update, report what it would change and what the XER lacks, then apply only on the user's explicit yes. Use when the user wants to import or load an XER update into a project."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md", "reference/example.md"] -->

# Update import (safe)

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- xer_path: Full path of the XER file
- project: Project ID as shown in P6 (the project to update)

Update project <project> from the XER file <xer_path>, safely: inspect the file, dry run the update, report what it would change and what the XER lacks, then apply only after the user's explicit yes.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules, checks before applying and before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Call 2 is a dry run: it writes nothing and returns a confirmation_token that you
keep for yourself and never show.
1. ins = p6_inspect_xer(path="<xer_path>"): file facts, projects in the file, pre-flight errors, warnings and info, global items reused or created.
2. dry = p6_import_xer(path="<xer_path>", mode="update", project="<project>"): dry run of the update (nothing is written): data date, refusal, counts per table, rows missing from the XER.

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
- File paths are written exactly as returned.

After the report, wait for the user's answers to the two questions:
- No, or no explicit yes to question 1: nothing is applied; say so.
- Yes to question 2 (remove the missing relationships, assignments or both): run the dry run again with
  the same arguments plus remove_missing=["TASKPRED"], ["TASKRSRC"] or ["TASKPRED", "TASKRSRC"], write
  the report again from its result and ask question 1 again: the token belongs to the arguments of its
  own dry run.
- Explicit yes to question 1: call p6_import_xer again with exactly the arguments of the dry run the user
  approved, dry_run=false and that dry run's confirmation_token (and confirmation_text when the dry run
  asks for it). P6 must be closed. Never show the token.
- Then report the backup taken and stale_projects of the result, ask the user to open P6 and press F9,
  and suggest a weekly update review once the F9 is done.

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
