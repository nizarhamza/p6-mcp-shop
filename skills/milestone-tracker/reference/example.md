# Milestone tracker of DEMO-SS225

Data date 2026-10-26, last schedule run (F9) 2026-10-26 17:30. Each milestone has one date: the start of a start milestone, the finish of a finish milestone, actual else forecast (early date of the last F9). Variance = date minus baseline date: positive = later than the baseline.

## Summary

- Baseline: DEMO-SS225_BL (baseline dates: current).
- Must finish by: 2027-08-16.
- Milestones: 11; completed: 3; open: 8, of which critical: 7 (project setting CT_TotFloat: total float <= 0 h (critical_drtn_hr_cnt); open activities).
- Against the baseline: late 10, of which open 8; early 0; on time 1; without a baseline date 0.

Warning: 8 open milestones are forecast later than their baseline date.

## All milestones, by date

| Milestone | Type | Status | Date | Date kind | Baseline date | Variance (wd) | Variance (cd) | Vs baseline | Total float (d) | Critical |
|-|-|-|-|-|-|-|-|-|-|-|
| MS-1000 - Notice to proceed | TT_Mile | TK_Complete | 2026-02-02 | actual | 2026-02-02 | 0.0 | 0.0 | on_time | n/a | no |
| MS-1010 - Civil design issued for construction | TT_FinMile | TK_Complete | 2026-08-05 | actual | 2026-07-17 | 13.0 | 19.0 | late | n/a | no |
| MS-1020 - Electrical design issued for construction | TT_FinMile | TK_Complete | 2026-09-21 | actual | 2026-09-04 | 11.0 | 17.0 | late | n/a | no |
| MS-1050 - Civil works complete | TT_FinMile | TK_NotStart | 2027-02-03 | forecast | 2026-12-21 | 25.0 | 44.0 | late | 90.0 | no |
| MS-1030 - 225 kV GIS delivered to site | TT_FinMile | TK_NotStart | 2027-03-17 | forecast | 2027-02-17 | 20.0 | 28.0 | late | -5.0 | yes |
| MS-1040 - Power transformers delivered to site | TT_FinMile | TK_NotStart | 2027-06-01 | forecast | 2027-04-08 | 36.0 | 54.0 | late | -36.0 | yes |
| MS-1060 - Mechanical completion | TT_FinMile | TK_NotStart | 2027-08-04 | forecast | 2027-06-14 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1070 - Ready for energization | TT_FinMile | TK_NotStart | 2027-08-18 | forecast | 2027-06-28 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1080 - First energization 225 kV | TT_FinMile | TK_NotStart | 2027-08-20 | forecast | 2027-06-30 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1090 - Provisional acceptance | TT_FinMile | TK_NotStart | 2027-10-05 | forecast | 2027-08-16 | 36.0 | 50.0 | late | -36.0 | yes |
| MS-1100 - Project completion | TT_FinMile | TK_NotStart | 2027-10-05 | forecast | 2027-08-16 | 36.0 | 50.0 | late | -36.0 | yes |

## Open milestones, largest variance first

| Milestone | Forecast | Baseline date | Variance (wd) | Variance (cd) | Vs baseline | Total float (d) | Critical |
|-|-|-|-|-|-|-|-|
| MS-1040 - Power transformers delivered to site | 2027-06-01 | 2027-04-08 | 36.0 | 54.0 | late | -36.0 | yes |
| MS-1060 - Mechanical completion | 2027-08-04 | 2027-06-14 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1070 - Ready for energization | 2027-08-18 | 2027-06-28 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1080 - First energization 225 kV | 2027-08-20 | 2027-06-30 | 36.0 | 51.0 | late | -36.0 | yes |
| MS-1090 - Provisional acceptance | 2027-10-05 | 2027-08-16 | 36.0 | 50.0 | late | -36.0 | yes |
| MS-1100 - Project completion | 2027-10-05 | 2027-08-16 | 36.0 | 50.0 | late | -36.0 | yes |
| MS-1050 - Civil works complete | 2027-02-03 | 2026-12-21 | 25.0 | 44.0 | late | 90.0 | no |
| MS-1030 - 225 kV GIS delivered to site | 2027-03-17 | 2027-02-17 | 20.0 | 28.0 | late | -5.0 | yes |

## What drives MS-1040 - Power transformers delivered to site

This is the open milestone with the largest variance; its total float is -36.0 d. Its driving predecessors on the early dates of the last F9 (level 0 is the milestone; completed activities are left out):

| Level | Activity | Status | Early start | Early finish | Total float (d) | Drives | Link | Lag (d) |
|-|-|-|-|-|-|-|-|-|
| 0 | MS-1040 - Power transformers delivered to site | TK_NotStart | 2027-06-01 | 2027-06-01 | -36.0 | n/a | n/a | n/a |
| 1 | PRC-TR-1060 - Power transformers 225/63 kV - shipping and delivery to site | TK_NotStart | 2027-04-12 | 2027-06-01 | -36.0 | MS-1040 - Power transformers delivered to site | FS | 0.0 |
| 2 | PRC-TR-1050 - Power transformers 225/63 kV - factory acceptance test | TK_NotStart | 2027-04-05 | 2027-04-09 | -36.0 | PRC-TR-1060 - Power transformers 225/63 kV - shipping and delivery to site | FS | 0.0 |
| 3 | PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | TK_Active | 2026-10-26 | 2027-04-02 | -36.0 | PRC-TR-1050 - Power transformers 225/63 kV - factory acceptance test | FS | 0.0 |

Each driving chain starts from:

| Activity | Starts from | Date |
|-|-|-|
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | data_date | 2026-10-26 |

## Contract milestones

The contract milestones given, with their constraint, how many predecessors drive them, their forecast against the constraint date in working days of their calendar (positive = later) and where their total float comes from.

| Milestone | Constraint | Constraint date | Hard | Predecessors | Forecast | Forecast - constraint (wd) | Total float (d) | Float comes from |
|-|-|-|-|-|-|-|-|-|
| MS-1080 - First energization 225 kV | none | n/a | no | 1 | 2027-08-20 | n/a | -36.0 | Total float -36.0 d of MS-1080 comes from the project must finish date 2027-08-16 17:00:00, through MS-1080 FS 0 d -> COM-ENR-1020 FS 0 d -> COM-ENR-1030 FS 0 d -> COM-ENR-1040 FS 0 d -> COM-ENR-1050 FS 0 d -> COM-HO-1030 FS 0 d -> MS-1090 FS 0 d -> MS-1100. |
| MS-1090 - Provisional acceptance | none | n/a | no | 1 | 2027-10-05 | n/a | -36.0 | Total float -36.0 d of MS-1090 comes from the project must finish date 2027-08-16 17:00:00, through MS-1090 FS 0 d -> MS-1100. |
| MS-1100 - Project completion | none | n/a | no | 3 | 2027-10-05 | n/a | -36.0 | Total float -36.0 d of MS-1100 comes from the project must finish date 2027-08-16 17:00:00, through MS-1100. |

Not found in DEMO-SS225: MS-1999. Check these Activity IDs.
