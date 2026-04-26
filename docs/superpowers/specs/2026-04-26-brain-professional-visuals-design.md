# Brain — Professional Visual Pass (Unified Body + Stroke Overlay + Random Arcs)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Touches (rendered):** `examples/rendered/extreme/brain-anatomical.svg` (auto-regenerated)

## Why this exists

The neon-rainbow brain currently paints six saturated colors as solid fills across six adjacent lobes. The eye reads it as a paint-by-numbers anatomy poster, not a data visualization. Three specific failures:

1. **Bold per-lobe color blocks dominate the brain** — six fully-saturated hues (red/green/orange/yellow/cyan/purple) at 100% fill on adjacent regions.
2. **No animated outline glow in card colors** — strokes are flat and global, not per-lobe and not animated.
3. **Electric arcs repeat at the same fixed grid positions** — `_cells_for_bbox` hard-codes 25%/75% corners of each lobe bbox; the four arcs always form the same clockwise quadrilateral.

The redesign moves the lobe identity from the fill channel to a stroke-overlay channel, demotes the fill to a single unified atmospheric gradient, and replaces the deterministic arc grid with a deterministic-but-disordered random arc network.

## What "professional" means here (visual targets)

- **Unified organ, not six color zones.** The brain reads as one body with a slow living color sweep across it — not as six adjacent solid-color regions.
- **Per-lobe identity comes from animated edge glow, not fill color.** Each lobe lights up its outline in its card's accent color, draws in over ~1s, holds, draws out, rests, and repeats — six lobes staggered.
- **Electric activity reads as lightning across the cortex.** Cross-lobe and intra-lobe arcs at randomized positions, randomized timing, randomized curvature — visible glow, no perceptible grid.

## Scope

**In scope:** All edits land in `packages/cortex-core/cortex/builders/brain.py`. Behavior is gated on the existing `config.brain.atmosphere` flags where applicable; no new schema fields.

**Out of scope:**
- Other widgets (tech-cards, current-focus, yearly-highlights) — extending this language to them is a separate ticket already noted in `CONTEXT.md`.
- New `cortex.yml` schema fields. The unified gradient and overlay are unconditional.
- Wiring `typography.scale` / `animations.speed` (separate pending work).
- Changing the source SVG or classification logic.

## Architecture (three coordinated changes)

### Change 1 — Unified body gradient (replaces per-lobe fills)

**Today:** six `linearGradient` defs `brainGrad_<lobe>`, each going `<accent> → #EC4899 → <accent>`, rotating on independent periods. Per-lobe `fill:url(#brainGrad_<lobe>)` substitution in `_recolor()`.

**New:** a single `linearGradient id="brainGrad_unified"` applied to every brain path. Stops:

```
0%   #0E0820              (deep navy, near-black)
25%  #1A0F35              (muted indigo)
50%  <p_accent_b> @ 0.40   (palette accent, low opacity via stop-opacity)
75%  #1A0F35              (muted indigo)
100% #0E0820              (deep navy, near-black)
```

Animated via `<animateTransform attributeName="gradientTransform" type="rotate" from="0 0.5 0.5" to="360 0.5 0.5" dur="30s" repeatCount="indefinite"/>` — the band sweeps once every 30s.

`_recolor()` is simplified: per-lobe substitution loop is removed; the global `_FILL_REPLACEMENTS` map points all source fills (`#fff0cd`, `#fdd99b`, `#d9bb7a`, `#ffffff`, `#816647`) at `url(#brainGrad_unified)`.

The six per-lobe `brainGrad_<lobe>` defs are deleted. `brainGrad` and `brainGradAlt` (the legacy fallbacks) are also deleted — nothing references them after this change.

**Why these stops:** mostly dark with one band of palette color at 40% opacity. The brain reads as a deep purple-black organ with a slow indigo→accent→indigo sweep traveling around it. No solid color blocks anywhere.

### Change 2 — Per-lobe stroke overlay (replaces flat global strokes for the lobe-identity channel)

**Today:** strokes use `palette_primary` globally (every brain path has the same brown-replaced outline color). No animation.

**New:** a *second pass* over the brain content that emits, **per lobe, the N largest paths** (ranked by `len(d)`) as fresh `<path>` elements with minimal attributes:

