# Brain — Professional Visual Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the brain's six saturated per-lobe color blocks with one unified muted gradient body, add an animated stroke-overlay layer that draws the lobe outlines in card colors on a 6s loop, and replace the fixed-grid arc quadrilateral with a deterministic-but-disordered random Bezier arc network.

**Architecture:** All edits land in `packages/cortex-core/cortex/builders/brain.py`. Lobe identity moves from the *fill channel* (per-lobe gradients) to a *stroke-overlay channel* (duplicated `<path>` elements above the body fill, animated via CSS `stroke-dashoffset`). Random arcs use a deterministic `random.Random` seeded by `sha256(config.identity.name)[:8]` so renders are reproducible per user. New tests live in `packages/cortex-core/tests/`.

**Tech Stack:** Python 3.10+, pydantic v2 (existing), pytest 8 (existing dev dep), SVG 1.1 with SMIL + CSS animation. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-professional-visuals-design.md` (commit `8b51be6`).

---

## File Structure

| Path | Purpose | Status |
|---|---|---|
| `packages/cortex-core/cortex/builders/brain.py` | All brain SVG generation logic; helpers + wrapper composer | Modified |
| `packages/cortex-core/tests/__init__.py` | Marks tests directory as a package | Created |
| `packages/cortex-core/tests/conftest.py` | pytest config — adds `cortex` to sys.path | Created |
| `packages/cortex-core/tests/test_brain_helpers.py` | Pure-function unit tests for new helpers (seed, cells, arcs, overlay) | Created |
| `packages/cortex-core/tests/test_brain_integration.py` | Two-builds-byte-equal determinism test + SVG validity check | Created |
| `examples/rendered/extreme/brain-anatomical.svg` | Pre-rendered showcase SVG | Regenerated (auto via build-examples.yml) |

---

## Task 1: Bootstrap tests directory

**Files:**
- Create: `packages/cortex-core/tests/__init__.py`
- Create: `packages/cortex-core/tests/conftest.py`

- [ ] **Step 1: Create empty `__init__.py`**

```bash
touch packages/cortex-core/tests/__init__.py
```

- [ ] **Step 2: Create `conftest.py` so `import cortex.builders.brain` works**

`packages/cortex-core/tests/conftest.py`:

```python
"""pytest config: ensure the cortex-core package is importable from tests."""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent  # packages/cortex-core
_SRC = _PKG_ROOT / "cortex"

