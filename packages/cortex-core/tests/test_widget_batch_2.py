"""Smoke + behavior tests for the seven Tier-1 + Tier-2 widgets."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from cortex.builders import (
    cubes,
    galaxy,
    heatmap,
    radar,
    roadmap,
    synthwave,
    trophies,
)
from cortex.schema import (
    Brand,
    Cards,
    Config,
    CubesConfig,
    GalaxyConfig,
    HeatmapConfig,
    Identity,
    MetroLine,
    MetroStation,
    RadarAxis,
    RadarConfig,
    RoadmapConfig,
    StarSpec,
    StatCube,
    SynthwaveConfig,
    TrophiesConfig,
    TrophySpec,
)


def _make_config(**cards_overrides: object) -> Config:
    return Config(
        identity=Identity(name="Test User", github_user="test"),
        brand=Brand(palette="neon-rainbow"),
        cards=Cards(**cards_overrides),  # type: ignore[arg-type]
    )


def _assert_well_formed(svg_path: Path) -> ET.Element:
    return ET.parse(svg_path).getroot()


# ─── Synthwave ──────────────────────────────────────────────────────────


def test_synthwave_builds_well_formed_xml(tmp_path: Path):
    cfg = _make_config(synthwave=SynthwaveConfig(enabled=True, title="Hi"))
    out = synthwave.build(cfg, tmp_path / "sw.svg")
    _assert_well_formed(out)


def test_synthwave_renders_title_and_subtitle(tmp_path: Path):
    cfg = _make_config(synthwave=SynthwaveConfig(enabled=True, title="HELLO", subtitle="hi there"))
    text = synthwave.build(cfg, tmp_path / "sw.svg").read_text(encoding="utf-8")
    assert ">HELLO<" in text
    assert ">hi there<" in text


def test_synthwave_palette_changes_gradient(tmp_path: Path):
    """Each palette uses different colors — the SVG output should reflect that."""
    cfg_outrun = _make_config(synthwave=SynthwaveConfig(enabled=True, palette="outrun"))
    cfg_neon = _make_config(synthwave=SynthwaveConfig(enabled=True, palette="neon"))
    a = synthwave.build(cfg_outrun, tmp_path / "a.svg").read_text(encoding="utf-8")
    b = synthwave.build(cfg_neon, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a != b


def test_synthwave_can_disable_mountains_and_sun(tmp_path: Path):
    cfg = _make_config(
        synthwave=SynthwaveConfig(enabled=True, show_sun=False, show_mountains=False)
    )
    text = synthwave.build(cfg, tmp_path / "sw.svg").read_text(encoding="utf-8")
    # The sun circle references url(#sw-sun); only present when show_sun=true.
    assert "url(#sw-sun)" not in text


# ─── Skill Galaxy ───────────────────────────────────────────────────────


def test_galaxy_empty_stars_returns_placeholder(tmp_path: Path):
    cfg = _make_config(galaxy=GalaxyConfig(enabled=True, stars=[]))
    text = galaxy.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    assert "Skill galaxy (empty)" in text


def test_galaxy_renders_each_star_label(tmp_path: Path):
    cfg = _make_config(
        galaxy=GalaxyConfig(
            enabled=True,
            stars=[StarSpec(label="Python"), StarSpec(label="Rust")],
        )
    )
    text = galaxy.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    assert ">Python<" in text
    assert ">Rust<" in text


def test_galaxy_layout_is_deterministic_for_same_name(tmp_path: Path):
    """Same identity + stars should produce identical SVGs across runs."""
    stars = [StarSpec(label=f"S{i}") for i in range(5)]
    cfg = _make_config(galaxy=GalaxyConfig(enabled=True, stars=stars))
    a = galaxy.build(cfg, tmp_path / "a.svg").read_text(encoding="utf-8")
    b = galaxy.build(cfg, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a == b


def test_galaxy_connections_only_render_when_both_endpoints_exist(tmp_path: Path):
    cfg = _make_config(
        galaxy=GalaxyConfig(
            enabled=True,
            stars=[StarSpec(label="A"), StarSpec(label="B")],
            connections=[["A", "B"], ["A", "MISSING"]],
        )
    )
    text = galaxy.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    # Should have exactly 1 connection line (A-B), since A-MISSING is dropped.
    assert text.count("<line x1=") >= 1
    # MISSING was never placed, so it shouldn't appear as a labelled star.
    assert ">MISSING<" not in text


@pytest.mark.parametrize("bg", ["deep-space", "nebula", "void"])
def test_galaxy_all_backgrounds_render(tmp_path: Path, bg: str):
    cfg = _make_config(
        galaxy=GalaxyConfig(enabled=True, background=bg, stars=[StarSpec(label="X")])  # type: ignore[arg-type]
    )
    out = galaxy.build(cfg, tmp_path / f"{bg}.svg")
    _assert_well_formed(out)


# ─── Skill Radar ────────────────────────────────────────────────────────


def test_radar_empty_axes_placeholder(tmp_path: Path):
    cfg = _make_config(radar=RadarConfig(enabled=True, axes=[]))
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert "Skill radar (empty)" in text


def test_radar_renders_axis_labels(tmp_path: Path):
    cfg = _make_config(
        radar=RadarConfig(
            enabled=True,
            axes=[
                RadarAxis(label="Backend", value=80),
                RadarAxis(label="Frontend", value=60),
                RadarAxis(label="DevOps", value=70),
            ],
        )
    )
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert ">Backend<" in text
    assert ">Frontend<" in text
    assert ">DevOps<" in text


def test_radar_breathe_off_skips_animation(tmp_path: Path):
    cfg = _make_config(
        radar=RadarConfig(
            enabled=True,
            breathe=False,
            axes=[RadarAxis(label="X", value=50), RadarAxis(label="Y", value=50)],
        )
    )
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert "animateTransform" not in text


def test_radar_explicit_color_used(tmp_path: Path):
    cfg = _make_config(
        radar=RadarConfig(
            enabled=True,
            color="#FF00FF",
            axes=[RadarAxis(label="X", value=50), RadarAxis(label="Y", value=50)],
        )
    )
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert "#FF00FF" in text


# ─── Code Roadmap ───────────────────────────────────────────────────────


def test_roadmap_empty_lines_placeholder(tmp_path: Path):
    cfg = _make_config(roadmap=RoadmapConfig(enabled=True, lines=[]))
    text = roadmap.build(cfg, tmp_path / "rm.svg").read_text(encoding="utf-8")
    assert "Code roadmap (empty)" in text


def test_roadmap_renders_line_names_when_legend_on(tmp_path: Path):
    cfg = _make_config(
        roadmap=RoadmapConfig(
            enabled=True,
            show_legend=True,
            lines=[
                MetroLine(
                    name="Backend",
                    stations=[MetroStation(label="Django", year=2020)],
                ),
                MetroLine(
                    name="Frontend",
                    stations=[MetroStation(label="React", year=2022)],
                ),
            ],
        )
    )
    text = roadmap.build(cfg, tmp_path / "rm.svg").read_text(encoding="utf-8")
    assert ">Backend<" in text
    assert ">Frontend<" in text


def test_roadmap_current_station_gets_pulse_animation(tmp_path: Path):
    cfg = _make_config(
        roadmap=RoadmapConfig(
            enabled=True,
            lines=[
                MetroLine(
                    name="L",
                    stations=[MetroStation(label="Now", year=2026, is_current=True)],
                )
            ],
        )
    )
    text = roadmap.build(cfg, tmp_path / "rm.svg").read_text(encoding="utf-8")
    # The current station gets a radius-pulsing animate.
    assert 'attributeName="r"' in text


# ─── Activity Heatmap ───────────────────────────────────────────────────


def test_heatmap_default_uses_mock_data(tmp_path: Path):
    cfg = _make_config(heatmap=HeatmapConfig(enabled=True))
    out = heatmap.build(cfg, tmp_path / "h.svg")
    text = out.read_text(encoding="utf-8")
    # 7 days x 52 weeks = 364 cells.
    assert text.count("<rect ") >= 360


def test_heatmap_explicit_data_takes_precedence(tmp_path: Path):
    """If a user passes a 7x52 matrix, it overrides the mock generator."""
    data = [[i % 5 for i in range(52)] for _ in range(7)]
    cfg = _make_config(heatmap=HeatmapConfig(enabled=True, data=data))
    out = heatmap.build(cfg, tmp_path / "h.svg")
    _assert_well_formed(out)


def test_heatmap_invalid_dimensions_falls_back_to_mock(tmp_path: Path):
    """Wrong-shape data should not crash — fall back to deterministic mock."""
    bad_data = [[0, 1, 2]]  # only 1 row, 3 cols, totally wrong shape.
    cfg = _make_config(heatmap=HeatmapConfig(enabled=True, data=bad_data))
    out = heatmap.build(cfg, tmp_path / "h.svg")
    _assert_well_formed(out)


def test_heatmap_glow_off_omits_filter(tmp_path: Path):
    cfg = _make_config(heatmap=HeatmapConfig(enabled=True, glow=False))
    text = heatmap.build(cfg, tmp_path / "h.svg").read_text(encoding="utf-8")
    assert 'filter="url(#hm-glow)"' not in text


def test_heatmap_mock_data_is_deterministic_per_name(tmp_path: Path):
    cfg = _make_config(heatmap=HeatmapConfig(enabled=True))
    a = heatmap.build(cfg, tmp_path / "a.svg").read_text(encoding="utf-8")
    b = heatmap.build(cfg, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a == b


# ─── 3D Stat Cubes ──────────────────────────────────────────────────────


def test_cubes_empty_placeholder(tmp_path: Path):
    cfg = _make_config(cubes=CubesConfig(enabled=True, cubes=[]))
    text = cubes.build(cfg, tmp_path / "c.svg").read_text(encoding="utf-8")
    assert "Stat cubes (empty)" in text


def test_cubes_renders_label_and_value(tmp_path: Path):
    cfg = _make_config(
        cubes=CubesConfig(
            enabled=True,
            cubes=[StatCube(label="PRs", value="1.2k")],
        )
    )
    text = cubes.build(cfg, tmp_path / "c.svg").read_text(encoding="utf-8")
    assert ">PRs<" in text
    assert ">1.2k<" in text


def test_cubes_orbit_off_skips_animation(tmp_path: Path):
    cfg = _make_config(
        cubes=CubesConfig(
            enabled=True,
            orbit=False,
            cubes=[StatCube(label="X", value="1")],
        )
    )
    text = cubes.build(cfg, tmp_path / "c.svg").read_text(encoding="utf-8")
    assert "animateTransform" not in text


# ─── Achievement Wall ───────────────────────────────────────────────────


def test_trophies_empty_placeholder(tmp_path: Path):
    cfg = _make_config(trophies=TrophiesConfig(enabled=True, trophies=[]))
    text = trophies.build(cfg, tmp_path / "t.svg").read_text(encoding="utf-8")
    assert "Trophy cabinet (empty)" in text


def test_trophies_renders_each_label_date_and_glyph(tmp_path: Path):
    cfg = _make_config(
        trophies=TrophiesConfig(
            enabled=True,
            title="My Wall",
            trophies=[
                TrophySpec(label="First PR", date="2018", glyph="★"),
                TrophySpec(label="1k Commits", date="2020", glyph="🔥"),
            ],
        )
    )
    text = trophies.build(cfg, tmp_path / "t.svg").read_text(encoding="utf-8")
    assert ">My Wall<" in text
    assert ">First PR<" in text
    assert ">2018<" in text
    assert ">1k Commits<" in text
    assert "★" in text


def test_trophies_columns_layout(tmp_path: Path):
    """4 trophies with columns=2 should produce 2 rows."""
    cfg = _make_config(
        trophies=TrophiesConfig(
            enabled=True,
            columns=2,
            trophies=[TrophySpec(label=f"T{i}") for i in range(4)],
        )
    )
    out = trophies.build(cfg, tmp_path / "t.svg")
    _assert_well_formed(out)
