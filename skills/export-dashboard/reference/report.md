# Excel dashboard of {project}

File written: {file}. The P6 database was not changed.

Data date {data_date}, last schedule run (F9) {last_f9}. Baseline: {bl_used}.

[if: stale]
Warning: this project was changed after its last F9. The dashboard shows the dates, float and critical path of the last F9: open P6, press F9, then export again.
[end if]

[if not: bl_used]
No baseline: the delayed activities card, the variance cards and the baseline bars stay empty. Set a project baseline in P6 or pass baseline= to fill them.
[end if]

## Cards (as written on the Dashboard)

[table: cards]

## Contents

- Activities: {n_acts}; WBS nodes: {n_wbs}; milestones: {n_ms}; critical activities: {n_crit}.

## DCMA checks that fail

[table: dcma_failed]

## Warnings

[table: warnings]

## How to use the file

- The Dashboard sheet prints on one A3 landscape page and is protected without a password.
- The Schedule Overview opens folded to WBS level 2: the outline buttons on the left unfold it.
- The Critical Path sheet lists the P6 float paths of the last F9 (when P6 stored none, the near critical activities grouped by total float).
- Every figure comes from the last F9: after changes in P6, press F9 and export again.
