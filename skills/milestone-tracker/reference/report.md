# Milestone tracker of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Each milestone has one date: the start of a start milestone, the finish of a finish milestone, actual else forecast (early date of the last F9). Variance = date minus baseline date: positive = later than the baseline.

[if: stale]
Warning: this project was changed after its last F9. Dates, float and critical flags are out of date until it is rescheduled in P6 (F9).
[end if]

[if not: baseline_project]
No baseline: this project has no project baseline and none was given, so no milestone has a baseline date or a variance. Set a project baseline in P6, or give the Project ID of a baseline.
[end if]

## Summary

- Baseline: {baseline_project} (baseline dates: {baseline_dates}).
- Must finish by: {must_finish}.
- Milestones: {n_milestones}; completed: {n_completed}; open: {n_open}, of which critical: {n_critical} ({critical_definition}).
- Against the baseline: late {n_late}, of which open {n_open_late}; early {n_early}; on time {n_on_time}; without a baseline date {n_no_baseline}.

[if: n_open_late]
Warning: {n_open_late} open milestones are forecast later than their baseline date.
[end if]

## All milestones, by date

[table: all]

## Open milestones, largest variance first

[table: late]

[if: target_code]
## What drives {target_code} - {target_name}

This is the open milestone with the largest variance; its total float is {target_tf} d. Its driving predecessors on the early dates of the last F9 (level 0 is the milestone; completed activities are left out):

[table: drivers]

Each driving chain starts from:

[table: roots]
[end if]

[if not: target_code]
There is no open milestone, so there is no driving path to show.
[end if]

[if: ct_def]
## Contract milestones

The contract milestones given, with their constraint, how many predecessors drive them, their forecast against the constraint date in working days of their calendar (positive = later) and where their total float comes from.

[table: contract]

[end if]
[if: ct_not_found]
Not found in {project}: {ct_not_found}. Check these Activity IDs.
[end if]
