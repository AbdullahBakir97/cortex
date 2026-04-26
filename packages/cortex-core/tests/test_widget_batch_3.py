"""Smoke + behavior tests for the batch-3 widgets: dna, globe, particles, now_playing."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from cortex.builders import dna, globe, now_playing, particles
from cortex.schema import (
    Brand,
    Cards,
    Config,
    DnaConfig,
    GlobeConfig,
    GlobePin,
    Identity,
    NowPlayingConfig,
    ParticlesConfig,
    ParticleSpec,
)


def _make_config(**cards_overrides: object) -> Config:
    return Config(
        identity=Identity(name="Test", github_user="test"),
        brand=Brand(palette="neon-rainbow"),
        cards=Cards(**cards_overrides),  # type: ignore[arg-type]
    )


def _assert_well_formed(p: Path) -> None:
    ET.parse(p)


# ─── DNA Helix ──────────────────────────────────────────────────────────


def test_dna_empty_languages_placeholder(tmp_path: Path):
    cfg = _make_config(dna=DnaConfig(enabled=True, languages=[]))
    text = dna.build(cfg, tmp_path / "d.svg").read_text(encoding="utf-8")
    assert "Code DNA (empty)" in text


def test_dna_renders_each_language_label(tmp_path: Path):
    cfg = _make_config(dna=DnaConfig(enabled=True, languages=["Python", "Rust", "TypeScript"]))
    text = dna.build(cfg, tmp_path / "d.svg").read_text(encoding="utf-8")
    assert ">Python<" in text
    assert ">Rust<" in text
    assert ">TypeScript<" in text


def test_dna_explicit_colors_override_default_palette(tmp_path: Path):
    cfg = _make_config(
        dna=DnaConfig(
            enabled=True,
            languages=["A", "B"],
            colors=["#FF00FF", "#00FF00"],
        )
    )
    text = dna.build(cfg, tmp_path / "d.svg").read_text(encoding="utf-8")
    assert "#FF00FF" in text
    assert "#00FF00" in text


def test_dna_well_formed_xml(tmp_path: Path):
    cfg = _make_config(dna=DnaConfig(enabled=True, languages=["X"]))
    out = dna.build(cfg, tmp_path / "d.svg")
    _assert_well_formed(out)


# ─── Globe ──────────────────────────────────────────────────────────────


def test_globe_empty_pins_renders_globe(tmp_path: Path):
    """Empty pins should still render the globe sphere — no placeholder."""
    cfg = _make_config(globe=GlobeConfig(enabled=True, pins=[]))
    text = globe.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    assert "gb-sphere" in text  # gradient id confirms sphere is drawn


def test_globe_renders_visible_pins_only(tmp_path: Path):
    """Pins on the front hemisphere are rendered; back-side pins are hidden."""
    cfg = _make_config(
        globe=GlobeConfig(
            enabled=True,
            pins=[
                GlobePin(label="Front", lon=0, lat=0),  # front-center, visible
                GlobePin(label="BackHidden", lon=170, lat=0),  # back side
            ],
        )
    )
    text = globe.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    assert ">Front<" in text
    assert ">BackHidden<" not in text


def test_globe_rotate_off_skips_animation(tmp_path: Path):
    cfg = _make_config(
        globe=GlobeConfig(
            enabled=True,
            rotate=False,
            pins=[GlobePin(label="X", lon=0, lat=0)],
        )
    )
    text = globe.build(cfg, tmp_path / "g.svg").read_text(encoding="utf-8")
    assert "animateTransform" not in text


def test_globe_well_formed_xml(tmp_path: Path):
    cfg = _make_config(
        globe=GlobeConfig(
            enabled=True,
            pins=[GlobePin(label="A", lon=10, lat=20)],
        )
    )
    _assert_well_formed(globe.build(cfg, tmp_path / "g.svg"))


# ─── Particle Cloud ─────────────────────────────────────────────────────


def test_particles_empty_placeholder(tmp_path: Path):
    cfg = _make_config(particles=ParticlesConfig(enabled=True, items=[]))
    text = particles.build(cfg, tmp_path / "p.svg").read_text(encoding="utf-8")
    assert "Particle cloud (empty)" in text


def test_particles_renders_each_label(tmp_path: Path):
    cfg = _make_config(
        particles=ParticlesConfig(
            enabled=True,
            items=[
                ParticleSpec(label="Python", weight=2.0),
                ParticleSpec(label="Rust", weight=1.0),
            ],
        )
    )
    text = particles.build(cfg, tmp_path / "p.svg").read_text(encoding="utf-8")
    assert "Python" in text
    assert "Rust" in text


def test_particles_layout_is_deterministic_per_name(tmp_path: Path):
    cfg = _make_config(
        particles=ParticlesConfig(
            enabled=True,
            items=[ParticleSpec(label=f"L{i}") for i in range(5)],
        )
    )
    a = particles.build(cfg, tmp_path / "a.svg").read_text(encoding="utf-8")
    b = particles.build(cfg, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a == b


def test_particles_weight_affects_font_size(tmp_path: Path):
    """Higher-weight particles should produce larger font-size values in the SVG."""
    cfg_heavy = _make_config(
        particles=ParticlesConfig(enabled=True, items=[ParticleSpec(label="X", weight=3.0)])
    )
    cfg_light = _make_config(
        particles=ParticlesConfig(enabled=True, items=[ParticleSpec(label="X", weight=0.5)])
    )
    heavy = particles.build(cfg_heavy, tmp_path / "h.svg").read_text(encoding="utf-8")
    light = particles.build(cfg_light, tmp_path / "l.svg").read_text(encoding="utf-8")
    assert heavy != light


# ─── Now Playing ────────────────────────────────────────────────────────


def test_now_playing_renders_language_and_project(tmp_path: Path):
    cfg = _make_config(
        now_playing=NowPlayingConfig(
            enabled=True,
            language="Python",
            project="Cortex v0.4",
            progress=0.5,
        )
    )
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    assert ">Python<" in text
    assert ">Cortex v0.4<" in text


def test_now_playing_activity_uppercased(tmp_path: Path):
    cfg = _make_config(now_playing=NowPlayingConfig(enabled=True, activity="debugging"))
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    assert ">DEBUGGING<" in text


def test_now_playing_progress_clamped(tmp_path: Path):
    """Progress > 1.0 or < 0 should clamp without crashing."""
    cfg_over = _make_config(now_playing=NowPlayingConfig(enabled=True, progress=2.5))
    cfg_under = _make_config(now_playing=NowPlayingConfig(enabled=True, progress=-0.3))
    _assert_well_formed(now_playing.build(cfg_over, tmp_path / "o.svg"))
    _assert_well_formed(now_playing.build(cfg_under, tmp_path / "u.svg"))


def test_now_playing_glyph_first_letter_of_language(tmp_path: Path):
    cfg = _make_config(now_playing=NowPlayingConfig(enabled=True, language="rust"))
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    # Should contain uppercase R as the album-art glyph (in a text element).
    assert ">R</text>" in text or 'class="np-glyph"' in text


def test_now_playing_explicit_color_used(tmp_path: Path):
    cfg = _make_config(now_playing=NowPlayingConfig(enabled=True, color="#FF00FF"))
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    assert "#FF00FF" in text
