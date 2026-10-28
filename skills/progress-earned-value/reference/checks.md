# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- A baseline was given and a call says it is not found: repeat the message and stop.
- p6_progress_curve says the project has no data date: repeat its message and stop.

## No baseline, errors

- sum.baseline.used is null: keep the report with its "No baseline" block; the baseline figures are n/a.
  Never compare with another project you chose.
- pc returned an error (for example no planned units on labor and nonlabor assignments): keep the report,
  write its "failed" block with the message; its slots are n/a and the S-curve table is left out.

## Cross-checks (each group must be equal)

1. sum.schedule_state.data_date = pc.schedule_state.data_date (same data date).
2. sum.baseline.used = pc.baseline.project = wbs.baseline.project (same baseline).
3. sum.baseline.spi_units = pc.to_date.spi (same SPI).
4. sum.percent_complete.budget_units = wbs.root.rollup.budget_units.
5. sum.percent_complete.actual_units = wbs.root.rollup.actual_units.

A failed call is not checked. If a group differs, the database changed between the calls: run the calls
again once. If it still differs, say which group differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The period count comes from pc.period_count, never from counting the periods.
- The tables keep the rows in the order returned and stop at their cap (periods 36, WBS 30). The WBS
  table ends with "Showing the first <returned> of <total> WBS nodes." when wbs.next_offset is not null;
  the periods table ends with "Only the first 36 periods are shown." when pc.periods holds more.
- Every WBS node is written "WBS code - name".
- The warning block is kept only when schedule_state.stale is true.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
