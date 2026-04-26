# Cortex — Visual Tooling Decision

> "Should we use Figma, Lottie, Three.js, AI image generation, or something else to make the outputs more professional and impressive?"
>
> Short answer: **No** — the GitHub-renders-no-JS constraint rules out most of what people think of as "modern visual tooling". The path to mind-blowing visuals goes through **mastering SVG techniques we currently underuse**, not switching tools.
>
> Companion to [`VISION.md`](./VISION.md). Decision-log entry: 2026-04-26.

---

## The hard constraint that drives every choice

GitHub's README renderer fetches embedded images through a proxy called **camo**, then serves them with a strict `Content-Security-Policy` that **strips all `<script>` tags from SVG content**. This is not a bug; it's a security measure. Every README that embeds an SVG worldwide is bound by this rule.

What this rules out for **README-embedded** widgets:

| Tool | Why it doesn't work in a GitHub README |
|---|---|
| **Lottie** (Bodymovin) | Requires `lottie-web` JS player to interpret JSON animations |
| **Rive** | Requires `rive-canvas` JS runtime |
| **Three.js / WebGL** | Native JS; no rendering without a script context |
| **GSAP** | JS animation library |
| **D3.js client-side** | JS-driven DOM manipulation |
| **anime.js** | Same |
| **Framer Motion / React** | Requires React runtime |
| **PixiJS / p5.js** | JS canvas/WebGL |
| **Figma interactive prototypes** | Use Figma's own JS runtime |

This is why every popular profile-README tool — `lowlighter/metrics`, `anuraghazra/github-readme-stats`, `kyechan99/capsule-render`, `DenverCoder1/readme-typing-svg` — generates **server-side SVG with no JS**. There is no exception. None of them embed Lottie or Three.js for the same reason we can't.

What **does** render in a GitHub-served SVG:

- Static SVG paths, gradients, text, shapes
- `<style>` blocks with CSS animations + keyframes
- SMIL animations: `<animate>`, `<animateTransform>`, `<animateMotion>`, `<set>`
- SVG filter effects: every `<fe*>` primitive (turbulence, displacement, blur, color-matrix, morphology, ...)
- Masks (`<mask>`, `<clipPath>`)
- Blend modes (`mix-blend-mode`)

This is more powerful than most developers realize. The next section maps the unused capacity.

---

## What we're underusing (the path to "mind-blowing")

Cortex currently uses ~30% of what plain SVG can do. The remaining 70% is where the visual upgrade lives.

### `feTurbulence` — Perlin noise generator built into SVG

```xml
<filter id="neuralPlasma">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="2">
    <animate attributeName="baseFrequency" values="0.02;0.04;0.02" dur="8s" repeatCount="indefinite"/>
  </feTurbulence>
  <feDisplacementMap in="SourceGraphic" scale="14"/>
</filter>
```

Apply this filter to any element and it gets a living, swirling distortion driven by animated noise. Use cases inside the brain:
- **Plasma fog** behind the brain anatomy — animated baseFrequency creates swirling cosmic background
- **Brain "thinking" pulse** — apply to the brain group at low scale, it gently warps as if alive
- **Lightning arcs** — feTurbulence + threshold + glow = electric bolts traveling between lobes

This is a **single filter** that creates effects that would otherwise require GPU shaders or video.

### `<animateMotion>` along an SVG path

```xml
<circle r="3" fill="#22D3EE">
  <animateMotion dur="3s" repeatCount="indefinite">
    <mpath href="#leaderLineFrontal"/>
  </animateMotion>
</circle>
```

A small dot traveling along the leader-line path. Multiplied across all 6 leader lines = "data packets" flowing from cards → brain in real time. Combined with a fade-in/fade-out animation it looks like binary data streaming.

### `feMorphology` + `feGaussianBlur` for electric glow

```xml
<filter id="electricGlow">
  <feMorphology operator="dilate" radius="1.5"/>
  <feGaussianBlur stdDeviation="3"/>
  <feFlood flood-color="#22D3EE"/>
  <feComposite in2="SourceGraphic" operator="in"/>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
```

Outline + glow combined. Apply to micro-cells = each synaptic firing has an electric corona. Apply to leader-line endpoints = the line tip looks plasma-charged.

### Animated path morphing

```xml
<path d="M 100,100 L 200,200">
  <animate attributeName="d" dur="3s" repeatCount="indefinite"
    values="M 100,100 L 200,200; M 100,100 Q 150,80 200,200; M 100,100 L 200,200"/>
</path>
```

Paths can morph between shapes. Leader lines could pulse in/out, breathe, or even rearrange themselves. The brain anatomy paths could "inhale" — slight morph that reads as breathing.

### Mask animation reveals

```xml
<mask id="scanline">
  <rect width="1400" height="20" fill="white" y="0">
    <animate attributeName="y" values="0;900;0" dur="6s" repeatCount="indefinite"/>
  </rect>
</mask>
```

A horizontal line scanning down the canvas, revealing brain interior detail — like a medical CT scan or sci-fi terminal effect. Pure SVG, no JS.

### Filter chains for compound effects

`<filter>` elements chain feXxx primitives in series. Real-world recipes:

