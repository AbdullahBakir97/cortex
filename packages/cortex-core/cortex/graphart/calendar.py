"""Daily contribution counts, plus the week/row grid GitHub draws them on."""

from __future__ import annotations

import datetime as dt
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

_TITLE_RE = re.compile(r"<title>(\d+) on (\d{4}-\d{2}-\d{2})</title>")

_YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionYears
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def year_start(year: int) -> dt.date:
    """The Sunday that opens column 0 of a year's grid (GitHub layout)."""
    jan1 = dt.date(year, 1, 1)
    return jan1 - dt.timedelta(days=(jan1.weekday() + 1) % 7)


def cell_of(day: dt.date) -> tuple[int, int]:
    """(week column, weekday row) of a date in its own year's grid. Row 0 = Sunday."""
    i = (day - year_start(day.year)).days
    return i // 7, i % 7


def date_of(year: int, week: int, row: int) -> dt.date:
    return year_start(year) + dt.timedelta(days=week * 7 + row)


@dataclass
class Calendar:
    """Daily contribution counts keyed by date."""

    days: dict[dt.date, int] = field(default_factory=dict)

    # ── loading ──────────────────────────────────────────────────────────
    @classmethod
    def from_mapping(cls, data: dict[str, int]) -> Calendar:
        return cls({dt.date.fromisoformat(k): int(v) for k, v in data.items()})

    @classmethod
    def from_json(cls, path: str | Path) -> Calendar:
        return cls.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))

    @classmethod
    def from_heatmap_svgs(cls, paths: Iterable[str | Path]) -> Calendar:
        days: dict[dt.date, int] = {}
        for p in paths:
            for n, d in _TITLE_RE.findall(Path(p).read_text(encoding="utf-8")):
                days[dt.date.fromisoformat(d)] = int(n)
        return cls(days)

    @classmethod
    def from_github(cls, client, years: Iterable[int] | None = None) -> Calendar:
        """Fetch every year (or the given years) through GraphQL. Needs a token."""
        if not getattr(client, "token", ""):
            raise RuntimeError("graph-art needs a GitHub token to read the contribution calendar")
        today = dt.date.today()
        if years is None:
            first = client.graphql(
                _YEAR_QUERY,
                {
                    "login": client.user,
                    "from": f"{today.year}-01-01T00:00:00Z",
                    "to": f"{today:%Y-%m-%d}T23:59:59Z",
                },
            )
            years = first["user"]["contributionsCollection"]["contributionYears"]
        days: dict[dt.date, int] = {}
        for y in sorted(set(years)):
            end = min(dt.date(y, 12, 31), today)
            data = client.graphql(
                _YEAR_QUERY,
                {
                    "login": client.user,
                    "from": f"{y}-01-01T00:00:00Z",
                    "to": f"{end:%Y-%m-%d}T23:59:59Z",
                },
            )
            weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            for w in weeks:
                for d in w["contributionDays"]:
                    day = dt.date.fromisoformat(d["date"])
                    if day.year == y:
                        days[day] = int(d["contributionCount"])
        return cls(days)

    # ── saving / access ──────────────────────────────────────────────────
    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps({d.isoformat(): n for d, n in sorted(self.days.items())}, indent=0),
            encoding="utf-8",
        )

    def count(self, day: dt.date) -> int:
        return self.days.get(day, 0)

    def years(self) -> list[int]:
        return sorted({d.year for d, n in self.days.items() if n > 0})

    def last_day(self) -> dt.date:
        return max(self.days) if self.days else dt.date.today()

    def grid(self, year: int) -> list[list[int | None]]:
        """7 rows x 53 weeks of counts for one year; None for days outside the year."""
        g: list[list[int | None]] = [[None] * 53 for _ in range(7)]
        d, end = dt.date(year, 1, 1), dt.date(year, 12, 31)
        while d <= end:
            w, r = cell_of(d)
            if w < 53:
                g[r][w] = self.count(d)
            d += dt.timedelta(days=1)
        return g
