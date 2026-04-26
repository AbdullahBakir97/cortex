"""Animated section divider — three layered sine waves drifting in counterpoint.

Used as both header and footer banner. Stretches edge-to-edge via width="100%".
The static thin base line keeps the divider visible when SMIL is disabled; the
three sine wave paths each have their own period, amplitude, color, and drift
timing — no two share a common multiple, so the composite never appears to
loop visibly.
"""

from __future__ import annotations

from pathlib import Path

from ..schema import Config


def _sine_path(period: float, amplitude: float, y_center: float, width: int = 1200) -> str:
    """Generate a smooth sine wave SVG path (Q + T commands).

    First quadratic curve sets the initial control point; subsequent T commands
    auto-reflect the control point to continue the wave. Result is mathematically
    smooth, not a polyline approximation.
    """
    half = period / 2
    quarter = period / 4
    # First quadratic: control at top of first hump → end at first zero crossing
    d = f"M 0,{y_center:.1f} Q {quarter:.1f},{y_center - amplitude:.1f} {half:.1f},{y_center:.1f}"
    x = half
    while x < width:
        x += half
        d += f" T {x:.1f},{y_center:.1f}"
    return d


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    background = config.brand.colors.background

    # Jewel-tone palette — same family as brain DNA + aurora flow + github_icon
    # halo. Unifies polish across all widgets.
    rose = "#C95E8A"
    violet = "#7B5EAA"
    cyan = "#4F8CC4"

    # 3 sine waves at different periods/amplitudes/y-centers — when layered they
    # never align visually, creating a continuous flowing wave-field rather than
    # repeating pattern.
    wave_cyan = _sine_path(period=120, amplitude=5, y_center=8)
    wave_rose = _sine_path(period=160, amplitude=4, y_center=12)
    wave_violet = _sine_path(period=200, amplitude=6, y_center=16)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="24" viewBox="0 0 1200 24"
     preserveAspectRatio="none" role="presentation" aria-hidden="true">
  <defs>
    <!-- Each sweep gradient drifts left↔right on a unique cycle. The fade at
         each end means the colored portion of each wave is always a soft
         travelling band, never the whole wave at once. Different durations
         (9s, 11s, 14s) and offset begin times keep the 3 waves out of sync. -->
    <linearGradient id="waveSweep1" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
      <stop offset="0%"   stop-color="{cyan}" stop-opacity="0"/>
      <stop offset="50%"  stop-color="{cyan}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{cyan}" stop-opacity="0"/>
      <animate attributeName="x1" values="-1;1;-1" dur="9s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
      <animate attributeName="x2" values="0;2;0" dur="9s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
    </linearGradient>
    <linearGradient id="waveSweep2" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
      <stop offset="0%"   stop-color="{rose}" stop-opacity="0"/>
      <stop offset="50%"  stop-color="{rose}" stop-opacity="0.90"/>
      <stop offset="100%" stop-color="{rose}" stop-opacity="0"/>
      <animate attributeName="x1" values="1;-1;1" dur="11s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
      <animate attributeName="x2" values="2;0;2" dur="11s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
    </linearGradient>
    <linearGradient id="waveSweep3" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
      <stop offset="0%"   stop-color="{violet}" stop-opacity="0"/>
      <stop offset="50%"  stop-color="{violet}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{violet}" stop-opacity="0"/>
      <animate attributeName="x1" values="-1;1;-1" dur="14s" begin="3s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
      <animate attributeName="x2" values="0;2;0" dur="14s" begin="3s" repeatCount="indefinite"
               calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
    </linearGradient>
    <!-- Soft glow filter — a subtle halo on the wave strokes makes them read as
         luminous lines rather than crisp pixels. -->
    <filter id="waveGlow" x="-5%" y="-50%" width="110%" height="200%">
      <feGaussianBlur stdDeviation="0.6"/>
    </filter>
  </defs>
  <!-- Static thin base line for SMIL-off renderers. -->
  <rect x="0" y="11.5" width="1200" height="1" fill="{violet}" fill-opacity="0.20"/>
  <!-- Three sine wave layers — different period/amplitude/y-center/timing/color.
       Stroked, not filled, so the wave shape is clearly visible. -->
  <g filter="url(#waveGlow)">
    <path d="{wave_cyan}" fill="none" stroke="url(#waveSweep1)" stroke-width="1.6" stroke-linecap="round"/>
    <path d="{wave_rose}" fill="none" stroke="url(#waveSweep2)" stroke-width="1.8" stroke-linecap="round"/>
    <path d="{wave_violet}" fill="none" stroke="url(#waveSweep3)" stroke-width="2.0" stroke-linecap="round"/>
  </g>
  <!-- Background fade for environments where the layered waves dominate too much.
       (Suppressed via opacity — kept for any future need to show a base color.) -->
  <rect x="0" y="0" width="1200" height="24" fill="{background}" fill-opacity="0"/>
</svg>
"""
    out.write_text(svg, encoding="utf-8")
    return out
