# ABOUTME: Preview and release helpers for rendering pending changes into CHANGELOG.md.
# ABOUTME: These functions format entries, insert release sections, and delete processed files.

from __future__ import annotations

import logging
import os
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

from .change import load_change_files
from .config import changelog_path

logger = logging.getLogger(__name__)


def preview_markdown(config: dict) -> str:
    entries_with_paths = load_change_files()
    entries = [entry for _, entry in entries_with_paths]
    _enrich_entries_with_pr_links(entries_with_paths, entries, config)
    return _render_entries(entries, config)


def apply_release(version: str, config: dict) -> int:
    entries_with_paths = load_change_files()
    entries = [entry for _, entry in entries_with_paths]
    _enrich_entries_with_pr_links(entries_with_paths, entries, config)
    body = _render_entries(entries, config, release_version=version)

    changelog = changelog_path(config)
    if not changelog.exists():
        raise FileNotFoundError(f"{changelog.name} not found. Run `chug init` first.")

    current = changelog.read_text()
    marker = config["change_marker"]
    if marker not in current:
        raise ValueError(f"Change marker not found in {changelog.name}.")

    updated = current.replace(marker, f"{marker}\n\n{body}", 1)
    changelog.write_text(updated)

    for path, _ in entries_with_paths:
        path.unlink()

    return len(entries)


def _render_entries(entries: list[dict], config: dict, release_version: str | None = None) -> str:
    grouped: dict[str, list[dict]] = {category: [] for category in config["categories"]}
    for entry in entries:
        category = entry.get("category")
        if category in grouped:
            grouped[category].append(entry)
        else:
            logger.warning("Skipping changelog entry with unknown category: %s", category)

    lines: list[str] = []
    if release_version is not None:
        lines.append(f"## [{release_version}] - {date.today().isoformat()}")
        lines.append("")

    has_entries = any(grouped.values())
    if not has_entries:
        lines.append("- No changes")
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    for category in config["categories"]:
        category_entries = grouped[category]
        if not category_entries:
            continue
        lines.append(f"### {category.capitalize()}")
        for entry in category_entries:
            description = entry["description"]
            attributions: list[str] = []
            attributions.extend(_format_pr_links(entry))
            attributions.extend(_format_stories(entry.get("stories", []), config))
            attributions.extend(_format_authors(entry.get("authors", [])))

            if attributions:
                lines.append(f"- {description} ({', '.join(attributions)})")
            else:
                lines.append(f"- {description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _format_stories(stories: list[str], config: dict) -> list[str]:
    template = config.get("story_link_template")
    if not stories:
        return []
    result = []
    for story in stories:
        parsed = urlparse(story)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            result.append(f"[{parsed.path}]({story})")
        elif template:
            result.append(f"[{story}]({template.format(id=story)})")
        else:
            result.append(story)
    return result


def _format_authors(authors: list[dict]) -> list[str]:
    formatted: list[str] = []
    for author in authors:
        name = author.get("name")
        github = author.get("github")
        if name and github:
            formatted.append(f"[{name}](https://github.com/{github})")
        elif name:
            formatted.append(name)
        elif github:
            formatted.append(f"[@{github}](https://github.com/{github})")
    return formatted


def _format_pr_links(entry: dict) -> list[str]:
    repository = entry.get("_github_repository")
    pr_numbers = entry.get("pr_numbers", [])
    if not repository or not pr_numbers:
        return []
    return [f"[#{number}](https://github.com/{repository}/pull/{number})" for number in pr_numbers]


def _enrich_entries_with_pr_links(
    entries_with_paths: list[tuple[Path, dict]], entries: list[dict], config: dict
) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token:
        return
    if not repository:
        logger.warning("Failed to enrich PR information: GITHUB_REPOSITORY is not set.")
        return

    repo_root = _get_repo_root()
    if repo_root is None:
        logger.warning("Failed to enrich PR information: could not determine repository root.")
        return

    if "/" not in repository:
        logger.warning("Failed to enrich PR information: GITHUB_REPOSITORY must be in owner/repo format.")
        return

    owner, repo = repository.split("/", 1)
    base_branch = config.get("git_base_branch", "main")

    for (path, _), entry in zip(entries_with_paths, entries):
        try:
            relative_path = path.relative_to(repo_root).as_posix()
        except ValueError:
            logger.warning("Failed to enrich PR information: change file path is outside the repository root.")
            continue

        try:
            commit_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                },
                params={"path": relative_path, "sha": base_branch, "per_page": 1},
                timeout=10,
            )
            commit_response.raise_for_status()
            commits = commit_response.json()
            if not commits:
                continue

            commit_sha = commits[0]["sha"]
            pulls_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/pulls",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                },
                timeout=10,
            )
            pulls_response.raise_for_status()
            pulls = pulls_response.json()
        except Exception as exc:
            logger.warning("Failed to enrich PR information: %s", exc)
            continue

        numbers = [str(pr["number"]) for pr in pulls if "number" in pr]
        if numbers:
            entry["pr_numbers"] = numbers
            entry["_github_repository"] = repository


def _get_repo_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())
