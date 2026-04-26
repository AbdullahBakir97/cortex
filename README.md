<!-- This is the marketing README that goes at the root of the cortex repo.
     Visitors land here from Hacker News, Product Hunt, marketplace listings, awesome-lists.
     The entire job: convince them in 10 seconds, install in 30. -->

<!-- ════════════════════════════════════════════════════════════════════════ -->
<!-- 🎬 ANIMATED HERO BANNER — Cortex's own generated banner (no external dep) -->
<!-- ════════════════════════════════════════════════════════════════════════ -->

<a href="https://cortex.dev">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/header-banner.svg" width="100%" alt="Cortex — turn your GitHub into a cinematic neon brain skill atlas"/>
</a>

<p align="center">
  <a href="https://github.com/marketplace/actions/cortex"><img src="https://img.shields.io/badge/GitHub_Action-v1-F90001?style=for-the-badge&logo=githubactions&logoColor=white&labelColor=0D1117" alt="Cortex Action v1"/></a>
  &nbsp;
  <a href="https://abdullahbakir97.github.io/AbdullahBakir97/"><img src="https://img.shields.io/badge/🧠_Live_Demo-Interactive_3D-7C3AED?style=for-the-badge&labelColor=0D1117" alt="Live demo"/></a>
  &nbsp;
  <a href="https://docs.cortex.dev"><img src="https://img.shields.io/badge/Docs-Get_Started-22D3EE?style=for-the-badge&labelColor=0D1117" alt="Docs"/></a>
  &nbsp;
  <a href="#-installation"><img src="https://img.shields.io/badge/Install-30s_setup-34D399?style=for-the-badge&labelColor=0D1117" alt="Install"/></a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=AbdullahBakir97-cortex&label=PROFILES%20BUILT&color=F90001&style=for-the-badge" alt="Profiles built" />
  <img src="https://img.shields.io/github/stars/AbdullahBakir97/cortex?style=for-the-badge&color=F90001&logo=github&logoColor=white&labelColor=0D1117" alt="Stars" />
  <img src="https://img.shields.io/github/v/release/AbdullahBakir97/cortex?style=for-the-badge&color=F90001&label=version&labelColor=0D1117" alt="Latest version" />
</p>

<br/>

> **Cortex turns your GitHub profile into an anatomically-accurate neon-rendered skill brain that pulses with your real activity, narrates itself in 3 languages, and updates daily — all from a 30-line YAML config.**

<br/>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/brain-anatomical.svg" alt="Cortex anatomical neon brain — generated from examples/extreme.yml, 200+ Wikimedia anatomy paths recolored with a multi-stop neon gradient. Each lobe maps to a skill domain." width="100%"/>
</p>

<p align="center">
  <sub>↑ <strong>Live SVG</strong> — generated from <a href="./examples/extreme.yml"><code>examples/extreme.yml</code></a> on every push. Open <a href="https://abdullahbakir97.github.io/AbdullahBakir97/">the 3D version</a> to drag and rotate it.</sub>
</p>

---

## ✨ Why Cortex

There are dozens of profile README generators. Cortex is the only one that gives you:

- **🧠 An actual neon brain** — built from real Wikimedia anatomy (200+ paths), recolored with a multi-stop neon gradient that flows in real time. Each lobe maps to a skill domain you define.
- **🌌 Interactive 3D version** auto-published to your GitHub Pages — drag, rotate, zoom. Three.js + OrbitControls, no setup.
- **🌍 Multilingual identity** — type-out headlines in English, Deutsch, العربية, or any language Unicode supports. 30+ rotating lines per language.
- **♾️ 50-line auto-updating widgets** — terminal commands, philosophy mottos, current focus, yearly highlights, recent activity, latest releases, contribution graphs, PageSpeed scores, WakaTime stats, and more. All refreshed daily.
- **🎨 4 cinematic SVG card systems** — tech stack, current focus, yearly timeline, anatomical brain — composed with glassmorphism, breathing borders, traveling synapses, animated gradients.
- **🚀 30-second install** — one workflow file, one config file, no JS, no build step on your end. Ships as a GitHub Action.

---

## 🎨 What this generates

> Every image below is the **actual output** from [`examples/extreme.yml`](./examples/extreme.yml). Refreshed on every push by [`.github/workflows/build-examples.yml`](./.github/workflows/build-examples.yml) — no screenshots, no fakes.

