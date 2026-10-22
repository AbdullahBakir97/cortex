"""Per-year story: stretches, streaks and peaks, written for a visitor."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from .calendar import Calendar


@dataclass
class Stretch:
    kind: str  # quiet | steady | busy
    first_month: int
    last_month: int
    contributions: int
    active_days: int
    days: int
    running: bool = False

    @property
    def label(self) -> str:
        return {"quiet": "Quiet stretch", "steady": "Steady stretch", "busy": "Busy stretch"}[
            self.kind
        ]

    @property
    def when(self) -> str:
        a = dt.date(2000, self.first_month, 1).strftime("%b")
        b = dt.date(2000, self.last_month, 1).strftime("%b")
        return a if a == b else f"{a}\u2013{b}"

    def caption(self) -> str:
        return f"{self.when}: {self.contributions:,} contributions, active {self.active_days} of {self.days} days"


@dataclass
class YearSummary:
    year: int
    total: int
    active_days: int
    months: list[int]
    best_month: int | None
    stretches: list[Stretch] = field(default_factory=list)
    streak: tuple[dt.date, dt.date, int] | None = None  # start, end, length
    biggest_day: tuple[dt.date, int] | None = None
    live: bool = False


def classify_months(months: list[int], last_month: int) -> list[list]:
    """Split months 1..last_month into at most four stretches by how busy they were."""
    peak = max([*months[:last_month], 1])

    def kind(v: int) -> str:
        return "busy" if v >= 0.45 * peak else "quiet" if v < 0.12 * peak else "steady"

    runs: list[list] = []
    for m in range(1, last_month + 1):
        k = kind(months[m - 1])
        if runs and runs[-1][0] == k:
            runs[-1][2] = m
        else:
            runs.append([k, m, m])
    rank = {"quiet": 0, "steady": 1, "busy": 2}

    def merge(i: int, j: int) -> None:
        a, b = runs[min(i, j)], runs[max(i, j)]
        keep = a[0] if (a[2] - a[1]) >= (b[2] - b[1]) else b[0]
        runs[min(i, j)] = [keep, a[1], b[2]]
        del runs[max(i, j)]

    changed = True
    while changed and len(runs) > 1:  # fold one-month blips into a neighbour
        changed = False
        for i, r in enumerate(runs):
            if r[1] == r[2] and len(runs) > 1:
                if i == 0:
                    j = 1
                elif i == len(runs) - 1:
                    j = i - 1
                else:
                    left = abs(rank[runs[i - 1][0]] - rank[r[0]])
                    right = abs(rank[runs[i + 1][0]] - rank[r[0]])
                    j = i - 1 if left <= right else i + 1
                merge(i, j)
                changed = True
                break
    while len(runs) > 4:
        i = min(range(len(runs) - 1), key=lambda i: abs(rank[runs[i][0]] - rank[runs[i + 1][0]]))
        merge(i, i + 1)
    i = 0
    while i < len(runs) - 1:  # neighbours of the same kind
        if runs[i][0] == runs[i + 1][0]:
            runs[i][2] = runs[i + 1][2]
            del runs[i + 1]
        else:
            i += 1
    return runs


def summarize_year(cal: Calendar, year: int, today: dt.date | None = None) -> YearSummary:
    today = today or cal.last_day()
    live = year == today.year
    last = today if live else dt.date(year, 12, 31)
    days = [
        dt.date(year, 1, 1) + dt.timedelta(i) for i in range((last - dt.date(year, 1, 1)).days + 1)
    ]
    val = {d: cal.count(d) for d in days}
    months = [sum(v for d, v in val.items() if d.month == m) for m in range(1, 13)]
    best = max(range(1, 13), key=lambda m: months[m - 1]) if any(months) else None

    stretches = []
    for kind, m0, m1 in classify_months(months, last.month):
        a = dt.date(year, m0, 1)
        b = min(last, dt.date(year + (m1 == 12), m1 % 12 + 1, 1) - dt.timedelta(days=1))
        span = [d for d in days if a <= d <= b]
        stretches.append(
            Stretch(
                kind,
                m0,
                m1,
                sum(val[d] for d in span),
                sum(1 for d in span if val[d]),
                len(span),
                live and b == last,
            )
        )

    run = best_len = 0
    rs = bs = be = None
    for d in days:
        if val[d]:
            run += 1
            rs = d if run == 1 else rs
            if run > best_len:
                best_len, bs, be = run, rs, d
        else:
            run = 0
    top = max(days, key=lambda d: val[d]) if days else None
    return YearSummary(
        year=year,
        total=sum(val.values()),
        active_days=sum(1 for v in val.values() if v),
        months=months,
        best_month=best,
        stretches=stretches,
        streak=(bs, be, best_len) if best_len else None,
        biggest_day=(top, val[top]) if top and val[top] else None,
        live=live,
    )
