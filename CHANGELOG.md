# Changelog

All notable changes to this project will be documented in this file.

<!-- #changelog-release-automation-hook-do-not-remove -->

## [0.1.3] - 2026-05-26

### Feature
- Add mix chug.new task as Elixir/Hex package ([#7](https://github.com/crayment/chug/pull/7), [Cody Rayment](https://github.com/crayment))

### Chore
- Add AGENTS.md with development and release guidance for agents ([#6](https://github.com/crayment/chug/pull/6), [Cody Rayment](https://github.com/crayment))
- Publish Elixir package to Hex.pm as part of release workflow ([#9](https://github.com/crayment/chug/pull/9), [Cody Rayment](https://github.com/crayment))


## [0.1.2] - 2026-05-25

### Feature
- Show version and commit in chug --version output ([#1](https://github.com/crayment/chug/pull/1), [Cody Rayment](https://github.com/crayment))
- Add chug validate subcommand for CI changelog enforcement ([#5](https://github.com/crayment/chug/pull/5), [Cody Rayment](https://github.com/crayment))
- Replace chug-validate and chug-release composite actions with root setup action ([#5](https://github.com/crayment/chug/pull/5), [Cody Rayment](https://github.com/crayment))

### Chore
- Use Chug for Chug's own changelog management ([Cody Rayment](https://github.com/crayment))
- Rewrite README for GitHub visitors ([#2](https://github.com/crayment/chug/pull/2), [Cody Rayment](https://github.com/crayment))
- Dogfood Chug validation and test workflows in pull requests ([#3](https://github.com/crayment/chug/pull/3), [Cody Rayment](https://github.com/crayment))
- Add Ruff formatting and linting for Python code ([#4](https://github.com/crayment/chug/pull/4), [Cody Rayment](https://github.com/crayment))

### Bug
- Skip git release steps for TestPyPI publishes ([Cody Rayment](https://github.com/crayment))