- `d="<original d>"` (copied from the source path)
- `fill="none"`
- `stroke="<card-color>"` (frontal=primary, parietal=accent_d, occipital=secondary, temporal=accent_c, cerebellum=accent_a, brainstem=accent_b — same mapping as `lobe_color_tokens` today)
- `stroke-width="2.2"` (renders ~1.5px after the 0.7 brain transform)
- `pathLength="100"` (so we can use a fixed dasharray without measuring)
- `stroke-dasharray="100 100"`
- `class="lobe-stroke ls-<lobe>"`

The filter is applied **to the parent group** `<g class="lobe-stroke-layer" filter="url(#electricGlow)">`, not per-path — single filter pass over the whole layer (~10× cheaper than per-element).

**Why duplicated `<path>` and not `<use href>`:** the source SVG paths carry `style="fill:..."` inline. SVG cascade rules give inline `style` higher specificity than properties inherited from `<use>`, so `<use stroke="red" fill="none">` would *not* reliably override `style="fill:X"` on the referenced path across renderers (especially GitHub's SVG sanitizer). Duplicating the path with explicit attributes is bulletproof.

**Why "N largest paths per lobe" not all paths:** each lobe has 25–50 source paths; most are tiny gyri details. Rendering all of them in stroke-overlay produces a busy outlined mess that fights the body fill. The N largest paths (by `d`-attribute length, a good proxy for path size) capture the major outline strokes that *read* as "this is the frontal lobe" with much less overdraw and far less file growth. Default `N=8`.

CSS animation per `.lobe-stroke`:

```css
@keyframes lstroke {
  0%     { stroke-dashoffset: 100; opacity: 0; }   /* invisible, ready to draw */
  16%    { stroke-dashoffset: 0;   opacity: 1; }   /* fully drawn (1s in) */
  26%    { stroke-dashoffset: 0;   opacity: 1; }   /* hold (0.6s) */
  43%    { stroke-dashoffset:-100; opacity: 0; }   /* drawn out (1s out) */
  100%   { stroke-dashoffset:-100; opacity: 0; }   /* rest (3.4s) */
}
.lobe-stroke { animation: lstroke 6s ease-in-out infinite; }
.ls-frontal    { animation-delay: 0s; stroke: var(--c-frontal); }   /* but inlined as stroke="..." */
.ls-parietal   { animation-delay: 1s; }
.ls-occipital  { animation-delay: 2s; }
.ls-temporal   { animation-delay: 3s; }
.ls-cerebellum { animation-delay: 4s; }
.ls-brainstem  { animation-delay: 5s; }
```

Six lobes × 1s stagger = all 6 lobes in flight at any moment, each at a different phase of the same 6s cycle. The stroke "draws in," holds, "draws out," then rests — looped.

**Why an overlay layer rather than mutating the existing strokes:** the body fill needs *unified, muted, slow*. The lobe identity needs *card-colored, animated, per-lobe*. These two channels can't share a stroke attribute on the same element. The overlay duplicates only the path geometry needed for the visual outline — the largest 8 paths per lobe — and leaves the rest of the lobe (the small gyri detail paths) showing only the muted body fill underneath.

**Implementation note:** `_iter_paths()` already gives us `(id, d)` pairs from a group fragment. During classification we cache the `(id, d)` pairs per lobe (lazy add to `_ensure_classification`'s cache), then `_build_lobe_stroke_overlay` ranks by `len(d)`, takes the top 8, and emits fresh `<path>` elements as a sibling layer above `{brain_content}` inside the wobble group.

### Change 3 — Randomized arc network (replaces fixed quadrilateral grid)

**Today:** `_cells_for_bbox` returns 4 fixed cells at 25%/75% corners. 4 arcs per lobe form a clockwise quadrilateral. 6 lobes × 4 arcs = 24 visible arcs always at the same positions, always at lobe-bbox edges.

**New:**

1. **Random cell pool per lobe.** New helper `_random_cells_in_bbox(bbox, n=6, rng) -> list[(int,int)]`. Pulls 6 positions from each lobe's bbox, each with random `(0.15..0.85, 0.15..0.85)` normalized offset. We keep cells *inside* the lobe but distributed organically.

2. **Random arc network across the brain.** New helper `_random_arc_network(cells_by_lobe, n=20, rng) -> list[Arc]`. Pulls 20 random pairs from the union of all cells. Mix is naturally ~70% intra-lobe / ~30% cross-lobe (because most random pairs land in adjacent lobes by population). Each arc has:
   - random midpoint offset `(±60px, ±60px)` from the line midpoint, used as the `Q` control point in a quadratic Bezier `M x1,y1 Q cx,cy x2,y2`
   - random `begin_s` in `[0, 12)` window — arcs fire continuously across a 12s pattern
   - random `dur_s` in `[0.8, 1.6)`
   - color = the source cell's lobe color

3. **Render & glow.** Arcs become `<path d="M ... Q ... ..." stroke="<color>" stroke-width="2.2" fill="none" pathLength="100" stroke-dasharray="100 100" filter="url(#electricGlow)" class="lobe-arc"/>` with inlined `style="animation-delay:<begin_s>s; animation-duration:<dur_s>s;"`. The existing `.lobe-arc` keyframes (`arcflow` + `arcfade`) keep working but now drive a randomized-position arc.

4. **Determinism.** Seed: `random.Random(int(hashlib.sha256(name.encode()).hexdigest()[:8], 16))`. Same user → same arc layout every render. Different user → different signature.

**Why deterministic:** CI diffs `examples/rendered/extreme/brain-anatomical.svg` between commits. A non-deterministic generator would make every push churn the entire arc layer.

**Why 20:** current is 24 but mostly invisible because they're thin and concentrated at lobe edges. 20 brighter, glowing, randomly-distributed arcs read as a higher-energy network because each one is individually visible.

The micro-cells (4 per lobe → 6 per lobe) keep their existing `.lobe-cell` keyframes; they're still the "synaptic flash" anchor points but no longer locked to bbox corners.

## Data flow (after changes)

```
config.yml
  ↓
build()
  ├─ classification = _ensure_classification()  (extended: now also caches paths_by_lobe = {lobe: [(id, d), ...]})
  │     → lobe_path_ids, lobe_centroids, lobe_bboxes, paths_by_lobe
  ├─ recolor(brain_group, ...)                  (simpler: all paths → brainGrad_unified)
  │     → unified_brain_content
  ├─ overlay = _build_lobe_stroke_overlay(paths_by_lobe, lobe_color_tokens, n_per_lobe=8)   ← NEW
  ├─ rng = random.Random(_seed_from_name(config.identity.name))   ← NEW
  ├─ cells_by_lobe = {lobe: _random_cells_in_bbox(bbox, 6, rng) for lobe, bbox in lobe_bboxes.items()}
  ├─ arcs = _random_arc_network(cells_by_lobe, n=20, rng, lobe_color_tokens)
  └─ _compose_wrapper(...)
        ↓
        emits in order inside the wobble group:
          1. unified_brain_content              (filled body, muted)
          2. region_glows                       (existing screen-blend tints)
          3. lobe_stroke_overlay                ← NEW (animated card-colored outlines)
          4. arcs (randomized)                  ← REPLACED
          5. micro_cells (random positions)     ← MODIFIED (positions are now random)
          6. halos, spark_dots                  (unchanged)
```

## File structure / new helpers

All new code lives in `brain.py`. No new modules.

```python
# Near the existing classification helpers
def _random_cells_in_bbox(
    bbox: tuple[float, float, float, float],
    n: int,
    rng: random.Random,
) -> list[tuple[int, int]]:
    """n cells inside bbox at random normalized offsets in [0.15, 0.85]."""

@dataclass(frozen=True)
class _Arc:
    x1: int; y1: int; x2: int; y2: int
    cx: int; cy: int          # quadratic Bezier control point
    color: str
    begin_s: float
    dur_s: float

def _random_arc_network(
    cells_by_lobe: dict[str, list[tuple[int, int]]],
    n: int,
    rng: random.Random,
    lobe_colors: dict[str, str],
) -> list[_Arc]:
    """n random pairs from the union of all cells, with random Bezier control offsets."""

def _build_lobe_stroke_overlay(
    paths_by_lobe: dict[str, list[tuple[str, str]]],   # lobe -> [(id, d), ...]
    lobe_colors: dict[str, str],
    n_per_lobe: int = 8,
) -> list[str]:
    """Return per-lobe duplicate <path/> elements (top N by len(d)) for the
    stroke-draw animation. fill='none' + colored stroke + class for keyframes."""

def _seed_from_name(name: str) -> int:
    """Stable 32-bit seed derived from the user's identity name."""
```

## SVG composition order (inside wobble group)

```xml
<g transform="translate(332,152) scale(0.7)">
  <g class="brain-pulse" filter="url(#brainGlow)">
    <g class="brain-3d">                           <!-- existing -->
      {unified_brain_content}                      <!-- filled body, muted gradient -->
      {region_glows}                               <!-- existing screen-blend tints -->
      <g class="lobe-stroke-layer">                <!-- NEW -->
        {lobe_stroke_overlay}                      <!-- animated colored outlines -->
      </g>
      <g class="arc-network">                      <!-- REPLACES today's lobe_arcs grid -->
        {randomized_arcs}
      </g>
      {micro_cells}                                <!-- existing keyframes, NEW positions -->
      {halos}                                      <!-- gated on atm.show_halos, unchanged -->
      {spark_dots}                                 <!-- unchanged -->
    </g>
  </g>
</g>
```

## Defaults (locked in)

| Knob | Value | Rationale |
|---|---|---|
| Body gradient stops | `#0E0820 → #1A0F35 → <accent_b>@40% → #1A0F35 → #0E0820` | Mostly dark, one muted accent band |
| Body sweep duration | 30s | Slow enough to read as living, not distracting |
| Stroke overlay width | 2.2px | Renders ~1.5px after 0.7 transform |
| Stroke draw cycle | 6s (1s in / 0.6s hold / 1s out / 3.4s rest) | Each lobe spends most time invisible — punctuation, not background |
| Stroke stagger | 1s per lobe | All 6 in flight, each at a different phase |
| Cells per lobe | 6 (was 4) | Larger pool for the arc network to draw from |
| Arcs in network | 20 (was 24) | Each is bigger and glowing, total energy is higher |
| Arc Bezier control offset | ±60px from midpoint | Visible curvature, not straight |
| Arc begin window | [0, 12)s | Continuous firing across a 12s pattern |
| Arc duration | [0.8, 1.6)s | Quick electric pulse |
| RNG seed | sha256(`identity.name`)[:8] as int | Deterministic per user, unique per user |
| Overlay paths per lobe | 8 (largest by `len(d)`) | Major outline strokes only, no gyri overdraw |

## Animation budget impact

- Removing per-lobe + legacy gradient rotations: 6 `brainGrad_<lobe>` + 1 `brainGrad` = **−7 `<animateTransform>`**
- Adding 1 `<animateTransform>` for the unified gradient rotation = **+1**
- Stroke overlay: pure CSS animation (one `@keyframes lstroke` shared by ~200 `<use>` elements) → 1 keyframes def, **no SMIL added**
- Arc network: 20 `<path>` elements reuse the existing `arcflow` + `arcfade` keyframes → **no new keyframes**, 20 elements
- Net: **−6 SMIL animations**. The per-lobe SMIL rotations collapse to a single one + the overlay is CSS-only. Net rendering budget improves.

## File-size impact

- Stroke overlay: 6 lobes × 8 paths × ~400 bytes each (d attr is most of each path's bytes) ≈ **+19 KB**
- Arc network: 20 paths × ~140 bytes ≈ **+2.8 KB**
- Removed defs: 6 per-lobe gradients + 2 legacy gradients (`brainGrad`, `brainGradAlt`) ≈ 8 × ~250 bytes ≈ **−2.0 KB**
- **Net: ~+20 KB on a 70 KB file** (~28% growth). Acceptable for the visual gain — the unified body and the animated lobe strokes are doing the heavy lifting visually.

## Testing plan

- **Unit:**
  - `_seed_from_name("foo") == _seed_from_name("foo")` (determinism)
  - `_seed_from_name("foo") != _seed_from_name("bar")` (uniqueness)
  - `_random_cells_in_bbox` returns `n` cells, all inside bbox
  - `_random_arc_network` returns `n` arcs, all referencing valid cells
  - `_build_lobe_stroke_overlay` returns `n_per_lobe` paths per lobe (or fewer if the lobe has fewer paths total), all with `fill="none"` and `stroke=<lobe_colors[lobe]>`
  - Top-N selection: a lobe with paths of `len(d)` = [10, 100, 50, 200, 30] and `n_per_lobe=2` returns the paths with `d` of length 200 and 100
- **Integration:**
  - Build the brain SVG twice with the same config → byte-identical output (determinism check)
  - Build with `palette=neon-rainbow` and `palette=monochrome` → both produce valid XML and `_FILL_REPLACEMENTS` substitution leaves no `#fff0cd`, `#fdd99b`, `#d9bb7a`, `#ffffff`, `#816647` literals in the rendered output
  - Build the `extreme` example → SVG validates as well-formed XML
- **Visual:**
  - Render the `extreme` example with the existing `scripts/build_examples.py` (or equivalent) and eyeball against `.claude/brain-phase-c-native.png` baseline
  - Confirm: no per-lobe color blocks, lobe outlines visibly draw in/out in card colors, arcs are visibly distributed across the brain (not at bbox corners)
- **CI:** `examples/rendered/extreme/brain-anatomical.svg` will be regenerated by the existing `build-examples.yml` workflow. The diff will be large (overlay layer added, arcs randomized) but stable across reruns thanks to the seed.

## Migration & backward compatibility

- No public API change. `build(config, output)` signature is unchanged.
- No schema change. No `cortex.yml` files break.
- The `_FILL_REPLACEMENTS` map keeps its keys (the legacy hex values from the source SVG); only the values change to point at `brainGrad_unified`.
- `brainGrad`, `brainGradAlt`, and `brainGrad_<lobe>` defs are deleted; `_FILL_REPLACEMENTS` no longer references them. Quick search for any external reference: none expected — they're internal to the wrapper template.
- `_LOBE_BBOXES` cache is still used (by `_random_cells_in_bbox`).
- `_LOBE_PATH_IDS` cache is now used by both `_recolor` (still, for any future reasons we want path-level fill selection) and `_build_lobe_stroke_overlay` (new).

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Stroke overlay doubles render cost in browsers | We're already at ~200 paths; doubling is ~400. Within reason for SMIL/CSS browsers. README markdown renderers (GitHub) animate fine. |
| Random arc network looks "noisy" rather than "purposeful" | Tunable: lower `n` from 20 → 12 if too busy; raise stroke-width if too quiet. The seeded determinism means we can iterate visually without losing reproducibility. |
| `pathLength="100"` with `stroke-dasharray="100 100"` doesn't quite cover a path because of edge cases in renderers | Fallback: `stroke-dasharray="120 120"` (overshoot). Negligible visual difference. |
| `feMorphology + feGaussianBlur` electric-glow filter on 200+ stroke paths is expensive | Apply the filter to the *parent group* `<g class="lobe-stroke-layer" filter="url(#electricGlow)">` instead of per-path. Single filter pass over the whole layer. |

## Implementation order (for the plan that follows)

1. Add `_seed_from_name`, `_random_cells_in_bbox`, `_Arc`, `_random_arc_network`, `_build_lobe_stroke_overlay`. Unit-test the helpers.
2. Update `_recolor()` to map all source fills to `brainGrad_unified`. Delete per-lobe substitution loop.
3. Update `_compose_wrapper`:
   - Replace 6 per-lobe gradient defs with 1 unified gradient def
   - Build the stroke overlay layer; insert above `{brain_content}` and below `{region_glows}` (or above region_glows — visually try both, pick the one where the colored outline pops over the screen-blend tint)
   - Replace `lobe_arcs` generation with the random arc network
   - Replace `micro_cells` generation to use the new random cells
4. Add the `lstroke` keyframes to the existing `<style>` block.
5. Move `electricGlow` filter from `.lobe-cell` (per-element) to `.lobe-stroke-layer` (per-group); keep on cells too if visually needed.
6. Render the `extreme` example, eyeball, tune knobs (arc count, stroke width, gradient opacity).
7. Update `CONTEXT.md` "Recent changes" auto-block via push (no manual edit).

## Self-review checklist (done)

- [x] Placeholder scan: no TBD/TODO left in this doc
- [x] Internal consistency: arc count (20) and cell count (6/lobe) align with the architecture section
- [x] Scope check: single implementation plan, no decomposition needed
- [x] Ambiguity check:
  - "card color" = the existing `lobe_color_tokens` mapping (frontal=primary, parietal=accent_d, occipital=secondary, temporal=accent_c, cerebellum=accent_a, brainstem=accent_b)
  - "draw in/out" = `stroke-dashoffset` 100 → 0 → −100, not opacity-only fade
  - "random" = seeded `random.Random` (deterministic per user), not non-deterministic
  - "across the brain" = arcs draw from the union of all lobes' cell pools, not constrained to one lobe
