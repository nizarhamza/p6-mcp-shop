# Fields of Excel dashboard

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. sum = p6_project_summary(project="{project}", baseline="{baseline}"): data date, last F9, schedule state and the baseline used, before the file is written.
2. dash = p6_export_dashboard(project="{project}", path="{path}", baseline="{baseline}", prepared_by="{prepared_by}", revision="{revision}", company="{company}", colors="{colors}"): writes the workbook (never the database): the 7 cards as written, counts, failed DCMA checks, warnings.
Leave out an argument whose value is empty (baseline, colors, company, prepared_by, revision).

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
- {path}: Full path of the .xlsx file to write, as given
- {baseline}: Project ID of the baseline (empty = the project baseline), as given
- {prepared_by}: Name printed under the title (may be empty), as given
- {revision}: Revision printed under the title (may be empty), as given
- {company}: Company name in the sidebar (may be empty), as given
- {colors}: Colors 'primary,accent' in hex, for example 1F3864,C00000 (may be empty), as given

## Units

- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | sum.schedule_state.data_date |  | date | n/a | data date of the project |
| last_f9 | sum.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | sum.schedule_state.stale |  | flag | n/a | this server changed the project after the last F9 |
| bl_used | sum.baseline.used |  | text | none | Project ID of the baseline used (baseline= else the project baseline) |
| file | dash.path |  | text | n/a | the .xlsx file written |
| n_acts | dash.counts.activities | count | int | n/a | activities in the Schedule Overview |
| n_wbs | dash.counts.wbs | count | int | n/a | WBS nodes, the project node included |
| n_ms | dash.counts.milestones | count | int | n/a | milestones in the Dashboard table (at most 30) |
| n_crit | dash.counts.critical | count | int | n/a | critical open activities under the project's definition |

## Table cards

The 7 cards of the Dashboard sheet in their order, value (as Excel shows it) and detail as written.

Rows: dash.cards, in the order returned, at most 7 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 7 items, add the line: Only the first 7 cards are shown.
No rows: write 'No card written.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Card | card |  | text | n/a |  |
| Value | text |  | text | n/a |  |
| Detail | detail |  | text | n/a |  |

## Table dcma_failed

DCMA 14 checks whose pass is false, in DCMA order (tool names).

Rows: dash.dcma_failed, in the order returned, at most 15 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 15 items, add the line: Only the first 15 checks are shown.
No rows: write 'Every DCMA check with a threshold passes.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Failed check | (the row itself) |  | text | n/a |  |

## Table warnings

Warnings of the export, as returned.

Rows: dash.warnings, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 warnings are shown.
No rows: write 'No warning.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Warning | (the row itself) |  | text | n/a |  |

## Cross-checks (equal values)

- same data date in the summary and the export: sum.schedule_state.data_date = dash.data_date
- same last F9 in the summary and the export: sum.schedule_state.last_schedule_date = dash.schedule_state.last_schedule_date
- same baseline in the summary and the export: sum.baseline.used = dash.baseline
- same number of activities: sum.activities.total = dash.counts.activities
- same number of WBS nodes: sum.counts.wbs = dash.counts.wbs
- same critical count: sum.critical.critical = dash.counts.critical
