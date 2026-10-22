"""SVG output for graph-art. Pure SVG, so it renders inside GitHub's <img> proxy."""

from __future__ import annotations

import datetime as dt
from xml.sax.saxutils import escape

from .analysis import summarize_year
from .calendar import Calendar, date_of, year_start
from .figures import Figure

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"
BLUE, GREEN, MUTED = "#58a6ff", "#42b883", "#8b949e"
LEVELS = ["#151b26", "#5a2a16", "#8f3b1b", "#cc4f22", "#ff6a2b"]
KIND = {"quiet": ("#8b949e", True), "steady": ("#58a6ff", True), "busy": ("#ff652f", False)}


def level(n: int) -> int:
    return 0 if n == 0 else 1 if n < 5 else 2 if n < 15 else 3 if n < 30 else 4


# ── year story ──────────────────────────────────────────────────────────────
def _year_block(
    cal: Calendar, year: int, today: dt.date, y0: float, x0: int = 52, c: int = 22
) -> tuple[list[str], float]:
    s = summarize_year(cal, year, today)
    last = today if s.live else dt.date(year, 12, 31)
    start = year_start(year)

    def xy(d: dt.date) -> tuple[float, float]:
        i = (d - start).days
        return x0 + (i // 7) * c, y0 + 74 + (i % 7) * c

    o = [
        f'<text x="0" y="{y0 + 30}" font-family="{SANS}" font-size="34" font-weight="800" fill="#ffffff">{year}'
        f'<tspan font-size="20" font-weight="700" fill="{BLUE}">  {s.total:,}</tspan>'
        f'<tspan font-size="18" font-weight="400" fill="{MUTED}"> contributions</tspan>'
        + (
            f'<tspan font-family="{MONO}" font-size="14" font-weight="700" letter-spacing="2.5" fill="{GREEN}">   · LIVE</tspan>'
            if s.live
            else ""
        )
        + "</text>"
    ]
    for k, t in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(
            f'<text x="{x0 - 44}" y="{y0 + 74 + k * c + 15}" font-family="{SANS}" font-size="13" fill="{BLUE}">{t}</text>'
        )
    d = dt.date(year, 1, 1)
    while d <= last:
        x, y = xy(d)
        o.append(
            f'<rect x="{x}" y="{y}" width="{c - 4}" height="{c - 4}" rx="4" fill="{LEVELS[level(cal.count(d))]}"/>'
        )
        if d.day == 1:
            o.append(
                f'<text x="{x}" y="{y0 + 64}" font-family="{SANS}" font-size="13" fill="{BLUE}">{d:%b}</text>'
            )
        d += dt.timedelta(days=1)

    top = y0 + 74
    for n, st in enumerate(s.stretches, 1):
        col, dashed = KIND[st.kind]
        a = dt.date(year, st.first_month, 1)
        b = min(
            last,
            dt.date(year + (st.last_month == 12), st.last_month % 12 + 1, 1) - dt.timedelta(days=1),
        )
        xa, _ = xy(a - dt.timedelta(days=(a.weekday() + 1) % 7))
        xb, _ = xy(b - dt.timedelta(days=(b.weekday() + 1) % 7))
        dash = ' stroke-dasharray="6 6"' if dashed else ""
        o.append(
            f'<rect x="{xa - 4}" y="{top - 4}" width="{xb - xa + c + 4}" height="{7 * c + 4}" rx="8" fill="{col}" '
            f'fill-opacity=".05" stroke="{col}" stroke-width="2.2"{dash}/>'
        )
        cx = (xa + xb + c) / 2
        o.append(
            f'<circle cx="{cx}" cy="{top + 7 * c + 20}" r="12" fill="{col}"/>'
            f'<text x="{cx}" y="{top + 7 * c + 25}" text-anchor="middle" font-family="{SANS}" font-size="13" '
            f'font-weight="800" fill="#0d1117">{n}</text>'
        )
    if s.streak and s.streak[2] >= 3:
        d = s.streak[0]
        while d <= s.streak[1]:
            x, y = xy(d)
            o.append(
                f'<rect x="{x - 1.5}" y="{y - 1.5}" width="{c - 1}" height="{c - 1}" rx="5" fill="none" stroke="{GREEN}" stroke-width="2.2"/>'
            )
            d += dt.timedelta(days=1)
    if s.biggest_day:
        x, y = xy(s.biggest_day[0])
        o.append(
            f'<circle cx="{x + (c - 4) / 2}" cy="{y + (c - 4) / 2}" r="16" fill="none" stroke="#ffffff" stroke-width="2.4"/>'
        )

    cy = top + 7 * c + 64
    for i, st in enumerate(s.stretches):
        col, _ = KIND[st.kind]
        x, y = (i % 2) * 650, cy + (i // 2) * 56
        title = st.label + (" · still running" if st.running else "")
        o.append(
            f'<circle cx="{x + 12}" cy="{y}" r="12" fill="{col}"/>'
            f'<text x="{x + 12}" y="{y + 5}" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="800" fill="#0d1117">{i + 1}</text>'
            f'<text x="{x + 34}" y="{y + 6}" font-family="{SANS}" font-size="18" font-weight="700" fill="#ffffff">{escape(title)}</text>'
            f'<text x="{x + 34}" y="{y + 30}" font-family="{SANS}" font-size="15.5" fill="{MUTED}">{escape(st.caption())}</text>'
        )
    y = cy + ((len(s.stretches) + 1) // 2) * 56 + 10
    if s.streak and s.streak[2] >= 3:
        a, b, n = s.streak
        o.append(
            f'<rect x="0" y="{y - 13}" width="16" height="16" rx="4" fill="none" stroke="{GREEN}" stroke-width="2.2"/>'
            f'<text x="26" y="{y}" font-family="{SANS}" font-size="15.5" fill="#c9d1d9">longest streak: {n} days '
            f"({a:%b} {a.day} \u2013 {b:%b} {b.day})</text>"
        )
    if s.biggest_day:
        d, n = s.biggest_day
        o.append(
            f'<circle cx="658" cy="{y - 5}" r="8" fill="none" stroke="#ffffff" stroke-width="2.2"/>'
            f'<text x="676" y="{y}" font-family="{SANS}" font-size="15.5" fill="#c9d1d9">biggest day: '
            f"{d:%b} {d.day} ({n} contributions)</text>"
        )
    return o, y + 34 - y0


def render_year_story(
    cal: Calendar, today: dt.date | None = None, years: list[int] | None = None
) -> str:
    today = today or min(dt.date.today(), cal.last_day())
    years = sorted(years or set(cal.years()) | {today.year}, reverse=True)
    body, y, width = [], 10.0, 1300
    for i, yr in enumerate(years):
        if i:
            body.append(
                f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#21262d" stroke-width="1.5"/>'
            )
            y += 30
        part, h = _year_block(cal, yr, today, y)
        body += part
        y += h
    label = ", ".join(f"{yr}: {summarize_year(cal, yr, today).total:,}" for yr in years)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {y:.0f}" width="{width}" height="{y:.0f}" '
        f'role="img" aria-label="Contributions per year with busy and quiet stretches: {label}">'
        + "".join(body)
        + "</svg>"
    )


# ── gallery of confirmed figures ────────────────────────────────────────────
def _figure_card(
    fig: Figure, cal: Calendar, x: float, y: float, w: float, cell: int = 26
) -> tuple[str, float]:
    w0, w1 = fig.weeks
    cols = w1 - w0 + 1
    gw = cols * cell
    gx = x + (w - gw) / 2
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="10" rx="0" fill="none"/>']
    o.append(
        f'<text x="{x + 20}" y="{y + 34}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="2" fill="{MUTED}">'
        f"{fig.year} · {escape(fig.when)}</text>"
        f'<text x="{x + 20}" y="{y + 64}" font-family="{SANS}" font-size="22" font-weight="800" fill="#f0f6fc">{escape(fig.name)}</text>'
    )
    gy = y + 86
    for wk in range(w0, w1 + 1):
        for r in range(7):
            d = date_of(fig.year, wk, r)
            if d.year != fig.year:
                continue
            key = f"{wk},{r}"
            fill = fig.cells.get(key)
            if fill is None:
                fill = LEVELS[level(cal.count(d))] if cal.count(d) else "#161b22"
                op = ' opacity=".35"'
            else:
                op = ""
            o.append(
                f'<rect x="{gx + (wk - w0) * cell}" y="{gy + r * cell}" width="{cell - 4}" height="{cell - 4}" rx="5" fill="{fill}"{op}/>'
            )
    ly = gy + 7 * cell + 26
    if fig.note:
        o.append(
            f'<text x="{x + 20}" y="{ly}" font-family="{SANS}" font-size="14" fill="{MUTED}">{escape(fig.note)}</text>'
        )
        ly += 28
    lx = x + 20
    for col, lab in fig.legend:
        o.append(
            f'<rect x="{lx}" y="{ly - 12}" width="14" height="14" rx="3" fill="{col}"/>'
            f'<text x="{lx + 20}" y="{ly}" font-family="{SANS}" font-size="13" fill="#c9d1d9">{escape(lab)}</text>'
        )
        lx += 34 + len(lab) * 7.4
    h = ly + 24 - y
    frame = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#0f141b" stroke="#ffffff" stroke-opacity=".1" stroke-width="1.2"/>'
    return frame + "".join(o), h


def render_gallery(figs: list[Figure], cal: Calendar, columns: int = 2, width: int = 1400) -> str:
    gap = 24
    cw = (width - gap * (columns - 1)) / columns
    parts, y, row_h = [], 0.0, 0.0
    for i, f in enumerate(figs):
        if i and i % columns == 0:
            y += row_h + gap
            row_h = 0.0
        card, h = _figure_card(f, cal, (i % columns) * (cw + gap), y, cw)
        parts.append(card)
        row_h = max(row_h, h)
    total = y + row_h + 2
    names = ", ".join(f.name for f in figs)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total:.0f}" width="{width}" height="{total:.0f}" '
        f'role="img" aria-label="Shapes found in a real contribution graph: {escape(names)}">'
        + "".join(parts)
        + "</svg>"
    )
