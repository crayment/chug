# ABOUTME: Rendering tests for authors, stories, and no-change release behavior.
# ABOUTME: These tests lock down the markdown output that Chug writes to changelogs.

from pathlib import Path

import yaml
from chug.config import DEFAULT_CHANGE_MARKER, DEFAULT_CONFIG, changes_dir
from chug.release import apply_release, preview_markdown


def test_preview_renders_story_links_and_author_links(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    changes_dir().mkdir(exist_ok=True)

    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "stories": ["sc-12345"],
        "authors": [{"name": "Jane Doe", "github": "janedoe"}],
    }
    (changes_dir() / "2026-05-20T150000-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    rendered = preview_markdown(DEFAULT_CONFIG)

    assert "### Bug" in rendered
    assert "Fix session timeout on mobile" in rendered
    assert "[sc-12345](https://example.com/stories/sc-12345)" in rendered
    assert "[Jane Doe](https://github.com/janedoe)" in rendered


def test_release_with_no_changes_writes_no_changes_section(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(f"# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n{DEFAULT_CHANGE_MARKER}\n")

    processed = apply_release("0.1.0", DEFAULT_CONFIG)

    assert processed == 0
    contents = changelog.read_text()
    assert "## [0.1.0]" in contents
    assert "- No changes" in contents
