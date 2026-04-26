# Brain — Aurora Flow Through Anatomy (Round 7)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Builds on:** Rounds 1–6.

## Why round 7 exists

User feedback after R6: *"i dont like the dots glowing the brain parts itself should have waved colored animation in professional shapes and animations, and push the brain down a bit to not be behind card its should be under it."*

Two issues:
1. The R6 region_glow circles (r=260, pulsing opacity 0.55↔1.0 + scale 0.92↔1.18 over 8s) read as "dots glowing" rather than as activation pulses. The disk shape is too visible.
2. The brain anatomy at `translate(332, 152)` overlaps with the parietal card (y=130) and slightly with the right-side cards (y=200). User wants it pushed down.

## The breakthrough idea: brain-masked aurora flow

Instead of *per-lobe gradient sweeps* (R3-R5) or *per-lobe pulse circles* (R6), use **palette-colored radial gradients drifting freely through the canvas**, masked by the brain anatomy. Each gradient is a "colored cloud" that slowly translates around the canvas; the brain shape acts as a *window* showing only the parts of the cloud that are inside the brain.

As the clouds drift, different colors move into and out of different brain regions over tens of seconds. Frontal might be pink for 8s, then shift toward purple as the pink cloud drifts away and a purple one drifts in. There's no fixed "this lobe is X color" — the colors *visit* each region.

This is **continuous color flow with no discrete shape**. No bands rotating. No bands translating. No pulse-circles fading. Just smooth multi-color drift through the brain anatomy.

## Architecture

### Mask source (Python prep in `_compose_wrapper`)

Build a "white-fill" copy of the brain content for the mask. Each path's `d` attribute is preserved; everything else is stripped:

```python
# All brain paths (union of per-lobe lists), as just <path d="..." fill="white"/>.
# Used as the source for <mask> — wherever brain anatomy exists, mask is opaque.
brain_mask_paths: list[str] = []
for lobe, pairs in paths_by_lobe.items():
    for _pid, d in pairs:
        brain_mask_paths.append(f'<path d="{d}" fill="white"/>')
```

This produces ~200 minimal `<path>` elements. They're embedded in a `<mask>` def with the same brain transform as the rendered brain group.

### Mask def

Add to `<defs>`:

```xml
<mask id="brainMask">
  <g transform="translate(332, 210) scale(0.7)">
    {brain_mask_paths joined by newline}
  </g>
</mask>
```

### Aurora flow layer

New `<g mask="url(#brainMask)" class="brain-aurora">` containing 4 large soft radial gradient rects, each in a palette accent color, each translating on its own slow trajectory. Placed inside the brain wobble group so the aurora flow respects the wobble + ripple animations.

```xml
<g mask="url(#brainMask)" class="brain-aurora">
  <rect x="-100" y="0" width="900" height="900" fill="url(#brainAurora_a)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; 600,200; 0,0" dur="32s" repeatCount="indefinite"/>
  </rect>
  <rect x="600" y="0" width="900" height="900" fill="url(#brainAurora_b)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; -500,250; 0,0" dur="38s" repeatCount="indefinite"/>
  </rect>
  <rect x="200" y="-100" width="900" height="900" fill="url(#brainAurora_c)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; 200,400; 0,0" dur="41s" repeatCount="indefinite"/>
  </rect>
  <rect x="-100" y="500" width="900" height="900" fill="url(#brainAurora_d)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; 700,-300; 0,0" dur="45s" repeatCount="indefinite"/>
  </rect>
</g>
```

The 4 rects start at different positions (top-left, top-right, top-center, bottom-left) and drift along different vectors over 32-45s on a return-to-origin loop. The trajectories are designed so:
- At any moment, all 4 rects' centers are at different points on the canvas
- Over 45s, each rect visits multiple parts of the brain
- The combined effect is continuous multi-color drift through the brain shape

### Aurora gradient defs

4 large radial gradients in palette accents, with the same opacity profile (0.45 peak fading to 0):

```xml
<radialGradient id="brainAurora_a" cx="50%" cy="50%" r="50%">
  <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.45"/>
  <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.18"/>
  <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
</radialGradient>
<radialGradient id="brainAurora_b" cx="50%" cy="50%" r="50%">
  <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.45"/>
  ...
</radialGradient>
<radialGradient id="brainAurora_c" cx="50%" cy="50%" r="50%">
  <stop offset="0%"   stop-color="#A78BFA" stop-opacity="0.45"/>
  ...
</radialGradient>
<radialGradient id="brainAurora_d" cx="50%" cy="50%" r="50%">
  <stop offset="0%"   stop-color="#34D399" stop-opacity="0.45"/>
  ...
</radialGradient>
```

Hardcoded palette colors (pink, cyan, purple, green) for visual variety. Could palette-drive these later, but starting hardcoded keeps R7 focused.

