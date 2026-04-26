"""Cycling typing-SVG builder.

Produces two SVGs:
  • about-typing.svg — N terminal commands cycling at the same screen position
  • motto-typing.svg — N philosophy quotes cycling

Each line types in, holds, erases, and waits — coordinated via SMIL keyTimes
on a per-line clipPath rect. Per-line color is thematic (terminal-prompt green
for ``$ whoami``, file-path orange for ``$ cat``, etc.).

Lines are categorized as ``generic`` (universal dev) or ``personal``
(references the user's specific projects from the config). The user picks
which categories to include via ``typing.about.include`` in cortex.yml.

Personal lines auto-substitute the user's identity fields where applicable
(github_user, primary projects from current_focus, etc.) so each profile
gets a personalized version without the user editing template strings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape as xml_escape

from cortex.schema import Config

Category = Literal["generic", "personal"]

# ─────────────────────────────────────────────────────────────────────────
# CURATED CONTENT
# Each entry: (text, color, category). Personal entries support {placeholders}
# substituted from the user's config at build time (see _expand_personal()).
# ─────────────────────────────────────────────────────────────────────────

ABOUT_LINES_GENERIC: list[tuple[str, str]] = [
    ("$ whoami", "#00C853"),  # green: terminal prompt
    ("$ pwd", "#22D3EE"),  # cyan: location
    ("$ cat about.py", "#FF652F"),  # orange: file path
    ("$ ls projects/", "#EC4899"),  # magenta: listing
    ("$ git status", "#F90001"),  # red: state check
    ("$ history | head", "#A78BFA"),  # purple: past commands
    ("$ uptime", "#34D399"),  # green: system info
    ("$ cat skills.json", "#FFD700"),  # gold: skills
    ("$ python --version", "#00C853"),
    ("$ tree -L 1", "#22D3EE"),
    ("$ docker ps", "#FF652F"),
    ("$ git log --oneline | head -3", "#EC4899"),
    ("$ stack list", "#F90001"),
    ("$ npm list -g --depth=0", "#A78BFA"),
    ("$ which python", "#34D399"),
    ("$ ls -la ~/code", "#FFD700"),
    ("$ pytest -q", "#00C853"),
    ("$ make build", "#22D3EE"),
    ("$ curl api.github.com/users/{github_user}", "#FF652F"),
    ("$ docker compose up -d", "#EC4899"),
    ("$ tmux attach", "#F90001"),
    ("$ vim ~/.config/me", "#A78BFA"),
    ("$ echo $LANG", "#34D399"),
    ("$ ssh prod -t htop", "#FFD700"),
    ("$ ps aux | grep python", "#00C853"),
    ("$ git push origin main", "#22D3EE"),
    ("$ tail -f /var/log/app.log", "#FF652F"),
    ("$ man developer", "#EC4899"),
    ("$ exit 0", "#A78BFA"),
    ("# open to collab", "#FFD700"),
]

ABOUT_LINES_PERSONAL: list[tuple[str, str]] = [
    ("$ cd ~/projects/{primary_project} && make dev", "#34D399"),
    ("$ python -m {primary_project} create my-app", "#F90001"),
    ("$ {primary_project} --status", "#FFD700"),
    ("$ docker compose -f {primary_project}.yml up", "#FFD700"),
    ("$ deploy.sh {primary_project}-prod", "#F90001"),
    ("$ tail -f /var/log/{primary_project}.log", "#34D399"),
    ("$ python manage.py migrate {primary_project}", "#A78BFA"),
    ("$ ssh {github_user}-prod", "#EC4899"),
    ("$ git checkout -b feature/new-thing", "#00C853"),
    ("$ pytest tests/ -v", "#FFD700"),
    ("$ gh extension install {github_user}/{primary_project}", "#F90001"),
    ("$ python -c 'import {github_user_pkg}'", "#A78BFA"),
    ("# made by {github_user}", "#22D3EE"),
    ("$ rabbitmq-plugins enable rabbitmq_management", "#FF652F"),
    ("$ npx nuxt build && npx nuxt start", "#22D3EE"),
    ("$ kubectl get pods -n {primary_project}", "#A78BFA"),
    ("$ redis-cli FLUSHDB", "#F90001"),
    ("$ celery worker -A {primary_project}", "#34D399"),
    ("$ make migrate && make seed", "#FFD700"),
    ("# from {location} with code", "#22D3EE"),
]

MOTTO_LINES_GENERIC: list[tuple[str, str]] = [
    ("// Curious about how systems break", "#FF652F"),
    ("// Stubborn about how they're rebuilt", "#F90001"),
    ("// Code should be useful before it's clever", "#FFD700"),
    ("// Boring architecture is usually the right one", "#34D399"),
    ("// Tests are letters from past me to future me", "#A78BFA"),
    ("// A good name is half the documentation", "#22D3EE"),
    ("// Ship -> measure -> learn -> ship again", "#EC4899"),
    ("// The simplest thing that could possibly work", "#00C853"),
    ("// Read the code, not the comments", "#FF652F"),
    ("// Premature optimization is the root of all evil", "#F90001"),
    ("// Make it work, make it right, make it fast", "#FFD700"),
    ("// Never trust user input", "#34D399"),
    ("// Naming things is the second-hardest problem", "#A78BFA"),
    ("// Off-by-one errors are inevitable -- design for them", "#22D3EE"),
    ("// Documentation is a love letter to your future self", "#EC4899"),
    ("// Refactor mercilessly once you understand more", "#00C853"),
    ("// Bugs are features waiting to be understood", "#FF652F"),
    ("// Empathy for the on-call engineer at 3am", "#F90001"),
    ("// YAGNI -- you aren't gonna need it", "#FFD700"),
    ("// The code is the source of truth -- comments lie", "#34D399"),
    ("// Done is better than perfect", "#A78BFA"),
    ("// First, do no harm to production", "#22D3EE"),
    ("// Question every assumption, including this one", "#EC4899"),
    ("// Patience is a feature, latency is a bug", "#00C853"),
    ("// Write code as if the next maintainer is psychotic", "#FF652F"),
    ("// Cache invalidation is one of two hard problems", "#F90001"),
    ("// The best code is code you don't have to write", "#FFD700"),
    ("// Build with care, deploy with confidence", "#34D399"),
    ("// Stay hungry, stay foolish -- keep shipping", "#A78BFA"),
    ("// Done > Perfect > Started", "#22D3EE"),
]

MOTTO_LINES_PERSONAL: list[tuple[str, str]] = [
    ("// I build for small businesses, not hyperscalers", "#FFD700"),
    ("// One keyboard, one ambition", "#FF652F"),
    ("// Code I write today runs in production tomorrow", "#34D399"),
    ("// Started in HTML, ended up in production", "#F90001"),
    ("// Production beats demo, every single Friday", "#FF652F"),
    ("// I write Python the way I'd explain it to a friend", "#FFD700"),
    ("// Build it once for yourself, then share it widely", "#00C853"),
    ("// Microservices for problems, monoliths for solutions", "#FFD700"),
    ("// Every commit is a small gift to my future team", "#22D3EE"),
    ("// From learning loop to long-running production", "#EC4899"),
    ("// Open-source what you wish others had shared with you", "#A78BFA"),
    ("// Made in {location}, for the world", "#A78BFA"),
    ("// Real users don't read API docs -- write smaller APIs", "#FF652F"),
    ("// Vue 3 because composition beats inheritance", "#34D399"),
    ("// The system never sleeps, the code shouldn't crash", "#F90001"),
    ("// I write what I'd want to maintain at 3am", "#A78BFA"),
    ("// Every shipped feature is a small bet that paid off", "#22D3EE"),
    ("// Less code, fewer bugs, happier users", "#FFD700"),
    ("// First principles over framework theology", "#FF652F"),
    ("// Still excited to type 'git init'", "#34D399"),
]


# ─────────────────────────────────────────────────────────────────────────
# Personal-line variable substitution
# ─────────────────────────────────────────────────────────────────────────


def _placeholder_values(config: Config) -> dict[str, str]:
    """Build the substitution map for personal-line placeholders."""
    primary_project = (
        config.cards.current_focus.tiles[0].project
        if config.cards.current_focus.tiles
        else config.identity.github_user.lower()
    )
    return {
        "github_user": config.identity.github_user,
        "github_user_pkg": config.identity.github_user.lower().replace("-", "_"),
        "primary_project": primary_project.lower().replace(" ", "-"),
        "location": config.identity.location or "Earth",
    }


def _expand_personal(line: str, vars: dict[str, str]) -> str:
    """Substitute {placeholder} tokens; missing tokens stay as literal text."""
    try:
        return line.format(**vars)
    except (KeyError, IndexError):
        return line


# ─────────────────────────────────────────────────────────────────────────
# clipPath keyTimes math (per-line type/hold/erase/off cycle)
# Cycle = N lines * seconds_per_line. Each line gets a time window with:
#   12% type / 62% hold / 10% erase / 16% off
# ─────────────────────────────────────────────────────────────────────────

_TYPE_RATIO = 0.12
_HOLD_RATIO = 0.62
_ERASE_RATIO = 0.10


def _round3(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".")


def _clip_animate(line_idx: int, n: int, reveal_w: int) -> tuple[str, str]:
    """Build (values, keyTimes) attribute strings for one line's animation."""
    window = 1.0 / n
    start = line_idx * window
    type_end = start + window * _TYPE_RATIO
    hold_end = start + window * (_TYPE_RATIO + _HOLD_RATIO)
    erase_end = start + window * (_TYPE_RATIO + _HOLD_RATIO + _ERASE_RATIO)

    if line_idx == 0:
        values = f"0;{reveal_w};{reveal_w};0;0"
        kt = f"0;{_round3(type_end)};{_round3(hold_end)};{_round3(erase_end)};1"
    elif line_idx == n - 1:
        values = f"0;0;{reveal_w};{reveal_w};0"
        kt = f"0;{_round3(start)};{_round3(type_end)};{_round3(hold_end)};1"
    else:
        values = f"0;0;{reveal_w};{reveal_w};0;0"
        kt = f"0;{_round3(start)};{_round3(type_end)};{_round3(hold_end)};{_round3(erase_end)};1"
    return values, kt


