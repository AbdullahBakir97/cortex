"""`cortex update-readme` — rewrite README marker blocks from live data."""
from __future__ import annotations

from pathlib import Path

import click

from cortex import Config
from cortex.github_api import client_from_env
from cortex.markers import update as markers_update


def run(*, config: Path, readme: Path) -> None:
    cfg = Config.from_yaml(config)
    if not readme.exists():
        click.echo(click.style(f"[WARN] {readme} does not exist — nothing to update.", fg="yellow"))
        return

    click.echo(click.style(f"Rewriting marker blocks in {readme}...", fg="cyan"))
    client = client_from_env(cfg.identity.github_user)
    if not client.token:
        click.echo(click.style(
            "       (no GH_TOKEN/GITHUB_TOKEN set — token-only sections will be skipped)",
            fg="white",
        ))

    result = markers_update(cfg, readme, client=client)

    for name in result.sections_updated:
        click.echo(click.style(f"     [OK]      CORTEX:{name}", fg="green"))
    for name in result.sections_missing:
        click.echo(click.style(f"     [missing] CORTEX:{name} — paste the marker pair to enable", fg="white"))
    for name in result.sections_skipped:
        click.echo(click.style(f"     [skip]    CORTEX:{name} — disabled in config", fg="white"))
    for name, err in result.sections_failed:
        click.echo(click.style(f"     [FAIL]    CORTEX:{name} — {err}", fg="red"))

    click.echo()
    if result.changed:
        click.echo(click.style(f"[OK] README updated — {len(result.sections_updated)} section(s) refreshed.", fg="green"))
    else:
        click.echo("[OK] No changes.")
