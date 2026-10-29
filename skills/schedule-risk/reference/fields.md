# Fields of Schedule risk (Monte Carlo)

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. cv = p6_cpm_validate(project="{project}", limit=5): the engine against the last F9: the simulation runs on it.
2. rk = p6_schedule_risk(project="{project}", iterations={iterations}, seed={seed}, limit=15): Monte Carlo: finish percentiles, chances, milestones, drivers, weeks.

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
- {iterations}: Monte Carlo iterations (100 to 5000), as given
- {seed}: Random seed: the same seed gives the same result, as given

## Units

- wd: working days of each activity's calendar
- wd proj: working days of the project calendar
- d: days of each activity's calendar (hours / hours per day)
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | rk.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | rk.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | rk.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| match_rate | cv.match_rate |  | n2 | n/a | share of open activities the engine reproduces (1.00 = all) |
| trusted | cv.trusted |  | flag | n/a | match rate at least 0.99 |
| det_finish | rk.deterministic.finish |  | datetime | n/a | finish of the engine with unchanged durations |
| det_activity | rk.['deterministic.finish_activity', 'deterministic.finish_activity_name'] |  | id_name | n/a | finish activity |
| stored_finish | rk.deterministic.stored_finish |  | datetime | n/a | finish of the last F9 |
| p10 | rk.finish.p10 |  | datetime | n/a | finish reached in 10 % of the iterations |
| p50 | rk.finish.p50 |  | datetime | n/a | finish reached in 50 % |
| p80 | rk.finish.p80 |  | datetime | n/a | finish reached in 80 % |
| p90 | rk.finish.p90 |  | datetime | n/a | finish reached in 90 % |
| must_finish | rk.must_finish |  | datetime | none | must finish by date |
| on_time_det | rk.on_time_probability.deterministic_pct | % | pct1 | n/a | iterations finishing by the deterministic finish |
| on_time_must | rk.on_time_probability.must_finish_pct | % | pct1 | n/a | iterations finishing by the must finish date |
| p80_buffer | rk.p80_buffer_wd | wd proj | n1 | n/a | deterministic finish to p80 |
| iterations_run | rk.iterations | count | int | n/a | iterations run |
| iterations_note | rk.iterations_note |  | text | n/a | why fewer or other iterations ran (null: as asked) |
| seed_used | rk.seed |  | int | n/a | random seed |
| engine_version | rk.engine_version |  | int | n/a | version of the engine's rules |
| d_min | rk.distribution.default.min_pct | % | n0 | n/a | default range: minimum, % of the remaining duration |
| d_mode | rk.distribution.default.mode_pct | % | n0 | n/a | most likely |
| d_max | rk.distribution.default.max_pct | % | n0 | n/a | maximum |
| n_drawn | rk.distribution.counts.drawn | count | int | n/a | activities whose remaining duration is drawn |
| caveat | rk.caveat |  | text | n/a | what the estimate leaves out |

## Table milestones

The finish activity, then the open constrained activities.

Rows: rk.milestones, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 milestones are shown.
No rows: write 'No milestone.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Deterministic | deterministic |  | datetime | n/a |  |
| P50 | p50 |  | datetime | n/a |  |
| P80 | p80 |  | datetime | n/a |  |
| P90 | p90 |  | datetime | n/a |  |
| On time % | on_time_pct | % | pct1 | n/a |  |
| Constraint date | constraint_date |  | datetime | none |  |
| By constraint % | by_constraint_pct | % | pct1 | n/a |  |
| P80 buffer (wd) | p80_buffer_wd | wd | n1 | n/a |  |

## Table drivers

Open activities by share of iterations on the critical path.

Rows: rk.rows, in the order returned, at most 15.
When rk.next_offset is not null, add the line: Showing the first <returned> of <total> activities. (returned and total of rk).
No rows: write 'No activity was critical.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Critical % | criticality_pct | % | pct1 | n/a |  |
| On today's path | on_deterministic_path |  | flag | n/a |  |
| Total float (d) | total_float_d | d | n1 | n/a |  |
| Remaining (d) | rem_dur_d | d | n1 | n/a |  |
| Min (d) | min_d | d | n1 | n/a |  |
| Max (d) | max_d | d | n1 | n/a |  |

## Table weeks

Project finish dates per week.

Rows: rk.histogram, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 weeks are shown.
No rows: write 'No week.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Week from | week_start |  | date | n/a |  |
| To | week_end |  | date | n/a |  |
| Iterations | count | count | int | n/a |  |
| % | pct | % | pct1 | n/a |  |
| Cumulative % | cum_pct | % | pct1 | n/a |  |

## Cross-checks (equal values)

- same data date: cv.schedule_state.data_date = rk.schedule_state.data_date
- same engine match rate: cv.match_rate = rk.engine.match_rate
