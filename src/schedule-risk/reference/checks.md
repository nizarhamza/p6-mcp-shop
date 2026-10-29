# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_schedule_risk says the project has no data date or that the network has a loop: repeat its message and
  stop (P6 cannot schedule a loop either).

## Warnings (fixed wording in report.md)

- schedule_state.stale is true: keep the warning.
- cv.trusted is false: keep the warning that the engine does not reproduce the last F9, and point to the
  logic-date-integrity skill.
- iterations_note is not null: keep its line (fewer iterations ran on a large network, or the number asked was
  outside 100 to 5000).

## Cross-checks (each group must be equal)

1. cv.schedule_state.data_date = rk.schedule_state.data_date (same data date).
2. cv.match_rate = rk.engine.match_rate (same engine).

If a group differs, the database changed between the calls: run the two calls again once. If it still
differs, say which group differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you: no
  percentile, chance or buffer is worked out from the weeks or from two dates.
- The tables keep the rows in the order returned and stop at their cap (milestones 10, drivers 15, weeks
  20). When rk has more pages of drivers (next_offset not null) the drivers table ends with "Showing the
  first <returned> of <total> activities.", both numbers copied from rk.
- Activities are written "Activity ID - name".
- The caveat is copied as it is (translated with the report), never left out.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
