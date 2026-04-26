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
