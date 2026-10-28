Delay what-if on project {project}: activity {task_code} delayed by {delay_days} d (days of its calendar, added to its remaining duration). The activity today, what drives it, where its float comes from, then the effect on the project finish, the milestones, the critical activities and the activities that move. The what-if runs in memory: nothing is written to the database.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order. Each call is one page: the report shows that page and says when there are more,
so do not read further pages. Pass delay_days as a number.
[steps]

[rules]

For this skill:
- The finish change is the delta field of the what-if: never work it out from two dates.

Nothing is changed in P6. To make the delay real, the user edits the activity in P6 (or with
p6_update_activity after their explicit yes) and reschedules (F9).
