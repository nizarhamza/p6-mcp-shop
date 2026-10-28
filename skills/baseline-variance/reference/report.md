# Baseline variance of {project}

Data date {data_date}, last schedule run (F9) {last_f9}.

[if: bl_used]
Compared with the baseline {bl_used} ({bl_source}), baseline data date {bl_data_date}. Activities are matched by Activity ID.
[end if]

[if: stale]
Warning: this project was changed after its last F9. Dates, float and variances are out of date until it is rescheduled in P6 (F9).
[end if]

[if not: bl_used]
No baseline: {project} has no project baseline and none was given. Assign a project baseline in P6 or run this skill again with the Project ID of a baseline. The variance cannot be reported.
[end if]

## Project finish

- Scheduled finish {finish}; baseline finish {bl_finish}; finish variance {fv_cd} cd, {fv_wd} wd proj (positive = later).
- Must finish by {must_finish}: the scheduled finish is {mf_cd} cd, {mf_wd} wd proj after it (negative = before).

## Activities

[if: act_error]
The activity comparison failed: {act_error}
[end if]

- Matched {matched}; only in the project (added) {added}; only in the baseline (removed) {removed}.
- Finishing later {later}, earlier {earlier}, same finish {same_finish}. Later ones: average {later_avg_cd} cd, largest {later_max_cd} cd; earliest {earlier_max_cd} cd.
- Status changed {status_changed}; original duration changed {dur_changed}; name changed {name_changed}; no slip cause (calendar or date missing) {slip_unknown}.

Slip causes of the matched activities (late_start: the start moved; longer_duration: the start-to-finish span grew; on_time: same finish within 5 minutes of work):

[table: causes]

### Largest finish variances

Start and finish are actual, else early dates of the last F9. Start var + duration delta = finish var, in working days of each activity's calendar.

[table: moved]

## Logic changes

[if: rel_error]
The relationship comparison failed: {rel_error}
[end if]

- Relationships matched {rel_matched}; added {rel_added}; removed {rel_removed}; lag changed {rel_lag_changed}.

[table: links]

## Earned value at the data date (units, h)

[if: pc_error]
The progress curve failed: {pc_error}
[end if]

- Baseline planned {bl_planned}, earned {earned}, actual {actual}.
- Schedule variance (earned - baseline planned) {ev_variance}; SPI (earned / baseline planned) {spi}; actual / baseline planned {spi_actual}.

Units are labor and nonlabor assignments, spread linearly between their dates (an approximation of P6's spread); earned = budget x activity % complete.
