# Authoring core skills

Core skills are the P6 skills the maintainer writes and MCP for Primavera P6 (called P6 MCP before 2.0) 1.9.0
and later installs on first start (the names in `core.json`). Each one lives in `src/<name>/`;
`python tools/catalog.py build` turns it into the published folder `skills/<name>/`. Shared skills (from the
Share a P6 skill issue form) keep their own path: see the README.

## The accuracy contract

A report is only as good as its least reliable figure, so a core skill never lets the model work a figure
out. Every skill follows these rules, and the build and the tests enforce them.

1. Every number, date and count in a report is a **slot**: one field of one tool result (`step.path` in
   `spec.json`), written in a fixed format (date = first 10 characters, YYYY-MM-DD; percent and days to 1
   decimal; null = "n/a"). The model never adds, subtracts, divides, counts rows or matches rows of two
   results.
2. A figure no tool returns is added to the server first (MCP for Primavera P6), never computed by the skill.
3. Counts come from `total`, `counts` or `totals` fields. A table shows one page (its cap is the limit of its
   call); when the call has more pages it ends with "Showing the first <returned> of <total> <noun>.", both
   numbers copied from the call.
4. Every column head that holds a duration or float names its unit: (wd) working days of each activity's
   calendar, (wd proj) working days of the project calendar, (cd) calendar days, (d) days of each
   activity's calendar, (h) hours. The build refuses a head without it.
5. Stop rules and warnings have fixed wording in `report.md` (an `[if: slot]` block) or `checks.md`: no data
   date, no baseline, a stale schedule, pre-flight errors, an engine that is not trusted.
6. Activities are written "A1230 - Activity name" (format `id_name`), projects by Project ID; template
   projects are never listed.
7. Before answering, the model runs `checks.md`: the cross-checks of `spec.json` (fields of two calls that
   must be equal, such as the data date) and the stop rules.

The proof is automatic: the golden harness (`tools/golden.py`) runs the skill's calls through the app's own
tools on a public demo database and renders the report exactly as the skill asks the model to; that
rendering is the published `reference/example.md`, and every slot and table cell is compared with an
independent oracle (`tests/oracles/<name>.py`: SQL on P6's tables, never the app's code).

## Anatomy

```
src/<name>/
  meta.json               name, title, description, args, min_app_version ("1.9.0"), example_args
  template.md             the SKILL.md workflow (at most 8,000 characters), with the lines [steps], [rules]
  reference/report.md     the report to fill: {slot} placeholders, [table: name] lines, [if: slot] blocks
  reference/checks.md     stop rules and checks before answering (written by hand)
  reference/spec.json     calls, slots, tables and cross-checks (machine readable, also read by the model)
tests/oracles/<name>.py   one independent value per slot and per table
```

