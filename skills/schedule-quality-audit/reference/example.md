# Schedule quality audit of DEMO-SS225

Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. Every figure comes from the last F9 in P6; this audit changed nothing in the database.

## Score

- Checks passed: 6 of 13 evaluated (46.2%); failed: 7; not evaluated: 3.
- Thresholds: DCMA defaults. Baseline of missed tasks and BEI: DEMO-SS225_BL.
- Open activities: 75 (not completed, LOE and WBS summary left out).

## DCMA checks

Count and Out of: open activities (logic, hard_constraints, high_float, negative_float), open TT_Task and TT_Rsrc activities (high_duration, resources), links whose successor is open (leads, lags, long_lags, fs_links), all activities (invalid_dates), baseline activities due by the data date (missed_tasks; bei counts the completed activities out of them), constraint dates plus the must finish date (key_dates). LOE and WBS summary activities are always left out. Pass: % at most the threshold, except fs_links (at least); cpli and bei compare their Value (at least the threshold). key_dates is information only.

| Check | Count | Out of | % | Value | Threshold | Pass |
|-|-|-|-|-|-|-|
| logic | 0 | 75 | 0.0% | n/a | 5.00 | yes |
| leads | 0 | 145 | 0.0% | n/a | 0.00 | yes |
| lags | 15 | 145 | 10.3% | n/a | 5.00 | no |
| long_lags | 0 | 145 | 0.0% | n/a | none | not evaluated |
| fs_links | 130 | 145 | 89.7% | n/a | 90.00 | no |
| hard_constraints | 0 | 75 | 0.0% | n/a | 5.00 | yes |
| high_float | 28 | 75 | 37.3% | n/a | 5.00 | no |
| negative_float | 37 | 75 | 49.3% | n/a | 0.00 | no |
| high_duration | 2 | 67 | 3.0% | n/a | 5.00 | yes |
| invalid_dates | 0 | 214 | 0.0% | n/a | 0.00 | yes |
| resources | 13 | 67 | 19.4% | n/a | none | not evaluated |
| missed_tasks | 134 | 149 | 89.9% | n/a | 5.00 | no |
| critical_path_test | n/a | n/a | n/a | n/a | none | yes |
| cpli | n/a | n/a | n/a | 0.85 | 0.95 | no |
| bei | 139 | 149 | 93.3% | 0.93 | 0.95 | no |
| key_dates | 1 | 1 | 100.0% | n/a | none | not evaluated |

Critical path test: PRC-TR-1040 - Power transformers 225/63 kV - manufacturing, the earliest most critical open task, is delayed in this server's CPM engine; the test passes when the project finish moves about as much as that activity's own finish.

## Trend since the previous audit

No trend: there is no earlier audit of this project in this database. This run saved a snapshot; the next audit is compared with it.

## Dangling ends

Dangling ends: 0, open starts (driven only by FF or SF predecessors) plus open finishes (driving only SS or SF successors); an activity with both counts twice.

No dangling start or finish.

## Redundant links

35 links are candidates for removal. Removing all of them would leave 12 open activities without a predecessor or a successor.

| Predecessor | Successor | Type | Lag (d) | Categories | Drives |
|-|-|-|-|-|-|
| ENG-SEC-1140 - Protection relay settings - revise and issue for construction | COM-ENR-1000 - Energization procedure approval | FS | 0.0 | completed_predecessor | no |
| ENG-SEC-1140 - Protection relay settings - revise and issue for construction | COM-PRE-1050 - Protection relay secondary injection tests | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1000 - GIS building foundations | CON-BLD-1000 - GIS building structure | FS | 5.0 | completed_predecessor | yes |
| CON-BLD-1030 - Control building structure | CON-BLD-1040 - Control building finishing | FS | 0.0 | completed_predecessor | yes |
| CON-FDN-1040 - Gantry and outdoor equipment foundations | CON-BLD-1060 - Internal roads and gravel surfacing | FS | 0.0 | completed_predecessor | yes |
| CON-FDN-1050 - Cable trench construction | CON-BLD-1060 - Internal roads and gravel surfacing | FS | 0.0 | completed_predecessor | yes |
| CON-SITE-1040 - Drainage and oil separator | CON-BLD-1060 - Internal roads and gravel surfacing | FS | 0.0 | completed_predecessor | yes |
| CON-FDN-1050 - Cable trench construction | CON-CBL-1000 - Control cable laying | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1050 - Cable trench construction | CON-CBL-1020 - LV power cabling | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1040 - Gantry and outdoor equipment foundations | CON-HV-1000 - Gantry steel structures and busbars | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1020 - Transformer TR1 foundation and oil pit | CON-HV-1040 - Power transformer TR1 installation and oil filling | FS | 0.0 | completed_predecessor, transitive | no |
| CON-FDN-1060 - Transformer firewall | CON-HV-1040 - Power transformer TR1 installation and oil filling | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1030 - Transformer TR2 foundation and oil pit | CON-HV-1050 - Power transformer TR2 installation and oil filling | FS | 0.0 | completed_predecessor | no |
| CON-FDN-1050 - Cable trench construction | CON-HV-1060 - 225 kV cable laying | FS | 0.0 | completed_predecessor | no |
| PRC-MVS-1060 - MV switchgear - shipping and delivery to site | CON-SEC-1000 - MV switchgear installation | FS | 0.0 | completed_predecessor | no |

Showing the first 15 of 35 candidate links.

## Float profile

Total float of the open activities from -36.0 d to 143.0 d; negative: 37; critical: 40 (project setting CT_TotFloat: total float <= 0 h (critical_drtn_hr_cnt)).

| Range (d) | Total float | Total float % | Free float | Free float % |
|-|-|-|-|-|
| < -20 | 27 | 36.0% | 1 | 1.3% |
| [-20, -10) | 0 | 0.0% | 0 | 0.0% |
| [-10, -5) | 0 | 0.0% | 0 | 0.0% |
| [-5, 0) | 10 | 13.3% | 0 | 0.0% |
| = 0 | 3 | 4.0% | 54 | 72.0% |
| (0, 5] | 0 | 0.0% | 1 | 1.3% |
| (5, 10] | 1 | 1.3% | 1 | 1.3% |
| (10, 20] | 2 | 2.7% | 2 | 2.7% |
| (20, 44] | 4 | 5.3% | 5 | 6.7% |
| > 44 | 28 | 37.3% | 11 | 14.7% |

## Proposed fixes

Proposals only: nothing was changed. A fix is applied by the user in P6, or through a dry run that the user reads and confirms; then the project is rescheduled (F9) and audited again.

- Negative float: 37 open activities, down to -36.0 d. Recover the driving path (logic, durations, resources) or review the date it is measured against.
- Missed tasks: 134 activities due by the baseline finished late or not at all. Re-plan their remaining work and its logic.
- High float: 28 open activities above the limit. Check their successors: a missing link gives float that is not real.
- Lags: 15 links with a positive lag. Replace a lag that stands for work (delivery, curing, review) by an activity.
- Redundant links: 35 candidates. Remove only a link that does not drive (Drives no), and check the activities it would leave without logic.
