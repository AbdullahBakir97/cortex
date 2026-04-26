"""Skill Radar / Polar Chart — translucent polygon over polar grid.

Shows skill levels on N axes (one per skill) with a filled translucent
polygon revealing relative strengths. Optional breathing animation pulses
the polygon scale subtly.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, RadarConfig
from ..themes import REDUCED_MOTION_CSS, resolve_theme


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200
DEFAULT_COLOR = "#7B5EAA"


def _polar_to_xy(cx: float, cy: float, r: float, angle_rad: float) -> tuple[float, float]:
    return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)


def _grid_polygon(cx: float, cy: float, n_axes: int, radius: float) -> str:
    """Closed polygon path connecting N equally-spaced points at given radius."""
    pts = []
    for i in range(n_axes):
        angle = -math.pi / 2 + i * (2 * math.pi / n_axes)
        x, y = _polar_to_xy(cx, cy, radius, angle)
        pts.append(f"{x:.1f},{y:.1f}")
    return "M " + " L ".join(pts) + " Z"


def _render(config: Config) -> str:
    rcfg: RadarConfig = config.cards.radar
    height = rcfg.height
    cx, cy = WIDTH / 2, height / 2 + 10
    max_r = min(WIDTH * 0.18, (height - 80) / 2)
    color = rcfg.color or resolve_theme(config)["primary"]
    title = rcfg.title or "Skill radar"

    axes = rcfg.axes
    if not axes:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
            'role="img" aria-label="Skill radar (empty)"></svg>\n'
        )

    n = len(axes)
    # Concentric grid rings (4 rings).
    rings = "\n  ".join(
        f'<path d="{_grid_polygon(cx, cy, n, max_r * t)}" '
        f'fill="none" stroke="#FFFFFF" stroke-opacity="{0.05 + t * 0.08:.2f}" '
        f'stroke-width="1"/>'
        for t in (0.25, 0.5, 0.75, 1.0)
    )

    # Axis spokes — radial lines from center to each outer vertex.
    spokes = []
    label_texts = []
    for i, axis in enumerate(axes):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        ex, ey = _polar_to_xy(cx, cy, max_r, angle)
        spokes.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            'stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'
        )
        # Label outside the outer ring.
        lx, ly = _polar_to_xy(cx, cy, max_r + 28, angle)
        # Anchor by quadrant for nice positioning.
        anchor = "middle"
        if math.cos(angle) > 0.3:
            anchor = "start"
        elif math.cos(angle) < -0.3:
            anchor = "end"
        label_texts.append(
            f'<text x="{lx:.1f}" y="{ly + 4:.1f}" class="r-label" '
            f'text-anchor="{anchor}">{_x(axis.label)}</text>'
        )

    # Data polygon — radius per axis = (value / max) * max_r.
    data_pts = []
    for i, axis in enumerate(axes):
        ratio = max(0.0, min(1.0, axis.value / max(1.0, rcfg.max_value)))
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        px, py = _polar_to_xy(cx, cy, max_r * ratio, angle)
        data_pts.append((px, py))
    data_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in data_pts) + " Z"

    # Vertex dots on the data polygon.
    vertex_dots = "\n  ".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" '
        f'stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.5"/>'
        for x, y in data_pts
    )

    breathe_anim = ""
    if rcfg.breathe:
        breathe_anim = (
            '<animateTransform attributeName="transform" type="scale" '
            'values="1;1.04;1" dur="3.5s" repeatCount="indefinite" additive="sum"/>'
        )

    title_svg = (
        f'<text x="{WIDTH / 2}" y="40" class="r-title" text-anchor="middle">{_x(title)}</text>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="{_x(title)}">
  <defs>
    <linearGradient id="r-fill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.18"/>
    </linearGradient>
    <filter id="r-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.6"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .r-title  {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; }}
    .r-label  {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 600; font-size: 14px; fill: #FFFFFF; fill-opacity: 0.86; }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  {title_svg}
  <g transform="translate(0,0)">
    {rings}
    {chr(10).join(spokes)}
    <g transform="translate({cx:.1f},{cy:.1f})">
      <g transform="translate({-cx:.1f},{-cy:.1f})">
        {breathe_anim}
        <path d="{data_d}" fill="url(#r-fill)" stroke="{color}"
              stroke-width="2.5" stroke-opacity="0.95" filter="url(#r-glow)"/>
        {vertex_dots}
      </g>
    </g>
    {chr(10).join(label_texts)}
  </g>
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
