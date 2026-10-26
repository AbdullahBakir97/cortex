# Brain — Vibrant Lobes & Atmospheric Depth (Round 3)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Builds on:** Round 1 (`469e565..909a6f5`) + Round 2 (`206dfa7..a7f7a2b`).

## Why round 3 exists

User feedback after Round 2:
- **"Brain looks like silver"** — the Round 2 specular pass over the muted unified body produces a chrome/metallic illusion (dark base + bright white sweep = the textbook recipe for silver in 3D rendering). User wants colorful, not metallic.
- **"Don't like the spinners"** — the specular gradient's rotating bright band reads as a *spinning object* rather than a *moving light source*.
- **"Background needs more details / mindblowing"** — aurora bands alone don't carry enough atmospheric depth. Wants more layers, more motion variation.
- **"Text is coming out of card"** — Round 2's tightened typography (letter-spacing 0.30em on the cap label) overflows long captions or domain text on some cards.
- **Wants per-lobe color identity** — but professionally executed (not the saturated paint-by-numbers of pre-Round-1).

## Four improvements (R3 Tasks 1–4)

### 1. Vibrant lobes — kill specular, revive per-lobe tinted gradients

Two coordinated changes:

**1a. Remove the specular pass entirely:**
- Delete `<linearGradient id="brainGrad_specular">` def from `<defs>`.
- Delete the `brain_content_specular = brain_content.replace(...)` line in `_compose_wrapper`.
- Delete the `<g class="brain-specular" style="mix-blend-mode: screen">{brain_content_specular}</g>` block from the SVG composition.

**1b. Add 6 per-lobe gradients with desaturated stops:**

Each lobe gets its own `linearGradient` with stops `dark → lobe_color@0.45 → lobe_color@0.45 → dark`, rotating on independent periods (so the 6 lobes are never visually synced):

```xml
<linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="1"
                gradientUnits="objectBoundingBox">
  <animateTransform attributeName="gradientTransform" type="rotate"
                    from="0 0.5 0.5" to="360 0.5 0.5" dur="20s" repeatCount="indefinite"/>
  <stop offset="0%"   stop-color="#0E0820"/>
  <stop offset="40%"  stop-color="{p_primary}"   stop-opacity="0.45"/>
  <stop offset="60%"  stop-color="{p_primary}"   stop-opacity="0.45"/>
  <stop offset="100%" stop-color="#0E0820"/>
</linearGradient>
```

Same shape for all 6 lobes with different colors and durations:

| Lobe | Color | Duration |
|---|---|---|
| frontal | `{p_primary}` | 20s |
| parietal | `{p_accent_d}` | 23s |
| occipital | `{p_secondary}` | 17s |
| temporal | `{p_accent_c}` | 25s |
| cerebellum | `{p_accent_a}` | 19s |
| brainstem | `{p_accent_b}` | 27s |

The stops use the `lobe_color@0.45` pattern (transparent at 45%) over a dark navy base — the path's underlying color (`#0E0820` from `brainGrad_unified` showing through where the specular layer used to add white) reads as deep purple-black, with the lobe color tinting through where the gradient sweeps. Each lobe is unmistakably its own color, but at low saturation so it reads as professional, not paint-by-numbers.

**1c. Wire per-lobe gradients into `brain_content` via regex substitution in `_compose_wrapper`:**

