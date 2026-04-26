"""Unit tests for the brain builder's pure helpers."""
from __future__ import annotations

from cortex.builders.brain import _seed_from_name


def test_seed_from_name_is_deterministic():
    assert _seed_from_name("Abdullah") == _seed_from_name("Abdullah")


def test_seed_from_name_differs_per_name():
    assert _seed_from_name("Abdullah") != _seed_from_name("Alice")


def test_seed_from_name_returns_int_in_32bit_range():
    seed = _seed_from_name("anything")
    assert isinstance(seed, int)
    assert 0 <= seed < (1 << 32)


import random as _random

from cortex.builders.brain import _random_cells_in_bbox


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


from cortex.builders.brain import _Arc, _random_arc_network


def _sample_cells_by_lobe() -> dict[str, list[tuple[int, int]]]:
    return {
        "frontal":    [(100, 100), (120, 100), (110, 130)],
        "parietal":   [(200, 100), (220, 100), (210, 130)],
        "occipital":  [(300, 100), (320, 100), (310, 130)],
        "temporal":   [(200, 200), (220, 200), (210, 230)],
        "cerebellum": [(280, 250), (300, 250), (290, 280)],
        "brainstem":  [(280, 320), (300, 320), (290, 350)],
    }


def _sample_lobe_colors() -> dict[str, str]:
    return {
        "frontal":    "#F90001",
        "parietal":   "#34D399",
        "occipital":  "#FF652F",
        "temporal":   "#FFD23F",
        "cerebellum": "#22D3EE",
        "brainstem":  "#A78BFA",
    }


def test_random_arc_network_returns_n_arcs():
    rng = _random.Random(42)
    arcs = _random_arc_network(_sample_cells_by_lobe(), n=20, rng=rng,
                                lobe_colors=_sample_lobe_colors())
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
    arcs = _random_arc_network(_sample_cells_by_lobe(), n=30, rng=rng,
                                lobe_colors=_sample_lobe_colors())
    for a in arcs:
        assert 0.0 <= a.begin_s < 12.0
        assert 0.8 <= a.dur_s < 1.6


def test_random_arc_network_is_deterministic():
    a = _random_arc_network(_sample_cells_by_lobe(), n=10, rng=_random.Random(99),
                              lobe_colors=_sample_lobe_colors())
    b = _random_arc_network(_sample_cells_by_lobe(), n=10, rng=_random.Random(99),
                              lobe_colors=_sample_lobe_colors())
    assert a == b


def test_random_arc_network_no_self_loops():
    rng = _random.Random(42)
    arcs = _random_arc_network(_sample_cells_by_lobe(), n=30, rng=rng,
                                lobe_colors=_sample_lobe_colors())
    for a in arcs:
        assert (a.x1, a.y1) != (a.x2, a.y2)
