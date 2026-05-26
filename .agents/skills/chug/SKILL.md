---
name: chug
description: Create a changelog entry with Chug when preparing a pull request or when asked to create a changelog or add a changelog. Trigger phrases include `chug`, `create a changelog`, and `add a changelog`. Load this skill when you need to run `chug new` to generate the change file for a code change.
tags:
  - chug
  - changelog
  - cli
version: 1.0.0
author: Claude
---

# Chug

Use Chug to create the pending changelog file for a code change before opening a pull request or when explicitly asked to add a changelog entry.

## Quick Start

1. Check whether `chug` is installed by running `chug --help`
2. Install `chug` if the command is missing
3. Read `chug.config.yml` before creating the entry
4. Run `chug new` with a user-facing description and a configured category

## Install

If `chug --help` fails because the command is missing, install it with one of:

```bash
uv tool install chug-cli
```

```bash
pipx install chug-cli
```

## Use

Read `chug.config.yml` first.

Pay attention to:

- `categories` — use only configured categories
- `story_link_template`
- `changelog_style` if present — follow it when writing descriptions

Create the changelog entry with:

```bash
chug new --description "Describe the user-visible change" --category feature
```

## Key Reminders

- Create a change file instead of editing `CHANGELOG.md` directly
- Keep descriptions concise and user-facing
- Use a category that actually appears in `chug.config.yml`
- Follow `changelog_style` if the repo defines it
- If author detection fails, Chug writes `authors: []`; do not block on missing git author config
