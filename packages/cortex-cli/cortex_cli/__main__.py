"""Cortex CLI entry point.

Usage:
    cortex init [--template TEMPLATE] [--output PATH]
    cortex validate [CONFIG]
    cortex build [--config CONFIG] [--output DIR]
    cortex update-readme [--config CONFIG] [--readme PATH]
    cortex viewer [--config CONFIG] [--output DIR]
    cortex --version
    cortex --help
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from cortex_cli import __version__
from cortex_cli.commands import build as build_cmd
from cortex_cli.commands import compose as compose_cmd
from cortex_cli.commands import init as init_cmd
from cortex_cli.commands import update_readme as update_readme_cmd
from cortex_cli.commands import validate as validate_cmd
from cortex_cli.commands import viewer as viewer_cmd

DEFAULT_CONFIG = ".github/cortex.yml"
DEFAULT_OUTPUT = "assets"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", prog_name="cortex")
def cli() -> None:
    """Cortex — turn your GitHub into a cinematic neon brain skill atlas."""


@cli.command("init")
@click.option(
    "-t",
    "--template",
    type=click.Choice(
        [
            "minimal",
            "standard",
            "extreme",
            "backend-engineer",
            "frontend-specialist",
            "full-stack",
            "data-scientist",
            "devops",
            "student",
        ]
    ),
    default="standard",
    show_default=True,
    help="Starter template archetype.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=DEFAULT_CONFIG,
    show_default=True,
    help="Where to write the generated cortex.yml.",
)
def init_command(template: str, output: str) -> None:
    """Scaffold a starter cortex.yml in the current repo."""
    init_cmd.run(template=template, output=Path(output))


@cli.command("validate")
@click.argument(
    "config",
    type=click.Path(exists=True, dir_okay=False),
    default=DEFAULT_CONFIG,
)
def validate_command(config: str) -> None:
    """Validate a cortex.yml file against the schema."""
    validate_cmd.run(config=Path(config))


@cli.command("build")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=DEFAULT_CONFIG,
    show_default=True,
    help="Path to your cortex.yml.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=DEFAULT_OUTPUT,
    show_default=True,
    help="Output directory for generated SVG assets.",
)
def build_command(config: str, output: str) -> None:
    """Render every enabled SVG to the output directory."""
    build_cmd.run(config=Path(config), output_dir=Path(output))


@cli.command("compose")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=DEFAULT_CONFIG,
    show_default=True,
    help="Path to your cortex.yml.",
)
@click.option(
    "-w",
    "--widget",
    "widgets",
    multiple=True,
    help="Widget slug to include (repeatable). Use --list to see available slugs.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="assets/composite.svg",
    show_default=True,
    help="Output path for the composite SVG.",
)
@click.option(
    "--gap",
    type=int,
    default=12,
    show_default=True,
    help="Vertical pixel gap between stacked widgets.",
)
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    default=False,
    help="Print the available widget slugs and exit.",
)
def compose_command(
    config: str, widgets: tuple[str, ...], output: str, gap: int, list_only: bool
) -> None:
    """Stack listed widgets into a single SVG (one image to drop in your README)."""
    if list_only:
        from cortex.compose import list_available

        for slug in list_available():
            click.echo(slug)
        return
    compose_cmd.run(config=Path(config), widgets=list(widgets), output=Path(output), gap=gap)


@cli.command("update-readme")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=DEFAULT_CONFIG,
    show_default=True,
)
@click.option(
    "-r",
    "--readme",
    type=click.Path(),
    default="README.md",
    show_default=True,
    help="Path to the README to rewrite.",
)
def update_readme_command(config: str, readme: str) -> None:
    """Rewrite README marker blocks (ACTIVITY, QUOTE, etc.) from live data."""
    update_readme_cmd.run(config=Path(config), readme=Path(readme))


@cli.command("viewer")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=DEFAULT_CONFIG,
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="docs",
    show_default=True,
    help="Output directory for the 3D viewer (typically /docs for GitHub Pages).",
)
def viewer_command(config: str, output: str) -> None:
    """Build the Three.js 3D viewer."""
    viewer_cmd.run(config=Path(config), output_dir=Path(output))


def main() -> int:
    try:
        cli(standalone_mode=False)
        return 0
    except click.exceptions.Exit as e:
        return e.exit_code or 0
    except click.exceptions.UsageError as e:
        click.echo(f"Error: {e.message}", err=True)
        return 2
    except Exception as e:
        click.echo(f"Unhandled error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
