"""Unit tests for the badges builder and icon library."""

from __future__ import annotations

from pathlib import Path

import pytest
from cortex.builders.badges import (
    BADGE_GAP,
    BADGE_H,
    BADGE_W,
    SVG_WIDTH,
    _layout_positions,
    _resolve,
    _shape_path,
    build,
)
from cortex.icons import KNOWN_ICONS, derive_monogram, lookup
from cortex.schema import BadgeItem, BadgesConfig, Brand, Cards, Config, Identity

# ── Helpers ──────────────────────────────────────────────────────────────


def _config_with_badges(items: list[BadgeItem], **kwargs: object) -> Config:
    """Build a minimal Config with the badges widget configured."""
    badges = BadgesConfig(enabled=True, items=items, **kwargs)  # type: ignore[arg-type]
    return Config(
        identity=Identity(name="Test", github_user="test"),
        brand=Brand(palette="neon-rainbow"),
        cards=Cards(badges=badges),
    )


# ── icons.py ────────────────────────────────────────────────────────────


def test_lookup_known_slug_returns_color_and_monogram():
    result = lookup("python")
    assert result is not None
    monogram, color = result
    assert monogram == "PY"
    assert color == "#3776AB"


def test_lookup_is_case_insensitive():
    assert lookup("PYTHON") == lookup("python") == lookup("Python")


def test_lookup_unknown_slug_returns_none():
    assert lookup("nonexistent-tech") is None


def test_known_icons_all_have_color_starting_with_hash():
    for slug, (monogram, color) in KNOWN_ICONS.items():
        assert color.startswith("#"), f"{slug} color must start with #"
        assert len(color) == 7, f"{slug} color must be #RRGGBB"
        assert monogram, f"{slug} monogram must be non-empty"


def test_derive_monogram_takes_first_two_letters():
    assert derive_monogram("Python") == "PY"
    assert derive_monogram("PostgreSQL") == "PO"


def test_derive_monogram_preserves_symbols():
    assert derive_monogram("C#") == "C#"
    assert derive_monogram("C++") == "C++"


def test_derive_monogram_handles_single_char():
    assert derive_monogram("R") == "R"


def test_derive_monogram_handles_empty():
    assert derive_monogram("") == "?"
    assert derive_monogram("   ") == "?"


# ── _resolve ────────────────────────────────────────────────────────────


def test_resolve_uses_brand_color_when_no_override():
    item = BadgeItem(label="Python", icon="python")
    monogram, color, label = _resolve(item)
    assert monogram == "PY"
    assert color == "#3776AB"
    assert label == "Python"


def test_resolve_explicit_color_overrides_brand_color():
    item = BadgeItem(label="Python", icon="python", color="#FF0000")
    _, color, _ = _resolve(item)
    assert color == "#FF0000"


def test_resolve_unknown_icon_falls_back_to_label_monogram():
    item = BadgeItem(label="Unknown Tech", icon="unknown-slug")
    monogram, color, _ = _resolve(item)
    assert monogram == "UN"
    # Fallback color is jewel-tone violet.
    assert color == "#7B5EAA"


def test_resolve_no_icon_at_all_uses_label():
    item = BadgeItem(label="Custom")
    monogram, color, _ = _resolve(item)
    assert monogram == "CU"
    assert color == "#7B5EAA"


# ── _shape_path ─────────────────────────────────────────────────────────


def test_shape_path_pill_returns_valid_d_string():
    d = _shape_path("pill", 168, 56)
    assert d.startswith("M ")
    assert d.endswith(" Z")
    assert " A " in d  # arc commands for the rounded ends


def test_shape_path_circle_returns_two_arcs():
    d = _shape_path("circle", 100, 100)
    # Full circle = two semicircle arcs.
    assert d.count(" A ") == 2


def test_shape_path_hex_has_six_line_commands():
    d = _shape_path("hex", 112, 116)
    # Hex = M + 5 L + Z (6 vertices total, first via M then 5 via L)
    assert d.count(" L ") == 5


def test_shape_path_shield_has_arcs_and_quadratic_curves():
    d = _shape_path("shield", 124, 128)
    assert " A " in d  # rounded top corners
    assert " Q " in d  # tapered bottom point


def test_shape_path_unknown_raises():
    with pytest.raises(ValueError, match="unknown badge shape"):
        _shape_path("triangle", 100, 100)


# ── _layout_positions ───────────────────────────────────────────────────


def test_layout_row_wraps_when_exceeds_svg_width():
    """Row layout should wrap to a new line when the next badge wouldn't fit."""
    positions, total_h = _layout_positions(
        n=10, layout="row", columns=6, badge_w=BADGE_W["pill"], badge_h=BADGE_H["pill"]
    )
    # 10 pills * (168 + 14) = 1820, exceeds 1200 -> must wrap.
    rows = {y for _, y in positions}
    assert len(rows) >= 2, "10 pills should wrap to multiple rows"
    # Total height should account for at least 2 rows.
    assert total_h > BADGE_H["pill"] + 40


def test_layout_grid_uses_columns():
    positions, _ = _layout_positions(n=12, layout="grid", columns=6, badge_w=80, badge_h=80)
    # First row: 6 badges at y=20.
    first_row = [(x, y) for x, y in positions if y == 20]
    assert len(first_row) == 6


