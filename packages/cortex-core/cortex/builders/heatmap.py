"""Activity Heatmap — GitHub-style contribution grid with neon glow.

7 rows (days of week) x 52 columns (weeks). Each cell intensity is one of
0..4. Cells with intensity > 0 get a neon fill + glow. Optional smoothing
sweep makes the field look organic rather than blocky.
"""

from __future__ import annotations

import random as _random
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, HeatmapConfig


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

# 5 intensity levels per palette: idx 0 = empty, 4 = brightest.
PALETTES: dict[str, list[str]] = {
    "neon-green": ["#0E1A14", "#1B4332", "#2D8659", "#52B788", "#74C69D"],
    "neon-cyan": ["#0E1A24", "#1A3A52", "#2575A8", "#33A0E0", "#7DD3FC"],
    "neon-rainbow": ["#0E0820", "#7B5EAA", "#C95E8A", "#FF6B9D", "#FFD23F"],
    "rose": ["#1A0A14", "#3A1A28", "#7B2D52", "#C95E8A", "#FF6B9D"],
}


def _seed_from_name(name: str) -> int:
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h


def _generate_mock_data(weeks: int, seed: int) -> list[list[int]]:
    """Plausible activity pattern: weekdays > weekends, recent weeks busier."""
    rng = _random.Random(seed)
    grid: list[list[int]] = []
    for day in range(7):
        row = []
        for w in range(weeks):
            # Recency boost: more recent weeks have higher base rate.
            recency = w / max(1, weeks - 1)  # 0..1
            # Weekday boost: Mon(1) - Fri(5) higher; Sat/Sun(0,6) lower.
            weekday_boost = 1.4 if 1 <= day <= 5 else 0.5
            base = (0.15 + 0.55 * recency) * weekday_boost
            roll = rng.random()
            if roll < base * 0.15:
                row.append(4)
            elif roll < base * 0.35:
                row.append(3)
            elif roll < base * 0.55:
                row.append(2)
            elif roll < base * 0.85:
                row.append(1)
            else:
                row.append(0)
        grid.append(row)
    return grid


def _render(config: Config) -> str:
    hcfg: HeatmapConfig = config.cards.heatmap
    palette = PALETTES.get(hcfg.palette, PALETTES["neon-green"])
    weeks = hcfg.weeks
    height = hcfg.height

    # Cell sizing: fit `weeks` columns + 7 rows nicely inside WIDTH.
    cell_size = 16
    cell_gap = 3
    grid_w = weeks * (cell_size + cell_gap)
    grid_h = 7 * (cell_size + cell_gap)
    margin_x = (WIDTH - grid_w) / 2
    margin_y = (height - grid_h) / 2

    # Resolve the data matrix.
    data = hcfg.data
    if hcfg.from_github and not data:
        # Live-fetch real contributions. Empty result on failure falls through
        # to the mock generator below, so we always render something.
        from cortex.github_api import client_from_env
        from cortex.sources import contribution_grid_from_github

        client = client_from_env(config.identity.github_user)
        data = contribution_grid_from_github(client, weeks=weeks)
    if not data or len(data) != 7 or any(len(r) != weeks for r in data):
        seed = _seed_from_name(config.identity.name) if config.identity.name else 42
        data = _generate_mock_data(weeks, seed)

    # Render each cell as a <use> reference to a shared <symbol>.
    # The <symbol> holds the rect geometry once; per-cell <use> elements
    # only carry x / y / fill / opacity / animation. This dedupes the
    # `width="16" height="16" rx="3"` boilerplate across all 364 cells,
    # cutting the heatmap SVG size by ~30% with no visual change.
    cells: list[str] = []
    for day in range(7):
        for w in range(weeks):
            intensity = max(0, min(4, data[day][w]))
            x = margin_x + w * (cell_size + cell_gap)
            y = margin_y + day * (cell_size + cell_gap)
            color = palette[intensity]
            target_opacity = 0.35 if intensity == 0 else 1.0
            filter_attr = ' filter="url(#hm-glow)"' if (hcfg.glow and intensity >= 2) else ""
            # Animated cells stagger across columns; static cells render at
            # their target opacity directly (no animate child needed).
            if intensity > 0:
                cells.append(
                    f'<use href="#hm-cell" x="{x:.1f}" y="{y:.1f}" fill="{color}" '
                    f'opacity="0"{filter_attr}>'
                    f'<animate attributeName="opacity" from="0" to="{target_opacity:.2f}" '
                    f'begin="{w * 0.012:.2f}s" dur="0.4s" fill="freeze"/>'
                    f"</use>"
                )
            else:
                cells.append(
                    f'<use href="#hm-cell" x="{x:.1f}" y="{y:.1f}" fill="{color}" '
                    f'opacity="{target_opacity:.2f}"/>'
                )

    # Day labels (left side) — Mon, Wed, Fri only to avoid clutter.
    day_labels = []
    for day, label in enumerate(["", "Mon", "", "Wed", "", "Fri", ""]):
        if not label:
            continue
        ly = margin_y + day * (cell_size + cell_gap) + cell_size - 4
        day_labels.append(
            f'<text x="{margin_x - 12:.1f}" y="{ly:.1f}" class="hm-axis" '
            f'text-anchor="end">{label}</text>'
        )

    # Month markers (top) — every ~4 weeks.
    month_markers = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for mi, m in enumerate(months):
        col = int(mi * weeks / 12)
        mx = margin_x + col * (cell_size + cell_gap)
        if mx + 30 < WIDTH - margin_x:
            month_markers.append(
                f'<text x="{mx:.1f}" y="{margin_y - 12:.1f}" class="hm-axis">{m}</text>'
            )

    # Legend in bottom right.
    legend_x = WIDTH - margin_x - 5 * (cell_size + 2) - 60
    legend_y = margin_y + grid_h + 18
    legend = (
        f'<text x="{legend_x - 6:.1f}" y="{legend_y + 12:.1f}" '
        f'class="hm-axis" text-anchor="end">Less</text>'
    )
    for i, c in enumerate(palette):
        legend += (
            f'<use href="#hm-cell" x="{legend_x + i * (cell_size + 2):.1f}" '
            f'y="{legend_y:.1f}" fill="{c}" '
            f'opacity="{0.5 if i == 0 else 1.0}"/>'
        )
    legend += (
        f'<text x="{legend_x + 5 * (cell_size + 2) + 6:.1f}" '
        f'y="{legend_y + 12:.1f}" class="hm-axis">More</text>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="Activity heatmap">
  <defs>
    <symbol id="hm-cell" overflow="visible">
      <rect width="{cell_size}" height="{cell_size}" rx="3"/>
    </symbol>
    <filter id="hm-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.4"/>
      <feComponentTransfer><feFuncA type="linear" slope="1.7"/></feComponentTransfer>
    </filter>
  </defs>
  <style><![CDATA[
    .hm-axis {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 500; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.55; letter-spacing: 0.06em; }}
  ]]></style>
  {chr(10).join(month_markers)}
  {chr(10).join(day_labels)}
  {chr(10).join(cells)}
  {legend}
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
