"""`cortex update-readme` — rewrite README marker blocks from live data.

Stub for v0.1. Wires up to ``cortex.markers.update`` once that module is ported.
"""
from __future__ import annotations

from pathlib import Path

import click

from cortex import Config


def run(*, config: Path, readme: Path) -> None:
    cfg = Config.from_yaml(config)
    if not readme.exists():
        click.echo(click.style(f"[WARN] {readme} does not exist — nothing to update.", fg="yellow"))
        return

    click.echo(click.style(
        f"[STUB] cortex.markers.update not ported yet (cortex-core v0.1).",
        fg="yellow",
    ))
    click.echo(f"       Would update marker blocks in {readme} for @{cfg.identity.github_user}.")
    click.echo("       This will be wired up in cortex-core v0.2 (next session).")
