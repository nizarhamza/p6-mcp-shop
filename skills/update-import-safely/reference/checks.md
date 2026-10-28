# Checks before answering

## Stop rules (write the sentence, then stop)

- p6_inspect_xer cannot read the file: repeat its message and stop.
- p6_inspect_xer returns no preflight because the file holds several projects: list the Project IDs of
  the file (the projects table), say "This file holds several projects: export the one to import alone
  from P6", and stop.
- p6_import_xer says the project is not found or is an EPS node: repeat its message and stop.
- ins.preflight.errors is not empty: write the report (the import would be refused), say "Fix these
  errors in the source schedule, export the XER again, then run this skill again", and stop: ask no
  question.
- dry.data_date.older is true: write the report and say "The XER data date is older than the project's:
  is this older file really the one to import?". Only on the user's explicit yes run the dry run again with
  allow_older_data_date=true, write the report again from its result and ask the two questions then.

## Cross-checks (each pair must be equal)

1. ins.preflight.project = dry.preflight.project (same project of the file).
2. ins.preflight.errors = dry.preflight.errors.
3. ins.preflight.warnings = dry.preflight.warnings.
4. ins.projects.0.data_date = dry.data_date.xer (same XER data date).

If a pair differs, the file changed between the calls: run both calls again once. If it still differs,
say which pair differs and do not apply anything.

## Before applying (only after the report)

- The user said yes to question 1 in their own words: a question, a "maybe" or a silence is not a yes.
- The apply call has exactly the arguments of the dry run the user approved (path, mode "update",
  project, and remove_missing or allow_older_data_date only when that dry run had them), dry_run=false and
  that dry run's confirmation_token. A change of arguments needs a new dry run and a new yes.
- The confirmation token is never shown to the user.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- Each table keeps the items in the order returned and stops at its cap; the counts table comes from
  dry.counts, never from the file's rows per table.
- The refusal block is kept only when would_refuse is true, the older data date block only when
  dd_older is true, the questions only when would_refuse is false.
- Headings and sentences are in the user's language; values, IDs, names, file paths and number formats
  exactly as formatted.
