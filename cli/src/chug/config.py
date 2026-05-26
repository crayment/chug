# ABOUTME: Configuration helpers for locating, reading, and bootstrapping Chug files.
# ABOUTME: These functions define the default changelog workflow used by the CLI.

from pathlib import Path

import yaml

CONFIG_FILE_NAME = "chug.config.yml"
DEFAULT_CHANGELOG_FILE = "CHANGELOG.md"
DEFAULT_CHANGE_MARKER = "<!-- #changelog-release-automation-hook-do-not-remove -->"
DEFAULT_CONFIG = {
    "categories": ["feature", "chore", "bug"],
    "changelog_file": DEFAULT_CHANGELOG_FILE,
    "change_marker": DEFAULT_CHANGE_MARKER,
    "story_link_template": "https://example.com/stories/{id}",
    "git_base_branch": "main",
}


def config_path(cwd: Path | None = None) -> Path:
    base_dir = cwd or Path.cwd()
    return base_dir / CONFIG_FILE_NAME


def load_config(cwd: Path | None = None) -> dict:
    path = config_path(cwd)
    if not path.exists():
        raise FileNotFoundError(f"{CONFIG_FILE_NAME} not found. Run `chug init` first.")

    data = yaml.safe_load(path.read_text()) or {}
    config = DEFAULT_CONFIG.copy()
    config.update(data)
    return config


def write_default_config(cwd: Path | None = None) -> Path:
    path = config_path(cwd)
    if not path.exists():
        path.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))
    return path


def changelog_path(config: dict, cwd: Path | None = None) -> Path:
    base_dir = cwd or Path.cwd()
    return base_dir / config["changelog_file"]


def changes_dir(cwd: Path | None = None) -> Path:
    base_dir = cwd or Path.cwd()
    return base_dir / "changes"
