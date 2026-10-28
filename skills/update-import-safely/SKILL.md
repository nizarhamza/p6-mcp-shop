---
name: p6-update-import-safely
description: "Import an updated XER into an existing project safely: inspect, dry run, review, then apply only on the user's yes. Use when the user wants to import or load an XER update into a project."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Update import (safe)

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- xer_path: Full path of the XER file
- project: Project ID as shown in P6

Update project <project> from the XER file <xer_path>, safely.

Steps:
1. p6_inspect_xer(path="<xer_path>"): projects in the file, data date, pre-flight errors and warnings.
   If there are pre-flight errors, stop and report them: the import would be refused.
2. p6_import_xer(path="<xer_path>", mode="update", project="<project>", dry_run=true): the dry run.
3. Review it: data_date (database against XER, older), would_refuse and refuse_reasons, counts per
   table, missing_from_xer (activities, links and assignments of the project that the XER does not
   contain) and the warnings.
4. Show the user a short summary of what the import would change and ask two questions: apply it (yes
   or no), and whether missing links or assignments must be removed (remove_missing).
5. Only after an explicit yes: call p6_import_xer again with the same arguments, dry_run=false and the
   confirmation_token of the dry run (and remove_missing if the user asked). Report the backup taken
   and stale_projects.
6. Ask the user to open P6 and press F9, then suggest the weekly update review.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
