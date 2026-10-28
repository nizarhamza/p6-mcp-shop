# Update import of DEMO-SS225 from C:\P6\demo\DEMO-SS225.xer (dry run)

Nothing was written: this is the dry run. The import is applied only after your explicit yes.

## The file

- Written by P6 24.12 on 2026-10-26; 125,164 bytes; encoding utf-8; end marker %E: yes; unreadable characters: 0.
- Project imported from the file: DEMO-SS225.

| Project ID | Data date | Activities |
|-|-|-|
| DEMO-SS225 | 2026-10-26 08:00 | 214 |

Rows per table in the file:

| Table | Rows |
|-|-|
| OBS | 1 |
| PROJECT | 1 |
| CALENDAR | 1 |
| SCHEDOPTIONS | 1 |
| PROJWBS | 35 |
| RSRC | 15 |
| TASK | 214 |
| TASKPRED | 332 |
| TASKRSRC | 257 |

## Pre-flight

Errors (a confirmed import refuses them):

No pre-flight error.

Warnings:

No pre-flight warning.

Information:

| Information | Items | First item | Note |
|-|-|-|-|
| schedule_options | 1 | SCHEDOPTIONS | written to the project's schedule options (PROJPROP scheduling) unless import_schedule_options=False (default off in baseline mode); compare with p6_schedule_options |

Global items of the file (matched by name in the database, else created):

| Table | Matched | Would be created |
|-|-|-|
| OBS | 1 | 0 |
| RSRC | 15 | 0 |

## Data date

Database 2026-10-26 08:00, XER 2026-10-26 08:00. XER older than the database: no.

## What the update would change

| Table | Matched | Inserted | Updated | Unchanged | Restored | Deleted | Kept existing | Skipped external | Skipped duplicate | Skipped unmapped |
|-|-|-|-|-|-|-|-|-|-|-|
| OBS | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| CALENDAR | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PROJECT | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RSRC | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PROJWBS | 1 | 0 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TASK | 0 | 0 | 214 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TASKPRED | 0 | 0 | 332 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TASKRSRC | 0 | 0 | 257 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PROJPROP | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

Warnings of the dry run:

No warning.

## Missing from the XER

- Activities of DEMO-SS225 not in the XER: 0. An import never deletes activities: delete them in P6 if they are obsolete.
- Relationships not in the XER: 0, plus 0 on missing activities (never removed).
- Assignments not in the XER: 0, plus 0 on missing activities (never removed).

## Your decision

1. Apply this update import to DEMO-SS225 (yes or no)?
2. When it is applied, remove the relationships and assignments of DEMO-SS225 that are missing from the XER (remove_missing)? Without it they are kept.
