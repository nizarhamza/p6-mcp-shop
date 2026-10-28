# Weekly update review of DEMO-SS225

Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. Read only: nothing was written to the database.

## Progress

- Units % complete (actual / at completion units, labor and nonlabor): 49.7%.
- Physical % complete (weighted by budget units): 45.7%; duration % complete: 66.4%; activities completed: 65.0%.
- Activities whose physical % and units % differ: 4.
- Baseline planned units % at the data date: 54.1%; SPI (units, earned / baseline planned): 0.85.

## Finish

- Scheduled finish 2027-10-05, must finish by 2027-08-16: 50.0 calendar days, 36.0 working days of the project calendar (positive = later).
- Baseline used: DEMO-SS225_BL. Scheduled finish against the baseline's: 50.0 calendar days, 36.0 working days of the project calendar (positive = later).

## Critical path

Critical: project setting CT_TotFloat: total float <= 0 h (critical_drtn_hr_cnt); LOE and WBS summary activities left out. Critical open activities: 40; open activities with negative float: 37.

| Activity | Status | Early start | Early finish | Remaining (d) | Total float (d) |
|-|-|-|-|-|-|
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | TK_Active | 2026-10-26 | 2027-04-02 | 106.0 | -36.0 |
| PRC-TR-1050 - Power transformers 225/63 kV - factory acceptance test | TK_NotStart | 2027-04-05 | 2027-04-09 | 5.0 | -36.0 |
| PRC-TR-1060 - Power transformers 225/63 kV - shipping and delivery to site | TK_NotStart | 2027-04-12 | 2027-06-01 | 35.0 | -36.0 |
| MS-1040 - Power transformers delivered to site | TK_NotStart | 2027-06-01 | 2027-06-01 | 0.0 | -36.0 |
| CON-HV-1040 - Power transformer TR1 installation and oil filling | TK_NotStart | 2027-06-02 | 2027-06-29 | 20.0 | -36.0 |
| CON-HV-1050 - Power transformer TR2 installation and oil filling | TK_NotStart | 2027-06-16 | 2027-07-13 | 20.0 | -36.0 |
| CON-CBL-1030 - Earthing connections to equipment | TK_NotStart | 2027-07-15 | 2027-08-04 | 15.0 | -36.0 |
| CON-SEC-1050 - Transformer firefighting system | TK_NotStart | 2027-07-15 | 2027-08-04 | 15.0 | -36.0 |
| MS-1060 - Mechanical completion | TK_NotStart | 2027-08-04 | 2027-08-04 | 0.0 | -36.0 |
| COM-ENR-1000 - Energization procedure approval | TK_NotStart | 2027-08-05 | 2027-08-18 | 10.0 | -36.0 |
| COM-PRE-1020 - Power transformer TR1 tests | TK_NotStart | 2027-08-05 | 2027-08-11 | 5.0 | -36.0 |
| COM-PRE-1030 - Power transformer TR2 tests | TK_NotStart | 2027-08-12 | 2027-08-18 | 5.0 | -36.0 |
| MS-1070 - Ready for energization | TK_NotStart | 2027-08-18 | 2027-08-18 | 0.0 | -36.0 |
| COM-ENR-1010 - Back-energization of the 225 kV GIS | TK_NotStart | 2027-08-19 | 2027-08-20 | 2.0 | -36.0 |
| MS-1080 - First energization 225 kV | TK_NotStart | 2027-08-20 | 2027-08-20 | 0.0 | -36.0 |

Showing the first 15 of 40 critical activities.

## Slipped against the baseline

Matched activities finishing later: 199; earlier: 10. Cause of each finish variance, from the start variance and the duration change in working days:

| Cause | Activities |
|-|-|
| late_start | 144 |
| longer_duration | 10 |
| late_start_and_longer_duration | 45 |
| on_time | 5 |
| earlier | 10 |

Activities added or removed, then those whose finish moved by 5 calendar days or more, largest absolute variance in calendar days first (earlier finishes appear too; the table shows working days, so its order can differ from them). Finish variance = start variance + duration delta, in working days of each activity's calendar.