<details open>
<summary><strong>🧠 Brain — anatomical skill atlas</strong> &nbsp;·&nbsp; <code>brain-anatomical.svg</code> · 42 KB · 200+ paths</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/brain-anatomical.svg" width="100%" alt="Anatomical brain SVG with neon-rainbow gradient, each lobe labelled with a skill domain"/>
</p>
</details>

<details>
<summary><strong>🎴 Tech cards — six glassmorphism skill panels</strong> &nbsp;·&nbsp; <code>tech-cards.svg</code> · 13 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/tech-cards.svg" width="100%" alt="Six glassmorphism cards arranged in a 3x2 grid, each one a brain region's tools and stats"/>
</p>
</details>

<details>
<summary><strong>📅 Yearly highlights — career timeline with LIVE pulse</strong> &nbsp;·&nbsp; <code>yearly-highlights.svg</code> · 14 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/yearly-highlights.svg" width="100%" alt="Year-by-year career timeline with markers and a live-pulsing tag for the current year"/>
</p>
</details>

<details>
<summary><strong>📺 Current focus — Netflix-tile dashboard</strong> &nbsp;·&nbsp; <code>current-focus.svg</code> · 14 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/current-focus.svg" width="100%" alt="Six tiles in a 3x2 grid, each one a project the author is actively working on with a status pill and tech stack"/>
</p>
</details>

<details>
<summary><strong>⌨️ About typing — multilingual rotating headlines</strong> &nbsp;·&nbsp; <code>about-typing.svg</code> · 16 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/about-typing.svg" width="100%" alt="Animated typing SVG cycling through about-me lines in multiple languages"/>
</p>
</details>

<details>
<summary><strong>💬 Motto typing — philosophy lines on rotation</strong> &nbsp;·&nbsp; <code>motto-typing.svg</code> · 17 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/motto-typing.svg" width="100%" alt="Animated typing SVG cycling through personal mottos and philosophy lines"/>
</p>
</details>

<details>
<summary><strong>✨ Animated divider</strong> &nbsp;·&nbsp; <code>animated-divider.svg</code> · 1 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/animated-divider.svg" width="100%" alt="Thin animated gradient divider"/>
</p>
</details>

> **Want to see other tiers?** [`examples/standard.yml`](./examples/standard.yml) is the default for full-stack devs (~60 lines). [`examples/minimal.yml`](./examples/minimal.yml) is the 10-line starting point. Both render to the same widget set above with smaller payloads.

---

<!-- ════════════════════════════════════════════════════════════════════════ -->
<!-- 🎨 AUTO-GENERATED WIDGET CATALOG — populated by `cortex update-readme`.   -->
<!-- Each push refreshes this block with previews of every Cortex widget plus -->
<!-- the cortex.yml snippet to enable + customize it. Set                    -->
<!-- `auto_update.markers.showcase: false` to suppress.                       -->
<!-- ════════════════════════════════════════════════════════════════════════ -->

<!-- CORTEX:SHOWCASE:START -->
## 🎨 What Cortex Generates — Examples & Recipes

Every preview below is a live SVG generated from your `cortex.yml`. Each widget has multiple example configurations — click any `<details>` to expand the variant and copy the snippet straight into your config. Full schema reference: [`packages/cortex-schema/schema.json`](packages/cortex-schema/schema.json).

<details>
<summary><strong>Header Banner</strong> &nbsp;·&nbsp; <code>header-banner.svg</code> &nbsp;·&nbsp; 4 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/header-banner.svg" alt="Header Banner" width="100%"/>
</p>

_Wide animated banner with shaped edge — capsule-render replacement. Title, subtitle, drifting gradient._

<details>
<summary><em>Wave shape, drifting (default)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/header-banner__wave-drift.svg" alt="Header Banner — Wave shape, drifting (default)" width="100%"/>
</p>

Sine-wave bottom edge, jewel-tone gradient drifts left↔right on a 22s ease-in-out cycle.

```yaml
cards:
  header:
    enabled: true
    shape: wave
    title: "Your Name"
    subtitle: "FULLSTACK · ENGINEER · BUILDER"
    height: 240
    animation: drift
```

</details>

<details>
<summary><em>Slice shape, pulsing</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/header-banner__slice-pulse.svg" alt="Header Banner — Slice shape, pulsing" width="100%"/>
</p>