# Add the package root so `import cortex` resolves to packages/cortex-core/cortex
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
```

- [ ] **Step 3: Verify pytest discovers the empty test dir**

Run: `pytest packages/cortex-core/tests -v`
Expected: `no tests ran` (exit 5, but no errors). If you see import errors, re-check `conftest.py`.

- [ ] **Step 4: Commit**

```bash
git add packages/cortex-core/tests/__init__.py packages/cortex-core/tests/conftest.py
git commit -m "test(brain): bootstrap tests directory with conftest"
```

---

## Task 2: `_seed_from_name` helper (deterministic RNG seed from identity name)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (add helper near top of file, after imports)
- Test: `packages/cortex-core/tests/test_brain_helpers.py`

- [ ] **Step 1: Write the failing test**

`packages/cortex-core/tests/test_brain_helpers.py`:

```python
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
```

- [ ] **Step 2: Run the test — expect ImportError**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: FAIL with `ImportError: cannot import name '_seed_from_name'`.

- [ ] **Step 3: Add the helper to `brain.py`**

In `packages/cortex-core/cortex/builders/brain.py`, add this import at the top (after the existing `import re`):

```python
import hashlib
import random
from dataclasses import dataclass
```

Add this helper anywhere in the file before `_compose_wrapper` (the existing helpers section after `_iter_paths` is a fine home):

```python
def _seed_from_name(name: str) -> int:
    """Stable 32-bit seed derived from the identity name. Deterministic per user."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)
```

- [ ] **Step 4: Run the test — expect PASS**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_helpers.py
git commit -m "feat(brain): _seed_from_name — deterministic RNG seed from identity"
```

---

## Task 3: `_random_cells_in_bbox` helper (random cells inside a lobe's bbox)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`
- Test: `packages/cortex-core/tests/test_brain_helpers.py`

- [ ] **Step 1: Write the failing test**

Append to `packages/cortex-core/tests/test_brain_helpers.py`:

```python
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
```

- [ ] **Step 2: Run the test — expect ImportError**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: FAIL with `ImportError: cannot import name '_random_cells_in_bbox'`.

- [ ] **Step 3: Add the helper to `brain.py`**

Add to `packages/cortex-core/cortex/builders/brain.py` near the other classification helpers:

```python
def _random_cells_in_bbox(
    bbox: tuple[float, float, float, float],
    n: int,
    rng: random.Random,
) -> list[tuple[int, int]]:
    """Return n cells at random normalized offsets in [0.15, 0.85] inside bbox.

    Inset 15% from each edge so cells sit well inside the lobe rather than on its edge.
    Coords are returned as ints (SVG tolerates floats but ints render slightly tighter).
    """
    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    out: list[tuple[int, int]] = []
    for _ in range(n):
        nx = rng.uniform(0.15, 0.85)
        ny = rng.uniform(0.15, 0.85)
        out.append((round(xmin + nx * w), round(ymin + ny * h)))
    return out
```

- [ ] **Step 4: Run the test — expect PASS**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: 4 new tests pass (7 total in file).

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_helpers.py
git commit -m "feat(brain): _random_cells_in_bbox — disordered cell placement"
```

---

## Task 4: `_Arc` dataclass + `_random_arc_network` helper

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`
- Test: `packages/cortex-core/tests/test_brain_helpers.py`

- [ ] **Step 1: Write the failing tests**

Append to `packages/cortex-core/tests/test_brain_helpers.py`:

```python
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
```

- [ ] **Step 2: Run the test — expect ImportError**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: FAIL with `ImportError: cannot import name '_Arc'`.

- [ ] **Step 3: Add the dataclass and helper to `brain.py`**

Add near the other classification helpers:

```python
@dataclass(frozen=True)
class _Arc:
    """One randomized synaptic arc between two cells, with Bezier control point."""
    x1: int
    y1: int
    x2: int
    y2: int
    cx: int   # quadratic Bezier control point x
    cy: int   # quadratic Bezier control point y
    color: str
    begin_s: float
    dur_s: float


def _random_arc_network(
    cells_by_lobe: dict[str, list[tuple[int, int]]],
    n: int,
    rng: random.Random,
    lobe_colors: dict[str, str],
) -> list[_Arc]:
    """n random arcs across the union of cells, colored by source lobe.

    Each arc:
      - source cell picked uniformly from the union of all lobes' cells
      - target cell picked uniformly from the union (resampled if equal to source)
      - color = source-lobe's accent
      - quadratic Bezier control point at midpoint + random offset (±60px each axis)
      - begin_s in [0, 12), dur_s in [0.8, 1.6)
    """
    cell_lobe: list[tuple[tuple[int, int], str]] = []
    for lobe, cells in cells_by_lobe.items():
        for c in cells:
            cell_lobe.append((c, lobe))

    arcs: list[_Arc] = []
    for _ in range(n):
        (p1, lobe1) = rng.choice(cell_lobe)
        (p2, _lobe2) = rng.choice(cell_lobe)
        # Resample if we drew the same cell twice (no self-loops)
        attempts = 0
        while p2 == p1 and attempts < 5:
            (p2, _lobe2) = rng.choice(cell_lobe)
            attempts += 1
        if p2 == p1:
            # Pathological: skip rather than emit a degenerate arc.
            continue
        mid_x = (p1[0] + p2[0]) // 2
        mid_y = (p1[1] + p2[1]) // 2
        cx = mid_x + rng.randint(-60, 60)
        cy = mid_y + rng.randint(-60, 60)
        arcs.append(_Arc(
            x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1],
            cx=cx, cy=cy,
            color=lobe_colors[lobe1],
            begin_s=rng.uniform(0.0, 12.0),
            dur_s=rng.uniform(0.8, 1.6),
        ))
    return arcs
```

- [ ] **Step 4: Run the tests — expect PASS**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: 6 new tests pass (13 total).

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_helpers.py
git commit -m "feat(brain): _Arc + _random_arc_network — randomized Bezier arc network"
```

---

## Task 5: Extend classification cache to include `paths_by_lobe`

The overlay layer needs `(id, d)` pairs per lobe. Today `_classify_brain_paths` returns only path IDs, centroids, and bboxes. We extend it to also return the `(id, d)` tuples per lobe.

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (extend `_classify_brain_paths` + `_ensure_classification`)
- Test: `packages/cortex-core/tests/test_brain_helpers.py`

- [ ] **Step 1: Write the failing test**

Append to `packages/cortex-core/tests/test_brain_helpers.py`:

```python
from cortex.builders.brain import _ensure_classification, _LOBE_KEYS


def test_ensure_classification_returns_paths_by_lobe():
    classification, _centroids, _bboxes, paths_by_lobe = _ensure_classification()
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
```

- [ ] **Step 2: Run the test — expect failure**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v -k classification`
Expected: FAIL — `_ensure_classification` returns a 3-tuple, not a 4-tuple, so unpacking fails.

- [ ] **Step 3: Extend `_classify_brain_paths` and `_ensure_classification`**

In `packages/cortex-core/cortex/builders/brain.py`:

Find the module-level cache vars (around line 67) and add a fourth:

```python
_LOBE_PATH_IDS: dict[str, set[str]] | None = None
_LOBE_CENTROIDS: dict[str, tuple[int, int]] | None = None
_LOBE_BBOXES: dict[str, tuple[float, float, float, float]] | None = None
_LOBE_PATHS_BY_LOBE: dict[str, list[tuple[str, str]]] | None = None  # NEW
```

Update `_classify_brain_paths`'s return type annotation and body. The signature becomes:

```python
def _classify_brain_paths(
    svg: str,
) -> tuple[
    dict[str, set[str]],
    dict[str, tuple[int, int]],
    dict[str, tuple[float, float, float, float]],
    dict[str, list[tuple[str, str]]],
]:
    ...
```

In the function body, build a `paths_by_lobe: dict[str, list[tuple[str, str]]]` alongside the existing `classification` set-of-ids. The existing `_iter_paths` calls already give `(pid, d)` — append both pieces.

Concretely, in the cerebellum loop (around line 132):

```python
cere_g = _extract_g_by_id(svg, "cerebellum")
cere_ids: set[str] = set()
cere_pairs: list[tuple[str, str]] = []
cere_centroids: list[tuple[float, float]] = []
for pid, d in _iter_paths(cere_g):
    cere_ids.add(pid)
    cere_pairs.append((pid, d))
    c = _path_centroid_d(d)
    if c is not None:
        cere_centroids.append(c)
```

In the brain-stem loop:

```python
bs_g = _extract_g_by_id(svg, "brain-stem")
bs_ids: set[str] = set()
bs_pairs: list[tuple[str, str]] = []
bs_centroids: list[tuple[float, float]] = []
for pid, d in _iter_paths(bs_g):
    if pid in cere_ids:
        continue
    bs_ids.add(pid)
    bs_pairs.append((pid, d))
    c = _path_centroid_d(d)
    if c is not None:
        bs_centroids.append(c)
```

In the cerebrum loop, capture pairs per spatial bucket:

```python
cb_g = _extract_g_by_id(svg, "cerebrum")
classification: dict[str, set[str]] = {k: set() for k in _LOBE_KEYS}
paths_by_lobe: dict[str, list[tuple[str, str]]] = {k: [] for k in _LOBE_KEYS}
centroids_by_lobe: dict[str, list[tuple[float, float]]] = {k: [] for k in _LOBE_KEYS}
for pid, d in _iter_paths(cb_g):
    c = _path_centroid_d(d)
    if c is None:
        continue
    cx, cy = c
    if cx < 350:
        lobe = "frontal"
    elif cx > 700:
        lobe = "occipital"
    elif cy < 300:
        lobe = "parietal"
    else:
        lobe = "temporal"
    classification[lobe].add(pid)
    paths_by_lobe[lobe].append((pid, d))
    centroids_by_lobe[lobe].append(c)

classification["cerebellum"] = cere_ids
classification["brainstem"] = bs_ids
paths_by_lobe["cerebellum"] = cere_pairs
paths_by_lobe["brainstem"] = bs_pairs
centroids_by_lobe["cerebellum"] = cere_centroids
centroids_by_lobe["brainstem"] = bs_centroids
```

Update the `return` of `_classify_brain_paths` to return `(classification, canvas_centroids, bboxes, paths_by_lobe)`.

Update `_ensure_classification`:

```python
def _ensure_classification() -> tuple[
    dict[str, set[str]],
    dict[str, tuple[int, int]],
    dict[str, tuple[float, float, float, float]],
    dict[str, list[tuple[str, str]]],
]:
    """Lazy module-level cache. First call parses + classifies; later calls reuse."""
    global _LOBE_PATH_IDS, _LOBE_CENTROIDS, _LOBE_BBOXES, _LOBE_PATHS_BY_LOBE
    if (
        _LOBE_PATH_IDS is None
        or _LOBE_CENTROIDS is None
        or _LOBE_BBOXES is None
        or _LOBE_PATHS_BY_LOBE is None
    ):
        src_text = (
            resources.files("cortex.assets")
            .joinpath("brain-source.svg")
            .read_text(encoding="utf-8")
        )
        (
            _LOBE_PATH_IDS,
            _LOBE_CENTROIDS,
            _LOBE_BBOXES,
            _LOBE_PATHS_BY_LOBE,
        ) = _classify_brain_paths(src_text)
    return _LOBE_PATH_IDS, _LOBE_CENTROIDS, _LOBE_BBOXES, _LOBE_PATHS_BY_LOBE
```

- [ ] **Step 4: Update existing call sites that unpack `_ensure_classification`**

There are two callers in `brain.py`:

1. In `_compose_wrapper` (around line 313): change `_, lobe_centroids, lobe_bboxes = _ensure_classification()` to `_, lobe_centroids, lobe_bboxes, _ = _ensure_classification()`.

2. In `build` (around line 796): change `classification, _, _ = _ensure_classification()` to `classification, _, _, _ = _ensure_classification()`.

(These will be revised again in later tasks; for this task, just keep them passing.)

- [ ] **Step 5: Run the tests — expect PASS**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: all 16 tests pass.

- [ ] **Step 6: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_helpers.py
git commit -m "feat(brain): cache paths_by_lobe in classification (id, d) pairs"
```

---

## Task 6: `_build_lobe_stroke_overlay` helper (top-N paths per lobe)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`
- Test: `packages/cortex-core/tests/test_brain_helpers.py`

- [ ] **Step 1: Write the failing tests**

Append to `packages/cortex-core/tests/test_brain_helpers.py`:

```python
from cortex.builders.brain import _build_lobe_stroke_overlay


def test_overlay_picks_n_largest_per_lobe():
    paths_by_lobe = {
        "frontal":    [("a", "x" * 10), ("b", "x" * 100), ("c", "x" * 50),
                       ("d", "x" * 200), ("e", "x" * 30)],
        "parietal":   [("f", "x" * 80), ("g", "x" * 20)],
        "occipital":  [("h", "x" * 5)],
        "temporal":   [],
        "cerebellum": [("i", "x" * 60), ("j", "x" * 70), ("k", "x" * 65)],
        "brainstem":  [],
    }
    colors = {
        "frontal":    "#FF0000",
        "parietal":   "#00FF00",
        "occipital":  "#0000FF",
        "temporal":   "#FFFF00",
        "cerebellum": "#00FFFF",
        "brainstem":  "#FF00FF",
    }
    overlay = _build_lobe_stroke_overlay(paths_by_lobe, colors, n_per_lobe=2)
    # frontal: 2 (b, d), parietal: 2 (f, g), occipital: 1 (h),
    # temporal: 0, cerebellum: 2 (j, k or i, j), brainstem: 0 → 7 total
    assert len(overlay) == 7


def test_overlay_picks_largest_d_first():
    """Top-N selection ranks by len(d), descending."""
    paths_by_lobe = {
        "frontal": [("small", "x"), ("big", "x" * 999), ("med", "x" * 50)],
        "parietal": [], "occipital": [], "temporal": [],
        "cerebellum": [], "brainstem": [],
    }
    colors = {k: "#000000" for k in [
        "frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem"]}
    overlay = _build_lobe_stroke_overlay(paths_by_lobe, colors, n_per_lobe=2)
    assert len(overlay) == 2
    # Both elements should reference the d-strings, with the longer d included
    joined = " ".join(overlay)
    assert ("x" * 999) in joined
    assert ("x" * 50) in joined
    assert " x\"" not in joined or joined.count('d="x"') == 0  # the 1-char d not picked


def test_overlay_emits_fill_none_and_lobe_color_stroke():
    paths_by_lobe = {
        "frontal": [("p1", "M0,0 L10,10")],
        "parietal": [], "occipital": [], "temporal": [],
        "cerebellum": [], "brainstem": [],
    }
    colors = {
        "frontal":    "#F90001",
        "parietal":   "#34D399",
        "occipital":  "#FF652F",
        "temporal":   "#FFD23F",
        "cerebellum": "#22D3EE",
        "brainstem":  "#A78BFA",
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
```

- [ ] **Step 2: Run the tests — expect ImportError**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v -k overlay`
Expected: FAIL — `_build_lobe_stroke_overlay` not found.

- [ ] **Step 3: Add the helper to `brain.py`**

Add near the other helpers, before `_compose_wrapper`:

```python
def _build_lobe_stroke_overlay(
    paths_by_lobe: dict[str, list[tuple[str, str]]],
    lobe_colors: dict[str, str],
    n_per_lobe: int = 8,
) -> list[str]:
    """Build per-lobe duplicate <path/> elements for the stroke-draw animation.

    For each lobe, emit the top n_per_lobe paths (ranked by len(d), descending)
    as fresh <path> elements with:
      - d="<original d>" (geometry copied from the source path)
      - fill="none" + stroke=<lobe_color> + stroke-width=2.2
      - pathLength="100" + stroke-dasharray="100 100" (so dashoffset animation
        works without per-path length measurement)
      - class="lobe-stroke ls-<lobe>" (CSS keyframes provide the draw-in/out)

    The overlay layer (parent <g>) gets filter="url(#electricGlow)" applied
    once, not per-path.
    """
    out: list[str] = []
    for lobe, pairs in paths_by_lobe.items():
        if not pairs:
            continue
        color = lobe_colors[lobe]
        ranked = sorted(pairs, key=lambda p: len(p[1]), reverse=True)
        for _pid, d in ranked[:n_per_lobe]:
            out.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" '
                f'pathLength="100" stroke-dasharray="100 100" '
                f'class="lobe-stroke ls-{lobe}"/>'
            )
    return out
```

- [ ] **Step 4: Run the tests — expect PASS**

Run: `pytest packages/cortex-core/tests/test_brain_helpers.py -v`
Expected: all 19 tests pass.

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_helpers.py
git commit -m "feat(brain): _build_lobe_stroke_overlay — top-N paths as colored stroke <path/>"
```

---

## Task 7: Replace per-lobe gradient defs with `brainGrad_unified`

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (gradient defs in `_compose_wrapper`)

- [ ] **Step 1: Locate the gradient defs block**

In `packages/cortex-core/cortex/builders/brain.py`, find the `<defs>` section starting at line ~516. Note the existing defs:
- `<linearGradient id="brainGrad" ...>` (lines 517-526)
- `<linearGradient id="brainGradAlt" ...>` (lines 527-532)
- `<linearGradient id="brainGrad_frontal" ...>` through `brainGrad_brainstem` (lines 536-571)

These 8 gradient defs collectively represent the per-lobe color blocks we're removing.

- [ ] **Step 2: Replace the 8 gradient defs with one unified gradient**

Delete the entire block from `<linearGradient id="brainGrad"` through the closing `</linearGradient>` of `brainGrad_brainstem` (line 571). Replace with:

```python
    <linearGradient id="brainGrad_unified" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="30s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="25%"  stop-color="#1A0F35"/>
      <stop offset="50%"  stop-color="{p_accent_b}" stop-opacity="0.40"/>
      <stop offset="75%"  stop-color="#1A0F35"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
```

(`{p_accent_b}` is already in scope inside the f-string composing `_compose_wrapper`'s return value.)

- [ ] **Step 3: Build the brain to confirm SVG is still well-formed**

```bash
python -c "
from cortex.builders.brain import build
from cortex.schema import Config
import yaml, sys
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml')))
build(cfg, 'examples/rendered/extreme/brain-anatomical.svg')
print('OK')
"
```
Expected: `OK` and a valid SVG file. Open it in a browser briefly — the brain will look mostly broken (still has stale `url(#brainGrad_<lobe>)` references) but the file should parse.

- [ ] **Step 4: Commit (will be visually fixed in next task)**

```bash
git add packages/cortex-core/cortex/builders/brain.py
git commit -m "refactor(brain): replace 8 per-lobe gradients with brainGrad_unified def"
```

---

## Task 8: Wire `brainGrad_unified` through `_FILL_REPLACEMENTS` and `_recolor`

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (`_FILL_REPLACEMENTS` map + `_recolor` function)

- [ ] **Step 1: Update `_FILL_REPLACEMENTS` to point at the unified gradient**

In `packages/cortex-core/cortex/builders/brain.py`, replace the `_FILL_REPLACEMENTS` dict (lines 35-41):

```python
_FILL_REPLACEMENTS: dict[str, str] = {
    "#fff0cd": "url(#brainGrad_unified)",
    "#fdd99b": "url(#brainGrad_unified)",
    "#d9bb7a": "url(#brainGrad_unified)",
    "#ffffff": "url(#brainGrad_unified)",
    "#816647": "url(#brainGrad_unified)",
}
```

- [ ] **Step 2: Simplify `_recolor` — drop per-lobe substitution loop**

Replace the entire `_recolor` function (currently around lines 211-247) with:

```python
def _recolor(
    content: str,
    palette_primary: str,
    palette_secondary: str,
) -> str:
    """All source fills → brainGrad_unified; strokes → palette colors.

    The body fill is unified across the brain (single gradient on every path).
    Lobe identity is conveyed by the stroke-overlay layer added later in the
    composition, not by per-path fill substitution.
    """
    for old, new in _FILL_REPLACEMENTS.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"fill:{variant}", f"fill:{new}")

    strokes = _stroke_replacements(palette_primary, palette_secondary)
    for old, new in strokes.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"stroke:{variant}", f"stroke:{new}")
    return content
```

- [ ] **Step 3: Update the single `_recolor` call site in `build` to drop the `classification` arg**

In `build` (around line 797), change:

```python
recolored = _recolor(brain_group, palette["primary"], palette["secondary"], classification)
```

to:

```python
recolored = _recolor(brain_group, palette["primary"], palette["secondary"])
```

- [ ] **Step 4: Render the brain to confirm body is now muted unified gradient**

```bash
python -c "
from cortex.builders.brain import build
from cortex.schema import Config
import yaml
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml')))
build(cfg, '/tmp/brain-task8.svg')
print('OK')
"
```
Expected: `OK`. Open `/tmp/brain-task8.svg` in a browser. Brain should now read as one dark navy/indigo organ with a slow soft-purple sweep — no per-lobe red/green/orange blocks. Lobe outlines are not yet animated (that's Task 10).

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py
git commit -m "feat(brain): unify body fill — all paths render brainGrad_unified"
```

---

## Task 9: Add CSS keyframes for `lstroke` (lobe-outline draw animation)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (the `<style>` block in `_compose_wrapper`)

- [ ] **Step 1: Find the `<style>` block**

In `_compose_wrapper`, the `<style><![CDATA[` block starts around line 630 and ends at line 706 with `]]></style>`.

- [ ] **Step 2: Add the new keyframes and per-lobe class delays**

Find the existing `.lobe-arc` block (around line 680) and **above it** add:

```css
      /* Per-lobe stroke-draw overlay — duplicate paths above the body fill,
         each lobe's outline draws in over 1s, holds, draws out over 1s, rests.
         Six lobes staggered by 1s on a shared 6s cycle. */
      .lobe-stroke {{
        animation: lstroke 6s ease-in-out infinite;
        stroke-dashoffset: 100;
        opacity: 0;
      }}
      @keyframes lstroke {{
        0%   {{ stroke-dashoffset: 100; opacity: 0; }}
        16%  {{ stroke-dashoffset: 0;   opacity: 1; }}
        26%  {{ stroke-dashoffset: 0;   opacity: 1; }}
        43%  {{ stroke-dashoffset:-100; opacity: 0; }}
        100% {{ stroke-dashoffset:-100; opacity: 0; }}
      }}
      .ls-frontal    {{ animation-delay: 0s; }}
      .ls-parietal   {{ animation-delay: 1s; }}
      .ls-occipital  {{ animation-delay: 2s; }}
      .ls-temporal   {{ animation-delay: 3s; }}
      .ls-cerebellum {{ animation-delay: 4s; }}
      .ls-brainstem  {{ animation-delay: 5s; }}
```

(Note: this is inside an f-string — the existing CSS already uses `{{` / `}}` to escape literal braces. Match that style.)

- [ ] **Step 3: Verify the f-string compiles**

```bash
python -c "from cortex.builders.brain import _compose_wrapper; print('imports ok')"
```
Expected: `imports ok`. (If you see a `KeyError` on a missing brace escape, double-check that every `{` in the CSS you added is doubled to `{{`.)

- [ ] **Step 4: Commit (CSS only — overlay layer wired in next task)**

```bash
git add packages/cortex-core/cortex/builders/brain.py
git commit -m "feat(brain): add lstroke keyframes + per-lobe stagger delays in CSS"
```

---

## Task 10: Wire the stroke-overlay layer into the composition

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (`_compose_wrapper` body + composition section)

- [ ] **Step 1: Build the overlay list inside `_compose_wrapper`**

In `_compose_wrapper`, after the existing `_, lobe_centroids, lobe_bboxes, _ = _ensure_classification()` line (~313), unpack the fourth element and build the overlay:

Change this line:
```python
    _, lobe_centroids, lobe_bboxes = _ensure_classification()
```

to:
```python
    _, lobe_centroids, lobe_bboxes, paths_by_lobe = _ensure_classification()
```

(If you already changed it to `..., _ = _ensure_classification()` in Task 5, replace `_` with `paths_by_lobe`.)

Now find the place where `lobe_color_tokens` is defined (around line 448). Right after that block, build the overlay:

```python
    # Per-lobe stroke overlay — top 8 paths per lobe, duplicated as colored
    # stroke <path/> elements with stroke-dashoffset animation. Lobe identity
    # comes from this layer, not the body fill.
    lobe_stroke_overlay = _build_lobe_stroke_overlay(
        paths_by_lobe, lobe_color_tokens, n_per_lobe=8,
    )
```

- [ ] **Step 2: Insert the overlay layer in the SVG composition**

Find the composition block in the f-string return value (around lines 757-766):

```python
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        {brain_content}
        {chr(10).join("        " + rg for rg in region_glows)}
        {chr(10).join("        " + la for la in lobe_arcs)}
        {chr(10).join("        " + mc for mc in micro_cells)}
        {chr(10).join("        " + h for h in halos) if atm.show_halos else ""}
        {chr(10).join("        " + sd for sd in spark_dots)}
      </g>
    </g>
  </g>
```

Insert the overlay layer between `region_glows` and `lobe_arcs`:

```python
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        {brain_content}
        {chr(10).join("        " + rg for rg in region_glows)}
        <g class="lobe-stroke-layer" filter="url(#electricGlow)">
        {chr(10).join("          " + lso for lso in lobe_stroke_overlay)}
        </g>
        {chr(10).join("        " + la for la in lobe_arcs)}
        {chr(10).join("        " + mc for mc in micro_cells)}
        {chr(10).join("        " + h for h in halos) if atm.show_halos else ""}
        {chr(10).join("        " + sd for sd in spark_dots)}
      </g>
    </g>
  </g>
```

- [ ] **Step 3: Render and verify the lobe outlines now animate**

```bash
python -c "
from cortex.builders.brain import build
from cortex.schema import Config
import yaml
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml')))
build(cfg, '/tmp/brain-task10.svg')
"
```
Open `/tmp/brain-task10.svg` in a browser. You should see: muted unified body + lobe outlines drawing in/out in card colors on a 6s loop, staggered by 1s per lobe. Arcs are still the old fixed quadrilateral (replaced in Task 11).

- [ ] **Step 4: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py
git commit -m "feat(brain): stroke-overlay layer — animated lobe outlines in card colors"
```

---

## Task 11: Replace fixed-grid arcs and cells with random network

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py` (`_compose_wrapper`)

- [ ] **Step 1: Delete the fixed-grid generator**

In `_compose_wrapper`, find and delete the `_cells_for_bbox` function (around lines 463-475) and the loops that build `micro_cells` + `lobe_arcs` from it (around lines 477-502).

- [ ] **Step 2: Build the random network from helpers**

In place of the deleted code, add:

```python
    # Deterministic-but-disordered RNG seeded by the user's name. Same user → same
    # arc layout every render (so CI diffs of examples/rendered/ are stable across
    # builds); different users → unique signatures.
    rng = random.Random(_seed_from_name(config.identity.name))

    # 6 random cells per lobe inside its bbox.
    cells_by_lobe: dict[str, list[tuple[int, int]]] = {}
    for lobe in _LOBE_KEYS:
        bbox = lobe_bboxes.get(lobe)
        if bbox is None:
            continue
        cells_by_lobe[lobe] = _random_cells_in_bbox(bbox, n=6, rng=rng)

    # 20 random Bezier arcs across the union of all cells.
    arcs = _random_arc_network(cells_by_lobe, n=20, rng=rng,
                                lobe_colors=lobe_color_tokens)

    # Cells render as the existing .lobe-cell synaptic-flash, but at random
    # positions instead of bbox-corner quadrilateral.
    micro_cells: list[str] = []
    cell_offsets = (0.0, 0.6, 1.2, 1.8, 2.4, 3.0)  # 6 cells × 0.6s within-lobe stagger
    lobe_phase = {
        "frontal": 0.0, "parietal": 0.4, "occipital": 0.8,
        "temporal": 1.2, "cerebellum": 1.6, "brainstem": 2.0,
    }
    for lobe, cells in cells_by_lobe.items():
        color = lobe_color_tokens[lobe]
        phase = lobe_phase[lobe]
        for i, (cx, cy) in enumerate(cells):
            delay = phase + cell_offsets[i % len(cell_offsets)]
            micro_cells.append(
                f'<circle cx="{cx}" cy="{cy}" r="4" fill="{color}" '
                f'class="lobe-cell" style="animation-delay:{delay:.2f}s"/>'
            )

    # Arcs render as quadratic Bezier <path/> with the existing .lobe-arc keyframes
    # (arcflow + arcfade). The animation-delay/duration come from the random per-arc
    # values so the network reads as continuous firing.
    lobe_arcs: list[str] = []
    for a in arcs:
        lobe_arcs.append(
            f'<path d="M{a.x1},{a.y1} Q{a.cx},{a.cy} {a.x2},{a.y2}" '
            f'stroke="{a.color}" stroke-width="2.2" fill="none" '
            f'pathLength="100" stroke-dasharray="100 100" '
            f'class="lobe-arc" '
            f'style="animation-delay:{a.begin_s:.2f}s;animation-duration:{a.dur_s:.2f}s"/>'
        )
```

- [ ] **Step 3: Move `electricGlow` filter from per-element to per-layer**

The `.lobe-cell` rule currently has `filter: url(#electricGlow)`. We're moving the filter to a parent group (cheaper). Change the `.lobe-cell` CSS rule to remove the per-element filter:

Find (around line 673):
```css
      .lobe-cell {{ animation: lcell 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; opacity: 0; filter: url(#electricGlow); }}
```

Replace with:
```css
      .lobe-cell {{ animation: lcell 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; opacity: 0; }}
```

Now wrap the `lobe_arcs` and `micro_cells` emissions in a parent group with the filter applied. In the composition block, change:

```python
        {chr(10).join("        " + la for la in lobe_arcs)}
        {chr(10).join("        " + mc for mc in micro_cells)}
```

to:

```python
        <g class="arc-network" filter="url(#electricGlow)">
        {chr(10).join("          " + la for la in lobe_arcs)}
        {chr(10).join("          " + mc for mc in micro_cells)}
        </g>
```

- [ ] **Step 4: Render and verify random arcs**

```bash
python -c "
from cortex.builders.brain import build
from cortex.schema import Config
import yaml
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml')))
build(cfg, '/tmp/brain-task11.svg')
"
```
Open `/tmp/brain-task11.svg`. Arcs should now: be curved (Bezier), be visible (glowing), be distributed across the brain (some intra-lobe, some cross-lobe), and not form a regular quadrilateral grid.

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py
git commit -m "feat(brain): random Bezier arc network replaces fixed-grid quadrilateral"
```

---

## Task 12: Determinism integration test

**Files:**
- Create: `packages/cortex-core/tests/test_brain_integration.py`

- [ ] **Step 1: Write the integration test**

`packages/cortex-core/tests/test_brain_integration.py`:

```python
"""End-to-end build determinism — same input → byte-equal output."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cortex.builders.brain import build
from cortex.schema import Config


