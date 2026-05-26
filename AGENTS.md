# AGENTS.md

Guidance for agents working in this repository.

## What Chug is

Chug is a changelog management tool. Instead of editing `CHANGELOG.md` directly, contributors write small YAML files into a `changes/` directory. At release time, `chug release` rolls them into a versioned section in `CHANGELOG.md` and deletes the processed files.

Chug ships two things: a CLI (`chug-cli` on PyPI) and a GitHub Action (`uses: crayment/chug@v1`) that installs the CLI in CI.

## Repo structure

```
cli/src/chug/      CLI source code
cli/tests/         Unit tests
action.yml         Root GitHub Action (public surface: uses: crayment/chug@v1)
.github/workflows/ CI, release, and changelog validation workflows
changes/           Pending changelog entries (YAML files)
chug.config.yml    Chug configuration for this repo
```

## Development

Run tests:
```bash
uv run --group dev pytest
```

Lint and format:
```bash
uv run --group dev ruff check cli
uv run --group dev ruff format --check cli
```

Follow TDD: write a failing test first, confirm it fails, then implement.

## Making changes

Every PR requires a change file. Create one with:
```bash
chug new --description "What changed, from the user's perspective" --category feature
```

Valid categories are in `chug.config.yml`. Do not edit `CHANGELOG.md` directly.

## Before cutting a release

Run the full integration test suite against `main` using the `crayment/chug-testing` repo. The skill is at:

```
/Users/crayment/dev/me/chug-testing/.agents/skills/chug-testing-integration/SKILL.md
```

Read it, follow both step files (`steps-pr-and-merge.md` then `steps-release.md`), and report results. Only trigger the release workflow once all steps pass.

## Cutting a release

Trigger the release workflow manually from `main`:
```bash
gh workflow run release.yml --repo crayment/chug --ref main -f version=X.Y.Z -f publish-target=pypi
```

Use the next patch version unless the change warrants a minor bump. The workflow handles the version bump, changelog, build, PyPI publish, git tag, and GitHub release.
