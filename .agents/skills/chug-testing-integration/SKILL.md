---
name: chug-testing-integration
description: Run real integration checks against the public crayment/chug and crayment/chug-testing repositories. Load this skill when validating Chug end-to-end through real git commits, pull requests, merges, releases, or workflow runs on any local machine.
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

- Assume the public remotes are `crayment/chug` and `crayment/chug-testing`
- Resolve local clone paths before running any scenario
- Assume `gh auth status` is healthy before starting
- Do not delete public repos without explicit approval

## Quick Start

1. Read [repository-baseline.md](./references/repository-baseline.md)
2. Read [repository-discovery.md](./references/repository-discovery.md)
3. Resolve `PRODUCT_REPO_DIR` and `CONSUMER_REPO_DIR`
4. Pick one scenario file from `references/`
5. Follow the scenario exactly
6. Record what happened, including URLs, workflow runs, and failure modes
7. If the scenario fails, explain whether the bug is in Chug, the test setup, or GitHub policy

## Navigation

- **[repository-baseline.md](./references/repository-baseline.md)** — Shared setup, repo assumptions, and operating rules
- **[repository-discovery.md](./references/repository-discovery.md)** — How to reuse an existing clone or create one when local paths are unknown
- **[scenario-cli-happy-path.md](./references/scenario-cli-happy-path.md)** — Validate the Chug CLI in the consumer repo
- **[scenario-validate-action.md](./references/scenario-validate-action.md)** — Validate that `chug-validate` enforces a change file in PRs
- **[scenario-release-action.md](./references/scenario-release-action.md)** — Validate that `chug-release` updates the changelog and optionally commits locally in CI

## Key Reminders

- Treat `CONSUMER_REPO_DIR` as an integration environment, not a scratchpad
- Prefer creating short-lived branches and PRs over direct pushes when testing workflows
- Capture real evidence: PR URLs, workflow run URLs, commit SHAs, and exact command output
- Keep scenarios small and isolated so failures are easy to diagnose
- If a workflow requires new repo settings or permissions, note that explicitly

## Red Flags — Stop

- A scenario requires force-pushing or destructive git cleanup
- A scenario would delete the public test repo
- A scenario depends on unpublished code from `chug` unless that is the point of the test
- The baseline assumptions in `repository-baseline.md` no longer match reality
