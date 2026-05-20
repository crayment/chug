# Scenario: Release Action

Validate that `crayment/chug/.github/actions/chug-release@main` works from a consumer repo.

## Goal

Prove that the public release action can:

- install Chug
- run `chug release`
- detect changed state
- optionally create a local git commit in CI

## Steps

1. Work in `/Users/crayment/dev/me/chug-testing`
2. Ensure the repo has a workflow that uses:

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
      - uses: crayment/chug/.github/actions/chug-release@main
        id: release
        with:
          version: ${{ inputs.version }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          commit-changes: true
```

3. Ensure there is at least one pending `changes/*.yml` file on `main`
4. Trigger the workflow with `gh workflow run`
5. Wait for completion with `gh run watch`
6. Inspect logs and resulting commit state
7. Repeat with no pending changes to validate the no-change path

## Expected Result

- the workflow succeeds
- the action outputs indicate whether changes were written and committed
- the local commit is created inside the workflow when there are staged changes
- the no-change run completes cleanly
- if Chug's release model writes a `No changes` version section, then the no-change run should still report `changed=true` and `committed=true`
- if Chug ever changes to a true no-op release model, update this scenario before treating those outputs as a bug

## Record

- workflow run URL
- whether `changed` was true or false
- whether `committed` was true or false
- commit SHA if one was created
- any permissions or branch policy constraints encountered
