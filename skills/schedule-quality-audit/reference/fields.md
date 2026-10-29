# Fields of Schedule quality audit

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. cv = p6_cpm_validate(project="{project}", limit=5): engine against the last F9: the critical path test relies on it.
2. hc = p6_health_check(project="{project}"): full DCMA 14 run: checks, score, thresholds, baseline (saves a snapshot).
3. tr = p6_health_check_compare(project="{project}", before="previous", after="latest"): trend since the previous audit (fails when there is none). If this call returns an error, keep its message as tr.error (its other fields are null).
4. dg = p6_dangling(project="{project}", limit=15): open starts and open finishes with a suggested link.
5. rd = p6_redundant_links(project="{project}", limit=15): links that are candidates for removal.
6. fa = p6_float_analysis(project="{project}"): total and free float distribution of the open activities.
7. fo_neg = p6_float_origin(project="{project}", task_code=<hc.checks.negative_float.worst.task_code>, limit=1): where the lowest negative float comes from. <hc.checks.negative_float.worst.task_code> is the field checks.negative_float.worst.task_code of the result of hc: when it is null or missing, skip this call (its fields are null).
8. fo_high = p6_float_origin(project="{project}", task_code=<hc.checks.high_float.worst.task_code>, limit=1): where the highest float comes from. <hc.checks.high_float.worst.task_code> is the field checks.high_float.worst.task_code of the result of hc: when it is null or missing, skip this call (its fields are null).

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

## Units

- d: days of each activity's calendar (hours / hours per day)
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | hc.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | hc.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | hc.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| score_passed | hc.score.passed | count | int | n/a | checks passed |
| score_failed | hc.score.failed | count | int | n/a | checks failed |
| score_not_evaluated | hc.score.not_evaluated | count | int | n/a | checks not evaluated (no threshold or no data) |
| score_evaluated | hc.score.evaluated | count | int | n/a | checks passed or failed |
| score_pct | hc.score.pct_passed | % | pct1 | n/a | passed / evaluated checks |
| threshold_source | hc.threshold_source |  | text | n/a | PROJPROP schedule_check or DCMA defaults |
| baseline | hc.baseline.project |  | text | n/a | baseline of missed tasks and BEI |
| open_activities | hc.open_incomplete_activities | count | int | n/a | open activities: not completed, LOE and WBS summary left out |
| cpt_activity | hc.['checks.critical_path_test.activity', 'checks.critical_path_test.activity_name'] |  | id_name | n/a | activity delayed by the critical path test |
| lags | hc.checks.lags.count | count | int | n/a | links (open successor) with a positive lag |
| high_float | hc.checks.high_float.count | count | int | n/a | open activities above the high float limit |
| missed | hc.checks.missed_tasks.count | count | int | n/a | baseline activities due that are missed |
| trend_error | tr.error |  | text | n/a | why there is no trend (null when there is one) |
| dangling | dg.total | count | int | n/a | open starts plus open finishes (an activity with both counts twice) |
| redundant | rd.total | count | int | n/a | links that are candidates for removal |
| red_side_effects | rd.side_effects.count | count | int | n/a | open activities left without predecessor or successor if all were removed |
| tf_min | fa.stats.tf_min_d | d | n1 | n/a | lowest total float |
| tf_max | fa.stats.tf_max_d | d | n1 | n/a | highest total float |
| tf_negative | fa.stats.negative_tf | count | int | n/a | open activities with negative total float |
| critical | fa.stats.critical | count | int | n/a | critical open activities |
| critical_definition | fa.stats.critical_definition |  | text | n/a | the project's definition of critical |
| match_rate | cv.match_rate |  | n2 | n/a | share of open activities the engine reproduces (1.00 = all) |
| trusted | cv.trusted |  | flag | n/a | match rate at least 0.99 |
| w_points | hc.weighted_score.points |  | n1 | n/a | weighted score out of 100 |
| w_grade | hc.weighted_score.grade |  | text | n/a | grade A to F |
| logic_count | hc.checks.logic.count | count | int | n/a | open activities without predecessor or successor |
| fs_pass | hc.checks.fs_links.pass |  | flag | n/a | fs_links passes |
| neg_expl | fo_neg.explanation |  | text | n/a | where the lowest negative float comes from |
| high_expl | fo_high.explanation |  | text | n/a | where the highest float comes from |