@pytest.fixture(scope="module")
def extreme_config() -> Config:
    """Load the extreme example config — known-good kitchen-sink config."""
    repo_root = Path(__file__).resolve().parents[3]  # src/
    config_path = repo_root / "examples" / "extreme.yml"
    return Config.model_validate(yaml.safe_load(config_path.read_text(encoding="utf-8")))


def test_build_is_deterministic(tmp_path: Path, extreme_config: Config) -> None:
    """Two builds with the same config produce byte-identical SVG output."""
    out_a = tmp_path / "a.svg"
    out_b = tmp_path / "b.svg"
    build(extreme_config, out_a)
    build(extreme_config, out_b)
    assert out_a.read_bytes() == out_b.read_bytes()


def test_build_output_is_well_formed_xml(tmp_path: Path, extreme_config: Config) -> None:
    """Built SVG parses as valid XML."""
    import xml.etree.ElementTree as ET

    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    # Will raise ParseError if malformed
    tree = ET.parse(out)
    root = tree.getroot()
    assert root.tag.endswith("svg")


def test_no_legacy_source_hex_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """The five legacy source-SVG fill hexes must all be substituted."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    for legacy in ("fill:#fff0cd", "fill:#fdd99b", "fill:#d9bb7a", "fill:#ffffff", "fill:#816647"):
        assert legacy not in text.lower(), f"legacy fill {legacy} not substituted"


def test_no_legacy_gradient_ids_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """Old gradient defs must be gone — only brainGrad_unified should remain."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    for legacy in ('id="brainGrad"', 'id="brainGradAlt"',
                    'id="brainGrad_frontal"', 'id="brainGrad_parietal"',
                    'id="brainGrad_occipital"', 'id="brainGrad_temporal"',
                    'id="brainGrad_cerebellum"', 'id="brainGrad_brainstem"'):
        assert legacy not in text, f"legacy gradient {legacy} still in output"
    assert 'id="brainGrad_unified"' in text


