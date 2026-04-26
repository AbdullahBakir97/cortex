"""`cortex build` — run every enabled builder, write SVGs to output dir."""
from __future__ import annotations

import time
from pathlib import Path

import click

from cortex import Config, build_all


def run(*, config: Path, output_dir: Path) -> None:
    cfg = Config.from_yaml(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(click.style(f"Building Cortex profile for @{cfg.identity.github_user}...", fg="cyan"))
    start = time.perf_counter()

    results = build_all(cfg, output_dir=str(output_dir))

    elapsed = (time.perf_counter() - start) * 1000

    # Per-widget status summary
    built = [f for f, s in results.items() if s == "built"]
    disabled = [f for f, s in results.items() if s == "disabled"]
    not_impl = [f for f, s in results.items() if s == "not-implemented"]

    for svg_name in built:
        path = output_dir / svg_name
        if path.exists():
            size_kb = path.stat().st_size / 1024
            click.echo(click.style(f"     [OK]   {svg_name:30s}  {size_kb:6.1f} KB", fg="green"))
    for svg_name in not_impl:
        click.echo(click.style(f"     [TODO] {svg_name:30s}  (not implemented in v0.1)", fg="yellow"))
    for svg_name in disabled:
        click.echo(click.style(f"     [skip] {svg_name:30s}  (disabled in config)", fg="white"))

    click.echo()
    click.echo(click.style(f"[OK] {len(built)} widget(s) built in {elapsed:,.0f} ms", fg="green"))
