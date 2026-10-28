# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_lookahead says the project has no data date: repeat its message and stop.
- weeks is not a whole number from 1 to 52: "The look-ahead takes 1 to 52 weeks." and stop.

## Cross-checks (each group must be equal)

1. crit.data_date = all.data_date = all.schedule_state.data_date (same data date).
2. crit.window.from = all.window.from (same window start).
3. crit.window.to = all.window.to (same window end).
4. crit.total = all.counts.critical (the critical table lists every critical activity counted in the window).

If one differs, the database changed between the calls: run the two calls again once. If it still
differs, say which pair differs and do not publish the counts it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The tables keep the rows in the order returned and stop at their cap (weeks 13, critical 30, all 50).
  A table whose call has more pages (next_offset not null) ends with its line "Showing the first
  <returned> of <total> ...", both numbers copied from that call.
- Every activity is written "Activity ID - name".
- The category counts overlap (an activity can be in progress and finishing): they are never added up
  or compared with the activities listed.
- Categories are the items of window joined by ", ", in their order. Start week and finish week are
  copied from start_week and finish_week; null is written "outside".
- The warning block is kept only when schedule_state.stale is true; each action is kept only when its
  count is not 0, with no other advice added.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