Diagonal bottom edge with opacity pulse — minimalist, matches landing-page aesthetics.

```yaml
cards:
  header:
    enabled: true
    shape: slice
    title: "Your Name"
    height: 220
    animation: pulse
```

</details>

<details>
<summary><em>Rect shape, static</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/header-banner__rect-static.svg" alt="Header Banner — Rect shape, static" width="100%"/>
</p>

No shaped edge, no animation — clean rectangular header for code-focused profiles.

```yaml
cards:
  header:
    enabled: true
    shape: rect
    title: "Your Name"
    subtitle: "github.com/your-handle"
    height: 180
    animation: static
```

</details>

<details>
<summary><em>Custom color palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/header-banner__custom-palette.svg" alt="Header Banner — Custom color palette" width="100%"/>
</p>

Override the default jewel-tones with your own gradient stops (3-5 hex colors recommended).

```yaml
cards:
  header:
    enabled: true
    shape: wave
    title: "Your Name"
    height: 240
    animation: drift
    colors: ["#0D1117", "#1E3A8A", "#2563EB", "#0EA5E9", "#0D1117"]
```

</details>

</details>

<details>
<summary><strong>Anatomical Brain</strong> &nbsp;·&nbsp; <code>brain-anatomical.svg</code> &nbsp;·&nbsp; 5 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/brain-anatomical.svg" alt="Anatomical Brain" width="100%"/>
</p>

_200+ Wikimedia anatomy paths recolored with rose-family gradient, masked aurora flow, DNA helixes, electric arcs across 6 lobes._

<details>
<summary><em>Default neon-rainbow palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/brain-anatomical__neon-rainbow.svg" alt="Anatomical Brain — Default neon-rainbow palette" width="100%"/>
</p>

Six lobes mapped to skill domains, full atmospheric layers (aurora, particles, DNA, halos), 3D wobble enabled.

```yaml
brand:
  palette: neon-rainbow
brain:
  enabled: true
  atmosphere:
    show_aura: true
    show_particles: true
    show_halos: true
    wobble: true
```

</details>

<details>
<summary><em>Cyberpunk palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/brain-anatomical__cyberpunk.svg" alt="Anatomical Brain — Cyberpunk palette" width="100%"/>
</p>

Hot magenta + electric cyan + acid yellow — same brain anatomy, different vibe.

```yaml
brand:
  palette: cyberpunk
brain:
  enabled: true
  atmosphere:
    show_aura: true
    show_particles: true
    wobble: true
```

</details>

<details>
<summary><em>Monochrome (atmosphere off)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/brain-anatomical__monochrome.svg" alt="Anatomical Brain — Monochrome (atmosphere off)" width="100%"/>
</p>

Subtle, professional single-accent rendering — atmospheric layers disabled for a code-focused look.

```yaml
brand:
  palette: monochrome
brain:
  enabled: true
  atmosphere:
    show_aura: false
    show_particles: false
    show_halos: false
    wobble: false
```

</details>

<details>
<summary><em>Retro warm palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/brain-anatomical__retro.svg" alt="Anatomical Brain — Retro warm palette" width="100%"/>
</p>

Warm 80s-inspired colors — orange/amber tones over rose body. Good for solo dev / indie hacker vibes.

```yaml
brand:
  palette: retro
brain:
  enabled: true
  atmosphere:
    show_aura: true
    show_particles: true
    wobble: true
```

</details>

<details>
<summary><em>Minimal palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/brain-anatomical__minimal.svg" alt="Anatomical Brain — Minimal palette" width="100%"/>
</p>

Subtle neutrals + one warm accent — professional, understated, terminal-friendly.

```yaml
brand:
  palette: minimal
brain:
  enabled: true
  atmosphere:
    show_aura: true
    show_particles: false
    show_halos: false
    wobble: true
```

</details>

</details>

<details>
<summary><strong>Tech Stack Cards</strong> &nbsp;·&nbsp; <code>tech-cards.svg</code> &nbsp;·&nbsp; 2 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/tech-cards.svg" alt="Tech Stack Cards" width="100%"/>
</p>

_6 glassmorphism cards in a 3x2 grid — one per brain region. Stacked drop shadows, traveling edge glow per card, inner color pulse._

<details>
<summary><em>With stats (default)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/tech-cards__with-stats.svg" alt="Tech Stack Cards — With stats (default)" width="100%"/>
</p>

