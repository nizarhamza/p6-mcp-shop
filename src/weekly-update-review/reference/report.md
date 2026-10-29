# Weekly update review of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Read only: nothing was written to the database.

[if: stale]
Warning: this project was changed after its last F9. Dates, float and critical counts are out of date until it is rescheduled in P6 (F9).
[end if]

## Progress

- Units % complete (actual / at completion units, labor and nonlabor): {units_pct}.
- Physical % complete (weighted by budget units): {physical_pct}; duration % complete: {duration_pct}; activities completed: {completed_pct}.
- Activities whose physical % and units % differ: {mismatch}.
- Baseline planned units % at the data date: {bl_planned_pct}; SPI (units, earned / baseline planned): {spi_units}.

## Finish

- Scheduled finish {scheduled_finish}, must finish by {must_finish}: {vs_must_cd} calendar days, {vs_must_wd} working days of the project calendar (positive = later).
- Baseline used: {baseline_used}. Scheduled finish against the baseline's: {vs_bl_cd} calendar days, {vs_bl_wd} working days of the project calendar (positive = later).

[if not: baseline_used]
This project has no baseline: the baseline figures are n/a.
[end if]

## Critical path

Critical: {cp_definition}. Critical open activities: {critical}; open activities with negative float: {neg_float}.

[table: critical]

## Slipped against the baseline

[if: cmp_error]
No comparison with a baseline: {cmp_error}
[end if]
[if not: cmp_error]
Matched activities finishing later: {later}; earlier: {earlier}. Cause of each finish variance, from the start variance and the duration change in working days:

[table: slip_causes]

Activities added or removed, then those whose finish moved by 5 calendar days or more, largest absolute variance in calendar days first (earlier finishes appear too; the table shows working days, so its order can differ from them). Finish variance = start variance + duration delta, in working days of each activity's calendar.

[table: slipped]
[end if]

[if: prev_dd]
## Since the previous update

Compared with {previous} (data date {prev_dd}): open activities with less total float {eroded}; open activities that became critical {became}; no longer critical {no_longer} (each project's own definition of critical). Added and removed activities first, then the largest finish changes in calendar days.

[table: prev_rows]

[end if]
## Progress issues

Out of sequence links: {oos_links}. Out of sequence option of F9: {logic_mode}.

[table: oos]

Status checks:

[table: status_checks]

## Critical look-ahead ({weeks} weeks)

Window from {la_from} to {la_to} (end excluded). Critical activities in the window: {la_critical}; of them in progress {la_in_progress}, starting {la_starting}, finishing {la_finishing}. Week 1 is the first 7 days of the window; outside = before or after it.

[table: lookahead]

## Actions

Only the actions that apply to this update:

[if: stale]
- Reschedule the project in P6 (F9) before using its dates: it was changed after its last F9.
[end if]
[if: oos_links]
- Out of sequence links: {oos_links}. Fix them before the next update.
[end if]
[if: chk_active]
- Activities in progress without an actual start: {chk_active}. Add their actual start.
[end if]
[if: chk_complete]
- Completed activities with remaining duration or no actual finish: {chk_complete}. Correct them.
[end if]
[if: chk_after_dd]
- Activities whose actual dates are after the data date: {chk_after_dd}. Correct them.
[end if]
[if: neg_float]
- Open activities with negative float: {neg_float}. Recover them: the schedule misses the must finish date or a constraint.
[end if]
[if: mismatch]
- Activities whose physical % and units % differ: {mismatch}. Check them.
[end if]
[if: la_critical]
- Critical activities in the look-ahead window: {la_critical}. Follow them up.
[end if]
[if: became]
- Activities that became critical since the previous update: {became}. Review what drives them with the planner before the next update.
[end if]
[if not: baseline_used]
- Assign a project baseline in P6 to measure slippage.
[end if]
