"""figures.json: drawings found in a contribution graph, and the honesty check.

A figure lives in one year's grid. ``cells`` maps "week,row" to a colour.
Coloured cells must be days that really had contributions; an empty day may
only be used when it is listed in ``holes`` (an eye, a mouth, a gap). That
rule is what keeps the drawing true to the graph: nothing is drawn in.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .calendar import Calendar, date_of


@dataclass
class Figure:
    year: int
    name: str
    weeks: tuple[int, int]
    cells: dict[str, str]
    holes: list[str] = field(default_factory=list)
    when: str = ""
    note: str = ""
    legend: list[tuple[str, str]] = field(default_factory=list)
    source: str = "manual"  # manual | holes | template:<name> | ai
    score: float | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Figure:
        return cls(
            year=int(d["year"]),
            name=d.get("name", "Untitled"),
            weeks=(int(d["weeks"][0]), int(d["weeks"][1])),
            cells=dict(d.get("cells", {})),
            holes=list(d.get("holes", [])),
            when=d.get("when", ""),
            note=d.get("note", ""),
            legend=[tuple(x) for x in d.get("legend", [])],
            source=d.get("source", "manual"),
            score=d.get("score"),
        )

    def to_dict(self) -> dict:
        out = asdict(self)
        out["weeks"] = list(self.weeks)
        out["legend"] = [list(x) for x in self.legend]
        return {k: v for k, v in out.items() if v not in (None, "", [])}


def _key(key: str) -> tuple[int, int]:
    w, r = key.split(",")
    return int(w), int(r)


def validate_figure(fig: Figure, cal: Calendar) -> list[str]:
    """Problems that would make the figure untrue to the graph. Empty list = OK."""
    problems = []
    holes = set(fig.holes)
    for key in fig.cells:
        w, r = _key(key)
        if not 0 <= r <= 6:
            problems.append(f"{key}: row must be 0..6")
            continue
        day = date_of(fig.year, w, r)
        if day.year != fig.year:
            problems.append(f"{key}: {day} is outside {fig.year}")
        elif cal.count(day) == 0 and key not in holes:
            problems.append(f"{key}: {day} had no contributions; mark it as a hole or remove it")
    for key in holes:
        w, r = _key(key)
        if cal.count(date_of(fig.year, w, r)):
            problems.append(
                f"{key}: listed as a hole but {date_of(fig.year, w, r)} had contributions"
            )
    return problems


def load_figures(path: str | Path) -> list[Figure]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data["figures"] if isinstance(data, dict) else data
    return [Figure.from_dict(d) for d in items]


def save_figures(figs: list[Figure], path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(
            {"version": 1, "figures": [f.to_dict() for f in figs]}, indent=1, ensure_ascii=False
        ),
        encoding="utf-8",
    )


def month_span(year: int, w0: int, w1: int) -> str:
    a, b = date_of(year, w0, 0), date_of(year, w1, 6)
    a = max(a, dt.date(year, 1, 1))
    b = min(b, dt.date(year, 12, 31))
    return a.strftime("%b").upper() if a.month == b.month else f"{a:%b} \u2013 {b:%b}".upper()
