# ABOUTME: Change-file helpers for creating and loading pending changelog entries.
# ABOUTME: These functions manage the YAML files stored in the changes directory.

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import subprocess

import yaml

from .config import changes_dir


def detect_authors() -> list[dict[str, str]]:
    name = _git_config("user.name")
    github = _git_config("github.user")

    if not name and not github:
        return []

    author: dict[str, str] = {}
    if name:
        author["name"] = name
    if github:
        author["github"] = github
    return [author] if author else []


def _git_config(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", key],
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    return value or None


def create_change_file(description: str, category: str, stories: list[str] | None = None) -> Path:
    directory = changes_dir()
    directory.mkdir(exist_ok=True)

    file_path = directory / _filename_for(description)
    payload = {
        "description": description,
        "category": category,
        "authors": detect_authors(),
    }
    if stories:
        payload["stories"] = stories

    file_path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return file_path


def load_change_files() -> list[tuple[Path, dict]]:
    directory = changes_dir()
    if not directory.exists():
        return []

    entries: list[tuple[Path, dict]] = []
    for path in sorted(directory.glob("*.yml")):
        payload = yaml.safe_load(path.read_text()) or {}
        entries.append((path, payload))
    return entries


def _filename_for(description: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", description.lower()).strip("-")
    if not slug:
        slug = "change"
    return f"{timestamp}-{slug}.yml"
