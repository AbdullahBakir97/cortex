"""Code DNA Helix — twin spiral strands with language base-pairs.

Two sinusoidal strands wrap around each other (one phase-shifted by π) with
colored "rungs" between them at regular intervals — each rung represents a
top language. Whole helix rotates slowly with optional language labels
floating beside the rungs.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, DnaConfig
from ..themes import REDUCED_MOTION_CSS


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

_DEFAULT_PALETTE = [
    "#FFD23F",
    "#FF6B9D",
    "#22D3EE",
    "#7C3AED",
    "#34D399",
    "#F90001",
    "#FF9D6B",
    "#A78BFA",
]


def _strand_path(amp: float, period: float, y_center: float, phase: float, width: int) -> str:
    """Sample a sine curve and emit a polyline-style path with line segments."""
    samples = 80
    pts = []
    for i in range(samples + 1):
        x = i * width / samples
        y = y_center + amp * math.sin((x / period) * 2 * math.pi + phase)
        pts.append((x, y))
    d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f},{y:.1f}"
    return d


def _render(config: Config) -> str:
    dcfg: DnaConfig = config.cards.dna
    h = dcfg.height
    title = dcfg.title or ""
    languages = dcfg.languages

    if not languages:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {h}" '
            'role="img" aria-label="Code DNA (empty)"></svg>\n'
        )

    # Helix geometry.
    y_center = h / 2 + 10
    amp = (h - 80) / 2 - 30
    # Pick period so we get ~3.5 full waves across the canvas — looks like a real helix.
    period = WIDTH / 3.5

    strand_a = _strand_path(amp, period, y_center, phase=0, width=WIDTH)
    strand_b = _strand_path(amp, period, y_center, phase=math.pi, width=WIDTH)

    # Rungs: connect strand A to strand B at evenly-spaced x-positions.
    # Number of rungs = number of languages, spaced across the canvas.
    n = max(1, len(languages))
    margin_x = 60
    rung_xs = (
        [margin_x + i * (WIDTH - 2 * margin_x) / max(1, n - 1) for i in range(n)]
        if n > 1
        else [WIDTH / 2]
    )

    rungs = []
    labels = []
    for i, x in enumerate(rung_xs):
        y_a = y_center + amp * math.sin((x / period) * 2 * math.pi)
        y_b = y_center + amp * math.sin((x / period) * 2 * math.pi + math.pi)
        color = (
            dcfg.colors[i]
            if i < len(dcfg.colors) and dcfg.colors[i]
            else _DEFAULT_PALETTE[i % len(_DEFAULT_PALETTE)]
        )
        # Rung as colored line + bead at each end.
        delay = (i * 0.18) % 4
        rungs.append(f"""
  <g>
    <line x1="{x:.1f}" y1="{y_a:.1f}" x2="{x:.1f}" y2="{y_b:.1f}"
          stroke="{color}" stroke-width="3" stroke-opacity="0.85"
          stroke-linecap="round" filter="url(#dna-glow)">
      <animate attributeName="stroke-opacity" values="0.55;1;0.55"
               begin="{delay:.2f}s" dur="2.6s" repeatCount="indefinite"/>
    </line>
    <circle cx="{x:.1f}" cy="{y_a:.1f}" r="5" fill="{color}"
            stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.5"/>
    <circle cx="{x:.1f}" cy="{y_b:.1f}" r="5" fill="{color}"
            stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.5"/>
  </g>""")
        # Language label above or below rung depending on which strand is on top.
        label_y = y_b + 26 if y_b > y_a else y_a + 26
        labels.append(
            f'<text x="{x:.1f}" y="{label_y:.1f}" class="dna-label" '
            f'text-anchor="middle">{_x(languages[i])}</text>'
        )

    title_svg = ""
    if title:
        title_svg = (
            f'<text x="{WIDTH / 2}" y="40" class="dna-title" '
            f'text-anchor="middle">{_x(title)}</text>'
        )

    # Slow horizontal drift — fakes 3D rotation by sliding the helix sideways.
    drift = (
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0;-30 0;0 0" dur="14s" repeatCount="indefinite"/>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"
     viewBox="0 0 {WIDTH} {h}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="Code DNA helix">
  <defs>
    <linearGradient id="dna-strand-a" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7B5EAA"/>
      <stop offset="50%" stop-color="#FF6B9D"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <linearGradient id="dna-strand-b" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22D3EE"/>
      <stop offset="50%" stop-color="#FFD23F"/>
      <stop offset="100%" stop-color="#7B5EAA"/>
    </linearGradient>
    <filter id="dna-glow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1.6"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.5"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .dna-title {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; }}
    .dna-label {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 600; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.85; letter-spacing: 0.04em; }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  {title_svg}
  <g>
    {drift}
    <path d="{strand_a}" fill="none" stroke="url(#dna-strand-a)"
          stroke-width="3.5" stroke-opacity="0.9" filter="url(#dna-glow)"/>
    <path d="{strand_b}" fill="none" stroke="url(#dna-strand-b)"
          stroke-width="3.5" stroke-opacity="0.9" filter="url(#dna-glow)"/>
    {"".join(rungs)}
  </g>
  {chr(10).join(labels)}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
