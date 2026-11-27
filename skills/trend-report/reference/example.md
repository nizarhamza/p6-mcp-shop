# Schedule trend across 3 updates

Updates from data date 2026-02-02 to 2026-10-26, ordered by data date. Values of the last F9 of each update; read only: nothing was written to the database.

## Finish by update

Finish variances are working days of each update's project calendar, positive = later: against the must finish date, the first update, the previous update and the update's own project baseline.

| # | Update | Data date | Finish | Must finish | vs must finish (wd proj) | vs first (wd proj) | vs previous (wd proj) | vs baseline (wd proj) | Changed after F9 |
|-|-|-|-|-|-|-|-|-|-|
| 1 | DEMO-SS225_BL | 2026-02-02 | 2027-08-16 | 2027-08-16 | 0.0 | 0.0 | n/a | n/a | no |
| 2 | DEMO-SS225_PREV | 2026-10-19 | 2027-10-19 | 2027-08-02 | 56.0 | 46.0 | 46.0 | n/a | no |
| 3 | DEMO-SS225 | 2026-10-26 | 2027-10-05 | 2027-08-16 | 36.0 | 36.0 | -10.0 | 36.0 | no |

## Progress and float by update

Units % = actual / at completion units (labor and nonlabor); BL planned % = baseline planned units at the data date; SPI = earned / baseline planned units (n/a without a project baseline). Near critical = open activities that are not critical with total float up to 10.0 days.

| Update | Units % | BL planned % | SPI (units) | Critical | Near critical | Negative float | Min float (d) | Median float (d) |
|-|-|-|-|-|-|-|-|-|
| DEMO-SS225_BL | 0.0% | n/a | n/a | 35 | 2 | 0 | 0.0 | 80.0 |
| DEMO-SS225_PREV | 48.3% | n/a | n/a | 45 | 4 | 43 | -56.0 | -14.0 |
| DEMO-SS225 | 49.7% | 54.1% | 0.85 | 40 | 1 | 37 | -36.0 | 0.0 |

## Schedule quality by update

DCMA weighted score (points out of 100) and grade, the checks that failed and BEI (n/a without a project baseline), as the health check computes them.

| Update | DCMA points | Grade | Failed checks | BEI | BEI passed |
|-|-|-|-|-|-|
| DEMO-SS225_BL | 88.6 | B | lags, high_float | n/a | n/a |
| DEMO-SS225_PREV | 70.5 | C | lags, fs_links, high_float, negative_float, cpli | n/a | n/a |
| DEMO-SS225 | 70.5 | C | lags, fs_links, high_float, negative_float, missed_tasks, cpli, bei | 0.93 | no |

## Changes since the previous update

| Update | Since | Activities added | Activities removed | Links added | Links removed | Durations cut |
|-|-|-|-|-|-|-|
| DEMO-SS225_BL | n/a | n/a | n/a | n/a | n/a | n/a |
| DEMO-SS225_PREV | DEMO-SS225_BL | 1 | 0 | 4 | 2 | 0 |
| DEMO-SS225 | DEMO-SS225_PREV | 0 | 1 | 2 | 4 | 2 |

## Milestones

Milestones followed (present in every update):

| Milestone | Type | Updates holding it |
|-|-|-|
| MS-1000 - Notice to proceed | TT_Mile | 3 |
| MS-1010 - Civil design issued for construction | TT_FinMile | 3 |
| MS-1020 - Electrical design issued for construction | TT_FinMile | 3 |
| MS-1050 - Civil works complete | TT_FinMile | 3 |
| MS-1030 - 225 kV GIS delivered to site | TT_FinMile | 3 |
| MS-1040 - Power transformers delivered to site | TT_FinMile | 3 |
| MS-1060 - Mechanical completion | TT_FinMile | 3 |
| MS-1070 - Ready for energization | TT_FinMile | 3 |
| MS-1080 - First energization 225 kV | TT_FinMile | 3 |
| MS-1090 - Provisional acceptance | TT_FinMile | 3 |
| MS-1100 - Project completion | TT_FinMile | 3 |

Their dates in the latest update shown, DEMO-SS225, in the same order:

| Activity ID | Date | Date kind | Status | Slip since previous (wd) | Variance since first (wd) |
|-|-|-|-|-|-|
| MS-1000 | 2026-02-02 | actual | TK_Complete | 0.0 | 0.0 |
| MS-1010 | 2026-08-05 | actual | TK_Complete | 0.0 | 13.0 |
| MS-1020 | 2026-09-21 | actual | TK_Complete | 0.0 | 11.0 |
| MS-1050 | 2027-02-03 | forecast | TK_NotStart | 0.0 | 25.0 |
| MS-1030 | 2027-03-17 | forecast | TK_NotStart | 0.0 | 20.0 |
| MS-1040 | 2027-06-01 | forecast | TK_NotStart | 0.0 | 36.0 |
| MS-1060 | 2027-08-04 | forecast | TK_NotStart | 0.0 | 36.0 |
| MS-1070 | 2027-08-18 | forecast | TK_NotStart | 0.0 | 36.0 |
| MS-1080 | 2027-08-20 | forecast | TK_NotStart | 0.0 | 36.0 |
| MS-1090 | 2027-10-05 | forecast | TK_NotStart | -10.0 | 36.0 |
| MS-1100 | 2027-10-05 | forecast | TK_NotStart | -10.0 | 36.0 |

## Notes

No note.

## Actions

Only the actions that apply to the latest update shown, DEMO-SS225:

- The finish moved by -10.0 working days since the previous update (positive = later): ask for the reason and review the critical path.
- Open activities with negative float: 37. Recover them: the schedule misses the must finish date or a constraint.
- DCMA checks failed: lags, fs_links, high_float, negative_float, missed_tasks, cpli, bei. Run the schedule quality audit on DEMO-SS225.
- Durations cut since the previous update: 2. Run the update integrity audit to see which and ask for the justification.
- Activities removed since the previous update: 1. Check that their scope was completed or transferred.
