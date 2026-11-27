Trend of a P6 schedule across its updates (Project IDs {updates}, or the projects of EPS {eps} when no update is given): one row per update ordered by data date, with finish, progress, float and DCMA figures, the milestones of the latest update shown and what changed between updates, then fixed follow-up actions. Nothing is written to the database.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Each call is one page: the report shows that page and says when there are more,
so do not read further pages.
[steps]

[rules]

For this skill:
- Give the call the Project IDs of the updates when the user names them, else the EPS ID; never both.
- rows.-1 is the last row of t.rows: the latest update shown. The milestone dates table and the actions
  are about that update only.
- The actions are the fixed sentences of report.md only.
