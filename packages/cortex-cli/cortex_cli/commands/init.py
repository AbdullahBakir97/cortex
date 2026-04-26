"""`cortex init` — scaffold a starter cortex.yml from a template archetype."""
from __future__ import annotations

from importlib import resources
from pathlib import Path

import click


def run(*, template: str, output: Path) -> None:
    if output.exists():
        if not click.confirm(f"{output} already exists. Overwrite?", default=False):
            click.echo("Aborted.")
            raise SystemExit(0)

    output.parent.mkdir(parents=True, exist_ok=True)

    # In v0.1 the templates aren't shipped yet — fall back to a minimal default.
    # When the templates/ directory is populated, this will load from package data.
    try:
        template_text = resources.files("cortex_cli.templates").joinpath(f"{template}.yml").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        template_text = _minimal_template()

    output.write_text(template_text, encoding="utf-8")
    click.echo(click.style(f"[OK] Scaffolded {output} (template: {template})", fg="green"))
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Edit {output} to taste")
    click.echo(f"  2. cortex validate {output}")
    click.echo(f"  3. cortex build")


def _minimal_template() -> str:
    return """# yaml-language-server: $schema=https://cortex.dev/schema/v1.json
# .github/cortex.yml — Cortex profile configuration
# Docs: https://docs.cortex.dev

version: 1

identity:
  name: "Your Name"
  github_user: "yourhandle"
  tagline: "What you do, in one line"
  location: ""

brand:
  palette: "neon-rainbow"           # neon-rainbow | monochrome | cyberpunk | minimal | retro

brain:
  enabled: true
  three_d:
    enabled: true                   # publishes interactive viewer to /docs
  regions:
    frontal:    { domain: "Backend",       tools: [Python, Django] }
    parietal:   { domain: "Architecture",  tools: [Microservices] }
    occipital:  { domain: "Frontend",      tools: [Vue, TypeScript] }
    temporal:   { domain: "Data Layer",    tools: [PostgreSQL, Redis] }
    cerebellum: { domain: "DevOps",        tools: [Docker, Git] }
    brainstem:  { domain: "AI & Data",     tools: [LLMs, RAG] }

typing:
  header:
    enabled: true
    languages: [en]
    lines_per_language: 10
  about:
    enabled: true
    lines: 30
  motto:
    enabled: true
    lines: 30

cards:
  tech_stack:        { enabled: true }
  yearly_highlights: { enabled: true, start_year: 2023 }
  current_focus:     { enabled: true }

auto_update:
  schedule: "0 6 * * *"
  markers:
    activity:         true
    latest_releases:  true
    quote_of_the_day: true
    gitgraph:         true
"""
