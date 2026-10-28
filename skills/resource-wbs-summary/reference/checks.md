# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_group_summary says the project has no data date or is an EPS node: repeat its message and stop.

## Cross-checks (each pair must be equal)

1. wbs.schedule_state.data_date = status.schedule_state.data_date (same data date).
2. wbs.totals.activities = status.totals.activities.
3. wbs.totals.budget_units = status.totals.budget_units.
4. wbs.totals.actual_units = status.totals.actual_units.
5. wbs.totals.critical = status.totals.critical.

If a pair differs, the database changed between the calls: run the three calls again once. If it still
differs, say which pair differs and do not publish the totals it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The tables keep the rows in the order returned and stop at their cap (resources 10, WBS 30,
  status 10). A table whose call has more pages (next_offset not null) ends with its line "Showing the
  first <returned> of <total> ...", both numbers copied from that call.
- The Total rows come from the totals of the call, never from adding the rows.
- Every resource is written "Resource ID - name", every WBS node "WBS code - name".
- Material quantities stay in their own unit: they are never added to hours.
- The warning block is kept only when schedule_state.stale is true.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
