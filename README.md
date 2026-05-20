# Chug

**Changelog management that works for teams and agents.**

Chug solves a deceptively annoying problem: keeping `CHANGELOG.md` up to date on a team without merge conflicts, inconsistent formatting, or deferred release notes.

The approach is borrowed from database migrations. Instead of editing `CHANGELOG.md` directly on every branch, each change gets captured in a small YAML file first. Those files accumulate while work is in progress. At release time, Chug rolls them into a new versioned section and deletes them. No conflicts. No ceremony. No special release platform required.

---

## The Problem

On a team, `CHANGELOG.md` is nobody's job and everyone's problem.

Editing it directly means:

- **Merge conflicts.** Every branch touches the same file at the top.
- **Inconsistent output.** Each contributor has a different idea of what belongs there.
- **Deferred work.** Changelog updates get skipped and batched later, when context is gone.
- **Agent friction.** Automated workflows that touch `CHANGELOG.md` need to parse, merge, and reformat it — fragile work that breaks silently.

Chug replaces all of that with a structured, automatable, merge-conflict-free workflow.

---

## How It Works

```
changes/
  2024-01-15T143022-fix-session-timeout.yml
  2024-01-16T091345-add-export-endpoint.yml
  2024-01-17T162801-update-rate-limits.yml
```

Each change is a small YAML file in a `changes/` directory. Branches create files, not edits. Files don't conflict with each other.

At release time:

```bash
chug release --version 1.4.0
```

Chug reads every pending file, groups entries by category, inserts a new version section into `CHANGELOG.md` at the configured marker, and deletes the processed files. The changelog grows forward; the pending files stay small and clean.

---

## Quick Start

**Install:**

```bash
uv tool install chug-cli
# or
pipx install chug-cli
```

Install from source while developing:

```bash
uv tool install .
# or
pipx install .
```

**Bootstrap a repo:**

```bash
chug init
```

This creates `chug.config.yml`, a `changes/` directory, and a `CHANGELOG.md` with an insertion marker — without touching anything that already exists.

**Record a change:**

```bash
chug new --description "Fix session timeout on mobile" --category bug
```

This writes a timestamped YAML file into `changes/`. No edits to `CHANGELOG.md`. No coordination required.

**Preview pending release notes:**

```bash
chug preview
```

Renders the full release output without touching any files. Use this to review before cutting a release.

**Cut a release:**

```bash
chug release --version 1.4.0
```

Inserts a new version section into `CHANGELOG.md` at the configured marker, then deletes the processed change files.

---

## Change File Format

Every change file looks like this:

```yaml
description: Fix session timeout on mobile
category: bug
stories:
  - sc-12345
authors:
  - name: Jane Doe
    github: janedoe
```

`description` and `category` are required. `stories` and `authors` are optional. Chug will attempt to populate `authors` from your local git config, and if it cannot determine author info it writes `authors: []` rather than failing.

---

## Configuration

`chug.config.yml` controls categories, changelog file path, story link formatting, and more:

```yaml
changelog_file: CHANGELOG.md
categories:
  - feature
  - chore
  - bug
story_format: "{id}"
story_link_template: "https://your-tracker.com/stories/{id}"
git_base_branch: main
```

### `changelog_style` — guidance for agents

You can optionally add a `changelog_style` field to document how your team wants changelog entries written. This is intended as structured guidance for future agent integrations and custom agent workflows.

```yaml
changelog_style: |
  Write descriptions from the user's perspective, not the implementer's.
  Be specific about what changed and why it matters.
  Avoid technical jargon unless it's the only precise term.
  Keep descriptions under 100 characters.
  Good: "Fix crash when opening documents with special characters in the filename"
  Avoid: "Handle edge case in path parsing logic"
```

This field has no effect on CLI behavior. Treat it as repository guidance for agents and automation, not as required configuration.

---

## GitHub PR Links (Optional)

If you provide a GitHub token, Chug enriches each changelog entry with a link to the pull request that introduced the change file:

```markdown
- Fix session timeout on mobile ([#87](https://github.com/owner/repo/pull/87), [Jane Doe](https://github.com/janedoe))
```