| Effect | Recipe |
|---|---|
| **Glow / bloom** | feGaussianBlur → feMerge with source |
| **Outline** | feMorphology dilate → feFlood → feComposite in |
| **Plasma fog** | feTurbulence → feColorMatrix hue-rotate animated |
| **Holographic shimmer** | feTurbulence (low freq) → feDisplacementMap → animated seed |
| **Liquid distortion** | feGaussianBlur → feDisplacementMap with noise source |
| **Color shift over time** | feColorMatrix `type="hueRotate"` with animated `values` |

Cortex's brain currently uses **one** filter (`brainGlow`, just a blur+merge). We could be using six.

---

## Where Figma fits — and where it doesn't

Figma is a design tool, not a runtime. The output of Figma is either:

1. **Static images** (PNG/JPEG/SVG export) — usable
2. **Interactive prototypes** (figma.com only) — not usable in a README

What Figma is good for in this project:

- **Mock the look first**, then implement. Designer drafts the brain composition with all the lighting, color, layout in Figma. Once approved, we re-implement in Python-generated SVG with theming/templating injected. Most professional design-driven generators work this way.
- **Static decorative assets**. A custom header banner, a custom divider, a hero illustration that doesn't need per-user theming — design in Figma, export as SVG, commit to `packages/cortex-core/cortex/assets/`. Treat it like the Wikimedia brain anatomy.

What Figma is **not** good for here:

- Per-user dynamic content. Cortex generates a brain *for each user* with their config. Figma can't bind to a YAML config or animate from data — the templating layer must live in code.
- Animations bound to data. Figma's prototype animations are time-based, not data-driven. You can't say "particle count = number of GitHub repos" in Figma.

---

## What about AI image generation (DALL-E / Midjourney / Stable Diffusion)?

Tempting, but wrong tool for this job because:

- **Non-deterministic**. Same input → different output every time. We need reproducibility.
- **Raster, not vector**. Output is PNG/JPEG. Loses scalability, can't be themed by editing source.
- **Per-generation cost**. Each user's profile would need an API call (~$0.04-0.30 per image). Not free-tier compatible.
- **Not on-brand**. AI-generated brains look painterly; cortex's brand is precise neon/cyberpunk anatomy.

Where it *would* fit: a one-time hero illustration for `apps/docs/`, hand-curated and committed as a static asset. That's already a Phase D possibility (the v2.1 "AI portrait" feature).

---

## What about pre-rendered video (FFmpeg, After Effects → Lottie)?

For the 30-second "Cortex in action" demo video on the marketing landing page, **yes** — record a screencast, polish in After Effects, export as MP4. That's a marketing asset, not a README embed. Already noted in VISION.md's go-viral strategy.

For the README-embedded widgets, **no** — videos can't be embedded inline (GitHub strips `<video>` and `<iframe>`).

---

## The actual recommendation

| Surface | Tool stack | Why |
|---|---|---|
| **README-embedded SVG widgets** | Python f-string templates + advanced SVG (filters, SMIL, CSS animations) | Hard constraint; what every successful profile-README generator does |
| **3D viewer page** (`apps/dashboard/`, `/docs/`) | Three.js + shaders + post-processing | No JS constraint here; full web tech available |
| **Marketing landing page** (`docs.cortex.dev`) | Next.js + Framer Motion + Lottie | No JS constraint here; can use full design-tool exports |
| **Static decorative assets** (banners, dividers, hero illustrations) | Designed in Figma, exported as SVG, committed to `assets/` | Best of both: visual quality + version control |
| **Demo video** for marketing | Screen-record + After Effects polish | Standard product-launch workflow |

---

## Concrete next steps for the brain widget

These are **all SVG**, all work in GitHub README, all pure animation/filter techniques. Listed in approximate order of visual impact per implementation hour:

1. **`feTurbulence`-driven plasma fog** behind the brain. Replaces or supplements the static `bgRadial`. Animated `baseFrequency` creates swirling motion. ~30 min to implement.
2. **`<animateMotion>` data packets traveling along leader lines** — small dots flowing from card → brain at staggered intervals, fading in and out. Reads as data streaming. ~45 min.
3. **`feMorphology` + `feGaussianBlur` electric glow on micro-cells** — synaptic firing now also has an electric corona. ~20 min.
4. **Animated `feColorMatrix` hue rotation on micro-cells** — synaptic colors shift through the spectrum on each firing. ~15 min.
5. **Path morphing on leader lines** — lines breathe in and out, suggesting living connection. ~30 min.
6. **Animated mask reveal** — when a region pulses, its mask reveals brain detail underneath. ~45 min.
7. **`feDisplacementMap` warp on the brain when wobbling** — the brain anatomy itself ripples with each wobble cycle. ~30 min.
8. **Per-lobe path classification** (deferred research) — bounding-box analysis of cerebrum's 149 paths to assign each to frontal/parietal/occipital/temporal. Unlocks per-region anatomical coloring. ~2 hours.

Each is a separate commit; we can ship them iteratively.

---

## Decision

We **stay on Python-generated SVG** for all README-embedded widgets, but we level up our SVG techniques. The above 8 enhancements are queued in `CONTEXT.md`'s "Active work" section. Figma stays available for static decorative assets if/when we need them, but is not the primary visual tool.

The constraint that looks limiting is actually a moat: every competing tool has the same constraint, but most of them never get past simple charts. Cortex's edge is using SVG more aggressively than anyone else.
