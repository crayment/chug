# ABOUTME: Tests for build metadata and source-path commit fallback.
# ABOUTME: Verifies local source installs can recover a commit from direct_url metadata.

from pathlib import Path

import chug.cli


def test_get_commit_uses_direct_url_repository_when_build_commit_unknown(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source-repo"
    source_repo.mkdir()

    class FakeDistribution:
        @staticmethod
        def read_text(name: str) -> str:
            assert name == "direct_url.json"
            return '{"url": "file://' + str(source_repo) + '"}'

    monkeypatch.setattr(chug.cli, "__commit__", "unknown")
    monkeypatch.setattr(chug.cli.importlib.metadata, "distribution", lambda name: FakeDistribution())

    observed = {}

    def fake_run(args, check, capture_output, text, cwd):
        observed["cwd"] = cwd

        class Result:
            stdout = "6bc6069\n"

        return Result()

    monkeypatch.setattr(chug.cli.subprocess, "run", fake_run)

    assert chug.cli.get_commit() == "6bc6069"
    assert observed["cwd"] == source_repo
