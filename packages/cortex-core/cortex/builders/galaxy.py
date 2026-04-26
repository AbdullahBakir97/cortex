"""Skill Galaxy / Constellation — stars + connection lines drifting in space.

Stars are positioned deterministically from a name-derived seed so the layout
reproduces across runs. Each star twinkles (opacity oscillation) on its own
phase. Connection lines fade between specified star pairs. Background is one
of three space variants: deep-space (gradient), nebula (colorful blob layers),
or void (near-black).
"""

from __future__ import annotations

import math
import random as _random
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, GalaxyConfig, StarSpec
from ..themes import REDUCED_MOTION_CSS


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

# Defaults to layer over when star.color is empty — jewel-tone palette.
_DEFAULT_STAR_COLORS = ["#FFFFFF", "#22D3EE", "#FF6B9D", "#FFD23F", "#34D399", "#7B5EAA"]


def _seed_from_name(name: str) -> int:
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h


def _bg_layers(bg: str, w: int, h: int) -> str:
    """Background fill layers — gradient + (for nebula) colored blobs."""
    if bg == "void":
        return f'<rect x="0" y="0" width="{w}" height="{h}" fill="#000000"/>'

    base_grad = f"""
  <defs>
    <radialGradient id="gx-bg" cx="50%" cy="55%" r="65%">
      <stop offset="0%" stop-color="#1A0A24"/>
      <stop offset="55%" stop-color="#0B0218"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="url(#gx-bg)"/>"""

    if bg == "deep-space":
        return base_grad

    # nebula: add three colored radial blobs that drift slowly.
    nebula_blobs = ""
    for i, (cx_pct, cy_pct, radius, color) in enumerate(
        [(30, 35, 280, "#7B5EAA"), (70, 60, 240, "#FF6B9D"), (50, 30, 200, "#22D3EE")]
    ):
        cx_v = w * cx_pct / 100
        cy_v = h * cy_pct / 100
        nebula_blobs += f"""
  <defs>
    <radialGradient id="gx-blob-{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <circle cx="{cx_v:.0f}" cy="{cy_v:.0f}" r="{radius}" fill="url(#gx-blob-{i})">
    <animate attributeName="cx" values="{cx_v:.0f};{cx_v + 30:.0f};{cx_v:.0f}"
             dur="{12 + i * 3}s" repeatCount="indefinite"/>
  </circle>"""
    return base_grad + nebula_blobs


def _render_stars_and_connections(
    cfg: GalaxyConfig, h: int, seed: int
) -> tuple[str, dict[str, tuple[float, float]]]:
    """Place stars deterministically. Returns (svg_fragment, label_to_xy_map)."""
    rng = _random.Random(seed)
    stars = list(cfg.stars)

    # Place each star at a random non-edge position, deterministic per name.
    positions: dict[str, tuple[float, float]] = {}
    for star in stars:
        x = rng.uniform(WIDTH * 0.08, WIDTH * 0.92)
        y = rng.uniform(h * 0.18, h * 0.82)
        positions[star.label] = (x, y)

    # Sprinkle background "filler" stars (small, dim, not labelled).
    fillers = []
    for _ in range(120):
        fx = rng.uniform(0, WIDTH)
        fy = rng.uniform(0, h)
        fr = rng.uniform(0.6, 1.6)
        fop = rng.uniform(0.25, 0.75)
        fillers.append(
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{fr:.1f}" fill="#FFFFFF" opacity="{fop:.2f}"/>'
        )

    # Connection lines drawn FIRST so stars sit on top.
    conn_lines = []
    for pair in cfg.connections:
        if len(pair) != 2:
            continue
        a, b = pair
        if a not in positions or b not in positions:
            continue
        ax, ay = positions[a]
        bx, by = positions[b]
        conn_lines.append(
            f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
            f'stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="1">'
            f'<animate attributeName="stroke-opacity" values="0.10;0.32;0.10" '
            f'dur="6s" repeatCount="indefinite"/></line>'
        )

    # Named stars — bigger, twinkling, with a label.
    named = []
    for i, star in enumerate(stars):
        x, y = positions[star.label]
        color = star.color or _DEFAULT_STAR_COLORS[i % len(_DEFAULT_STAR_COLORS)]
        size = max(2, min(12, star.size))
        # Twinkle: opacity oscillates with per-star phase offset.
        phase = (i * 0.37) % 4
        twinkle_dur = 2.2 + (i % 5) * 0.4
        # Star body + cross-shaped halo for that "lens flare" feel.
        named.append(f"""
  <g transform="translate({x:.1f},{y:.1f})">
    <circle r="{size + 8}" fill="{color}" opacity="0.18"/>
    <circle r="{size}" fill="{color}">
      <animate attributeName="opacity" values="0.55;1;0.55"
               begin="{phase:.2f}s" dur="{twinkle_dur:.1f}s" repeatCount="indefinite"/>
    </circle>
    <line x1="-{size + 6}" y1="0" x2="{size + 6}" y2="0"
          stroke="{color}" stroke-opacity="0.55" stroke-width="0.8"/>
    <line x1="0" y1="-{size + 6}" x2="0" y2="{size + 6}"
          stroke="{color}" stroke-opacity="0.55" stroke-width="0.8"/>
    <text y="{size + 18}" class="gx-label" text-anchor="middle">{_x(star.label)}</text>
  </g>""")

    return (
        "\n  ".join(fillers) + "\n  " + "\n  ".join(conn_lines) + "\n  " + "\n  ".join(named),
        positions,
    )


def _render(config: Config) -> str:
    gcfg: GalaxyConfig = config.cards.galaxy
    h = gcfg.height
    title = gcfg.title or ""

    if not gcfg.stars:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {h}" '
            'role="img" aria-label="Skill galaxy (empty)"></svg>\n'
        )

    seed = _seed_from_name(config.identity.name or "default") + len(gcfg.stars)
    bg_svg = _bg_layers(gcfg.background, WIDTH, h)
    stars_svg, _positions = _render_stars_and_connections(gcfg, h, seed)

    title_svg = ""
    if title:
        title_svg = (
            f'<text x="{WIDTH / 2}" y="40" class="gx-title" text-anchor="middle">{_x(title)}</text>'
        )

    # Slow drift on the entire star field for parallax feel.
    drift_dur = max(20.0, 40.0 / gcfg.drift_speed)
    drift = (
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;-12 -8;0 0" dur="{drift_dur:.0f}s" repeatCount="indefinite"/>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"
     viewBox="0 0 {WIDTH} {h}" preserveAspectRatio="xMidYMin slice"
     role="img" aria-label="{_x(title) if title else "Skill galaxy"}">
  <style><![CDATA[
    .gx-title {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; }}
    .gx-label {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 500; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.85; letter-spacing: 0.04em; }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  {bg_svg}
  {title_svg}
  <g>
    {drift}
    {stars_svg}
  </g>
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out


# Re-export for use in tests / variants.
__all__ = ["StarSpec", "build"]
# math is referenced for symmetry with other geom-heavy builders even if unused
# in trivial paths — keep import to avoid lint ImportError if added later.
_ = math
