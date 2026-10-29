Schedule quality audit of project {project}: DCMA 14 checks, score and weighted grade, engine check, trend since the previous audit, dangling ends, redundant links and float profile. Fixes are proposed, never applied: this skill calls no write tool.

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

For this skill: the DCMA and trend tables have one row per key of hc.checks and tr.checks, the key in the
Check column, in the order returned; the weighted table one row per key of hc.weighted_score.checks. The dangling count adds open starts and open finishes: an activity
with both counts twice.

Fixes: the report only proposes them. Do not call a write tool in this skill. If the user then asks to
apply one, use the matching tool as a dry run first (p6_add_relationships with the items of a dangling
suggestion, p6_delete_relationships with the task_pred_id of a redundant link from rd), show its plan,
and apply it only after the user's explicit yes to that plan. Then ask the user to open P6, press F9
and run this audit again.
