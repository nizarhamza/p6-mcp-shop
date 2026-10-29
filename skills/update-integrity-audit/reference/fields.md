# Fields of Update integrity audit

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. ui = p6_update_integrity(project="{project}", other="{previous}", sample_size=10): every flag: count, up to 10 rows.
2. cmp = p6_compare_projects(project="{project}", other="{previous}", section="activities", limit=1): both data dates again (cross-check).

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

- {project}: Project ID of the update to review, as given
- {previous}: Project ID of the previous update (or a baseline saved from it), as given

## Units

- wd proj: working days of the project calendar
- cd: calendar days
- d: days of each activity's calendar (hours / hours per day)
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | ui.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | ui.schedule_state.last_schedule_date |  | datetime | n/a | last F9 of the update |
| stale | ui.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| dd_before | ui.data_date.before |  | date | n/a | previous data date |
| dd_delta | ui.data_date.delta_cd | cd | n1 | n/a | data date moved by |
| raised | ui.raised_count | count | int | n/a | flags with a count |
| n_open_end | ui.summary.open_end_to_finish | count | int | n/a | flag count |
| n_neg | ui.summary.negative_float_cleared_by_constraint | count | int | n/a | flag count |
| n_must | ui.summary.must_finish_moved | count | int | n/a | flag count |
| n_act | ui.summary.actuals_changed | count | int | n/a | flag count |
| n_cut | ui.summary.duration_cut | count | int | n/a | flag count |
| n_cut_crit | ui.flags.duration_cut.critical | count | int | n/a | critical before |
| n_links | ui.summary.links_removed_on_critical | count | int | n/a | flag count |
| n_rel | ui.summary.rel_type_or_lag_changed | count | int | n/a | flag count |
| n_opt | ui.summary.schedule_options_changed | count | int | n/a | flag count |
| n_cal | ui.summary.calendars_changed | count | int | n/a | flag count |
| n_del | ui.summary.deleted_in_progress_or_critical | count | int | n/a | flag count |
| n_dd | ui.summary.data_date | count | int | n/a | 1: did not advance |
| must_before | ui.must_finish.before |  | datetime | none | previous must finish |
| must_after | ui.must_finish.after |  | datetime | none | must finish now |
| must_wd | ui.must_finish.delta_wd | wd proj | n1 | n/a | must finish moved by |
| caveat | ui.caveat |  | text | n/a | what a flag is and is not |

## Table summary

Rows: ui.summary, in the order returned, at most 11 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 11 items, add the line: Only the first 11 flags are shown.
No rows: write 'No flag.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Flag | _key |  | text | n/a |  |
| Count | _value | count | int | n/a |  |

## Table t_open_end

Rows: ui.flags.open_end_to_finish.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Had no | side |  | text | n/a |  |
| Now linked to | linked_to + linked_to_name |  | id_name | n/a |  |

## Table t_neg

Rows: ui.flags.negative_float_cleared_by_constraint.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Float before (d) | total_float_before_d | d | n1 | n/a |  |
| Float now (d) | total_float_after_d | d | n1 | n/a |  |
| Cause | cause |  | text | n/a |  |

## Table t_act

Rows: ui.flags.actuals_changed.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Date | field |  | text | n/a |  |
| Before | before |  | datetime | none |  |
| Now | after |  | datetime | none |  |

## Table t_cut

Rows: ui.flags.duration_cut.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Original before (d) | original_before_d | d | n1 | n/a |  |
| Original now (d) | original_after_d | d | n1 | n/a |  |
| Remaining before (d) | remaining_before_d | d | n1 | n/a |  |
| Remaining now (d) | remaining_after_d | d | n1 | n/a |  |

## Table t_links

Rows: ui.flags.links_removed_on_critical.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Predecessor | pred_code + pred_name |  | id_name | n/a |  |
| Successor | succ_code + succ_name |  | id_name | n/a |  |
| Type | type |  | text | n/a |  |
| Successor float before (d) | successor_total_float_before_d | d | n1 | n/a |  |

## Table t_rel

Rows: ui.flags.rel_type_or_lag_changed.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Predecessor | pred_code + pred_name |  | id_name | n/a |  |
| Successor | succ_code + succ_name |  | id_name | n/a |  |
| Change | change |  | text | n/a |  |
| Before | before |  | text | n/a |  |
| Now | after |  | text | n/a |  |

## Table t_opt

Rows: ui.flags.schedule_options_changed.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Option | option |  | text | n/a |  |
| Before | before |  | text | not stored |  |
| Now | after |  | text | not stored |  |

## Table t_cal

Rows: ui.flags.calendars_changed.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity or calendar | item + item_name |  | id_name | n/a |  |
| Before | before |  | text | n/a |  |
| Now | after |  | text | n/a |  |
| Detail | detail |  | text | n/a |  |

## Table t_del

Rows: ui.flags.deleted_in_progress_or_critical.sample, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 rows are shown.
No rows: write 'None.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status before | status_before |  | text | n/a |  |
| Float before (d) | total_float_before_d | d | n1 | n/a |  |
| Critical before | critical_before |  | flag | n/a |  |

## Cross-checks (equal values)

- same data date of the update: ui.data_date.after = ui.schedule_state.data_date = cmp.projects.last_recalc_date.project
- same data date of the previous update: ui.data_date.before = cmp.projects.last_recalc_date.other
