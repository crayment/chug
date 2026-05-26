# AGENTS.md

Guidance for agents working in this repository.

## What Chug is

Chug is a changelog management tool. Instead of editing `CHANGELOG.md` directly, contributors write small YAML files into a `changes/` directory. At release time, `chug release` rolls them into a versioned section in `CHANGELOG.md` and deletes the processed files.

Chug ships three things: a CLI (`chug-cli` on PyPI), a GitHub Action (`uses: crayment/chug@v1`) that installs the CLI in CI, and an Elixir package (`chug` on Hex.pm) that provides `mix chug.new` for Elixir projects.

## Repo structure

```
cli/src/chug/      Python CLI source code
cli/tests/         Python unit tests
elixir/            Elixir/Hex package (mix chug.new task)
action.yml         Root GitHub Action (public surface: uses: crayment/chug@v1)
.github/workflows/ CI, release, and changelog validation workflows
changes/           Pending changelog entries (YAML files)
chug.config.yml    Chug configuration for this repo
```

## Development

Python tests:
```bash
uv run --group dev pytest
uv run --group dev ruff check cli
uv run --group dev ruff format --check cli
```

Elixir tests:
```bash
cd elixir && mix deps.get && mix test
```

## Making changes

Every PR requires a change file. Create one with:
```bash
chug new --description "What changed, from the user's perspective" --category feature
```

Valid categories are in `chug.config.yml`. Do not edit `CHANGELOG.md` directly.

## Before cutting a release

Run the full integration test suite against `main` using the `crayment/chug-testing` repo. The skill lives at `.agents/skills/chug-testing-integration/SKILL.md` in that repo. Spawn a child agent to run it — have the child find or clone `crayment/chug-testing` locally, load the skill, and follow both step files (`steps-pr-and-merge.md` then `steps-release.md`) in order. Wait for the child to report results before triggering the release workflow.

## Cutting a release

Trigger the release workflow manually from `main`:
```bash
gh workflow run release.yml --repo crayment/chug --ref main -f version=X.Y.Z -f publish-target=pypi
```

Use the next patch version unless the change warrants a minor bump. The workflow handles the version bump, changelog, build, PyPI publish, git tag, and GitHub release.
