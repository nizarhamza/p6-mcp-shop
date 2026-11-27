# Resource loading review of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Read only: nothing was written to the database.

[if: stale]
Warning: this project was changed after its last F9. Dates and loading are out of date until it is rescheduled in P6 (F9).
[end if]

[if not: total_rows]
No assignments: {project} has no resource assignment to review (none on the resource given, when one was given). Assign resources in P6, or run this skill without a resource.
[end if]

[if: total_rows]
## Summary

- Resources with assignments: {res_count}, of which material: {material}. Resource periods loaded: {total_rows}.
- Over-allocated resource periods: {over_periods}, on {res_over} resources.
- Labor and nonlabor resources without a limit (no max units or no calendar), never flagged as over-allocated: {no_limit}.

Load = actual (up to the data date) + remaining, spread over the working time of each assignment's calendar. Available = working hours of the resource's calendar x its max units per hour. Labor and nonlabor quantities are hours; material quantities are in the material's own unit and have no limit.

## By resource

[table: resources]

## Over-allocated periods

[table: over]
[end if]

## Actions

Only the actions that apply:

[if: stale]
- Reschedule the project in P6 (F9) before using the loading: it was changed after its last F9.
[end if]
[if: over_periods]
- Over-allocated resource periods: {over_periods}, on {res_over} resources. Level these resources or review their max units and calendars with the planner.
[end if]
[if: no_limit]
- Resources without a limit: {no_limit}. Enter their max units per hour and calendar in P6 to check their loading.
[end if]
