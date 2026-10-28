# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_project_summary says the baseline is not found: repeat its message and stop.
- Before call 2, sum.schedule_state.stale is true or edited_since_last_schedule is not null: "The schedule of
  <project> was changed after its last F9: export anyway, or press F9 in P6 first?" Wait for the answer.
- p6_export_dashboard says the file already exists: "<path> already exists: replace it?" Only after the
  user's yes, run call 2 again with the same arguments and overwrite=true. Never pass overwrite=true
  without that yes.
- p6_export_dashboard says it cannot write the file (open in Excel): "Close <path> in Excel, then tell me
  to export again." Run call 2 again only when the user says so.
- p6_export_dashboard says the schedule changed during the export: run call 2 again once; if it fails
  again, repeat its message and stop.
- Any other error of call 2 (path not .xlsx, folder missing, bad colors): repeat its message and stop.

## Cross-checks (each pair must be equal)

1. sum.schedule_state.data_date = dash.data_date (same data date).
2. sum.schedule_state.last_schedule_date = dash.schedule_state.last_schedule_date (same last F9).
3. sum.baseline.used = dash.baseline (same baseline).
4. sum.activities.total = dash.counts.activities.
5. sum.counts.wbs = dash.counts.wbs.
6. sum.critical.critical = dash.counts.critical.

If a pair differs, the database changed between the calls: say which pair differs and ask the user to
export again once the F9 in P6 is done.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The cards table has the 7 cards of dash.cards in their order: the text (the value as Excel shows it) and the
  detail as returned, a | inside a detail written /.
- The DCMA checks are dash.dcma_failed in their order; its empty text when the list is empty.
- Every warning of dash.warnings is listed.
- The stale and no baseline blocks are kept only when their slot says so.
- Headings and sentences are in the user's language; values, IDs, names, file paths and number formats
  exactly as formatted.
