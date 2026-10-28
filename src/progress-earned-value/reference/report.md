# Progress and earned value of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Baseline {bl_used}. Units are hours of labor and nonlabor resources.

[if: stale]
Warning: this project was changed after its last F9. Dates, float and progress figures are out of date until it is rescheduled in P6 (F9).
[end if]

[if not: bl_used]
No baseline: {project} has no project baseline and none was given, so baseline planned values, earned value variance and SPI are n/a. Assign a project baseline in P6 or run this skill again with the Project ID of a baseline.
[end if]

## Percent complete

- Units % complete (actual / at completion, P6 Units % Complete): {units_pct}.
- Physical % complete (weighted by budget units): {physical_pct}; duration % complete: {duration_pct}; activities completed: {completed_pct}.
- Baseline planned % at the data date: {bl_planned_pct}.
- Activity units (h): budget {budget_units}, actual {actual_units}, remaining {remaining_units}.
- Default percent complete type: {pct_type}. Activities whose physical % and units % differ: {mismatch}.

## Earned value at the data date (units, h)

[if: pc_error]
The progress curve failed: {pc_error}
[end if]

- Budget {budget}; at completion {at_completion}.
- Baseline planned (planned value) {bl_planned}; planned on the current dates {planned}.
- Earned (budget x activity % complete) {earned} ({earned_pct} of budget); actual {actual} ({actual_pct} of budget).
- Schedule variance (earned - baseline planned) {ev_variance}; SPI (earned / baseline planned) {spi}; actual / baseline planned {spi_actual}.

[if: ev_other]
WBS nodes with another earned value technique than activity percent complete (earned ignores it): {ev_other}.
[end if]

[if: clipped]
Assignments with actual dates after the data date (their actuals are counted at the data date): {clipped}.
[end if]

[if: clamped]
Assignments with a remaining start before the data date (their remaining work starts at the data date): {clamped}.
[end if]

## S-curve by {period}

The curve has {period_count} periods; this table shows at most the first 36. Period values are spread linearly over calendar time between the assignment dates (an approximation of P6's spread); only the values at the data date are exact. Cumulative % are of each curve's own budget; forecast = actual, then remaining.

[table: periods]

## Progress by WBS (level 1)

[table: wbs]
