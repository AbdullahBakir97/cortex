"""Unit tests for the brain builder's pure helpers."""

from __future__ import annotations

import random as _random

from cortex.builders.brain import (
    _LOBE_KEYS,
    _build_lobe_stroke_overlay,
    _ensure_classification,
    _random_arc_network,
    _random_cells_in_bbox,
    _seed_from_name,
)


def test_seed_from_name_is_deterministic():
    assert _seed_from_name("Abdullah") == _seed_from_name("Abdullah")


def test_seed_from_name_differs_per_name():
    assert _seed_from_name("Abdullah") != _seed_from_name("Alice")


def test_seed_from_name_returns_int_in_32bit_range():
    seed = _seed_from_name("anything")
    assert isinstance(seed, int)
    assert 0 <= seed < (1 << 32)


def test_random_cells_count_matches_n():
    rng = _random.Random(42)
    cells = _random_cells_in_bbox((0.0, 0.0, 100.0, 100.0), n=6, rng=rng)
    assert len(cells) == 6


def test_random_cells_are_inside_inset_bbox():
    """Cells must be inside the bbox at normalized offsets in [0.15, 0.85]."""
    rng = _random.Random(42)
    bbox = (0.0, 0.0, 100.0, 100.0)
    cells = _random_cells_in_bbox(bbox, n=20, rng=rng)
    for cx, cy in cells:
        assert 15 <= cx <= 85, f"cell x={cx} outside inset"
        assert 15 <= cy <= 85, f"cell y={cy} outside inset"


def test_random_cells_are_deterministic_for_same_rng_seed():
    a = _random_cells_in_bbox((0.0, 0.0, 100.0, 100.0), n=6, rng=_random.Random(7))
    b = _random_cells_in_bbox((0.0, 0.0, 100.0, 100.0), n=6, rng=_random.Random(7))
    assert a == b


def test_random_cells_returns_int_tuples():
    rng = _random.Random(42)
    cells = _random_cells_in_bbox((10.0, 20.0, 110.0, 220.0), n=4, rng=rng)
    for cx, cy in cells:
        assert isinstance(cx, int)
        assert isinstance(cy, int)


def _sample_cells_by_lobe() -> dict[str, list[tuple[int, int]]]:
    return {
        "frontal": [(100, 100), (120, 100), (110, 130)],
        "parietal": [(200, 100), (220, 100), (210, 130)],
        "occipital": [(300, 100), (320, 100), (310, 130)],
        "temporal": [(200, 200), (220, 200), (210, 230)],
        "cerebellum": [(280, 250), (300, 250), (290, 280)],
        "brainstem": [(280, 320), (300, 320), (290, 350)],
    }


def _sample_lobe_colors() -> dict[str, str]:
    return {
        "frontal": "#F90001",
        "parietal": "#34D399",
        "occipital": "#FF652F",
        "temporal": "#FFD23F",
        "cerebellum": "#22D3EE",
        "brainstem": "#A78BFA",
    }


def test_random_arc_network_returns_n_arcs():
    rng = _random.Random(42)
    arcs = _random_arc_network(
        _sample_cells_by_lobe(), n=20, rng=rng, lobe_colors=_sample_lobe_colors()
    )
    assert len(arcs) == 20


def test_random_arc_network_endpoints_are_real_cells():
    rng = _random.Random(42)
    cells = _sample_cells_by_lobe()
    all_cells = {pt for lst in cells.values() for pt in lst}
    arcs = _random_arc_network(cells, n=15, rng=rng, lobe_colors=_sample_lobe_colors())
    for a in arcs:
        assert (a.x1, a.y1) in all_cells
        assert (a.x2, a.y2) in all_cells


def test_random_arc_network_color_matches_source_lobe():
    rng = _random.Random(42)
    cells = _sample_cells_by_lobe()
    colors = _sample_lobe_colors()
    arcs = _random_arc_network(cells, n=30, rng=rng, lobe_colors=colors)
    valid_colors = set(colors.values())
    for a in arcs:
        assert a.color in valid_colors


def test_random_arc_network_timing_in_range():
    rng = _random.Random(42)
    arcs = _random_arc_network(
        _sample_cells_by_lobe(), n=30, rng=rng, lobe_colors=_sample_lobe_colors()
    )
    for a in arcs:
        assert 0.0 <= a.begin_s < 12.0
        assert 0.8 <= a.dur_s < 1.6


def test_random_arc_network_is_deterministic():
    a = _random_arc_network(
        _sample_cells_by_lobe(), n=10, rng=_random.Random(99), lobe_colors=_sample_lobe_colors()
    )
    b = _random_arc_network(
        _sample_cells_by_lobe(), n=10, rng=_random.Random(99), lobe_colors=_sample_lobe_colors()
    )
    assert a == b


