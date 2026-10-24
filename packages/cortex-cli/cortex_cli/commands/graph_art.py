"""`cortex graph-art` — read a contribution graph as a story and as drawings."""

from __future__ import annotations

import glob
import json
from pathlib import Path

import click
from cortex.github_api import client_from_env
from cortex.graphart.analysis import summarize_year
from cortex.graphart.calendar import Calendar
from cortex.graphart.detect import detect
from cortex.graphart.figures import load_figures, save_figures, validate_figure
from cortex.graphart.name_art import render_name_art
from cortex.graphart.render import render_gallery, render_year_story


def load_calendar(user: str | None, calendar: str | None, heatmaps: str | None) -> Calendar:
    if calendar:
        return Calendar.from_json(calendar)
    if heatmaps:
        files = sorted(glob.glob(heatmaps))
        if not files:
            raise click.ClickException(f"no files match {heatmaps}")
        return Calendar.from_heatmap_svgs(files)
    if user:
        try:
            return Calendar.from_github(client_from_env(user))
        except RuntimeError as e:
            raise click.ClickException(f"{e} (set GH_TOKEN or GITHUB_TOKEN)") from e
    raise click.ClickException("give --user, --calendar or --heatmaps")


def source_options(f):
    f = click.option("--heatmaps", help="Glob of SVGs with <title>N on YYYY-MM-DD</title> cells.")(
        f
    )
    f = click.option(
        "--calendar",
        type=click.Path(exists=True, dir_okay=False),
        help="calendar.json from `fetch`.",
    )(f)
    f = click.option("-u", "--user", help="GitHub login (needs GH_TOKEN or GITHUB_TOKEN).")(f)
    return f


@click.group("graph-art")
def group() -> None:
    """Find the story and the drawings in a contribution graph."""


@group.command("fetch")
@click.option("-u", "--user", required=True)
@click.option("-o", "--out", default="calendar.json", show_default=True)
def fetch(user: str, out: str) -> None:
    """Save every year of daily contribution counts to a JSON file."""
    cal = load_calendar(user, None, None)
    cal.to_json(out)
    click.echo(f"saved {len(cal.days)} days ({', '.join(map(str, cal.years()))}) to {out}")


@group.command("analyze")
@source_options
@click.option("--json", "as_json", is_flag=True, help="Print machine-readable JSON.")
def analyze(user, calendar, heatmaps, as_json) -> None:
    """Per-year story: stretches, longest streak, biggest day."""
    cal = load_calendar(user, calendar, heatmaps)
    out = []
    for y in cal.years():
        s = summarize_year(cal, y)
        row = {
            "year": y,
            "total": s.total,
            "active_days": s.active_days,
            "best_month": s.best_month,
            "stretches": [
                {"kind": st.kind, "when": st.when, "caption": st.caption(), "running": st.running}
                for st in s.stretches
            ],
            "longest_streak": s.streak
            and {"from": str(s.streak[0]), "to": str(s.streak[1]), "days": s.streak[2]},
            "biggest_day": s.biggest_day
            and {"date": str(s.biggest_day[0]), "count": s.biggest_day[1]},
        }
        out.append(row)
    if as_json:
        click.echo(json.dumps(out, indent=2))
        return
    for r in out:
        click.echo(f"{r['year']}: {r['total']:,} contributions on {r['active_days']} days")
        for st in r["stretches"]:
            click.echo(f"  - {st['kind']:<6} {st['caption']}")
        if r["longest_streak"]:
            click.echo(
                f"  longest streak {r['longest_streak']['days']} days, biggest day {r['biggest_day']['date']}"
            )


@group.command("detect")
@source_options
@click.option("-o", "--out", default="figures.draft.json", show_default=True)
@click.option("--per-year", default=4, show_default=True)
def detect_cmd(user, calendar, heatmaps, out, per_year) -> None:
    """Suggest shapes hiding in the graph. Review them, then rename/edit into figures.json."""
    cal = load_calendar(user, calendar, heatmaps)
    figs = detect(cal, limit_per_year=per_year)
    save_figures(figs, out)
    click.echo(f"{len(figs)} candidates written to {out}")
    for f in figs:
        click.echo(f"  {f.year} {f.when:<12} {f.name:<16} score {f.score}  ({f.source})")


@group.command("check")
@source_options
@click.option("-f", "--figures", required=True, type=click.Path(exists=True, dir_okay=False))
def check(user, calendar, heatmaps, figures) -> None:
    """Fail if a figure colours a day that had no contributions."""
    cal = load_calendar(user, calendar, heatmaps)
    bad = 0
    for f in load_figures(figures):
        problems = validate_figure(f, cal)
        bad += bool(problems)
        click.echo(f"{'ok ' if not problems else 'BAD'} {f.year} {f.name}")
        for p in problems[:5]:
            click.echo(f"      {p}")
    if bad:
        raise click.ClickException(f"{bad} figure(s) are not true to the graph")


@group.command("render")
@source_options
@click.option(
    "-f", "--figures", type=click.Path(exists=True, dir_okay=False), help="Confirmed figures.json."
)
@click.option("-o", "--out", default="assets", show_default=True)
def render(user, calendar, heatmaps, figures, out) -> None:
    """Write year-story.svg and, with --figures, graph-art.svg."""
    cal = load_calendar(user, calendar, heatmaps)
    d = Path(out)
    d.mkdir(parents=True, exist_ok=True)
    (d / "year-story.svg").write_text(render_year_story(cal), encoding="utf-8")
    click.echo(f"wrote {d / 'year-story.svg'}")
    if figures:
        figs = load_figures(figures)
        for f in figs:
            if validate_figure(f, cal):
                raise click.ClickException(
                    f"{f.name} is not true to the graph; run `cortex graph-art check`"
                )
        (d / "graph-art.svg").write_text(render_gallery(figs, cal), encoding="utf-8")
        click.echo(f"wrote {d / 'graph-art.svg'} ({len(figs)} figures)")


@group.command("name-art")
@source_options
@click.option("-n", "--name", required=True, help='The name to write, e.g. "Ada Lovelace".')
@click.option(
    "-f",
    "--figures",
    type=click.Path(exists=True, dir_okay=False),
    help="Confirmed figures.json to place around it.",
)
@click.option("--handle", default="", help="Shown in the footer, e.g. github.com/you.")
@click.option("-o", "--out", default="assets/name-art.svg", show_default=True)
def name_art_cmd(user, calendar, heatmaps, name, figures, handle, out) -> None:
    """Write NAME in your real commit days, with drawings, an octopus and a worm."""
    cal = load_calendar(user, calendar, heatmaps)
    figs = load_figures(figures) if figures else []
    for f in figs:
        if validate_figure(f, cal):
            raise click.ClickException(
                f"{f.name} is not true to the graph; run `cortex graph-art check`"
            )
    svg = render_name_art(cal, name, handle or (f"github.com/{user}" if user else ""), figs)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(svg, encoding="utf-8")
    click.echo(f"wrote {out} ({len(svg) // 1024} KB, {len(figs)} drawings)")
