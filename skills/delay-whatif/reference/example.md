# Delay what-if: PRC-TR-1040 - Power transformers 225/63 kV - manufacturing delayed by 10 d

Project DEMO-SS225. Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. The delay is added to the remaining duration and the schedule is computed again in memory by P6 MCP's CPM engine: nothing is written to the database. Before = the last F9 as stored.

## The activity today

- PRC-TR-1040 - Power transformers 225/63 kV - manufacturing: status TK_Active, WBS Power transformers 225/63 kV, calendar DEMO 5-Day Workweek 8h.
- Actual start 2026-07-30; early start 2026-10-26, early finish 2027-04-02; late finish 2027-02-10.
- Original duration 150.0 d, remaining duration 106.0 d, physical % complete 33.0%.
- Total float -36.0 d, free float 0.0 d; on the longest path: Y.

## What drives it

Driving predecessors on the early dates of the last F9 (level 0 is the activity; completed activities are left out):

| Level | Activity | Early start | Early finish | Total float (d) | Drives | Link | Lag (d) |
|-|-|-|-|-|-|-|-|
| 0 | PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | 2026-10-26 | 2027-04-02 | -36.0 | n/a | n/a | n/a |

Each driving chain starts from:

| Activity | Starts from | Date |
|-|-|-|
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | data_date | 2026-10-26 |

## Where its float comes from

Origin of the late dates: project_must_finish, at MS-1100 - Project completion, date 2027-08-16.

Total float -36.0 d of PRC-TR-1040 comes from the project must finish date 2027-08-16 17:00:00, through PRC-TR-1040 FS 0 d -> PRC-TR-1050 FS 0 d -> PRC-TR-1060 FS 0 d -> MS-1040 FS 0 d -> CON-HV-1040 SS 10 d -> CON-HV-1050 FS 0 d -> CON-CBL-1030 FS 0 d -> COM-PRE-1020 FS 0 d -> COM-PRE-1030 FS 0 d -> MS-1070 FS 0 d -> COM-ENR-1010 FS 0 d -> MS-1080 FS 0 d -> COM-ENR-1020 ....

## Impact of the delay

- Edit applied: PRC-TR-1040: remaining 106 d +10 d = 116 d.
- Project finish: before 2027-10-05, after 2027-10-19; change 14.0 cd, 10.0 wd (working days of the finish activity's calendar).
- Critical open activities (total float <= 0 h; open activities, LOE and WBS summary left out): 40 before, 40 after; 0 become critical, 0 are no longer critical.
- Open activities with negative float: 37 before, 37 after.
- Activities whose dates or float move: 27.

Warning: this delay moves the project finish by 10.0 wd.

### Finish activity and constrained activities

| Activity | Finish before | Finish after | Change (cd) | Total float before (d) | Total float after (d) |
|-|-|-|-|-|-|
| MS-1100 - Project completion | 2027-10-05 | 2027-10-19 | 14.0 | -36.0 | -46.0 |

### Activities that become critical

No activity becomes critical.

### Activities that move, largest finish change first

| Activity | Early finish before | Early finish after | Finish change (cd) | Total float before (d) | Total float after (d) |
|-|-|-|-|-|-|
| CON-HV-1050 - Power transformer TR2 installation and oil filling | 2027-07-13 | 2027-07-28 | 15.0 | -36.0 | -46.0 |
| COM-ENR-1000 - Energization procedure approval | 2027-08-18 | 2027-09-01 | 14.0 | -36.0 | -46.0 |
| COM-ENR-1010 - Back-energization of the 225 kV GIS | 2027-08-20 | 2027-09-03 | 14.0 | -36.0 | -46.0 |
| COM-ENR-1020 - Energization of transformer TR1 | 2027-08-23 | 2027-09-06 | 14.0 | -36.0 | -46.0 |
| COM-ENR-1030 - Energization of transformer TR2 | 2027-08-24 | 2027-09-07 | 14.0 | -36.0 | -46.0 |
| COM-ENR-1040 - On-load tests and protection stability checks | 2027-08-31 | 2027-09-14 | 14.0 | -36.0 | -46.0 |
| COM-ENR-1050 - Trial operation | 2027-09-28 | 2027-10-12 | 14.0 | -36.0 | -46.0 |
| COM-HO-1000 - Punch list closure | 2027-09-21 | 2027-10-05 | 14.0 | -36.0 | -46.0 |
| COM-HO-1010 - As-built documentation | 2027-10-05 | 2027-10-19 | 14.0 | -36.0 | -46.0 |
| COM-HO-1020 - Operator training | 2027-09-14 | 2027-09-28 | 14.0 | -21.0 | -31.0 |
| COM-HO-1030 - Provisional acceptance inspection | 2027-10-05 | 2027-10-19 | 14.0 | -36.0 | -46.0 |
| COM-PRE-1020 - Power transformer TR1 tests | 2027-08-11 | 2027-08-25 | 14.0 | -36.0 | -46.0 |
| COM-PRE-1030 - Power transformer TR2 tests | 2027-08-18 | 2027-09-01 | 14.0 | -36.0 | -46.0 |
| COM-PRE-1100 - Fire protection system tests | 2027-08-11 | 2027-08-25 | 14.0 | -31.0 | -41.0 |
| COM-PRE-1110 - Earthing resistance measurements | 2027-08-09 | 2027-08-23 | 14.0 | -29.0 | -39.0 |

Showing the first 15 of 27 activities that move.

## Next step

Nothing was changed in P6: this what-if ran in memory. To make the delay real, change the activity in P6 (or ask for p6_update_activity, which is applied only after your explicit yes), then reschedule the project in P6 (F9).
