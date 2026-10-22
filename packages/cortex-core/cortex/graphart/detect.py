"""Find shapes hiding in a contribution graph.

Two detectors, both deterministic and free to run:

* faces   - small empty pockets surrounded by active days read as eyes. Two
            of them side by side inside a dense patch make a face candidate.
* templates - small pixel-art masks (# = active, . = empty, ? = any) slid
            across the grid and scored by how many defined cells agree.

Detectors only suggest. A person confirms, renames or edits a candidate
(``figures.json``), which is where the real reading of the drawing happens.
"""

from __future__ import annotations

from dataclasses import dataclass

from .calendar import Calendar
from .figures import Figure, month_span

BODY, EYE = "#e6edf3", "#F90001"

TEMPLATES: dict[str, list[str]] = {
    "Heart": [
        ".##.##.",
        "#######",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    "Space invader": [
        "..#...#..",
        "...#.#...",
        "..#####..",
        ".##.#.##.",
        "#########",
        "#.#####.#",
        "#.#...#.#",
    ],
    "Plus": [
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
    ],
}


@dataclass
class Grid:
    year: int
    active: list[list[bool | None]]  # [row][week]; None = outside the year

    @classmethod
    def of(cls, cal: Calendar, year: int) -> Grid:
        g = cal.grid(year)
        return cls(year, [[None if v is None else v > 0 for v in row] for row in g])

    def at(self, w: int, r: int) -> bool | None:
        if 0 <= r < 7 and 0 <= w < 53:
            return self.active[r][w]
        return None


def _holes(g: Grid, max_size: int = 3) -> list[list[tuple[int, int]]]:
    """Small empty pockets mostly surrounded by active days."""
    seen: set[tuple[int, int]] = set()
    out = []
    for r in range(7):
        for w in range(53):
            if g.at(w, r) is not False or (w, r) in seen:
                continue
            comp, stack = [], [(w, r)]
            seen.add((w, r))
            while stack:
                cw, cr = stack.pop()
                comp.append((cw, cr))
                for dw, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (cw + dw, cr + dr)
                    if n not in seen and g.at(*n) is False:
                        seen.add(n)
                        stack.append(n)
            if len(comp) > max_size:
                continue
            ring, act = 0, 0
            cs = set(comp)
            for cw, cr in comp:
                for dw in (-1, 0, 1):
                    for dr in (-1, 0, 1):
                        n = (cw + dw, cr + dr)
                        if n in cs or not 0 <= n[1] < 7:
                            continue  # rows beyond the grid edge don't count
                        ring += 1
                        act += g.at(*n) is True
            if ring and act / ring >= 0.75:
                out.append(comp)
    return out


def find_faces(cal: Calendar, year: int) -> list[Figure]:
    g = Grid.of(cal, year)
    holes = _holes(g)
    figs = []
    for i, a in enumerate(holes):
        for b in holes[i + 1 :]:
            ar = sum(r for _, r in a) / len(a)
            br = sum(r for _, r in b) / len(b)
            aw = sum(w for w, _ in a) / len(a)
            bw = sum(w for w, _ in b) / len(b)
            if abs(ar - br) > 1 or not 2 <= abs(aw - bw) <= 5:
                continue
            if (ar + br) / 2 > 3.5:  # eyes sit in the upper half of a face
                continue
            w0 = int(min(aw, bw)) - 2
            w1 = int(max(aw, bw)) + 2
            box = [(w, r) for w in range(w0, w1 + 1) for r in range(7) if g.at(w, r) is not None]
            dens = sum(1 for c in box if g.at(*c)) / max(1, len(box))
            if dens < 0.55:
                continue
            eyes = {f"{w},{r}" for w, r in a + b}
            cells = {f"{w},{r}": BODY for w, r in box if g.at(w, r)}
            cells.update({k: EYE for k in eyes})
            figs.append(
                Figure(
                    year=year,
                    name="A face",
                    weeks=(w0, w1),
                    cells=cells,
                    holes=sorted(eyes),
                    when=month_span(year, max(w0, 0), min(w1, 52)),
                    note="two empty days surrounded by busy ones read as eyes",
                    legend=[(BODY, "face"), (EYE, "eyes")],
                    source="holes",
                    score=round(dens, 2),
                )
            )
    return figs


def find_templates(cal: Calendar, year: int, threshold: float = 0.86) -> list[Figure]:
    g = Grid.of(cal, year)
    figs = []
    for name, rows in TEMPLATES.items():
        h, w = len(rows), len(rows[0])
        for top in range(0, 7 - h + 1):
            for left in range(0, 53 - w + 1):
                defined = hit = 0
                cells: dict[str, str] = {}
                holes = []
                for dr, line in enumerate(rows):
                    for dw, ch in enumerate(line):
                        if ch == "?":
                            continue
                        v = g.at(left + dw, top + dr)
                        if v is None:
                            defined = -1
                            break
                        defined += 1
                        want = ch == "#"
                        hit += v == want
                        if want and v:
                            cells[f"{left + dw},{top + dr}"] = BODY
                    if defined < 0:
                        break
                if defined <= 0 or hit / defined < threshold:
                    continue
                figs.append(
                    Figure(
                        year=year,
                        name=f"A {name.lower()}",
                        weeks=(left, left + w - 1),
                        cells=cells,
                        holes=holes,
                        when=month_span(year, left, left + w - 1),
                        note=f"matches the {name.lower()} shape",
                        legend=[(BODY, name.lower())],
                        source=f"template:{name}",
                        score=round(hit / defined, 2),
                    )
                )
    return figs


def _overlap(a: Figure, b: Figure) -> float:
    lo, hi = max(a.weeks[0], b.weeks[0]), min(a.weeks[1], b.weeks[1])
    if hi < lo:
        return 0.0
    return (hi - lo + 1) / min(a.weeks[1] - a.weeks[0] + 1, b.weeks[1] - b.weeks[0] + 1)


def detect(cal: Calendar, years: list[int] | None = None, limit_per_year: int = 4) -> list[Figure]:
    """Candidate figures for every year, best first, without overlapping each other."""
    out: list[Figure] = []
    for y in years or cal.years():
        cands = sorted(
            find_faces(cal, y) + find_templates(cal, y), key=lambda f: f.score or 0, reverse=True
        )
        kept: list[Figure] = []
        for c in cands:
            if all(_overlap(c, k) < 0.5 for k in kept):
                kept.append(c)
            if len(kept) == limit_per_year:
                break
        out += kept
    return out
