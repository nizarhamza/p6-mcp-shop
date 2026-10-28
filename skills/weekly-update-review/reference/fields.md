# Fields of Weekly update review

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. sum = p6_project_summary(project="{project}"): data date, percent complete, finish dates, baseline.
2. prog = p6_progress_check(project="{project}", sample_size=5): out of sequence links, status checks.
3. cp = p6_critical_path(project="{project}", limit=15): critical open activities.
4. la = p6_lookahead(project="{project}", weeks={weeks}, critical_only=true, limit=20): critical activities of the look-ahead window.
5. cmp = p6_compare_projects(project="{project}", section="activities", min_variance_days=5, limit=15): slippage against the project baseline. If this call returns an error, keep its message as cmp.error (its other fields are null).

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
- {weeks}: Weeks of the critical look-ahead window from the data date, as given

## Units

- wd: working days of each activity's calendar
- wd proj: working days of the project calendar
- cd: calendar days
- d: days of each activity's calendar (hours / hours per day)
- %: percent

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | sum.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | sum.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) |
| stale | sum.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| units_pct | sum.percent_complete.units | % | pct1 | n/a | units % complete, labor and nonlabor |
| physical_pct | sum.percent_complete.physical | % | pct1 | n/a | physical % weighted by budget units |
| duration_pct | sum.percent_complete.duration | % | pct1 | n/a | duration % complete |
| completed_pct | sum.percent_complete.activities_completed | % | pct1 | n/a | completed / all activities |
| mismatch | sum.percent_complete.units_vs_physical_mismatch |  | int | n/a | activities whose physical % and units % differ |
| bl_planned_pct | sum.baseline.planned_units_pct_at_data_date | % | pct1 | n/a | baseline planned units % at the data date |
| spi_units | sum.baseline.spi_units |  | n2 | n/a | earned units / baseline planned units |
| scheduled_finish | sum.dates.scheduled_finish |  | date | n/a | scheduled finish |
| must_finish | sum.dates.must_finish_by |  | date | n/a | must finish by |
| vs_must_cd | sum.dates.finish_vs_must_finish_by_cd | cd | n1 | n/a | scheduled finish minus must finish by |
| vs_must_wd | sum.dates.finish_vs_must_finish_by_wd | wd proj | n1 | n/a | the same in working days |
| baseline_used | sum.baseline.used |  | text | n/a | baseline used (null: none) |
| vs_bl_cd | sum.baseline.finish_variance_cd | cd | n1 | n/a | scheduled finish minus the baseline's |
| vs_bl_wd | sum.baseline.finish_variance_wd | wd proj | n1 | n/a | the same in working days |
| cp_definition | cp.definition |  | text | n/a | definition of critical |
| critical | cp.total |  | int | n/a | critical open activities |
| neg_float | cp.counts.negative_float |  | int | n/a | open activities with negative float |
| cmp_error | cmp.error |  | text | n/a | error of the comparison (no baseline) |
| later | cmp.summary.activities.later |  | int | n/a | matched activities finishing later |
| earlier | cmp.summary.activities.earlier |  | int | n/a | matched activities finishing earlier |
| oos_links | prog.out_of_sequence_total.links |  | int | n/a | out of sequence links |
| logic_mode | prog.logic_option.mode |  | text | n/a | out of sequence option of F9 |
| chk_active | prog.status_checks.active_without_start.count |  | int | n/a | in progress, no actual start |
| chk_complete | prog.status_checks.complete_with_remaining_or_no_finish.count |  | int | n/a | completed, remaining duration or no actual finish |
| chk_after_dd | prog.status_checks.actual_after_data_date.count |  | int | n/a | actual dates after the data date |
| la_from | la.window.from |  | datetime | n/a | window start |
| la_to | la.window.to |  | datetime | n/a | window end (excluded) |
| la_critical | la.counts.critical |  | int | n/a | critical activities in the window |
| la_in_progress | la.counts.in_progress |  | int | n/a | of them in progress |
| la_starting | la.counts.starting |  | int | n/a | of them starting in the window |
| la_finishing | la.counts.finishing |  | int | n/a | of them finishing in the window |

## Table critical

Rows: cp.rows, in the order returned, at most 15.
When cp.next_offset is not null, add the line: Showing the first <returned> of <total> critical activities. (returned and total of cp).
No rows: write 'No critical open activity.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Early start | early_start_date |  | date | n/a |  |
| Early finish | early_end_date |  | date | n/a |  |
| Remaining (d) | rem_dur_d | d | n1 | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |

## Table slip_causes

Rows: cmp.summary.activities.slip_causes, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 causes are shown.
No rows: write 'No matched activity.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Cause | _key |  | text | n/a |  |
| Activities | _value |  | int | n/a |  |

## Table slipped

Rows: cmp.rows, in the order returned, at most 15.
When cmp.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of cmp).
No rows: write 'No activity moved by 5 calendar days or more.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + name |  | id_name | n/a |  |
| Change | change |  | text | n/a |  |
| Finish | finish |  | date | n/a |  |
| Baseline finish | other_finish |  | date | n/a |  |
| Finish variance (wd) | variance_wd | wd | n1 | n/a |  |
| Start variance (wd) | start_variance_wd | wd | n1 | n/a |  |
| Duration delta (wd) | duration_delta_wd | wd | n1 | n/a |  |
| Cause | slip_cause |  | text | n/a |  |

## Table oos

Rows: prog.out_of_sequence, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 link types are shown.
No rows: write 'No link checked.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Type | _key |  | text | n/a |  |
| Links | links |  | int | n/a |  |
| Successors | successors |  | int | n/a |  |

## Table status_checks

Rows: prog.status_checks, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 checks are shown.
No rows: write 'No check ran.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Check | _key |  | text | n/a |  |
| Activities | count |  | int | n/a |  |

## Table lookahead

Rows: la.rows, in the order returned, at most 20.
When la.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of la).
No rows: write 'No critical activity in the window.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| In the window | window |  | list | n/a |  |
| Forecast start | fcst_start |  | date | n/a |  |
| Forecast finish | fcst_finish |  | date | n/a |  |
| Start week | start_week |  | int | outside |  |
| Finish week | finish_week |  | int | outside |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |

## Cross-checks (equal values)

- same data date: sum.schedule_state.data_date = prog.schedule_state.data_date = cp.schedule_state.data_date = la.schedule_state.data_date
- same last F9: sum.schedule_state.last_schedule_date = cp.schedule_state.last_schedule_date = la.schedule_state.last_schedule_date
- same critical count: sum.critical.critical = cp.total
- same negative float count: sum.critical.negative_float = cp.counts.negative_float
- same baseline: sum.baseline.used = cmp.other
