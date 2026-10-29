---
name: p6-schedule-quality-audit
description: "DCMA 14 quality audit of a P6 project: score and weighted grade, checks against their thresholds, engine check, trend since the previous audit, dangling ends, redundant links and float profile, with fixes proposed only. Use when the user asks to audit, check or score the quality of a schedule."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->
<!-- p6mcp files: ["reference/report.md", "reference/checks.md", "reference/spec.json", "reference/fields.md", "reference/example.md"] -->

# Schedule quality audit

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6

Schedule quality audit of project <project>: DCMA 14 checks, score and weighted grade, engine check, trend since the previous audit, dangling ends, redundant links and float profile. Fixes are proposed, never applied: this skill calls no write tool.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Each call is one page: the report shows that page and says when there are more,
so do not read further pages.
1. cv = p6_cpm_validate(project="<project>", limit=5): engine against the last F9: the critical path test relies on it.
2. hc = p6_health_check(project="<project>"): full DCMA 14 run: checks, score, thresholds, baseline (saves a snapshot).
3. tr = p6_health_check_compare(project="<project>", before="previous", after="latest"): trend since the previous audit (fails when there is none). If this call returns an error, keep its message as tr.error (its other fields are null).
4. dg = p6_dangling(project="<project>", limit=15): open starts and open finishes with a suggested link.
5. rd = p6_redundant_links(project="<project>", limit=15): links that are candidates for removal.
6. fa = p6_float_analysis(project="<project>"): total and free float distribution of the open activities.
7. fo_neg = p6_float_origin(project="<project>", task_code=<hc.checks.negative_float.worst.task_code>, limit=1): where the lowest negative float comes from. <hc.checks.negative_float.worst.task_code> is the field checks.negative_float.worst.task_code of the result of hc: when it is null or missing, skip this call (its fields are null).
8. fo_high = p6_float_origin(project="<project>", task_code=<hc.checks.high_float.worst.task_code>, limit=1): where the highest float comes from. <hc.checks.high_float.worst.task_code> is the field checks.high_float.worst.task_code of the result of hc: when it is null or missing, skip this call (its fields are null).

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

For this skill: the DCMA and trend tables have one row per key of hc.checks and tr.checks, the key in the
Check column, in the order returned; the weighted table one row per key of hc.weighted_score.checks. The dangling count adds open starts and open finishes: an activity
with both counts twice.

Fixes: the report only proposes them. Do not call a write tool in this skill. If the user then asks to
apply one, use the matching tool as a dry run first (p6_add_relationships with the items of a dangling
suggestion, p6_delete_relationships with the task_pred_id of a redundant link from rd), show its plan,
and apply it only after the user's explicit yes to that plan. Then ask the user to open P6, press F9
and run this audit again.

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