def test_random_arc_network_no_self_loops():
    rng = _random.Random(42)
    arcs = _random_arc_network(
        _sample_cells_by_lobe(), n=30, rng=rng, lobe_colors=_sample_lobe_colors()
    )
    for a in arcs:
        assert (a.x1, a.y1) != (a.x2, a.y2)


def test_ensure_classification_returns_paths_by_lobe():
    _classification, _centroids, _bboxes, paths_by_lobe = _ensure_classification()
    assert set(paths_by_lobe.keys()) == set(_LOBE_KEYS)
    # Every lobe should have at least one path
    for lobe in _LOBE_KEYS:
        assert len(paths_by_lobe[lobe]) > 0, f"{lobe} has no paths"


def test_paths_by_lobe_contains_id_and_d_strings():
    _classification, _centroids, _bboxes, paths_by_lobe = _ensure_classification()
    sample = paths_by_lobe["frontal"][0]
    assert isinstance(sample, tuple)
    assert len(sample) == 2
    pid, d = sample
    assert isinstance(pid, str) and pid
    assert isinstance(d, str) and d


def test_paths_by_lobe_ids_match_classification_set():
    classification, _centroids, _bboxes, paths_by_lobe = _ensure_classification()
    for lobe in _LOBE_KEYS:
        ids_from_pairs = {pid for pid, _d in paths_by_lobe[lobe]}
        assert ids_from_pairs == classification[lobe], f"{lobe} id mismatch"


def test_overlay_picks_n_largest_per_lobe():
    paths_by_lobe = {
        "frontal": [
            ("a", "x" * 10),
            ("b", "x" * 100),
            ("c", "x" * 50),
            ("d", "x" * 200),
            ("e", "x" * 30),
        ],
        "parietal": [("f", "x" * 80), ("g", "x" * 20)],
        "occipital": [("h", "x" * 5)],
        "temporal": [],
        "cerebellum": [("i", "x" * 60), ("j", "x" * 70), ("k", "x" * 65)],
        "brainstem": [],
    }
    colors = {
        "frontal": "#FF0000",
        "parietal": "#00FF00",
        "occipital": "#0000FF",
        "temporal": "#FFFF00",
        "cerebellum": "#00FFFF",
        "brainstem": "#FF00FF",
    }
    overlay = _build_lobe_stroke_overlay(paths_by_lobe, colors, n_per_lobe=2)
    # frontal: 2 (b, d), parietal: 2 (f, g), occipital: 1 (h),
    # temporal: 0, cerebellum: 2 (j, k or i, j), brainstem: 0 → 7 total
    assert len(overlay) == 7


def test_overlay_picks_largest_d_first():
    """Top-N selection ranks by len(d), descending."""
    paths_by_lobe = {
        "frontal": [("small", "x"), ("big", "x" * 999), ("med", "x" * 50)],
        "parietal": [],
        "occipital": [],
        "temporal": [],
        "cerebellum": [],
        "brainstem": [],
    }
    colors = {
        k: "#000000"
        for k in ["frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem"]
    }
    overlay = _build_lobe_stroke_overlay(paths_by_lobe, colors, n_per_lobe=2)
    assert len(overlay) == 2
    # Both elements should reference the d-strings, with the longer d included
    joined = " ".join(overlay)
    assert ("x" * 999) in joined
    assert ("x" * 50) in joined
    assert ' x"' not in joined or joined.count('d="x"') == 0  # the 1-char d not picked


def test_overlay_emits_fill_none_and_lobe_color_stroke():
    paths_by_lobe = {
        "frontal": [("p1", "M0,0 L10,10")],
        "parietal": [],
        "occipital": [],
        "temporal": [],
        "cerebellum": [],
        "brainstem": [],
    }
    colors = {
        "frontal": "#F90001",
        "parietal": "#34D399",
        "occipital": "#FF652F",
        "temporal": "#FFD23F",
        "cerebellum": "#22D3EE",
        "brainstem": "#A78BFA",
    }
    overlay = _build_lobe_stroke_overlay(paths_by_lobe, colors, n_per_lobe=8)
    assert len(overlay) == 1
    el = overlay[0]
    assert 'fill="none"' in el
    assert 'stroke="#F90001"' in el
    assert 'pathLength="100"' in el
    assert 'stroke-dasharray="100 100"' in el
    assert 'class="lobe-stroke ls-frontal"' in el
    assert 'd="M0,0 L10,10"' in el
