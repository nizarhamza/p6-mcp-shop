# Look-ahead brief of DEMO-SS225

Window from 2026-10-26 08:00 to 2026-11-09 08:00 (end excluded): 14 calendar days from the data date 2026-10-26. Last schedule run (F9) 2026-10-26 17:30. Dates and float come from that run: open activities use their remaining dates, LOE and WBS summary activities are left out.

## In the window

- Activities listed: 16.
- In progress: 11; starting: 5; finishing: 4; spanning the whole window: 0.
  These categories overlap (an activity can be in progress and finishing): they do not add up to the activities listed.
- Critical: 2 (project setting CT_TotFloat: total float <= 0 h (critical_drtn_hr_cnt); open activities).

## Weeks

In the tables below, categories are the reasons an activity is listed (in_progress, starting, finishing, spanning); forecast start is the actual start of an activity in progress, else its remaining start; forecast finish is its remaining finish. Start week and finish week are the weeks of the window holding those dates ("outside" when the date is not in the window).

| Week | From | To (excluded) |
|-|-|-|
| 1 | 2026-10-26 08:00 | 2026-11-02 08:00 |
| 2 | 2026-11-02 08:00 | 2026-11-09 08:00 |

## Critical activities

| Activity | Status | Categories | Forecast start | Forecast finish | Start week | Finish week | Total float (d) | Critical |
|-|-|-|-|-|-|-|-|-|
| PRC-GIS225-1040 - 225 kV GIS - manufacturing | TK_Active | in_progress | 2026-07-16 | 2027-01-27 | outside | outside | -5.0 | yes |
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | TK_Active | in_progress | 2026-07-30 | 2027-04-02 | outside | outside | -36.0 | yes |

## All activities of the window

| Activity | Status | Categories | Forecast start | Forecast finish | Start week | Finish week | Total float (d) | Critical |
|-|-|-|-|-|-|-|-|-|
| PRC-GIS63-1040 - 63 kV GIS - manufacturing | TK_Active | in_progress | 2026-07-07 | 2026-12-14 | outside | outside | 60.0 | no |
| PRC-GIS225-1040 - 225 kV GIS - manufacturing | TK_Active | in_progress | 2026-07-16 | 2027-01-27 | outside | outside | -5.0 | yes |
| PRC-PCP-1040 - Protection and control panels - manufacturing | TK_Active | in_progress | 2026-07-24 | 2026-11-13 | outside | outside | 61.0 | no |
| PRC-TR-1040 - Power transformers 225/63 kV - manufacturing | TK_Active | in_progress | 2026-07-30 | 2027-04-02 | outside | outside | -36.0 | yes |
| CON-BLD-1000 - GIS building structure | TK_Active | in_progress | 2026-09-23 | 2026-11-30 | outside | outside | 25.0 | no |
| PRC-HVC-1060 - 225 kV cables and accessories - shipping and delivery to site | TK_Active | in_progress, finishing | 2026-09-30 | 2026-11-03 | outside | 2 | 108.0 | no |
| CON-BLD-1060 - Internal roads and gravel surfacing | TK_Active | in_progress | 2026-10-05 | 2026-11-20 | outside | outside | 121.0 | no |
| PRC-AUX-1060 - Auxiliary transformers - shipping and delivery to site | TK_Active | in_progress, finishing | 2026-10-07 | 2026-10-29 | outside | 1 | 143.0 | no |
| PRC-LVB-1050 - LV AC/DC boards, batteries and chargers - factory acceptance test | TK_Active | in_progress, finishing | 2026-10-20 | 2026-10-26 | outside | 1 | 114.0 | no |
| PRC-STL-1060 - Steel structures and gantries - shipping and delivery to site | TK_Active | in_progress, finishing | 2026-10-23 | 2026-11-05 | outside | 2 | 111.0 | no |
| CON-BLD-1040 - Control building finishing | TK_Active | in_progress | 2026-10-23 | 2026-11-27 | outside | outside | 71.0 | no |
| PRC-SCA-1060 - SCADA and telecom equipment - shipping and delivery to site | TK_NotStart | starting | 2026-10-26 | 2026-11-16 | 1 | outside | 120.0 | no |
| PRC-LVB-1060 - LV AC/DC boards, batteries and chargers - shipping and delivery to site | TK_NotStart | starting | 2026-10-27 | 2026-11-09 | 1 | outside | 114.0 | no |
| CON-SEC-1010 - Auxiliary transformer installation | TK_NotStart | starting | 2026-10-30 | 2026-11-10 | 1 | outside | 143.0 | no |
| CON-HV-1060 - 225 kV cable laying | TK_NotStart | starting | 2026-11-04 | 2026-12-09 | 2 | outside | 108.0 | no |
| CON-HV-1000 - Gantry steel structures and busbars | TK_NotStart | starting | 2026-11-06 | 2026-12-04 | 2 | outside | 111.0 | no |

## Actions

- Review the 2 critical activities of the window first, with their owners: confirm their forecast dates and what they wait for.
- Collect the progress of the 11 activities in progress before the next update: actual dates, remaining duration and percent complete.
- Check that the 5 activities starting in the window are ready: predecessors finished, crews, materials and permits available.
