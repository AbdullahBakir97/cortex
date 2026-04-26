"""Skill Globe — stylized 2D globe with neon contribution pins.

Renders a circle representing Earth with latitude/longitude grid lines and
named glowing pins at user-supplied (lon, lat) coordinates. Optional gentle
rotation animates the grid lines drifting around the sphere for a 3D feel
without needing actual 3D math.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, GlobeConfig, GlobePin


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

_PIN_PALETTE = [
    "#FFD23F",
    "#FF6B9D",
    "#22D3EE",
    "#34D399",
    "#7C3AED",
    "#F90001",
    "#FF9D6B",
]


def _project(lon: float, lat: float, cx: float, cy: float, r: float) -> tuple[float, float, bool]:
    """Project (lon, lat) onto the visible hemisphere of a 2D circle.

    Returns (x, y, visible). visible = false when the point is on the back
    half (lon outside (-90, 90)) so the caller can hide it.
    """
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = cx + r * math.cos(lat_rad) * math.sin(lon_rad)
    y = cy - r * math.sin(lat_rad)
    visible = -90 < lon < 90
    return x, y, visible


def _meridians(cx: float, cy: float, r: float, n: int = 9) -> str:
    """Vertical curves representing meridians of constant longitude."""
    paths = []
    for i in range(1, n):
        # Longitude offset from prime meridian. Skip 0 and 180 (handled).
        lon_pct = (i / n) * 2 - 1  # -1..1
        # Foreshortening: meridians look like ellipses with reduced x-radius.
        ellipse_rx = abs(lon_pct) * r
        # Skip when foreshortening makes the ellipse collapse.
        if ellipse_rx < 5:
            continue
        # An ellipse path covering the full visible meridian.
        paths.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{ellipse_rx:.1f}" ry="{r:.1f}" '
            f'fill="none" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'
        )
    return "\n  ".join(paths)


def _parallels(cx: float, cy: float, r: float, n: int = 7) -> str:
    """Horizontal lines representing latitude parallels."""
    paths = []
    for i in range(1, n):
        # Latitudes at -60..60 in equal steps.
        lat = -60 + (i - 1) * 120 / (n - 2)
        lat_rad = math.radians(lat)
        y = cy - r * math.sin(lat_rad)
        # Width of parallel at this latitude.
        circle_r = r * math.cos(lat_rad)
        paths.append(
            f'<line x1="{cx - circle_r:.1f}" y1="{y:.1f}" '
            f'x2="{cx + circle_r:.1f}" y2="{y:.1f}" '
            f'stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'
        )
    return "\n  ".join(paths)


def _render(config: Config) -> str:
    gcfg: GlobeConfig = config.cards.globe
    h = gcfg.height
    title = gcfg.title or ""

    cx = WIDTH / 2
    cy = h / 2 + 20
    r = (h - 80) / 2

    pins_svg = []
    for i, pin in enumerate(gcfg.pins):
        x, y, visible = _project(pin.lon, pin.lat, cx, cy, r)
        if not visible:
            # Pin on back side — show as faint marker on globe rim.
            continue
        color = pin.color or _PIN_PALETTE[i % len(_PIN_PALETTE)]
        delay = (i * 0.32) % 3
        # Pulsing pin: outer ring expands and fades, inner dot static.
        pins_svg.append(f"""
  <g transform="translate({x:.1f},{y:.1f})">
    <circle r="14" fill="none" stroke="{color}" stroke-width="2" stroke-opacity="0.85">
      <animate attributeName="r" values="6;18;6" begin="{delay:.2f}s"
               dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0.85;0;0.85"
               begin="{delay:.2f}s" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle r="5" fill="{color}" stroke="#FFFFFF" stroke-opacity="0.9"
            stroke-width="1.5" filter="url(#gb-glow)"/>
    <text y="-22" class="gb-label" text-anchor="middle">{_x(pin.label)}</text>
  </g>""")

    rotate_anim = ""
    if gcfg.rotate:
        # Rotate the meridian/parallel grid (NOT the pins) for a sense of motion.
        rotate_anim = (
            '<animateTransform attributeName="transform" type="rotate" '
            f'from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" '
            'dur="60s" repeatCount="indefinite"/>'
        )

    title_svg = ""
    if title:
        title_svg = (
            f'<text x="{cx:.1f}" y="40" class="gb-title" text-anchor="middle">{_x(title)}</text>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"
     viewBox="0 0 {WIDTH} {h}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="{_x(title) if title else "Skill globe"}">
  <defs>
    <radialGradient id="gb-sphere" cx="35%" cy="32%" r="62%">
      <stop offset="0%" stop-color="#1A1A48"/>
      <stop offset="50%" stop-color="#0E0820"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>
    <radialGradient id="gb-atmosphere" cx="50%" cy="50%" r="50%">
      <stop offset="85%" stop-color="#22D3EE" stop-opacity="0"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.45"/>
    </radialGradient>
    <filter id="gb-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.6"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .gb-title {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; }}
    .gb-label {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 600; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.92; letter-spacing: 0.06em; }}
  ]]></style>
  {title_svg}
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 10:.1f}" fill="url(#gb-atmosphere)"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#gb-sphere)"
          stroke="#22D3EE" stroke-opacity="0.45" stroke-width="1.5"/>
  <g>
    {rotate_anim}
    {_meridians(cx, cy, r)}
    {_parallels(cx, cy, r)}
  </g>
  {"".join(pins_svg)}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out


__all__ = ["GlobePin", "build"]
