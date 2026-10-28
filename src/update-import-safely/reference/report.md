# Update import of {project} from {xer_path} (dry run)

Nothing was written: this is the dry run. The import is applied only after your explicit yes.

[if: would_refuse]
The import would be refused as it is:

[table: refuse]
[end if]

## The file

- Written by P6 {file_version} on {file_date}; {file_bytes} bytes; encoding {encoding}; end marker %E: {end_marker}; unreadable characters: {bad_chars}.
- Project imported from the file: {xer_project}.

[table: xer_projects]

Rows per table in the file:

[table: file_tables]

## Pre-flight

Errors (a confirmed import refuses them):

[table: pf_errors]

Warnings:

[table: pf_warnings]

Information:

[table: pf_info]

Global items of the file (matched by name in the database, else created):

[table: global_items]

## Data date

Database {dd_database}, XER {dd_xer}. XER older than the database: {dd_older}.

[if: dd_older]
The XER data date is older than the project's: the import is refused unless you confirm that this older file is the one to import.
[end if]

## What the update would change

[table: counts]

Warnings of the dry run:

[table: dry_warnings]

## Missing from the XER

- Activities of {project} not in the XER: {miss_acts}. An import never deletes activities: delete them in P6 if they are obsolete.
- Relationships not in the XER: {miss_links}, plus {miss_links_on} on missing activities (never removed).
- Assignments not in the XER: {miss_asg}, plus {miss_asg_on} on missing activities (never removed).

[if not: would_refuse]
## Your decision

1. Apply this update import to {project} (yes or no)?
2. When it is applied, remove the relationships and assignments of {project} that are missing from the XER (remove_missing)? Without it they are kept.
[end if]
