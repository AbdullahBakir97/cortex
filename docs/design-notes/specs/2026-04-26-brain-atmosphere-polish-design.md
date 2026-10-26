# Brain — Atmosphere & Polish (Round 2)

**Status:** approved (design)
**Date:** 2026-04-26
**Owner:** Abdullah Bakir
**Touches:** `packages/cortex-core/cortex/builders/brain.py` only
**Touches (rendered):** `examples/rendered/extreme/brain-anatomical.svg` (auto-regenerated)
**Builds on:** [`2026-04-26-brain-professional-visuals-design.md`](./2026-04-26-brain-professional-visuals-design.md) — Round 1 already shipped (commits `469e565..909a6f5`)

## Why round 2 exists

User feedback after Round 1:
- **Liked:** stroke-overlay draws (lobes glow in card colors), random Bezier arc network.
- **Disliked:** `feTurbulence` plasma fog reads as digital grain; cards look like rectangles, not premium UI; atmosphere feels mostly static; brain body color reads as flat / "drained."

Round 2 is a polish pass with four targeted improvements (A → D → B → C in implementation order):

## Four improvements

### A. Aurora bands — replaces `feTurbulence` plasma fog

**Today:** `<filter id="plasmaFog"><feTurbulence baseFrequency="0.012" numOctaves="2"/></filter>` applied to a covering `<rect>` at 0.55 opacity. `feColorMatrix` tints it pink/purple. Reads as TV noise.

**New:** Delete the `plasmaFog` filter and its `<rect>`. Add **3 large soft radial gradients** drifting across the canvas via `<animateTransform translate>` over 25–40s on staggered phases:

| Gradient | Color | Position | Drift period |
|---|---|---|---|
| `aurora_a` | `#EC4899` (pink) @ 0.10 | top-left | 28s |
| `aurora_b` | `#7C3AED` (purple) @ 0.10 | center-bottom | 35s |
| `aurora_c` | `#22D3EE` (cyan) @ 0.08 | top-right | 31s |

Each rendered as a `<rect width="900" height="900">` filled with the radial gradient, animated with `translate` of ±200px diagonal motion. The three overlap and shift, producing aurora-style color flow that reads as *atmospheric light*, not grain.

Gated by `atm.show_aura` (existing flag). When off, no aurora rendered.

### D. Brain specular highlight — depth pass on the body

**Today:** body has one `brainGrad_unified` (the "diffuse" layer). Reads as flat because it's a single uniform sweep.

**New:** add a **second pass** that renders the same brain content again, with fill replaced by a thin specular gradient, blended via `mix-blend-mode: screen`. Implementation is a single regex substitution on the recolored brain content:

```python
specular_content = brain_content.replace(
    "url(#brainGrad_unified)", "url(#brainGrad_specular)"
)
```

Then render this as a sibling `<g class="brain-specular">` group above the diffuse body in the wobble group. The 'screen' blend mode adds light without recoloring the underlying paths.

The specular gradient is a thin bright band that rotates at a *different* speed and angle from the diffuse:

```xml
<linearGradient id="brainGrad_specular" x1="0" y1="0" x2="1" y2="1"
                gradientUnits="objectBoundingBox">
  <animateTransform attributeName="gradientTransform" type="rotate"
                    from="45 0.5 0.5" to="405 0.5 0.5" dur="18s" repeatCount="indefinite"/>
  <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0"/>
  <stop offset="42%"  stop-color="#FFFFFF" stop-opacity="0"/>
  <stop offset="50%"  stop-color="#FFFFFF" stop-opacity="0.40"/>
  <stop offset="58%"  stop-color="#FFFFFF" stop-opacity="0"/>
  <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
</linearGradient>
```

Plus a small bump on the diffuse body: `accent_b@40%` → `accent_b@55%` for slightly more body color.

The interaction of two animated gradients at different speeds gives the brain a "light catching off curved surface" feel — the visual signature of premium 3D / liquid glass.

### B. Card polish

Three changes to each lobe card:

#### B1. Replace breathing top stripe with traveling edge glow

**Today:** `<rect width="320" height="4" fill="{color}" class="breathe-stripe">` at the top, animating opacity 0.85↔1.0 over 3s. Barely perceptible.

