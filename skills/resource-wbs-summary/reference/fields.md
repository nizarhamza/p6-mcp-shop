# Fields of Resource and WBS summary

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. res = p6_resource_summary(project="{project}", limit=10): quantities and costs per resource, totals.
2. wbs = p6_group_summary(project="{project}", by="wbs", wbs_level={wbs_level}, limit=30): activities and units per WBS node, totals, data date.
3. status = p6_group_summary(project="{project}", by="status", limit=10): activities and units per status.

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
- {wbs_level}: WBS level of the WBS table (1 = the level below the project node), as given

## Units

- d: days of each activity's calendar (hours / hours per day)
- h: hours
- qty: resource units: hours for labor and nonlabor, the material's own unit for material
- cost: cost in the database currency
- %: percent
- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| data_date | wbs.schedule_state.data_date |  | date | n/a | data date of the project |
| last_f9 | wbs.schedule_state.last_schedule_date |  | datetime | n/a | last schedule run (F9) in P6 |
| stale | wbs.schedule_state.stale |  | flag | n/a | this server changed the project after the last F9 |
| resources | res.totals.resources | count | int | n/a | resources assigned in the project (role only assignments not counted) |
| assignments | res.totals.assignments | count | int | n/a | resource assignments |
| asg_activities | res.totals.activities | count | int | n/a | activities with at least one assignment |
| units_planned | res.totals.planned_qty | h | n1 | n/a | planned (budgeted) units of the labor and nonlabor assignments |
| units_actual | res.totals.actual_qty | h | n1 | n/a | actual units (regular plus overtime) of the labor and nonlabor assignments |
| units_remaining | res.totals.remaining_qty | h | n1 | n/a | remaining units of the labor and nonlabor assignments |
| units_at_completion | res.totals.at_completion_qty | h | n1 | n/a | actual plus remaining units of the labor and nonlabor assignments |
| units_pct | res.totals.units_pct | % | pct1 | n/a | units % complete: actual / at completion units, labor and nonlabor |
| cost_planned | res.totals.planned_cost | cost | n0 | n/a | planned cost of every assignment |
| cost_actual | res.totals.actual_cost | cost | n0 | n/a | actual cost of every assignment |
| cost_remaining | res.totals.remaining_cost | cost | n0 | n/a | remaining cost of every assignment |
| cost_at_completion | res.totals.at_completion_cost | cost | n0 | n/a | actual plus remaining cost of every assignment |
| other_assignments | res.totals.other_type_assignments | count | int | n/a | material and other assignments left out of the unit totals |
| activities | wbs.totals.activities | count | int | n/a | activities of the project |
| open_activities | wbs.totals.open | count | int | n/a | open activities: not completed, LOE and WBS summary left out |
| critical | wbs.totals.critical | count | int | n/a | critical open activities under the project's definition |
| critical_definition | wbs.critical_definition |  | text | n/a | the project's definition of critical |
| level | wbs.level |  | int | n/a | WBS level of the WBS table |

## Table resources

One row per resource: labor and nonlabor first, then material, each by largest planned quantity.

Rows: res.rows, in the order returned, at most 10.
When res.next_offset is not null, add the line: Showing the first <returned> of <total> resources. (returned and total of res).
No rows: write 'No resource assignment in this project.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Resource | resource + name |  | id_name | n/a |  |
| Type | type |  | text | n/a |  |
| Activities | activities | count | int | n/a |  |
| Planned qty | planned_qty | qty | n1 | n/a |  |
| Actual qty | actual_qty | qty | n1 | n/a |  |
| Remaining qty | remaining_qty | qty | n1 | n/a |  |
| Units % | units_pct | % | pct1 | n/a |  |
| At completion cost | at_completion_cost | cost | n0 | n/a |  |
| Start | start |  | date | n/a |  |
| Finish | finish |  | date | n/a |  |

## Table wbs

One row per WBS node at the level asked, in P6 WBS order; activities on a shallower node keep their own row.

Rows: wbs.rows, in the order returned, at most 30.
Last row: 'Total' in the first column, the other columns from wbs.totals (same field names; blank where marked).
When wbs.next_offset is not null, add the line: Showing the first <returned> of <total> WBS nodes. (returned and total of wbs).
No rows: write 'No activity in this project.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| WBS | group + name |  | id_name | n/a | label |
| Activities | activities | count | int | n/a | yes |
| Not started | not_started | count | int | n/a | yes |
| In progress | in_progress | count | int | n/a | yes |
| Completed | completed | count | int | n/a | yes |
| Budget units (h) | budget_units | h | n1 | n/a | yes |
| Actual units (h) | actual_units | h | n1 | n/a | yes |
| Units % | units_pct | % | pct1 | n/a | yes |
| Critical | critical | count | int | n/a | yes |
| Min total float (d) | min_tf_d | d | n1 | n/a | yes |
| Finish | finish |  | date | n/a | yes |

## Table status

One row per activity status, in P6 order (not started, in progress, completed).

Rows: status.rows, in the order returned, at most 10.
Last row: 'Total' in the first column, the other columns from status.totals (same field names; blank where marked).
When status.next_offset is not null, add the line: Showing the first <returned> of <total> statuses. (returned and total of status).
No rows: write 'No activity in this project.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Status | name |  | text | n/a | label |
| Activities | activities | count | int | n/a | yes |
| Budget units (h) | budget_units | h | n1 | n/a | yes |
| Actual units (h) | actual_units | h | n1 | n/a | yes |
| Units % | units_pct | % | pct1 | n/a | yes |
| Remaining duration (d) | rem_dur_d | d | n1 | n/a | yes |
| Critical | critical | count | int | n/a | yes |

## Cross-checks (equal values)

- same data date in both group summaries: wbs.schedule_state.data_date = status.schedule_state.data_date
- same number of activities by WBS and by status: wbs.totals.activities = status.totals.activities
- same budget units by WBS and by status: wbs.totals.budget_units = status.totals.budget_units
- same actual units by WBS and by status: wbs.totals.actual_units = status.totals.actual_units
- same critical count by WBS and by status: wbs.totals.critical = status.totals.critical
