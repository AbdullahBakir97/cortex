"""`cortex validate` — check a cortex.yml against the schema."""
from __future__ import annotations

from pathlib import Path

import click
from pydantic import ValidationError

from cortex import Config


def run(*, config: Path) -> None:
    try:
        cfg = Config.from_yaml(config)
    except ValidationError as e:
        click.echo(click.style(f"[FAIL] {config} has {e.error_count()} validation error(s):", fg="red"), err=True)
        for err in e.errors():
            loc = ".".join(str(p) for p in err["loc"])
            click.echo(f"   {loc}: {err['msg']}", err=True)
        raise SystemExit(1)
    except Exception as e:  # noqa: BLE001
        click.echo(click.style(f"[FAIL] Could not parse {config}: {e}", fg="red"), err=True)
        raise SystemExit(1)

    click.echo(click.style(f"[OK] {config} is valid.", fg="green"))
    click.echo(f"     Schema version: {cfg.version}")
    click.echo(f"     Identity:       {cfg.identity.name} (@{cfg.identity.github_user})")
    click.echo(f"     Palette:        {cfg.brand.palette}")
    enabled_widgets = []
    if cfg.brain.enabled:                    enabled_widgets.append("brain")
    if cfg.cards.tech_stack.enabled:         enabled_widgets.append("tech-stack")
    if cfg.cards.current_focus.enabled:      enabled_widgets.append("current-focus")
    if cfg.cards.yearly_highlights.enabled:  enabled_widgets.append("yearly-highlights")
    if cfg.typing.about.enabled:             enabled_widgets.append("about-typing")
    if cfg.typing.motto.enabled:             enabled_widgets.append("motto-typing")
    click.echo(f"     Widgets:        {', '.join(enabled_widgets) if enabled_widgets else '(none)'}")