| Activity | Change | Finish | Baseline finish | Finish variance (wd) | Start variance (wd) | Duration delta (wd) | Cause |
|-|-|-|-|-|-|-|-|
| CON-BLD-1060 - Internal roads and gravel surfacing | matched | 2026-11-20 | 2026-09-11 | 49.0 | 35.0 | 14.0 | late_start_and_longer_duration |
| CON-SEC-1060 - Perimeter lighting and CCTV | matched | 2026-12-11 | 2026-10-02 | 49.0 | 49.0 | 0.0 | late_start |
| MS-1040 - Power transformers delivered to site | matched | 2027-06-01 | 2027-04-08 | 36.0 | 36.0 | 0.0 | late_start |
| PRC-TR-1060 - Power transformers 225/63 kV - shipping and delivery to site | matched | 2027-06-01 | 2027-04-08 | 36.0 | 36.0 | 0.0 | late_start |
| COM-ENR-1020 - Energization of transformer TR1 | matched | 2027-08-23 | 2027-07-01 | 36.0 | 36.0 | 0.0 | late_start |
| COM-ENR-1030 - Energization of transformer TR2 | matched | 2027-08-24 | 2027-07-02 | 36.0 | 36.0 | 0.0 | late_start |
| COM-ENR-1040 - On-load tests and protection stability checks | matched | 2027-08-31 | 2027-07-09 | 36.0 | 36.0 | 0.0 | late_start |
| COM-PRE-1110 - Earthing resistance measurements | matched | 2027-08-09 | 2027-06-17 | 36.0 | 36.0 | 0.0 | late_start |
| CON-HV-1040 - Power transformer TR1 installation and oil filling | matched | 2027-06-29 | 2027-05-07 | 36.0 | 36.0 | 0.0 | late_start |
| COM-ENR-1000 - Energization procedure approval | matched | 2027-08-18 | 2027-06-28 | 36.0 | 36.0 | 0.0 | late_start |
| COM-ENR-1010 - Back-energization of the 225 kV GIS | matched | 2027-08-20 | 2027-06-30 | 36.0 | 36.0 | 0.0 | late_start |
| COM-PRE-1020 - Power transformer TR1 tests | matched | 2027-08-11 | 2027-06-21 | 36.0 | 36.0 | 0.0 | late_start |
| COM-PRE-1030 - Power transformer TR2 tests | matched | 2027-08-18 | 2027-06-28 | 36.0 | 36.0 | 0.0 | late_start |
| COM-PRE-1100 - Fire protection system tests | matched | 2027-08-11 | 2027-06-21 | 36.0 | 36.0 | 0.0 | late_start |
| CON-CBL-1030 - Earthing connections to equipment | matched | 2027-08-04 | 2027-06-14 | 36.0 | 36.0 | 0.0 | late_start |

Showing the first 15 of 174 activities.

## Progress issues

Out of sequence links: 0. Out of sequence option of F9: retained logic.

| Type | Links | Successors |
|-|-|-|
| FS | 0 | 0 |
| FS_lead | 0 | 0 |
| SS | 0 | 0 |
| FF | 0 | 0 |
| SF | 0 | 0 |

Status checks:

| Check | Activities |
|-|-|
| active_without_start | 0 |
| complete_with_remaining_or_no_finish | 0 |
| pct_100_not_complete | 0 |
| not_started_with_actuals | 0 |
| finish_before_start | 0 |
| suspended_without_resume | 0 |
| actual_after_data_date | 0 |

## Critical look-ahead (3 weeks)

Window from 2026-10-26 08:00 to 2026-11-16 08:00 (end excluded). Critical activities in the window: 2; of them in progress 2, starting 0, finishing 0. Week 1 is the first 7 days of the window; outside = before or after it.

| Activity | In the window | Forecast start | Forecast finish | Start week | Finish week | Total float (d) |
|-|-|-|-|-|-|-|
| PRC-GIS225-1040 - 225 kV GIS - manufacturing | in_progress | 2026-07-16 | 2027-01-27 | outside | outside | -5.0 |
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | in_progress | 2026-07-30 | 2027-04-02 | outside | outside | -36.0 |

## Actions

Only the actions that apply to this update:

- Open activities with negative float: 37. Recover them: the schedule misses the must finish date or a constraint.
- Activities whose physical % and units % differ: 4. Check them.
- Critical activities in the look-ahead window: 2. Follow them up.
