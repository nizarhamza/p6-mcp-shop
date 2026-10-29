# Schedule risk of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Read only: nothing was written to the database.

[if: stale]
Warning: this project was changed after its last F9. The simulation starts from out of date dates until it is rescheduled in P6 (F9).
[end if]

[if not: trusted]
Warning: this server's CPM engine does not reproduce the last F9 of this project (match rate {match_rate}), so the simulated dates may not follow P6's. Run the logic-date-integrity skill to see the differences before using these figures.
[end if]

## Finish

- Deterministic finish (the engine, durations unchanged): {det_finish}, {det_activity}; last F9: {stored_finish}.
- P10 {p10}; P50 {p50}; P80 {p80}; P90 {p90}.
- Chance to finish by the deterministic finish: {on_time_det}. Must finish by {must_finish}: chance {on_time_must}.
- P80 buffer: {p80_buffer} working days of the project calendar after the deterministic finish.

## Milestones

[table: milestones]

## Drivers

Share of the iterations in which each open activity sat on the critical path (the chain of links that set each start, back from the project finish); On today's path = on the critical path of the deterministic run. Min and Max are the remaining durations drawn from.

[table: drivers]

## Finish dates per week

[table: weeks]

## Assumptions

- {iterations_run} iterations, seed {seed_used}, engine version {engine_version}. Engine match rate with the last F9: {match_rate}.
- Remaining duration of {n_drawn} open activities drawn from a triangular range of {d_min} % (minimum), {d_mode} % (most likely) and {d_max} % (maximum) of the remaining duration.
[if: iterations_note]
- Iterations: {iterations_note}.
[end if]
- {caveat}
