# Brain — Rose Body, Wave Lobes & DNA Helixes (Round 4)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Builds on:** Round 1 + 2 + 3 (all on `feature/brain-professional-visuals`).

## Why round 4 exists

User feedback after Round 3:
- **"Why do I see full bold colored parts in all brain parts"** — the per-lobe gradient bands at 40-60% offset (20% wide band) read as "whole lobe colored", not as a wave passing through.
- **"The colors should only wave on each brain part professionally with animations"** — wants a thin sweeping band of lobe color, not a filled tint.
- **"Brain main color should be more to rose"** — body should be rose family, not deep navy.
- **"Slowly changing colors in loop in close colors grades"** — body itself should cycle through close hues within the rose family.
- **"Remove this small lines from background that moves from right to left"** — the perspective grid (R3-2) is out of place; remove it.
- **"We could add professional DNA symbols that fades in and out with professional animations and colors and drawing"** — add DNA helix symbols at corners as a new background element.
- **"Everything in background should fit together"** — cohesion concern.

## Four improvements (R4 Tasks 1–4)

### 1. Rose body + thin wave lobe gradients

**1a. Rose-family unified body gradient (slow loop through close hues):**

Replace `brainGrad_unified`'s deep-navy stops with 4 rose-family stops at full opacity, rotating over 40s. As the gradient rotates, the apparent body color shifts smoothly through `#3A1A28` (deep wine rose) → `#4D2438` (mauve) → `#5C2E45` (medium mauve) → `#3A1A28`, all in the same hue family (~330° hue, varying lightness).

```xml
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

This is the body color visible across most of every brain path — warm, deep, slowly cycling through close hues.

**1b. Rewrite the 6 per-lobe gradients as "thin wave" gradients:**

Each per-lobe gradient now has rose-family stops at the edges and a NARROW band of lobe color at the middle (45-55% offset = 10% wide band, vs. R3's 40-60% = 20%) at low opacity (0.40). As the gradient rotates, only a slim wave of the lobe color is visible at any moment — sweeping through the lobe.

```xml
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

Same shape for all 6 lobes; lobe colors and rotation periods unchanged from R3:
- frontal: `{p_primary}` / 20s
- parietal: `{p_accent_d}` / 23s
- occipital: `{p_secondary}` / 17s
- temporal: `{p_accent_c}` / 25s
- cerebellum: `{p_accent_a}` / 19s
- brainstem: `{p_accent_b}` / 27s

The narrow 10% band at low opacity (0.40) over the rose base gives a true "wave passing through" effect — visible only momentarily as the gradient rotates, and even at peak it's just a tint, not a fill.

**1c. Tint the bgRadial to rose:**

Update `bgRadial`'s inner stop to a rose-dark color so the entire background is tied to the rose theme:

```xml
<stop offset="0%"   stop-color="#280816"/>   <!-- was #180826, now rose-dark -->
<stop offset="60%"  stop-color="#100308"/>   <!-- was #080410, now slightly warmer -->
<stop offset="100%" stop-color="{p_background}"/>
```

### 2. Remove the perspective grid

The R3 perspective grid is the geometric/digital outlier. Delete:
- The `<g class="grid">` block from the SVG composition
- The `gridFade` radial gradient + `gridMask` defs
- The `grid_lines` Python prep block

Other R3 atmospheric layers (stars, nebula clouds, aurora) stay — they're all organic/cosmic and fit with rose + DNA.

### 3. Add 4 DNA helix symbols

Add a new background element: 4 DNA double-helix symbols at the canvas corners, each fading in (with a "drawing in" effect via stroke-dashoffset) and out on staggered 16s timers. Reads as a scientific/biological motif that fits the brain theme without competing for attention.

**3a. Helper to generate one helix:**

```python
def _dna_helix_paths(
    cx: int, cy: int,
    width: int = 80, height: int = 170,
    samples: int = 24,
) -> tuple[str, str, list[tuple[tuple[int, int], tuple[int, int]]]]:
    """Generate two intertwining sine paths + base-pair rung connectors.

    Returns (strand_a_path_d, strand_b_path_d, rungs).
    Strand A: cosine wave (one phase).
    Strand B: -cosine wave (anti-phase, mirrored).
    Rungs: horizontal connectors at every 6th sample point.
    """
    import math
    points_a: list[tuple[int, int]] = []
    points_b: list[tuple[int, int]] = []
    rungs: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(samples + 1):
        t = i / samples
        y = round(cy + (t - 0.5) * height)
        offset = round(math.cos(t * 2 * math.pi * 2) * (width / 2))  # 2 full cycles
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

**3b. 4 helixes at canvas corners:**

```python
dna_specs = [
    (120, 120,  "#22D3EE", 0),    # top-left,    cyan,   delay 0s
    (1280, 120, "#EC4899", 4),    # top-right,   pink,   delay 4s
    (120, 780,  "#7C3AED", 8),    # bottom-left, purple, delay 8s
    (1280, 780, "#22D3EE", 12),   # bottom-right, cyan,  delay 12s
]