Each card shows years/projects/mastery row plus an animated proficiency bar.

```yaml
cards:
  tech_stack:
    enabled: true
    show_stats: true
```

</details>

<details>
<summary><em>Without stats — text-only</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/tech-cards__without-stats.svg" alt="Tech Stack Cards — Without stats — text-only" width="100%"/>
</p>

Hide the years/projects/mastery row for a cleaner card focused on the tools list and tagline.

```yaml
cards:
  tech_stack:
    enabled: true
    show_stats: false
```

</details>

</details>

<details>
<summary><strong>Current Focus Tiles</strong> &nbsp;·&nbsp; <code>current-focus.svg</code> &nbsp;·&nbsp; 2 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/current-focus.svg" alt="Current Focus Tiles" width="100%"/>
</p>

_Netflix-style "now playing" tiles for active projects — status pill, live dot, traveling edge highlight, tile-rise stagger animation._

<details>
<summary><em>Single project tile</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/current-focus__single-tile.svg" alt="Current Focus Tiles — Single project tile" width="100%"/>
</p>

Just one focus area — the grid auto-reflows so a 1-tile config still looks polished.

```yaml
cards:
  current_focus:
    enabled: true
    tiles:
      - project: "Cortex"
        status: SHIPPING
        accent: red
        emoji: "🧠"
        description: "Animated neon-brain README generator with 10 SVG widgets."
        tech: [Python, Pydantic, SVG, GitHub Actions]
```

</details>

<details>
<summary><em>Multiple tiles, mixed statuses + accents</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/current-focus__multiple-tiles.svg" alt="Current Focus Tiles — Multiple tiles, mixed statuses + accents" width="100%"/>
</p>

Up to 6 tiles in a 3x2 grid. status: ACTIVE/SHIPPING/EXPLORING/MAINTAINING/BUILDING. accent: red/orange/green/gold/cyan/purple.

```yaml
cards:
  current_focus:
    enabled: true
    tiles:
      - { project: "Cortex",     status: SHIPPING,    accent: red,    emoji: "🧠", description: "Profile README brain generator.",                       tech: [Python, SVG] }
      - { project: "Pydev",      status: BUILDING,    accent: orange, emoji: "🐍", description: "Local-first Python dev environment manager.",            tech: [Tauri, Vue, TypeScript] }
      - { project: "Skill DNA",  status: EXPLORING,   accent: cyan,   emoji: "🧬", description: "AI-driven skill atlas + portfolio generator.",            tech: [LangChain, RAG] }
      - { project: "Brain 3D",   status: MAINTAINING, accent: purple, emoji: "🌌", description: "Three.js viewer for the cortex brain.",                  tech: [Three.js, Vite] }
```

</details>

</details>

<details>
<summary><strong>Yearly Timeline</strong> &nbsp;·&nbsp; <code>yearly-highlights.svg</code> &nbsp;·&nbsp; 3 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/yearly-highlights.svg" alt="Yearly Timeline" width="100%"/>
</p>

_Horizontal career timeline — gradient connector, year markers with LIVE pulse on current year, tall cards with stats and bullets._

<details>
<summary><em>Auto-generated from start_year</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/yearly-highlights__auto.svg" alt="Yearly Timeline — Auto-generated from start_year" width="100%"/>
</p>

Just specify when you started — Cortex generates placeholder cards for every year up to today. Replace as you fill them in.

```yaml
cards:
  yearly_highlights:
    enabled: true
    start_year: 2022
    bullets_per_year: 3
    years: []
```

</details>

<details>
<summary><em>Fully custom years (recommended)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/yearly-highlights__fully-custom.svg" alt="Yearly Timeline — Fully custom years (recommended)" width="100%"/>
</p>

Hand-curate each year's headline, bullets, and stats. Up to 6 years; oldest first.

```yaml
cards:
  yearly_highlights:
    enabled: true
    years:
      - year: 2024
        label: "FOUNDATION"
        headline: "A Year of Shipping"
        bullets:
          - "Built foundations in Python + Vue."
          - "Earned first community stars."
        stats:
          - { num: "25+", label: "PROJECTS" }
          - { num: "52★", label: "PEAK STARS" }
      - year: 2025
        label: "GROWTH"
        headline: "Production & AI"
        bullets:
          - "Shipped LLM-powered features for clients."
          - "Open-sourced 3 internal tools."
        stats:
          - { num: "10+", label: "AI EXPERIMENTS" }
          - { num: "200+", label: "DEPLOYS" }
```

