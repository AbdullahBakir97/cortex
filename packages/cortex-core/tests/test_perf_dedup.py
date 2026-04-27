"""Performance regression tests for the symbol/use dedup pass.

Locks in the size budgets achieved by:

  • heatmap: <use href="#hm-cell"> dedup of 364 cells
  • badges marquee: <use href="#b-loop"> instead of rendering twice

These thresholds are intentionally loose (15-25% headroom) so unrelated
content additions don't false-positive, but tight enough to catch a
regression that re-inlines either dedup pattern.
"""

from __future__ import annotations

from pathlib import Path

from cortex.builders import badges, heatmap
from cortex.schema import (
    BadgeItem,
    BadgesConfig,
    Brand,
    Cards,
    Config,
    HeatmapConfig,
    Identity,
)


def _config(**cards_kwargs: object) -> Config:
    return Config(
        identity=Identity(name="Test User", github_user="test"),
        brand=Brand(),
        cards=Cards(**cards_kwargs),  # type: ignore[arg-type]
    )


def test_heatmap_uses_symbol_dedup_for_cells(tmp_path: Path):
    cfg = _config(heatmap=HeatmapConfig(enabled=True))
    text = heatmap.build(cfg, tmp_path / "h.svg").read_text(encoding="utf-8")
    # Symbol must be defined once.
    assert text.count('<symbol id="hm-cell"') == 1
    # Every cell + the 5 legend swatches reference it.
    assert text.count("<use ") >= 364 + 5


def test_heatmap_under_size_budget(tmp_path: Path):
    """Pre-dedup baseline: ~51KB. Post-dedup target: <48KB. Budget: 50KB."""
    cfg = _config(heatmap=HeatmapConfig(enabled=True))
    out = heatmap.build(cfg, tmp_path / "h.svg")
    size = out.stat().st_size
    assert size < 50_000, f"heatmap regressed: {size} bytes (budget 50KB)"


def test_marquee_dedups_via_use_reference(tmp_path: Path):
    """Marquee must reference its loop with <use>, not duplicate badges inline."""
    cfg = _config(
        badges=BadgesConfig(
            enabled=True,
            shape="shield",
            layout="marquee",
            items=[BadgeItem(label=f"L{i}") for i in range(8)],
        )
    )
    text = badges.build(cfg, tmp_path / "m.svg").read_text(encoding="utf-8")
    assert 'id="b-loop"' in text
    assert 'href="#b-loop"' in text


def test_marquee_under_size_budget(tmp_path: Path):
    """Pre-dedup baseline: ~23KB (badges rendered twice). Post-dedup: ~12KB."""
    cfg = _config(
        badges=BadgesConfig(
            enabled=True,
            shape="shield",
            layout="marquee",
            items=[BadgeItem(label=f"Item {i}", icon="python") for i in range(8)],
        )
    )
    out = badges.build(cfg, tmp_path / "m.svg")
    size = out.stat().st_size
    assert size < 16_000, f"marquee regressed: {size} bytes (budget 16KB)"