`build` writes `skills/<name>/`: `p6mcp.json` (what the app installs: the shared fields plus tools, writes,
min_app_version, version, author nizarhamza, license, published_at), `SKILL.md` (as the app writes it for
the clients: `p6mcp.skills.skill_md`) and five reference files: the three above, `reference/fields.md`
(generated from `spec.json`: calls, formats, units, every slot and column with its field, unit, format and
meaning) and `reference/example.md` (the harness rendering on the demo project). In `template.md` the line
`[steps]` becomes the numbered calls of `spec.json` (a `{=step.path}` argument is written `<step.path>`
there) and the line `[rules]` the writing rules every core skill shares (`golden.WRITE_RULES`: placeholders,
tables and their Showing or "Only the first" lines, `[if:]` blocks, number rounding and thousands, no
arithmetic, notes ignored, the user's language, the checks); a skill's own instructions go in a "For this
skill:" paragraph after it. The template is published without leading or trailing line breaks, as the app's
Skills page stores it. The app fills every field of a template: the only braces `template.md` may hold are the
skill's
argument placeholders (write "a slot name in curly braces", never `{slot}`).

The core set (`core.json`) is the set of 15 skills: weekly-update-review, schedule-quality-audit,
update-import-safely, delay-whatif, baseline-variance, export-dashboard, list, lookahead-brief,
progress-earned-value, float-near-critical, milestone-tracker, resource-wbs-summary, and since 1.10.0
update-integrity-audit, schedule-risk and logic-date-integrity. The app bundles a copy of it for offline
first starts: after a catalog commit, run `python tools/bundle_core_skills.py <catalog>` in the MCP for
Primavera P6 checkout.

The version goes up by one only when the published content changes; a build with nothing new rewrites
nothing, so `git status` stays clean (the check workflow fails otherwise). Built-in entries of older
catalogs are removed. `index.json` flags the names of `core.json` with `"core": true`; a core name must have
its `src/` folder, and an issue sharing a skill under a core name is refused.

Every text is ASCII without a double hyphen (the app's house rule, `p6mcp.skills.house_problems`): this is
why the markers are `[table: name]` and not HTML comments, and why tables use `|-|-|` separator rows.

## spec.json

```json
{
  "spec": 1,
  "steps": [
    {"id": "wbs", "tool": "p6_group_summary",
     "args": {"project": "{project}", "by": "wbs", "wbs_level": "{wbs_level}", "limit": 30},
     "why": "activities and units per WBS node, totals, data date"}
  ],
  "slots": {
    "data_date": {"step": "wbs", "path": "schedule_state.data_date", "format": "date",
                  "meaning": "data date of the project"},
    "units_pct": {"step": "res", "path": "totals.units_pct", "format": "pct1", "unit": "%",
                  "meaning": "units % complete: actual / at completion units, labor and nonlabor"}
  },
  "tables": {
    "wbs": {"step": "wbs", "rows": "rows", "cap": 30, "noun": "WBS nodes", "empty": "No activity in this project.",
            "totals": {"path": "totals", "label": "Total"},
            "columns": [
              {"key": "wbs", "head": "WBS", "path": ["group", "name"], "format": "id_name"},
              {"key": "min_tf", "head": "Min total float (d)", "path": "min_tf_d", "format": "n1", "unit": "d"}
            ]}
  },
  "checks": [
    {"equal": ["wbs.schedule_state.data_date", "status.schedule_state.data_date"],
     "text": "same data date in both group summaries"}
  ]
}
```

- **steps**: `id` (a short name the slots refer to), `tool`, `args`, `why` (shown in the call list),
  `optional`, `when`. The calls run in this order, one page each. In `args` (lists and dicts too):
  - `"{arg}"` alone is a skill argument; an argument whose default is a whole number is passed and written
    as a number (`"add_remaining_days": "{delay_days}"` gives 10); an argument that is empty (default `""`,
    such as `baseline`) leaves its key out of the call, and the call list says so.
  - `"{=step.path}"` alone is a field of an earlier call's result (`"target": "{=late.rows.0.task_code}"`).
    When it is null or missing, or that call failed, the step is skipped: its result is `{error}`.
  - Every key must be a parameter of the tool. `dry_run`, `confirmation_token`, `confirmation_text` and
    `confirm` are refused: a write tool (`p6_import_xer`) only runs as a dry run, and a skill applies a
    change only through prose in `template.md`, after the user's explicit yes.
  - `"when": "<arg>"`: the call runs only when that optional argument (default `""`) is given; when it is
    empty the step is skipped like a null `{=step.path}` (its result is `{error}`, its slots are null, its
    tables print nothing) and the call list says so. Put what uses it in `[if: slot]` blocks, so the report
    without the argument stays the report the skill gave before (a key left out would change the call
    instead: `other=` empty compares with the project baseline).
  - `"optional": true`: a ValueError of the call (no baseline, no previous snapshot) becomes
    `{"error": message}`; the slots of that step are null and its tables print nothing. A slot with
    path `error` holds the message (null when the call worked): use it in an `[if: ...]` block.
- **slots**: `step`, `path` (dotted keys, list indexes allowed: `rows.0.task_code`), `format`, `unit`
  (optional), `none` (text for null, default `n/a`), `meaning`. A path the tool does not return fails the
  build; a field under a null one is null (`suggestion.reason` when `suggestion` is null). In a table, a
  field some rows lack is null in those rows; a field no row has fails the build. `confirmation_token`, `token_expires_in_s`, `confirmation_text_required` and `next` of a write
  tool are refused.
- **tables**: `step`, `rows`, `cap`, `noun`, `empty` (text when the list is empty), `filter` (optional: keep
  the rows whose field is true; then the cap applies to the kept rows), `totals` (optional `{path, label}`:
  a last row from a dict with the same field names, such as `totals`), `meaning`, `columns` [{`key` (unique,
  used by the oracle), `head`, `path` (a pair for `id_name`), `format`, `unit`, `none`, `in_totals` (false:
  blank in the totals row)}]. Rows keep the tool's order.
  - `rows: "rows"` is a paged list: `cap` equals the call's `limit`, and when the call has more pages the
    table ends with "Showing the first <returned> of <total> <noun>." (no row is counted).
  - Any other list (`dcma_failed`, `warnings`) or dict: a dict gives one row per item in order, its key in
    `_key` and, for a plain value, the value in `_value` (`counts` per table of an import, `slip_causes`); a
    column path `""` is the row itself (a list of texts). When the list is longer than `cap` the table ends
    with "Only the first <cap> <noun> are shown."
- **checks**: `equal` (two `step.path` or more that must hold the same value), `text`. The harness fails on
  the demo when one differs; `checks.md` tells the model what to do when one differs.

Formats: `text`, `int` (a comma between thousands: 1,227), `date` (YYYY-MM-DD), `datetime` (YYYY-MM-DD
HH:MM), `n0`, `n1`, `n2` (the number as written in the result, rounded halves away from zero, a comma
between thousands: -104274.95 in n1 is -104,275.0), `pct1` (the same to 1 decimal, then %), `flag` (yes /
no), `id_name` ("ID - Name"; the ID alone when the name is null, the none text when the ID is null), `list`
(the items of a list joined by ", ", an empty list = the none text; `text` refuses a list). Units: `wd`,
`wd proj`, `cd`, `d`, `h`, `qty`, `cost`, `%`, `count`.

## report.md

- `{slot}`: the slot written in its format; `{arg}`: a skill argument as given (`{project}`).
- A line `[table: name]`: the table (heads, `|-|` row, one line per row, the totals row, then the "Showing
  the first" line when the call has more pages; the `empty` text when there is no row).
- `[if: slot]` ... `[end if]`: kept only when the slot is true (`[if not: slot]`: false). True is true, a
  number other than 0, a text or a list that is not empty, an `id_name` pair whose ID is not null; null, 0,
  false and "" are false. Blocks do not nest. Use them for warnings, stop rules and actions with fixed wording (a stale schedule, no baseline,
  "N activities are out of sequence": `[if: oos_total]`).
- Headings and sentences are written in English; the model translates them, never the values.

Every slot and table of `spec.json` must be used by `report.md`, and every placeholder must be a slot or an
argument: the build lists what is missing.

## Adding a slot

1. Find the field: run `python tools/golden.py render <name>` after adding the call, or read the tool's
   docstring. If no tool returns the figure, add the field to the app first (accuracy contract, rule 2).
2. Add the slot to `spec.json` (`step`, `path`, `format`, `unit`, `meaning`) and its placeholder to
   `report.md` (or a column to a table: `key`, `head` with the unit, `path`, `format`).
3. Add its oracle to `tests/oracles/<name>.py` (`SLOTS[slot]`, or the column key in the rows `TABLES[table]`
   returns): the value computed again with SQL on P6's tables. For a text whose wording is the tool's, return
   `Contains(...)` with the parts that carry the data. Never import the app's server for an oracle.
4. Run `python tools/catalog.py build`, then `python -m pytest`. Commit `src/`, `skills/`, `index.json` and
   the oracle together.

A new skill: create `src/<name>/` (copy the pilot `resource-wbs-summary`), add its oracle module, add the name
to `core.json` when it belongs to the core set, build, test.

## Running the harness

Needs an MCP for Primavera P6 checkout with its tests (the demo fixture is `tests/fixtures/make_demo.py`) on
`PYTHONPATH` and its dependencies installed (`pip install <checkout> pytest`, or the checkout's virtual
environment). `P6MCP_SRC` names the checkout when `p6mcp` is imported from elsewhere. The harness builds the
demo database in a temporary folder and points the app at it through a throwaway config: it never reads your
settings or your databases.

```bash
export PYTHONPATH=../p6mcp
python tools/golden.py render resource-wbs-summary   # print the report on the demo project
python tools/golden.py verify resource-wbs-summary   # render, limits, house rules and oracles of one skill
python tools/catalog.py build                        # write skills/ and index.json
python tools/golden.py check                         # every example.md equal to its rendering
python -m pytest                                     # oracles, harness, build and catalog tests
```

PowerShell: `$env:PYTHONPATH = "..\p6mcp"`, then the same commands.

`example_args` in `meta.json` give the arguments of the golden run; `{work}` in them is the harness work
folder, which holds the demo database and the two demo XER files (`{work}/DEMO-SS225.xer`,
`{work}/DEMO-SS225_BL.xer`) and receives output files (`{work}/DEMO-SS225.xlsx`). `example.md` shows that
folder as `C:\P6\demo`. Before each skill's run the harness removes the health snapshots and output files an
earlier skill left, so a rendering never depends on the order skills run in; a rendering must not show
anything that changes between runs (snapshot ids, times of day of the run, durations of the call).

The demo project DEMO-SS225 (a 225/63 kV GIS substation, 214 activities, 332 links, 35 WBS nodes, 15
invented resources including a crane and a cable material) is generated by the app's CPM engine and imported
with `p6_import_xer`: an update at the data date 2026-10-26 with progress, late work, negative float, the
driving path and five float paths, and its baseline DEMO-SS225_BL set as project baseline. All its data is
invented, so example reports can be published.

## Limits

The app's own: `template.md` at most 8,000 characters after `[steps]` is expanded, five reference files of
at most 12,000 characters each (10,000 before 1.10.0: a skill with a larger file needs
`min_app_version` 1.10.0), the whole skill at most 60,000 characters as JSON. A core skill has exactly
five reference files, so keep `spec.json` compact (one line per column) and give tables caps that keep
`example.md` short.