# ─────────────────────────────────────────────────────────────────────────
# SVG composition
# ─────────────────────────────────────────────────────────────────────────


def _compose(
    lines: list[tuple[str, str]],
    *,
    width: int,
    height: int,
    font_size: int,
    font_weight: int,
    total_dur_s: float,
    reveal_w: int,
    text_x: int,
    text_y: int,
    has_cursor: bool,
) -> str:
    n = len(lines)
    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="cycling typing animation, {n} lines">'
    )
    out.append("  <!-- Generated by cortex.builders.typing — see cortex.yml to customize. -->")
    out.append("  <style>")
    out.append(
        f"    .term {{ font-family: 'JetBrains Mono','Fira Code','SF Mono',"
        f"Consolas,monospace; font-size: {font_size}px; font-weight: {font_weight}; }}"
    )
    if has_cursor:
        # Cursor: jewel-tone cyan (matches DNA / aurora palette across widgets)
        # with a soft glow halo via feGaussianBlur. Step-end blink keeps the
        # terminal-cursor metaphor; ease-in-out would feel like a different
        # element entirely.
        out.append("    .cursor { fill: #4F8CC4; filter: url(#cursorGlow); }")
        out.append("    .cursor-blink { animation: blink 0.8s step-end infinite; }")
        out.append("    @keyframes blink { 50% { opacity: 0; } }")
    out.append("  </style>")
    out.append("  <defs>")
    if has_cursor:
        out.append(
            '    <filter id="cursorGlow" x="-200%" y="-50%" width="500%" height="200%">'
            '<feGaussianBlur stdDeviation="1.5" result="blur"/>'
            '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
            "</filter>"
        )

    for i in range(n):
        values, kt = _clip_animate(i, n, reveal_w)
        out.append(
            f'    <clipPath id="t{i:02d}"><rect x="0" y="0" height="{height}">'
            f'<animate attributeName="width" values="{values}" keyTimes="{kt}" '
            f'dur="{total_dur_s:g}s" repeatCount="indefinite"/></rect></clipPath>'
        )

    out.append("  </defs>")

    for i, (text, color) in enumerate(lines):
        safe = xml_escape(text, {"'": "&apos;", '"': "&quot;"})
        out.append(
            f'  <text class="term" x="{text_x}" y="{text_y}" fill="{color}" '
            f'clip-path="url(#t{i:02d})">{safe}</text>'
        )

    if has_cursor:
        cursor_h = font_size + 2
        cursor_y = text_y - font_size + 2
        out.append(
            f'  <rect class="cursor cursor-blink" x="6" y="{cursor_y}" '
            f'width="3" height="{cursor_h}"/>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────
# Line selection (filter by ``include`` + truncate to ``lines`` count)
# ─────────────────────────────────────────────────────────────────────────


def _select_lines(
    generic: list[tuple[str, str]],
    personal: list[tuple[str, str]],
    *,
    include: list[Category],
    target_count: int,
    config: Config,
) -> list[tuple[str, str]]:
    """Pick `target_count` lines respecting the `include` filter and substituting
    placeholders in personal lines. Generic lines first, then personal, capped."""
    pool: list[tuple[str, str]] = []
    if "generic" in include:
        pool.extend(generic)
    if "personal" in include:
        vars_ = _placeholder_values(config)
        pool.extend((_expand_personal(text, vars_), color) for text, color in personal)

    if not pool:
        # Sensible fallback: at least one motto so the SVG isn't empty
        return [("// configure typing.about.include in cortex.yml", "#9BA1A6")]

    return pool[:target_count]


# ─────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────


def build_about(config: Config, output: str | Path) -> Path:
    """Build the about-typing SVG (cycling terminal commands)."""
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    selection = _select_lines(
        ABOUT_LINES_GENERIC,
        ABOUT_LINES_PERSONAL,
        include=config.typing.about.include,
        target_count=config.typing.about.lines,
        config=config,
    )
    n = len(selection)
    seconds_per_line = 2.0
    svg = _compose(
        selection,
        width=600,
        height=60,
        font_size=22,
        font_weight=700,
        total_dur_s=n * seconds_per_line,
        reveal_w=580,
        text_x=20,
        text_y=40,
        has_cursor=True,
    )
    out_path.write_text(svg, encoding="utf-8")
    return out_path


def build_motto(config: Config, output: str | Path) -> Path:
    """Build the motto-typing SVG (cycling philosophy quotes)."""
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    selection = _select_lines(
        MOTTO_LINES_GENERIC,
        MOTTO_LINES_PERSONAL,
        include=config.typing.motto.include,
        target_count=config.typing.motto.lines,
        config=config,
    )
    n = len(selection)
    seconds_per_line = 3.0
    svg = _compose(
        selection,
        width=900,
        height=40,
        font_size=17,
        font_weight=500,
        total_dur_s=n * seconds_per_line,
        reveal_w=880,
        text_x=10,
        text_y=26,
        has_cursor=False,
    )
    out_path.write_text(svg, encoding="utf-8")
    return out_path
