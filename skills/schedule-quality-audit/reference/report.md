# Schedule quality audit of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Every figure comes from the last F9 in P6; this audit changed nothing in the database.

[if: stale]
Warning: this project was changed after its last F9. Dates, float and the checks below are out of date until it is rescheduled in P6 (F9).
[end if]

[if not: trusted]
Warning: this server's CPM engine does not reproduce the last F9 of this project (match rate {match_rate}). The critical path test relies on it: its result is not reliable until the differences are explained (the logic-date-integrity skill lists them).
[end if]

## Score

- Checks passed: {score_passed} of {score_evaluated} evaluated ({score_pct}); failed: {score_failed}; not evaluated: {score_not_evaluated}.
- Weighted score: {w_points} points out of 100, grade {w_grade}. Engine match rate with the last F9: {match_rate}.
- Thresholds: {threshold_source}. Baseline of missed tasks and BEI: {baseline}.
- Open activities: {open_activities} (not completed, LOE and WBS summary left out).

[if not: baseline]
No baseline: missed tasks and BEI are not evaluated. Set a project baseline in P6 to evaluate them.
[end if]

Weighted score: each check below earns its weight when it passes, half when it fails within its warn band (an at most check up to twice its threshold, an at least check down to 0.9 times it; no band at a zero threshold) and nothing when it fails; a check not evaluated is left out, and the points are the earned weight out of the weight of the evaluated checks. Grades: A from 90 points, B from 80, C from 70, D from 55, F below.

[table: weighted]

## DCMA checks

Count and Out of: open activities (logic, hard_constraints, high_float, negative_float), open TT_Task and TT_Rsrc activities (high_duration, resources), links whose successor is open (leads, lags, long_lags, fs_links), all activities (invalid_dates), baseline activities due by the data date (missed_tasks; bei counts the completed activities out of them), constraint dates plus the must finish date (key_dates). LOE and WBS summary activities are always left out. Pass: % at most the threshold, except fs_links (at least); logic_density, cpli and bei compare their Value (at least the threshold). logic_density is links whose successor is open per open activity; it counts in the weighted score only, not in the checks passed above. key_dates is information only.

[table: dcma]

[if: cpt_activity]
Critical path test: {cpt_activity}, the earliest most critical open task, is delayed in this server's CPM engine; the test passes when the project finish moves about as much as that activity's own finish.
[end if]

## Trend since the previous audit

[if: trend_error]
No trend: there is no earlier audit of this project in this database. This run saved a snapshot; the next audit is compared with it.
[end if]

[table: trend]

## Dangling ends

Dangling ends: {dangling}, open starts (driven only by FF or SF predecessors) plus open finishes (driving only SS or SF successors); an activity with both counts twice.

[table: dangling]

## Redundant links

{redundant} links are candidates for removal. Removing all of them would leave {red_side_effects} open activities without a predecessor or a successor.

[table: redundant]

## Float profile

Total float of the open activities from {tf_min} d to {tf_max} d; negative: {tf_negative}; critical: {critical} ({critical_definition}).

[table: float]

## Proposed fixes

Proposals only: nothing was changed. A fix is applied by the user in P6, or through a dry run that the user reads and confirms; then the project is rescheduled (F9) and audited again.

[if: tf_negative]
- Negative float: {tf_negative} open activities, down to {tf_min} d. Recover the driving path (logic, durations, resources) or review the date it is measured against. Never delete a constraint only to clear negative float.
[end if]
[if: neg_expl]
  {neg_expl}
[end if]
[if: missed]
- Missed tasks: {missed} activities due by the baseline finished late or not at all. Re-plan their remaining work and its logic.
[end if]
[if: high_float]
- High float: {high_float} open activities above the limit. Check their successors: a missing link gives float that is not real.
[end if]
[if: high_expl]
  {high_expl}
[end if]
[if: logic_count]
- Open ends: {logic_count} open activities without a predecessor or a successor. Tie an open end to the work it really drives, never straight to the project finish.
[end if]
[if: lags]
- Lags: {lags} links with a positive lag. Replace a lag that stands for work (delivery, curing, review) by an activity.
[end if]
[if: dangling]
- Dangling ends: {dangling}. Add the suggested link after checking it, or an FS link if the work cannot overlap.
[end if]
[if not: fs_pass]
- Relationship types: do not convert SS or FF ties to FS only to pass fs_links: a link type follows how the work overlaps.
[end if]
[if: redundant]
- Redundant links: {redundant} candidates. Remove only a link that does not drive (Drives no), and check the activities it would leave without logic.
[end if]
