# P6 MCP skill shop

P6 skills shared by users of [P6 MCP](https://github.com/nizarhamza/p6-mcp), the MCP server for Primavera P6
Professional. A skill is a ready-made workflow (instructions for the AI, which P6 tools to call, optional
text reference files) in the [Agent Skills](https://agentskills.io) format.

## Install a skill

Open **P6 MCP Settings > Skill shop**, select a skill, read it, click **Install**, then **Save** and
**Update skills** on the MCP clients page. Or ask your AI client: "search the P6 skill shop for a look-ahead
skill" (tools `p6_shop_search`, `p6_shop_get`, `p6_shop_install`). Reading the shop needs no GitHub account.

Each skill is also a plain skill folder: `skills/<name>/SKILL.md` and its reference files can be copied to
`%USERPROFILE%\.claude\skills\p6-<name>` (the folder name must match the `name` in SKILL.md).

## Share a skill

In **P6 MCP Settings > Skills**, select one of your skills and click **Share on GitHub**. P6 MCP copies the
skill to your clipboard and your browser opens the [Share a P6 skill](../../issues/new?template=share-skill.yml)
form: sign in if asked (a free GitHub account is needed), paste the skill in the Skill field and click Create. The maintainer reviews it; once approved it is published here under the
Apache-2.0 license and appears in every P6 MCP Shop page within a few minutes. A new version of your own
skill is shared the same way (same name, same GitHub account).

No GitHub account? Export the skill to a zip file in P6 MCP and send it to a colleague: Import adds it.

## How publication works

- `skills/<name>/p6mcp.json` is what P6 MCP installs (the skill plus version, author, license, issue).
  `SKILL.md` and the reference files beside it are generated from it. `index.json` lists every skill with
  the SHA256 of its p6mcp.json; P6 MCP checks it before installing.
- The label **approved** on a share issue runs `.github/workflows/publish.yml`: it checks that a maintainer
  added the label, checks the skill with P6 MCP's own rules (`p6mcp.shop.check_shared` from the release
  `P6MCP_REF`: known tools only, description, text reference files only, sizes), writes the folder and
  `index.json`, commits, comments and closes the issue (label **published**). A refused skill gets a comment
  and the label **needs-changes**.
- A name belongs to its first author: another account must choose another name. Approving the same content
  again publishes nothing (no new version).

## Maintainer review checklist

Before adding **approved**:

1. The instructions do what the title and description say, and only that.
2. Write tools (`p6_update_*`, `p6_add_*`, `p6_delete_*`, `p6_import_xer`, `p6_restore_backup`...) are needed
   for the purpose, and the text never asks the AI to skip the dry run or the user's confirmation.
3. No client names, project names, schedule data, personal data or links to other sites.
4. Reference files are useful text (checklists, thresholds, examples).
5. Add the label right after reading: the workflow publishes the issue body as it is at that moment. Check
   the commit it makes.

To remove a skill, delete its folder, run `python tools/catalog.py index` (with a P6 MCP checkout on
`PYTHONPATH`) and commit. Labels used: `submission`, `approved`, `needs-changes`, `published`.

## License

Apache-2.0 (see [LICENSE](LICENSE)). Each skill is published under the same license by its author.