`brain_content` arrives with all paths pointing at `url(#brainGrad_unified)` (set in Round 1's `_recolor`). For each lobe, iterate the paths in `paths_by_lobe[lobe]` and regex-substitute the unified URL with the lobe URL:

```python
brain_content_lobed = brain_content
for lobe, pairs in paths_by_lobe.items():
    grad_url = f"url(#brainGrad_{lobe})"
    for pid, _d in pairs:
        pattern = (
            rf'(<path\b[^>]*?\sid="{re.escape(pid)}"[^>]*?\sstyle="[^"]*?fill:)'
            rf'url\(#brainGrad_unified\)'
        )
        brain_content_lobed = re.sub(pattern, rf"\1{grad_url}", brain_content_lobed)
```

Use `brain_content_lobed` in the SVG composition where `brain_content` was used. Any unclassified paths (rare; should be 0 in practice) keep `url(#brainGrad_unified)` — the unified gradient stays as the fallback.

**1d. Simplify `brainGrad_unified` (now used as fallback only):**

Since per-lobe gradients carry the color, the unified gradient just needs a calm dark base. Keep the 5 stops but bump `accent_b` opacity back down from 0.55 → 0.30 (the higher value was meaningful when unified was the *primary* fill; now it's just a fallback):

```xml
<stop offset="50%"  stop-color="{p_accent_b}" stop-opacity="0.30"/>
```

This task gives back the per-lobe color identity the user wanted in their second proposal, but at the right level of polish — soft tints over a dark base, animated independently, no saturated blocks.

### 2. Background depth layers — star field + perspective grid + nebula clouds

Three new background layers, each on a different motion timescale, gated by `atm.show_aura` (matches existing pattern):

**2a. Far star field (30 dim points):**
- 30 small `<circle>` elements at deterministic positions (seeded RNG using `_seed_from_name` so reproducible per user)
- Smaller (r=0.6–1.2) and dimmer (opacity 0.2–0.5) than the existing ambient particles (which are r=1.2–2.2, opacity 0.2–0.6)
- Animated via CSS: very slow opacity twinkle (8–14s) + slow translate drift (40–70s)
- Renders BEHIND aurora bands → reads as deep space

**2b. Perspective grid:**
- ~12 horizontal + ~16 vertical thin `<line>` elements across the canvas, spaced 80px apart
- `stroke="{p_accent_b}"` at very low opacity (0.04)
- Edges fade via a radial mask centered on canvas (so grid is visible only in the central area, fades at corners)
- Animated via slow `<animateTransform translate>` over 50s — grid drifts diagonally, evoking digital data space
- Renders BEHIND nebula clouds, ABOVE the bgRadial fill

**2c. Nebula clouds (4 large soft blobs):**
- 4 `<rect>` elements filled with large radial gradients in palette colors (pink, purple, cyan, accent_d=green by default)
- Apply `feGaussianBlur stdDeviation="40"` filter for soft amorphous edges
- Sizes 1100×1100, positioned around the canvas (top-left, top-right, bottom-left, bottom-right)
- Drifting via `<animateTransform translate>` on staggered phases (38s, 44s, 41s, 47s)
- Different from aurora: aurora is *flat radial circles drifting*, nebula is *blurred amorphous clouds drifting* — different visual character, more organic

Combined with the existing aurora bands (R2-1) + constellation lines (R2-5) + light streaks (R2-6) + ambient particles (R1) + bgAura drift (R2-7) + bgRadial pulse, that's **9 distinct background layers** at different motion timescales. Genuine cinematic depth.

### 3. Fix text overflow on cards

Three coordinated CSS changes:

- `.t-cat-cap`: revert `letter-spacing` from 0.30em → **0.25em** (compromise between the original 0.20em and the too-tight 0.30em). Keep `font-weight: 800` from R2-4.
- `.t-region`: drop `font-size` from 24px → **22px**
- `.t-skill`: drop `font-size` from 18px → **16px**

These three changes together give breathing room for long captions ("OCCIPITAL · LOBE"), long domain text, and long tool lists — without a clip path (which would risk hiding important content).

If users still see overflow on extreme content (e.g., 6+ very long tool names), they need to keep their `cortex.yml` configs reasonable. The existing tool list is already truncated to 4 tools in Python (`region_obj.tools[:4]`).

### 4. Regenerate showcase + visual verification

Final task: run `cortex build` to regenerate `examples/rendered/extreme/brain-anatomical.svg`, eyeball in browser, commit.

## Out of scope

- Multiple SVG style variants (deferred — a `brain.style` schema field is a separate ticket once one strong style is locked in)
- Removing the round-2 R1-R2 work that the user liked (stroke overlay, random arc network, aurora bands, card edge glow, card inner pulse, stacked shadow, constellation lines, light streaks, bgAura drift — all stay)
- Any cortex.yml schema changes — all changes are template-level
- Mid-task tuning of the lobe gradient opacities (start at 0.45; user can request a tweak after seeing the result)

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Per-lobe regex substitution breaks if a path has no `style="fill:..."` attribute | Source SVG paths reliably have `style="fill:..."` (verified in Round 1). Substitution is a no-op for any path without the pattern — safe. |
| Removing specular + adding per-lobe gradients regresses determinism | Per-lobe stops are static; rotation animations are SMIL with no random state. Deterministic by definition. The integration test (`test_build_is_deterministic`) catches any drift. |
| Background grid + 30 stars + 4 nebula clouds bloat the SVG | Each layer is bounded: grid is ~28 `<line>` elements, stars are 30 `<circle>` elements, nebula is 4 `<rect>` + 4 gradients. Net add ~4 KB. |
| Nebula `feGaussianBlur` with stdDeviation=40 is expensive | Filter applies to a small fixed shape (rect) once per nebula, not per-frame. Modern browsers handle this without issue. |
| Lobe gradient colors clash with aurora colors | Aurora is at low opacity (0.04–0.10) and behind everything. Lobe gradients are at 0.45 in the brain area. Different opacity ranges + different layers → no clash. |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>` left.
- [x] Internal consistency: per-lobe gradient durations all unique, all in 17–27s range. Lobe colors map to existing `lobe_color_tokens` keys (frontal=primary, parietal=accent_d, etc.) — same mapping as R1's stroke overlay.
- [x] Scope check: focused on user feedback; no scope creep.
- [x] Ambiguity check:
  - "Vibrant" = lobe-color-at-0.45-opacity, not saturated solid.
  - "Mindblowing" = layered depth (9 distinct background layers), not noise.
  - "Per-lobe colored as classified" = per-lobe gradients filling the paths in each lobe, not just the stroke overlay.
