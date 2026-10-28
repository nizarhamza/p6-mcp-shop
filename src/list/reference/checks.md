# Checks before answering

## Stop rules (write the sentence, then stop)

- p6_list_projects says the EPS is not found: "EPS <eps> was not found. EPS IDs: <the list in its message>." Then
  stop.
- p6_list_eps says there is no EPS node: repeat its message and stop.

## Before sending

- Every number, date and count is a slot or a table cell of reference/fields.md, copied from its field
  and written in its format. Nothing was added, subtracted, divided, counted or matched by you.
- The tables keep the rows in the order returned and stop at their cap (EPS 200, projects 200). A table
  whose call has more pages (next_offset not null) ends with its line "Showing the first <returned> of
  <total> ...", both numbers copied from that call.
- The number of projects is prj.total, never a count of the rows.
- Every project is written "Project ID - name". Template projects (status WS_Template or without an EPS)
  and baselines are never listed, counted or mentioned.
- Headings and sentences are in the user's language; values, IDs, names and number formats exactly as
  formatted.