dna_blocks: list[str] = []
for cx, cy, color, delay in dna_specs:
    strand_a, strand_b, rungs = _dna_helix_paths(cx, cy)
    rung_lines = "\n".join(
        f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
        f'stroke="{color}" stroke-width="0.8" stroke-opacity="0.5"/>'
        for a, b in rungs
    )
    dna_blocks.append(
        f'<g class="dna" style="animation-delay:{delay}s">\n'
        f'    <path d="{strand_a}" stroke="{color}" stroke-width="1.5" '
        f'fill="none" stroke-opacity="0.7" pathLength="100" '
        f'stroke-dasharray="100 100" class="dna-strand"/>\n'
        f'    <path d="{strand_b}" stroke="{color}" stroke-width="1.5" '
        f'fill="none" stroke-opacity="0.7" pathLength="100" '
        f'stroke-dasharray="100 100" class="dna-strand"/>\n'
        f'{rung_lines}\n'
        f'  </g>'
    )
```

Each helix is positioned ~120px from the canvas edge so it doesn't crowd the brain. Different colors at each corner give visual variety.

**3c. CSS animations:**

```css
.dna {
  opacity: 0;
  animation: dnaFade 16s ease-in-out infinite;
}
@keyframes dnaFade {
  0%, 100% { opacity: 0; }
  10%      { opacity: 0; }
  25%      { opacity: 0.85; }
  50%      { opacity: 0.85; }
  65%      { opacity: 0; }
}
.dna-strand {
  animation: dnaDraw 16s ease-in-out infinite;
}
@keyframes dnaDraw {
  0%   { stroke-dashoffset: 100; }
  25%  { stroke-dashoffset: 0; }
  50%  { stroke-dashoffset: 0; }
  65%  { stroke-dashoffset: -100; }
  100% { stroke-dashoffset: -100; }
}
```

The `.dna-strand` rule animates `stroke-dashoffset` so the strand visibly "draws in" during the fade-in phase, then "draws out" during the fade-out phase. Synchronized with the parent's `.dna` opacity fade so the visual is "DNA appears, draws itself, holds, draws away."

The 4 helixes use `animation-delay: 0s/4s/8s/12s` so at any given moment, 1-2 are visible and the others are hidden — sparse, not crowded.

**3d. Composition placement:**

DNA layer goes BEFORE aurora bands in source order (so it's at the same z-depth as nebula clouds — atmospheric background, not foreground decoration). Gated by `atm.show_aura` (matches other atmospheric layers).

### 4. Final regen + visual verification

Final task: regenerate showcase, ruff lint, pytest, determinism check, structural grep.

## Out of scope

- Moving DNA closer to the brain (corners are intentional — keeps brain breathing room)
- Animating the helix to rotate (just fade + draw is the spec; rotation would be too much motion competing with the brain's animations)
- Changing the lobe rotation periods (kept identical to R3 — they work)
- Tweaking aurora/nebula colors (the rose body unifies everything; existing layers' colors still fit)

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Rose body looks too "warm" / unbalanced | Cool-tone elements (cyan stars, cyan/purple aurora, cyan/purple nebula) provide cool counterweight to the warm rose |
| Lobe wave too subtle / invisible | The thin band (10% wide) at 0.40 opacity is calibrated against the dark rose base — visible at the peak of rotation. If still too subtle after eyeballing, easy single-line opacity tweak follow-up |
| DNA helix paths jagged (low samples, polyline) | 24 samples per 2-cycle helix = ~12 segments per cycle; visually smooth at the small canvas size |
| 4 simultaneous DNA elements + 30 stars + nebulae overload renderer | All animations are CSS keyframes (single rule each) + a few SMIL on gradients; same complexity class as before — no perf concern |
| Determinism breaks if `_dna_helix_paths` uses unseeded randomness | Helper is purely deterministic (math-based, no rng). DNA positions/colors are hardcoded |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>` left
- [x] Internal consistency: rose hex codes form a true hue family (`#3A1A28`, `#4D2438`, `#5C2E45` are all ~330° hue at varying lightness 8-13%)
- [x] Scope: focused on R3 feedback; no scope creep
- [x] Ambiguity check:
  - "Wave" = thin (10%) opacity-blended band, not a fill
  - "Close color grades" = same hue family, varying lightness only
  - "Rose" = `#3A1A28` to `#5C2E45` family, not bright pink
  - "DNA symbols" = double-helix line drawings, not 3D models or characters
  - "Background fits together" = removing the digital grid, adding organic DNA, tinting bgRadial to rose
