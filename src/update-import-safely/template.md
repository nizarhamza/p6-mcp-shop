Update project {project} from the XER file {xer_path}, safely: inspect the file, dry run the update, report what it would change and what the XER lacks, then apply only after the user's explicit yes.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules, checks before applying and before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Call 2 is a dry run: it writes nothing and returns a confirmation_token that you
keep for yourself and never show.
[steps]

[rules]

For this skill:
- File paths are written exactly as returned.

After the report, wait for the user's answers to the two questions:
- No, or no explicit yes to question 1: nothing is applied; say so.
- Yes to question 2 (remove the missing relationships, assignments or both): run the dry run again with
  the same arguments plus remove_missing=["TASKPRED"], ["TASKRSRC"] or ["TASKPRED", "TASKRSRC"], write
  the report again from its result and ask question 1 again: the token belongs to the arguments of its
  own dry run.
- Explicit yes to question 1: call p6_import_xer again with exactly the arguments of the dry run the user
  approved, dry_run=false and that dry run's confirmation_token (and confirmation_text when the dry run
  asks for it). P6 must be closed. Never show the token.
- Then report the backup taken and stale_projects of the result, ask the user to open P6 and press F9,
  and suggest a weekly update review once the F9 is done.
