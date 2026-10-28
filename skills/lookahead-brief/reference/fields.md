# Fields of Look-ahead brief

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. crit = p6_lookahead(project="{project}", weeks={weeks}, critical_only=true, limit=30): critical activities of the window.
2. all = p6_lookahead(project="{project}", weeks={weeks}, limit=50): every activity of the window, weeks, counts, data date.

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
- {weeks}: Look-ahead length in weeks from the data date (1 to 52), as given

## Units

- d: days of each activity's calendar (hours / hours per day)
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | all.data_date |  | date | n/a | data date of the project |
| last_f9 | all.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | all.schedule_state.stale |  | flag | n/a | this server changed the project after the last F9 |
| window_from | all.window.from |  | datetime | n/a | start of the window (the data date) |
| window_to | all.window.to |  | datetime | n/a | end of the window, excluded |
| window_days | all.window.days | count | int | n/a | length of the window in calendar days |
| listed | all.total | count | int | n/a | activities of the window (LOE and WBS summary left out) |
| in_progress | all.counts.in_progress | count | int | n/a | activities in progress |
| starting | all.counts.starting | count | int | n/a | not started activities starting in the window |
| finishing | all.counts.finishing | count | int | n/a | open activities finishing in the window |
| spanning | all.counts.spanning | count | int | n/a | not started activities starting before and finishing after the window |
| critical | all.counts.critical | count | int | n/a | critical open activities of the window |
| critical_definition | all.critical_definition |  | text | n/a | the project's definition of critical |

## Table weeks

The weeks of the window: 7 calendar days each from the window start, the last one cut at the window end.

Rows: all.weeks, in the order returned, at most 13 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 13 items, add the line: Only the first 13 weeks are shown.
No rows: write 'No week in the window.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Week | week |  | int | n/a |  |
| From | from |  | datetime | n/a |  |
| To (excluded) | to |  | datetime | n/a |  |

## Table critical

Critical open activities of the window, by forecast start, then finish, then Activity ID.

Rows: crit.rows, in the order returned, at most 30.
When crit.next_offset is not null, add the line: Showing the first <returned> of <total> critical activities. (returned and total of crit).
No rows: write 'No critical activity in the window.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Categories | window |  | list | n/a |  |
| Forecast start | fcst_start |  | date | n/a |  |
| Forecast finish | fcst_finish |  | date | n/a |  |
| Start week | start_week |  | int | outside |  |
| Finish week | finish_week |  | int | outside |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Critical | critical |  | flag | n/a |  |

## Table all

Every activity of the window, by forecast start, then finish, then Activity ID.

Rows: all.rows, in the order returned, at most 50.
When all.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of all).
No rows: write 'No activity in the window.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Categories | window |  | list | n/a |  |
| Forecast start | fcst_start |  | date | n/a |  |
| Forecast finish | fcst_finish |  | date | n/a |  |
| Start week | start_week |  | int | outside |  |
| Finish week | finish_week |  | int | outside |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Critical | critical |  | flag | n/a |  |

## Cross-checks (equal values)

- same data date in both look-aheads and the schedule state: crit.data_date = all.data_date = all.schedule_state.data_date
- same window start: crit.window.from = all.window.from
- same window end: crit.window.to = all.window.to
- critical activities listed = critical count of the window: crit.total = all.counts.critical
