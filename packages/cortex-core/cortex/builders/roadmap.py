"""Code Roadmap — metro/subway-style multi-line career map.

Each "line" is a tech path (e.g. Python → Django → Postgres → AWS) drawn
as a colored stroke with stations at milestone years. The current station
on each line gets a LIVE marker. Lines stack vertically; legend on the
left shows line names + colors.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, RoadmapConfig


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

LINE_COLORS = ["#22D3EE", "#FF6B9D", "#FFD23F", "#34D399", "#7C3AED", "#F90001"]


def _render(config: Config) -> str:
    rcfg: RoadmapConfig = config.cards.roadmap
    height = rcfg.height
    title = rcfg.title or "Code roadmap"

    if not rcfg.lines:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
            'role="img" aria-label="Code roadmap (empty)"></svg>\n'
        )

    # Compute the global year range across all lines.
    all_years: list[int] = []
    for line in rcfg.lines:
        for s in line.stations:
            if s.year:
                all_years.append(s.year)
    if not all_years:
        # No years specified anywhere — auto-space stations evenly per line.
        year_min = 0
        year_max = 1
        auto_x = True
    else:
        year_min = min(all_years)
        year_max = max(all_years)
        if year_max == year_min:
            year_max = year_min + 1
        auto_x = False

    legend_w = 180 if rcfg.show_legend else 0
    track_left = 60 + legend_w
    track_right = WIDTH - 60
    title_h = 60
    bottom_axis_h = 36
    n_lines = len(rcfg.lines)
    available_h = height - title_h - bottom_axis_h
    line_gap = available_h / max(1, n_lines)

    def x_for_year(y: int, line_idx: int, station_idx: int, n_stations: int) -> float:
        if auto_x or not y:
            # Evenly distribute stations across the track.
            if n_stations <= 1:
                return (track_left + track_right) / 2
            return track_left + (track_right - track_left) * station_idx / (n_stations - 1)
        ratio = (y - year_min) / (year_max - year_min)
        return track_left + (track_right - track_left) * ratio

    parts: list[str] = []

    # Title.
    parts.append(
        f'<text x="{WIDTH / 2}" y="40" class="rd-title" text-anchor="middle">{_x(title)}</text>'
    )

    # Year axis at bottom (if real years).
    if not auto_x:
        ticks_y = height - 16
        parts.append(
            f'<line x1="{track_left}" y1="{ticks_y - 12}" x2="{track_right}" '
            f'y2="{ticks_y - 12}" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'
        )
        for y in range(year_min, year_max + 1):
            tx = x_for_year(y, 0, 0, 1)
            parts.append(
                f'<text x="{tx:.1f}" y="{ticks_y:.1f}" class="rd-axis" '
                f'text-anchor="middle">{y}</text>'
            )

    # Each metro line.
    for li, line in enumerate(rcfg.lines):
        color = line.color or LINE_COLORS[li % len(LINE_COLORS)]
        ly = title_h + line_gap * li + line_gap / 2
        n = len(line.stations)
        if n == 0:
            continue

        # Stroke the line as a smooth curve through its station x-positions.
        xs = [x_for_year(s.year, li, si, n) for si, s in enumerate(line.stations)]
        # Build a path: start at first station, smooth curves between.
        d = f"M {xs[0]:.1f},{ly:.1f}"
        for x in xs[1:]:
            d += f" L {x:.1f},{ly:.1f}"

        # Draw line with traveling dash highlight.
        parts.append(f"""
  <g>
    <path d="{d}" fill="none" stroke="{color}" stroke-width="6"
          stroke-linecap="round" stroke-opacity="0.92" filter="url(#rd-glow)"/>
    <path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="2"
          stroke-linecap="round" stroke-opacity="0.45"
          stroke-dasharray="3 18">
      <animate attributeName="stroke-dashoffset" from="0" to="-42"
               dur="3s" repeatCount="indefinite"/>
    </path>
  </g>""")

        # Stations.
        for si, s in enumerate(line.stations):
            sx = xs[si]
            station_circle = (
                f'<circle cx="{sx:.1f}" cy="{ly:.1f}" r="9" fill="{color}" '
                f'stroke="#FFFFFF" stroke-width="2.5" filter="url(#rd-glow)"/>'
            )
            parts.append(station_circle)
            # Alternate label position above/below to avoid overlap.
            label_y = ly - 16 if si % 2 == 0 else ly + 26
            parts.append(
                f'<text x="{sx:.1f}" y="{label_y:.1f}" class="rd-station" '
                f'text-anchor="middle">{_x(s.label)}</text>'
            )
            if s.is_current:
                # LIVE pulsating ring around the current station.
                parts.append(f"""
  <circle cx="{sx:.1f}" cy="{ly:.1f}" r="14" fill="none" stroke="{color}"
          stroke-width="2" stroke-opacity="0.8">
    <animate attributeName="r" values="14;22;14" dur="1.6s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.85;0;0.85"
             dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <text x="{sx:.1f}" y="{ly + 4:.1f}" class="rd-live" text-anchor="middle">●</text>""")

    # Legend on the left (if enabled).
    if rcfg.show_legend:
        parts.append(f'<text x="40" y="{title_h + 30}" class="rd-legend-h">LINES</text>')
        for li, line in enumerate(rcfg.lines):
            color = line.color or LINE_COLORS[li % len(LINE_COLORS)]
            ly = title_h + line_gap * li + line_gap / 2
            parts.append(
                f'<rect x="40" y="{ly - 4:.1f}" width="22" height="8" rx="3" fill="{color}"/>'
            )
            parts.append(f'<text x="68" y="{ly + 4:.1f}" class="rd-legend">{_x(line.name)}</text>')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="{_x(title)}">
  <defs>
    <filter id="rd-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.4"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .rd-title    {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 22px; letter-spacing: 0.20em; text-transform: uppercase; fill: #FFFFFF; }}
    .rd-station  {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 700; font-size: 12px; fill: #FFFFFF; fill-opacity: 0.92; }}
    .rd-axis     {{ font-family: 'JetBrains Mono','SF Mono',monospace; font-weight: 500; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.62; letter-spacing: 0.06em; }}
    .rd-legend   {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 600; font-size: 13px; fill: #FFFFFF; fill-opacity: 0.85; }}
    .rd-legend-h {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 800; font-size: 11px; letter-spacing: 0.30em; fill: #FFFFFF; fill-opacity: 0.55; }}
    .rd-live     {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 12px; fill: #FFFFFF; }}
  ]]></style>
  {"".join(parts)}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
