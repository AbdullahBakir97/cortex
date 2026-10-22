"""graph-art: calendar, analysis, detection, honesty check and SVG output."""

from __future__ import annotations

import datetime as dt
import itertools
import json
import xml.dom.minidom

from click.testing import CliRunner
from cortex.graphart.analysis import classify_months, summarize_year
from cortex.graphart.calendar import Calendar, cell_of, date_of
from cortex.graphart.detect import TEMPLATES, detect, find_faces, find_templates
from cortex.graphart.figures import Figure, load_figures, save_figures, validate_figure
from cortex.graphart.render import render_gallery, render_year_story

YEAR = 2024


def _paint(rows: list[str], left: int, top: int = 0, count: int = 5) -> Calendar:
    """Calendar whose grid shows `rows` (# = active) starting at week `left`."""
    days = {}
    for r, line in enumerate(rows):
        for w, ch in enumerate(line):
            if ch == "#":
                d = date_of(YEAR, left + w, top + r)
                if d.year == YEAR:
                    days[d] = count
    return Calendar(days)


FACE = [
    "#######",
    "##.#.##",
    "#######",
    "#######",
    "##...##",
    "#######",
    "#######",
]


def test_cell_and_date_round_trip():
    for d in (dt.date(YEAR, 1, 1), dt.date(YEAR, 6, 15), dt.date(YEAR, 12, 31)):
        assert date_of(YEAR, *cell_of(d)) == d


def test_grid_marks_days_outside_the_year():
    g = Calendar().grid(YEAR)
    assert len(g) == 7 and len(g[0]) == 53
    jan1_w, jan1_r = cell_of(dt.date(YEAR, 1, 1))
    assert jan1_w == 0
    assert all(g[r][0] is None for r in range(jan1_r))


def test_calendar_json_round_trip(tmp_path):
    cal = _paint(FACE, 10)
    p = tmp_path / "cal.json"
    cal.to_json(p)
    assert Calendar.from_json(p).days == cal.days


def test_heatmap_svg_loader(tmp_path):
    p = tmp_path / "h.svg"
    p.write_text(
        "<svg><rect><title>4 on 2024-03-05</title></rect><rect><title>0 on 2024-03-06</title></rect></svg>"
    )
    cal = Calendar.from_heatmap_svgs([p])
    assert cal.count(dt.date(2024, 3, 5)) == 4 and cal.years() == [2024]


def test_classify_months_folds_blips_and_caps_at_four():
    runs = classify_months([1, 1, 50, 1, 1, 90, 95, 1, 1, 1, 40, 1], 12)
    assert 1 <= len(runs) <= 4
    assert runs[0][1] == 1 and runs[-1][2] == 12


def test_summary_streak_and_biggest_day():
    days = {dt.date(YEAR, 3, d): 2 for d in range(1, 11)}
    days[dt.date(YEAR, 7, 4)] = 40
    s = summarize_year(Calendar(days), YEAR, today=dt.date(YEAR, 12, 31))
    assert s.total == 60 and s.active_days == 11
    assert s.streak[2] == 10
    assert s.biggest_day == (dt.date(YEAR, 7, 4), 40)
    assert s.best_month == 7


def test_detect_finds_the_face():
    cal = _paint(FACE, 20)
    faces = find_faces(cal, YEAR)
    assert faces, "two eyes in a dense patch should be a face"
    best = max(faces, key=lambda f: f.score)
    assert {"22,1", "24,1"} <= set(best.holes)
    assert validate_figure(best, cal) == []


def test_template_match():
    cal = _paint([ln.replace(".", " ") for ln in TEMPLATES["Plus"]], 30, top=1)
    found = [f for f in find_templates(cal, YEAR) if f.source == "template:Plus"]
    assert found and found[0].weeks == (30, 34)


def test_detect_keeps_candidates_apart():
    cal = _paint(FACE, 10)
    cal.days.update(_paint(FACE, 30).days)
    figs = detect(cal)
    spans = sorted(f.weeks for f in figs)
    assert all(a[1] < b[0] for a, b in itertools.pairwise(spans))


def test_validate_rejects_drawn_in_days():
    cal = _paint(FACE, 20)
    fig = Figure(year=YEAR, name="x", weeks=(20, 26), cells={"22,1": "#f00"})
    assert validate_figure(fig, cal)  # empty day, not a hole
    fig.holes = ["22,1"]
    assert validate_figure(fig, cal) == []  # allowed as an eye
    fig.holes = ["20,0"]
    assert any("listed as a hole" in p for p in validate_figure(fig, cal))


def test_figures_file_round_trip(tmp_path):
    fig = Figure(
        year=YEAR, name="A face", weeks=(1, 4), cells={"1,1": "#fff"}, legend=[("#fff", "face")]
    )
    p = tmp_path / "f.json"
    save_figures([fig], p)
    assert load_figures(p)[0].to_dict() == fig.to_dict()


def test_svgs_are_valid_xml():
    cal = _paint(FACE, 20)
    story = render_year_story(cal, today=dt.date(YEAR, 12, 31))
    gallery = render_gallery(detect(cal), cal)
    for svg in (story, gallery):
        xml.dom.minidom.parseString(svg)
    assert "<script" not in story and "foreignObject" not in gallery


def test_cli_end_to_end(tmp_path):
    from cortex_cli.__main__ import cli

    cal = _paint(FACE, 20)
    cal_path = tmp_path / "calendar.json"
    cal.to_json(cal_path)
    r = CliRunner()
    res = r.invoke(cli, ["graph-art", "analyze", "--calendar", str(cal_path), "--json"])
    assert res.exit_code == 0, res.output
    assert json.loads(res.output)[0]["year"] == YEAR
    draft = tmp_path / "draft.json"
    assert (
        r.invoke(
            cli, ["graph-art", "detect", "--calendar", str(cal_path), "-o", str(draft)]
        ).exit_code
        == 0
    )
    assert (
        r.invoke(
            cli, ["graph-art", "check", "--calendar", str(cal_path), "-f", str(draft)]
        ).exit_code
        == 0
    )
    out = tmp_path / "out"
    res = r.invoke(
        cli, ["graph-art", "render", "--calendar", str(cal_path), "-f", str(draft), "-o", str(out)]
    )
    assert res.exit_code == 0, res.output
    assert (out / "year-story.svg").exists() and (out / "graph-art.svg").exists()
