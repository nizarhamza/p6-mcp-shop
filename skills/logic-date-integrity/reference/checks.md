# Checks before answering

## Stop rules (write the sentence, then stop)

- A call says the project is not found: "Project <project> was not found: check the Project ID (p6_list_projects)."
- p6_cpm_validate says the project has no data date or that the network has a loop: repeat its message and
  stop (P6 cannot schedule a loop either).

## Warnings (fixed wording in report.md)

- schedule_state.stale is true: keep the warning; the probable cause of every row then says the project was
  edited since its last F9.
- trusted is false (or the match rate is n/a): keep the sentence asking for a reschedule and a resubmission,
  or an explanation of the mismatches.
- The sentence on running this check before F9 is always kept.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The match rates are the fields match_rate and match_rate_completed, never a share you worked out from the
  counts.
- The activities table keeps the rows in the order returned and stops at 15; when cv has more pages
  (next_offset not null) it ends with "Showing the first <returned> of <total> activities that differ.",
  both numbers copied from cv.
- The options table lists the options as returned (at most 40), the value as stored.
- Activities are written "Activity ID - name".
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
