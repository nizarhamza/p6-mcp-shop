# Fields of Float and near-critical

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. fa = p6_float_analysis(project="{project}"): float statistics and distribution of the open activities, data date.
2. fp = p6_float_paths(project="{project}", limit=30): float paths of the last F9: summary per path and the activities in path order.
3. nc = p6_critical_path(project="{project}", float_threshold_days={near_days}, min_float_days=0, limit=30): near-critical activities: total float above 0 and at or below near_days; project counts.

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
- {near_days}: Near-critical threshold: total float above 0 and at or below this many days (each activity's calendar); 10 when the user gives none, as given

## Units

- d: days of each activity's calendar (hours / hours per day)
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | fa.schedule_state.data_date |  | date | n/a | data date of the project |
| last_f9 | fa.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | fa.schedule_state.stale |  | flag | n/a | this server changed the project after the last F9 |
| activities | fa.scope.activities | count | int | n/a | open activities analysed: not completed, LOE and WBS summary left out |
| no_tf | fa.no_value.total_float | count | int | n/a | open activities without a total float |
| tf_min | fa.stats.tf_min_d | d | n1 | n/a | lowest total float |
| tf_max | fa.stats.tf_max_d | d | n1 | n/a | highest total float |
| tf_mean | fa.stats.tf_mean_d | d | n1 | n/a | mean total float |
| tf_median | fa.stats.tf_median_d | d | n1 | n/a | median total float |
| negative | fa.stats.negative_tf | count | int | n/a | open activities with negative total float |
| zero | fa.stats.zero_tf | count | int | n/a | open activities with total float exactly 0 |
| critical | fa.stats.critical | count | int | n/a | critical open activities under the project's definition |
| critical_definition | fa.stats.critical_definition |  | text | n/a | the project's definition of critical |
| tf_not_whole | fa.stats.tf_not_whole_days | count | int | n/a | total floats that are not a whole number of days |
| ranges_covered | fa.all_ranges_covered |  | flag | n/a | range counts plus activities without float equal the activities analysed |
| fp_source | fp.source |  | text | n/a | float_path (P6 multiple float paths) or driving_path_flag (no float path stored) |
| longest_path | nc.counts.longest_path | count | int | n/a | open activities on the longest path (driving path flag) |
| within_near | nc.counts.total_float | count | int | n/a | open activities with total float at or below near_days, critical included |
| near_total | nc.total | count | int | n/a | near-critical activities: total float above 0 and at or below near_days |
| near_definition | nc.definition |  | text | n/a | the threshold used by the near-critical table |

## Table buckets

Float ranges in days: below the first edge, [a, b) below zero, exactly 0, (a, b] above zero, above the last edge.

Rows: fa.buckets, in the order returned, at most 12 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 12 items, add the line: Only the first 12 ranges are shown.
No rows: write 'No open activity.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Range (d) | label | d | text | n/a |  |
| Total float | total_float | count | int | n/a |  |
| Total float % | tf_pct | % | pct1 | n/a |  |
| Free float | free_float | count | int | n/a |  |
| Free float % | ff_pct | % | pct1 | n/a |  |

## Table paths

One row per float path (1 = the most critical), over every page.

Rows: fp.paths, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 float paths are shown.
No rows: write 'P6 stored no float paths for this project: the next table lists the longest path activities (driving path flag) by start.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Path | path |  | int | n/a |  |
| Activities | activities | count | int | n/a |  |
| Min total float (d) | min_tf_d | d | n1 | n/a |  |
| Max total float (d) | max_tf_d | d | n1 | n/a |  |
| Finish | finish |  | date | n/a |  |

## Table path_rows

Open activities of the float paths in P6 order: path, then order on the path.

Rows: fp.rows, in the order returned, at most 30.
When fp.next_offset is not null, add the line: Showing the first <returned> of <total> float path activities. (returned and total of fp).
No rows: write 'No open activity on a float path.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Path | float_path |  | int | none |  |
| Order | float_path_order |  | int | none |  |
| Activity | task_code + task_name |  | id_name | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Early start | early_start_date |  | date | n/a |  |
| Early finish | early_end_date |  | date | n/a |  |

## Table near

Near-critical activities: total float above 0 and at or below near_days, by total float then start.

Rows: nc.rows, in the order returned, at most 30.
When nc.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of nc).
No rows: write 'No open activity with total float above 0 and at or below this threshold.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Free float (d) | free_float_d | d | n1 | n/a |  |
| Remaining duration (d) | rem_dur_d | d | n1 | n/a |  |
| Early finish | early_end_date |  | date | n/a |  |
| Float path | float_path |  | int | none |  |

## Cross-checks (equal values)

- same data date in the three calls: fa.schedule_state.data_date = fp.schedule_state.data_date = nc.schedule_state.data_date
- same number of open activities: fa.scope.activities = nc.counts.open
- same negative float count: fa.stats.negative_tf = nc.counts.negative_float
