# ABOUTME: Tests for the CLI version output.
# ABOUTME: Verifies Chug reports the package version and commit hash.

from click.testing import CliRunner

import chug.cli
from chug.cli import cli


def test_version_output_includes_version_and_commit(monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.setattr(chug.cli, "__version__", "1.2.3")
    monkeypatch.setattr(chug.cli, "get_commit", lambda: "6bc6069")

    result = runner.invoke(cli, ["--version"], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == "chug, version 1.2.3 (6bc6069)\n"
