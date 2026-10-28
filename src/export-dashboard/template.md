Excel project controls dashboard of project {project}, written to {path}, then a short summary of its cards, counts, failed DCMA checks and warnings. The P6 database is never written.

This skill gives you every figure: you copy fields, you never compute them.
- reference/spec.json: the calls, the slots (each a field of one call) and the tables.
- reference/fields.md: for every slot and table column, its field, unit, format and meaning.
- reference/report.md: the report to fill.
- reference/checks.md: stop rules and checks to run before answering.
- reference/example.md: the report filled on a demo project (an example of the format, not of the figures).

Calls, in this order:
[steps]

Between the two calls and around call 2:
- After call 1, if sum.schedule_state.stale is true or edited_since_last_schedule is not null, say so and
  ask the user whether to export anyway or to press F9 in P6 first; wait for the answer. If
  sum.baseline.used is null, say that the delayed count, the variance cards and the baseline bars will
  stay empty.
- If a file already exists at <path>, call 2 is refused: ask the user whether to replace it, and only on
  a yes repeat call 2 with the same arguments and overwrite=true.
- If the file is open in Excel, call 2 is refused: ask the user to close it, then run call 2 again.

[rules]

For this skill:
- The card values (their text) and details are copied as returned; a | inside a cell is written /.
- File paths are written exactly as returned.
