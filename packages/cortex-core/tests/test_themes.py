"""Tests for the brand.theme propagation + reduced-motion CSS injection."""

from __future__ import annotations

from pathlib import Path

import pytest
from cortex.builders import badges, now_playing, radar
from cortex.schema import (
    BadgeItem,
    BadgesConfig,
    Brand,
    Cards,
    Config,
    Identity,
    NowPlayingConfig,
    RadarAxis,
    RadarConfig,
)
from cortex.themes import (
    DEFAULT_THEME,
    REDUCED_MOTION_CSS,
    palette_for,
    resolve_theme,
)


def _make_config(theme: str | None = None, **cards_overrides: object) -> Config:
    brand_kwargs: dict[str, object] = {}
    if theme is not None:
        brand_kwargs["theme"] = theme
    return Config(
        identity=Identity(name="Test", github_user="test"),
        brand=Brand(**brand_kwargs),  # type: ignore[arg-type]
        cards=Cards(**cards_overrides),  # type: ignore[arg-type]
    )


# ── themes.py module ────────────────────────────────────────────────────


def test_default_theme_is_outrun():
    assert DEFAULT_THEME == "outrun"


@pytest.mark.parametrize("name", ["outrun", "sunset", "midnight", "minimal", "cyberpunk", "rose"])
def test_every_theme_has_5_slots(name: str):
    p = palette_for(name)
    assert set(p.keys()) == {"primary", "secondary", "warm", "cool", "atmosphere"}
    for slot, hex_str in p.items():
        assert hex_str.startswith("#"), f"{name}.{slot} must be a hex color"
        assert len(hex_str) == 7, f"{name}.{slot} must be #RRGGBB"


def test_unknown_theme_falls_back_to_default():
    """palette_for and resolve_theme must never crash on bogus names."""
    assert palette_for("not-a-real-theme") == palette_for(DEFAULT_THEME)


def test_resolve_theme_reads_brand_theme():
    cfg = _make_config(theme="midnight")
    assert resolve_theme(cfg)["primary"] == palette_for("midnight")["primary"]


def test_resolve_theme_handles_missing_brand_attr():
    """resolve_theme on a non-Config object should still return a valid palette."""
    p = resolve_theme(object())
    assert "primary" in p


# ── REDUCED_MOTION_CSS injection ────────────────────────────────────────


def test_reduced_motion_css_uses_correct_media_query():
    assert "@media (prefers-reduced-motion: reduce)" in REDUCED_MOTION_CSS
    assert "animation: none" in REDUCED_MOTION_CSS


def test_badges_svg_contains_reduced_motion_block(tmp_path: Path):
    cfg = _make_config(badges=BadgesConfig(enabled=True, items=[BadgeItem(label="X")]))
    text = badges.build(cfg, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert "@media (prefers-reduced-motion: reduce)" in text


def test_radar_svg_contains_reduced_motion_block(tmp_path: Path):
    cfg = _make_config(radar=RadarConfig(enabled=True, axes=[RadarAxis(label="X", value=50)]))
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert "@media (prefers-reduced-motion: reduce)" in text


def test_now_playing_svg_contains_reduced_motion_block(tmp_path: Path):
    cfg = _make_config(now_playing=NowPlayingConfig(enabled=True))
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    assert "@media (prefers-reduced-motion: reduce)" in text


# ── Theme propagation through widgets ───────────────────────────────────


def test_radar_uses_theme_primary_when_no_explicit_color(tmp_path: Path):
    cfg = _make_config(
        theme="midnight",
        radar=RadarConfig(
            enabled=True,
            axes=[RadarAxis(label="X", value=50), RadarAxis(label="Y", value=70)],
        ),
    )
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert palette_for("midnight")["primary"].upper() in text.upper()


def test_radar_explicit_color_beats_theme(tmp_path: Path):
    cfg = _make_config(
        theme="midnight",
        radar=RadarConfig(
            enabled=True,
            color="#FF00FF",
            axes=[RadarAxis(label="X", value=50)],
        ),
    )
    text = radar.build(cfg, tmp_path / "r.svg").read_text(encoding="utf-8")
    assert "#FF00FF" in text
    # Midnight's primary should NOT appear since the explicit override wins.
    midnight_primary = palette_for("midnight")["primary"]
    assert midnight_primary not in text or text.count("#FF00FF") > text.count(midnight_primary)


def test_now_playing_uses_theme_primary(tmp_path: Path):
    cfg = _make_config(theme="cyberpunk", now_playing=NowPlayingConfig(enabled=True))
    text = now_playing.build(cfg, tmp_path / "np.svg").read_text(encoding="utf-8")
    assert palette_for("cyberpunk")["primary"].upper() in text.upper()


def test_badges_use_theme_for_unknown_icon_fallback(tmp_path: Path):
    """When icon slug is unknown, the badge falls back to theme.primary, not a hardcoded color."""
    cfg = _make_config(
        theme="rose",
        badges=BadgesConfig(
            enabled=True,
            items=[BadgeItem(label="Made-up tech", icon="not-a-real-slug")],
        ),
    )
    text = badges.build(cfg, tmp_path / "b.svg").read_text(encoding="utf-8")
    rose_primary = palette_for("rose")["primary"]
    assert rose_primary.upper() in text.upper()


def test_changing_theme_changes_output(tmp_path: Path):
    """Same config, different theme → different SVG output."""
    cfg_a = _make_config(
        theme="outrun",
        radar=RadarConfig(enabled=True, axes=[RadarAxis(label="X", value=50)]),
    )
    cfg_b = _make_config(
        theme="cyberpunk",
        radar=RadarConfig(enabled=True, axes=[RadarAxis(label="X", value=50)]),
    )
    a = radar.build(cfg_a, tmp_path / "a.svg").read_text(encoding="utf-8")
    b = radar.build(cfg_b, tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a != b
