# Fields of Progress and earned value

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. sum = p6_project_summary(project="{project}", baseline="{baseline}"): % complete by every method, baseline used, schedule state.
2. pc = p6_progress_curve(project="{project}", period="{period}", baseline="{baseline}"): earned value at the data date and the S-curve periods. If this call returns an error, keep its message as pc.error (its other fields are null).
3. wbs = p6_list_wbs(project="{project}", max_depth=1, baseline="{baseline}", limit=30): units % and baseline planned % per level 1 WBS node.
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
- {baseline}: Project ID of the baseline (empty: the project baseline), as given
- {period}: S-curve period: month or week, as given

## Units

- h: hours
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | sum.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | sum.schedule_state.last_schedule_date |  | datetime | n/a | last F9 in P6 |
| stale | sum.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| bl_used | sum.baseline.used |  | text | n/a | baseline used (null: none) |
| units_pct | sum.percent_complete.units | % | pct1 | n/a | actual / at completion units (P6 units % complete) |
| physical_pct | sum.percent_complete.physical | % | pct1 | n/a | physical % weighted by budget units |
| duration_pct | sum.percent_complete.duration | % | pct1 | n/a | (original - remaining) / original duration, tasks only |
| completed_pct | sum.percent_complete.activities_completed | % | pct1 | n/a | completed / all activities |
| budget_units | sum.percent_complete.budget_units | h | n1 | n/a | budget units of the activities |
| actual_units | sum.percent_complete.actual_units | h | n1 | n/a | actual units of the activities |
| remaining_units | sum.percent_complete.remaining_units | h | n1 | n/a | remaining units of the activities |
| mismatch | sum.percent_complete.units_vs_physical_mismatch | count | int | n/a | activities whose physical % and units % differ |
| pct_type | sum.percent_complete.activity_percent_type |  | text | n/a | default percent complete type of the project |
| bl_planned_pct | sum.baseline.planned_units_pct_at_data_date | % | pct1 | n/a | baseline planned / baseline budget units at the data date |
| bl_planned | pc.to_date.baseline_planned | h | n1 | n/a | baseline planned units (planned value) |
| planned | pc.to_date.planned | h | n1 | n/a | planned units on the current planned dates |
| actual | pc.to_date.actual | h | n1 | n/a | actual units of the assignments |
| actual_pct | pc.to_date.actual_pct | % | pct1 | n/a | actual / budget units |
| earned | pc.to_date.earned | h | n1 | n/a | budget x activity % complete |
| earned_pct | pc.to_date.earned_pct | % | pct1 | n/a | earned / budget units |
| ev_variance | pc.to_date.variance | h | n1 | n/a | earned minus baseline planned |
| spi | pc.to_date.spi |  | n2 | n/a | earned / baseline planned |
| spi_actual | pc.to_date.spi_actual |  | n2 | n/a | actual / baseline planned |
| budget | pc.measure.budget | h | n1 | n/a | budget units of the assignments |
| at_completion | pc.measure.at_completion | h | n1 | n/a | actual plus remaining units of the assignments |
| period_count | pc.period_count | count | int | n/a | periods of the S-curve |
| clipped | pc.checks.clipped_actuals | count | int | n/a | assignments with actual dates after the data date |
| clamped | pc.checks.clamped_remaining | count | int | n/a | assignments whose remaining start is before the data date |
| ev_other | pc.checks.wbs_other_ev_technique | count | int | n/a | WBS nodes with another earned value technique |
| pc_error | pc.error |  | text | n/a | error of pc (null: it worked) |

## Table periods

One row per period from the first assignment date; quantities of the period, cumulative % of each curve's budget.

Rows: pc.periods, in the order returned, at most 36 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 36 items, add the line: Only the first 36 periods are shown.
No rows: write 'No period.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Period | period |  | text | n/a |  |
| Baseline (h) | baseline | h | n1 | n/a |  |
| Baseline cum % | baseline_pct | % | pct1 | n/a |  |
| Planned (h) | planned | h | n1 | n/a |  |
| Planned cum % | planned_pct | % | pct1 | n/a |  |
| Actual (h) | actual | h | n1 | n/a |  |
| Actual cum % | actual_pct | % | pct1 | n/a |  |
| Forecast (h) | forecast | h | n1 | n/a |  |
| Forecast cum % | forecast_pct | % | pct1 | n/a |  |

## Table wbs

The project node, then the level 1 WBS nodes in P6 order; figures of the whole subtree.

Rows: wbs.rows, in the order returned, at most 30.
When wbs.next_offset is not null, add the line: Showing the first <returned> of <total> WBS nodes. (returned and total of wbs).
No rows: write 'No WBS node.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| WBS | wbs_code + wbs_name |  | id_name | n/a |  |
| Units % | rollup.units_pct | % | pct1 | n/a |  |
| BL planned % | rollup.bl_planned_pct | % | pct1 | n/a |  |
| Budget units (h) | rollup.budget_units | h | n1 | n/a |  |
| Actual units (h) | rollup.actual_units | h | n1 | n/a |  |
| Finish | rollup.finish |  | date | n/a |  |

## Cross-checks (equal values)

- same data date: sum.schedule_state.data_date = pc.schedule_state.data_date
- same baseline: sum.baseline.used = pc.baseline.project = wbs.baseline.project
- same SPI: sum.baseline.spi_units = pc.to_date.spi
- same budget units: sum.percent_complete.budget_units = wbs.root.rollup.budget_units
- same actual units: sum.percent_complete.actual_units = wbs.root.rollup.actual_units
