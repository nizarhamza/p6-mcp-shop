# Look-ahead brief of {project}

Window from {window_from} to {window_to} (end excluded): {window_days} calendar days from the data date {data_date}. Last schedule run (F9) {last_f9}. Dates and float come from that run: open activities use their remaining dates, LOE and WBS summary activities are left out.

[if: stale]
Warning: this project was changed after its last F9. Dates, float and critical flags are out of date until it is rescheduled in P6 (F9).
[end if]

## In the window

- Activities listed: {listed}.
- In progress: {in_progress}; starting: {starting}; finishing: {finishing}; spanning the whole window: {spanning}.
  These categories overlap (an activity can be in progress and finishing): they do not add up to the activities listed.
- Critical: {critical} ({critical_definition}).

## Weeks

In the tables below, categories are the reasons an activity is listed (in_progress, starting, finishing, spanning); forecast start is the actual start of an activity in progress, else its remaining start; forecast finish is its remaining finish. Start week and finish week are the weeks of the window holding those dates ("outside" when the date is not in the window).

[table: weeks]

## Critical activities

[table: critical]

## All activities of the window

[table: all]

## Actions

[if: critical]
- Review the {critical} critical activities of the window first, with their owners: confirm their forecast dates and what they wait for.
[end if]
[if: in_progress]
- Collect the progress of the {in_progress} activities in progress before the next update: actual dates, remaining duration and percent complete.
[end if]
[if: starting]
- Check that the {starting} activities starting in the window are ready: predecessors finished, crews, materials and permits available.
[end if]
