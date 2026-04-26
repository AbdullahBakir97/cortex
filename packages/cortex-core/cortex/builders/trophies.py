"""Achievement Wall / Trophy Cabinet — beveled cabinet with mounted trophies.

Each trophy is a hexagonal medallion with a glyph (emoji or letter) at its
center, label below, and date sub-label. Trophies are arranged in a grid.
The whole cabinet has a subtle wood-grain background and inset bevels for
a tactile feel.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, TrophiesConfig


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

DEFAULT_PALETTE = ["#FFD23F", "#FF6B9D", "#22D3EE", "#34D399", "#7C3AED", "#F90001"]


def _hex_path(cx: float, cy: float, r: float) -> str:
    """Pointy-top hexagon centered on (cx, cy) with radius r."""
    pts = []
    for i, angle in enumerate([90, 30, -30, -90, -150, 150]):
        import math

        a = math.radians(angle)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy - r * math.sin(a):.1f}")
        if i == 0:
            d_start = pts[-1]
    d_start = pts[0]
    return "M " + d_start + " L " + " L ".join(pts[1:]) + " Z"


def _trophy(cx: float, cy: float, label: str, date: str, glyph: str, color: str, idx: int) -> str:
    radius = 48
    hex_d = _hex_path(cx, cy, radius)

    # Pulse on the trophy face — subtle scale breathing.
    pulse = (
        '<animateTransform attributeName="transform" type="scale" '
        f'values="1;1.03;1" dur="{3.5 + (idx % 3) * 0.4:.1f}s" '
        'repeatCount="indefinite" additive="sum"/>'
    )

    glyph_svg = ""
    if glyph:
        glyph_svg = (
            f'<text x="{cx:.1f}" y="{cy + 6:.1f}" class="tr-glyph" '
            f'text-anchor="middle">{_x(glyph)}</text>'
        )

    return f"""
  <g transform="translate({cx:.1f},{cy:.1f})">
    {pulse}
    <g transform="translate({-cx:.1f},{-cy:.1f})">
      <path d="{hex_d}" fill="url(#tr-grad-{idx})" stroke="#FFFFFF"
            stroke-opacity="0.42" stroke-width="2" filter="url(#tr-shadow)"/>
      <path d="{hex_d}" fill="none" stroke="{color}" stroke-opacity="0.9"
            stroke-width="1.5" stroke-dasharray="3 4">
        <animate attributeName="stroke-dashoffset" from="0" to="-14"
                 dur="6s" repeatCount="indefinite"/>
      </path>
      {glyph_svg}
    </g>
  </g>
  <text x="{cx:.1f}" y="{cy + radius + 22:.1f}" class="tr-label" text-anchor="middle">{_x(label)}</text>
  <text x="{cx:.1f}" y="{cy + radius + 38:.1f}" class="tr-date" text-anchor="middle">{_x(date)}</text>
"""


def _grad_defs(trophies: list, palette: list[str]) -> str:
    parts = []
    for i, t in enumerate(trophies):
        color = t.color or palette[i % len(palette)]
        parts.append(
            f'<radialGradient id="tr-grad-{i}" cx="40%" cy="35%" r="70%">'
            f'<stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.25"/>'
            f'<stop offset="50%" stop-color="{color}" stop-opacity="0.95"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0.55"/>'
            f"</radialGradient>"
        )
    return "\n  ".join(parts)


def _render(config: Config) -> str:
    tcfg: TrophiesConfig = config.cards.trophies
    height = tcfg.height
    title = tcfg.title or "Achievements"

    if not tcfg.trophies:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
            'role="img" aria-label="Trophy cabinet (empty)"></svg>\n'
        )

    cols = max(1, tcfg.columns)
    n = len(tcfg.trophies)
    rows = (n + cols - 1) // cols
    margin_x = 80
    margin_top = 80
    cell_w = (WIDTH - 2 * margin_x) / cols
    cell_h = (height - margin_top - 30) / max(1, rows)

    palette = DEFAULT_PALETTE
    bodies = []
    for i, t in enumerate(tcfg.trophies):
        col = i % cols
        row = i // cols
        cx = margin_x + col * cell_w + cell_w / 2
        cy = margin_top + row * cell_h + cell_h / 2 - 10
        color = t.color or palette[i % len(palette)]
        bodies.append(_trophy(cx, cy, t.label, t.date, t.glyph or "★", color, i))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="{_x(title)}">
  <defs>
    <linearGradient id="tr-cabinet" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1A0F0A"/>
      <stop offset="40%" stop-color="#2A1A12"/>
      <stop offset="100%" stop-color="#0E0805"/>
    </linearGradient>
    <linearGradient id="tr-shelf" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#5C3A24"/>
      <stop offset="100%" stop-color="#3A2418"/>
    </linearGradient>
    <filter id="tr-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.65"/>
    </filter>
    {_grad_defs(tcfg.trophies, palette)}
  </defs>
  <style><![CDATA[
    .tr-title {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 24px; letter-spacing: 0.24em; text-transform: uppercase; fill: #FFFFFF; }}
    .tr-label {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 700; font-size: 13px; fill: #FFFFFF; fill-opacity: 0.92; letter-spacing: 0.04em; }}
    .tr-date  {{ font-family: 'JetBrains Mono','SF Mono',monospace; font-weight: 500; font-size: 10px; fill: #FFFFFF; fill-opacity: 0.55; letter-spacing: 0.12em; }}
    .tr-glyph {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 28px; fill: #FFFFFF; text-anchor: middle; }}
  ]]></style>
  <rect x="0" y="0" width="{WIDTH}" height="{height}" fill="url(#tr-cabinet)"/>
  <rect x="20" y="20" width="{WIDTH - 40}" height="{height - 40}" fill="none"
        stroke="#5C3A24" stroke-opacity="0.6" stroke-width="2"/>
  <text x="{WIDTH / 2}" y="48" class="tr-title" text-anchor="middle">{_x(title)}</text>
  {"".join(bodies)}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
