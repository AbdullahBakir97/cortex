"""Tech-stack cards builder — six glassmorphism cards on a 3x2 grid.

Each card maps to one brain region (frontal, occipital, parietal, temporal,
cerebellum, brainstem) — keeping a single source of truth: the user describes
their skill domains once in `brain.regions`, and Cortex renders both the
anatomical brain *and* the matching tech-stack cards from the same data.

Visual metadata (emoji, caption, tagline, mastery, stats) is optional on each
BrainRegion. When not supplied, Cortex falls back to a domain-keyed preset
table so the simple case still looks polished out of the box.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import BrainRegion, Config, StatEntry


# ── XML helper ───────────────────────────────────────────────────────────
def _x(s: str) -> str:
    """XML-escape a user-provided string for safe inlining into SVG."""
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# ── Visual presets ───────────────────────────────────────────────────────
# Keyed by canonical (lowercased, stripped) domain name.
_PRESETS: dict[str, dict[str, str]] = {
    "backend": {
        "emoji": "⚙️",
        "caption": "SERVER · APIS · LOGIC",
        "tagline": "Robust, well-tested server-side systems.",
        "mastery": "EXPERT",
    },
    "frontend": {
        "emoji": "🎨",
        "caption": "CLIENT · UI · INTERACTION",
        "tagline": "Interactive, accessible interfaces.",
        "mastery": "ADVANCED",
    },
    "architecture": {
        "emoji": "🏗️",
        "caption": "SYSTEMS · DESIGN · SCALE",
        "tagline": "Distributed, event-driven systems.",
        "mastery": "PROFICIENT",
    },
    "data layer": {
        "emoji": "💾",
        "caption": "PERSISTENCE · STATE · CACHE",
        "tagline": "Modeling, indexing, performance.",
        "mastery": "EXPERT",
    },
    "data": {
        "emoji": "💾",
        "caption": "PERSISTENCE · STATE · CACHE",
        "tagline": "Modeling, indexing, performance.",
        "mastery": "EXPERT",
    },
    "devops": {
        "emoji": "🛠️",
        "caption": "PLATFORM · CI/CD · DEPLOY",
        "tagline": "Pipelines that don't break on Friday.",
        "mastery": "ADVANCED",
    },
    "ai & data": {
        "emoji": "🤖",
        "caption": "INTELLIGENCE · ANALYTICS",
        "tagline": "LLMs, RAG, agents, notebooks.",
        "mastery": "GROWING",
    },
    "ai": {
        "emoji": "🤖",
        "caption": "INTELLIGENCE · ANALYTICS",
        "tagline": "LLMs, RAG, agents, notebooks.",
        "mastery": "GROWING",
    },
}

# Default stats per mastery — used when the region didn't specify any.
_DEFAULT_STATS: dict[str, list[StatEntry]] = {
    "EXPERT": [
        StatEntry(num="4+", label="YEARS"),
        StatEntry(num="30+", label="PROJECTS"),
        StatEntry(num="EXPERT", label="MASTERY"),
    ],
    "ADVANCED": [
        StatEntry(num="4+", label="YEARS"),
        StatEntry(num="20+", label="PROJECTS"),
        StatEntry(num="ADVANCED", label="MASTERY"),
    ],
    "PROFICIENT": [
        StatEntry(num="3+", label="YEARS"),
        StatEntry(num="10+", label="PROJECTS"),
        StatEntry(num="PROFICIENT", label="MASTERY"),
    ],
    "GROWING": [
        StatEntry(num="2+", label="YEARS"),
        StatEntry(num="5+", label="PROJECTS"),
        StatEntry(num="GROWING", label="MASTERY"),
    ],
}

# Mastery level → bar fill width (out of 336 visible track width).
_MASTERY_BAR: dict[str, int] = {
    "EXPERT": 336,
    "ADVANCED": 305,
    "PROFICIENT": 270,
    "GROWING": 225,
}

# Six card slots: position + accent color + stagger class.
# `inner` references the radial-gradient id for the per-accent inner glow rect.
# `edge` is the per-card stagger class for the traveling edge highlight.
_SLOTS: list[dict] = [
    {"x": 30,  "y": 30,  "accent": "Red",    "hex": "#F90001", "fade": "c1", "bar": "b1", "edge": "ce1", "inner": "innerGlowRed"},
    {"x": 450, "y": 30,  "accent": "Orange", "hex": "#FF652F", "fade": "c2", "bar": "b2", "edge": "ce2", "inner": "innerGlowOrange"},
    {"x": 870, "y": 30,  "accent": "Green",  "hex": "#34D399", "fade": "c3", "bar": "b3", "edge": "ce3", "inner": "innerGlowGreen"},
    {"x": 30,  "y": 440, "accent": "Gold",   "hex": "#FFD23F", "fade": "c4", "bar": "b4", "edge": "ce4", "inner": "innerGlowGold"},
    {"x": 450, "y": 440, "accent": "Cyan",   "hex": "#22D3EE", "fade": "c5", "bar": "b5", "edge": "ce5", "inner": "innerGlowCyan"},
    {"x": 870, "y": 440, "accent": "Purple", "hex": "#A78BFA", "fade": "c6", "bar": "b6", "edge": "ce6", "inner": "innerGlowPurple"},
]

# Brain regions render in this order (matches the reference layout).
_REGION_ORDER: list[str] = [
    "frontal",
    "occipital",
    "parietal",
    "temporal",
    "cerebellum",
    "brainstem",
]


# ── Region → visual metadata resolution ──────────────────────────────────
def _resolve_visual(region: BrainRegion) -> dict[str, str]:
    """Return effective {emoji, caption, tagline, mastery} for a region.

    Order of precedence: explicit field on the region → preset matched by
    canonical domain name → conservative blank/PROFICIENT fallback.
    """
    key = region.domain.strip().lower()
    preset = _PRESETS.get(key, {})
    return {
        "emoji": region.emoji or preset.get("emoji", "🧠"),
        "caption": region.caption or preset.get("caption", region.domain.upper()),
        "tagline": region.tagline or preset.get("tagline", "Tools, patterns, taste."),
        "mastery": region.mastery or preset.get("mastery", "PROFICIENT"),
    }


def _split_tools(tools: list[str]) -> tuple[str, str, str]:
    """Split a flat tools list into 3 visual tiers (primary/secondary/tertiary)."""
    if not tools:
        return ("—", "", "")
    if len(tools) <= 2:
        return (" · ".join(tools), "", "")
    if len(tools) <= 4:
        return (" · ".join(tools[:2]), " · ".join(tools[2:]), "")
    if len(tools) <= 6:
        return (" · ".join(tools[:2]), " · ".join(tools[2:4]), " · ".join(tools[4:]))
    return (" · ".join(tools[:2]), " · ".join(tools[2:5]), " · ".join(tools[5:]))


def _stats_for(region: BrainRegion, mastery: str) -> list[StatEntry]:
    if region.stats:
        return list(region.stats)[:3]
    return _DEFAULT_STATS.get(mastery, _DEFAULT_STATS["PROFICIENT"])


# ── SVG composition ──────────────────────────────────────────────────────
_HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="850" viewBox="0 0 1300 850" role="img" aria-label="__ARIA__">
  <style>
    .t-caption  { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 14px; letter-spacing: 0.20em; text-transform: uppercase; }
    .t-title    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 34px; letter-spacing: -0.01em; fill: #FFFFFF; }
    .t-tagline  { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 500; font-size: 17px; font-style: italic; fill: #9BA1A6; }
    .t-tool     { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 500; font-size: 18px; letter-spacing: 0.01em; fill: #E8E8E8; }
    .t-stat-num    { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 700; font-size: 26px; }
    .t-stat-num-sm { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 700; font-size: 18px; }
    .t-stat-lbl    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; fill: #8B95A1; }

    /* Travelling edge highlight — a colored segment loops around each card
       perimeter every 4s, staggered per card. Same pattern brain region cards
       got in R2-4 — replaces the static "breathe stripe" at the top with a
       continuously-moving glow that gives the card visible energy. */
    .card-edge {
      stroke-dasharray: 80 1480;
      animation: cardEdgeTravel 4s linear infinite;
      filter: url(#cardEdgeGlow);
      opacity: 0.95;
    }
    @keyframes cardEdgeTravel { to { stroke-dashoffset: -1560; } }
    .ce1 { animation-delay: 0s; }
    .ce2 { animation-delay: 0.7s; }
    .ce3 { animation-delay: 1.4s; }
    .ce4 { animation-delay: 2.1s; }
    .ce5 { animation-delay: 2.8s; }
    .ce6 { animation-delay: 3.5s; }

    /* Inner radial glow — soft accent-colored pulse from card center, slow 5s
       ease-in-out, gives the card warmth from within without pulling focus. */
    .card-inner-pulse { animation: cardPulse 5s ease-in-out infinite; }
    @keyframes cardPulse { 0%, 100% { opacity: 0.55; } 50% { opacity: 1.0; } }

    .draw-bar { stroke-dasharray: 200; stroke-dashoffset: 200; animation: drawBar 1.8s cubic-bezier(0.22,1,0.36,1) forwards; }
    @keyframes drawBar { to { stroke-dashoffset: 0; } }

    /* opacity-only fade — never set transform here, it would overwrite the parent's translate() */
    .card-fade { opacity: 0; animation: cardFade 0.7s cubic-bezier(0.22,1,0.36,1) forwards; }
    @keyframes cardFade { to { opacity: 1; } }
    .c1{animation-delay:0.0s}.c2{animation-delay:0.08s}.c3{animation-delay:0.16s}
    .c4{animation-delay:0.24s}.c5{animation-delay:0.32s}.c6{animation-delay:0.40s}
    .b1{animation-delay:0.5s}.b2{animation-delay:0.6s}.b3{animation-delay:0.7s}
    .b4{animation-delay:0.8s}.b5{animation-delay:0.9s}.b6{animation-delay:1.0s}
  </style>
  <defs>
    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1A2028" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="#0D1117" stop-opacity="0.96"/>
    </linearGradient>
    <linearGradient id="cardHighlight" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#FFFFFF" stop-opacity="0.06"/>
      <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="accentRed"    x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#F90001"/><stop offset="100%" stop-color="#FF4D4F"/></linearGradient>
    <linearGradient id="accentOrange" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FF652F"/><stop offset="100%" stop-color="#FFB088"/></linearGradient>
    <linearGradient id="accentGreen"  x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#34D399"/><stop offset="100%" stop-color="#6EE7B7"/></linearGradient>
    <linearGradient id="accentGold"   x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FFD23F"/><stop offset="100%" stop-color="#FFE680"/></linearGradient>
    <linearGradient id="accentCyan"   x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#22D3EE"/><stop offset="100%" stop-color="#67E8F9"/></linearGradient>
    <linearGradient id="accentPurple" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#A78BFA"/><stop offset="100%" stop-color="#C4B5FD"/></linearGradient>
    <linearGradient id="profGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#F90001"/><stop offset="100%" stop-color="#FF652F"/></linearGradient>
    <pattern id="dots" x="0" y="0" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.9" fill="#F90001" fill-opacity="0.08"/>
    </pattern>
    <!-- Stacked drop shadow: 3 layered feDropShadow for real depth perception
         (single shadow reads as flat). Same pattern brain cards got in R2-4. -->
    <filter id="cardShadowStacked" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="2"  stdDeviation="4"  flood-color="#000" flood-opacity="0.30"/>
      <feDropShadow dx="0" dy="6"  stdDeviation="12" flood-color="#000" flood-opacity="0.40"/>
      <feDropShadow dx="0" dy="14" stdDeviation="24" flood-color="#000" flood-opacity="0.30"/>
    </filter>
    <!-- Edge-glow filter — soft halo on the traveling edge segment so the glow
         radiates beyond the stroke. -->
    <filter id="cardEdgeGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="1.2"/>
    </filter>
    <!-- Per-accent inner glow gradients for the soft pulsing fill inside each
         card. Each lobe color radiates from card center at low opacity. -->
    <radialGradient id="innerGlowRed"    cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#F90001" stop-opacity="0.18"/><stop offset="100%" stop-color="#F90001" stop-opacity="0"/></radialGradient>
    <radialGradient id="innerGlowOrange" cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#FF652F" stop-opacity="0.18"/><stop offset="100%" stop-color="#FF652F" stop-opacity="0"/></radialGradient>
    <radialGradient id="innerGlowGreen"  cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#34D399" stop-opacity="0.18"/><stop offset="100%" stop-color="#34D399" stop-opacity="0"/></radialGradient>
    <radialGradient id="innerGlowGold"   cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#FFD23F" stop-opacity="0.18"/><stop offset="100%" stop-color="#FFD23F" stop-opacity="0"/></radialGradient>
    <radialGradient id="innerGlowCyan"   cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#22D3EE" stop-opacity="0.18"/><stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>
    <radialGradient id="innerGlowPurple" cx="50%" cy="50%" r="60%"><stop offset="0%" stop-color="#A78BFA" stop-opacity="0.18"/><stop offset="100%" stop-color="#A78BFA" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="1300" height="850" fill="url(#dots)"/>
"""

