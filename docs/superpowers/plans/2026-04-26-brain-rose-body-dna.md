# Brain — Rose Body, Wave Lobes & DNA Helixes Implementation Plan (Round 4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Replace the bold per-lobe color blocks with thin sweeping color waves over a slowly-cycling rose body. Remove the perspective grid. Add 4 DNA double-helix symbols in canvas corners that fade in (drawing in via `stroke-dashoffset`) and out on staggered 16s cycles.

**Architecture:** All edits land in `packages/cortex-core/cortex/builders/brain.py`. Per-lobe gradients keep the same id names and per-lobe rotation periods from R3, but with new stop offsets and opacity. New `_dna_helix_paths` helper (math-based, deterministic). DNA blocks are pre-computed Python strings injected into the f-string composition.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-rose-body-dna-design.md`.

---

## Task 1: Rose body + thin wave lobe gradients

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1.1: Update `bgRadial`'s inner stops to rose

Find the `<radialGradient id="bgRadial">` def in `_compose_wrapper`'s `<defs>` block. Currently the first two stops are:
```
<stop offset="0%"   stop-color="#180826"/>
<stop offset="60%"  stop-color="#080410"/>
```
Change to:
```
<stop offset="0%"   stop-color="#280816"/>
<stop offset="60%"  stop-color="#100308"/>
```
Keep the 100% stop (`stop-color="{p_background}"`) unchanged.

### Step 1.2: Rewrite `brainGrad_unified` with rose-family stops

Find the `<linearGradient id="brainGrad_unified">` def. Replace the entire stop list with rose-family stops cycling through close hues, full opacity, rotating 40s:

```
    <linearGradient id="brainGrad_unified" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="40s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="33%"  stop-color="#4D2438"/>
      <stop offset="66%"  stop-color="#5C2E45"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

The existing dur was 30s; change to 40s. The middle stop (was `{p_accent_b}` at 0.30 opacity) is replaced with rose-family colors at full opacity.

### Step 1.3: Rewrite all 6 per-lobe gradients with thin-wave stops

Each per-lobe gradient (`brainGrad_frontal`, `_parietal`, `_occipital`, `_temporal`, `_cerebellum`, `_brainstem`) needs its stop list rewritten. The new pattern is:
- 0%: `#3A1A28` (rose base, full opacity)
- 45%: `#3A1A28` (rose base, full opacity — extended dark zone before band)
- 50%: lobe color, `stop-opacity="0.40"` (the thin band peak)
- 55%: `#3A1A28` (rose base, full opacity — extended dark zone after band)
- 100%: `#3A1A28` (rose base, full opacity)

