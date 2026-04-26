"""`cortex viewer` — build the Three.js 3D viewer.

Stub for v0.1. The Vite project lives at ``packages/cortex-3d``; this command
will run its build and copy the static output to the user's /docs directory.
"""

from __future__ import annotations

from pathlib import Path

import click
from cortex import Config


def run(*, config: Path, output_dir: Path) -> None:
    cfg = Config.from_yaml(config)
    click.echo(
        click.style(
            "[STUB] cortex viewer not implemented yet (cortex-3d v0.1).",
            fg="yellow",
        )
    )
    click.echo(
        f"       Would build Three.js viewer for @{cfg.identity.github_user} into {output_dir}/."
    )
    click.echo("       This will be wired up alongside packages/cortex-3d in the next session.")
