# Brain — Activation Pulse + Organic Ripple (Round 6)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Builds on:** Rounds 1–5.

## Why round 6 exists

User feedback after 5 rounds of gradient-sweep iterations: *"this not what i exactly want, search to learn how you could similar animation and learn new ideas."*

Cause: every round R1–R5 used gradient sweeps (rotated, then translated) on per-lobe `<linearGradient>` defs. Gradient sweeps = continuous graphic motion. Real brain visualizations (fMRI, OpenAI sphere, Anthropic brand, Apple Neural Engine) use **discrete activation events** — zones light up, hold, fade — and **organic tissue distortion** — the anatomy ripples like real living matter. Both are missing in R5.

## Three coordinated changes

### 1. Delete per-lobe wave gradients entirely

Remove all 6 `<linearGradient id="brainGrad_<lobe>">` defs. Remove the `brain_content_lobed` regex substitution loop. Replace `{brain_content_lobed}` with `{brain_content}` in the SVG composition (so all paths use just `brainGrad_unified` — the rose body cycling slowly through close hues).

After this change, the brain has NO per-lobe gradient sweep. The body is uniformly rose. Lobe identity is carried entirely by:
- The animated stroke overlay (R1 — draws each lobe's outline in card color, 6s cycle, staggered)
- The region_glow circles (atmosphere — radial gradients at lobe centroids, pulsing) — promoted in change #2

### 2. Promote region_glow as the primary per-lobe color carrier

Existing region_glow (R1 brain.py:425-428):
```xml
<circle cx="bx" cy="by" r="200" fill="url(#rgrad_<key>)"
        class="region-glow region-pulse rg{i+1}"/>
```

Existing CSS (R1):
```css
.region-pulse { animation: rpulse 5s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }
@keyframes rpulse {
  0%, 100% { opacity: 0.65; transform: scale(1); }
  50%      { opacity: 1.0;  transform: scale(1.10); }
}
.rg1{animation-delay:0s}    .rg2{animation-delay:0.6s}
.rg3{animation-delay:1.2s}  .rg4{animation-delay:1.8s}
.rg5{animation-delay:2.4s}  .rg6{animation-delay:3.0s}
```

**Promotion changes:**

- Render: bump radius `r=200` → `r=260` (more presence; lobes glow visibly out to where the lobe-stroke overlay draws)
- CSS: stretch cycle `5s` → `8s` (slower, more cinematic; lobes "breathe" rather than "blink")
- CSS: increase peak opacity `1.0` → `1.0` (already maxed at 1.0 in keyframes; bump scale `1.10` → `1.18` for more dramatic pulse instead)
- CSS: re-stagger delays `0s/0.6s/1.2s/1.8s/2.4s/3.0s` → `0s/1.3s/2.6s/3.9s/5.2s/6.5s` so the 6 lobes spread across the full 8s cycle (each at a unique phase) — combined with the stroke overlay's existing 6s cycle, the brain runs two rhythmic systems in counterpoint, never syncing
- Boost the per-lobe radial gradient (`rgrad_<key>`) saturation: stops `0.55 / 0.18 / 0` → `0.85 / 0.30 / 0` (was tuned for "subtle tint when there's also a per-lobe gradient sweep underneath"; now that the gradient sweep is gone, the glow needs to do all the per-lobe color work)

### 3. Add `feDisplacementMap` organic ripple to the brain group

Define a new filter and apply it to the brain wobble group, so the brain anatomy itself ripples by ~2-3 px. Combined with the existing CSS scale-pulse and 3D-wobble, the brain has three layered organic motions.

```xml
<filter id="brainRipple" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="2" result="noise">
    <animate attributeName="baseFrequency" values="0.018;0.024;0.018"
             dur="11s" repeatCount="indefinite"/>
  </feTurbulence>
  <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.5"/>
</filter>
```

Application: add `filter="url(#brainRipple)"` to the existing `<g class="brain-pulse" filter="url(#brainGlow)">`. The two filters chain — the existing brainGlow softens the brain's edges, and brainRipple displaces them organically.

Wait — SVG filter chaining requires nesting. Better: chain inside one filter via `result` references. But `brainGlow` is a separate filter. Simplest: replace the existing `filter="url(#brainGlow)"` with `filter="url(#brainComposite)"` where `brainComposite` chains both effects. Implementation in the plan.

**Why `feTurbulence` is OK now (was rejected in R4):** in R4, turbulence was a *visible* render output (alpha-tinted noise rect). Visible noise = grain = amateur. Here it's an *invisible displacement source* — the noise itself isn't rendered; it only controls how the brain pixels are pushed around. The brain rippling organically is a million miles from grain.

## Out of scope

- Sequencing the lobe activations to flow in a specific anatomical order (occipital→parietal→frontal). Could add later. For now: the 8s cycle with 6 phases distributes activation reasonably across time.
- Adding new visual elements (more particles, more arcs, etc.). The atmosphere is rich enough.
- Schema changes — `atm.show_aura`/`atm.show_particles` still gate the right things.
- Removing R5's translate-based code structure entirely — we just delete the per-lobe gradient defs and the substitution loop. The change is subtractive, not architectural.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Without per-lobe gradient sweeps, the brain looks too uniform/rose | Region glow at higher saturation (0.85 vs. 0.55) carries the per-lobe color identity. Stroke overlay (R1) still draws lobe outlines. Visual identity is preserved — moved to a different channel |
| `feDisplacementMap scale="2.5"` distorts text/lobe-cell positions | The filter is on the brain group only (`<g class="brain-pulse">`). Cards and arcs and labels are outside that group, unaffected. Lobe-cells and stroke-overlay are inside but they're small/thin so 2-3px distortion just makes them look organic, not broken |
| `feTurbulence` re-introduction triggers user's "noise" memory from R4 | Visually completely different — no rendered noise output. Only the displacement effect is visible (rippling brain anatomy). User's earlier complaint was about visible grain, which this isn't |
| Filter chaining breaks GitHub SVG sanitizer | Both `feGaussianBlur` (used by brainGlow) and `feTurbulence + feDisplacementMap` are standard SVG 1.1, supported by sanitizer. Combining them via a single composite filter or via separate filters on nested groups both work |
| Determinism breaks because of `<animate>` on baseFrequency | SMIL `<animate>` is deterministic (no random state). Filter `seed="2"` gives the same noise pattern every render. Two builds → identical output |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>`.
- [x] Internal consistency: 8s cycle / 6 stagger phases / 1.18 scale / 0.85 peak opacity all coherent. Filter scale 2.5 is subtle.
- [x] Scope: focused (single-task plan). Subtractive in two places (gradient defs, substitution loop), additive in two places (filter def, new CSS values).
- [x] Ambiguity check:
  - "Activation pulse" = the existing region_glow opacity+scale animation, with bigger radius and longer cycle
  - "Organic ripple" = `feDisplacementMap` driven by animated `feTurbulence`
  - "Per-lobe color comes from glow not gradient" = explicit removal of `brainGrad_<lobe>` defs, glow saturation boosted
