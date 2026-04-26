"""Animated section divider — a brand-color highlight that sweeps across.

Stretches edge-to-edge in the README via width="100%". The animated gradient
is what catches the eye; the static base line keeps the divider visible
even in environments where SMIL is disabled.
"""

from __future__ import annotations

from pathlib import Path

from ..schema import Config


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    background = config.brand.colors.background

    # Jewel-tone palette — same family as brain DNA + aurora flow + github_icon
    # halo. Replaces the previous brand-primary red sweep so divider matches
    # the unified polish across all widgets.
    rose = "#C95E8A"
    violet = "#7B5EAA"
    cyan = "#4F8CC4"

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="6" viewBox="0 0 1200 6" '
        'preserveAspectRatio="none" role="presentation" aria-hidden="true">\n'
        "  <defs>\n"
        '    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">\n'
        f'      <stop offset="0%"   stop-color="{background}" stop-opacity="0"/>\n'
        f'      <stop offset="30%"  stop-color="{cyan}"       stop-opacity="0.55"/>\n'
        f'      <stop offset="50%"  stop-color="{rose}"       stop-opacity="0.95"/>\n'
        f'      <stop offset="70%"  stop-color="{violet}"     stop-opacity="0.65"/>\n'
        f'      <stop offset="100%" stop-color="{background}" stop-opacity="0"/>\n'
        # Slower 11s drift + ease-in-out spline for organic motion (was 6s linear)
        '      <animate attributeName="x1" values="-1;1;-1" dur="11s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>\n'
        '      <animate attributeName="x2" values="0;2;0"  dur="11s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>\n'
        "    </linearGradient>\n"
        "  </defs>\n"
        f'  <rect x="0" y="2.5" width="1200" height="1" fill="{violet}" fill-opacity="0.25"/>\n'
        '  <rect x="0" y="0" width="1200" height="6" fill="url(#sweep)"/>\n'
        "</svg>\n"
    )
    out.write_text(svg, encoding="utf-8")
    return out
