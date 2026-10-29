# Update integrity audit of DEMO-SS225 against DEMO-SS225_PREV

Data date of the previous update 2026-10-19, of this update 2026-10-26 (7.0 calendar days later). Last schedule run (F9) of this update 2026-10-26 17:30. Read only: nothing was written to the database.

Each flag is a question to raise with whoever submitted the update, not proof of manipulation: a change can be a correct revision (new information, a re-plan, a corrected error). Ask for the reason and the evidence behind it.

## Flags

10 of the 11 flags have a count. Each table below shows at most 10 rows of its flag.

| Flag | Count |
|-|-|
| open_end_to_finish | 1 |
| negative_float_cleared_by_constraint | 6 |
| must_finish_moved | 1 |
| actuals_changed | 2 |
| duration_cut | 2 |
| links_removed_on_critical | 1 |
| rel_type_or_lag_changed | 2 |
| schedule_options_changed | 1 |
| calendars_changed | 2 |
| deleted_in_progress_or_critical | 1 |
| data_date | 0 |

### Open ends tied to the finish or start (1)

| Activity | Had no | Now linked to |
|-|-|-|
| COM-HO-1020 - Operator training | successor | MS-1100 - Project completion |

### Negative float cleared by a constraint or the must finish date (6)

| Activity | Float before (d) | Float now (d) | Cause |
|-|-|-|-|
| COM-PRE-1040 - 225 kV cable sheath and high-voltage tests | -14.0 | 6.0 | the must finish by date, the source of its float, moved later |
| COM-PRE-1120 - Metering tests | -20.0 | 0.0 | the must finish by date, the source of its float, moved later |
| CON-HV-1020 - 225 kV GIS gas filling and checks | -20.0 | 0.0 | the must finish by date, the source of its float, moved later |
| CON-HV-1070 - 225 kV cable terminations | -20.0 | 0.0 | the must finish by date, the source of its float, moved later |
| CON-SEC-1010 - Auxiliary transformer installation | -7.0 | 143.0 | its own constraint was removed or changed |
| PRC-AUX-1060 - Auxiliary transformers - shipping and delivery to site | -7.0 | 143.0 | the constraint of CON-SEC-1010, the source of its float, was removed or changed |

### Must finish by date moved

Previous update 2027-08-02 17:00, this update 2027-08-16 17:00: moved by 10.0 working days of the project calendar.

### Actual dates changed (2)

| Activity | Date | Before | Now |
|-|-|-|-|
| PRC-GIS225-1040 - 225 kV GIS - manufacturing | actual_start | 2026-07-23 08:00 | 2026-07-16 08:00 |
| PRC-MVS-1040 - MV switchgear - manufacturing | actual_finish | 2026-09-24 17:00 | 2026-09-25 17:00 |

### Durations cut (2, of which critical before: 1)

| Activity | Original before (d) | Original now (d) | Remaining before (d) | Remaining now (d) |
|-|-|-|-|-|
| COM-ENR-1050 - Trial operation | 30.0 | 20.0 | 30.0 | 20.0 |
| CON-SEC-1060 - Perimeter lighting and CCTV | 20.0 | 15.0 | 20.0 | 15.0 |

### Links removed on critical or near critical work (1)

| Predecessor | Successor | Type | Successor float before (d) |
|-|-|-|-|
| COM-PRE-1090 - Auxiliary systems tests (AC/DC, batteries) | COM-ENR-1000 - Energization procedure approval | FS | -56.0 |

### Link types or lags changed (2)

| Predecessor | Successor | Change | Before | Now |
|-|-|-|-|-|
| CON-FDN-1000 - GIS building foundations | CON-BLD-1000 - GIS building structure | lag | FS 3 d | FS 5 d |
| CON-HV-1060 - 225 kV cable laying | CON-HV-1070 - 225 kV cable terminations | type | SS 10 d | FS 0 d |

### Schedule options changed (1)

| Option | Before | Now |
|-|-|-|
| sched_open_critical_flag | Y | N |

### Calendars changed (2)

| Activity or calendar | Before | Now | Detail |
|-|-|-|-|
| CON-HV-1000 - Gantry steel structures and busbars | DEMO 6-Day Workweek 8h | DEMO 5-Day Workweek 8h | the activity is on another calendar |
| DEMO 5-Day Workweek 8h | 17 exceptions | 18 exceptions | 1 added or changed (2027-11-11) |

### Activities deleted while in progress or critical (1)

| Activity | Status before | Float before (d) | Critical before |
|-|-|-|-|
| CON-SITE-1050 - Temporary site facilities | TK_Active | 125.0 | no |

## Questions to raise with the contractor

- Open ends: why were these activities tied straight to the project finish (or start)? Which work do they really drive, or follow?
- Negative float: why were these constraints removed or changed, or the must finish date moved, when this cleared negative float? Which recovery of the work supports the new float?
- Must finish date: was the new must finish by date agreed, by an approved extension of time or change order? Please give its reference.
- Actual dates: why were actual dates reported in the previous update changed? Please provide the site records that support the new dates.
- Durations: what supports the shorter durations (more resources, another method, less scope)? For the critical ones, how will they be achieved?
- Removed links: why were these links to critical or near critical work removed? Is the logic they stood for no longer valid?
- Link types and lags: why were these relationship types or lags changed? Do the new ones match how the work will be done?
- Schedule options: why were these scheduling options changed? They change how every date and float is calculated.
- Calendars: why were these calendars or calendar assignments changed? Are the new working times and holidays agreed?
- Deleted activities: why were activities that were in progress or critical deleted? Was their scope completed, moved or removed?