def test_layout_marquee_is_single_row():
    positions, total_h = _layout_positions(
        n=20, layout="marquee", columns=6, badge_w=100, badge_h=100
    )
    # All badges must be on the same y row.
    ys = {y for _, y in positions}
    assert ys == {20}
    assert total_h == 100 + 40


def test_layout_grid_total_height_grows_with_rows():
    _, h_2_rows = _layout_positions(n=12, layout="grid", columns=6, badge_w=80, badge_h=80)
    _, h_3_rows = _layout_positions(n=18, layout="grid", columns=6, badge_w=80, badge_h=80)
    assert h_3_rows > h_2_rows


def test_layout_row_first_badge_at_origin():
    positions, _ = _layout_positions(
        n=1, layout="row", columns=6, badge_w=BADGE_W["pill"], badge_h=BADGE_H["pill"]
    )
    assert positions == [(20, 20)]


# ── End-to-end: build() ─────────────────────────────────────────────────


def test_build_writes_valid_xml(tmp_path: Path):
    items = [
        BadgeItem(label="Python", icon="python", value="Senior"),
        BadgeItem(label="Rust", icon="rust", value="85%"),
    ]
    config = _config_with_badges(items)
    out = build(config, output=tmp_path / "badges.svg")
    assert out.exists()
    import xml.etree.ElementTree as ET

    ET.parse(out)  # raises if not well-formed XML


def test_build_empty_items_still_writes_file(tmp_path: Path):
    config = _config_with_badges([])
    out = build(config, output=tmp_path / "empty.svg")
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Badges (empty)" in text


def test_build_includes_brand_color_for_known_icon(tmp_path: Path):
    config = _config_with_badges([BadgeItem(label="Python", icon="python")], shape="pill")
    out = build(config, output=tmp_path / "badges.svg")
    text = out.read_text(encoding="utf-8")
    assert "#3776AB" in text


def test_build_uses_explicit_color_override(tmp_path: Path):
    config = _config_with_badges(
        [BadgeItem(label="Custom", icon="python", color="#FF00FF")], shape="pill"
    )
    out = build(config, output=tmp_path / "badges.svg")
    text = out.read_text(encoding="utf-8")
    assert "#FF00FF" in text
    # The python brand color should NOT appear since it was overridden.
    assert "#3776AB" not in text


def test_build_renders_user_supplied_svg_path(tmp_path: Path):
    custom_path = "M12 2L2 22h20L12 2z"
    config = _config_with_badges(
        [BadgeItem(label="Triangle", icon_svg=custom_path, color="#7C3AED")]
    )
    out = build(config, output=tmp_path / "badges.svg")
    text = out.read_text(encoding="utf-8")
    assert custom_path in text


def test_build_renders_value_text_when_provided(tmp_path: Path):
    config = _config_with_badges(
        [BadgeItem(label="Rust", icon="rust", value="Senior")], shape="pill"
    )
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    assert ">Senior<" in text
    assert "b-value" in text


def test_build_circle_shape_omits_value_text(tmp_path: Path):
    """Circle is the most compact form — value field is intentionally not rendered."""
    config = _config_with_badges(
        [BadgeItem(label="Py", icon="python", value="HiddenForCircle")],
        shape="circle",
    )
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    assert "HiddenForCircle" not in text


def test_build_marquee_layout_includes_translate_animation(tmp_path: Path):
    config = _config_with_badges(
        [BadgeItem(label="A", icon="python"), BadgeItem(label="B", icon="rust")],
        shape="pill",
        layout="marquee",
    )
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    assert "animateTransform" in text
    assert 'type="translate"' in text


def test_build_stagger_animation_includes_per_badge_delay(tmp_path: Path):
    config = _config_with_badges(
        [BadgeItem(label="A"), BadgeItem(label="B"), BadgeItem(label="C")],
        animation="stagger",
    )
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    # First badge starts immediately; later ones have offsets.
    assert 'begin="0.00s"' in text
    assert 'begin="0.06s"' in text


def test_build_pulse_animation_applies_class(tmp_path: Path):
    config = _config_with_badges([BadgeItem(label="A", icon="python")], animation="pulse")
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    assert 'class="b-pulse"' in text


def test_build_href_wraps_badge_in_anchor(tmp_path: Path):
    config = _config_with_badges([BadgeItem(label="GH", icon="github", href="https://github.com")])
    text = build(config, output=tmp_path / "b.svg").read_text(encoding="utf-8")
    assert 'xlink:href="https://github.com"' in text
    assert 'target="_blank"' in text


def test_build_handles_all_four_shapes(tmp_path: Path):
    """Smoke test: every shape produces valid XML."""
    for shape in ("pill", "hex", "shield", "circle"):
        config = _config_with_badges([BadgeItem(label="X", icon="python")], shape=shape)
        out = build(config, output=tmp_path / f"{shape}.svg")
        import xml.etree.ElementTree as ET

        ET.parse(out)  # well-formed
        assert out.read_text(encoding="utf-8").startswith("<?xml")


def test_build_viewbox_width_is_svg_width():
    """Sanity: SVG viewBox uses the layout-constant width."""
    assert SVG_WIDTH == 1200
    # Per-shape dimensions are positive.
    for shape, w in BADGE_W.items():
        assert w > 0, f"BADGE_W[{shape}] must be positive"
        assert BADGE_H[shape] > 0, f"BADGE_H[{shape}] must be positive"
    assert BADGE_GAP > 0
