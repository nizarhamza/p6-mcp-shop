# Logic and date integrity of DEMO-SS225

Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. Read only: nothing was written to the database.

Run this check before pressing F9 on an imported update, because F9 overwrites the submitted dates.

## Engine against the last F9

- Open activities: 75; match rate 1.00 (early and late dates and total float the same); differing: 0.
- Completed activities: 139; match rate 1.00 (early dates the same); differing: 0.
- Project finish: engine 2027-10-05 17:00, last F9 2027-10-05 17:00.
- Trusted (match rate at least 0.99): yes. Engine version 1.

## Activities whose stored dates differ

No activity differs: every stored date follows from the logic.

## What the engine models

retained logic placing every status (lag between two completed activities ignored), lag elapsed before the data date dropped, calendars per activity, lag rule calendar, must finish date for open ends, total float per sched_float_type; LOE, WBS summary, ALAP approximated; leveling not modelled

## Schedule options in force

Stored in: PROJPROP scheduling. Calendar of the lags: rcal_Predecessor. Options the project does not store take P6's defaults, which are not listed.

| Option | Value |
|-|-|
| enable_multiple_longest_path_calc | Y |
| key_activity_for_multiple_longest_paths | (none) |
| level_all_rsrc_flag | Y |
| level_float_thrs_cnt | 0 |
| level_keep_sched_date_flag | Y |
| level_outer_assign_flag | N |
| level_outer_assign_priority | 1 |
| level_over_alloc_pct | 0.0 |
| level_within_float_flag | N |
| limit_multiple_longest_path_calc | Y |
| max_multiple_longest_path | 5 |
| sched_calendar_on_relationship_lag | rcal_Predecessor |
| sched_float_type | FT_FF |
| sched_lag_early_start_flag | Y |
| sched_open_critical_flag | N |
| sched_outer_depend_type | SD_Both |
| sched_progress_override | N |
| sched_retained_logic | Y |
| sched_setplantoforecast | N |
| sched_use_expect_end_flag | Y |
| sched_use_project_end_date_for_float | Y |
| use_total_float_multiple_longest_paths | Y |
| levelprioritylist | priority_type:ASC |
