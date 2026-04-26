"""Badges widget — compact skill / tech / achievement badges.

Renders a row, grid, or scrolling marquee of badges where each badge can be
rendered in one of four shapes (pill, hex, shield, circle) with an icon
monogram, label, and optional value sublabel. The visual polish (drop shadow,
inner glow, stacked gradients) matches the rest of the cortex widget set.

Public API:

    >>> from cortex.builders.badges import build
    >>> build(config, output="assets/badges.svg")

Layout strategies:

  • row     — flex-style horizontal flow that wraps when wider than the SVG
  • grid    — fixed N columns, regular rows
  • marquee — horizontal scroll on one line (animated translate)

Animations:

  • stagger — sequential fade-in on load (0.06s offset between badges)
  • shimmer — diagonal highlight sweep across each badge
  • pulse   — subtle scale breathing on each badge
  • static  — no animation (useful for high-contrast accessibility)
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..icons import derive_monogram, lookup
from ..schema import BadgeItem, BadgesConfig, Config
from ..themes import REDUCED_MOTION_CSS, resolve_theme


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# ── Layout constants ────────────────────────────────────────────────────────
SVG_WIDTH = 1200

# Per-shape pixel dimensions. Pill = label + value; others are icon-first.
BADGE_W = {"pill": 168, "hex": 112, "shield": 124, "circle": 100}
BADGE_H = {"pill": 56, "hex": 116, "shield": 128, "circle": 100}
BADGE_GAP = 14


def _resolve(item: BadgeItem, theme_fallback: str) -> tuple[str, str, str]:
    """Return (monogram, color, label) for a badge.

    Resolution order for monogram:
        1. icon_svg (caller bypasses monogram entirely — handled later)
        2. icon slug → KNOWN_ICONS lookup
        3. derive from label

    Resolution order for color:
        1. explicit ``color`` field
        2. brand color from KNOWN_ICONS lookup
        3. ``brand.theme`` primary slot
    """
    if item.icon and (hit := lookup(item.icon)):
        mono_default, color_default = hit
    else:
        mono_default, color_default = derive_monogram(item.label), theme_fallback
    color = item.color or color_default
    return mono_default, color, item.label


def _shape_path(shape: str, w: int, h: int) -> str:
    """Return the closed SVG path ``d`` for the badge background shape.

    All paths are positioned so the top-left of the shape is at (0, 0) — the
    caller wraps each in a ``<g transform="translate(...)">``.
    """
    if shape == "pill":
        r = h / 2
        return (
            f"M {r:.1f},0 H {w - r:.1f} A {r:.1f},{r:.1f} 0 0 1 {w - r:.1f},{h} "
            f"H {r:.1f} A {r:.1f},{r:.1f} 0 0 1 {r:.1f},0 Z"
        )
    if shape == "circle":
        r = min(w, h) / 2
        cx, cy = w / 2, h / 2
        return (
            f"M {cx - r:.1f},{cy:.1f} A {r:.1f},{r:.1f} 0 1 0 {cx + r:.1f},{cy:.1f} "
            f"A {r:.1f},{r:.1f} 0 1 0 {cx - r:.1f},{cy:.1f} Z"
        )
    if shape == "hex":
        # Pointy-top hexagon; flat sides left/right.
        cx, cy = w / 2, h / 2
        rx, ry = w / 2, h / 2
        # 6 points starting at top.
        pts = [
            (cx, cy - ry),
            (cx + rx * 0.866, cy - ry * 0.5),
            (cx + rx * 0.866, cy + ry * 0.5),
            (cx, cy + ry),
            (cx - rx * 0.866, cy + ry * 0.5),
            (cx - rx * 0.866, cy - ry * 0.5),
        ]
        d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
        for px, py in pts[1:]:
            d += f" L {px:.1f},{py:.1f}"
        return d + " Z"
    if shape == "shield":
        # Heraldic shield: rounded top, tapered point at bottom.
        cx = w / 2
        r = 14
        return (
            f"M {r:.1f},0 H {w - r:.1f} A {r:.1f},{r:.1f} 0 0 1 {w},{r:.1f} "
            f"V {h * 0.55:.1f} Q {w},{h * 0.85:.1f} {cx:.1f},{h:.1f} "
            f"Q 0,{h * 0.85:.1f} 0,{h * 0.55:.1f} V {r:.1f} "
            f"A {r:.1f},{r:.1f} 0 0 1 {r:.1f},0 Z"
        )
    raise ValueError(f"unknown badge shape: {shape}")


def _layout_positions(
    n: int, layout: str, columns: int, badge_w: int, badge_h: int
) -> tuple[list[tuple[int, int]], int]:
    """Compute (x, y) origin for each badge given the layout. Returns (positions, total_height)."""
    if layout == "grid":
        cols = max(1, columns)
        positions = []
        for i in range(n):
            row, col = divmod(i, cols)
            x = col * (badge_w + BADGE_GAP) + 20
            y = row * (badge_h + BADGE_GAP) + 20
            positions.append((x, y))
        total_h = ((n + cols - 1) // cols) * (badge_h + BADGE_GAP) + 20
        return positions, total_h
    if layout == "marquee":
        # Single line, no wrap — total width is sum of badges; SVG viewBox
        # only shows the visible window.
        positions = [(i * (badge_w + BADGE_GAP) + 20, 20) for i in range(n)]
        return positions, badge_h + 40
    # row (default): wrap when next badge would exceed SVG_WIDTH.
    positions = []
    x, y = 20, 20
    for _ in range(n):
        if x + badge_w + 20 > SVG_WIDTH:
            x = 20
            y += badge_h + BADGE_GAP
        positions.append((x, y))
        x += badge_w + BADGE_GAP
    total_h = y + badge_h + 20
    return positions, total_h


def _icon_glyph(item: BadgeItem, monogram: str, cx: float, cy: float, size: int) -> str:
    """Render the icon area: either user-supplied SVG path or the monogram."""
    if item.icon_svg:
        # User-supplied SVG path data is normalized to a 24-unit canvas;
        # we scale it up so the glyph fits the badge.
        scale = size / 24.0
        tx = cx - size / 2
        ty = cy - size / 2
        return (
            f'<g transform="translate({tx:.1f},{ty:.1f}) scale({scale:.3f})" fill="#FFFFFF">'
            f'<path d="{_x(item.icon_svg)}"/>'
            f"</g>"
        )
    # Monogram: bold sans-serif, white-with-soft-shadow.
    return (
        f'<text x="{cx:.1f}" y="{cy + size * 0.18:.1f}" '
        f'class="b-mono" text-anchor="middle">{_x(monogram)}</text>'
    )


def _render_badge(
    item: BadgeItem,
    x: int,
    y: int,
    shape: str,
    idx: int,
    animation: str,
    theme_fallback: str,
) -> str:
    """Render a single badge group at (x, y)."""
    monogram, color, label = _resolve(item, theme_fallback)
    w, h = BADGE_W[shape], BADGE_H[shape]
    shape_d = _shape_path(shape, w, h)
    grad_id = f"bg-{idx}"
    glow_id = f"glow-{idx}"

    # Layout knobs per shape: where icon sits, where label/value sit.
    if shape == "pill":
        icon_cx, icon_cy, icon_size = 28, h / 2, 24
        label_x, label_y = 60, h / 2 - 4 if item.value else h / 2 + 4
        label_anchor = "start"
        value_x, value_y = 60, h / 2 + 14
        value_anchor = "start"
    elif shape == "circle":
        icon_cx, icon_cy, icon_size = w / 2, h / 2 - 6, 28
        label_x, label_y = w / 2, h - 18
        label_anchor = "middle"
        value_x = value_y = 0  # circle skips value
        value_anchor = "middle"
    elif shape == "hex":
        icon_cx, icon_cy, icon_size = w / 2, h / 2 - 14, 30
        label_x, label_y = w / 2, h - 30
        label_anchor = "middle"
        value_x, value_y = w / 2, h - 14
        value_anchor = "middle"
    else:  # shield
        icon_cx, icon_cy, icon_size = w / 2, h * 0.32, 32
        label_x, label_y = w / 2, h * 0.62
        label_anchor = "middle"
        value_x, value_y = w / 2, h * 0.78
        value_anchor = "middle"

    icon_svg = _icon_glyph(item, monogram, icon_cx, icon_cy, icon_size)

    # Stagger animation: each badge fades in 0.06s after the previous.
    # Implemented via per-group opacity animate so it works in both
    # GitHub's SVG sandbox AND ordinary browsers.
    stagger_attr = ""
    if animation == "stagger":
        delay = idx * 0.06
        stagger_attr = (
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>'
        )
    pulse_class = ' class="b-pulse"' if animation == "pulse" else ""
    shimmer_overlay = ""
    if animation == "shimmer":
        # Diagonal highlight sweep that translates left→right behind the shape.
        shimmer_overlay = (
            f'<rect x="-{w}" y="0" width="{w * 0.4:.0f}" height="{h}" '
            f'fill="url(#shimmer-{idx})" clip-path="url(#clip-{idx})">'
            f'<animate attributeName="x" from="-{w}" to="{w * 1.6:.0f}" '
            f'begin="{(idx * 0.15) % 4:.2f}s" dur="2.6s" repeatCount="indefinite"/>'
            f"</rect>"
        )

    label_text = (
        f'<text x="{label_x:.1f}" y="{label_y:.1f}" class="b-label" '
        f'text-anchor="{label_anchor}">{_x(label)}</text>'
    )
    value_text = ""
    if item.value and shape != "circle":
        value_text = (
            f'<text x="{value_x:.1f}" y="{value_y:.1f}" class="b-value" '
            f'text-anchor="{value_anchor}">{_x(item.value)}</text>'
        )

    inner = (
        f"<defs>"
        f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.95"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0.55"/>'
        f"</linearGradient>"
        f'<clipPath id="clip-{idx}"><path d="{shape_d}"/></clipPath>'
        f'<linearGradient id="shimmer-{idx}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>'
        f'<stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.45"/>'
        f'<stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>'
        f"</linearGradient>"
        f"</defs>"
        f'<path d="{shape_d}" fill="url(#{grad_id})" filter="url(#{glow_id})"/>'
        f'<path d="{shape_d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'
        f"{shimmer_overlay}"
        f"{icon_svg}"
        f"{label_text}"
        f"{value_text}"
        f"{stagger_attr}"
    )

    g_open = f'<g transform="translate({x},{y})"{pulse_class}'
    if animation == "stagger":
        g_open += ' opacity="0"'
    g_open += ">"

    if item.href:
        return (
            f'<a xlink:href="{_x(item.href)}" target="_blank" rel="noopener">'
            f"{g_open}{inner}</g></a>"
        )
    return f"{g_open}{inner}</g>"


def _render(config: Config) -> str:
    bcfg: BadgesConfig = config.cards.badges
    theme = resolve_theme(config)
    theme_fallback = theme["primary"]
    items = list(bcfg.items)
    if not items:
        # Render an empty placeholder so the file always exists.
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 60" '
            'role="img" aria-label="Badges (empty)"></svg>\n'
        )

    shape = bcfg.shape
    w, h = BADGE_W[shape], BADGE_H[shape]
    positions, total_h = _layout_positions(len(items), bcfg.layout, bcfg.columns, w, h)

    badges_svg = "\n  ".join(
        _render_badge(item, x, y, shape, i, bcfg.animation, theme_fallback)
        for i, (item, (x, y)) in enumerate(zip(items, positions, strict=True))
    )

    # Marquee wraps the whole badge group in an animated translate.
    marquee_open = ""
    marquee_close = ""
    if bcfg.layout == "marquee":
        # Compute total content width to know when to wrap.
        total_w = len(items) * (w + BADGE_GAP)
        marquee_open = (
            '<g class="b-marquee">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="-{total_w} 0" dur="{max(20, len(items) * 2)}s" '
            f'repeatCount="indefinite"/>'
        )
        marquee_close = "</g>"
        # Render twice for seamless loop.
        badges_svg = (
            badges_svg
            + "\n  "
            + "\n  ".join(
                _render_badge(
                    item, x + total_w, y, shape, i + len(items), bcfg.animation, theme_fallback
                )
                for i, (item, (x, y)) in enumerate(zip(items, positions, strict=True))
            )
        )

    # One shared filter (drop shadow + inner glow) used by every badge.
    glow_filters = "\n    ".join(
        f'<filter id="glow-{i}" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.45"/>'
        f"</filter>"
        for i in range(len(items) * (2 if bcfg.layout == "marquee" else 1))
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {SVG_WIDTH} {total_h}"
     preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="Skill badges">
  <defs>
    {glow_filters}
  </defs>
  <style><![CDATA[
    .b-mono   {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 800; font-size: 18px; fill: #FFFFFF; letter-spacing: -0.02em; }}
    .b-label  {{ font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 14px; fill: #FFFFFF; letter-spacing: -0.01em; }}
    .b-value  {{ font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 500; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.78; letter-spacing: 0.06em; text-transform: uppercase; }}
    .b-pulse  {{ animation: bPulse 3.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
    @keyframes bPulse {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.04); }} }}
    {REDUCED_MOTION_CSS}
  ]]></style>
  {marquee_open}
  {badges_svg}
  {marquee_close}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    """Build the badges SVG and write it to ``output``."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
