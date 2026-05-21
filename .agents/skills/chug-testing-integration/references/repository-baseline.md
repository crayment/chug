# Repository Baseline

Use this reference before running any scenario.

## Local Repositories

Resolve local clone paths using [repository-discovery.md](./repository-discovery.md).

Record the result as:

- `PRODUCT_REPO_DIR`
- `CONSUMER_REPO_DIR`

## Public Repositories

- Product repo: https://github.com/crayment/chug
- Consumer repo: https://github.com/crayment/chug-testing

## Assumptions

- `crayment/chug` contains the current public composite actions under `.github/actions/`
- `crayment/chug-testing` is the integration target
- `gh` is authenticated as `crayment`
- The default branch is `main` in both repositories

## Operating Rules

- Create a branch for each scenario unless the scenario explicitly tests direct pushes
- Use descriptive branch names like `test/validate-missing-change-file`
- Prefer one scenario per PR
- Merge or close test PRs after the scenario is complete
- Do not rewrite public history on either repo

## Evidence To Capture

- command output
- created branch name
- PR URL
- workflow run URL
- final commit SHA if a commit was created
- whether the observed result matched the expected result

## Cleanup Rules

- Delete short-lived branches after merge or close when safe
- Leave a clean `main` branch in the resolved consumer repo
- Keep useful workflow files and fixtures if they support future scenarios
