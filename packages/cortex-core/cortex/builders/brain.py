"""Anatomical neon brain builder.

Pipeline:
  1. Read the cached Wikimedia ``Human-brain.SVG`` (Hugh Guiney, CC-BY-SA-3.0)
     from ``cortex/assets/brain-source.svg``.
  2. Extract the ``<g id="brain">`` element via bracket-balanced parsing.
  3. Recolor every fill/stroke to the configured neon palette.
  4. Embed inside a hand-crafted wrapper SVG with title, leader lines, labels,
     and animations driven by the user's ``cortex.yml``.
  5. Write to the provided output path.

Ported from the prototype at:
  https://github.com/AbdullahBakir97/AbdullahBakir97/blob/main/scripts/build_anatomical_brain.py
"""

from __future__ import annotations

import re
from importlib import resources
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from cortex.palettes import resolve_palette
from cortex.schema import BrainRegion, Config


def _x(text: str) -> str:
    """XML-escape user-provided text before injection into the SVG template."""
    return xml_escape(text, {"'": "&apos;", '"': "&quot;"})


# ── Color replacement maps (Wikimedia source uses these specific hexes) ──
_FILL_REPLACEMENTS: dict[str, str] = {
    "#fff0cd": "url(#brainGrad)",
    "#fdd99b": "url(#brainGrad)",
    "#d9bb7a": "url(#brainGradAlt)",
    "#ffffff": "url(#brainGrad)",
    "#816647": "url(#brainGradAlt)",
}


def _stroke_replacements(palette_primary: str, palette_secondary: str) -> dict[str, str]:
    return {
        "#816647": palette_primary,  # main brown outline → palette primary
        "#000000": palette_secondary,  # any black outlines → palette secondary
    }


# ── Brain group extraction (bracket-balanced) ────────────────────────────
def _extract_brain_group(svg: str) -> str:
    """Pull the entire ``<g id="brain">…</g>`` block via balanced-tag walk."""
    m = re.search(r'<g\b[^>]*?id="brain"[^>]*?>', svg, re.DOTALL)
    if not m:
        raise RuntimeError('Could not find <g id="brain"> in source SVG')
    start = m.start()
    pos = m.end()
    depth = 1
    while depth > 0 and pos < len(svg):
        next_open = svg.find("<g", pos)
        next_close = svg.find("</g>", pos)
        if next_close == -1:
            raise RuntimeError("Unbalanced <g> tags in source SVG")
        if next_open != -1 and next_open < next_close:
            after = svg[next_open + 2 : next_open + 3]
            if after in (" ", ">", "\n", "\t", "\r"):
                depth += 1
            pos = next_open + 2
        else:
            depth -= 1
            pos = next_close + 4
    return svg[start:pos]


def _recolor(content: str, palette_primary: str, palette_secondary: str) -> str:
    """Apply both fill and stroke replacements to a brain SVG fragment."""
    for old, new in _FILL_REPLACEMENTS.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"fill:{variant}", f"fill:{new}")
    strokes = _stroke_replacements(palette_primary, palette_secondary)
    for old, new in strokes.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"stroke:{variant}", f"stroke:{new}")
    return content


# ── Region label data (positions on the wrapper canvas) ──────────────────
_REGION_POSITIONS = {
    "frontal": {"label_xy": (1180, 150), "target_xy": (850, 310), "color": "primary"},
    "parietal": {"label_xy": (600, 90), "target_xy": (700, 260), "color": "accent_d"},
    "occipital": {"label_xy": (20, 150), "target_xy": (480, 300), "color": "secondary"},
    "temporal": {"label_xy": (1180, 470), "target_xy": (830, 500), "color": "accent_c"},
    "cerebellum": {"label_xy": (20, 690), "target_xy": (470, 600), "color": "accent_a"},
    "brainstem": {"label_xy": (1180, 690), "target_xy": (760, 620), "color": "accent_b"},
}

_REGION_CAPTIONS = {
    "frontal": "FRONTAL · LOBE",
    "parietal": "PARIETAL · LOBE",
    "occipital": "OCCIPITAL · LOBE",
    "temporal": "TEMPORAL · LOBE",
    "cerebellum": "CEREBELLUM",
    "brainstem": "BRAINSTEM",
}


def _emoji_for_region(region: str) -> str:
    return {
        "frontal": "⚙️",
        "parietal": "🏗️",
        "occipital": "🎨",
        "temporal": "💾",
        "cerebellum": "🛠️",
        "brainstem": "🤖",
    }.get(region, "🧠")


