# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- sum.dates.data_date is null, or p6_lookahead says the project has no data date: "Project <project> has no data date: open it in P6, set the data date and run F9, then ask again."
- p6_project_summary says the project is an EPS node: repeat its message and stop.

## Warnings (kept in the report, never a stop)

- schedule_state.stale is true: the warning block of report.md and the reschedule action.
- The comparison call (cmp) returned an error, for example no project baseline: its message is written in the
  "Slipped against the baseline" section and the rest of the report is written as usual.

## Cross-checks (each group must be equal)

1. sum.schedule_state.data_date = prog.schedule_state.data_date = cp.schedule_state.data_date =
   la.schedule_state.data_date (same data date).
2. sum.schedule_state.last_schedule_date = cp.schedule_state.last_schedule_date =
   la.schedule_state.last_schedule_date (same last F9).
3. sum.critical.critical = cp.total (same critical count).
4. sum.critical.negative_float = cp.counts.negative_float.
5. sum.baseline.used = cmp.other (the comparison used the project baseline; skip when cmp failed).
6. sum.schedule_state.data_date = prev.schedule_state.data_date (only when previous is given).

If a group differs, the database changed between the calls (an F9 or an import): run the calls again
once. If it still differs, say which group differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The tables keep the rows in the order returned and stop at their cap (critical 15, slipped 15,
  since the previous update 15, look-ahead 20). A table whose call has more pages (next_offset not null) ends with its line "Showing
  the first <returned> of <total> ...", both numbers copied from that call.
- Every activity is written "Activity ID - name"; the baseline by its Project ID.
- Day columns keep their unit: (d) days of each activity's calendar, (wd) working days of each
  activity's calendar; the finish variances name calendar days and working days of the project calendar.
- The warning block is kept only when schedule_state.stale is true; an action only when its slot is true.
- The section Since the previous update is kept only when previous is given (prev ran): its counts are
  the summary fields of prev, never rows you counted.
  No other advice is added.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
