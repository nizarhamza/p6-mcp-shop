# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- A call says the baseline is not found: "Baseline <baseline> was not found: check its Project ID (p6_list_projects)."
- p6_milestones says the project has no data date or is an EPS node: repeat its message and stop.

## Warnings (fixed sentences of report.md)

- schedule_state.stale is true: keep the warning that the project changed after its last F9.
- baseline.project is null: keep the "No baseline" sentence; the variance columns then read n/a.
- counts.open_late is not 0: keep the warning on open milestones later than their baseline date.

## Cross-checks (each pair must be equal)

1. ms.schedule_state.data_date = late.schedule_state.data_date (same data date).
2. ms.schedule_state.data_date = drv.data_date (skip when drv was skipped).
3. ms.must_finish = late.must_finish.
4. ms.counts.open = late.counts.milestones.
5. ms.counts.open_late = late.counts.late.
6. ms.counts.critical = late.counts.critical.
7. late.rows.0.total_float_d = drv.target.total_float_d (skip when drv was skipped).
8. ms.schedule_state.data_date = ct.schedule_state.data_date (only when contract is given).

If a pair differs, the database changed between the calls: run the three calls again once. If it still
differs, say which pair differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- Variances are the variance_wd (working days of the milestone's calendar) and variance_cd (calendar
  days) fields, never a difference of two dates you worked out.
- The tables keep the rows in the order returned and stop at their cap (all milestones 30, open
  milestones 10, drivers 15, chain starts 10). A table whose call has more pages (next_offset not null)
  ends with its line "Showing the first <returned> of <total> ...", both numbers copied from that call.
- Every milestone and activity is written "Activity ID - name".
- The driving path section is kept only when drv ran (target_code not null).
- The contract milestones section is kept only when contract is given (ct ran), with at most 20 rows in
  the order returned; its Float comes from cells are copied as returned. The Not found sentence lists
  ct.not_found as returned.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
