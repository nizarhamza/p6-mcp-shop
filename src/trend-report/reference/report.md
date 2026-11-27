# Schedule trend across {total} updates

Updates from data date {first_dd} to {last_dd}, ordered by data date. Values of the last F9 of each update; read only: nothing was written to the database.

## Finish by update

Finish variances are working days of each update's project calendar, positive = later: against the must finish date, the first update, the previous update and the update's own project baseline.

[table: updates]

## Progress and float by update

Units % = actual / at completion units (labor and nonlabor); BL planned % = baseline planned units at the data date; SPI = earned / baseline planned units (n/a without a project baseline). Near critical = open activities that are not critical with total float up to {near_d} days.

[table: progress]

## Schedule quality by update

DCMA weighted score (points out of 100) and grade, the checks that failed and BEI (n/a without a project baseline), as the health check computes them.

[table: quality]

## Changes since the previous update

[table: changes]

## Milestones

Milestones followed (present in every update):

[table: milestones]

Their dates in the latest update shown, {last_project}, in the same order:

[table: ms_latest]

## Notes

[table: notes]

## Actions

Only the actions that apply to the latest update shown, {last_project}:

[if: last_stale]
- {last_project} was changed after its last F9: reschedule it in P6 (F9) before using its figures.
[end if]
[if: last_vs_prev]
- The finish moved by {last_vs_prev} working days since the previous update (positive = later): ask for the reason and review the critical path.
[end if]
[if: last_neg]
- Open activities with negative float: {last_neg}. Recover them: the schedule misses the must finish date or a constraint.
[end if]
[if: last_failed]
- DCMA checks failed: {last_failed}. Run the schedule quality audit on {last_project}.
[end if]
[if: last_cuts]
- Durations cut since the previous update: {last_cuts}. Run the update integrity audit to see which and ask for the justification.
[end if]
[if: last_removed]
- Activities removed since the previous update: {last_removed}. Check that their scope was completed or transferred.
[end if]
