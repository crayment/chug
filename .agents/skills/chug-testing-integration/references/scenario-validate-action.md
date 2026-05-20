# Scenario: Validate Action

Validate that `crayment/chug/.github/actions/chug-validate@main` enforces a change file in pull requests.

## Goal

Prove that a consumer repository can reference the public action and get correct PR validation behavior.

## Steps

1. Work in `/Users/crayment/dev/me/chug-testing`
2. Ensure the repo has a workflow that uses:

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
      - uses: crayment/chug/.github/actions/chug-validate@main
```

3. Create a branch with a normal code or README change but no `changes/` file
4. Push the branch and open a PR
5. Wait for the workflow run to complete
6. Confirm the workflow fails with the expected validation error
7. Update the same branch by adding a valid `changes/*.yml` file
8. Push again and confirm the workflow passes

## Expected Result

- first PR run fails without a change file
- second PR run passes after adding a change file

## Record

- PR URL
- failing workflow run URL
- passing workflow run URL
- exact error text from the failing run
