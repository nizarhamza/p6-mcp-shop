# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_health_check says the project is an EPS node or has no data date: repeat its message and stop.

## Warnings (fixed wording in report.md)

- schedule_state.stale is true: keep the warning block, first in the report.
- hc.baseline is null: keep the "No baseline" block; missed_tasks and bei show "not evaluated".
- tr failed: keep the "No trend" block and leave the trend table out. A tr.error saying the project "has 1
  health snapshot(s)" (or 0) is the no-previous-audit case: the snapshot this audit just saved is the only
  one, and the block says all there is to say. Any other tr.error: repeat it after that block. Never work out
  a trend yourself.
- A check whose pass is null is written "not evaluated", never pass or fail.

## Cross-checks (each group must be equal)

1. hc, dg, rd and fa schedule_state.data_date (same data date).
2. hc.open_incomplete_activities = fa.scope.activities.
3. hc.checks.negative_float.count = fa.stats.negative_tf.
4. hc.checks.logic.dangling.open_start.count = dg.counts.start.
5. hc.checks.logic.dangling.open_finish.count = dg.counts.finish.

If a group differs, the database changed between the calls: run the calls again once (the health check
saves one more snapshot). If it still differs, say which group differs and do not publish the figures it
concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The DCMA table has one row per key of hc.checks, in the order returned, with "none" for a missing
  threshold and "not evaluated" for a null pass.
- The paged tables (dangling 15, redundant 15) stop at their cap; when the call has more pages
  (next_offset not null) the table ends with "Showing the first <returned> of <total> ...", both numbers
  copied from that call.
- Activities are written "Activity ID - name", the link ends of the redundant links table too; its
  Categories cell lists every category of the link, joined by a comma.
- No write tool was called. Fixes are proposals; a fix is applied only through a dry run the user
  confirms explicitly, then F9 in P6.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
