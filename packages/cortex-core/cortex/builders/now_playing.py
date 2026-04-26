"""Now Playing — Spotify-style "currently coding in" card.

Wide horizontal card showing the current activity (e.g. "Coding"), the
"track title" (language), an "artist line" (project/repo), animated
waveform bars, and a progress bar with elapsed/duration timestamps.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, NowPlayingConfig


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200
DEFAULT_COLOR = "#7B5EAA"


def _render(config: Config) -> str:
    npcfg: NowPlayingConfig = config.cards.now_playing
    h = npcfg.height
    color = npcfg.color or DEFAULT_COLOR
    progress = max(0.0, min(1.0, npcfg.progress))

    # Layout: card with rounded corners, full canvas.
    pad = 28
    card_w = WIDTH - 2 * pad
    card_h = h - 2 * pad

    # Album-art placeholder on the left — large rounded square with a glyph.
    art_size = card_h - 2 * pad
    art_x = pad + pad
    art_y = pad + pad

    text_x = art_x + art_size + 36

    # Activity pill (top-right of the text area).
    activity_text = (npcfg.activity or "Coding").upper()

    # Waveform: 32 bars to the right of the title, animated heights.
    n_bars = 32
    bars_x = text_x + 280
    bars_y = pad + pad + 12
    bars_w = card_w - (bars_x - pad) - 30
    bar_w = (bars_w / n_bars) * 0.55
    bar_gap = (bars_w / n_bars) * 0.45

    bars = []
    for i in range(n_bars):
        bx = bars_x + i * (bar_w + bar_gap)
        # Each bar oscillates with its own phase.
        phase = (i * 0.21) % 1.6
        # Three-keyframe up/down/up.
        hi = 12 + ((i * 7919) % 28)  # deterministic-ish "max" height per bar
        lo = max(3, hi - 22)
        bars.append(
            f'<rect x="{bx:.1f}" y="{bars_y:.1f}" width="{bar_w:.1f}" '
            f'height="{lo}" rx="2" fill="{color}" fill-opacity="0.92">'
            f'<animate attributeName="height" values="{lo};{hi};{lo}" '
            f'begin="{phase:.2f}s" dur="0.8s" repeatCount="indefinite"/>'
            f"</rect>"
        )

    # Progress bar — bottom of the card.
    bar_y = pad + card_h - pad - 32
    bar_w_total = card_w - 2 * pad
    bar_x = pad + pad
    fill_w = bar_w_total * progress

    # Glyph in album art — first letter of language, big.
    first_letter = (npcfg.language[:1] or "?").upper()

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"
     viewBox="0 0 {WIDTH} {h}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="Now playing — {_x(npcfg.language)}">
  <defs>
    <linearGradient id="np-card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1A0F26"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="np-art" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.45"/>
    </linearGradient>
    <linearGradient id="np-bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.9"/>
    </linearGradient>
    <filter id="np-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.55"/>
    </filter>
  </defs>
  <style><![CDATA[
    .np-activity  {{ font-family: 'JetBrains Mono','SF Mono',monospace; font-weight: 700; font-size: 11px; letter-spacing: 0.30em; fill: {color}; text-transform: uppercase; }}
    .np-title     {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 32px; letter-spacing: -0.01em; fill: #FFFFFF; }}
    .np-artist    {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 500; font-size: 16px; fill: #FFFFFF; fill-opacity: 0.65; }}
    .np-time      {{ font-family: 'JetBrains Mono','SF Mono',monospace; font-weight: 500; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.55; letter-spacing: 0.06em; }}
    .np-glyph     {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 80px; fill: #FFFFFF; }}
  ]]></style>
  <rect x="{pad}" y="{pad}" width="{card_w}" height="{card_h}" rx="16"
        fill="url(#np-card)" filter="url(#np-shadow)"/>
  <rect x="{pad}" y="{pad}" width="{card_w}" height="{card_h}" rx="16"
        fill="none" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1"/>
  <rect x="{art_x}" y="{art_y}" width="{art_size}" height="{art_size}" rx="12"
        fill="url(#np-art)"/>
  <text x="{art_x + art_size / 2:.1f}" y="{art_y + art_size / 2 + 28:.1f}"
        class="np-glyph" text-anchor="middle">{_x(first_letter)}</text>
  <text x="{text_x}" y="{pad + pad + 22}" class="np-activity">{_x(activity_text)}</text>
  <text x="{text_x}" y="{pad + pad + 64}" class="np-title">{_x(npcfg.language)}</text>
  <text x="{text_x}" y="{pad + pad + 92}" class="np-artist">{_x(npcfg.project) if npcfg.project else "—"}</text>
  {"".join(bars)}
  <rect x="{bar_x}" y="{bar_y}" width="{bar_w_total}" height="4" rx="2"
        fill="#FFFFFF" fill-opacity="0.18"/>
  <rect x="{bar_x}" y="{bar_y}" width="{fill_w:.1f}" height="4" rx="2"
        fill="url(#np-bar)">
    <animate attributeName="width" values="{fill_w * 0.92:.1f};{fill_w:.1f};{fill_w * 0.92:.1f}"
             dur="3s" repeatCount="indefinite"/>
  </rect>
  <text x="{bar_x}" y="{bar_y + 22}" class="np-time">{_x(npcfg.elapsed)}</text>
  <text x="{bar_x + bar_w_total:.1f}" y="{bar_y + 22}" class="np-time" text-anchor="end">{_x(npcfg.duration)}</text>
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out


# math kept available for symmetry with other geom builders.
_ = math
