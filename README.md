# Chug

Keeping `CHANGELOG.md` tidy on a team is one of those things that's never quite as simple as it should be. Chug is a small tool I built to take the friction out of it. It works well for me, so I'm sharing it.

---

## The Problems

**Parallel branches create merge conflicts.**
Every PR that edits `CHANGELOG.md` touches the same file at the same position. On an active team this produces conflicts regularly.

**Release mechanics are manual.**
The typical pattern is an "Unreleased" section at the top that accumulates changes and gets renamed to a version when you ship. It works, but it's a manual step that's easy to skip or do inconsistently.

**Agents don't know the rules.**
When you ask an agent to open a pull request, it has no idea a changelog entry is expected. It ships the PR without one unless it's been explicitly taught otherwise.

---

## How Chug Fixes It

Instead of editing `CHANGELOG.md` directly, each change gets written as a small YAML file in a `changes/` directory. Branches create new files — they don't edit existing ones. New files never conflict with each other.

```
changes/
  2024-01-15T143022-fix-session-timeout.yml
  2024-01-16T091345-add-export-endpoint.yml
  2024-01-17T162801-update-rate-limits.yml
```

At release time, one command rolls all pending files into a new versioned section in `CHANGELOG.md` and deletes them.

Chug ships three things to make this work end-to-end:

- **A CLI** for creating change YAML files. Automatically pulls author info from your git config and validates that the change is categorized into one of your configured categories.
- **Two GitHub Actions** — one to validate that every PR includes a change file, one to process a release (create an entry in `CHANGELOG.md` from your change files, delete them, and commit everything).
- **An agent skill** so agents know to create a change file when they open a PR.

That's it. Chug is deliberately small. It's not a release platform or a versioning system — just a better way to maintain your changelog.

---

## Quick Start

**Install:**

```bash
uv tool install chug-cli
# or
pipx install chug-cli
```

**Bootstrap a repo:**

```bash
chug init
```

Creates `chug.config.yml`, a `changes/` directory, and a `CHANGELOG.md` with an insertion marker — without touching anything that already exists.

**Record a change:**

```bash
chug new --description "Fix session timeout on mobile" --category bug
```

Writes a timestamped YAML file into `changes/`. No edit to `CHANGELOG.md`. No coordination required. Safe to run on any branch.

**Preview before releasing:**

```bash
chug preview
```

Renders the full release output without touching any files.

**Cut a release:**

```bash
chug release --version 1.4.0
```

Inserts a new versioned section at the configured marker in `CHANGELOG.md`, then deletes the processed change files.

---

## Change File Format

```yaml
description: Fix session timeout on mobile
category: bug
stories:
  - sc-12345
authors:
  - name: Jane Doe
    github: janedoe
```

`description` and `category` are required. `stories` and `authors` are optional. Chug populates `authors` from your local git config when it can; if it can't, it writes `authors: []` rather than failing.

---

## Author Detection

When you run `chug new`, Chug automatically populates the `authors` field by reading two git config values:

- `user.name` — your display name
- `github.user` — your GitHub username

If both are set, the entry looks like:

```yaml
authors:
  - name: Jane Doe
    github: janedoe
```

If neither is set, `authors` is written as an empty list and Chug continues without failing.

**To set these up:**

```bash
git config --global user.name "Jane Doe"
git config --global github.user janedoe
```

`user.name` is typically set already. `github.user` is not a standard git config key — you need to add it explicitly if you want GitHub usernames in your changelog entries.

---

## Configuration

`chug.config.yml` lives at the repo root:

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

An optional field that documents how your team wants entries written. It has no effect on CLI behavior — it exists as structured guidance for agents and automation that create change files on your behalf.

```yaml
changelog_style: |
  Write descriptions from the user's perspective, not the implementer's.
  Be specific about what changed and why it matters.
  Keep descriptions under 100 characters.
  Good: "Fix crash when opening documents with special characters in the filename"
  Avoid: "Handle edge case in path parsing logic"
```

---

## GitHub PR Links

With a GitHub token, Chug enriches each changelog entry with a link to the pull request that introduced the change file:

```markdown
- Fix session timeout on mobile ([#87](https://github.com/owner/repo/pull/87), [Jane Doe](https://github.com/janedoe))
```

Without a token, entries render without PR links and everything else works the same.

```bash
export GITHUB_TOKEN=ghp_...
chug release --version 1.4.0
```

Chug finds the most recent base-branch commit that touched the change file, looks up associated pull requests, and adds the link. All API calls are read-only.

---

## GitHub Actions

Two companion actions for teams that want changelog hygiene enforced in CI.

**Working examples:**

- [Validation workflow in `crayment/chug-testing`](https://github.com/crayment/chug-testing/blob/main/.github/workflows/validate-changelog.yml)
- [Release workflow in `crayment/chug-testing`](https://github.com/crayment/chug-testing/blob/main/.github/workflows/release-changelog.yml)

This repo uses local-path action references in its own workflows so changes to the actions can be tested on the same PR that modifies them. Consumer repos should reference the published action path by tag.

### `chug-validate`

Fails a pull request if no file in `changes/` was added or modified. Use this to make a changelog entry a required part of every PR.

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

Runs `chug release` in CI and handles the edge cases that are easy to get wrong — deleted change files, an empty `changes/` directory after processing, and releases that write a `No changes` section. Stages a clean commit when the release actually modifies files.

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

These actions are hosted in `crayment/chug` and can be referenced directly by tag from any repository. No special read token required.

Push is left to the calling workflow intentionally — whether it succeeds depends on your branch protection rules and token permissions.

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

Chug ships a companion skill that teaches agents how to use the CLI, what makes a good changelog entry, and how to apply your project's `changelog_style` guidance. Once installed, agents working in your repository create change files instead of editing `CHANGELOG.md` directly.

```bash
npx skills add crayment/chug
```

The skill is a single `SKILL.md` file. Copy it, adjust the guidelines to match your team's voice, and host it wherever you want.

---

## License

MIT
