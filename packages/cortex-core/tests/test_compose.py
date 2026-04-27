"""Tests for cortex.compose — stacking widgets into a single SVG."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from cortex.compose import (
    _strip_xml_decl,
    compose,
    list_available,
)
from cortex.schema import (
    BadgeItem,
    BadgesConfig,
    Brand,
    Cards,
    Config,
    Identity,
    NowPlayingConfig,
    SynthwaveConfig,
)


def _config() -> Config:
    return Config(
        identity=Identity(name="Test User", github_user="test"),
        brand=Brand(),
        cards=Cards(
            synthwave=SynthwaveConfig(enabled=True, title="HEY"),
            badges=BadgesConfig(enabled=True, items=[BadgeItem(label="Python", icon="python")]),
            now_playing=NowPlayingConfig(enabled=True),
        ),
    )


# ── list_available ──────────────────────────────────────────────────────


def test_list_available_includes_all_known_widgets():
    slugs = list_available()
    # Spot-check: every widget the catalog mentions should be composable.
    for required in (
        "brain-anatomical",
        "synthwave-banner",
        "badges",
        "skill-galaxy",
        "skill-radar",
        "code-roadmap",
        "activity-heatmap",
        "stat-cubes",
        "achievement-wall",
        "code-dna",
        "skill-globe",
        "particle-cloud",
        "now-playing",
    ):
        assert required in slugs, f"missing widget slug: {required}"


# ── _strip_xml_decl ─────────────────────────────────────────────────────


def test_strip_xml_decl_removes_declaration():
    raw = '<?xml version="1.0" encoding="UTF-8"?>\n<svg></svg>'
    assert _strip_xml_decl(raw).strip() == "<svg></svg>"


def test_strip_xml_decl_passthrough_when_no_decl():
    raw = "<svg>x</svg>"
    assert _strip_xml_decl(raw) == "<svg>x</svg>"


# ── compose end-to-end ──────────────────────────────────────────────────


def test_compose_produces_well_formed_xml(tmp_path: Path):
    out = compose(
        _config(),
        widgets=["synthwave-banner", "badges"],
        output=tmp_path / "c.svg",
    )
    ET.parse(out)


def test_compose_unknown_slug_raises(tmp_path: Path):
    with pytest.raises(ValueError, match="Unknown widget slug"):
        compose(
            _config(),
            widgets=["does-not-exist"],
            output=tmp_path / "c.svg",
        )


def test_compose_stacks_widgets_at_increasing_y(tmp_path: Path):
    """Each child <svg> after the first must have y > previous y."""
    out = compose(
        _config(),
        widgets=["synthwave-banner", "badges", "now-playing"],
        output=tmp_path / "c.svg",
    )
    text = out.read_text(encoding="utf-8")
    # Find the y= attributes that we wrote (the ones with x="0" prefix).
    import re

    pattern = re.compile(r'<svg x="0" y="(\d+)" width="\d+" height="\d+"')
    ys = [int(m.group(1)) for m in pattern.finditer(text)]
    assert len(ys) == 3
    assert ys == sorted(ys), f"expected non-decreasing y values, got {ys}"
    # First widget must start at y=0; later widgets must be strictly below.
    assert ys[0] == 0
    assert ys[1] > 0
    assert ys[2] > ys[1]


def test_compose_total_height_matches_sum_of_widgets(tmp_path: Path):
    """Composite viewBox height should be sum(child heights) + gaps."""
    out = compose(
        _config(),
        widgets=["synthwave-banner", "badges"],
        output=tmp_path / "c.svg",
        gap=20,
    )
    text = out.read_text(encoding="utf-8")
    # Pull child heights from our wrapping <svg x="0" y="..." height="...">.
    import re

    heights = [int(m) for m in re.findall(r'<svg x="0" y="\d+" width="\d+" height="(\d+)"', text)]
    expected_total = sum(heights) + 20 * (len(heights) - 1)
    # Composite outer viewBox.
    vb = re.search(r'viewBox="0 0 1200 (\d+)"', text)
    assert vb is not None
    assert int(vb.group(1)) == expected_total


def test_compose_output_size_under_kitchen_sink_budget(tmp_path: Path):
    """Composite of the 5 most common widgets stays under ~250KB."""
    out = compose(
        _config(),
        widgets=["synthwave-banner", "badges", "now-playing"],
        output=tmp_path / "c.svg",
    )
    size = out.stat().st_size
    assert size < 60_000, f"3-widget compose grew unexpectedly: {size} bytes"
