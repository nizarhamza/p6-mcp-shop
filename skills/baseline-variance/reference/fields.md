# Fields of Baseline variance

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. sum = p6_project_summary(project="{project}", baseline="{baseline}"): dates, baseline used, finish variance.
2. act = p6_compare_projects(project="{project}", other="{baseline}", section="activities", min_variance_days=1, limit=20): activity summary, slip causes, largest finish variances. If this call returns an error, keep its message as act.error (its other fields are null).
3. rel = p6_compare_projects(project="{project}", other="{baseline}", section="relationships", limit=20): relationships added, removed or with another lag. If this call returns an error, keep its message as rel.error (its other fields are null).
4. pc = p6_progress_curve(project="{project}", baseline="{baseline}"): earned value in units at the data date. If this call returns an error, keep its message as pc.error (its other fields are null).
Leave out an argument whose value is empty (baseline).

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
- {baseline}: Project ID of the baseline or project to compare with (empty: the project baseline), as given

## Units

- wd: working days of each activity's calendar
- wd proj: working days of the project calendar
- cd: calendar days
- d: days of each activity's calendar (hours / hours per day)
- h: hours
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | sum.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | sum.schedule_state.last_schedule_date |  | datetime | n/a | last F9 in P6 |
| stale | sum.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| bl_used | sum.baseline.used |  | text | n/a | baseline compared with (null: none) |
| bl_source | sum.baseline.source |  | text | n/a | how the baseline was chosen |
| bl_data_date | sum.baseline.data_date |  | date | n/a | data date of the baseline |
| finish | sum.dates.scheduled_finish |  | date | n/a | scheduled finish |
| bl_finish | sum.baseline.finish |  | date | n/a | scheduled finish of the baseline |
| fv_cd | sum.baseline.finish_variance_cd | cd | n1 | n/a | finish minus baseline finish |
| fv_wd | sum.baseline.finish_variance_wd | wd proj | n1 | n/a | finish minus baseline finish |
| must_finish | sum.dates.must_finish_by |  | date | n/a | must finish by date |
| mf_cd | sum.dates.finish_vs_must_finish_by_cd | cd | n1 | n/a | finish minus must finish by |
| mf_wd | sum.dates.finish_vs_must_finish_by_wd | wd proj | n1 | n/a | finish minus must finish by |
| matched | act.summary.activities.matched | count | int | n/a | activities in both (Activity ID) |
| added | act.summary.activities.added | count | int | n/a | only in the project |
| removed | act.summary.activities.removed | count | int | n/a | only in the baseline |
| later | act.summary.activities.later | count | int | n/a | matched, finishing later |
| earlier | act.summary.activities.earlier | count | int | n/a | matched, finishing earlier |
| same_finish | act.summary.activities.same_finish | count | int | n/a | matched, same finish |
| later_avg_cd | act.summary.activities.later_avg_cd | cd | n1 | n/a | average variance of the later ones |
| later_max_cd | act.summary.activities.later_max_cd | cd | n1 | n/a | largest finish variance |
| earlier_max_cd | act.summary.activities.earlier_max_cd | cd | n1 | n/a | most negative finish variance |
| status_changed | act.summary.activities.status_changed | count | int | n/a | matched, other status |
| dur_changed | act.summary.activities.orig_dur_changed | count | int | n/a | matched, other original duration |
| name_changed | act.summary.activities.name_changed | count | int | n/a | matched, other name |
| slip_unknown | act.summary.activities.slip_cause_unknown | count | int | n/a | matched, no slip cause (calendar or date missing) |
| rel_matched | rel.summary.relationships.matched | count | int | n/a | relationships in both |
| rel_added | rel.summary.relationships.added | count | int | n/a | only in the project |
| rel_removed | rel.summary.relationships.removed | count | int | n/a | only in the baseline |
| rel_lag_changed | rel.summary.relationships.lag_changed | count | int | n/a | in both, other lag |
| bl_planned | pc.to_date.baseline_planned | h | n1 | n/a | baseline planned units (planned value) |
| earned | pc.to_date.earned | h | n1 | n/a | budget x activity % complete |
| actual | pc.to_date.actual | h | n1 | n/a | actual units |
| ev_variance | pc.to_date.variance | h | n1 | n/a | earned minus baseline planned |
| spi | pc.to_date.spi |  | n2 | n/a | earned / baseline planned |
| spi_actual | pc.to_date.spi_actual |  | n2 | n/a | actual / baseline planned |
| act_error | act.error |  | text | n/a | error of act (null: it worked) |
| rel_error | rel.error |  | text | n/a | error of rel (null: it worked) |
| pc_error | pc.error |  | text | n/a | error of pc (null: it worked) |

## Table causes

Matched activities per slip cause.

Rows: act.summary.activities.slip_causes, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 causes are shown.
No rows: write 'No matched activity.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Slip cause | _key |  | text | n/a |  |
| Activities | _value | count | int | n/a |  |

## Table moved

Added and removed first, then matched ones moved by 1 cd or more, largest absolute variance first.

Rows: act.rows, in the order returned, at most 20.
When act.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of act).
No rows: write 'No activity moved by 1 calendar day or more.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + name |  | id_name | n/a |  |
| Change | change |  | text | n/a |  |
| Status | status |  | text | n/a |  |
| BL start | other_start |  | date | n/a |  |
| Start | start |  | date | n/a |  |
| Start var (wd) | start_variance_wd | wd | n1 | n/a |  |
| BL finish | other_finish |  | date | n/a |  |
| Finish | finish |  | date | n/a |  |
| Finish var (cd) | variance_cd | cd | n1 | n/a |  |
| Finish var (wd) | variance_wd | wd | n1 | n/a |  |
| Duration delta (wd) | duration_delta_wd | wd | n1 | n/a |  |
| Slip cause | slip_cause |  | text | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |

## Table links

Added, lag_changed, then removed; by successor, predecessor, type.

Rows: rel.rows, in the order returned, at most 20.
When rel.next_offset is not null, add the line: Showing the first <returned> of <total> relationship changes. (returned and total of rel).
No rows: write 'No relationship added, removed or with another lag.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Change | change |  | text | n/a |  |
| Predecessor | pred_code + pred_name |  | id_name | n/a |  |
| Successor | succ_code + succ_name |  | id_name | n/a |  |
| Type | type |  | text | n/a |  |
| Predecessor project | pred_project |  | text | same |  |
| Lag (d) | lag_d | d | n1 | n/a |  |
| BL lag (d) | other_lag_d | d | n1 | n/a |  |

## Cross-checks (equal values)

- same data date: sum.schedule_state.data_date = act.schedule_state.data_date = rel.schedule_state.data_date = pc.schedule_state.data_date
- same baseline: sum.baseline.used = act.other = rel.other = pc.baseline.project
- same project finish: sum.dates.scheduled_finish = act.projects.scd_end_date.project
- same baseline finish: sum.baseline.finish = act.projects.scd_end_date.other
- same SPI: sum.baseline.spi_units = pc.to_date.spi
- same relationships matched: act.summary.relationships.matched = rel.summary.relationships.matched
