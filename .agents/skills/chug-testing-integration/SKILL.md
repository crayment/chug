---
name: chug-testing-integration
description: Run real integration checks against the public crayment/chug and crayment/chug-testing repositories. Load this skill when validating Chug end-to-end through real git commits, pull requests, merges, releases, or workflow runs.
tags:
  - chug
  - github
  - integration-tests
version: 1.0.0
author: Claude
---

# Chug Testing Integration

Use this skill to validate Chug through the real public repositories, not just local unit tests.

The purpose of this skill is to prove that Chug works as a product:

- the CLI works in a consumer repository
- the GitHub Actions are consumable from another repository
- the release workflow behaves correctly with real git history and GitHub state

## Preconditions

- Work from the local repo at `/Users/crayment/dev/me/chug`
- Use the test repo at `/Users/crayment/dev/me/chug-testing`
- Assume the public remotes are `crayment/chug` and `crayment/chug-testing`
- Assume `gh auth status` is healthy before starting
- Do not delete public repos without explicit approval

## Quick Start

1. Read [repository-baseline.md](./references/repository-baseline.md)
2. Pick one scenario file from `references/`
3. Follow the scenario exactly
4. Record what happened, including URLs, workflow runs, and failure modes
5. If the scenario fails, explain whether the bug is in Chug, the test setup, or GitHub policy

## Navigation

- **[repository-baseline.md](./references/repository-baseline.md)** — Shared setup, repo assumptions, and operating rules
- **[scenario-cli-happy-path.md](./references/scenario-cli-happy-path.md)** — Validate the Chug CLI in the consumer repo
- **[scenario-validate-action.md](./references/scenario-validate-action.md)** — Validate that `chug-validate` enforces a change file in PRs
- **[scenario-release-action.md](./references/scenario-release-action.md)** — Validate that `chug-release` updates the changelog and optionally commits locally in CI

## Key Reminders

- Treat `crayment/chug-testing` as an integration environment, not a scratchpad
- Prefer creating short-lived branches and PRs over direct pushes when testing workflows
- Capture real evidence: PR URLs, workflow run URLs, commit SHAs, and exact command output
- Keep scenarios small and isolated so failures are easy to diagnose
- If a workflow requires new repo settings or permissions, note that explicitly

## Red Flags — Stop

- A scenario requires force-pushing or destructive git cleanup
- A scenario would delete the public test repo
- A scenario depends on unpublished code from `chug` unless that is the point of the test
- The baseline assumptions in `repository-baseline.md` no longer match reality