**New:** Delete the stripe. Add a `<rect>` outline that wraps the full card perimeter with an animated `stroke-dasharray + stroke-dashoffset` so a thin 80px-long colored segment travels around the perimeter once per 4s (similar visual idea to Vision Pro's window highlight rings).

```xml
<rect x="0" y="0" width="320" height="140" rx="14" fill="none"
      stroke="{color}" stroke-width="2"
      class="card-edge ce{i+1}" pathLength="1000"/>
```

Plus CSS:
```css
.card-edge {
  stroke-dasharray: 80 1000;
  animation: cardEdgeTravel 4s linear infinite;
  filter: url(#electricGlow);
  opacity: 0.9;
}
@keyframes cardEdgeTravel { to { stroke-dashoffset: -1080; } }
.ce1 { animation-delay: 0s; }
.ce2 { animation-delay: 0.7s; }
.ce3 { animation-delay: 1.4s; }
.ce4 { animation-delay: 2.1s; }
.ce5 { animation-delay: 2.8s; }
.ce6 { animation-delay: 3.5s; }
```

`pathLength="1000"` normalizes the perimeter so dashoffset works without measuring.

#### B2. Inner radial glow per card

A subtle radial gradient inside each card, tinted in the lobe color, pulsing 5s. Adds warmth without distracting.

```xml
<radialGradient id="cardInnerGlow_{key}" cx="50%" cy="50%" r="60%">
  <stop offset="0%"   stop-color="{color}" stop-opacity="0.18"/>
  <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
</radialGradient>
...
<rect x="6" y="6" width="308" height="128" rx="10"
      fill="url(#cardInnerGlow_{key})" class="card-inner-pulse"/>
```

CSS:
```css
.card-inner-pulse { animation: cardPulse 5s ease-in-out infinite; }
@keyframes cardPulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1.0; } }
```

#### B3. Stacked drop shadow + typography polish

**Replace** `cardShadow` filter with `cardShadowStacked` — three `feDropShadow` layered for real depth:

```xml
<filter id="cardShadowStacked" x="-50%" y="-50%" width="200%" height="200%">
  <feDropShadow dx="0" dy="2"  stdDeviation="4"  flood-color="#000" flood-opacity="0.30"/>
  <feDropShadow dx="0" dy="6"  stdDeviation="12" flood-color="#000" flood-opacity="0.40"/>
  <feDropShadow dx="0" dy="14" stdDeviation="24" flood-color="#000" flood-opacity="0.30"/>
</filter>
```

**Typography polish in `<style>`:**
- `.t-cat-cap`: `letter-spacing: 0.20em` → `0.30em`, `font-weight: 700` → `800`
- `.t-region` (the emoji + domain text): drop the emoji size by 20% — wrap the emoji in `<tspan font-size="20">{emoji}</tspan>`

### C. Atmosphere — make it lively (no noise)

Three additions:

#### C1. Particle constellation lines

For the 16 ambient particles, pre-compute pairs within 220px of each other (deterministically — fixed positions, fixed pairs). For each pair, emit a thin `<line>` at low opacity that fades in and out via CSS over 8s on staggered phases. Reads as a neural-web / constellation.

Compute at build time: `_particle_pairs(particles: list[(x,y)], threshold=220) -> list[(int, int)]` returns indices into the particle list.

Render:
```xml
<line x1="..." y1="..." x2="..." y2="..."
      stroke="{p_accent_b}" stroke-width="0.8" stroke-opacity="0"
      class="constellation-line cl{n}"/>
```

CSS:
```css
.constellation-line { animation: clFade 8s ease-in-out infinite; }
@keyframes clFade { 0%, 100% { stroke-opacity: 0; } 50% { stroke-opacity: 0.30; } }
.cl1 { animation-delay: 0s; }   .cl2 { animation-delay: 1s; }   ...
```

Up to ~12 lines depending on how the 16 fixed particle positions cluster.

#### C2. Occasional light streaks

5 thin diagonal `<line>` elements at staggered positions, each animating with `<animate>` on x1/x2/opacity to traverse the canvas over 3s, then 8–14s gap before next firing. Reads as meteors / lens flares.

```xml
<line x1="-100" y1="200" x2="-100" y2="220"
      stroke="#EC4899" stroke-width="1.5" stroke-opacity="0"
      filter="url(#electricGlow)" class="light-streak ls1">
  <animate attributeName="x1" values="-100;1500" dur="3s" begin="0s;13s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="0;1600" dur="3s" begin="0s;13s" repeatCount="indefinite"/>
  <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
           dur="3s" begin="0s;13s" repeatCount="indefinite"/>
</line>
```

5 streaks, each on its own begin times (`0s;13s`, `2s;15s`, `5s;18s`, `8s;21s`, `11s;24s`) so the firing reads as continuous but irregular.

Gated by `atm.show_particles` (matches existing flag).

#### C3. Make `bgAura` move

Today: static radial gradient covering the canvas. Add `<animateTransform>` translating ±150px diagonal motion over 40s. Bumps the dynamic feel of the background without visible motion.

## Implementation order

A → D → B → C, as specified by the user. Estimated 8 plan tasks, ~6-8 commits, ~60-90 minutes of subagent-driven work.

Same branch (`feature/brain-professional-visuals`) — these polish commits land alongside the Round 1 commits before merging to main.

## Out of scope

- New cortex.yml schema fields (atm.show_aura and atm.show_particles already exist).
- Light streaks rendering when `atm.show_particles=False` (gating handles this).
- Aurora rendering when `atm.show_aura=False` (gating handles this).
- Per-palette tweaks for non-`neon-rainbow` palettes (the colors used in aurora and streaks are hardcoded — assumes the magenta/purple/cyan vocabulary is universal, which is true for all 5 named palettes since they all carry these as accents in some form).

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Specular pass doubles brain SVG size | The duplicated content reuses the same `d` attributes; net adds ~30 KB on a 79 KB file (~38%). Acceptable. |
| `mix-blend-mode: screen` not supported on older browsers | GitHub's renderer supports it; modern README viewers all do. Worst case: no specular highlight, body fill still renders normally. |
| Aurora drift across canvas edges leaves visible color blocks | The radial gradients fade to 0 at their edges, so even if the rect translates 200px, the visible area always has a smooth falloff. |
| Light streaks fire when user has `atm.show_particles=False` | Gate streaks on the same flag. |
| 13+ new SMIL animations push browser perf | Round 1 net was −6 SMIL animations (gradient consolidation). Round 2 adds: 3 aurora `translate`, 1 specular `rotate`, 5 streaks × 3 attrs = 15 SMIL. Net total = +13 SMIL on top of where we started. Within reason for static rendered SVG in README. |

## Self-review checklist

- [x] Placeholder scan: no `TBD`, no `<insert>` left.
- [x] Internal consistency: aurora gradients don't conflict with `bgAura` (existing). bgAura stays; aurora adds 3 more layers above it but below the brain.
- [x] Scope check: focused, single implementation plan, no decomposition needed.
- [x] Ambiguity check:
  - "Specular pass uses screen blend mode" — explicitly stated, not "some blend mode."
  - "Aurora colors are hardcoded pink/purple/cyan" — explicit, not "palette-driven."
  - "Light streaks gate on `atm.show_particles`" — explicit.
