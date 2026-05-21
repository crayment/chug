---
name: chug
description: Use the Chug CLI to manage changelog entries through small files. Load this skill when a repo uses Chug, has a chug.config.yml file, or needs a changelog entry created, previewed, or released.
tags:
  - chug
  - changelog
  - cli
version: 1.0.0
author: Claude
---

# Chug

Use Chug to manage changelog work through small files in `changes/` instead of editing `CHANGELOG.md` directly.

## Quick Start

1. Check whether the `chug` command is installed
2. Install it if missing
3. Read `chug.config.yml` before creating or releasing entries
4. Use `chug new`, `chug preview`, and `chug release` instead of editing `CHANGELOG.md` directly

## Install

If `chug` is missing, install it with one of:

```bash
uv tool install chug-cli
```

```bash
pipx install chug-cli
```

If working from a local source checkout of Chug, install from the repo root instead:

```bash
uv tool install .
```

## Use

Read `chug.config.yml` first.

Pay attention to:

- `categories` — use only configured categories
- `story_format`
- `story_link_template`
- `git_base_branch`
- `changelog_style` if present — follow it when writing descriptions

Use these commands:

```bash
chug init
```

```bash
chug new --description "Describe the user-visible change" --category feature
```

```bash
chug preview
```

```bash
chug release --version 1.2.3
```

## Key Reminders

- Prefer creating a change file over editing `CHANGELOG.md` directly
- Keep descriptions concise and user-facing
- If author detection fails, Chug writes `authors: []`; do not block on missing git author config
- `chug release` deletes processed change files after writing the changelog section