## Table dcma

One row per check, in the order returned (DCMA 14 with logic_density, then key_dates, information only); Value for logic_density, cpli and bei.

Rows: hc.checks, in the order returned, at most 17 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 17 items, add the line: Only the first 17 checks are shown.
No rows: write 'No check returned.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Check | _key |  | text | n/a |  |
| Count | count | count | int | n/a |  |
| Out of | denominator | count | int | n/a |  |
| % | pct | % | pct1 | n/a |  |
| Value | value |  | n2 | n/a |  |
| Threshold | threshold |  | n2 | none |  |
| Pass | pass |  | flag | not evaluated |  |

## Table trend

One row per check: count at the previous audit and now, change, pass now.

Rows: tr.checks, in the order returned, at most 17 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 17 items, add the line: Only the first 17 checks are shown.
No rows: write 'No check to compare.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Check | _key |  | text | n/a |  |
| Count before | count.before | count | int | n/a |  |
| Count now | count.after | count | int | n/a |  |
| Change | count.delta | count | int | n/a |  |
| Pass now | pass.after |  | flag | not evaluated |  |

## Table dangling

Open starts first, then open finishes, by Activity ID.

Rows: dg.rows, in the order returned, at most 15.
When dg.next_offset is not null, add the line: Showing the first <returned> of <total> dangling ends. (returned and total of dg).
No rows: write 'No dangling start or finish.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Open | kind |  | text | n/a |  |
| Activity | task_code + task_name |  | id_name | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Suggested link | suggestion.reason |  | text | n/a |  |

## Table redundant

By first category, then successor and predecessor ID; every category of the link.

Rows: rd.rows, in the order returned, at most 15.
When rd.next_offset is not null, add the line: Showing the first <returned> of <total> candidate links. (returned and total of rd).
No rows: write 'No redundant link.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Predecessor | predecessor + predecessor_name |  | id_name | n/a |  |
| Successor | successor + successor_name |  | id_name | n/a |  |
| Type | type |  | text | n/a |  |
| Lag (d) | lag_d | d | n1 | n/a |  |
| Categories | categories |  | list | n/a |  |
| Drives | drives |  | flag | n/a |  |

## Table weighted

Weighted checks: pass earns the weight, warn half, fail 0; not evaluated left out.

Rows: hc.weighted_score.checks, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 checks are shown.
No rows: write 'No weighted check.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Check | _key |  | text | n/a |  |
| Weight | weight |  | int | n/a |  |
| Status | status |  | text | n/a |  |
| Earned | earned |  | n1 | left out |  |

## Table float

Total and free float of the open activities per range of days.

Rows: fa.buckets, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 float ranges are shown.
No rows: write 'No open activity.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Range (d) | label | d | text | n/a |  |
| Total float | total_float | count | int | n/a |  |
| Total float % | tf_pct | % | pct1 | n/a |  |
| Free float | free_float | count | int | n/a |  |
| Free float % | ff_pct | % | pct1 | n/a |  |

## Cross-checks (equal values)

- same data date in every call: cv.schedule_state.data_date = hc.schedule_state.data_date = dg.schedule_state.data_date = rd.schedule_state.data_date = fa.schedule_state.data_date
- same open activities: hc.open_incomplete_activities = fa.scope.activities
- same negative float count: hc.checks.negative_float.count = fa.stats.negative_tf
- same open starts: hc.checks.logic.dangling.open_start.count = dg.counts.start
- same open finishes: hc.checks.logic.dangling.open_finish.count = dg.counts.finish
