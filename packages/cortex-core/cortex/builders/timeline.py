"""Yearly-highlights timeline builder.

Renders a horizontal career timeline with N year-marker circles connected by a
flowing gradient line, plus N tall cards below — one per year — each with a
breathing border, a headline, bullets, and stats.

Auto-extends each year:
  • The user supplies a `cards.yearly_highlights.years` list with per-year
    metadata (label, headline, bullets, stats).
  • If empty, we generate placeholder entries from `start_year` → current year
    so the page is never blank for first-time users.
  • The current calendar year always gets the gold accent + a pulsing LIVE badge.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, StatEntry, YearEntry


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


# Per-position accent colors — index 0 is oldest, last is current/most recent.
# Matches the reference layout (purple → red → orange → gold).
_DEFAULT_ACCENTS = ["#A78BFA", "#F90001", "#FF652F", "#22D3EE", "#34D399", "#FFD23F"]
_GOLD = "#FFD23F"

_DEFAULT_LABELS_BY_INDEX = {
    0: "ORIGIN",
    1: "FOUNDATION",
    2: "GROWTH",
}
_DEFAULT_HEADLINE_BY_INDEX = {
    0: "First Steps",
    1: "A Year of Shipping",
    2: "Production & Growth",
}


def _resolve_entries(config: Config) -> list[YearEntry]:
    """Return a fully-populated list of year entries — explicit or generated."""
    yh = config.cards.yearly_highlights
    if yh.years:
        # User supplied entries — sort oldest → newest, cap at 6.
        return sorted(yh.years, key=lambda y: y.year)[:6]

    # Generate placeholder entries from start_year → today.
    today_year = date.today().year
    if yh.start_year > today_year:
        return []
    n = min(today_year - yh.start_year + 1, 6)
    out: list[YearEntry] = []
    for i in range(n):
        year = yh.start_year + i
        is_current = year == today_year
        out.append(
            YearEntry(
                year=year,
                label="CURRENT YEAR"
                if is_current
                else _DEFAULT_LABELS_BY_INDEX.get(i, "MILESTONE"),
                headline=_DEFAULT_HEADLINE_BY_INDEX.get(i, "Continuing the Journey"),
                bullets=[
                    "Configure cards.yearly_highlights.years in cortex.yml",
                    "to fill this card with your own highlights.",
                    "See examples/extreme.yml for the full schema.",
                ],
                stats=[],
            )
        )
    return out


def _accent_for(index: int, n: int, is_current: bool) -> str:
    """The current year is always gold; otherwise pick from the palette by position."""
    if is_current:
        return _GOLD
    # Reserve gold for current — give other slots the next best palette entry.
    palette = [c for c in _DEFAULT_ACCENTS if c != _GOLD]
    return palette[index % len(palette)]


def _wrap_bullet(text: str, max_chars: int = 36) -> list[str]:
    """Greedy word-wrap for bullet body text. Caps at 3 visual lines."""
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


def _render_marker(
    x: int, y: int, year: int, color: str, anim_delay_s: float, *, with_live: bool
) -> str:
    """One big circle with the 2-digit year inside, optionally with a LIVE badge."""
    yy = f"'{year % 100:02d}"
    parts = [
        f'  <g transform="translate({x},{y})">',
        '    <circle r="34" fill="url(#markerGlow)"/>',
        f'    <circle r="24" fill="#0D1117" stroke="{color}" stroke-width="2" class="marker-pulse" style="animation-delay:{anim_delay_s:.1f}s"/>',
        f'    <text x="0" y="6" class="t-year" fill="{color}" text-anchor="middle">{_x(yy)}</text>',
    ]
    if with_live:
        parts += [
            '    <g transform="translate(60, 0)" class="live-pulse">',
            f'      <rect x="0" y="-12" width="60" height="22" rx="11" fill="{color}"/>',
            '      <circle cx="11" cy="-1" r="3.5" fill="#0D1117"/>',
            '      <text x="40" y="3" class="t-year-tag" fill="#0D1117" text-anchor="middle" font-weight="700">LIVE</text>',
            "    </g>",
        ]
    parts.append("  </g>")
    return "\n".join(parts)


def _render_card(
    card_x: int,
    card_w: int,
    marker_x: int,
    entry: YearEntry,
    color: str,
    fade_class: str,
    *,
    is_current: bool,
) -> str:
    """Tall year card with breathing border, headline, bullets, and stats."""
    # Connector line from card top → timeline marker
    rel_marker_x = marker_x - card_x

    label = entry.label or ("CURRENT YEAR" if is_current else "MILESTONE")
    headline = entry.headline or f"{entry.year}"

    # Compose bullets — wrap each into up to 3 lines, total 3 bullets per card.
    bullets = entry.bullets[:3]
    bullet_blocks: list[tuple[int, list[str]]] = []  # (start_y, wrapped lines)
    y_cursor = 144
    for body in bullets:
        wrapped = _wrap_bullet(body, max_chars=34)
        bullet_blocks.append((y_cursor, wrapped))
        y_cursor += 20 * len(wrapped) + 18  # 20px line height + 18px gap

    # Stats default if not supplied
    stats = list(entry.stats)[:3]
    if not stats:
        stats = [
            StatEntry(num="—", label="STATS"),
            StatEntry(num="—", label="COMING"),
            StatEntry(num="—", label="SOON"),
        ]

    parts = [
        f'  <g transform="translate({card_x}, 230)" class="card-rise {fade_class}">',
        f'    <line x1="{rel_marker_x}" y1="0" x2="{rel_marker_x}" y2="-60" stroke="{color}" stroke-width="1" stroke-opacity="0.5"/>',
        f'    <rect x="0" y="0" width="{card_w}" height="460" rx="16" fill="url(#cardBg)" filter="url(#cardShadow)"/>',
        f'    <rect x="0" y="0" width="{card_w}" height="460" rx="16" fill="none" stroke="{color}" stroke-width="2" class="breathe-border"/>',
        f'    <text x="24" y="42" class="t-year-tag" fill="{color}">{_x(f"{entry.year} · {label}")}</text>',
        f'    <text x="24" y="84" class="t-headline">{_x(headline)}</text>',
        f'    <line x1="24" y1="108" x2="{card_w - 24}" y2="108" stroke="#21262D" stroke-width="1"/>',
    ]

    for start_y, lines in bullet_blocks:
        parts.append(f'    <text x="24"  y="{start_y}" class="t-bullet" fill="{color}">▸</text>')
        for li, line in enumerate(lines):
            parts.append(
                f'    <text x="48"  y="{start_y + li * 20}" class="t-highlight">{_x(line)}</text>'
            )

    parts.append(
        f'    <line x1="24" y1="388" x2="{card_w - 24}" y2="388" stroke="#21262D" stroke-width="1"/>'
    )

    # Stats row — 3 columns evenly spread inside card width
    stat_x_step = (card_w - 48) // 3
    for i, stat in enumerate(stats[:3]):
        sx = 24 + i * stat_x_step
        parts.append(
            f'    <text x="{sx}"  y="422" class="t-stat-num" fill="{color}">{_x(stat.num)}</text>'
        )
        parts.append(f'    <text x="{sx}"  y="444" class="t-stat-lbl">{_x(stat.label)}</text>')

    parts.append("  </g>")
    return "\n".join(parts)


def build(config: Config, output: str | Path) -> Path:
    """Emit assets/yearly-highlights.svg from cards.yearly_highlights.years."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    entries = _resolve_entries(config)
    if not entries:
        # Empty timeline — emit a tiny placeholder SVG instead of failing.
        out.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="120" viewBox="0 0 800 120">'
            '<text x="400" y="60" font-family="Inter,sans-serif" fill="#9BA1A6" text-anchor="middle">'
            "Configure cards.yearly_highlights to populate the timeline."
            "</text></svg>\n",
            encoding="utf-8",
        )
        return out

    n = len(entries)
    today_year = date.today().year
    is_current = [e.year == today_year for e in entries]

    # Layout: card width 320, gap 20px → SVG width = 340 * n + 20
    card_w = 320
    gap = 20
    side_pad = 20
    svg_w = side_pad * 2 + n * card_w + (n - 1) * gap
    svg_h = 760

    # Marker x = center of each card; timeline line spans first→last marker
    card_xs = [side_pad + i * (card_w + gap) for i in range(n)]
    marker_xs = [cx + card_w // 2 for cx in card_xs]
    line_x1 = marker_xs[0] - 40
    line_x2 = marker_xs[-1] + 40

    # Title in middle
    span_label = f"{entries[0].year} — {entries[-1].year}"

    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" '
        f'role="img" aria-label="{_x(f"Career timeline {span_label}")}">\n'
        "  <style>\n"
        "    .t-display     { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 36px; letter-spacing: -0.01em; fill: #FFFFFF; }\n"
        "    .t-tag         { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 14px; letter-spacing: 0.30em; text-transform: uppercase; fill: #C4B5FD; }\n"
        "    .t-year        { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 800; font-size: 26px; letter-spacing: -0.04em; }\n"
        "    .t-year-tag    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; }\n"
        "    .t-headline    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 800; font-size: 26px; letter-spacing: -0.01em; fill: #FFFFFF; }\n"
        "    .t-highlight   { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 500; font-size: 15px; fill: #E8E8E8; }\n"
        "    .t-bullet      { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 700; font-size: 17px; }\n"
        "    .t-stat-num    { font-family: 'JetBrains Mono','SF Mono',Consolas,monospace; font-weight: 700; font-size: 22px; }\n"
        "    .t-stat-lbl    { font-family: 'Inter','SF Pro Display','Segoe UI',sans-serif; font-weight: 700; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; fill: #8B95A1; }\n"
        "    .timeline-pulse { stroke-dasharray: 4 8; animation: tlflow 3s linear infinite; }\n"
        "    @keyframes tlflow { to { stroke-dashoffset: -36; } }\n"
        "    .marker-pulse { animation: markerPulse 2s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }\n"
        "    @keyframes markerPulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.10); opacity: 0.85; } }\n"
        "    .live-pulse { animation: livePulse 1.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }\n"
        "    @keyframes livePulse { 0%, 100% { transform: scale(1); filter: drop-shadow(0 0 4px rgba(255,210,63,0.6)); } 50% { transform: scale(1.06); filter: drop-shadow(0 0 14px rgba(255,210,63,1)); } }\n"
        "    .card-rise { opacity: 0; animation: cardRise 0.9s cubic-bezier(0.22,1,0.36,1) forwards; }\n"
        "    @keyframes cardRise { to { opacity: 1; } }\n"
        "    .y0 { animation-delay: 0.30s; } .y1 { animation-delay: 0.50s; }\n"
        "    .y2 { animation-delay: 0.70s; } .y3 { animation-delay: 0.90s; }\n"
        "    .y4 { animation-delay: 1.10s; } .y5 { animation-delay: 1.30s; }\n"
        "    .breathe-border { animation: breathe 3.4s ease-in-out infinite; }\n"
        "    @keyframes breathe { 0%,100%{stroke-opacity:0.7} 50%{stroke-opacity:1} }\n"
        "  </style>\n"
        "  <defs>\n"
        '    <radialGradient id="bgRadial" cx="50%" cy="50%" r="80%"><stop offset="0%" stop-color="#0F0816"/><stop offset="100%" stop-color="#000000"/></radialGradient>\n'
        '    <pattern id="dots" x="0" y="0" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="0.8" fill="#F90001" fill-opacity="0.07"/></pattern>\n'
        '    <linearGradient id="tlGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#A78BFA"/><stop offset="33%" stop-color="#F90001"/><stop offset="66%" stop-color="#FF652F"/><stop offset="100%" stop-color="#FFD23F"/></linearGradient>\n'
        '    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1C1428" stop-opacity="0.94"/><stop offset="100%" stop-color="#0A0612" stop-opacity="0.94"/></linearGradient>\n'
        '    <radialGradient id="markerGlow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.55"/><stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>\n'
        '    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur in="SourceAlpha" stdDeviation="5"/><feOffset dx="0" dy="3" result="shadow"/><feFlood flood-color="#000000" flood-opacity="0.65"/><feComposite in2="shadow" operator="in"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>\n'
        "  </defs>\n"
        f'  <rect width="{svg_w}" height="{svg_h}" fill="url(#bgRadial)"/>\n'
        f'  <rect width="{svg_w}" height="{svg_h}" fill="url(#dots)"/>\n'
        f'  <text x="{svg_w // 2}" y="42" class="t-tag" text-anchor="middle">{_x(f"⏵ CAREER · TIMELINE · {span_label} ⏴")}</text>\n'
        f'  <text x="{svg_w // 2}" y="78" class="t-display" text-anchor="middle">Yearly Journey</text>\n'
        f'  <line x1="{line_x1}" y1="160" x2="{line_x2}" y2="160" stroke="url(#tlGrad)" stroke-width="3" stroke-opacity="0.4"/>\n'
        f'  <line x1="{line_x1}" y1="160" x2="{line_x2}" y2="160" stroke="url(#tlGrad)" stroke-width="3" class="timeline-pulse"/>\n'
    )

    markers = "\n".join(
        _render_marker(
            marker_xs[i],
            160,
            entries[i].year,
            _accent_for(i, n, is_current[i]),
            0.3 * i,
            with_live=is_current[i],
        )
        for i in range(n)
    )

    cards = "\n".join(
        _render_card(
            card_xs[i],
            card_w,
            marker_xs[i],
            entries[i],
            _accent_for(i, n, is_current[i]),
            f"y{i}",
            is_current=is_current[i],
        )
        for i in range(n)
    )

    out.write_text(head + markers + "\n" + cards + "\n</svg>\n", encoding="utf-8")
    return out
