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
    "frontal": {"label_xy": (1060, 200), "target_xy": (850, 320), "color": "primary"},
    "parietal": {"label_xy": (540, 130), "target_xy": (700, 280), "color": "accent_d"},
    "occipital": {"label_xy": (20, 200), "target_xy": (490, 310), "color": "secondary"},
    "temporal": {"label_xy": (1060, 480), "target_xy": (830, 510), "color": "accent_c"},
    "cerebellum": {"label_xy": (20, 660), "target_xy": (480, 610), "color": "accent_a"},
    "brainstem": {"label_xy": (1060, 660), "target_xy": (760, 630), "color": "accent_b"},
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
    atm = config.brain.atmosphere
    brain_3d_class = "brain-3d" if atm.wobble else ""

    # Region labels (anatomical → user's domain mapping)
    region_blocks: list[str] = []
    region_lines: list[str] = []
    spark_dots: list[str] = []  # rendered INSIDE brain-3d so they wobble with the brain
    target_halos: list[str] = []  # rendered in canvas space; static anchor for leader-line endpoints
    for i, (key, region_data) in enumerate(_REGION_POSITIONS.items()):
        region_obj: BrainRegion = getattr(config.brain.regions, key)
        color_token = region_data["color"]
        color = palette[color_token]  # type: ignore[index]
        lx, ly = region_data["label_xy"]
        tx, ty = region_data["target_xy"]
        emoji = _emoji_for_region(key)
        cap = _REGION_CAPTIONS[key]
        domain = _x(region_obj.domain)
        tools_preview = _x(" · ".join(region_obj.tools[:4])) if region_obj.tools else ""

        # Glassmorphism lobe card: base + highlight overlay + top breathing stripe.
        # Matches the visual language of tech-cards.svg (also card-based).
        region_blocks.append(
            f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
            f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardBg)" '
            f'stroke="{color}" stroke-width="1.8" filter="url(#cardShadow)"/>'
            f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardHighlight)"/>'
            f'<rect x="0" y="0" width="320" height="4" rx="2" fill="{color}" class="breathe-stripe"/>'
            f'<text x="160" y="38" class="t-cat-cap" text-anchor="middle" fill="{color}">{cap}</text>'
            f'<text x="160" y="80" class="t-region" text-anchor="middle">{emoji} {domain}</text>'
            f'<text x="160" y="116" class="t-skill" text-anchor="middle">{tools_preview}</text>'
            f"</g></g>"
        )

        # Leader line from label edge to brain target (canvas space)
        mid_x = (lx + tx) // 2
        mid_y = (ly + 140 + ty) // 2 if ly < 400 else (ly + ty) // 2
        anchor_x = lx if lx > 600 else lx + 320
        anchor_y = ly + 70
        region_lines.append(
            f'<path d="M {anchor_x},{anchor_y} Q {mid_x},{mid_y} {tx},{ty}" '
            f'stroke="{color}" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.7" class="leader-flow"/>'
        )

        # Halo ring stays in canvas space — anchors the leader-line endpoint
        # so the line never visually disconnects when the dot wobbles below.
        target_halos.append(
            f'<circle cx="{tx}" cy="{ty}" r="14" fill="none" stroke="{color}" '
            f'stroke-width="1.5" class="target-halo" '
            f'style="animation-delay:{i * 0.3}s"/>'
        )

        # Spark dot lives in brain-local coordinates so it inherits the
        # brain-3d skew/scale wobble. Brain group transform is
        # translate(332,152) scale(0.7), so brain-local = (canvas - 332)/0.7.
        # Dot radius compensates: r=6 here renders as r≈4.2 after the 0.7 scale.
        bx = round((tx - 332) / 0.7)
        by = round((ty - 152) / 0.7)
        spark_dots.append(
            f'<circle cx="{bx}" cy="{by}" r="6" fill="{color}" class="target-pulse" '
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
      <animate attributeName="r" values="72%;88%;72%" dur="9s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#180826"/>
      <stop offset="60%"  stop-color="#080410"/>
      <stop offset="100%" stop-color="{p_background}"/>
    </radialGradient>
    <radialGradient id="bgAura" cx="50%" cy="50%" r="40%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#1C1428" stop-opacity="0.94"/>
      <stop offset="100%" stop-color="#0A0612" stop-opacity="0.94"/>
    </linearGradient>
    <linearGradient id="cardHighlight" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#FFFFFF" stop-opacity="0.08"/>
      <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0"/>
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
      .t-display   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 44px; fill: #FFFFFF; }}
      .t-tag       {{ font-family: 'Inter', sans-serif; font-weight: 600; font-size: 15px; letter-spacing: 0.30em; text-transform: uppercase; fill: {p_accent_b}; }}
      .t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 17px; letter-spacing: 0.20em; text-transform: uppercase; }}
      .t-region    {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 24px; fill: #FFFFFF; }}
      .t-skill     {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 18px; fill: #E5E7EB; }}
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
      .target-halo {{ animation: thalo 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes thalo {{ 0%,100%{{opacity:0.18;transform:scale(0.9)}} 50%{{opacity:0.45;transform:scale(1.25)}} }}
      .label-fade {{ opacity: 0; animation: lfade 0.8s cubic-bezier(0.22,1,0.36,1) forwards; }}
      @keyframes lfade {{ to {{ opacity: 1; }} }}
      .lf1{{animation-delay:0.4s}} .lf2{{animation-delay:0.55s}} .lf3{{animation-delay:0.7s}}
      .lf4{{animation-delay:0.85s}} .lf5{{animation-delay:1.0s}} .lf6{{animation-delay:1.15s}}
      .breathe-stripe {{ animation: stripeBreathe 3s ease-in-out infinite; }}
      @keyframes stripeBreathe {{ 0%,100%{{opacity:0.85}} 50%{{opacity:1}} }}
      .particle {{ animation: pdrift 14s ease-in-out infinite; transform-box: fill-box; }}
      @keyframes pdrift {{
        0%,100% {{ opacity: 0.18; transform: translate(0, 0); }}
        25%      {{ opacity: 0.55; transform: translate(8px, -10px); }}
        50%      {{ opacity: 0.32; transform: translate(-4px, -22px); }}
        75%      {{ opacity: 0.60; transform: translate(-12px, -8px); }}
      }}
      .p1{{animation-delay:0s;animation-duration:14s}} .p2{{animation-delay:1.5s;animation-duration:18s}}
      .p3{{animation-delay:3s;animation-duration:11s}} .p4{{animation-delay:4.5s;animation-duration:15s}}
      .p5{{animation-delay:6s;animation-duration:13s}} .p6{{animation-delay:7.5s;animation-duration:16s}}
      .p7{{animation-delay:2s;animation-duration:12s}} .p8{{animation-delay:3.5s;animation-duration:17s}}
      .p9{{animation-delay:5s;animation-duration:14s}} .p10{{animation-delay:6.5s;animation-duration:11s}}
      .p11{{animation-delay:0.5s;animation-duration:19s}} .p12{{animation-delay:8s;animation-duration:13s}}
      .p13{{animation-delay:1s;animation-duration:15s}} .p14{{animation-delay:2.5s;animation-duration:18s}}
      .p15{{animation-delay:9s;animation-duration:12s}} .p16{{animation-delay:4s;animation-duration:16s}}
    ]]></style>
  </defs>

  <rect width="1400" height="900" fill="url(#bgRadial)"/>
  {('<rect width="1400" height="900" fill="url(#bgAura)"/>') if atm.show_aura else ""}

  {('''<!-- Ambient particle drift — atmospheric depth behind the brain -->
  <g fill="''' + p_accent_b + '''">
    <circle cx="120"  cy="180" r="1.8" class="particle p1"/>
    <circle cx="260"  cy="540" r="1.4" class="particle p2"/>
    <circle cx="380"  cy="120" r="2.0" class="particle p3" fill="''' + p_accent_a + '''"/>
    <circle cx="420"  cy="760" r="1.2" class="particle p4"/>
    <circle cx="560"  cy="380" r="1.6" class="particle p5" fill="''' + p_accent_a + '''"/>
    <circle cx="700"  cy="220" r="2.2" class="particle p6"/>
    <circle cx="780"  cy="700" r="1.4" class="particle p7" fill="''' + p_secondary + '''"/>
    <circle cx="900"  cy="160" r="1.8" class="particle p8"/>
    <circle cx="980"  cy="520" r="1.6" class="particle p9" fill="''' + p_accent_a + '''"/>
    <circle cx="1080" cy="340" r="2.0" class="particle p10"/>
    <circle cx="1180" cy="780" r="1.4" class="particle p11"/>
    <circle cx="1260" cy="240" r="1.8" class="particle p12" fill="''' + p_secondary + '''"/>
    <circle cx="160"  cy="780" r="1.6" class="particle p13"/>
    <circle cx="340"  cy="660" r="1.2" class="particle p14" fill="''' + p_accent_a + '''"/>
    <circle cx="640"  cy="80"  r="1.8" class="particle p15"/>
    <circle cx="1320" cy="500" r="1.4" class="particle p16"/>
  </g>''') if atm.show_particles else ""}

  <!-- Title -->
  <text x="700" y="50" class="t-tag" text-anchor="middle">⏵ NEURAL · SKILL · ATLAS · v1.0 ⏴</text>
  <text x="700" y="86" class="t-display" text-anchor="middle">{name}'s Skill Brain</text>

  <!-- Leader lines (drawn behind brain) -->
  <g fill="none">
    {chr(10).join("    " + ln for ln in region_lines)}
  </g>

  {('''<!-- Static halo rings in canvas space — anchor the leader-line endpoints
       so the connection reads as continuous even when the spark dot below
       drifts with the brain's 3D wobble. -->
  <g>
    ''' + chr(10).join("    " + ha for ha in target_halos) + '''
  </g>''') if atm.show_halos else ""}

  <!-- The neon brain (Wikimedia anatomical, recolored, centered, optionally
       3D-wobbling). Spark dots live INSIDE the wobble group so they inherit
       the animation and stay anchored to actual lobe positions. The wobble
       class is conditional on brain.atmosphere.wobble in the user's config. -->
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        {brain_content}
        {chr(10).join("        " + sd for sd in spark_dots)}
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
