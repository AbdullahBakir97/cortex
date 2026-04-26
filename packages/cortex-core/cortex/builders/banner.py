"""Animated header / footer banner — capsule-render replacement.

Renders a wide banner SVG (1200 x H) with:
  • Animated multi-color jewel-tone gradient background
  • Configurable bottom edge shape: wave / slice / rect (top edge for footer)
  • Optional centered title + subtitle text overlay
  • Three layered sine waves near the shaped edge for depth (when shape=wave)
  • Soft glow filters for premium feel

Used as both header and footer — the footer reuses the same logic with edge
position flipped so the shaped edge is at the TOP of the banner.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import BannerConfig, Config


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# Default jewel-tone palette — matches brain DNA, aurora flow, divider.
# Used when BannerConfig.colors is empty.
_DEFAULT_COLORS = ["#0E0820", "#7B5EAA", "#C95E8A", "#4F8CC4", "#0E0820"]


def _sine_path(period: float, amplitude: float, y_center: float, width: int = 1200) -> str:
    """Generate a smooth sine wave SVG path (Q + T commands)."""
    half = period / 2
    quarter = period / 4
    d = f"M 0,{y_center:.1f} Q {quarter:.1f},{y_center - amplitude:.1f} {half:.1f},{y_center:.1f}"
    x = half
    while x < width:
        x += half
        d += f" T {x:.1f},{y_center:.1f}"
    return d


def _shape_path(shape: str, height: int, edge_y: float, width: int = 1200, *, footer: bool) -> str:
    """Generate a closed path for the banner background shape.

    Header layout: shape forms the BOTTOM edge of the banner. Path covers
    everything ABOVE the shaped edge.
    Footer layout: shape forms the TOP edge of the banner. Path covers
    everything BELOW the shaped edge.

    `edge_y` = the y-coordinate of the shaped edge's center line.
    """
    if shape == "wave":
        amp = 22
        period = 280
        # Wave shape on the chosen edge, then close the rectangle on the other 3 sides.
        wave_d = (
            f"M 0,{edge_y:.1f} Q {period / 4:.1f},{edge_y - amp:.1f} {period / 2:.1f},{edge_y:.1f}"
        )
        x = period / 2
        while x < width:
            x += period / 2
            wave_d += f" T {x:.1f},{edge_y:.1f}"
        if footer:
            # Wave at top → close path going DOWN to fill footer.
            return wave_d + f" L {width},{height} L 0,{height} Z"
        # Wave at bottom → close path going UP to fill header.
        return wave_d + f" L {width},0 L 0,0 Z"
    elif shape == "slice":
        # Diagonal edge — rises from left edge to a point partway across.
        if footer:
            return (
                f"M 0,{edge_y - 30:.1f} L {width},{edge_y + 10:.1f} "
                f"L {width},{height} L 0,{height} Z"
            )
        return f"M 0,{edge_y - 10:.1f} L {width},{edge_y - 50:.1f} L {width},0 L 0,0 Z"
    else:  # rect — straight edge, no decoration
        if footer:
            return f"M 0,{edge_y:.1f} L {width},{edge_y:.1f} L {width},{height} L 0,{height} Z"
        return f"M 0,{edge_y:.1f} L {width},{edge_y:.1f} L {width},0 L 0,0 Z"


def _gradient_stops(colors: list[str]) -> str:
    """Build SVG <stop> elements for the banner background gradient.

    Distributes the color list evenly across 0%-100% offsets.
    """
    n = len(colors)
    stops = []
    for i, color in enumerate(colors):
        offset = round(100 * i / (n - 1)) if n > 1 else 0
        stops.append(f'<stop offset="{offset}%" stop-color="{color}"/>')
    return "".join(stops)


def _animation_block(banner_id: str, animation: str) -> str:
    """SMIL animation snippet for the gradient based on animation style."""
    if animation == "static":
        return ""
    if animation == "pulse":
        # Opacity pulse on the entire fill — slow, ease-in-out.
        return ""
    # "drift" — gradient stops translate left↔right.
    return (
        '<animate attributeName="x1" values="-1;1;-1" dur="22s" '
        'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
        'keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
        '<animate attributeName="x2" values="0;2;0" dur="22s" '
        'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
        'keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
    )


def _render_banner(config: Config, banner: BannerConfig, *, footer: bool) -> str:
    """Render a single banner SVG (header or footer)."""
    width = 1200
    height = banner.height

    # Resolve color palette
    colors = banner.colors if banner.colors else _DEFAULT_COLORS

    # Edge geometry — for "wave" the centerline is set so the wave doesn't
    # spill outside the banner box at peak amplitude.
    edge_y = float(height - 30) if not footer else 30.0

    shape_d = _shape_path(banner.shape, height, edge_y, width, footer=footer)

    # Layered decorative sine waves near the shaped edge — only for "wave" shape.
    deco_waves = ""
    if banner.shape == "wave":
        # 3 sine waves stroked, drifting at different speeds — same pattern as divider.
        if not footer:
            wave_a_y = edge_y - 50
            wave_b_y = edge_y - 30
            wave_c_y = edge_y - 10
        else:
            wave_a_y = edge_y + 50
            wave_b_y = edge_y + 30
            wave_c_y = edge_y + 10

        d_a = _sine_path(period=160, amplitude=8, y_center=wave_a_y)
        d_b = _sine_path(period=200, amplitude=6, y_center=wave_b_y)
        d_c = _sine_path(period=240, amplitude=5, y_center=wave_c_y)
        deco_waves = (
            f'<g filter="url(#bannerWaveGlow)" opacity="0.7">'
            f'  <path d="{d_a}" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.35" stroke-linecap="round"/>'
            f'  <path d="{d_b}" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-opacity="0.50" stroke-linecap="round"/>'
            f'  <path d="{d_c}" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-opacity="0.65" stroke-linecap="round"/>'
            f"</g>"
        )

    # Title text overlay — centered, uses Inter at large display size.
    title_text = ""
    if banner.title:
        # Title y-position: vertically centered in the area ABOVE the wave (header)
        # or BELOW the wave (footer).
        if not footer:
            ty = (edge_y - 50) // 2 + 20
        else:
            ty = edge_y + (height - edge_y) // 2 + 20
        title_text = (
            f'<text x="{width // 2}" y="{ty}" class="banner-title" '
            f'text-anchor="middle">{_x(banner.title)}</text>'
        )
        if banner.subtitle:
            title_text += (
                f'<text x="{width // 2}" y="{ty + 32}" class="banner-subtitle" '
                f'text-anchor="middle">{_x(banner.subtitle)}</text>'
            )

    bg_id = "bannerBgFooter" if footer else "bannerBg"
    fill_anim = _animation_block(bg_id, banner.animation)

    pulse_class = ' class="banner-pulse"' if banner.animation == "pulse" else ""

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {width} {height}" preserveAspectRatio="none"
     role="img" aria-label="{_x(banner.title or ("Footer" if footer else "Header"))}">
  <defs>
    <linearGradient id="{bg_id}" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
      {_gradient_stops(colors)}
      {fill_anim}
    </linearGradient>
    <filter id="bannerWaveGlow" x="-5%" y="-50%" width="110%" height="200%">
      <feGaussianBlur stdDeviation="0.8"/>
    </filter>
  </defs>
  <style><![CDATA[
    .banner-title    {{ font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 54px; letter-spacing: -0.015em; fill: #FFFFFF; }}
    .banner-subtitle {{ font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 500; font-size: 18px; letter-spacing: 0.18em; text-transform: uppercase; fill: #FFFFFF; fill-opacity: 0.78; }}
    .banner-pulse {{ animation: bannerPulse 7s ease-in-out infinite; }}
    @keyframes bannerPulse {{ 0%, 100% {{ opacity: 0.85; }} 50% {{ opacity: 1.0; }} }}
  ]]></style>
  <path d="{shape_d}" fill="url(#{bg_id})"{pulse_class}/>
  {deco_waves}
  {title_text}
</svg>
"""
    return svg


def build_header(config: Config, output: str | Path) -> Path:
    """Build the header banner SVG."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_banner(config, config.cards.header, footer=False), encoding="utf-8")
    return out


def build_footer(config: Config, output: str | Path) -> Path:
    """Build the footer banner SVG."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_banner(config, config.cards.footer, footer=True), encoding="utf-8")
    return out
