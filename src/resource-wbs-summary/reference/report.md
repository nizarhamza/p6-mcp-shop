# Resource and WBS summary of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Quantities and costs as stored on the assignments (not time-phased).

[if: stale]
Warning: this project was changed after its last F9. Dates, float and critical counts are out of date until it is rescheduled in P6 (F9).
[end if]

## Totals

- Resources: {resources}; assignments: {assignments}, on {asg_activities} activities.
- Labor and nonlabor units (h): planned {units_planned}, actual {units_actual}, remaining {units_remaining}, at completion {units_at_completion}; units % complete {units_pct}.
- Costs of every assignment: planned {cost_planned}, actual {cost_actual}, remaining {cost_remaining}, at completion {cost_at_completion}.
- Material and other assignments, left out of the unit totals: {other_assignments}.
- Activities: {activities}; open: {open_activities}; critical: {critical} ({critical_definition}).

## By resource

Quantities in hours for labor and nonlabor resources, in the material's own unit for material (RT_Mat).

[table: resources]

## By WBS (level {level})

[table: wbs]

## By status

[table: status]
