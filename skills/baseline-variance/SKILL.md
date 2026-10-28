---
name: p6-baseline-variance
description: "Variance of a project against its baseline (or another project): finish variance, slipped activities, link changes and SPI. Use when the user asks to compare a project with its baseline or with another version."
---
<!-- p6mcp skill: written by P6 MCP Settings, overwritten on the next install -->

# Baseline variance

Inputs (take them from the user's message; ask for a required one that is missing, use the default when an optional one is empty):
- project: Project ID as shown in P6
- baseline: Project ID of the baseline (empty = the project baseline) (may be empty)

Variance of project <project> against the baseline "<baseline>" (when it is empty, use the project
baseline: leave other= and baseline= out of the calls below).

Steps:
1. p6_compare_projects(project="<project>", other="<baseline>", section="activities",
   min_variance_days=1): the summary (finish variance, activities added, removed, later and earlier)
   and the most slipped activities first.
2. p6_compare_projects(project="<project>", other="<baseline>", section="relationships"): logic added,
   removed and lags changed.
3. p6_progress_curve(project="<project>", baseline="<baseline>"): planned against actual and earned at
   the data date (to_date: spi, variance).

Report: project finish against the baseline (calendar days); the slipped activities grouped by cause
when visible (late start, longer duration, logic change); added and removed scope and logic; SPI and
planned against earned at the data date; a short conclusion on the recovery needed. If there is no
baseline, say so and stop.

Rules: name projects by Project ID and activities by Activity ID. Dates, float and the critical
path come from the last P6 schedule run (F9): if schedule_state says stale or edited since the last
schedule, say so first. Durations and float are in days. Read every page you rely on (offset =
next_offset). Writes take two calls: the first one (dry_run=true, the default) only returns the plan and a
confirmation_token; repeat it with dry_run=false and that token only after the user's explicit yes to
that plan. After a write, ask the user to open P6 and press F9.
