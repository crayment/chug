# Chug PRD

## Product

**Chug** is agent-first changelog management for teams.

Chug manages a project changelog the same way database migrations manage schema changes: each change is captured in a small file first, those files accumulate during development, and they are rolled into a versioned section in `CHANGELOG.md` at release time. Once released, the processed change files are deleted.

The product exists to solve a simple team problem:

**How do we maintain a `CHANGELOG.md` file without making it annoying for everyone on the team?**

## Problem

Editing `CHANGELOG.md` directly is fine for one person and painful for a team.

Common failure modes:

- frequent merge conflicts in `CHANGELOG.md`
- inconsistent formatting and level of detail
- incomplete release notes because changelog work gets deferred
- poor fit for agent workflows that need deterministic, non-interactive steps

Existing tooling often misses one of the things teams actually need:

- simple enough to adopt quickly
- structured enough to automate
- non-interactive enough for agents
- lightweight enough that it does not become its own release platform

## Vision

Chug should make changelog work boring, predictable, and easy to automate.

If all it does is help a team maintain a useful changelog without merge-conflict pain, it is doing its job.

## Primary Audience

Primary audience:

- engineering teams adopting a changelog workflow that should work well with their agents

Secondary audiences:

- individual developers working in agent-assisted repositories
- maintainers who want a lightweight changelog workflow for GitHub repositories

## Product Principles

- Non-interactive by default
- Works for humans and agents
- Core workflow works locally without GitHub access
- GitHub integration is optional and additive
- Missing metadata should degrade gracefully
- The change-file schema should remain compatible with the existing Chug format
- Documentation should explain both the problem Chug solves and exactly how it works

## Core Workflow

Chug uses small YAML files in `changes/` to represent pending changelog entries. Those files are the working state of the changelog before release.

Typical workflow:

1. Initialize a repo for Chug
2. Create change files as work is done
3. Preview pending release notes
4. Run release to append a new version section to `CHANGELOG.md`
5. Delete the processed change files after that release is written

## V1 Commands

Chug v1 includes four commands.

### `chug init`

Purpose:

- bootstrap a repository for Chug

Behavior:

- create `chug.config.yml` if missing
- create `changes/` if missing
- create `CHANGELOG.md` with a release insertion marker if missing
- avoid destructive edits to an existing repository setup

Why it exists:

- first-run adoption should be fast for humans
- agents should have a deterministic way to scaffold a repository

### `chug new`

Purpose:

- create a new pending changelog entry

Behavior:

- require `description`
- require `category`
- optionally accept `stories`
- attempt to populate authors from local git config
- if author info cannot be determined, write `authors: []`
- never fail only because author info is unavailable
- write a timestamped YAML file into `changes/`

Why it exists:

- every change should start as a small structured artifact instead of an edit to `CHANGELOG.md`

### `chug preview`

Purpose:

- render pending changelog content without mutating files

Behavior:

- read pending change files
- group entries by configured category order
- render markdown that matches release formatting as closely as possible
- optionally include GitHub PR enrichment when configured and available

Why it exists:

- users and agents need a dry run before mutating the changelog

### `chug release`

Purpose:

- process pending change files into a release section in `CHANGELOG.md`

Behavior:

- read all pending change files
- optionally enrich entries with GitHub PR links
- group entries by category order from config
- insert a new version section into `CHANGELOG.md`
- delete processed change files after successful release generation
- if there are no pending change files, still add a release section with `No changes`

Why it exists:

- the changelog should be generated at release time, not edited continuously on every branch

## Change File Schema

V1 keeps schema compatibility with the existing Chug change-file format.

Supported fields:

- `description`: string, required
- `category`: string, required
- `stories`: list of strings, optional
- `authors`: list of author objects, required in shape but may be empty

Author object:

- `name`: string, optional
- `github`: string, optional

Example:

```yaml
description: Tighten session timeout behavior
category: bug
stories:
  - sc-12345
authors:
  - name: Jane Doe
    github: janedoe
```

Example when author detection is unavailable:

```yaml
description: Tighten session timeout behavior
category: bug
authors: []
```

## Configuration

Chug is configured with `chug.config.yml`.

V1 configuration fields:

- `categories`
- `changelog_file`
- `change_marker`
- `story_format`
- `story_link_template`
- `git_base_branch` (optional, default `main`)

Expected behavior:

- if `git_base_branch` is missing, default to `main`
- story linking should be configurable and not tied to a single tracker in product positioning

## GitHub PR Enrichment

GitHub enrichment is a first-class v1 feature.

Its purpose is simple:

- attach pull request links to generated changelog entries when possible

### Desired Output

When PR lookup succeeds, rendered changelog entries include GitHub PR links.

Example:

```markdown
- Tighten session timeout behavior ([#123](https://github.com/owner/repo/pull/123), [Jane Doe](https://github.com/janedoe))
```

If GitHub returns multiple PRs for the relevant commit, Chug should include multiple PR links.

If lookup fails, Chug should:

- emit a warning
- keep the entry
- omit the PR link

### Lookup Method

V1 lookup method:

1. determine the change file path relative to the repository root
2. call the GitHub API to find the latest commit on the configured base branch that touched that file
3. call the GitHub API to find the pull request or pull requests associated with that commit
4. render PR links from the returned PR numbers

### Token Policy

GitHub access should be optional.

Without a GitHub token, Chug must still:

- create change files
- preview changelog output
- generate changelog releases

With a GitHub token, Chug may enrich entries with PR links.

The documentation must explain exactly:

- that the token is optional
- what additional output the token enables
- which data is fetched
- which API calls are made
- that this feature is read-only enrichment

V1 product expectation:

- the token is used for GitHub PR enrichment
- Chug should be easy to try without passing a token

## GitHub Actions

Chug v1 includes two public GitHub Actions.

### `chug-validate`

Purpose:

- verify that a pull request includes a changelog entry file

Behavior:

- check whether the pull request adds or modifies at least one file in `changes/`
- fail clearly when no change file is present

Product goal:

- make adoption easy for teams that want consistent changelog hygiene in CI

### `chug-release`

Purpose:

- run release automation in GitHub Actions without forcing every repository to rediscover the same staging logic

Behavior:

- install the public Chug CLI
- run `chug release`
- optionally create a local git commit
- do not push to the remote repository
- expose simple outputs for downstream workflow steps

Why local commit support matters:

- staging the resulting changes is slightly tricky in CI
- processed change files may be deleted
- `changes/` may become empty or disappear
- no-change releases still need clean handling

V1 local commit logic should robustly handle:

- staging `CHANGELOG.md`
- staging deletions in `changes/`
- avoiding commits when nothing is staged

Recommended action inputs:

- `version`
- optional GitHub token for PR enrichment
- `commit-changes` boolean

Recommended action outputs:

- `changed`
- `committed`
- `commit-sha`

### Why Push Is Not Included

Push behavior depends heavily on repository-specific policy:

- branch protection
- rulesets
- workflow token permissions
- repository governance choices

For v1, Chug should stop short of push and leave that final step to the calling workflow.

This keeps the product broadly usable across public repositories without embedding repo-specific policy assumptions.

## Installation and Distribution

The repo root should support local install with:

```bash
uv tool install .
pipx install .
```

The public product should also support installation from published package sources so teams can adopt it without cloning the repo first.

## UX Expectations

Chug should be designed for agent use more than interactive human use.

That means:

- non-interactive by default
- explicit flags over prompts
- stable, readable output
- warnings that help users fix missing setup without blocking unrelated work

Warnings should be informative but not noisy.

Examples:

- missing GitHub token for PR enrichment
- malformed GitHub repository context
- inability to detect authors from git config
- inability to determine PR information for a change file

## Documentation Goals

The README derived from this PRD should do two jobs at once:

1. explain why Chug exists and why a team should care
2. show exactly how to try and use it in under five minutes

After reading the README, a new user should feel:

- I understand exactly why this exists
- I can try this quickly

The README should sell the workflow without sounding like an internal project update.

It should feel like product documentation that also markets the product.

## Product Summary

Chug is deliberately small.

It is not trying to become a release platform, a versioning system, or a generic CI framework.

It should solve one concrete team problem well:

**maintaining a useful `CHANGELOG.md` through small change files instead of painful direct edits.**
