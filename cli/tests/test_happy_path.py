# ABOUTME: End-to-end tests for the local Chug happy path.
# ABOUTME: Verifies init, new, preview, and release work together in one repo.

from pathlib import Path

import chug.change
import yaml
from chug.cli import cli
from click.testing import CliRunner

CHANGE_MARKER = "<!-- #changelog-release-automation-hook-do-not-remove -->"


def test_local_happy_path_end_to_end(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(chug.change, "detect_authors", lambda: [])

    init_result = runner.invoke(cli, ["init"], catch_exceptions=False)

    assert init_result.exit_code == 0
    assert (tmp_path / "chug.config.yml").exists()
    assert (tmp_path / "changes").is_dir()
    assert (tmp_path / "CHANGELOG.md").exists()
    assert CHANGE_MARKER in (tmp_path / "CHANGELOG.md").read_text()

    new_result = runner.invoke(
        cli,
        ["new", "--description", "Fix session timeout on mobile", "--category", "bug"],
        catch_exceptions=False,
    )

    assert new_result.exit_code == 0

    change_files = list((tmp_path / "changes").glob("*.yml"))
    assert len(change_files) == 1

    entry = yaml.safe_load(change_files[0].read_text())
    assert entry["description"] == "Fix session timeout on mobile"
    assert entry["category"] == "bug"
    assert entry["authors"] == []

    preview_result = runner.invoke(cli, ["preview"], catch_exceptions=False)

    assert preview_result.exit_code == 0
    assert "### Bug" in preview_result.output
    assert "Fix session timeout on mobile" in preview_result.output

    release_result = runner.invoke(
        cli,
        ["release", "--version", "0.1.0"],
        catch_exceptions=False,
    )

    assert release_result.exit_code == 0
    changelog = (tmp_path / "CHANGELOG.md").read_text()
    assert "## [0.1.0]" in changelog
    assert "### Bug" in changelog
    assert "Fix session timeout on mobile" in changelog
    assert not list((tmp_path / "changes").glob("*.yml"))
