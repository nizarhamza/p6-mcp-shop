# Fields of Delay what-if

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. act = p6_get_activity(project="{project}", task_code="{task_code}"): the activity today.
2. drv = p6_driving_path(project="{project}", target="{task_code}", limit=15): what drives it.
3. fo = p6_float_origin(project="{project}", task_code="{task_code}", limit=10): where its total float comes from. If this call returns an error, keep its message as fo.error (its other fields are null).
4. wi = p6_schedule_whatif(project="{project}", edits=[{"op": "duration", "task_code": "{task_code}", "add_remaining_days": {delay_days}}], limit=15): the delay applied in memory.

## Formats

- text: the value as returned
- int: the whole number, a comma between thousands: 1,227
- date: the first 10 characters: YYYY-MM-DD
- datetime: the first 16 characters: YYYY-MM-DD HH:MM
- n0: the number as written in the result rounded to a whole number, halves away from zero, a comma between thousands: 12,345
- n1: the same to 1 decimal: 12,345.6 (-104274.95 gives -104,275.0)
- n2: the same to 2 decimals: 12,345.67
- pct1: the same to 1 decimal, then %: 49.7%
- flag: yes for true, no for false
- id_name: the two fields joined: ID - Name (the ID alone when the name is null, the none text when the ID is null)
- list: the items of the list in their order, joined by a comma and a space: in_progress, finishing
- A null value is written as the slot's or column's none text (n/a unless stated).
- [if: slot] is true for true, a number other than 0, a text or list that is not empty.

## Arguments

- {project}: Project ID as shown in P6, as given
- {task_code}: Activity ID of the activity to delay, as given
- {delay_days}: Delay in days of the activity's calendar, added to its remaining duration, as given

## Units

- wd: working days of each activity's calendar
- cd: calendar days
- d: days of each activity's calendar (hours / hours per day)
- %: percent

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | act.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | act.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | act.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| act_name | act.task_name |  | text | n/a | activity name |
| act_status | act.status_code |  | text | n/a | activity status |
| act_wbs | act.wbs_name |  | text | n/a | WBS node name |
| act_calendar | act.calendar.name |  | text | n/a | calendar name |
| act_actual_start | act.act_start_date |  | date | n/a | actual start (null: not started) |
| act_es | act.early_start_date |  | date | n/a | early start |
| act_ef | act.early_end_date |  | date | n/a | early finish |
| act_lf | act.late_end_date |  | date | n/a | late finish |
| act_orig_d | act.orig_dur_d | d | n1 | n/a | original duration |
| act_rem_d | act.rem_dur_d | d | n1 | n/a | remaining duration |
| act_pct | act.phys_complete_pct | % | pct1 | n/a | physical % complete |
| act_tf | act.total_float_d | d | n1 | n/a | total float |
| act_ff | act.free_float_d | d | n1 | n/a | free float |
| act_longest | act.driving_path_flag |  | text | n/a | on the longest path (Y or N) |
| fo_error | fo.error |  | text | n/a | why the float origin failed |
| origin_type | fo.origin.type |  | text | n/a | source of the late dates |
| origin_activity | fo.['origin.task_code', 'origin.task_name'] |  | id_name | n/a | activity at the source (null: several sources) |
| origin_date | fo.origin.date |  | date | n/a | date at the source |
| explanation | fo.explanation |  | text | n/a | the float origin in words |
| edit_applied | wi.edits.0 |  | text | n/a | the edit as applied |
| finish_before | wi.project_finish.before |  | date | n/a | project finish of the last F9 |
| finish_after | wi.project_finish.after |  | date | n/a | project finish with the delay |
| finish_delta_cd | wi.project_finish.delta_cd | cd | n1 | n/a | project finish change |
| finish_delta_wd | wi.project_finish.delta_wd | wd | n1 | n/a | same, finish activity's calendar |
| fc_definition | wi.float_change.definition |  | text | n/a | definition of critical used |
| critical_before | wi.float_change.critical_before |  | int | n/a | critical open activities before |
| critical_after | wi.float_change.critical_after |  | int | n/a | critical open activities after |
| negative_before | wi.float_change.negative_float_before |  | int | n/a | open activities with negative float, before |
| negative_after | wi.float_change.negative_float_after |  | int | n/a | same, after |
| became_critical | wi.float_change.became_critical |  | int | n/a | open activities that become critical |
| no_longer_critical | wi.float_change.no_longer_critical |  | int | n/a | open activities no longer critical |
| changed_total | wi.total |  | int | n/a | activities whose dates or float move |
| engine_trusted | wi.engine.trusted |  | flag | n/a | engine matches the last F9 (rate >= 0.99) |
| engine_mismatched | wi.engine.open_mismatched |  | int | n/a | open activities differing from the last F9 |

## Table drivers

Level 0 = the activity, then its open driving predecessors.

Rows: drv.rows, in the order returned, at most 15.
When drv.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of drv).
No rows: write 'No driving predecessor.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Level | level |  | int | n/a |  |
| Activity | task_code + task_name |  | id_name | n/a |  |
| Early start | early_start |  | date | n/a |  |
| Early finish | early_finish |  | date | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Drives | successor + successor_name |  | id_name | n/a |  |
| Link | type |  | text | n/a |  |
| Lag (d) | lag_d | d | n1 | n/a |  |

## Table roots

What starts each driving chain.

Rows: drv.drivers_at_root, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 chain starts are shown.
No rows: write 'No chain start found.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Starts from | type |  | text | n/a |  |
| Date | date |  | date | n/a |  |

## Table milestones

The finish activity and every constrained activity.

Rows: wi.milestones, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 milestones are shown.
No rows: write 'No milestone to compare.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Finish before | finish_before |  | date | n/a |  |
| Finish after | finish_after |  | date | n/a |  |
| Change (cd) | delta_cd | cd | n1 | n/a |  |
| Total float before (d) | total_float_d_before | d | n1 | n/a |  |
| Total float after (d) | total_float_d_after | d | n1 | n/a |  |

## Table became

Open activities that become critical.

Rows: wi.float_change.became_critical_rows, in the order returned, at most 15 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 15 items, add the line: Only the first 15 activities are shown.
No rows: write 'No activity becomes critical.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Total float before (d) | total_float_d_before | d | n1 | n/a |  |
| Total float after (d) | total_float_d_after | d | n1 | n/a |  |

## Table changed

Activities whose dates or float move, largest finish change first.

Rows: wi.rows, in the order returned, at most 15.
When wi.next_offset is not null, add the line: Showing the first <returned> of <total> activities that move. (returned and total of wi).
No rows: write 'No activity moves.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Early finish before | early_finish_before |  | date | n/a |  |
| Early finish after | early_finish_after |  | date | n/a |  |
| Finish change (cd) | finish_delta_cd | cd | n1 | n/a |  |
| Total float before (d) | total_float_d_before | d | n1 | n/a |  |
| Total float after (d) | total_float_d_after | d | n1 | n/a |  |

## Cross-checks (equal values)

- data date: activity, driving path, what-if: act.schedule_state.data_date = drv.data_date = wi.schedule_state.data_date
- data date: activity, float origin: act.schedule_state.data_date = fo.schedule_state.data_date
- total float: activity, driving path: act.total_float_d = drv.target.total_float_d
- total float: activity, float origin: act.total_float_d = fo.activity.total_float_d
- early finish: activity, driving path: act.early_end_date = drv.target.early_finish
- project finish before the delay: fo.project_finish = wi.project_finish.before
