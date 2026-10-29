Schedule risk of project {project}: a Monte Carlo simulation of {iterations} iterations (seed {seed}) on this server's CPM engine gives the finish dates at p10, p50, p80 and p90, the chance to finish on time, the p80 buffer, the milestones and the activities most often on the critical path. Read only: nothing is written to the database.

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
- The caveat of the result is copied as it is, in the user's language: never present the percentiles as a
  forecast without it.
- The same project, iterations and seed give the same figures: say which seed was used, and run again with
  another seed only when the user asks.
- Other ranges (by Activity ID, WBS or activity code, or three-point estimates in UDFs) are arguments of
  p6_schedule_risk: use them only when the user gives the ranges, and say which were used.
