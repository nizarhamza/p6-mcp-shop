# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- A call says the resource is not found: "Resource <resource> was not found: check the Resource ID (p6_resource_summary)."
- p6_resource_loading says the project has no data date: repeat its message and stop.
- rl.total is 0: write the report with its "No assignments" block only (title, data date, that block, the
  actions), then stop.

## Cross-checks (each group must be equal)

1. rl.data_date = rl.schedule_state.data_date (same data date).

If it differs, the database changed during the call: run it again once. If it still differs, say so and do
not publish the figures.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The resources table keeps the order returned and stops at 30 rows ("Only the first 30 resources are
  shown." when rl.resources holds more). The over-allocated table lists the rows of the page whose over is
  true, at most 30; when rl.next_offset is not null it ends with "Showing the first <returned> of <total>
  resource periods." and the over-allocated count of the summary (from counts) still covers every period.
- Every resource is written "Resource ID - name".
- An over-allocated periods cell is "no limit" when the resource has no max units or no calendar.
- Material quantities stay in their own unit: they are never added to hours.
- The warning block is kept only when schedule_state.stale is true.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