# ── Wrapper SVG composition ──────────────────────────────────────────────
def _compose_wrapper(brain_content: str, config: Config) -> str:
    """Wrap recolored brain content in the full Cortex composition."""
    palette = (
        resolve_palette(config.brand.palette)
        if config.brand.palette in {"neon-rainbow", "monochrome", "cyberpunk", "minimal", "retro"}
        else None
    )
    if palette is None:
        palette = config.brand.colors.model_dump()  # explicit colors override

    p_primary = palette["primary"]
    p_secondary = palette["secondary"]
    p_accent_a = palette["accent_a"]
    p_accent_b = palette["accent_b"]
    p_background = palette["background"]

    name = _x(config.identity.name)

    # Region labels (anatomical → user's domain mapping)
    region_blocks: list[str] = []
    region_lines: list[str] = []
    spark_dots: list[str] = []
    for i, (key, region_data) in enumerate(_REGION_POSITIONS.items()):
        region_obj: BrainRegion = getattr(config.brain.regions, key)
        color_token = region_data["color"]
        color = palette[color_token]  # type: ignore[index]
        lx, ly = region_data["label_xy"]
        tx, ty = region_data["target_xy"]
        emoji = _emoji_for_region(key)
        cap = _REGION_CAPTIONS[key]
        domain = _x(region_obj.domain)
        tools_preview = _x(" · ".join(region_obj.tools[:3])) if region_obj.tools else ""

        region_blocks.append(
            f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
            f'<rect x="0" y="0" width="200" height="80" rx="10" fill="url(#cardBg)" '
            f'stroke="{color}" stroke-width="1.5" filter="url(#cardShadow)"/>'
            f'<rect x="0" y="0" width="5" height="80" rx="2" fill="{color}"/>'
            f'<text x="100" y="20" class="t-cat-cap" text-anchor="middle" fill="{color}">{cap}</text>'
            f'<text x="100" y="44" class="t-region" text-anchor="middle">{emoji} {domain}</text>'
            f'<text x="100" y="64" class="t-skill" text-anchor="middle">{tools_preview}</text>'
            f"</g></g>"
        )

        # Leader line from label edge to brain target
        # Pick a midpoint between label and target for a soft curve
        mid_x = (lx + tx) // 2
        mid_y = (ly + 80 + ty) // 2 if ly < 400 else (ly + ty) // 2
        # Determine which side of label to anchor (right-side labels start at lx,
        # left-side labels start at lx+200)
        anchor_x = lx if lx > 600 else lx + 200
        anchor_y = ly + 40
        region_lines.append(
            f'<path d="M {anchor_x},{anchor_y} Q {mid_x},{mid_y} {tx},{ty}" '
            f'stroke="{color}" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.7" class="leader-flow"/>'
        )

        spark_dots.append(
            f'<circle cx="{tx}" cy="{ty}" r="4" fill="{color}" class="target-pulse" '
            f'style="animation-delay:{i * 0.3}s"/>'
        )

    # Compose the SVG
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  Neural Skill Atlas — anatomical neon brain
    • Brain anatomy by Hugh Guiney, CC-BY-SA-3.0
      (https://commons.wikimedia.org/wiki/File:Human-brain.SVG)
    • Recolored + composed by Cortex (https://github.com/AbdullahBakir97/cortex)
    • Generated for: {name}
-->
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900"
     viewBox="0 0 1400 900" role="img"
     aria-label="Cortex Neural Skill Atlas — {name}">
  <defs>
    <linearGradient id="brainGrad" x1="0" y1="0.05" x2="1" y2="0.95"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="22s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="{p_accent_a}"/>
      <stop offset="22%"  stop-color="{p_accent_b}"/>
      <stop offset="50%"  stop-color="#EC4899"/>
      <stop offset="76%"  stop-color="{p_secondary}"/>
      <stop offset="100%" stop-color="{p_primary}"/>
    </linearGradient>
    <linearGradient id="brainGradAlt" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <stop offset="0%"   stop-color="{p_accent_b}"/>
      <stop offset="50%"  stop-color="#EC4899"/>
      <stop offset="100%" stop-color="{p_secondary}"/>
    </linearGradient>
    <radialGradient id="bgRadial" cx="50%" cy="50%" r="80%">
      <stop offset="0%"   stop-color="#180826"/>
      <stop offset="60%"  stop-color="#080410"/>
      <stop offset="100%" stop-color="{p_background}"/>
    </radialGradient>
    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#1C1428" stop-opacity="0.94"/>
      <stop offset="100%" stop-color="#0A0612" stop-opacity="0.94"/>
    </linearGradient>
    <filter id="cardShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="5"/>
      <feOffset dx="0" dy="3" result="shadow"/>
      <feFlood flood-color="#000000" flood-opacity="0.7"/>
      <feComposite in2="shadow" operator="in"/>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="brainGlow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style><![CDATA[
      .t-display   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 30px; fill: #FFFFFF; }}
      .t-tag       {{ font-family: 'Inter', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 0.30em; text-transform: uppercase; fill: {p_accent_b}; }}
      .t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 600; font-size: 9px; letter-spacing: 0.22em; text-transform: uppercase; }}
      .t-region    {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 14px; fill: #FFFFFF; }}
      .t-skill     {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 10.5px; fill: #D1D5DB; }}
      .brain-pulse {{ animation: brainPulse 5s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes brainPulse {{
        0%, 100% {{ filter: drop-shadow(0 0 16px rgba(236,72,153,0.45)); }}
        50%      {{ filter: drop-shadow(0 0 32px rgba(236,72,153,0.85)); }}
      }}
      .brain-3d {{ animation: brain3d 16s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes brain3d {{
        0%, 100% {{ transform: scaleX(1)    skewY(0deg); }}
        25%      {{ transform: scaleX(0.92) skewY(-1.5deg); }}
        50%      {{ transform: scaleX(0.82) skewY(0deg); }}
        75%      {{ transform: scaleX(0.92) skewY(1.5deg); }}
      }}
      .leader-flow  {{ stroke-dasharray: 4 6; animation: lflow 1.6s linear infinite; }}
      @keyframes lflow {{ to {{ stroke-dashoffset: -20; }} }}
      .target-pulse {{ animation: tpulse 1.6s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes tpulse {{ 0%,100%{{transform:scale(1);opacity:0.85}} 50%{{transform:scale(1.5);opacity:1}} }}
      .label-fade {{ opacity: 0; animation: lfade 0.8s cubic-bezier(0.22,1,0.36,1) forwards; }}
      @keyframes lfade {{ to {{ opacity: 1; }} }}
      .lf1{{animation-delay:0.4s}} .lf2{{animation-delay:0.55s}} .lf3{{animation-delay:0.7s}}
      .lf4{{animation-delay:0.85s}} .lf5{{animation-delay:1.0s}} .lf6{{animation-delay:1.15s}}
    ]]></style>
  </defs>

  <rect width="1400" height="900" fill="url(#bgRadial)"/>

  <!-- Title -->
  <text x="700" y="50" class="t-tag" text-anchor="middle">⏵ NEURAL · SKILL · ATLAS · v1.0 ⏴</text>
  <text x="700" y="86" class="t-display" text-anchor="middle">{name}'s Skill Brain</text>

  <!-- Leader lines (drawn behind brain) -->
  <g fill="none">
    {chr(10).join("    " + ln for ln in region_lines)}
  </g>

  <!-- Synaptic spark dots at leader endpoints -->
  <g>
    {chr(10).join("    " + sd for sd in spark_dots)}
  </g>

  <!-- The neon brain (Wikimedia anatomical, recolored, centered, 3D wobble) -->
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="brain-3d">
        {brain_content}
      </g>
    </g>
  </g>

  <!-- Region labels -->
  {chr(10).join("  " + b for b in region_blocks)}
</svg>
"""


# ── Public API ───────────────────────────────────────────────────────────
def build(config: Config, output: str | Path) -> Path:
    """Build the anatomical neon brain SVG and write it to ``output``."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load the cached source SVG from package data
    src_text = (
        resources.files("cortex.assets").joinpath("brain-source.svg").read_text(encoding="utf-8")
    )

    # Pull just the brain group
    brain_group = _extract_brain_group(src_text)

    # Recolor with the user's palette
    palette = (
        resolve_palette(config.brand.palette)
        if config.brand.palette in {"neon-rainbow", "monochrome", "cyberpunk", "minimal", "retro"}
        else config.brand.colors.model_dump()
    )
    recolored = _recolor(brain_group, palette["primary"], palette["secondary"])

    # Compose into the wrapper
    svg = _compose_wrapper(recolored, config)
    output_path.write_text(svg, encoding="utf-8")

    return output_path
