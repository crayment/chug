# ABOUTME: Tests for optional GitHub PR enrichment in preview and release output.
# ABOUTME: These tests verify PR links are additive and degrade gracefully on failure.

from pathlib import Path

import yaml

from chug.config import DEFAULT_CONFIG, changes_dir
from chug.release import preview_markdown


def test_preview_includes_pr_links_when_github_lookup_succeeds(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "crayment/chug-testing")
    monkeypatch.setattr("chug.release._get_repo_root", lambda: tmp_path)

    changes_dir().mkdir(exist_ok=True)
    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "authors": [{"name": "Jane Doe", "github": "janedoe"}],
    }
    (changes_dir() / "2026-05-20T150500-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    def fake_get(url, headers=None, params=None, timeout=None):
        class Response:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        if url.endswith("/commits"):
            return Response([{"sha": "abc123"}])
        if url.endswith("/commits/abc123/pulls"):
            return Response([{"number": 87}])
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("requests.get", fake_get)

    rendered = preview_markdown(DEFAULT_CONFIG)

    assert "[#87](https://github.com/crayment/chug-testing/pull/87)" in rendered
    assert "[Jane Doe](https://github.com/janedoe)" in rendered


def test_preview_warns_and_omits_pr_links_when_lookup_fails(tmp_path: Path, monkeypatch, caplog) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "crayment/chug-testing")
    monkeypatch.setattr("chug.release._get_repo_root", lambda: tmp_path)

    changes_dir().mkdir(exist_ok=True)
    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "authors": [],
    }
    (changes_dir() / "2026-05-20T150600-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    def failing_get(url, headers=None, params=None, timeout=None):
        raise RuntimeError("boom")

    monkeypatch.setattr("requests.get", failing_get)

    rendered = preview_markdown(DEFAULT_CONFIG)

    assert "[#" not in rendered
    assert "Fix session timeout on mobile" in rendered
    assert "Failed to enrich PR information" in caplog.text
