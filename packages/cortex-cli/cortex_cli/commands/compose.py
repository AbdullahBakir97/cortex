"""`cortex compose` — stack widgets into a single SVG."""

from __future__ import annotations

from pathlib import Path

import click
from cortex import Config
from cortex.compose import compose, list_available


def run(*, config: Path, widgets: list[str], output: Path, gap: int) -> None:
    cfg = Config.from_yaml(config)
    if not widgets:
        click.echo(
            click.style(
                "[FAIL] At least one --widget is required. "
                f"Available: {', '.join(list_available())}",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(2)

    output.parent.mkdir(parents=True, exist_ok=True)
    click.echo(
        click.style(
            f"Composing {len(widgets)} widget(s) for @{cfg.identity.github_user}...",
            fg="cyan",
        )
    )
    for w in widgets:
        click.echo(f"     - {w}")

    out_path = compose(cfg, widgets, output, gap=gap)
    size_kb = out_path.stat().st_size / 1024
    click.echo()
    click.echo(click.style(f"[OK] Composite SVG -> {out_path}  ({size_kb:,.1f} KB)", fg="green"))
