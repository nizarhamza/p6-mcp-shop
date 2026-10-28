# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_get_activity says the activity is not found: "Activity <task_code> was not found in <project>: check the Activity ID (p6_query_activities)."
- act.status_code is TK_Complete: "<task_code> - <name> is completed: it has no remaining duration to delay." Do not run the what-if.
- p6_schedule_whatif returns an error: repeat its message and stop.

## Warnings (fixed sentences of report.md)

- schedule_state.stale is true: keep the warning that the project changed after its last F9.
- wi.engine.trusted is false: keep the warning that the engine does not reproduce the last F9.
- fo returned an error (fo.error not null): keep its sentence instead of the float origin.
- wi.project_finish.delta_cd is not 0: keep the warning that the delay moves the project finish.

## Cross-checks (each pair must be equal)

1. act.schedule_state.data_date = drv.data_date = wi.schedule_state.data_date (same data date).
2. act.schedule_state.data_date = fo.schedule_state.data_date (skip when fo returned an error).
3. act.total_float_d = drv.target.total_float_d.
4. act.total_float_d = fo.activity.total_float_d (skip when fo returned an error).
5. act.early_end_date = drv.target.early_finish.
6. fo.project_finish = wi.project_finish.before (skip when fo returned an error).

If a pair differs, the database changed between the calls: run the four calls again once. If it still
differs, say which pair differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The finish change comes from wi.project_finish.delta_cd and delta_wd, never from two dates.
- The tables keep the rows in the order returned and stop at their cap (drivers 15, chain starts 10,
  milestones 10, become critical 15, activities that move 15). A table whose call has more pages
  (next_offset not null) ends with its line "Showing the first <returned> of <total> ...", both numbers
  copied from that call.
- Every activity is written "Activity ID - name".
- The report says that nothing was written: the what-if runs in memory. Any real change needs the
  user's explicit yes, then F9 in P6.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
