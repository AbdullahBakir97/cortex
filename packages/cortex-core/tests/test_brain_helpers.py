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
