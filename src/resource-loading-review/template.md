Resource loading review of project {project} per {period}: for each resource (or resource {resource} alone when it is given) the totals, the peak period and the over-allocated periods, then the periods over the limit and the resources without a limit, with fixed follow-up actions. Nothing is written to the database.

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
- Labor and nonlabor quantities are hours; material quantities are in the material's own unit (column Unit)
  and are never compared with a limit or added to hours.
- The actions are the fixed sentences of report.md only.
