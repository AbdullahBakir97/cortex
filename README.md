<!-- This is the marketing README that goes at the root of the cortex repo.
     Visitors land here from Hacker News, Product Hunt, marketplace listings, awesome-lists.
     The entire job: convince them in 10 seconds, install in 30. -->

<!-- ════════════════════════════════════════════════════════════════════════ -->
<!-- 🎬 ANIMATED HERO BANNER — capsule-render with brain-themed gradient     -->
<!-- ════════════════════════════════════════════════════════════════════════ -->
 
<a href="https://cortex.dev">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1117,50:7C3AED,100:F90001&height=240&section=header&text=Cortex&fontSize=110&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Turn%20your%20GitHub%20into%20a%20cinematic%20neon%20brain%20skill%20atlas&descSize=20&descAlignY=58&descColor=F0F0F0" width="100%" alt="Cortex — turn your GitHub into a cinematic neon brain skill atlas"/>
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
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/brain-anatomical.svg" alt="Cortex anatomical neon brain — generated from examples/extreme.yml, 200+ Wikimedia anatomy paths recolored with a multi-stop neon gradient. Each lobe maps to a skill domain." width="92%"/>
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
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/brain-anatomical.svg" width="92%" alt="Anatomical brain SVG with neon-rainbow gradient, each lobe labelled with a skill domain"/>
</p>
</details>

<details>
<summary><strong>🎴 Tech cards — six glassmorphism skill panels</strong> &nbsp;·&nbsp; <code>tech-cards.svg</code> · 13 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/tech-cards.svg" width="92%" alt="Six glassmorphism cards arranged in a 3x2 grid, each one a brain region's tools and stats"/>
</p>
</details>

<details>
<summary><strong>📅 Yearly highlights — career timeline with LIVE pulse</strong> &nbsp;·&nbsp; <code>yearly-highlights.svg</code> · 14 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/yearly-highlights.svg" width="92%" alt="Year-by-year career timeline with markers and a live-pulsing tag for the current year"/>
</p>
</details>

<details>
<summary><strong>📺 Current focus — Netflix-tile dashboard</strong> &nbsp;·&nbsp; <code>current-focus.svg</code> · 14 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/current-focus.svg" width="92%" alt="Six tiles in a 3x2 grid, each one a project the author is actively working on with a status pill and tech stack"/>
</p>
</details>

<details>
<summary><strong>⌨️ About typing — multilingual rotating headlines</strong> &nbsp;·&nbsp; <code>about-typing.svg</code> · 16 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/about-typing.svg" width="92%" alt="Animated typing SVG cycling through about-me lines in multiple languages"/>
</p>
</details>

<details>
<summary><strong>💬 Motto typing — philosophy lines on rotation</strong> &nbsp;·&nbsp; <code>motto-typing.svg</code> · 17 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/motto-typing.svg" width="92%" alt="Animated typing SVG cycling through personal mottos and philosophy lines"/>
</p>
</details>

<details>
<summary><strong>✨ Animated divider</strong> &nbsp;·&nbsp; <code>animated-divider.svg</code> · 1 KB</summary>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/rendered/extreme/animated-divider.svg" width="92%" alt="Thin animated gradient divider"/>
</p>
</details>

> **Want to see other tiers?** [`examples/standard.yml`](./examples/standard.yml) is the default for full-stack devs (~60 lines). [`examples/minimal.yml`](./examples/minimal.yml) is the 10-line starting point. Both render to the same widget set above with smaller payloads.

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
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:F90001,50:7C3AED,100:0D1117&height=140&section=footer&text=Build%20your%20brain&fontSize=32&fontColor=ffffff&animation=twinkling&fontAlignY=72&reversal=true" width="100%" alt="Build your brain"/>
</a>
