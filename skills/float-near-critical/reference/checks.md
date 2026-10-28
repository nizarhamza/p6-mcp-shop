# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_float_analysis finds no open activity (scope.activities 0): "Project <project> has no open activity: there is no float to analyse." and stop.

## Cross-checks (each group must be equal)

1. fa.schedule_state.data_date = fp.schedule_state.data_date = nc.schedule_state.data_date (same data date).
2. fa.scope.activities = nc.counts.open (same open activities).
3. fa.stats.negative_tf = nc.counts.negative_float (same negative float count).

If one differs, the database changed between the calls: run the three calls again once. If it still
differs, say which pair differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The tables keep the rows in the order returned and stop at their cap (ranges 12, float paths 10,
  float path activities 30, near-critical 30). Every near-critical row has a total float above 0. A table whose call has more pages (next_offset not null)
  ends with its line "Showing the first <returned> of <total> ...", both numbers copied from that call.
- Every activity is written "Activity ID - name". A null float path or order is written "none".
- The bucket samples (tf_sample, ff_sample) are not shown: they carry Activity IDs without names.
- The warning blocks are kept only when their slot says so (stale true, negative not 0,
  ranges_covered false).
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
