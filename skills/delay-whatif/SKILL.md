---
name: p6-delay-whatif
description: "What-if impact of delaying one activity: driving path, float origin and the effect on the project finish and milestones (nothing is written). Use when the user asks what happens if an activity is late or delayed."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Delay what-if

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- task_code: Activity ID
- delay_days: Extra working days (default 10)

What happens to project <project> if activity <task_code> takes <delay_days> more days?

Steps:
1. p6_get_activity(project="<project>", task_code="<task_code>"): remaining and original duration, total
   float, calendar.
2. p6_driving_path(project="<project>", target="<task_code>"): what drives it today.
3. p6_float_origin(project="<project>", task_code="<task_code>"): where its float comes from.
4. p6_schedule_whatif(project="<project>", edits=[{"op": "duration", "task_code": "<task_code>",
   "remaining_days": <current remaining days + <delay_days>>}]): use the remaining duration read in
   step 1 (for a not started activity also set original_days the same way).

Report: the activity today (dates, float, drivers); the project finish before and after (calendar and
working days); milestones and constrained activities that move or go negative; the activities that
become critical; whether the engine is trusted (engine.trusted) for this project. Nothing is written to
the database.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