Without a token, Chug still works — entries render without PR links.

**How enrichment works:**

1. Chug finds the most recent commit on your base branch that touched the change file.
2. It looks up any pull requests associated with that commit.
3. PR links are added to the rendered entry.

All API calls are read-only. Chug never writes to GitHub.

```bash
export GITHUB_TOKEN=ghp_...
chug release --version 1.4.0
```

---

## GitHub Actions

Chug ships two companion GitHub Actions for teams that want changelog hygiene enforced in CI.

### `chug-validate`

Fails a pull request if no file in `changes/` was added or modified. Use this to make changelog entries a required part of every PR.

```yaml
name: Validate Changelog Entry

on:
  pull_request:

permissions:
  contents: read
  pull-requests: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: crayment/chug/.github/actions/chug-validate@v1
```

### `chug-release`

Runs `chug release` in CI and handles the parts that are easy to get wrong.

Staging a release commit in CI is trickier than it looks. After `chug release` runs, `CHANGELOG.md` has been updated and every file in `changes/` has been deleted. If all change files are removed, `changes/` becomes an empty directory — and empty directories don't exist in git. If there were no pending changes at all, nothing may have been modified. A naive `git add .` or `git add changes/` will fail or produce unexpected results in these cases.

`chug-release` handles all of it: it stages the changelog update, correctly handles deleted change files, and creates a clean local commit when the release actually changes repository files. That includes releases that intentionally write a `No changes` section.

```yaml
name: Update Changelog

on:
  workflow_dispatch:
    inputs:
      version:
        required: true

permissions:
  contents: write
  pull-requests: read

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: crayment/chug/.github/actions/chug-release@v1
        id: release
        with:
          version: ${{ inputs.version }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          commit-changes: true

      - name: Push changelog commit
        if: steps.release.outputs.committed == 'true'
        run: git push
```

These actions are public actions hosted in `crayment/chug`, so other repositories can reference them directly by tag. No special read token is required to fetch the action code.

Push is left to the calling workflow intentionally. Whether `git push` succeeds depends on branch protection rules, rulesets, and token permissions in the calling repository.

**Inputs:**

| Input | Required | Description |
|---|---|---|
| `version` | Yes | Version string for the release section |
| `github-token` | No | Enables PR link enrichment |
| `commit-changes` | No | Create a local git commit after release (default: `false`) |

**Outputs:**

| Output | Description |
|---|---|
| `changed` | Whether any changelog changes were written |
| `committed` | Whether a local commit was created |
| `commit-sha` | The SHA of the commit, if one was created |

---

## Agent Skill

Chug is designed to pair well with agent skills. A companion skill can teach agents how to use the Chug CLI, what makes a good changelog entry, and how to read repository guidance like `changelog_style`.

**Install the Chug skill:**

```bash
npx skills add crayment/chug
```

Once installed, agents working in your repository can create change files instead of editing `CHANGELOG.md` directly and can apply your project's `changelog_style` guidance when writing descriptions.

**Want different defaults?** The skill is a single `SKILL.md` file. Copy it, adjust the entry-writing guidelines to match your team's voice, and host it in your own repository. Point your agents there instead.

---

## Why Small Files Instead of Direct Edits

The key insight is that merge conflicts in `CHANGELOG.md` are a structural problem, not a discipline problem. When every branch edits the same file at the same position, conflicts are guaranteed regardless of how careful everyone is.

Change files don't conflict because each one is a new file with a unique name. Branches create, not edit. Conflicts disappear.

The workflow also fits naturally into agent-assisted development. Agents that open pull requests can call `chug new` as a deterministic, non-interactive step. No parsing. No reformatting. Just a structured file that accumulates with everything else.

---

## Design Philosophy

Chug is deliberately small. It is not a release platform, a versioning system, or a CI framework. It solves one problem: maintaining a useful `CHANGELOG.md` through structured change files instead of direct edits.

Non-interactive by default. Structured output. Graceful degradation when context is missing. Designed for humans and agents to use the same way.

---

## License

MIT
