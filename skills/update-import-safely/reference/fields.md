# Fields of Update import (safe)

Generated from reference/spec.json by the catalog build. Each slot of reference/report.md is copied from one field of one call; write it in its format, never compute it.

## Calls

1. ins = p6_inspect_xer(path="{xer_path}"): file facts, projects in the file, pre-flight errors, warnings and info, global items reused or created.
2. dry = p6_import_xer(path="{xer_path}", mode="update", project="{project}"): dry run of the update (nothing is written): data date, refusal, counts per table, rows missing from the XER.

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

- {xer_path}: Full path of the XER file, as given
- {project}: Project ID as shown in P6 (the project to update), as given

## Units

- count: a count

## Slots

| Slot | Field (call.path) | Unit | Format | None | Meaning |
|-|-|-|-|-|-|
| file_version | ins.header.1 |  | text | n/a | P6 version that wrote the file |
| file_date | ins.header.2 |  | date | n/a | export date in the file header |
| file_bytes | ins.bytes |  | n0 | n/a | file size in bytes |
| encoding | ins.encoding |  | text | n/a | text encoding read (utf-8, else cp1252) |
| end_marker | ins.has_end_marker |  | flag | n/a | the file ends with %E (not truncated) |
| bad_chars | ins.replacement_chars | count | int | n/a | characters not readable in that encoding |
| xer_project | ins.preflight.project |  | text | n/a | Project ID of the file's project that is imported |
| dd_database | dry.data_date.database |  | datetime | n/a | data date of the project in the database |
| dd_xer | dry.data_date.xer |  | datetime | n/a | data date of the XER project |
| dd_older | dry.data_date.older |  | flag | n/a | the XER data date is older than the database's |
| would_refuse | dry.would_refuse |  | flag | n/a | applying these arguments would be refused |
| miss_acts | dry.missing_from_xer.TASK.count | count | int | n/a | activities of the project not in the XER (never deleted) |
| miss_links | dry.missing_from_xer.TASKPRED.count | count | int | n/a | relationships of the project not in the XER (removable) |
| miss_links_on | dry.missing_from_xer.TASKPRED.on_missing_activities | count | int | n/a | relationships of missing activities (never removed) |
| miss_asg | dry.missing_from_xer.TASKRSRC.count | count | int | n/a | assignments of the project not in the XER (removable) |
| miss_asg_on | dry.missing_from_xer.TASKRSRC.on_missing_activities | count | int | n/a | assignments of missing activities (never removed) |

## Table xer_projects

Rows: ins.projects, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 projects are shown.
No rows: write 'No project in the file.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Project ID | short_name |  | text | n/a |  |
| Data date | data_date |  | datetime | n/a |  |
| Activities | activities | count | int | n/a |  |

## Table file_tables

Rows: ins.tables, in the order returned, at most 30 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 30 items, add the line: Only the first 30 tables are shown.
No rows: write 'No table in the file.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Table | _key |  | text | n/a |  |
| Rows | _value | count | int | n/a |  |

## Table pf_errors

Rows: ins.preflight.errors, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 errors are shown.
No rows: write 'No pre-flight error.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Error | check |  | text | n/a |  |
| Items | count | count | int | n/a |  |
| First item | sample.0 |  | text | n/a |  |
| Note | note |  | text |  |  |

## Table pf_warnings

Rows: ins.preflight.warnings, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 warnings are shown.
No rows: write 'No pre-flight warning.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Warning | check |  | text | n/a |  |
| Items | count | count | int | n/a |  |
| First item | sample.0 |  | text | n/a |  |
| Note | note |  | text |  |  |

## Table pf_info

Rows: ins.preflight.info, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 items are shown.
No rows: write 'No pre-flight information.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Information | check |  | text | n/a |  |
| Items | count | count | int | n/a |  |
| First item | sample.0 |  | text | n/a |  |
| Note | note |  | text |  |  |

## Table global_items

Rows: ins.preflight.db_preview, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 tables are shown.
No rows: write 'No global item in the file.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Table | _key |  | text | n/a |  |
| Matched | matched | count | int | n/a |  |
| Would be created | would_create | count | int | n/a |  |

## Table refuse

Rows: dry.refuse_reasons, in the order returned, at most 10 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 10 items, add the line: Only the first 10 reasons are shown.
No rows: write 'No reason.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Reason | (the row itself) |  | text | n/a |  |

## Table counts

One row per table the import touches, in import order; Unchanged and Restored: the schedule options row (PROJPROP).

Rows: dry.counts, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 tables are shown.
No rows: write 'No table imported.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Table | _key |  | text | n/a |  |
| Matched | matched | count | int | n/a |  |
| Inserted | inserted | count | int | n/a |  |
| Updated | updated | count | int | n/a |  |
| Unchanged | unchanged | count | int | n/a |  |
| Restored | restored | count | int | n/a |  |
| Deleted | deleted | count | int | n/a |  |
| Kept existing | kept_existing | count | int | n/a |  |
| Skipped external | skipped_external | count | int | n/a |  |
| Skipped duplicate | skipped_duplicate | count | int | n/a |  |
| Skipped unmapped | skipped_unmapped | count | int | n/a |  |

## Table dry_warnings

Rows: dry.warnings, in the order returned, at most 20 (a dict gives one row per item: its key is _key, a plain value _value).
When the list holds more than 20 items, add the line: Only the first 20 warnings are shown.
No rows: write 'No warning.' instead of the table (nothing when the call failed).

| Column | Field (row path) | Unit | Format | None | In totals row |
|-|-|-|-|-|-|
| Warning | (the row itself) |  | text | n/a |  |

## Cross-checks (equal values)

- same project of the file in both calls: ins.preflight.project = dry.preflight.project
- same pre-flight errors in both calls: ins.preflight.errors = dry.preflight.errors
- same pre-flight warnings in both calls: ins.preflight.warnings = dry.preflight.warnings
- same XER data date in both calls: ins.projects.0.data_date = dry.data_date.xer
