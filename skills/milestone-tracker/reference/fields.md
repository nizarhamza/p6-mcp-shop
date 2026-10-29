# Fields of Milestone tracker

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. ms = p6_milestones(project="{project}", baseline="{baseline}", limit=30): every milestone by date with its baseline date and variance, counts, baseline, must finish date.
2. late = p6_milestones(project="{project}", baseline="{baseline}", open_only=true, order="variance", limit=10): open milestones, largest variance in working days first.
3. drv = p6_driving_path(project="{project}", target=<late.rows.0.task_code>, limit=15): driving predecessors of the open milestone with the largest variance. <late.rows.0.task_code> is the field rows.0.task_code of the result of late: when it is null or missing, skip this call (its fields are null).
4. ct = p6_milestones(project="{project}", baseline="{baseline}", codes="{contract}", limit=20): the contract milestones given. Make this call only when <contract> is given; when it is empty, skip it (its fields are null).
Leave out an argument whose value is empty (baseline, contract).

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
- {baseline}: Project ID of the baseline to compare with (empty: the project baseline set in P6), as given
- {contract}: Activity IDs of the contract milestones, separated by commas (empty: no contract table), as given

## Units

- wd: working days of each activity's calendar
- cd: calendar days
- d: days of each activity's calendar (hours / hours per day)
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | ms.schedule_state.data_date |  | date | n/a | data date of the project |
| last_f9 | ms.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | ms.schedule_state.stale |  | flag | n/a | this server changed the project after the last F9 |
| baseline_project | ms.baseline.project |  | text | none | Project ID of the baseline compared with (null: no baseline) |
| baseline_dates | ms.baseline.dates |  | text | n/a | baseline date rule: current = the baseline's actual else forecast date |
| must_finish | ms.must_finish |  | date | n/a | project must finish by date (PROJECT.plan_end_date) |
| critical_definition | ms.critical_definition |  | text | n/a | the project's definition of critical |
| n_milestones | ms.counts.milestones | count | int | n/a | milestones of the project (start and finish milestones) |
| n_completed | ms.counts.completed | count | int | n/a | completed milestones |
| n_open | ms.counts.open | count | int | n/a | milestones not completed |
| n_critical | ms.counts.critical | count | int | n/a | open milestones that are critical |
| n_late | ms.counts.late | count | int | n/a | milestones later than their baseline date |
| n_early | ms.counts.early | count | int | n/a | milestones earlier than their baseline date |
| n_on_time | ms.counts.on_time | count | int | n/a | milestones on their baseline date (within 5 minutes of working time) |
| n_no_baseline | ms.counts.no_baseline | count | int | n/a | milestones without a baseline date |
| n_open_late | ms.counts.open_late | count | int | n/a | open milestones later than their baseline date |
| target_code | drv.target.task_code |  | text | n/a | Activity ID of the open milestone with the largest variance (null: no open milestone) |
| target_name | drv.target.task_name |  | text | n/a | its name |
| target_tf | drv.target.total_float_d | d | n1 | n/a | its total float |
| ct_def | ct.critical_definition |  | text | n/a | set when ct ran |
| ct_not_found | ct.not_found |  | list | n/a | contract IDs not found |

## Table all

Every milestone by date then Activity ID.

Rows: ms.rows, in the order returned, at most 30.
When ms.next_offset is not null, add the line: Showing the first <returned> of <total> milestones. (returned and total of ms).
No rows: write 'This project has no milestone.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Milestone | task_code + task_name |  | id_name | n/a |  |
| Type | task_type |  | text | n/a |  |
| Status | status_code |  | text | n/a |  |
| Date | date |  | date | n/a |  |
| Date kind | date_kind |  | text | n/a |  |
| Baseline date | baseline_date |  | date | n/a |  |
| Variance (wd) | variance_wd | wd | n1 | n/a |  |
| Variance (cd) | variance_cd | cd | n1 | n/a |  |
| Vs baseline | vs_baseline |  | text | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Critical | critical |  | flag | n/a |  |

## Table late

Open milestones, largest variance in working days first, without a baseline date last, then by date.

Rows: late.rows, in the order returned, at most 10.
When late.next_offset is not null, add the line: Showing the first <returned> of <total> open milestones. (returned and total of late).
No rows: write 'No open milestone.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Milestone | task_code + task_name |  | id_name | n/a |  |
| Forecast | date |  | date | n/a |  |
| Baseline date | baseline_date |  | date | n/a |  |
| Variance (wd) | variance_wd | wd | n1 | n/a |  |
| Variance (cd) | variance_cd | cd | n1 | n/a |  |
| Vs baseline | vs_baseline |  | text | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Critical | critical |  | flag | n/a |  |

## Table drivers

The milestone (level 0) and its open driving predecessors, by level then early finish.

Rows: drv.rows, in the order returned, at most 15.
When drv.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of drv).
No rows: write 'No driving predecessor.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Level | level |  | int | n/a |  |
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Early start | early_start |  | date | n/a |  |
| Early finish | early_finish |  | date | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Drives | successor + successor_name |  | id_name | n/a |  |
| Link | type |  | text | n/a |  |
| Lag (d) | lag_d | d | n1 | n/a |  |

## Table contract

Contract milestones by date.

Rows: ct.rows, in the order returned, at most 20.
When ct.next_offset is not null, add the line: Showing the first <returned> of <total> contract milestones. (returned and total of ct).
No rows: write 'No contract milestone found.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Milestone | task_code + task_name |  | id_name | n/a |  |
| Constraint | cstr_label |  | text | none |  |
| Constraint date | cstr_date |  | date | n/a |  |
| Hard | hard_constraint |  | flag | n/a |  |
| Predecessors | predecessor_count | count | int | n/a |  |
| Forecast | date |  | date | n/a |  |
| Forecast - constraint (wd) | vs_constraint_wd | wd | n1 | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Float comes from | float_origin_explanation |  | text | n/a |  |

## Table roots

What starts each driving chain: data_date, constraint, actual_date (progress), open_start (no predecessor), completed_predecessor, unexplained.

Rows: drv.drivers_at_root, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 chain starts are shown.
No rows: write 'No chain start found.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Starts from | type |  | text | n/a |  |
| Date | date |  | date | n/a |  |

## Cross-checks (equal values)

- same data date: ms.schedule_state.data_date = late.schedule_state.data_date
- same data date (driving path): ms.schedule_state.data_date = drv.data_date
- same must finish date: ms.must_finish = late.must_finish
- open milestones = milestones of the open list: ms.counts.open = late.counts.milestones
- same open late milestones: ms.counts.open_late = late.counts.late
- same critical milestones: ms.counts.critical = late.counts.critical
- same total float of the first open milestone: late.rows.0.total_float_d = drv.target.total_float_d
- same data date (contract): ms.schedule_state.data_date = ct.schedule_state.data_date