</details>

<details>
<summary><em>Tighter — start in 2024, 2 bullets per year</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/yearly-highlights__tighter.svg" alt="Yearly Timeline — Tighter — start in 2024, 2 bullets per year" width="100%"/>
</p>

Shorter cards for early-career profiles or when you want the timeline to feel tight rather than expansive.

```yaml
cards:
  yearly_highlights:
    enabled: true
    start_year: 2024
    bullets_per_year: 2
    years: []
```

</details>

</details>

<details>
<summary><strong>About Typing</strong> &nbsp;·&nbsp; <code>about-typing.svg</code> &nbsp;·&nbsp; 3 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/about-typing.svg" alt="About Typing" width="100%"/>
</p>

_Cycling terminal-style typing animation — 30+ rotating commands with jewel-tone cursor glow._

<details>
<summary><em>Generic only</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/about-typing__generic.svg" alt="About Typing — Generic only" width="100%"/>
</p>

Universal dev terminal commands ($ whoami, $ git status, etc.) — no personal references. Works for any profile.

```yaml
typing:
  about:
    enabled: true
    lines: 8
    include: [generic]
```

</details>

<details>
<summary><em>Personal only</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/about-typing__personal.svg" alt="About Typing — Personal only" width="100%"/>
</p>

References your specific projects from current_focus + identity (your github_user, project names, etc.). More personal.

```yaml
typing:
  about:
    enabled: true
    lines: 6
    include: [personal]
```

</details>

<details>
<summary><em>Both — recommended mix</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/about-typing__mixed.svg" alt="About Typing — Both — recommended mix" width="100%"/>
</p>

Mix of universal + personal lines — best balance of relatability and personality.

```yaml
typing:
  about:
    enabled: true
    lines: 10
    include: [generic, personal]
```

</details>

</details>

<details>
<summary><strong>Motto Typing</strong> &nbsp;·&nbsp; <code>motto-typing.svg</code> &nbsp;·&nbsp; 2 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/motto-typing.svg" alt="Motto Typing" width="100%"/>
</p>

_Philosophy quotes cycling — same engine as About but no cursor, longer hold time per line. Use for taglines/principles._

<details>
<summary><em>Default — 6 rotating mottos</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/motto-typing__default.svg" alt="Motto Typing — Default — 6 rotating mottos" width="100%"/>
</p>

Cortex ships 30+ curated dev-philosophy quotes; the typer cycles through 6 of them by default.

```yaml
typing:
  motto:
    enabled: true
    lines: 6
```

</details>

<details>
<summary><em>Tight — 4 lines, faster cycle</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/motto-typing__tight.svg" alt="Motto Typing — Tight — 4 lines, faster cycle" width="100%"/>
</p>

Fewer lines = each one shows for longer. Good when you want each motto to register fully before rotating.

```yaml
typing:
  motto:
    enabled: true
    lines: 4
```

</details>

</details>

<details>
<summary><strong>GitHub Icon</strong> &nbsp;·&nbsp; <code>github-icon.svg</code> &nbsp;·&nbsp; 1 example</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/github-icon.svg" alt="GitHub Icon" width="100%"/>
</p>

_Pulsing octocat disc with jewel-tone violet halo + soft Gaussian-blur glow — drop-in 96x96 profile icon._

<details>
<summary><em>Default (no config required)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/github-icon__default.svg" alt="GitHub Icon — Default (no config required)" width="100%"/>
</p>

Renders automatically from identity.github_user — no widget-level config exists. Halo color is the jewel-tone violet that ties to the rest of the composition.

```yaml
identity:
  github_user: "your-handle"  # the icon picks up your handle automatically
```

</details>

</details>

<details>
<summary><strong>Animated Divider</strong> &nbsp;·&nbsp; <code>animated-divider.svg</code> &nbsp;·&nbsp; 1 example</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/animated-divider.svg" alt="Animated Divider" width="100%"/>
</p>

_Three layered sine waves drifting in counterpoint at different speeds (9s/11s/14s) — used between sections._

<details>
<summary><em>Default (no config required)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/animated-divider__default.svg" alt="Animated Divider — Default (no config required)" width="100%"/>
</p>