_TAIL = "</svg>\n"


def _render_card(slot: dict, region: BrainRegion, *, show_stats: bool) -> str:
    visual = _resolve_visual(region)
    primary, secondary, tertiary = _split_tools(region.tools)
    stats = _stats_for(region, visual["mastery"])
    bar_x_end = 32 + _MASTERY_BAR.get(visual["mastery"], 270)

    title = f"{visual['emoji']} {region.domain}"
    parts: list[str] = []
    parts.append(f'  <g transform="translate({slot["x"]},{slot["y"]})">')
    parts.append(f'    <g class="card-fade {slot["fade"]}">')
    parts.append(
        '      <rect x="0" y="0" width="400" height="380" rx="14" fill="url(#cardBg)" filter="url(#cardShadowStacked)"/>'
    )
    parts.append(
        f'      <rect x="6" y="6" width="388" height="368" rx="10" fill="url(#{slot["inner"]})" class="card-inner-pulse"/>'
    )
    parts.append(
        f'      <rect x="0" y="0" width="400" height="380" rx="14" fill="none" stroke="{slot["hex"]}" stroke-width="2" pathLength="1560" class="card-edge {slot["edge"]}"/>'
    )
    parts.append(
        '      <rect x="0" y="0" width="400" height="380" rx="14" fill="url(#cardHighlight)"/>'
    )
    parts.append(
        f'      <text x="32" y="52" class="t-caption" fill="{slot["hex"]}">{_x(visual["caption"])}</text>'
    )
    parts.append(f'      <text x="32" y="96" class="t-title">{_x(title)}</text>')
    parts.append(f'      <text x="32" y="130" class="t-tagline">{_x(visual["tagline"])}</text>')
    parts.append(
        f'      <text x="32" y="180" class="t-tool" fill="#FFFFFF" font-weight="700">{_x(primary)}</text>'
    )
    if secondary:
        parts.append(f'      <text x="32" y="208" class="t-tool">{_x(secondary)}</text>')
    if tertiary:
        parts.append(
            f'      <text x="32" y="236" class="t-tool" fill="#9BA1A6">{_x(tertiary)}</text>'
        )
    parts.append(
        '      <line x1="32" y1="266" x2="368" y2="266" stroke="#21262D" stroke-width="1"/>'
    )
    if show_stats:
        for i, stat in enumerate(stats):
            sx = 32 + i * 120
            # Long stat values (>5 chars, typically mastery words like
            # "PROFICIENT" or "ADVANCED") get a smaller font so they don't
            # overflow the ~96px-wide column. Short numeric values like "4+"
            # or "30+" stay at the larger 26px for visual prominence.
            num_class = "t-stat-num-sm" if len(stat.num) > 5 else "t-stat-num"
            # Smaller font sits 4px lower so its baseline visually aligns
            # with the larger numeric stats in adjacent columns.
            num_y = 308 if len(stat.num) > 5 else 306
            parts.append(
                f'      <text x="{sx}"  y="{num_y}" class="{num_class}" fill="{slot["hex"]}">{_x(stat.num)}</text>'
            )
            parts.append(
                f'      <text x="{sx}"  y="324" class="t-stat-lbl">{_x(stat.label)}</text>'
            )
    parts.append('      <rect x="32" y="354" width="336" height="3" rx="1.5" fill="#21262D"/>')
    parts.append(
        f'      <line x1="32" y1="355.5" x2="{bar_x_end}" y2="355.5" stroke="url(#profGrad)" stroke-width="3" stroke-linecap="round" class="draw-bar {slot["bar"]}"/>'
    )
    parts.append("    </g>")
    parts.append("  </g>")
    return "\n".join(parts)


# ── Public API ───────────────────────────────────────────────────────────
def build(config: Config, output: str | Path) -> Path:
    """Emit assets/tech-cards.svg from the user's brain regions.

    Layout: 3 columns x 2 rows of glassmorphism cards. Each card draws from
    one brain region — domain becomes the title, tools become the tech list,
    and visual metadata (emoji/caption/tagline/mastery/stats) comes from the
    region itself or domain-keyed presets.
    """
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    regions_obj = config.brain.regions
    regions = [getattr(regions_obj, name) for name in _REGION_ORDER]

    aria_domains = ", ".join(r.domain for r in regions if r.domain)
    head = _HEAD.replace("__ARIA__", _x(f"Tech stack — {aria_domains}"))

    show_stats = config.cards.tech_stack.show_stats
    cards = "\n".join(
        _render_card(slot, region, show_stats=show_stats)
        for slot, region in zip(_SLOTS, regions, strict=True)
    )

    out.write_text(head + cards + "\n" + _TAIL, encoding="utf-8")
    return out