### Composition placement (inside brain wobble group)

The aurora flow goes ABOVE the body fill (`brain_content`) and BELOW the lobe stroke overlay. Inside the `<g class="brain-3d">` wobble group:

```
{brain_content}                                <!-- body fill (rose) -->
<g mask="url(#brainMask)" class="brain-aurora">  <!-- NEW: color flow -->
  ...4 aurora rects...
</g>
<g class="lobe-stroke-layer" filter="url(#electricGlow)">  <!-- existing -->
  ...stroke overlay...
</g>
<g class="arc-network" filter="url(#electricGlow)">        <!-- existing -->
  ...arcs + cells...
</g>
```

## Brain position update

Three coordinated changes for the y-shift:

1. **Brain wobble group transform:** `translate(332, 152)` → `translate(332, 210)` (+58px down)
2. **Mask def transform:** must match — `translate(332, 210) scale(0.7)`
3. **Centroid formula in `_classify_brain_paths`:**
   ```python
   canvas_centroids[lobe] = (round(ax * 0.7 + 332), round(ay * 0.7 + 152))
   #                                                              ^^^
   # change to:
   canvas_centroids[lobe] = (round(ax * 0.7 + 332), round(ay * 0.7 + 210))
   ```

Card positions stay unchanged — leader lines automatically follow the new centroids since they're computed from the lobe_centroids dict.

The brain extent shifts from y=152-664 to y=210-722. Canvas is 900 tall, so the brain still has 178px margin below.

## Removal of region_glow

Three things to delete:

1. **Python prep:** Delete the `region_grads.append(...)` block and the `region_glows.append(...)` block in `_compose_wrapper`. Remove `region_grads` and `region_glows` from the variable list.

2. **Defs injection:** Remove the line `{chr(10).join("    " + g for g in region_grads)}` from the f-string (it joined region_grads into the `<defs>` block).

3. **Body composition:** Remove the line `{chr(10).join("        " + rg for rg in region_glows)}` from the wobble group composition.

4. **CSS:** Delete the `.region-glow`, `.region-pulse`, `@keyframes rpulse`, and `.rg1`–`.rg6` rules from the `<style>` block.

After this, the rgrad/region_glow system is fully removed.

## Out of scope

- Palette-driving the aurora colors (hardcoded pink/cyan/purple/green for now; can palette-drive in a future round)
- Adjusting card positions (cards stay where they are; brain shifts down to not overlap)
- Tuning aurora opacity beyond 0.45 (start there; if too subtle, simple opacity tweak follow-up)

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Mask with 200 path geometries bloats SVG file size | Each mask path is just `<path d="..." fill="white"/>` (~30 bytes overhead per path beyond the d attribute). Net add ~6 KB on top of the existing brain content's d attributes (which are reused). Acceptable |
| `<mask>` not handled by GitHub's SVG sanitizer | SVG 1.1 standard primitive, sanitizer-safe |
| Aurora rects clip incorrectly because rect transforms don't compose with mask | The mask is in canvas coords (via the brain group transform). The rects are inside the same `<g mask="url(#brainMask)">` group, so the mask applies to them post-render. The rects' own `<animateTransform translate>` moves them in their parent's local coords, but the mask is applied to the final pixel output. Should work — verify in smoke build |
| Brain position shift breaks card-leader-line connections | Leader lines compute their endpoint from `lobe_centroids[key]`, which is recomputed by the classifier with the new offset. Lines auto-update |
| Aurora flow looks too uniform / "milky" | The 4 colors at low opacity will mix into a colored haze. Different starting positions + different durations + different translate vectors should keep the colors distinguishable |
| Aurora flow conflicts with existing `feDisplacementMap` ripple | Both apply to the same brain group. The displacement filter applies to all rendered children including the masked aurora — so the aurora pixels also ripple, which actually reinforces the "alive tissue" effect. No conflict |
| Determinism breaks because mask uses `paths_by_lobe` order | `paths_by_lobe` is a dict; iteration order is insertion order (Python 3.7+). Insertion order is deterministic in `_classify_brain_paths`. Determinism preserved |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>`.
- [x] Internal consistency: 4 unique aurora durations (32, 38, 41, 45s), 4 unique colors, 4 unique starting positions and translate trajectories. The brain transform offset (210) matches in all three places that reference it.
- [x] Scope: focused — adds aurora flow, removes region_glow, shifts brain. No other architectural changes.
- [x] Ambiguity check:
  - "Aurora flow" = drifting radial gradients clipped by brain mask, NOT per-path gradient fills
  - "No dots" = region_glow circles are completely removed
  - "Push brain down" = +58px on y axis (translate y 152→210)
  - Body color (rose) and ripple filter and stroke overlay are all KEPT