Always-on, no widget-level config — the divider matches the jewel-tone palette of header/footer/brain. Drop the SVG anywhere in your README.

```yaml
# Place the rendered SVG anywhere in your README:
# ![](https://raw.githubusercontent.com/<user>/<user>/main/assets/animated-divider.svg)
```

</details>

</details>

<details>
<summary><strong>Footer Banner</strong> &nbsp;·&nbsp; <code>footer-banner.svg</code> &nbsp;·&nbsp; 3 examples</summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/footer-banner.svg" alt="Footer Banner" width="100%"/>
</p>

_Inverted wave-shape footer mirroring the header — title, subtitle, drifting jewel-tone gradient. Capsule-render replacement._

<details>
<summary><em>Wave shape, drifting (default)</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/footer-banner__wave-drift.svg" alt="Footer Banner — Wave shape, drifting (default)" width="100%"/>
</p>

Sine-wave top edge with the same drift animation as the header — symmetric bookends.

```yaml
cards:
  footer:
    enabled: true
    shape: wave
    title: "@your-handle"
    subtitle: "Built with Cortex"
    height: 180
    animation: drift
```

</details>

<details>
<summary><em>Slice shape, static</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/footer-banner__slice-static.svg" alt="Footer Banner — Slice shape, static" width="100%"/>
</p>

Diagonal top edge, no animation — minimal footer for understated profiles.

```yaml
cards:
  footer:
    enabled: true
    shape: slice
    title: "@your-handle"
    height: 140
    animation: static
```

</details>

<details>
<summary><em>Rect shape with custom palette</em></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/variants/footer-banner__rect-custom.svg" alt="Footer Banner — Rect shape with custom palette" width="100%"/>
</p>

Flat rectangular footer with your own brand colors — e.g., warm sunset gradient.

```yaml
cards:
  footer:
    enabled: true
    shape: rect
    title: "@your-handle"
    height: 120
    animation: drift
    colors: ["#1A0612", "#7C2D12", "#EA580C", "#FBBF24", "#1A0612"]
```

</details>

</details>

---
_All widgets render to pure SVG with SMIL + CSS animations — no JS, no build step, no external CDN dependency. Schema is validated at build time; mismatched configs fail loudly with field-specific error messages._
<!-- CORTEX:SHOWCASE:END -->

---

## 📺 Profile gallery

