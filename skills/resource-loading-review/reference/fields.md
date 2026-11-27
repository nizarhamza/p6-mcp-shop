# Fields of Resource loading review

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. rl = p6_resource_loading(project="{project}", period="{period}", resource="{resource}", limit=200): time-phased load per resource and period against its limit, totals, peaks and counts.
Leave out an argument whose value is empty (resource).

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
- {period}: Loading period: month or week, as given
- {resource}: Resource ID to review alone (empty: every resource), as given

## Units

- qty: resource units: hours for labor and nonlabor, the material's own unit for material
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | rl.data_date |  | date | n/a | data date |
| last_f9 | rl.schedule_state.last_schedule_date |  | datetime | n/a | last F9 in P6 |
| stale | rl.schedule_state.stale |  | flag | n/a | changed by this server after the last F9 |
| total_rows | rl.total | count | int | n/a | resource periods (one row per resource and loaded period) |
| res_count | rl.counts.resources | count | int | n/a | resources with assignments |
| over_periods | rl.counts.over_allocated_periods | count | int | n/a | over-allocated resource periods (labor and nonlabor) |
| res_over | rl.counts.resources_over | count | int | n/a | resources over their limit in at least one period |
| material | rl.counts.material_resources | count | int | n/a | material resources (own unit, no limit) |
| no_limit | rl.counts.no_limit |  | list | none | labor and nonlabor resources without a max units limit or a calendar |

## Table resources

One row per resource, labor and nonlabor first, then material: stored quantities, the peak period and the over-allocated periods (n/a: no limit).

Rows: rl.resources, in the order returned, at most 30 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 30 items, add the line: Only the first 30 resources are shown.
No rows: write 'No resource is assigned.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Resource | resource + name |  | id_name | n/a |  |
| Kind | kind |  | text | n/a |  |
| Unit | unit |  | text | n/a |  |
| Budget | budget | qty | n1 | n/a |  |
| Actual | actual | qty | n1 | n/a |  |
| Remaining | remaining | qty | n1 | n/a |  |
| At completion | at_completion | qty | n1 | n/a |  |
| Max units/h | max_units_per_hour |  | n2 | n/a |  |
| Peak period | peak.period |  | text | n/a |  |
| Peak load | peak.load | qty | n1 | n/a |  |
| Available at peak | peak.available | qty | n1 | n/a |  |
| Peak load % | peak.load_pct | % | pct1 | n/a |  |
| Over-allocated periods | over_periods | count | int | no limit |  |

## Table over

The resource periods of the page whose load (actual + remaining) is above what the resource can give.

Rows: rl.rows, in the order returned, at most 30, only the rows whose over is true.
When rl.next_offset is not null, add the line: Showing the first <returned> of <total> resource periods. (returned and total of rl).
No rows: write 'No period is over-allocated on this page.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Resource | resource + name |  | id_name | n/a |  |
| Period | period |  | text | n/a |  |
| Load | load | qty | n1 | n/a |  |
| Available | available | qty | n1 | n/a |  |
| Load % | load_pct | % | pct1 | n/a |  |
| Over by | over_by | qty | n1 | n/a |  |

## Cross-checks (equal values)

- same data date: rl.data_date = rl.schedule_state.data_date
