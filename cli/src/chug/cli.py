# ABOUTME: Command-line interface for Chug's init, new, preview, and release workflow.
# ABOUTME: The CLI is non-interactive by default and operates on the current repository.

from pathlib import Path
import json
import subprocess
from urllib.parse import unquote, urlparse
import importlib.metadata

import click

from . import __commit__, __version__
from .change import create_change_file
from .config import DEFAULT_CHANGE_MARKER, DEFAULT_CHANGELOG_FILE, changes_dir, load_config, write_default_config
from .release import apply_release, preview_markdown


def get_commit() -> str:
    if __commit__ != "unknown":
        return __commit__

    repo_dir = get_source_repository_dir()
    if repo_dir is not None:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            cwd=repo_dir,
        )
        commit = result.stdout.strip()
        if commit:
            return commit

    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent,
    )
    commit = result.stdout.strip()
    return commit or __commit__


def get_source_repository_dir() -> Path | None:
    try:
        distribution = importlib.metadata.distribution("chug-cli")
        direct_url = distribution.read_text("direct_url.json")
    except importlib.metadata.PackageNotFoundError:
        return None

    if not direct_url:
        return None

    data = json.loads(direct_url)
    url = data.get("url")
    if not url:
        return None

    parsed_url = urlparse(url)
    if parsed_url.scheme != "file":
        return None

    return Path(unquote(parsed_url.path))


def get_version_output(prog_name: str = "chug") -> str:
    return f"{prog_name}, version {__version__} ({get_commit()})"


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


def main() -> None:
    cli()