def test_overlay_layer_present_with_six_lobe_classes(tmp_path: Path, extreme_config: Config) -> None:
    """Stroke overlay must be wired in — one .ls-<lobe> class per lobe."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    assert 'class="lobe-stroke-layer"' in text
    for lobe in ("frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem"):
        assert f'ls-{lobe}' in text, f"missing overlay class for {lobe}"
```

- [ ] **Step 2: Run the integration tests**

Run: `pytest packages/cortex-core/tests/test_brain_integration.py -v`
Expected: 5 tests pass.

- [ ] **Step 3: Run the full test suite to confirm nothing else broke**

Run: `pytest -v`
Expected: all tests pass (19 helper unit tests + 5 integration tests = 24 total).

- [ ] **Step 4: Commit**

```bash
git add packages/cortex-core/tests/test_brain_integration.py
git commit -m "test(brain): determinism + well-formed-XML + legacy-substitution checks"
```

---

## Task 13: Regenerate showcase SVG and visual-eyeball check

**Files:**
- Modify: `examples/rendered/extreme/brain-anatomical.svg` (regenerated)

- [ ] **Step 1: Locate the showcase build script**

Look for the existing build script:

```bash
ls scripts/ examples/ .github/workflows/build-examples.yml 2>/dev/null
```

The script is referenced from `.github/workflows/build-examples.yml`. Read it to find the exact command (likely `python scripts/build_examples.py` or similar).

- [ ] **Step 2: Run the example builder**

```bash
python scripts/build_examples.py
```
(Substitute the actual command from step 1 if different.)

Expected: regenerates `examples/rendered/extreme/brain-anatomical.svg` (and other widget SVGs).

- [ ] **Step 3: Open in a browser and verify visually**

Open `examples/rendered/extreme/brain-anatomical.svg` in a browser. Confirm:
- [x] Brain body is muted (deep navy/indigo with a soft purple sweep), no per-lobe red/green/orange blocks
- [x] Lobe outlines visibly draw in/out in card colors on a loop, staggered (frontal first, brainstem last)
- [x] Arcs are curved Bezier, glowing, randomly distributed (not at the four corners of each lobe)
- [x] No hard-line color zones between adjacent lobes

If any of these fail, tune knobs in `brain.py`:
- Body too dark / lobe color invisible: raise `stop-opacity="0.40"` to `0.55` on the middle stop
- Stroke draw too fast / too slow: change `lstroke 6s` duration in CSS
- Arcs too busy: lower `n=20` to `n=15` in `_compose_wrapper`'s `_random_arc_network` call
- Arcs too quiet: raise `stroke-width="2.2"` to `2.6` in the `lobe_arcs` template

- [ ] **Step 4: Final commit**

```bash
git add examples/rendered/extreme/brain-anatomical.svg
git commit -m "chore(showcase): regenerate brain-anatomical.svg with professional visual pass"
```

- [ ] **Step 5: Verify CONTEXT.md auto-block doesn't need manual changes**

`CONTEXT.md` has an `<!-- AUTO:RECENT_COMMITS:START -->` block that's regenerated by `scripts/refresh_context.py` on push. No manual edit needed — the next push will refresh it.

---

## Self-Review

**Spec coverage:**
- Unified body gradient → Task 7 (defs) + Task 8 (substitution)
- Per-lobe stroke overlay (top-N paths, duplicated, animated draw) → Task 6 (helper) + Task 9 (CSS) + Task 10 (composition)
- Random arc network (deterministic, Bezier, electricGlow) → Tasks 2/3/4 (helpers) + Task 11 (composition)
- Random cells (replace fixed quadrilateral) → Task 3 (helper) + Task 11 (composition)
- Determinism via seed-from-name → Task 2 (helper) + Task 11 (wiring) + Task 12 (test)
- Filter on parent group not per-element → Task 10 (overlay layer) + Task 11 (arc-network layer)
- Tests directory bootstrap → Task 1
- Regenerated showcase SVG → Task 13

**Placeholder scan:** No `TBD`/`TODO`/"implement later" — every step contains the actual code or command.

**Type/name consistency:**
- `_seed_from_name` (str → int) used in Task 2 (defined), Task 11 (called)
- `_random_cells_in_bbox` (bbox, n, rng → list[tuple]) — Task 3 defines, Task 11 calls with the same signature
- `_random_arc_network` (cells_by_lobe, n, rng, lobe_colors → list[_Arc]) — Task 4 defines, Task 11 calls. Note keyword arg `lobe_colors=lobe_color_tokens` matches.
- `_Arc` field names — `x1, y1, x2, y2, cx, cy, color, begin_s, dur_s` — used consistently in Task 4 (define), Task 11 (`a.x1`, `a.cx`, `a.begin_s`, etc.)
- `_build_lobe_stroke_overlay` (paths_by_lobe, lobe_colors, n_per_lobe → list[str]) — Task 6 defines, Task 10 calls with `n_per_lobe=8`. ✓
- `_ensure_classification` returns 4-tuple — Task 5 changes signature, Task 10 unpacks all 4 (`paths_by_lobe`).
- `lobe_color_tokens` dict — defined once in `_compose_wrapper` (already exists, line ~448), used as `lobe_colors` arg to both `_random_arc_network` and `_build_lobe_stroke_overlay`. ✓

**Cleanup verified:**
- `_cells_for_bbox` deleted in Task 11 (was the source of the fixed-grid quadrilateral)
- `_FILL_REPLACEMENTS` updated in Task 8 (no stale gradient names)
- `classification` arg removed from `_recolor` in Task 8 (no stale call sites — `build` is the only caller)
