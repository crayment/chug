# ABOUTME: Validation logic for checking that a changelog entry exists in the current PR diff.
# ABOUTME: Used by `chug validate` to enforce changelog requirements in CI and locally.

from __future__ import annotations

import os
import subprocess

CI_ERROR_MESSAGE = "::error::A changelog entry file in changes/ is required for this pull request."
LOCAL_ERROR_MESSAGE = "No changelog entry found. Add a changes/*.yml file for this pull request."


def get_base_branch(config: dict) -> str:
    """Return the base branch to diff against.

    In GitHub Actions, GITHUB_BASE_REF takes precedence over the config value.
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        ref = os.environ.get("GITHUB_BASE_REF")
        if ref:
            return ref
    return config.get("git_base_branch", "main")


def get_changed_files(base_branch: str) -> list[str]:
    """Run git diff and return the list of changed file paths.

    Raises RuntimeError if the git command fails.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip() or 'unknown error'}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def has_changes_entry(changed_files: list[str]) -> bool:
    """Return True if any changed file is a changes/*.yml entry."""
    return any(f.startswith("changes/") and f.endswith(".yml") for f in changed_files)


def is_ci() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"
