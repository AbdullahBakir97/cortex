# Brain — True Waves (Round 5)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Builds on:** Rounds 1–4 (all on `feature/brain-professional-visuals`).

## Why round 5 exists

User feedback after Round 4:
- **"Remove the colored spinners from brain parts and make colored waves instead"** — even with thin (10% wide) bands at low opacity (0.40), the rotating-gradient pattern still reads as a *spinner* (band tracing a circular path around the lobe center) rather than a *wave* (band traveling in one direction across the lobe).

## The core fix

Replace `<animateTransform type="rotate">` on each per-lobe gradient with `<animateTransform type="translate">`. A rotating band traces a circle (spinner); a translating band traces a line (wave). Add `spreadMethod="repeat"` to the gradient so the colored band tiles seamlessly — when the translation reaches 100%, the next tile slides in from 0% with no visible loop seam.

This is a one-knob change per gradient with no other architectural impact:

```xml
<!-- BEFORE (rotation = spinner): -->
<linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
  <animateTransform attributeName="gradientTransform" type="rotate"
                    from="0 0.5 0.5" to="360 0.5 0.5" dur="20s" repeatCount="indefinite"/>
  ...

<!-- AFTER (translate + repeat = wave): -->
<linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox"
                spreadMethod="repeat">
  <animateTransform attributeName="gradientTransform" type="translate"
                    from="0 0" to="1 0" dur="10s" repeatCount="indefinite"/>
  ...
```

Three changes per gradient:
1. `<animateTransform type="rotate" from="0 0.5 0.5" to="360 0.5 0.5">` → `type="translate" from="0 0" to="1 0"` (or other direction vector).
2. Add `spreadMethod="repeat"` to the gradient open tag (so the loop is seamless).
3. Adjust `x1/y1/x2/y2` to set the gradient direction (LTR / TTB / diagonal / etc).

## Per-lobe wave directions

Different direction per lobe so the brain doesn't read as 6 synchronized waves marching in one direction. Each lobe has a wave traveling at its own angle and speed:

| Lobe | Direction | Gradient `(x1,y1)→(x2,y2)` | Translate `from→to` | Duration |
|---|---|---|---|---|
| frontal | horizontal LTR | (0,0)→(1,0) | (0,0)→(1,0) | 10s |
| parietal | vertical TTB | (0,0)→(0,1) | (0,0)→(0,1) | 12s |
| occipital | horizontal RTL | (1,0)→(0,0) | (0,0)→(1,0)* | 9s |
| temporal | diagonal ↗ | (0,1)→(1,0) | (0,0)→(1,-1) | 14s |
| cerebellum | diagonal ↘ | (0,0)→(1,1) | (0,0)→(1,1) | 11s |
| brainstem | vertical BTT | (0,1)→(0,0) | (0,0)→(0,1)* | 13s |

*RTL/BTT directions: with the gradient direction reversed in `x1/y1/x2/y2`, translating positively still moves the wave in the natural direction (the gradient's "0%" stop is now on the right or bottom, so translating right-shifts the wave appearance leftward).

The 6 durations (10, 12, 9, 14, 11, 13) are coprime-ish — no two lobes ever sync up visually.

## Why each gradient still uses 5 stops with the same band shape

The stop pattern stays unchanged: rose at 0/45/55/100, lobe color at 50% with `stop-opacity="0.40"`. What changes is HOW the gradient animates — translate instead of rotate. The colored band is the same; only its motion path is different.

Combined with `spreadMethod="repeat"`, each path receives a continuous stream of waves: at any moment, the band is somewhere on its journey across the path bbox. When it exits one side, the next "tile" of the gradient brings a new band in from the other side. The eye sees a continuous flow of colored waves — like ripples in water, not LEDs blinking on a fixed circular track.

## Keep `brainGrad_unified` rotating (it doesn't read as a spinner)

The unified gradient is 4 rose-family stops at full opacity rotating over 40s. Because all the stops are similar colors (varying only in lightness within the rose family), there's no high-contrast band to "rotate." The rotation just produces a slow ambient hue shift. This stays as-is — it's the "slowly changing colors in close color grades" the user requested earlier.

## Out of scope

- Changing brain anatomy or the stroke overlay (still working).
- Changing the random arc network (still working).
- Changing background atmospheric layers (DNA helixes, aurora, nebulae, stars all stay).
- Adjusting wave opacity from 0.40 (might tune later if waves are too subtle, but start at the same value to isolate the rotation→translation change).

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Translate animation with `spreadMethod="repeat"` produces a visible "snap" when the loop restarts | Translating by exactly `(1, 0)` (or equivalent in the wave's direction) makes the loop point coincide with a tile boundary — the snap is invisible because the gradient pattern is identical at that boundary |
| 6 different wave directions look chaotic / disordered | Each lobe's wave is contained within that lobe's paths (per-path objectBoundingBox gradients). Visually you see "wave through frontal" + "wave through parietal" etc., not "6 overlapping global waves" |
| `spreadMethod` not supported in some renderers | Native SVG 1.1 attribute, supported by all browsers + GitHub's SVG sanitizer. Safe |
| Different durations make it feel out of sync | That's intentional — synchronization would feel artificial / choreographed. Asynchrony reads as organic |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>` left.
- [x] Internal consistency: 6 unique durations (10, 12, 9, 14, 11, 13), 6 unique direction vectors. No two lobes share both attributes.
- [x] Scope: focused on user feedback; only per-lobe gradient animations change. Stop colors, opacity, and offsets all unchanged from R4.
- [x] Ambiguity check:
  - "Wave" = translation animation with `spreadMethod="repeat"`, not a sine-wave path
  - "Spinners removed" = no more `type="rotate"` on per-lobe gradients (`brainGrad_unified` rotation stays since it's color-cycling, not a visible band rotating)
