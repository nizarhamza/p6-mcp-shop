# Checks before answering

## Stop rules (write the sentence, then stop)

- Neither updates nor eps was given, or the call asks for one of them: "Give the Project IDs of the updates, separated by commas, or the EPS ID that holds them."
- The call says a trend needs at least two updates, or that the EPS holds fewer than two projects: "A trend needs at least two updates of the same schedule: give two Project IDs or more."
- The call says a project is not found: "Project <the Project ID of the message> was not found: check the Project ID (p6_list_projects)."
- The call says an update has no data date: "<the Project ID of the message> has no data date: schedule it once in P6 (F9), then run this skill again."
- The call says a Project ID is an EPS node: repeat its message and stop.
- Any other error of the call: repeat its message and stop.

## Cross-checks (each group must be equal)

1. t.total = t.series.updates (every update of the series counted once).

If it differs, the database changed during the call: run it again once. If it still differs, say so and do
not publish the tables.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The updates keep the order returned (by data date). When t.next_offset is not null, the four update tables
  end with "Showing the first <returned> of <total> updates." and the latest update shown is the last row
  of the page, not the latest of the series: say so once.
- The milestone dates are those of the latest update shown, in the order of the milestones table.
- Every milestone of the milestones table is written "Activity ID - name".
- Failed checks are written with the names the call returns, separated by commas; an empty list is "none".
- A value the call leaves null is n/a: the first update has no variance against the previous one and no
  changes, an update without a project baseline has no baseline variance, BL planned %, SPI or BEI.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
