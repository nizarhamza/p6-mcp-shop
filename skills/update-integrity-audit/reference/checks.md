# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says a project is not found: "Project <project or previous> was not found: check the Project ID
  (p6_list_projects)."
- p6_update_integrity says other must be another project: "Give the Project ID of the previous update, not the
  update itself."

## Warnings (fixed wording in report.md)

- The caveat of ui is always copied, first after the data dates: a flag is a question, not proof.
- schedule_state.stale is true: keep the warning.
- summary.data_date is 1: keep the data date section and its question.

## Cross-checks (each group must be equal)

1. ui.data_date.after = ui.schedule_state.data_date = cmp.projects.last_recalc_date.project (data date of the
   update).
2. ui.data_date.before = cmp.projects.last_recalc_date.other (data date of the previous update).

If a group differs, the database changed between the calls: run the two calls again once. If it still
differs, say which group differs and do not publish the figures it concerns.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The summary table lists the 11 flags in the order returned, with their counts. A flag table and its
  question appear only when its count is not 0; each table shows the sample rows of its flag (at most 10)
  in the order returned. When a count is larger than its table, say nothing more: the count is the figure.
- Activities are written "Activity ID - name"; a calendar is written by its name alone.
- The questions are the fixed sentences of report.md, one per flag raised, worded as questions: never call a
  change manipulation, fraud or an error.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
