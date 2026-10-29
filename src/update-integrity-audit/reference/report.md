# Update integrity audit of {project} against {previous}

Data date of the previous update {dd_before}, of this update {data_date} ({dd_delta} calendar days later). Last schedule run (F9) of this update {last_f9}. Read only: nothing was written to the database.

{caveat}

[if: stale]
Warning: this update was changed after its last F9. Its dates and float are out of date until it is rescheduled in P6 (F9).
[end if]

## Flags

{raised} of the 11 flags have a count. Each table below shows at most 10 rows of its flag.

[table: summary]

[if: n_open_end]
### Open ends tied to the finish or start ({n_open_end})

[table: t_open_end]

[end if]
[if: n_neg]
### Negative float cleared by a constraint or the must finish date ({n_neg})

[table: t_neg]

[end if]
[if: n_must]
### Must finish by date moved

Previous update {must_before}, this update {must_after}: moved by {must_wd} working days of the project calendar.

[end if]
[if: n_act]
### Actual dates changed ({n_act})

[table: t_act]

[end if]
[if: n_cut]
### Durations cut ({n_cut}, of which critical before: {n_cut_crit})

[table: t_cut]

[end if]
[if: n_links]
### Links removed on critical or near critical work ({n_links})

[table: t_links]

[end if]
[if: n_rel]
### Link types or lags changed ({n_rel})

[table: t_rel]

[end if]
[if: n_opt]
### Schedule options changed ({n_opt})

[table: t_opt]

[end if]
[if: n_cal]
### Calendars changed ({n_cal})

[table: t_cal]

[end if]
[if: n_del]
### Activities deleted while in progress or critical ({n_del})

[table: t_del]

[end if]
[if: n_dd]
### Data date

The data date did not move forward: previous update {dd_before}, this update {data_date}.
[end if]

## Questions to raise with the contractor

[if not: raised]
No flag was raised: there is no question to raise from this comparison.
[end if]
[if: n_open_end]
- Open ends: why were these activities tied straight to the project finish (or start)? Which work do they really drive, or follow?
[end if]
[if: n_neg]
- Negative float: why were these constraints removed or changed, or the must finish date moved, when this cleared negative float? Which recovery of the work supports the new float?
[end if]
[if: n_must]
- Must finish date: was the new must finish by date agreed, by an approved extension of time or change order? Please give its reference.
[end if]
[if: n_act]
- Actual dates: why were actual dates reported in the previous update changed? Please provide the site records that support the new dates.
[end if]
[if: n_cut]
- Durations: what supports the shorter durations (more resources, another method, less scope)? For the critical ones, how will they be achieved?
[end if]
[if: n_links]
- Removed links: why were these links to critical or near critical work removed? Is the logic they stood for no longer valid?
[end if]
[if: n_rel]
- Link types and lags: why were these relationship types or lags changed? Do the new ones match how the work will be done?
[end if]
[if: n_opt]
- Schedule options: why were these scheduling options changed? They change how every date and float is calculated.
[end if]
[if: n_cal]
- Calendars: why were these calendars or calendar assignments changed? Are the new working times and holidays agreed?
[end if]
[if: n_del]
- Deleted activities: why were activities that were in progress or critical deleted? Was their scope completed, moved or removed?
[end if]
[if: n_dd]
- Data date: why did the data date not move forward since the previous update?
[end if]
