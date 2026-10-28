# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- sum.baseline.used is null (no project baseline and no baseline given): write the title, the data date line
  and the "No baseline" block of reference/report.md, then stop. Never compare with another project you chose.
- A baseline was given and a call says it is not found: repeat the message and stop.

## Errors of optional calls

- act, rel or pc returned an error: keep the report, write its "failed" block with the message; the slots
  and tables of that call are n/a or left out. Never rebuild them from another call.

## Cross-checks (each group must be equal)

1. sum.schedule_state.data_date = act.schedule_state.data_date = rel.schedule_state.data_date =
   pc.schedule_state.data_date (same data date).
2. sum.baseline.used = act.other = rel.other = pc.baseline.project (same baseline).
3. sum.dates.scheduled_finish = act.projects.scd_end_date.project (same project finish).
4. sum.baseline.finish = act.projects.scd_end_date.other (same baseline finish).
5. sum.baseline.spi_units = pc.to_date.spi (same SPI).
6. act.summary.relationships.matched = rel.summary.relationships.matched.

A failed call is not checked. If a group differs, the database changed between the calls: run the calls
again once. If it still differs, say which group differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- Finish variance in cd and wd proj comes from sum.baseline, never from subtracting two dates.
- The tables keep the rows in the order returned and stop at their cap (causes 10, moved 20, links 20).
  A table whose call has more pages (next_offset not null) ends with its line "Showing the first
  <returned> of <total> ...", both numbers copied from that call.
- Every activity is written "Activity ID - name", in the links table too.
- The warning block is kept only when schedule_state.stale is true.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
