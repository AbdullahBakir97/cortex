"""Synthwave Horizon hero banner — 80s retro-futurist landscape.

Receding perspective grid floor, slatted sun, mountain silhouette, neon
gradient atmosphere. Drop-in replacement for the capsule-render banner
with a much stronger visual signature.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, SynthwaveConfig
from ..themes import REDUCED_MOTION_CSS


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# Each palette is a top→bottom atmospheric sweep of 5 stops.
PALETTES: dict[str, list[str]] = {
    "outrun": ["#0E0820", "#3A1A28", "#7B5EAA", "#FF6B9D", "#FFD23F"],
    "sunset": ["#1A0633", "#5C2E45", "#FF6B9D", "#FFA940", "#FFD23F"],
    "neon": ["#000000", "#0E0820", "#7C3AED", "#22D3EE", "#34D399"],
    "miami": ["#0E0820", "#7B5EAA", "#FF6B9D", "#FF9D6B", "#22D3EE"],
}

WIDTH = 1200


def _atmosphere_stops(palette: list[str]) -> str:
    n = len(palette)
    return "".join(
        f'<stop offset="{i / (n - 1) * 100:.0f}%" stop-color="{c}"/>' for i, c in enumerate(palette)
    )


def _grid_lines(horizon_y: int, height: int) -> str:
    """Receding perspective grid — vanishing point at horizon, lines fan toward viewer."""
    cx = WIDTH / 2
    bottom = height
    floor_h = bottom - horizon_y
    # Vertical fan-out lines (perspective).
    verticals = []
    for i in range(-12, 13):
        # Bottom x spreads further from center than horizon x.
        bx = cx + i * 80
        hx = cx + i * 6  # tighter at horizon
        verticals.append(
            f'<line x1="{hx:.1f}" y1="{horizon_y}" x2="{bx:.1f}" y2="{bottom}" '
            'stroke="#FF6B9D" stroke-opacity="0.55" stroke-width="1"/>'
        )
    # Horizontal grid bands — non-uniform spacing for receding feel (closer = wider gap).
    horizontals = []
    for i, t in enumerate([0.0, 0.05, 0.12, 0.22, 0.36, 0.55, 0.78, 1.0]):
        y = horizon_y + t * floor_h
        # Slow drift downward to fake forward motion.
        anim = (
            f'<animate attributeName="y1" from="{y:.1f}" to="{y + 14:.1f}" '
            f'dur="{2.4 - i * 0.18:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" from="{y:.1f}" to="{y + 14:.1f}" '
            f'dur="{2.4 - i * 0.18:.1f}s" repeatCount="indefinite"/>'
        )
        horizontals.append(
            f'<line x1="0" y1="{y:.1f}" x2="{WIDTH}" y2="{y:.1f}" '
            f'stroke="#22D3EE" stroke-opacity="{0.7 - i * 0.06:.2f}" stroke-width="1.2">'
            f"{anim}</line>"
        )
    return "\n  ".join(verticals + horizontals)


def _sun_with_slits(cx: float, cy: float, r: float) -> str:
    """The iconic synthwave sun: gradient circle with 5 horizontal slits cut out."""
    slits = []
    for i, t in enumerate([0.62, 0.72, 0.81, 0.89, 0.95]):
        sy = cy - r + t * 2 * r
        sh = max(2, int(4 - i * 0.6))
        slits.append(
            f'<rect x="{cx - r:.1f}" y="{sy:.1f}" width="{2 * r:.1f}" '
            f'height="{sh}" fill="#0E0820"/>'
        )
    return f"""
  <defs>
    <radialGradient id="sw-sun" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFE066"/>
      <stop offset="55%" stop-color="#FF6B9D"/>
      <stop offset="100%" stop-color="#7C3AED"/>
    </radialGradient>
  </defs>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#sw-sun)" filter="url(#sw-sunglow)"/>
  {"".join(slits)}
"""


def _mountains(horizon_y: int) -> str:
    """Three layers of jagged silhouette mountains — back darker, front brighter."""
    layers = []
    for li, (peak_h, color, opacity) in enumerate(
        [(70, "#1A0633", 0.95), (55, "#3A1A28", 0.85), (38, "#5C2E45", 0.75)]
    ):
        # Build a jagged path per layer.
        d = f"M 0,{horizon_y}"
        x = 0.0
        offset = li * 60  # stagger the peaks per layer
        # Deterministic but varying peak heights.
        widths = [120, 80, 140, 90, 110, 75, 130, 95, 115, 85, 125, 105, 90]
        for w in widths:
            x += w
            peak_y = horizon_y - peak_h * (0.55 + 0.45 * ((x + offset) % 100) / 100)
            d += f" L {x:.0f},{peak_y:.1f}"
            d += f" L {x + w / 2:.0f},{horizon_y - peak_h * 0.3:.1f}"
        d += f" L {WIDTH},{horizon_y} L 0,{horizon_y} Z"
        layers.append(f'<path d="{d}" fill="{color}" fill-opacity="{opacity}"/>')
    return "\n  ".join(layers)


def _render(config: Config) -> str:
    swc: SynthwaveConfig = config.cards.synthwave
    palette = PALETTES.get(swc.palette, PALETTES["outrun"])
    height = swc.height
    horizon_y = int(height * 0.55)

    sun_svg = ""
    if swc.show_sun:
        sun_svg = _sun_with_slits(cx=WIDTH / 2, cy=horizon_y - 30, r=130)

    mountains_svg = ""
    if swc.show_mountains:
        mountains_svg = _mountains(horizon_y=horizon_y)

    grid_svg = ""
    if swc.show_grid:
        grid_svg = _grid_lines(horizon_y=horizon_y, height=height)

    title_svg = ""
    if swc.title:
        title_svg = (
            f'<text x="{WIDTH / 2}" y="{horizon_y - 80}" '
            f'class="sw-title" text-anchor="middle">{_x(swc.title)}</text>'
        )
    subtitle_svg = ""
    if swc.subtitle:
        subtitle_svg = (
            f'<text x="{WIDTH / 2}" y="{horizon_y - 40}" '
            f'class="sw-subtitle" text-anchor="middle">{_x(swc.subtitle)}</text>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="none"
     role="img" aria-label="Synthwave horizon banner">
  <defs>
    <linearGradient id="sw-sky" x1="0" y1="0" x2="0" y2="1">
      {_atmosphere_stops(palette)}
    </linearGradient>
    <linearGradient id="sw-floor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0E0820"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
    <filter id="sw-sunglow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
    <clipPath id="sw-floor-clip">
      <rect x="0" y="{horizon_y}" width="{WIDTH}" height="{height - horizon_y}"/>
    </clipPath>
  </defs>
  <style><![CDATA[
    .sw-title    {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 76px; letter-spacing: 0.04em; text-transform: uppercase; fill: #FFFFFF; filter: drop-shadow(0 2px 14px rgba(255,107,157,0.7)); }}
    .sw-subtitle {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 500; font-size: 18px; letter-spacing: 0.32em; text-transform: uppercase; fill: #FFFFFF; fill-opacity: 0.85; }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  <rect x="0" y="0" width="{WIDTH}" height="{horizon_y}" fill="url(#sw-sky)"/>
  <rect x="0" y="{horizon_y}" width="{WIDTH}" height="{height - horizon_y}" fill="url(#sw-floor)"/>
  {sun_svg}
  {mountains_svg}
  <g clip-path="url(#sw-floor-clip)">
    {grid_svg}
  </g>
  {title_svg}
  {subtitle_svg}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