Keep the existing rotation animations (they're correct — frontal=20s, parietal=23s, occipital=17s, temporal=25s, cerebellum=19s, brainstem=27s).

Concretely, each gradient becomes:

```
    <linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="20s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_primary}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

Apply the same pattern to all 6 lobes, swapping the lobe color and the `dur`:
- `brainGrad_parietal`: `{p_accent_d}`, `dur="23s"`
- `brainGrad_occipital`: `{p_secondary}`, `dur="17s"`
- `brainGrad_temporal`: `{p_accent_c}`, `dur="25s"`
- `brainGrad_cerebellum`: `{p_accent_a}`, `dur="19s"`
- `brainGrad_brainstem`: `{p_accent_b}`, `dur="27s"`

### Step 1.4: Smoke build + verify

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify in the output SVG:
- `grep -c '#3A1A28' examples/rendered/extreme/brain-anatomical.svg` ≥ 35 (rose stop appears in unified def + 6 lobe defs × ~4 stops + bgRadial reference — total 25-40)
- `grep -c '#280816\|#100308' examples/rendered/extreme/brain-anatomical.svg` ≥ 2 (bgRadial inner stops)
- `grep -c 'stop-opacity="0.40"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6 (one per lobe gradient)
- `grep -c 'offset="45%"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6
- `grep -c 'offset="55%"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6
- `grep -c 'dur="40s"' examples/rendered/extreme/brain-anatomical.svg` ≥ 1 (the new unified rotation)
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical

### Step 1.5: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): rose body + thin wave per-lobe gradients"
```

---

## Task 2: Remove the perspective grid

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 2.1: Delete the gridFade gradient + gridMask def

In `_compose_wrapper`'s `<defs>` block, find and DELETE the entire `<radialGradient id="gridFade">` block AND the entire `<mask id="gridMask">` block. Use grep to locate:
```bash
grep -n "gridFade\|gridMask" packages/cortex-core/cortex/builders/brain.py
```
After deletion, the only remaining hits should be 0.

### Step 2.2: Delete the `grid_lines` Python prep block

Find and DELETE the entire Python loop that builds `grid_lines: list[str] = []` and populates it via `for x in range(80, 1400, 80)` and `for y in range(80, 900, 80)`. Use grep:
```bash
grep -n "grid_lines" packages/cortex-core/cortex/builders/brain.py
```

### Step 2.3: Delete the `<g class="grid">` block from SVG composition

In the f-string return value, find and DELETE the entire grid block. It looks like:

```
  {('''<!-- Perspective grid: 80px grid lines, edge-faded via radial mask, slow drift. -->
  <g class="grid" mask="url(#gridMask)">
    <g>
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 40,30; 0,0" dur="50s" repeatCount="indefinite"/>
  ''' + chr(10).join("      " + ln for ln in grid_lines) + '''
    </g>
  </g>''') if atm.show_aura else ""}
```

Delete the entire f-string ternary (from `{(` through `else ""}`).

### Step 2.4: Smoke build + verify

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify in the output SVG:
- `grep -c 'class="grid"' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'gridFade\|gridMask' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'class="stars"\|class="nebulae"\|class="aurora"\|class="constellation"\|class="streaks"' examples/rendered/extreme/brain-anatomical.svg` = 5 (the 5 OTHER atmospheric layers still present — NO 'grid' in this list)
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical

### Step 2.5: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): remove perspective grid (clashed with organic atmosphere)"
```

---

## Task 3: Add DNA helix symbols

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 3.1: Add `_dna_helix_paths` helper

Place this helper near the other classification/path helpers (e.g., after `_build_lobe_stroke_overlay` and before `_classify_brain_paths`). Add the `import math` at the top of the file if not already imported:

```python
def _dna_helix_paths(
    cx: int, cy: int,
    width: int = 80, height: int = 170,
    samples: int = 24,
) -> tuple[str, str, list[tuple[tuple[int, int], tuple[int, int]]]]:
    """Generate two intertwining sine paths + base-pair rung connectors.

    Returns (strand_a_path_d, strand_b_path_d, rungs).
    Strand A: cosine wave (one phase). Strand B: -cosine (anti-phase, mirrored).
    Rungs: horizontal connectors at every 6th sample point (excluding endpoints).
    """
    import math

    points_a: list[tuple[int, int]] = []
    points_b: list[tuple[int, int]] = []
    rungs: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(samples + 1):
        t = i / samples
        y = round(cy + (t - 0.5) * height)
        offset = round(math.cos(t * 2 * math.pi * 2) * (width / 2))
        ax = cx + offset
        bx = cx - offset
        points_a.append((ax, y))
        points_b.append((bx, y))
        if i % 6 == 0 and i not in (0, samples):
            rungs.append(((ax, y), (bx, y)))

    strand_a = "M" + " L".join(f"{x},{y}" for x, y in points_a)
    strand_b = "M" + " L".join(f"{x},{y}" for x, y in points_b)
    return strand_a, strand_b, rungs
```

### Step 3.2: Build the 4 DNA blocks (Python prep in `_compose_wrapper`)

In `_compose_wrapper`, after `nebula_blocks` is built (or near other prep code), add:

```python
    # DNA helix symbols — 4 double-helix line drawings at canvas corners,
    # each fading in/out + drawing in via stroke-dashoffset on staggered 16s
    # timers. Reads as a scientific/biological motif tying the brain theme
    # to the organic atmosphere (no longer competing with the digital grid,
    # which was removed in this round).
    dna_specs = [
        (120, 120,  "#22D3EE", 0),    # top-left,    cyan,   delay 0s
        (1280, 120, "#EC4899", 4),    # top-right,   pink,   delay 4s
        (120, 780,  "#7C3AED", 8),    # bottom-left, purple, delay 8s
        (1280, 780, "#22D3EE", 12),   # bottom-right, cyan,  delay 12s
    ]
    dna_blocks: list[str] = []
    for cx_d, cy_d, dcolor, ddelay in dna_specs:
        strand_a, strand_b, rungs = _dna_helix_paths(cx_d, cy_d)
        rung_lines = "\n".join(
            f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
            f'stroke="{dcolor}" stroke-width="0.8" stroke-opacity="0.5"/>'
            for a, b in rungs
        )
        dna_blocks.append(
            f'<g class="dna" style="animation-delay:{ddelay}s">\n'
            f'    <path d="{strand_a}" stroke="{dcolor}" stroke-width="1.5" '
            f'fill="none" stroke-opacity="0.7" pathLength="100" '
            f'stroke-dasharray="100 100" class="dna-strand"/>\n'
            f'    <path d="{strand_b}" stroke="{dcolor}" stroke-width="1.5" '
            f'fill="none" stroke-opacity="0.7" pathLength="100" '
            f'stroke-dasharray="100 100" class="dna-strand"/>\n'
            f'{rung_lines}\n'
            f'  </g>'
        )
```

### Step 3.3: Add CSS keyframes for DNA fade + draw

In the `<style>` block, add (anywhere — recommended near the other atmospheric animations like `.far-star`):

```
      .dna {{
        opacity: 0;
        animation: dnaFade 16s ease-in-out infinite;
        transform-origin: center;
        transform-box: fill-box;
      }}
      @keyframes dnaFade {{
        0%, 100% {{ opacity: 0; }}
        10%      {{ opacity: 0; }}
        25%      {{ opacity: 0.85; }}
        50%      {{ opacity: 0.85; }}
        65%      {{ opacity: 0; }}
      }}
      .dna-strand {{
        animation: dnaDraw 16s ease-in-out infinite;
      }}
      @keyframes dnaDraw {{
        0%   {{ stroke-dashoffset: 100; }}
        25%  {{ stroke-dashoffset: 0; }}
        50%  {{ stroke-dashoffset: 0; }}
        65%  {{ stroke-dashoffset: -100; }}
        100% {{ stroke-dashoffset: -100; }}
      }}
```

### Step 3.4: Wire DNA blocks into the SVG composition

In the f-string return value, find the existing `<g class="nebulae">` block (added in R3-2). Insert the DNA composition block IMMEDIATELY AFTER the nebulae block (before aurora bands), gated by `atm.show_aura`:

```
  {('''<!-- DNA helix symbols at canvas corners — fade in/out + draw in
       on staggered 16s timers. 1-2 visible at any moment, others hidden. -->
  <g class="dna-helixes">
  ''' + chr(10).join("    " + db for db in dna_blocks) + '''
  </g>''') if atm.show_aura else ""}
```

### Step 3.5: Smoke build + verify

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="dna-helixes"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'class="dna"' examples/rendered/extreme/brain-anatomical.svg` = 4
- `grep -c 'class="dna-strand"' examples/rendered/extreme/brain-anatomical.svg` = 8 (2 strands × 4 helixes)
- `grep -c '@keyframes dnaFade' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c '@keyframes dnaDraw' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'animation-delay:0s' examples/rendered/extreme/brain-anatomical.svg` ≥ 1 (at least the first DNA)
- `grep -c 'animation-delay:4s' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'animation-delay:8s' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'animation-delay:12s' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `python -m pytest -q` → 24 passed
- XML well-formed
- Two builds → byte-identical

### Step 3.6: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): DNA helix symbols at corners — fade + draw atmospheric motif"
```

---

## Task 4: Final regen + verification

This task is the closing sweep.

### Step 4.1: Final regen + ruff + tests

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
python -m ruff check packages/cortex-core/cortex/builders/brain.py
python -m pytest
```

Expected: build succeeds, ruff clean, 24 tests pass.

### Step 4.2: Determinism final check

```bash
python -c "
import yaml, os
from cortex.builders.brain import build
from cortex.schema import Config
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml', encoding='utf-8')))
out_a = os.path.expanduser('~/r4-a.svg')
out_b = os.path.expanduser('~/r4-b.svg')
build(cfg, out_a)
build(cfg, out_b)
import filecmp
print('identical:', filecmp.cmp(out_a, out_b, shallow=False))
"
```
Expected: `identical: True`.

### Step 4.3: Final structural verification

```bash
grep -c 'class="dna-helixes"\|class="stars"\|class="nebulae"\|class="aurora"\|class="constellation"\|class="streaks"' examples/rendered/extreme/brain-anatomical.svg
```
Expected: 6 (six atmospheric layer parents — no grid).

```bash
grep -c 'class="grid"' examples/rendered/extreme/brain-anatomical.svg
```
Expected: 0.

### Step 4.4: No commit needed (showcase already regenerated in Tasks 1-3)

Verify with `git status` — working tree should be clean. If not, run `cortex build` once more and commit any final showcase drift.

---

## Self-Review

**Spec coverage:**
- Rose body + thin wave lobes → Task 1 (with bgRadial tint)
- Remove grid → Task 2
- Add DNA helixes → Task 3
- Final verification → Task 4

**Type/name consistency:**
- `_dna_helix_paths(cx, cy, width=80, height=170, samples=24) -> tuple[str, str, list[tuple[tuple[int,int], tuple[int,int]]]]` defined in Task 3.1; called with positional `cx_d, cy_d` in Task 3.2.
- `dna_specs` list of 4 tuples; `dna_blocks` list of f-strings.
- All 6 lobe gradients use the same 5-stop pattern with offsets 0/45/50/55/100.

**Placeholder scan:** No `TBD` / `<insert>` / `TODO` left.

**Cleanup verified:**
- gridFade + gridMask + grid_lines + `<g class="grid">` all deleted in Task 2.
- Old per-lobe stop pattern (40/60 offsets at 0.45 opacity) is replaced by new pattern in Task 1.3.
