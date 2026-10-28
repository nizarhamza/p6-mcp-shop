# Fields of List projects by EPS

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. eps = p6_list_eps(order="tree", limit=200): every EPS node in tree order, with its path and project counts.
2. prj = p6_list_projects(exclude_templates=true, eps="{eps}", order="eps", limit=200): projects in EPS tree order, then Project ID (template projects and baselines left out).
Leave out an argument whose value is empty (eps).

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

- {eps}: EPS ID whose projects to list, with the EPS below it (empty = every EPS), as given

## Units

- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| eps_total | eps.total | count | int | n/a | EPS nodes of the database |
| total | prj.total | count | int | n/a | projects listed (of the EPS asked and the EPS below it, else of every EPS), templates and baselines left out |

## Table eps

One row per EPS node, each before the EPS below it; project counts leave out baselines and templates.

Rows: eps.rows, in the order returned, at most 200.
When eps.next_offset is not null, add the line: Showing the first <returned> of <total> EPS nodes. (returned and total of eps).
No rows: write 'No EPS node in this database.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| EPS | path |  | text | n/a |  |
| EPS ID | eps_id |  | text | n/a |  |
| Projects | projects | count | int | n/a |  |
| With the EPS below | projects_subtree | count | int | n/a |  |

## Table projects

One row per project, in EPS tree order then Project ID.

Rows: prj.rows, in the order returned, at most 200.
When prj.next_offset is not null, add the line: Showing the first <returned> of <total> projects. (returned and total of prj).
No rows: write 'No project to list.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| EPS | eps_path |  | text | n/a |  |
| Project | proj_short_name + project_name |  | id_name | n/a |  |
| Status | status_code |  | text | n/a |  |
| Data date | last_recalc_date |  | date | n/a |  |
| Finish | scd_end_date |  | date | n/a |  |
