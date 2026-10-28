# Delay what-if: {task_code} - {act_name} delayed by {delay_days} d

Project {project}. Data date {data_date}, last schedule run (F9) {last_f9}. The delay is added to the remaining duration and the schedule is computed again in memory by P6 MCP's CPM engine: nothing is written to the database. Before = the last F9 as stored.

[if: stale]
Warning: this project was changed after its last F9. The stored dates and float are out of date, so the before values and the what-if are too, until it is rescheduled in P6 (F9).
[end if]

[if not: engine_trusted]
Warning: the CPM engine does not reproduce the last F9 of this project ({engine_mismatched} open activities differ). The what-if figures are approximate: check them in P6 before relying on them.
[end if]

## The activity today

- {task_code} - {act_name}: status {act_status}, WBS {act_wbs}, calendar {act_calendar}.
- Actual start {act_actual_start}; early start {act_es}, early finish {act_ef}; late finish {act_lf}.
- Original duration {act_orig_d} d, remaining duration {act_rem_d} d, physical % complete {act_pct}.
- Total float {act_tf} d, free float {act_ff} d; on the longest path: {act_longest}.

## What drives it

Driving predecessors on the early dates of the last F9 (level 0 is the activity; completed activities are left out):

[table: drivers]

Each driving chain starts from:

[table: roots]

## Where its float comes from

[if: fo_error]
The float origin is not available: {fo_error}
[end if]

[if: origin_type]
Origin of the late dates: {origin_type}, at {origin_activity}, date {origin_date}.

{explanation}
[end if]

## Impact of the delay

- Edit applied: {edit_applied}.
- Project finish: before {finish_before}, after {finish_after}; change {finish_delta_cd} cd, {finish_delta_wd} wd (working days of the finish activity's calendar).
- Critical open activities ({fc_definition}): {critical_before} before, {critical_after} after; {became_critical} become critical, {no_longer_critical} are no longer critical.
- Open activities with negative float: {negative_before} before, {negative_after} after.
- Activities whose dates or float move: {changed_total}.

[if: finish_delta_cd]
Warning: this delay moves the project finish by {finish_delta_wd} wd.
[end if]

[if not: finish_delta_cd]
The project finish does not move: the delay is absorbed by float.
[end if]

### Finish activity and constrained activities

[table: milestones]

### Activities that become critical

[table: became]

### Activities that move, largest finish change first

[table: changed]

## Next step

Nothing was changed in P6: this what-if ran in memory. To make the delay real, change the activity in P6 (or ask for p6_update_activity, which is applied only after your explicit yes), then reschedule the project in P6 (F9).
