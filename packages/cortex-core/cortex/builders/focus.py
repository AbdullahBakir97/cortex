"""Current-focus tile dashboard — Netflix-style "now playing" cards.

Renders up to 6 rich tiles in a 3x2 grid. Each tile = one project the user is
working on right now. Status pill pulses ("RECORDING NOW" feel), accent stripe
glows, tiles stagger-fade in.

Per-tile content:
  • status badge (ACTIVE / SHIPPING / EXPLORING / MAINTAINING / BUILDING)
  • emoji + project title
  • description (word-wrapped to ≤3 lines)
  • up to 4 tech pills (auto-sized by label width)
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, FocusTile


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# Accent name → hex (matches the brain palette + tech-cards palette)
_ACCENT_HEX: dict[str, str] = {
    "red": "#F90001",
    "orange": "#FF652F",
    "green": "#34D399",
    "gold": "#FFD23F",
    "cyan": "#22D3EE",
    "purple": "#A78BFA",
}

# Tile geometry
_TILE_W = 460
_TILE_H = 280
_GAP = 20
_PAD = 40
_COLS = 3

# Stagger classes per slot
_STAGGER = ["t1", "t2", "t3", "t4", "t5", "t6"]


def _wrap_desc(text: str, max_chars: int = 38) -> list[str]:
    """Greedy word-wrap for tile description. Caps at 3 lines."""
    if not text:
        return []
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = (" ".join([*current, word])).strip()
        if len(candidate) <= max_chars or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
        if len(lines) >= 3:
            break
    if current and len(lines) < 3:
        lines.append(" ".join(current))
    return lines[:3]


def _pill_width(label: str) -> int:
    """Approximate pixel width of a tech pill at 13px JetBrains Mono."""
    return max(52, len(label) * 9 + 22)


def _render_tile(slot_x: int, slot_y: int, slot_idx: int, tile: FocusTile) -> str:
    accent = _ACCENT_HEX.get(tile.accent, _ACCENT_HEX["red"])
    title = f"{tile.emoji} {tile.project}".strip()
    desc_lines = _wrap_desc(tile.description, max_chars=33)

    # Status pill auto-sizes to the label
    status_label = tile.status
    status_w = max(92, len(status_label) * 9 + 44)
    status_text_x = (status_w + 22) // 2  # offset right of the dot

    parts = [
        f'  <g transform="translate({slot_x},{slot_y})">',
        f'    <g class="tile-rise {_STAGGER[slot_idx]}">',
        f'      <rect x="0" y="0" width="{_TILE_W}" height="{_TILE_H}" rx="14" fill="url(#tileBg)" filter="url(#tileShadowStacked)"/>',
        f'      <rect x="6" y="6" width="{_TILE_W - 12}" height="{_TILE_H - 12}" rx="10" fill="{accent}" fill-opacity="0.10" class="tile-inner-pulse"/>',
        f'      <rect x="0" y="0" width="{_TILE_W}" height="{_TILE_H}" rx="14" fill="none" stroke="{accent}" stroke-width="2" pathLength="1580" class="tile-edge te{slot_idx + 1}"/>',
        f'      <rect x="0" y="0" width="{_TILE_W}" height="{_TILE_H}" rx="14" fill="url(#tileHighlight)"/>',
        '      <g transform="translate(24, 28)">',
        f'        <rect x="0" y="0" width="{status_w}" height="28" rx="14" fill="{accent}" fill-opacity="0.18" stroke="{accent}" stroke-width="1"/>',
        f'        <circle cx="16" cy="14" r="4" fill="{accent}" class="live-dot"/>',
        f'        <text x="{status_text_x}" y="19" class="t-status" fill="{accent}" text-anchor="middle">{_x(status_label)}</text>',
        "      </g>",
        f'      <text x="24" y="106" class="t-title">{_x(title)}</text>',
    ]

    # Description lines (up to 3)
    for li, line in enumerate(desc_lines):
        parts.append(f'      <text x="24" y="{146 + li * 22}" class="t-desc">{_x(line)}</text>')

    # Tech pills
    if tile.tech:
        pill_x = 0
        pill_parts = ['      <g transform="translate(24, 226)">']
        for label in tile.tech[:4]:
            w = _pill_width(label)
            pill_parts.append(
                f'        <g><rect x="{pill_x}" y="0" width="{w}" height="28" rx="14" fill="none" stroke="{accent}" stroke-width="1"/><text x="{pill_x + w // 2}" y="19" class="t-pill" fill="{accent}" text-anchor="middle">{_x(label)}</text></g>'
            )
            pill_x += w + 10
        pill_parts.append("      </g>")
        parts.extend(pill_parts)

    parts.append("    </g>")
    parts.append("  </g>")
    return "\n".join(parts)


def build(config: Config, output: str | Path) -> Path:
    """Emit assets/current-focus.svg from cards.current_focus.tiles."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    tiles = list(config.cards.current_focus.tiles)[:6]
    if not tiles:
        out.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="120" viewBox="0 0 800 120">'
            '<text x="400" y="60" font-family="Inter,sans-serif" fill="#9BA1A6" text-anchor="middle">'
            "Add tiles to cards.current_focus.tiles in cortex.yml."
            "</text></svg>\n",
            encoding="utf-8",
        )
        return out

    n = len(tiles)
    cols = min(_COLS, n)
    rows = (n + cols - 1) // cols
    svg_w = _PAD * 2 + cols * _TILE_W + (cols - 1) * _GAP
    svg_h = 110 + rows * _TILE_H + (rows - 1) * _GAP + _PAD

    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" '
        f'role="img" aria-label="Currently working on — {n} active focus tiles">\n'
        "  <style>\n"
        "    .t-display   { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 36px; letter-spacing: -0.01em; fill: #FFFFFF; }\n"
        "    .t-tag       { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 14px; letter-spacing: 0.30em; text-transform: uppercase; fill: #C4B5FD; }\n"
        "    .t-status    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 12px; letter-spacing: 0.20em; text-transform: uppercase; }\n"
        "    .t-title     { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 24px; letter-spacing: -0.005em; fill: #FFFFFF; }\n"
        "    .t-desc      { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 500; font-size: 16px; fill: #C9CDD3; }\n"
        "    .t-pill      { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 700; font-size: 13px; }\n"
        "    .live-dot { animation: liveDot 1.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }\n"
        "    @keyframes liveDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.8); opacity: 0.4; } }\n"
        "    .tile-rise { opacity: 0; animation: tileRise 0.7s cubic-bezier(0.22,1,0.36,1) forwards; }\n"
        "    @keyframes tileRise { to { opacity: 1; } }\n"
        "    .t1 { animation-delay: 0.0s; } .t2 { animation-delay: 0.08s; } .t3 { animation-delay: 0.16s; }\n"
        "    .t4 { animation-delay: 0.24s; } .t5 { animation-delay: 0.32s; } .t6 { animation-delay: 0.40s; }\n"
        "    /* Travelling edge highlight + inner glow — same R2-4 pattern as brain cards. */\n"
        "    .tile-edge { stroke-dasharray: 80 1500; animation: tileEdgeTravel 4.4s linear infinite; filter: url(#tileEdgeGlow); opacity: 0.95; }\n"
        "    @keyframes tileEdgeTravel { to { stroke-dashoffset: -1580; } }\n"
        "    .te1 { animation-delay: 0s; } .te2 { animation-delay: 0.7s; } .te3 { animation-delay: 1.4s; }\n"
        "    .te4 { animation-delay: 2.1s; } .te5 { animation-delay: 2.8s; } .te6 { animation-delay: 3.5s; }\n"
        "    .tile-inner-pulse { animation: tilePulse 5s ease-in-out infinite; }\n"
        "    @keyframes tilePulse { 0%, 100% { opacity: 0.55; } 50% { opacity: 1.0; } }\n"
        "  </style>\n"
        "  <defs>\n"
        '    <radialGradient id="bgRadial" cx="50%" cy="50%" r="80%"><stop offset="0%" stop-color="#0F0816"/><stop offset="100%" stop-color="#000000"/></radialGradient>\n'
        '    <pattern id="dots" x="0" y="0" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="0.8" fill="#F90001" fill-opacity="0.07"/></pattern>\n'
        '    <linearGradient id="tileBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1A2028" stop-opacity="0.96"/><stop offset="100%" stop-color="#0D1117" stop-opacity="0.96"/></linearGradient>\n'
        '    <linearGradient id="tileHighlight" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.08"/><stop offset="40%" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>\n'
        '    <!-- Stacked drop shadow + edge-glow filter (matches brain + tech-cards). -->\n'
        '    <filter id="tileShadowStacked" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.30"/><feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.40"/><feDropShadow dx="0" dy="14" stdDeviation="24" flood-color="#000" flood-opacity="0.30"/></filter>\n'
        '    <filter id="tileEdgeGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.2"/></filter>\n'
        "  </defs>\n"
        f'  <rect width="{svg_w}" height="{svg_h}" fill="url(#bgRadial)"/>\n'
        f'  <rect width="{svg_w}" height="{svg_h}" fill="url(#dots)"/>\n'
        f'  <text x="{svg_w // 2}" y="42" class="t-tag" text-anchor="middle">⏵ NOW · WORKING · ON ⏴</text>\n'
        f'  <text x="{svg_w // 2}" y="78" class="t-display" text-anchor="middle">Current Focus</text>\n'
    )

    tile_blocks: list[str] = []
    for i, tile in enumerate(tiles):
        col = i % cols
        row = i // cols
        slot_x = _PAD + col * (_TILE_W + _GAP)
        slot_y = 110 + row * (_TILE_H + _GAP)
        tile_blocks.append(_render_tile(slot_x, slot_y, i, tile))

    out.write_text(head + "\n".join(tile_blocks) + "\n</svg>\n", encoding="utf-8")
    return out
