# Cortex v1 Development Summary

> Comprehensive log of the work that took Cortex from a 10-widget alpha to **v1.0.0 production release** — 22 widgets, 164 tests, real GitHub data integrations, coordinated theming, and a Marketplace-ready GitHub Action.

**Release tag:** [`v1.0.0`](https://github.com/AbdullahBakir97/cortex/releases/tag/v1.0.0)
**Date:** 2026-04-27

---

## TL;DR

| | Before | After |
|---|---|---|
| Widget builders | 10 | **22** |
| Tests passing | ~24 | **164** |
| SVGs per `cortex build` | 10 main / 0 variants | **21 main + 53 variants = 74** |
| Themes | hardcoded jewel-tone | **6 coordinated themes**, single-line switch |
| Real-data integrations | none | **GitHub stats + contribution calendar** |
| CLI commands | `init` · `validate` · `build` · `update-readme` · `viewer` | + `compose` |
| CI workflows | `ci.yml` · `build-examples.yml` · `refresh-context.yml` | + `health-check.yml` |
| Largest SVG | heatmap 51 KB · marquee 23 KB | heatmap 45 KB (-12%) · marquee 12 KB (**-47%**) |
| Accessibility | per-widget animation toggles | + `prefers-reduced-motion` CSS opt-out across 8 builders |
| Repo description | (empty) | populated + 18 topic tags |
| Marketplace | not listed | technically ready (one web-UI step remaining) |

---

## All 14 PRs merged

| # | Title | Commit |
|---|---|---|
| 1 | brain professional visuals + 9-widget polish + auto-rendered showcase | `d30bc0b` |
| 2 | revert(readme): restore capsule-render hero + footer banners | `03f6f02` |
| 3 | feat(badges): new compact skill/tech/achievement badges widget | `4d3ff2b` |
| 4 | docs(readme): feature badges widget with handwritten section | `c16caba` |
| 5 | feat: 7 mind-blowing widgets — galaxy, synthwave, radar, roadmap, heatmap, cubes, trophies | `5b3ec23` |
| 6 | docs(readme): feature 7 new widgets in handwritten showcase grid | `7631fec` |
| 7 | feat: 4 more widgets — DNA helix, globe, particle cloud, now-playing | `64e68d2` |
| 8 | docs+ci: README grid for batch-3 + persistent health-check workflow | `e1c12a4` |
| 9 | feat(theme+a11y): brand.theme system + reduced-motion across 8 widgets | `c88257e` |
| 10 | feat(sources): real GitHub data integrations for cubes + heatmap | `8d114ad` |
| 11 | perf(svg): symbol/use dedup for heatmap cells + marquee loop | `f5f0f84` |
| 12 | feat(compose): cortex compose command stacks widgets into single SVG | `e913f5e` |
| 13 | release: v1.0.0 — action.yml polish for Marketplace publishing | `8217205` |
| 14 | fix(ci): rebase-and-retry auto-commit pushes to survive races | `14a0875` |

---

## Widget catalog (22 total)

### Tier-1 distinctive (added this development cycle)

| Widget | What it is | Key features |
|---|---|---|
| 🌅 **synthwave-banner** | 80s retro-futurist hero | Receding perspective grid, slatted neon sun, layered mountain silhouettes, 4 palettes (outrun, sunset, neon, miami) |
| 🌌 **skill-galaxy** | Constellation of skills as named stars | 3 backgrounds (deep-space, nebula, void), per-star twinkle, slow parallax drift, deterministic layout from name seed |
| 📡 **skill-radar** | Polar chart with translucent polygon | N axes, breathing scale animation, custom color, value 0..max |
| 🚇 **code-roadmap** | Metro/subway-style multi-line career map | Multiple colored lines along year axis, LIVE-pulsing marker on current station per line, optional legend |

### Tier-2 polished commons (added this cycle)

| Widget | What it is | Key features |
|---|---|---|
| 🟩 **activity-heatmap** | GitHub 7×52 contribution grid reimagined | Neon glow on bright cells, 4 palettes, sequential per-column reveal, falls back to deterministic mock if no real data |
| 🧊 **stat-cubes** | Isometric 3D blocks displaying numeric stats | 3 visible faces per cube (top label, front value, side dim), gentle orbit animation |
| 🏆 **achievement-wall** | Beveled trophy cabinet | Hexagonal mounted trophies with glyph + label + date, scale-breathing per trophy |

### Tier-3 / batch-3 (added this cycle)

| Widget | What it is | Key features |
|---|---|---|
| 🧬 **code-dna** | Twin spiral strands | Sinusoidal helix with colored base-pair rungs labelled by top languages, slow horizontal drift |
| 🌍 **skill-globe** | Stylized 2D globe with neon contribution pins | Lat/lon grid + rotation, pulsing pin rings, back-side pins auto-hidden |
| ✨ **particle-cloud** | Tag cloud orbiting a glowing core | Per-particle elliptical animateMotion paths, weight = inner+bigger, deterministic per-name |
| 🎵 **now-playing** | Spotify-style "currently coding in" card | Activity pill, language as track title, 32-bar animated waveform, progress bar with elapsed/duration |

### Earlier shipped widgets

| Widget | What it is |
|---|---|
| 🧠 **brain-anatomical** | 200+ Wikimedia anatomy paths recolored with multi-stop neon gradient |
| 🎴 **tech-cards** | Six glassmorphism skill panels in 3×2 grid |
| 📅 **yearly-highlights** | Career timeline with LIVE pulse on current year |
| 📺 **current-focus** | Netflix-style "now playing" tiles for active projects |
| 🎖️ **badges** | Compact skill strip — 4 shapes (pill/hex/shield/circle) × 3 layouts (row/grid/marquee) × 4 animations |
| 🌊 **header-banner / footer-banner** | Wide animated banners with shaped edges |
| ✨ **animated-divider** | Three layered sine waves drifting in counterpoint |
| 🐙 **github-icon** | Stylized small GH icon with halo |
| ⌨️ **about-typing / motto-typing** | Multilingual rotating typewriter headlines |

---

## System features

### `brand.theme` — coordinated palette system

Six named themes that propagate as default colors to every widget:

| Theme | Vibe | Slots |
|---|---|---|
| `outrun` (default) | Synthwave purple → pink → gold | primary `#7B5EAA` · secondary `#FF6B9D` · warm `#FFD23F` · cool `#22D3EE` · atmosphere `#0E0820` |
| `sunset` | Warm amber-pink, softer than outrun | primary `#FF6B9D` · secondary `#FFA940` · warm `#FFD23F` · cool `#7B5EAA` · atmosphere `#1A0633` |
| `midnight` | Deep blue/cyan, professional | primary `#3178C6` · secondary `#22D3EE` · warm `#7DD3FC` · cool `#1A1A48` · atmosphere `#0B0218` |
| `minimal` | Restrained two-tone | primary `#FFFFFF` · secondary `#A0A0A8` · warm `#D4D4D8` · cool `#71717A` · atmosphere `#18181B` |
| `cyberpunk` | High-contrast pink/cyan/yellow | primary `#F90001` · secondary `#22D3EE` · warm `#FFD23F` · cool `#7C3AED` · atmosphere `#000000` |
| `rose` | Pinks/violets matching brain body | primary `#C95E8A` · secondary `#FF6B9D` · warm `#F8C8DC` · cool `#7B5EAA` · atmosphere `#3A1A28` |

Wired into 8 builders: badges · radar · synthwave · galaxy · dna · globe · particles · now_playing. Per-widget explicit `color:` overrides still win — themes only set defaults.

### Reduced-motion accessibility

`@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }` injected into the `<style>` block of 8 themed builders. Honors the OS preference for CSS-driven animations (badges pulse, banner pulse, brain electric arcs). Per-widget animation toggles (`breathe: false`, `rotate: false`, `animation: static`) remain available for SMIL animations the CSS rule can't reach.

### Real GitHub data integrations

New `cortex.sources` package wraps `GitHubClient` with widget-shaped queries:

| Helper | Returns | Used by |
|---|---|---|
| `stats_cubes_from_github(client)` | 5 `StatCube` objects (PRs / commits / stars / repos / issues) with compact 8.4k / 1.2M formatting | `cubes.from_github=True` |
| `contribution_grid_from_github(client, weeks=52)` | 7×N intensity matrix (0..4) from real contribution calendar | `heatmap.from_github=True` |
| `top_languages_from_github(client, top_n=8)` | List of `{name, color, bytes}` aggregated across all public repos | reserved for galaxy/dna/badges follow-up |

All three degrade gracefully on missing token / API error — widgets always render. The query layer is fully tested without network access via monkeypatched GraphQL responses.

### `cortex compose` CLI

```bash
cortex compose -c examples/extreme.yml \
  -w synthwave-banner -w brain-anatomical -w badges \
  -w yearly-highlights -w footer-banner \
  -o assets/composite.svg
```

Stacks any subset of the 22 widgets into a single composite SVG. Each child SVG keeps its own viewBox; the parent nests them via `<svg x="0" y="<offset>" ...>` so the renderer treats each as an independent coordinate space — no path-rewriting needed. Composite outer viewBox = 1200 × sum(child heights) + gaps. `--list` flag prints available slugs.

---

## Performance pass

| Asset | Before | After | Delta | Technique |
|---|---|---|---|---|
| `activity-heatmap.svg` | 51,061 B | 44,834 B | **−12.2%** | `<symbol id="hm-cell">` + 364 `<use>` references for cells |
| `badges__shield-marquee.svg` | 23,098 B | 12,249 B | **−47.0%** | Render badge row once into `<g id="b-loop">`, `<use href="#b-loop">` for the seamless-loop duplicate |

Size budgets locked in by `test_perf_dedup.py`:
- heatmap < 50 KB
- marquee < 16 KB

---

## CI infrastructure

### Existing workflows (improved)

| Workflow | Cadence | What it does |
|---|---|---|
| `ci.yml` | every push to main, feature/**, fix/**, chore/**, every PR | Lint (ruff) + format check + mypy + pytest matrix (3.10/3.11/3.12) + CLI smoke + ajv JSON Schema validation + README link check |
| `build-examples.yml` | push to main | Re-renders `examples/rendered/extreme/*.svg` and auto-commits |
| `refresh-context.yml` | push to main | Refreshes `CONTEXT.md` auto-marker sections and auto-commits |

**Race fix (PR #14):** both auto-commit workflows now use a 3-attempt `git pull --rebase origin main && git push` loop with 3-second backoff between retries. Survives the case where two workflows fire on the same merge and race for the ref.

### New workflow — `health-check.yml` (PR #8)

Persistent (runs in GitHub Actions, survives across Claude sessions, no 7-day TTL):

| Job | Cadence | What it does |
|---|---|---|
| Daily build smoke | 07:17 UTC daily | `cortex build`, XML well-formedness, file-size delta vs committed baseline (>20% growth or >30% shrink flagged in job summary) |
| Weekly code-debt audit | 14:23 UTC Mondays | TODO/FIXME counts, skipped-test detection, total test count, largest builder LOC |
| Weekly community signal | 14:23 UTC Mondays | Star/fork/watcher counts, recent open issues, external-author PRs |

Outputs go to GitHub Actions job summaries — silent unless something fails.

### In-session schedules (auto-expire 2026-05-03)

Four cron jobs created during the session:

| Cadence | Job ID | Purpose |
|---|---|---|
| Daily 08:17 | `54579620` | Morning health check |
| Every 2 days 14:23 | `6a087991` | Build regression check |
| Every 3 days 11:08 | `897174bd` | Community signal sweep |
| Every 3 days 17:42 | `b2463564` | Code-debt audit |

These mirror what `health-check.yml` does, but run as in-session crons that report back conversationally. They auto-expire — the persistent workflow handles the same checks long-term.

---

## Schema additions

| Field | Type | Purpose |
|---|---|---|
| `brand.theme` | enum (6 values) | Coordinated palette propagation |
| `cards.synthwave` | `SynthwaveConfig` | Synthwave Horizon banner |
| `cards.galaxy` | `GalaxyConfig` (+ `StarSpec`) | Skill galaxy widget |
| `cards.radar` | `RadarConfig` (+ `RadarAxis`) | Skill radar widget |
| `cards.roadmap` | `RoadmapConfig` (+ `MetroLine`, `MetroStation`) | Code roadmap |
| `cards.heatmap` | `HeatmapConfig` | Activity heatmap |
| `cards.cubes` | `CubesConfig` (+ `StatCube`) | 3D stat cubes |
| `cards.trophies` | `TrophiesConfig` (+ `TrophySpec`) | Achievement wall |
| `cards.dna` | `DnaConfig` | Code DNA helix |
| `cards.globe` | `GlobeConfig` (+ `GlobePin`) | Skill globe |
| `cards.particles` | `ParticlesConfig` (+ `ParticleSpec`) | Particle cloud |
| `cards.now_playing` | `NowPlayingConfig` | Now-playing card |
| `cards.badges` | `BadgesConfig` (+ `BadgeItem`) | Skill badges |
| `cards.cubes.from_github` | `bool` | Auto-populate cubes from GitHub stats |
| `cards.heatmap.from_github` | `bool` | Pull real contribution calendar |

JSON Schema mirror in `packages/cortex-schema/schema.json` kept in sync. All 3 example YAMLs (minimal · standard · extreme) validate against the schema via ajv on every CI run.

---

## Test coverage

**164 tests passing** at v1.0.0 GA, organized as:

| File | Tests | Covers |
|---|---|---|
| `test_brain_helpers.py` | ~10 | brain seed, cell placement, arc network, lobe stroke overlay |
| `test_brain_integration.py` | ~5 | end-to-end brain SVG generation |
| `test_badges.py` | ~25 | icon library, monogram, shape paths, layout, end-to-end SVG content |
| `test_widget_batch_2.py` | 29 | 7-widget batch (synthwave, galaxy, radar, roadmap, heatmap, cubes, trophies) — empty fallbacks, label rendering, palette/animation toggles, deterministic seeding |
| `test_widget_batch_3.py` | 17 | 4-widget batch (dna, globe, particles, now-playing) — empty fallbacks, color overrides, hemisphere visibility, progress clamping |
| `test_themes.py` | 19 | every theme has 5 valid hex slots, REDUCED_MOTION_CSS injection, theme→primary fallback, explicit color overrides theme |
| `test_github_sources.py` | 28 | pure helpers (`_fmt_count`, `_intensity_for`), source functions with monkeypatched GraphQL, end-to-end builder integration |
| `test_perf_dedup.py` | 4 | size budgets locked in for heatmap + marquee |
| `test_compose.py` | 8 | widget registry, XML stripping, monotonic Y stacking, total height, size budget |

---

## Repo metadata

**Description:**
> Anatomically-accurate neon brain skill atlas for your GitHub profile README. Turns 30 lines of YAML into 10 animated SVG widgets that pulse with your real activity. Pure SVG + SMIL, no JS, no build step.

**Topics (18):** `github-action` · `github-profile` · `profile-readme` · `readme-generator` · `svg` · `animated-svg` · `smil` · `generative-art` · `neon` · `skill-atlas` · `developer-portfolio` · `brain-visualization` · `anatomical` · `python` · `pydantic` · `yaml` · `self-updating` · `showcase`

**Branding (action.yml):** icon `cpu` · color `purple`

---

## What's NOT done (deliberately or out-of-scope)

| Item | Why |
|---|---|
| **Marketplace web-UI publish** | Requires manual click on the v1.0.0 release page (Settings → Actions → "Publish to Marketplace"). All technical prerequisites are ready. |
| **Docs site** at `docs.cortex.dev` | Separate-repo work, needs Mintlify/Starlight setup decisions. Hero badge currently 404s. |
| **Web playground** | Separate hosting + WASM-Python-or-render-API decision. Weeks of work. |
| **More widgets** | 21 is past the point where surface area helps adoption. Per the "what next" advice, focus shifted to making existing widgets easier to use, not adding new ones. |
| **WakaTime integration** | Requires user API key, adds friction. Reserved for follow-up if there's user demand. |
| **`top_languages_from_github` wiring** | The source helper exists and is tested, but galaxy/dna/badges builders don't yet consume it. One follow-up PR. |
| **Node.js 20 deprecation** | `actions/checkout@v4` and `actions/setup-python@v5` flagged as deprecated. Force-upgrade default starts 2026-06-02. Bump within 30 days. |

---

## Files of interest

```
packages/
├── cortex-core/
│   └── cortex/
│       ├── __init__.py              # build_all() with 22 widgets
│       ├── schema.py                # All Pydantic configs
│       ├── themes.py                # 6 themes + REDUCED_MOTION_CSS
│       ├── compose.py               # Stack widgets into single SVG
│       ├── icons.py                 # 40+ tech-icon monograms
│       ├── markers.py               # CORTEX:SHOWCASE catalog (22 entries)
│       ├── github_api.py            # Thin REST + GraphQL client
│       ├── builders/
│       │   ├── brain.py             # Anatomical neon brain
│       │   ├── synthwave.py         # 80s retro hero
│       │   ├── galaxy.py            # Skill constellation
│       │   ├── radar.py             # Polar chart
│       │   ├── roadmap.py           # Metro map
│       │   ├── heatmap.py           # Contribution grid
│       │   ├── cubes.py             # Isometric stats
│       │   ├── trophies.py          # Trophy cabinet
│       │   ├── dna.py               # Twin helix
│       │   ├── globe.py             # 2D globe + pins
│       │   ├── particles.py         # Tag cloud
│       │   ├── now_playing.py       # Spotify card
│       │   ├── badges.py            # Skill strip
│       │   ├── tech_cards.py · timeline.py · focus.py
│       │   ├── typing.py · github_icon.py · divider.py · banner.py
│       └── sources/
│           ├── __init__.py
│           └── github.py            # Stats / contribution / languages
├── cortex-cli/
│   └── cortex_cli/
│       ├── __main__.py              # CLI entrypoint
│       └── commands/
│           ├── build.py · validate.py · init.py
│           ├── update_readme.py · viewer.py
│           └── compose.py           # NEW
└── cortex-schema/
    └── schema.json                  # JSON Schema mirror

.github/workflows/
├── ci.yml                           # Lint + test + smoke + schema
├── build-examples.yml               # Auto-render to examples/rendered/
├── refresh-context.yml              # Auto-update CONTEXT.md
└── health-check.yml                 # NEW — persistent monitoring

examples/
├── minimal.yml · standard.yml · extreme.yml
└── rendered/extreme/                # 21 main + 53 variant SVGs (auto-refreshed)

CHANGELOG.md                          # [1.0.0] release notes
action.yml                            # GitHub Action manifest
```

---

## Versions

- `cortex-core`: `0.2.1` → **`1.0.0`** (Production/Stable classifier)
- `cortex-cli` (PyPI: `cortex-profile`): `0.1.0` → **`1.0.0`**
- `cortex --version` reports `1.0.0`
- Git tag: `v1.0.0` published as a non-prerelease, non-draft GitHub release

---

## Install Cortex (post-v1)

```yaml
# .github/workflows/cortex.yml
name: Cortex Profile
on:
  schedule: [{cron: "0 6 * * *"}]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    permissions: { contents: write, pages: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: AbdullahBakir97/cortex@v1.0.0
        with:
          config: .github/cortex.yml
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

Configure widgets in `.github/cortex.yml`:

```yaml
brand:
  theme: outrun                    # outrun | sunset | midnight | minimal | cyberpunk | rose

cards:
  synthwave:                       # 80s hero banner
    enabled: true
    title: "Your Name"
  cubes:                           # Real GitHub stats
    enabled: true
    from_github: true
  heatmap:                         # Real contribution calendar
    enabled: true
    from_github: true
    palette: neon-rainbow
  radar:                           # Skill polar chart
    enabled: true
    axes:
      - { label: "Backend",  value: 90 }
      - { label: "Frontend", value: 70 }
      - { label: "DevOps",   value: 75 }
```

That's it. Backward-compatible with all v0.x configs; no breaking changes.
