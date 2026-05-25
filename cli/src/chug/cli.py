# ABOUTME: Command-line interface for Chug's init, new, preview, release, and validate workflow.
# ABOUTME: The CLI is non-interactive by default and operates on the current repository.

from pathlib import Path

import click

from . import __commit__, __version__
from ._validate import (
    CI_ERROR_MESSAGE,
    LOCAL_ERROR_MESSAGE,
    get_base_branch,
    get_changed_files,
    has_changes_entry,
    is_ci,
)
from .change import create_change_file
from .config import DEFAULT_CHANGE_MARKER, DEFAULT_CHANGELOG_FILE, changes_dir, load_config, write_default_config
from .release import apply_release, preview_markdown


def get_version_output(prog_name: str = "chug") -> str:
    return f"{prog_name}, version {__version__} ({__commit__})"


def show_version(ctx: click.Context, param: click.Option, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(get_version_output(ctx.command_path))
    ctx.exit()


@click.group(name="chug")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=show_version,
    help="Show the installed Chug version and commit.",
)
def cli() -> None:
    """Manage a team changelog through small change files."""


@cli.command()
def init() -> None:
    """Initialize the current repository for Chug."""
    write_default_config()
    changes_dir().mkdir(exist_ok=True)

    changelog = Path(DEFAULT_CHANGELOG_FILE)
    if not changelog.exists():
        initial_changelog = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented in this file.\n\n"
            f"{DEFAULT_CHANGE_MARKER}\n"
        )
        changelog.write_text(initial_changelog)

    click.echo("Initialized Chug in the current repository.")


@cli.command()
@click.option("--description", required=True, help="Description for the change entry.")
@click.option("--category", required=True, help="Category for the change entry.")
@click.option("--stories", "stories_csv", default="", help="Comma-separated story references.")
def new(description: str, category: str, stories_csv: str) -> None:
    """Create a new pending changelog entry."""
    config = load_config()
    if category not in config["categories"]:
        raise click.ClickException(f"Category '{category}' is not allowed in chug.config.yml.")

    stories = [item.strip() for item in stories_csv.split(",") if item.strip()] or None
    path = create_change_file(description=description, category=category, stories=stories)
    click.echo(f"Created changelog entry: {path}")


@cli.command()
def preview() -> None:
    """Render pending changelog entries without mutating files."""
    config = load_config()
    click.echo(preview_markdown(config), nl=False)


@cli.command()
@click.option("--version", required=True, help="Version string for the release section.")
def release(version: str) -> None:
    """Write a new changelog release section and delete processed changes."""
    config = load_config()
    processed = apply_release(version, config)
    click.echo(f"Released {processed} changelog entr{'y' if processed == 1 else 'ies'}.")


@cli.command()
def validate() -> None:
    """Check that a changelog entry exists for the current pull request."""
    config = load_config()

    base_branch = get_base_branch(config)

    try:
        changed_files = get_changed_files(base_branch)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    if has_changes_entry(changed_files):
        return

    if is_ci():
        click.echo(CI_ERROR_MESSAGE)
        raise SystemExit(1)
    else:
        raise click.ClickException(LOCAL_ERROR_MESSAGE)


def main() -> None:
    cli()
