# Fields of Trend across updates

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. t = p6_trend(projects=["{updates}"], eps="{eps}", near_critical_days={near_days}, limit=20): one row per update: finish, progress, float, DCMA, milestones and changes since the previous update. In projects=[...], write one list item per value of the argument updates (values separated by commas: "A,B" gives "A", "B"); leave projects out when it is empty.
Leave out an argument whose value is empty (eps, updates).

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

- {updates}: Project IDs of the updates, separated by commas (empty: give eps), as given
- {eps}: EPS ID holding the updates, used when updates is empty, as given
- {near_days}: Near critical: total float up to this many days, as given

## Units

- wd: working days of each activity's calendar
- wd proj: working days of the project calendar
- d: days of each activity's calendar (hours / hours per day)
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| total | t.total | count | int | n/a | updates in the series |
| first_dd | t.series.first_data_date |  | date | n/a | data date of the first update |
| last_dd | t.series.last_data_date |  | date | n/a | data date of the latest update |
| near_d | t.near_critical_days | d | n1 | n/a | near critical limit in days of each activity's calendar |
| last_project | t.rows.-1.project |  | text | n/a | Project ID of the latest update shown |
| last_vs_prev | t.rows.-1.finish_variance_previous_wd | wd proj | n1 | n/a | finish of the latest update shown minus the previous update's (positive = later) |
| last_neg | t.rows.-1.negative_float | count | int | n/a | open activities with negative float in the latest update shown |
| last_failed | t.rows.-1.dcma.failed |  | list | none | DCMA checks failed in the latest update shown |
| last_cuts | t.rows.-1.changes.durations_cut | count | int | n/a | durations cut since the previous update (as p6_update_integrity) |
| last_removed | t.rows.-1.changes.activities_removed | count | int | n/a | activities removed since the previous update |
| last_stale | t.rows.-1.stale |  | flag | n/a | the latest update shown was changed by this server after its last F9 |

## Table updates

Dates of each update; finish variances in working days of the update's project calendar, positive = later.

Rows: t.rows, in the order returned, at most 20.
When t.next_offset is not null, add the line: Showing the first <returned> of <total> updates. (returned and total of t).
No rows: write 'No update.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| # | update |  | int | n/a |  |
| Update | project |  | text | n/a |  |
| Data date | data_date |  | date | n/a |  |
| Finish | finish |  | date | n/a |  |
| Must finish | must_finish |  | date | n/a |  |
| vs must finish (wd proj) | finish_vs_must_finish_wd | wd proj | n1 | n/a |  |
| vs first (wd proj) | finish_variance_first_wd | wd proj | n1 | n/a |  |
| vs previous (wd proj) | finish_variance_previous_wd | wd proj | n1 | n/a |  |
| vs baseline (wd proj) | baseline_finish_variance_wd | wd proj | n1 | n/a |  |
| Changed after F9 | stale |  | flag | n/a |  |

## Table progress

Progress and float of each update; float of open activities (LOE and WBS summary left out).

Rows: t.rows, in the order returned, at most 20.
When t.next_offset is not null, add the line: Showing the first <returned> of <total> updates. (returned and total of t).
No rows: write 'No update.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Update | project |  | text | n/a |  |
| Units % | units_pct | % | pct1 | n/a |  |
| BL planned % | planned_units_pct | % | pct1 | n/a |  |
| SPI (units) | spi_units |  | n2 | n/a |  |
| Critical | critical | count | int | n/a |  |
| Near critical | near_critical | count | int | n/a |  |
| Negative float | negative_float | count | int | n/a |  |
| Min float (d) | total_float.min_d | d | n1 | n/a |  |
| Median float (d) | total_float.median_d | d | n1 | n/a |  |

## Table quality

DCMA weighted score, grade, failed checks and BEI of each update, as p6_health_check with its defaults.

Rows: t.rows, in the order returned, at most 20.
When t.next_offset is not null, add the line: Showing the first <returned> of <total> updates. (returned and total of t).
No rows: write 'No update.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Update | project |  | text | n/a |  |
| DCMA points | dcma.points |  | n1 | n/a |  |
| Grade | dcma.grade |  | text | n/a |  |
| Failed checks | dcma.failed |  | list | none |  |
| BEI | dcma.bei |  | n2 | n/a |  |
| BEI passed | dcma.bei_pass |  | flag | n/a |  |

## Table changes

What changed since the previous update (n/a on the first): activities by Activity ID, links, durations cut.

Rows: t.rows, in the order returned, at most 20.
When t.next_offset is not null, add the line: Showing the first <returned> of <total> updates. (returned and total of t).
No rows: write 'No update.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Update | project |  | text | n/a |  |
| Since | changes.since |  | text | n/a |  |
| Activities added | changes.activities_added | count | int | n/a |  |
| Activities removed | changes.activities_removed | count | int | n/a |  |
| Links added | changes.links_added | count | int | n/a |  |
| Links removed | changes.links_removed | count | int | n/a |  |
| Durations cut | changes.durations_cut | count | int | n/a |  |

## Table milestones

Milestones followed, by date in the latest update.

Rows: t.milestones, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 milestones are shown.
No rows: write 'No milestone is followed.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Milestone | task_code + task_name |  | id_name | n/a |  |
| Type | task_type |  | text | n/a |  |
| Updates holding it | updates | count | int | n/a |  |

## Table ms_latest

The milestones followed in the latest update shown (same order as the milestones table): date (actual else forecast), slip since the previous update and variance since the first, in working days of the milestone's calendar.

Rows: t.rows.-1.milestones, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 milestones are shown.
No rows: write 'No milestone is followed.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Activity ID | task_code |  | text | n/a |  |
| Date | date |  | date | n/a |  |
| Date kind | date_kind |  | text | n/a |  |
| Status | status_code |  | text | n/a |  |
| Slip since previous (wd) | slip_wd | wd | n1 | n/a |  |
| Variance since first (wd) | variance_first_wd | wd | n1 | n/a |  |

## Table notes

Rows: t.notes, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 notes are shown.
No rows: write 'No note.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Note | (the row itself) |  | text | n/a |  |

## Cross-checks (equal values)

- every update of the series counted once: t.total = t.series.updates