| Tier | Profile | Live 3D |
|---|---|---|
| **Reference (Extreme)** | [@AbdullahBakir97](https://github.com/AbdullahBakir97) | [3D Brain →](https://abdullahbakir97.github.io/AbdullahBakir97/) |
| **Standard** | _your profile here — submit a [showcase issue](https://github.com/AbdullahBakir97/cortex/issues/new?template=showcase.yml)_ | _coming soon_ |
| **Minimal** | _your profile here_ | _coming soon_ |

> Want a faster setup? Pick a [template archetype](./templates/) — Backend Engineer, Frontend Specialist, Data Scientist, Student, etc.

---

## ⚡ Installation (30 seconds)

### Step 1 — drop this workflow into your profile repo

```yaml
# .github/workflows/cortex.yml
name: Cortex Profile
on:
  schedule: [{cron: "0 6 * * *"}]
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AbdullahBakir97/cortex@v1
        with:
          config: .github/cortex.yml
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Step 2 — write a config

```yaml
# .github/cortex.yml
identity:
  name: "Your Name"
  github_user: "yourhandle"
  tagline: "What you do, in one line"

brand:
  palette: "neon-rainbow"

brain:
  enabled: true
  three_d: { enabled: true }

cards:
  tech_stack: { enabled: true }
  yearly_highlights: { enabled: true }
  current_focus: { enabled: true }

typing:
  header: { languages: [en], lines_per_language: 10 }
  about:  { lines: 30 }
  motto:  { lines: 30 }

auto_update:
  markers: { activity: true, latest_releases: true, quote_of_the_day: true }
```

### Step 3 — trigger once manually

GitHub → Actions tab → Cortex Profile → Run workflow.

That's it. Wait ~2 minutes for the first build. Reload your profile. 🧠

> **Want config autocomplete in VS Code?** Add `# yaml-language-server: $schema=https://cortex.dev/schema/v1.json` at the top of your `cortex.yml`.

---

## 🎯 What you get

- `assets/brain-anatomical.svg` — the centerpiece neon brain, ~200 anatomical paths
- `assets/tech-cards.svg` — 6 glassmorphism skill cards with stats + animated proficiency bars
- `assets/yearly-highlights.svg` — career timeline with year markers + LIVE pulse on current year
- `assets/current-focus.svg` — Netflix-tile dashboard for active projects
- `assets/about-typing.svg` + `motto-typing.svg` — 30-50 cycling lines each, multi-color
- `docs/index.html` — interactive 3D brain viewer (auto-deployed to GitHub Pages)
- `README.md` markers — auto-rewritten daily with: recent activity, latest releases, quote of the day, gitGraph, PageSpeed, WakaTime, more

---

## 🚀 Roadmap

- [x] **v1.0** — GitHub Action with 5 core widgets (current state of [@AbdullahBakir97](https://github.com/AbdullahBakir97))
- [ ] **v1.1** — Brain Heatmap (lobes glow by real GH activity per region)
- [ ] **v1.2** — Skill DNA Strand visualization
- [ ] **v1.3** — Project Trading Cards (Pokemon-style holographic SVGs)
- [ ] **v1.4** — Time-lapse brain (years 2018 → today rendered as animation)
- [ ] **v2.0** — Web dashboard (no-YAML config UI) at `app.cortex.dev`
- [ ] **v2.1** — AI Portrait generator
- [ ] **v2.2** — Digital Twin chatbot (visitors ask "what does X work on?")
- [ ] **v3.0** — Cortex Pro (custom domain for 3D viewer, advanced AI features)

> Vote on what we should ship next via [GitHub Discussions](https://github.com/AbdullahBakir97/cortex/discussions/categories/roadmap).

---

## 🌟 Showcase

Built something cool with Cortex? **[Open a Showcase issue](https://github.com/AbdullahBakir97/cortex/issues/new?template=showcase.yml)** — we feature one new profile in the README every Friday.

---

## ⚖️ License & attribution

- **Code**: [MIT](./LICENSE) — use it for anything, including commercial.
- **Brain anatomy SVG paths**: [CC-BY-SA-3.0](./LICENSES/BRAIN-ANATOMY-CC-BY-SA-3.0.txt) (Hugh Guiney, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Human-brain.SVG)). Cortex recolors these paths but the underlying geometry is Hugh's work.
- **Fonts**: JetBrains Mono ([OFL-1.1](https://github.com/JetBrains/JetBrainsMono/blob/master/OFL.txt)), Inter ([OFL-1.1](https://github.com/rsms/inter/blob/master/LICENSE.txt))
- **Inspiration**: [`lowlighter/metrics`](https://github.com/lowlighter/metrics), [`yoshi389111/github-profile-3d-contrib`](https://github.com/yoshi389111/github-profile-3d-contrib), [`anuraghazra/github-readme-stats`](https://github.com/anuraghazra/github-readme-stats) — Cortex stands on the shoulders of these giants and makes them work together.

---

<p align="center">
  <a href="https://twitter.com/intent/tweet?text=I%20just%20turned%20my%20GitHub%20profile%20into%20a%20neon%20brain%20with%20%40CortexProfile%20%F0%9F%A7%A0&url=https%3A%2F%2Fgithub.com%2FAbdullahBakir97%2Fcortex"><img src="https://img.shields.io/badge/Tweet-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white&labelColor=0D1117" alt="Tweet about Cortex"/></a>
  &nbsp;
  <a href="https://www.producthunt.com/products/cortex"><img src="https://img.shields.io/badge/Vote-Product_Hunt-DA552F?style=for-the-badge&logo=producthunt&logoColor=white&labelColor=0D1117" alt="Vote on Product Hunt"/></a>
  &nbsp;
  <a href="https://news.ycombinator.com/submit"><img src="https://img.shields.io/badge/Show-HN-FF6600?style=for-the-badge&logo=ycombinator&logoColor=white&labelColor=0D1117" alt="Show HN"/></a>
</p>

<p align="center">
  <sub>Made with 🧠 by <a href="https://github.com/AbdullahBakir97">@AbdullahBakir97</a> · <a href="https://github.com/AbdullahBakir97/cortex/discussions">Discussions</a> · <a href="https://github.com/AbdullahBakir97/cortex/issues/new/choose">Issues</a></sub>
</p>

<a href="#-cortex">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/footer-banner.svg" width="100%" alt="Built with Cortex"/>
</a>
