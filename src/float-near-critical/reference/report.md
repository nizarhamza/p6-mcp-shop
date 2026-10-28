# Float and near-critical activities of {project}

Data date {data_date}, last schedule run (F9) {last_f9}. Float of that run, in days of each activity's calendar.

[if: stale]
Warning: this project was changed after its last F9. Float, float paths and critical counts are out of date until it is rescheduled in P6 (F9).
[end if]

## Total float

- Open activities analysed: {activities} (not completed; LOE and WBS summary left out); without a total float: {no_tf}.
- Total float (d): minimum {tf_min}, maximum {tf_max}, mean {tf_mean}, median {tf_median}.
- Negative total float: {negative}; zero total float: {zero}; critical: {critical} ({critical_definition}).
- On the longest path (driving path flag): {longest_path}.
- Total float at or below {near_days} d, critical included: {within_near}.
- Near-critical, total float above 0 d and at or below {near_days} d: {near_total} ({near_definition}).
- Total floats that are not whole days: {tf_not_whole}.

[if: negative]
Warning: {negative} open activities have negative total float: they finish later than a constraint or the project must finish date allows.
[end if]
[if not: ranges_covered]
Warning: the range counts do not add up to the activities analysed: do not use the distribution below.
[end if]

## Float distribution

Ranges in days: [a, b) includes a and excludes b, (a, b] excludes a and includes b. Percentages of the {activities} open activities analysed.

[table: buckets]

## Float paths

Source: {fp_source} (float_path: P6's multiple float paths of the last F9; driving_path_flag: no float path stored).

[table: paths]

[table: path_rows]

## Near-critical activities (total float above 0 d and at or below {near_days} d)

By total float, then start. Activities with total float at or below 0 are left out of this table.

[table: near]
