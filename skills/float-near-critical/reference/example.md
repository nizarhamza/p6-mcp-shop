# Float and near-critical activities of DEMO-SS225

Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. Float of that run, in days of each activity's calendar.

## Total float

- Open activities analysed: 75 (not completed; LOE and WBS summary left out); without a total float: 0.
- Total float (d): minimum -36.0, maximum 143.0, mean 24.0, median 0.0.
- Negative total float: 37; zero total float: 3; critical: 40 (project setting CT_TotFloat: total float <= 0 h (critical_drtn_hr_cnt)).
- On the longest path (driving path flag): 24.
- Total float at or below 10 d, critical included: 41.
- Near-critical, total float above 0 d and at or below 10 d: 1 (total float <= 10 d (days of each activity's calendar); total float > 0 d (days of each activity's calendar); LOE and WBS summary activities left out).
- Total floats that are not whole days: 0.

Warning: 37 open activities have negative total float: they finish later than a constraint or the project must finish date allows.

## Float distribution

Ranges in days: [a, b) includes a and excludes b, (a, b] excludes a and includes b. Percentages of the 75 open activities analysed.

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

## Float paths

Source: float_path (float_path: P6's multiple float paths of the last F9; driving_path_flag: no float path stored).

| Path | Activities | Min total float (d) | Max total float (d) | Finish |
|-|-|-|-|-|
| 1 | 24 | -36.0 | -36.0 | 2027-10-05 |
| 2 | 1 | -31.0 | -31.0 | 2027-08-11 |
| 3 | 1 | -29.0 | -29.0 | 2027-08-09 |
| 4 | 1 | -21.0 | -21.0 | 2027-09-14 |
| 5 | 10 | -5.0 | -5.0 | 2027-07-05 |

| Path | Order | Activity | Total float (d) | Early start | Early finish |
|-|-|-|-|-|-|
| 1 | 1 | PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | -36.0 | 2026-10-26 | 2027-04-02 |
| 1 | 2 | PRC-TR-1050 - Power transformers 225/63 kV - factory acceptance test | -36.0 | 2027-04-05 | 2027-04-09 |
| 1 | 3 | PRC-TR-1060 - Power transformers 225/63 kV - shipping and delivery to site | -36.0 | 2027-04-12 | 2027-06-01 |
| 1 | 4 | MS-1040 - Power transformers delivered to site | -36.0 | 2027-06-01 | 2027-06-01 |
| 1 | 5 | CON-HV-1040 - Power transformer TR1 installation and oil filling | -36.0 | 2027-06-02 | 2027-06-29 |
| 1 | 6 | CON-HV-1050 - Power transformer TR2 installation and oil filling | -36.0 | 2027-06-16 | 2027-07-13 |
| 1 | 7 | CON-CBL-1030 - Earthing connections to equipment | -36.0 | 2027-07-15 | 2027-08-04 |
| 1 | 8 | CON-SEC-1050 - Transformer firefighting system | -36.0 | 2027-07-15 | 2027-08-04 |
| 1 | 9 | MS-1060 - Mechanical completion | -36.0 | 2027-08-04 | 2027-08-04 |
| 1 | 10 | COM-PRE-1020 - Power transformer TR1 tests | -36.0 | 2027-08-05 | 2027-08-11 |
| 1 | 11 | COM-ENR-1000 - Energization procedure approval | -36.0 | 2027-08-05 | 2027-08-18 |
| 1 | 12 | COM-PRE-1030 - Power transformer TR2 tests | -36.0 | 2027-08-12 | 2027-08-18 |
| 1 | 13 | MS-1070 - Ready for energization | -36.0 | 2027-08-18 | 2027-08-18 |
| 1 | 14 | COM-ENR-1010 - Back-energization of the 225 kV GIS | -36.0 | 2027-08-19 | 2027-08-20 |
| 1 | 15 | MS-1080 - First energization 225 kV | -36.0 | 2027-08-20 | 2027-08-20 |
| 1 | 16 | COM-ENR-1020 - Energization of transformer TR1 | -36.0 | 2027-08-23 | 2027-08-23 |
| 1 | 17 | COM-ENR-1030 - Energization of transformer TR2 | -36.0 | 2027-08-24 | 2027-08-24 |
| 1 | 18 | COM-ENR-1040 - On-load tests and protection stability checks | -36.0 | 2027-08-25 | 2027-08-31 |
| 1 | 19 | COM-HO-1000 - Punch list closure | -36.0 | 2027-09-01 | 2027-09-21 |
| 1 | 20 | COM-ENR-1050 - Trial operation | -36.0 | 2027-09-01 | 2027-09-28 |
| 1 | 21 | COM-HO-1010 - As-built documentation | -36.0 | 2027-09-08 | 2027-10-05 |
| 1 | 22 | COM-HO-1030 - Provisional acceptance inspection | -36.0 | 2027-09-29 | 2027-10-05 |
| 1 | 23 | MS-1090 - Provisional acceptance | -36.0 | 2027-10-05 | 2027-10-05 |
| 1 | 24 | MS-1100 - Project completion | -36.0 | 2027-10-05 | 2027-10-05 |
| 2 | 1 | COM-PRE-1100 - Fire protection system tests | -31.0 | 2027-08-05 | 2027-08-11 |
| 3 | 1 | COM-PRE-1110 - Earthing resistance measurements | -29.0 | 2027-08-05 | 2027-08-09 |
| 4 | 1 | COM-HO-1020 - Operator training | -21.0 | 2027-09-01 | 2027-09-14 |
| 5 | 1 | PRC-GIS225-1040 - 225 kV GIS - manufacturing | -5.0 | 2026-10-26 | 2027-01-27 |
| 5 | 2 | PRC-GIS225-1050 - 225 kV GIS - factory acceptance test | -5.0 | 2027-01-28 | 2027-02-03 |
| 5 | 3 | PRC-GIS225-1060 - 225 kV GIS - shipping and delivery to site | -5.0 | 2027-02-04 | 2027-03-17 |

Showing the first 30 of 37 float path activities.

## Near-critical activities (total float above 0 d and at or below 10 d)

By total float, then start. Activities with total float at or below 0 are left out of this table.

| Activity | Status | Total float (d) | Free float (d) | Remaining duration (d) | Early finish | Float path |
|-|-|-|-|-|-|-|
| COM-PRE-1040 - 225 kV cable sheath and high-voltage tests | TK_NotStart | 6.0 | 42.0 | 4.0 | 2027-06-18 | none |
