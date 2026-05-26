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


def test_preview_renders_full_url_story_as_link_with_path_label(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    changes_dir().mkdir(exist_ok=True)

    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "stories": ["https://linear.app/myteam/issue/OPS-79/fix-session-timeout"],
    }
    (changes_dir() / "2026-05-26T100000-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    rendered = preview_markdown(DEFAULT_CONFIG)

    expected = "[/myteam/issue/OPS-79/fix-session-timeout](https://linear.app/myteam/issue/OPS-79/fix-session-timeout)"
    assert expected in rendered


def test_preview_renders_full_url_story_without_path_as_bare_link(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    changes_dir().mkdir(exist_ok=True)

    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "stories": ["https://example.com/PROJ-42"],
    }
    (changes_dir() / "2026-05-26T100001-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    rendered = preview_markdown(DEFAULT_CONFIG)

    assert "[/PROJ-42](https://example.com/PROJ-42)" in rendered


def test_preview_renders_url_story_ignoring_story_link_template(tmp_path: Path, monkeypatch) -> None:
    """A full URL story bypasses the story_link_template entirely."""
    monkeypatch.chdir(tmp_path)
    changes_dir().mkdir(exist_ok=True)

    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "stories": ["https://mytracker.io/issues/123"],
    }
    (changes_dir() / "2026-05-26T100002-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    config = {**DEFAULT_CONFIG, "story_link_template": "https://example.com/stories/{id}"}
    rendered = preview_markdown(config)

    # Should NOT have the template applied to the URL
    assert "https://example.com/stories/https" not in rendered
    # Should use the URL directly
    assert "[/issues/123](https://mytracker.io/issues/123)" in rendered


def test_preview_renders_url_story_with_no_path_using_netloc_as_label(tmp_path: Path, monkeypatch) -> None:
    """A URL with no path (e.g. https://example.com) falls back to netloc as the link label."""
    monkeypatch.chdir(tmp_path)
    changes_dir().mkdir(exist_ok=True)

    entry = {
        "description": "Fix session timeout on mobile",
        "category": "bug",
        "stories": ["https://example.com"],
    }
    (changes_dir() / "2026-05-26T100003-fix.yml").write_text(yaml.safe_dump(entry, sort_keys=False))

    rendered = preview_markdown(DEFAULT_CONFIG)

    assert "[example.com](https://example.com)" in rendered


def test_release_with_no_changes_writes_no_changes_section(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    changelog = tmp_path / "CHANGELOG.md"
    initial_changelog = (
        "# Changelog\n\n"
        "All notable changes to this project will be documented in this file.\n\n"
        f"{DEFAULT_CHANGE_MARKER}\n"
    )
    changelog.write_text(initial_changelog)

    processed = apply_release("0.1.0", DEFAULT_CONFIG)

    assert processed == 0
    contents = changelog.read_text()
    assert "## [0.1.0]" in contents
    assert "- No changes" in contents
