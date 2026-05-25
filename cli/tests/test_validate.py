# ABOUTME: Tests for the `chug validate` subcommand.
# ABOUTME: Verifies changelog entry detection against git diff output in local and CI contexts.

import subprocess
from pathlib import Path

from chug.cli import cli
from click.testing import CliRunner


def _make_repo_with_config(tmp_path: Path) -> None:
    """Write a minimal chug.config.yml so load_config() succeeds."""
    (tmp_path / "chug.config.yml").write_text("categories:\n  - feature\n  - bug\ngit_base_branch: main\n")
    (tmp_path / "changes").mkdir(exist_ok=True)


def _fake_git_diff(changed_files: list[str]):
    """Return a callable that monkeypatches subprocess.run to simulate git diff output."""

    def fake_run(cmd, **kwargs):
        if cmd[:3] == ["git", "diff", "--name-only"]:
            output = "\n".join(changed_files) + ("\n" if changed_files else "")
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=output, stderr="")
        # Pass through other subprocess calls (e.g. git config from change.py)
        raise AssertionError(f"Unexpected subprocess call: {cmd}")

    return fake_run


def _fake_git_diff_failure():
    """Return a callable that simulates a failing git command."""

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=128, stdout="", stderr="fatal: not a git repository")

    return fake_run


# ---------------------------------------------------------------------------
# Happy path: a changes/*.yml file appears in the diff → exit 0
# ---------------------------------------------------------------------------


def test_validate_exits_zero_when_changes_file_in_diff(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setattr(subprocess, "run", _fake_git_diff(["changes/2026-05-20T120000-fix.yml"]))

    result = runner.invoke(cli, ["validate"], catch_exceptions=False)

    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Failure path: no changes file in diff → exit non-zero, human-readable error
# ---------------------------------------------------------------------------


def test_validate_exits_nonzero_when_no_changes_file_in_diff(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setattr(subprocess, "run", _fake_git_diff(["src/foo.py", "README.md"]))

    result = runner.invoke(cli, ["validate"])

    assert result.exit_code != 0


def test_validate_prints_human_error_locally_when_no_changes_file(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(subprocess, "run", _fake_git_diff(["src/foo.py"]))

    result = runner.invoke(cli, ["validate"])

    # Should print a plain human-readable error, not a GitHub annotation
    assert "::error::" not in result.output
    assert "changes/" in result.output.lower() or "changelog" in result.output.lower()


# ---------------------------------------------------------------------------
# CI failure: GITHUB_ACTIONS=true → GitHub annotation format
# ---------------------------------------------------------------------------


def test_validate_prints_github_annotation_in_ci(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(subprocess, "run", _fake_git_diff(["src/foo.py"]))

    result = runner.invoke(cli, ["validate"])

    assert result.exit_code != 0
    assert "::error::A changelog entry file in changes/ is required for this pull request." in result.output


# ---------------------------------------------------------------------------
# GITHUB_BASE_REF overrides config base branch
# ---------------------------------------------------------------------------


def test_validate_uses_github_base_ref_when_set_in_ci(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_BASE_REF", "develop")

    captured_calls: list[list[str]] = []

    def recording_fake_run(cmd, **kwargs):
        captured_calls.append(list(cmd))
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="changes/fix.yml\n", stderr="")
        raise AssertionError(f"Unexpected subprocess call: {cmd}")

    monkeypatch.setattr(subprocess, "run", recording_fake_run)

    result = runner.invoke(cli, ["validate"], catch_exceptions=False)

    assert result.exit_code == 0
    diff_cmd = next(c for c in captured_calls if "diff" in c)
    # The branch used in the diff command should be origin/develop, not origin/main
    assert any("develop" in arg for arg in diff_cmd)


def test_validate_falls_back_to_config_base_branch_without_github_base_ref(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)

    captured_calls: list[list[str]] = []

    def recording_fake_run(cmd, **kwargs):
        captured_calls.append(list(cmd))
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="changes/fix.yml\n", stderr="")
        raise AssertionError(f"Unexpected subprocess call: {cmd}")

    monkeypatch.setattr(subprocess, "run", recording_fake_run)

    result = runner.invoke(cli, ["validate"], catch_exceptions=False)

    assert result.exit_code == 0
    diff_cmd = next(c for c in captured_calls if "diff" in c)
    # Should use origin/main from config
    assert any("main" in arg for arg in diff_cmd)


# ---------------------------------------------------------------------------
# Git command failure → graceful error
# ---------------------------------------------------------------------------


def test_validate_handles_git_command_failure_gracefully(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    _make_repo_with_config(tmp_path)
    monkeypatch.setattr(subprocess, "run", _fake_git_diff_failure())

    result = runner.invoke(cli, ["validate"])

    assert result.exit_code != 0
    # Should print something meaningful, not just a traceback
    assert result.output.strip() != ""
