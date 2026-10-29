# Logic and date integrity of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Read only: nothing was written to the database.

Run this check before pressing F9 on an imported update, because F9 overwrites the submitted dates.

[if: stale]
Warning: this project was changed after its last F9. The stored dates are out of date until it is rescheduled in P6 (F9), so differences are expected.
[end if]

## Engine against the last F9

- Open activities: {n_open}; match rate {match_rate} (early and late dates and total float the same); differing: {n_open_bad}.
- Completed activities: {n_done}; match rate {match_done} (early dates the same); differing: {n_done_bad}.
- Project finish: engine {finish_engine}, last F9 {finish_stored}.
- Trusted (match rate at least 0.99): {trusted}. Engine version {engine_version}.

[if not: trusted]
The stored dates do not all follow from the stored logic, durations and options: ask for a reschedule with these options and a resubmission, or an explanation of the mismatches.
[end if]

## Activities whose stored dates differ

[table: mismatched]

## What the engine models

{rules}

## Schedule options in force

Stored in: {opt_source}. Calendar of the lags: {lag_rule}. Options the project does not store take P6's defaults, which are not listed.

[table: options]
