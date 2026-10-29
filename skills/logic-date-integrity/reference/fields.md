# Fields of Logic and date integrity

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. cv = p6_cpm_validate(project="{project}", limit=15): the engine against the last F9: match rates, activities that differ, rules.
2. so = p6_schedule_options(project="{project}"): schedule options stored for the project and the lag calendar.

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

- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | cv.schedule_state.data_date |  | date | n/a | data date |
| last_f9 | cv.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | cv.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| match_rate | cv.match_rate |  | n2 | n/a | share of open activities with the same early and late dates and total float (1.00 = all) |
| match_done | cv.match_rate_completed |  | n2 | n/a | share of completed activities with the same early dates |
| trusted | cv.trusted |  | flag | n/a | match rate at least 0.99 |
| n_open | cv.counts.open | count | int | n/a | open activities |
| n_open_bad | cv.counts.open_mismatched | count | int | n/a | open activities that differ |
| n_done | cv.counts.completed | count | int | n/a | completed activities |
| n_done_bad | cv.counts.completed_mismatched | count | int | n/a | completed activities whose early dates differ |
| finish_engine | cv.project_finish.engine |  | datetime | n/a | project finish computed by the engine |
| finish_stored | cv.project_finish.stored |  | datetime | n/a | project finish of the last F9 |
| rules | cv.rules |  | text | n/a | what the engine models |
| engine_version | cv.engine_version |  | int | n/a | version of the engine's date and float rules |
| opt_source | so.db_source |  | text | n/a | where the options are stored |
| lag_rule | so.lag_rule.db_effective |  | text | n/a | calendar of the lags |

## Table mismatched

Open activities first, then completed ones, by Activity ID.

Rows: cv.rows, in the order returned, at most 15.
When cv.next_offset is not null, add the line: Showing the first <returned> of <total> activities that differ. (returned and total of cv).
No rows: write 'No activity differs: every stored date follows from the logic.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity | task_code + task_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Differences (stored, engine) | differences_text |  | text | n/a |  |
| Probable cause | probable_cause |  | text | n/a |  |

## Table options

Options stored in the database, as P6 names them.

Rows: so.options, in the order returned, at most 40 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 40 items, add the line: Only the first 40 options are shown.
No rows: write 'No schedule option is stored for this project.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Option | option |  | text | n/a |  |
| Value | db |  | text | not stored |  |
