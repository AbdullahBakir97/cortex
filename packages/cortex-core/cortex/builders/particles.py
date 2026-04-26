"""Particle Tag Cloud — drifting labelled particles around a center.

Items are placed deterministically in a ring around the canvas center, then
each one drifts on its own elliptical orbit. Item weight controls font size
and ring radius (higher weight = closer to center, more prominent).
"""

from __future__ import annotations

import math
import random as _random
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, ParticlesConfig
from ..themes import REDUCED_MOTION_CSS


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

_DEFAULT_PALETTE = [
    "#FFFFFF",
    "#FFD23F",
    "#FF6B9D",
    "#22D3EE",
    "#34D399",
    "#7C3AED",
    "#FF9D6B",
]


def _seed_from_name(name: str) -> int:
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h


def _render(config: Config) -> str:
    pcfg: ParticlesConfig = config.cards.particles
    h = pcfg.height
    title = pcfg.title or ""
    items = pcfg.items

    if not items:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {h}" '
            'role="img" aria-label="Particle cloud (empty)"></svg>\n'
        )

    cx = WIDTH / 2
    cy = h / 2 + 20

    seed = _seed_from_name(config.identity.name or "default") + len(items)
    rng = _random.Random(seed)

    n = len(items)
    # Sort by weight descending so highest-weight items get inner orbits.
    indexed = sorted(enumerate(items), key=lambda p: -p[1].weight)

    parts: list[str] = []
    for rank, (orig_idx, item) in enumerate(indexed):
        # Inner items closer to center, outer items further out.
        ring = rank / max(1, n - 1)  # 0..1
        base_radius = 80 + ring * (min(WIDTH, h) * 0.32)
        # Spread items evenly around the ring with a per-item jitter.
        angle_base = (orig_idx / n) * 2 * math.pi + rng.uniform(-0.4, 0.4)
        # Per-particle elliptical orbit deltas.
        orbit_rx = 18 + rng.uniform(0, 18)
        orbit_ry = 14 + rng.uniform(0, 12)
        orbit_dur = 14 + rng.uniform(0, 8)

        # Center position (where the particle lives on average).
        x0 = cx + base_radius * math.cos(angle_base)
        y0 = cy + base_radius * math.sin(angle_base)

        color = item.color or _DEFAULT_PALETTE[orig_idx % len(_DEFAULT_PALETTE)]

        # Font size scales with weight (clamped).
        weight = max(0.5, min(3.0, item.weight))
        font_size = 12 + weight * 6

        # Generate the orbit values list for animateMotion path.
        # Use a small ellipse path centered at (x0, y0): "M x0,y0 m -rx,0 a rx,ry 0 1,0 2*rx,0 a rx,ry 0 1,0 -2*rx,0"
        orbit_path_d = (
            f"M {x0:.1f},{y0:.1f} "
            f"m {-orbit_rx:.1f},0 "
            f"a {orbit_rx:.1f},{orbit_ry:.1f} 0 1,0 {2 * orbit_rx:.1f},0 "
            f"a {orbit_rx:.1f},{orbit_ry:.1f} 0 1,0 {-2 * orbit_rx:.1f},0"
        )

        # Each particle: orbiting group with a faint halo + the label text.
        parts.append(f"""
  <g>
    <text class="pc-label" text-anchor="middle" fill="{color}"
          style="font-size: {font_size:.1f}px;" filter="url(#pc-glow)">
      {_x(item.label)}
      <animateMotion dur="{orbit_dur:.1f}s" repeatCount="indefinite" rotate="auto-reverse">
        <mpath xlink:href="#pc-orbit-{orig_idx}"/>
      </animateMotion>
    </text>
    <path id="pc-orbit-{orig_idx}" d="{orbit_path_d}" fill="none" stroke="none"/>
  </g>""")

    title_svg = ""
    if title:
        title_svg = (
            f'<text x="{cx:.1f}" y="40" class="pc-title" text-anchor="middle">{_x(title)}</text>'
        )

    # Center "core" — a glowing nucleus that the particles orbit around.
    core = f"""
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="36" fill="url(#pc-core)" filter="url(#pc-glow)"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="#FFFFFF" opacity="0.95">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="2.6s" repeatCount="indefinite"/>
  </circle>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" height="{h}"
     viewBox="0 0 {WIDTH} {h}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="{_x(title) if title else "Particle cloud"}">
  <defs>
    <radialGradient id="pc-core" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="40%" stop-color="#FF6B9D" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#7B5EAA" stop-opacity="0"/>
    </radialGradient>
    <filter id="pc-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.4"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .pc-title {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; }}
    .pc-label {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 700; letter-spacing: 0.04em; }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  {title_svg}
  {core}
  {"".join(parts)}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
