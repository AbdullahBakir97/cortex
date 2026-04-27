# Changelog

All notable changes to Cortex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-04-27

First production release. Cortex ships 22 widget builders, 180+ tests, a coordinated theme system, real GitHub data integrations, and the `cortex compose` command for one-image profile setups.

### Added — widgets (22 total)
- 🧠 **brain-anatomical** — anatomically-accurate neon brain, 200+ Wikimedia paths
- 🌅 **synthwave-banner** — 80s retro-futurist hero (4 palettes)
- 🌌 **skill-galaxy** — constellation of skills as named stars (3 backgrounds)
- 📡 **skill-radar** — polar chart with translucent breathing polygon
- 🚇 **code-roadmap** — metro/subway-style multi-line career map
- 🟩 **activity-heatmap** — 7×52 contribution grid with neon glow (4 palettes)
- 🧊 **stat-cubes** — isometric 3D blocks with label/value faces
- 🏆 **achievement-wall** — beveled trophy cabinet with hex medallions
- 🧬 **code-dna** — twin spiral strands with language base-pair rungs
- 🌍 **skill-globe** — stylized 2D globe with neon contribution pins
- ✨ **particle-cloud** — labelled particles orbiting a glowing core
- 🎵 **now-playing** — Spotify-style "currently coding in" card
- 🎖️ **badges** — compact skill strip (4 shapes × 3 layouts × 4 animations)
- Plus original suite: tech-cards, current-focus, yearly-highlights, header-banner, footer-banner, animated-divider, github-icon, about-typing, motto-typing

### Added — system features
- **`brand.theme`** (outrun · sunset · midnight · minimal · cyberpunk · rose) — propagates as default colors to every widget. One line changes the whole palette.
- **Reduced-motion accessibility** — `@media (prefers-reduced-motion: reduce)` opt-out injected into 8 builders.
- **Real GitHub data integrations** — `cubes.from_github` and `heatmap.from_github` flags pull live stats / contribution calendar via the GraphQL API. Graceful fallback on missing token or API error.
- **`cortex compose`** CLI — stack any subset of the 22 widgets into a single composite SVG.
- **`cortex.sources` package** — pure-data helpers for auto-population (`stats_cubes_from_github`, `contribution_grid_from_github`, `top_languages_from_github`).

### Performance
- Heatmap SVG: 51KB → 45KB (–12%) via `<symbol>` / `<use>` cell dedup.
- Badges marquee: 23KB → 12KB (–47%) via `<g id>` / `<use>` loop dedup.

### CI
- New `health-check.yml` — daily build smoke + size-delta tracking, Monday code-debt audit + community signal sweep.
- CI matrix: Python 3.10 / 3.11 / 3.12, ruff lint + format, pytest, ajv JSON Schema validation, README link check.

### Breaking changes
- None. Fully backward-compatible with v0.x widget configs.

## [Unreleased]

### Added — Phase B.1 theming surface (foundation for inline directives + web playground)
- **`brain.typography.scale`** — global font-size multiplier (0.5-1.5,
  default 1.0). Useful for users embedding Cortex in narrower contexts
  or with smaller READMEs. Schema-only for now; builders wire it in
  follow-up commits.
- **`brain.animations.speed`** — global animation duration multiplier
  (0.25-4.0, default 1.0). >1.0 slows everything down; useful for
  reduced-motion accessibility preferences.
- **`brain.atmosphere`** — sub-model with four bool toggles for the
  visual layers added in the brain atmosphere pass:
  - `show_particles` (default true) — 16 ambient drifting particles
  - `show_aura` (default true) — pink/purple radial glow center-canvas
  - `show_halos` (default true) — static rings at leader-line endpoints
  - `wobble` (default true) — 3D scaleX/skewY breathing on brain anatomy
- All four flags wired into `cortex/builders/brain.py` via conditional
  template fragments — disabling all four trims the rendered SVG by
  ~2.3 KB and removes all atmosphere-related animations. Backward
  compatible: existing configs without these fields render identically
  to before via Pydantic defaults.

### Added — widget readability sweep
- **`cortex/builders/timeline.py`** — yearly-highlights fonts scaled
  for the ~0.55x README downscale (display 30->36, headline 22->26,
  bullet body 11.5->15, etc.). Card height 360->460 + svg_h 660->760
  + per-card y-positions re-spaced.
- **`cortex/builders/focus.py`** — current-focus fonts scaled the same
  way (title 19->24, desc 12.5->16, status 9->12, pill 10->13). Tile
  dimensions 420x220 -> 460x280 with re-spaced internal positions.
- **`cortex/builders/brain.py`** — five atmosphere upgrades shipped
  as part of the polish pass: glassmorphism cards (top stripe + highlight
  overlay matching tech-cards), background pulse (bgRadial r animation),
  bgAura radial-gradient overlay, 16 ambient particles, spark dots
  moved INSIDE brain-3d transform group so they wobble with the brain,
  static halo rings in canvas space anchoring the leader-line endpoints.

### Added — operational infrastructure
- **`CONTEXT.md`** at the repo root — single source of truth for current
  project state. Designed to be read first when resuming work; replaces
  the need to scan 30 source files. Manual sections (code map, active
  work, design decisions) + auto-marker sections (recent commits)
  regenerated by `scripts/refresh_context.py` on every push.
- **`VISION.md`** at the repo root — longform "where this is going" doc.
  Competitive landscape, trends to ride, go-viral strategy, phase
  roadmap (B/C/D), quality bar, decision log. Companion to CONTEXT.md
  (which decays fast); VISION decays slowly.
- **`scripts/refresh_context.py`** — regenerates auto-marker sections in
  CONTEXT.md by reading git log. Forces UTF-8 decoding so commit messages
  with non-ASCII characters survive Windows-default-codepage subprocess.
- **`.github/workflows/refresh-context.yml`** — runs the refresh script
  on every push to main, commits the diff back as `cortex-bot[bot]` with
  `[skip ci]` to avoid loops. Concurrency-grouped to prevent races.

### Added — widget showcase
- **`examples/rendered/extreme/`** — pre-generated SVG showcase committed to
  the repo so the marketing README can embed real, current widget output
  instead of placeholder/missing screenshots.
- **`.github/workflows/build-examples.yml`** — auto-renders the extreme tier
  whenever `packages/cortex-{core,cli}/**` or `examples/*.yml` changes on
  main, then commits the refreshed SVGs back as `cortex-bot[bot]`. Marked
  `[skip ci]` to avoid loops; concurrency-grouped to avoid mid-commit races.

### Changed
- **README.md** — replaced the broken `hero-demo.gif` reference with the
  live `brain-anatomical.svg`. Added a "What this generates" section with
  collapsible `<details>` blocks for all 8 widgets, each backed by the real
  output from `examples/extreme.yml`. Fixed a `<ivmg>` typo in the badges
  row that was rendering as plain text.

### Architectural decisions (locked in for v1)
- **Composite GitHub Action** (not Docker) — chosen for cold-start speed (~5 s vs ~60 s).
- **YAML config** (not TOML) — matches the format GitHub Actions users already write.
- **Wikimedia brain anatomy is checked into the repo** at
  `packages/cortex-core/cortex/assets/brain-source.svg`. User Action runs never depend
  on Wikimedia uptime. Refresh manually via `python scripts/update_brain_anatomy.py`.
- **Python for builders, TypeScript for the 3D viewer** — Three.js is JS-native and
  Python has the cleaner SVG generation story.
- **Schema versioning baked in from day one** — every `cortex.yml` has a top-level
  `version: 1` field; mismatches raise a helpful migration error rather than a
  cryptic crash.

## [0.2.1] — 2026-04-26 (alpha — markers + decorative bits)

### Added
- **`cortex.markers`** — daily README rewriter, ported from
  `scripts/update_readme.py`. Ten sections registered:
  QUOTE / ACTIVITY / GITGRAPH / SKYLINE_GRID / CITY_GRID / STL_LINKS /
  GITCITY_LINKS (token-free) +
  LATEST_RELEASES / HIGHLIGHTS_STATS / PAGESPEED (token-required).
- **`cortex.github_api`** — thin REST + GraphQL client; anonymous mode
  supported for token-free sections; GraphQL raises a helpful error
  rather than 401-ing on missing token.
- **`cortex.builders.github_icon`** — pulsing brand-glow Octocat halo.
- **`cortex.builders.divider`** — animated section divider with the
  brand color sweeping across.
- `cortex update-readme` CLI command now wired to `cortex.markers.update`
  with per-section status reporting (updated / missing / skipped /
  failed) and precise skip reasons.

### Schema additions
- `auto_update.markers` gains five new bool flags
  (`highlights_stats`, `skyline_grid`, `city_grid`, `stl_links`,
  `gitcity_links`) and the existing nested PageSpeedConfig is now
  dispatched correctly via `getattr(attr, "enabled", attr)`.

### Verified
- 8 widgets emit clean XML end-to-end (`cortex build` ~41 ms).
- 5 token-free marker sections rewrite a synthetic README correctly with
  no GitHub token set; PAGESPEED reports a single graceful failure when
  rate-limited; LATEST_RELEASES + HIGHLIGHTS_STATS report precise skip
  reasons.

## [0.2.0] — 2026-04-26 (alpha — full core widget set)

### Added
- **`cortex.builders.typing`** — about & motto cycling SVGs
  (30 generic + 20 personal lines each, with `{github_user}` / `{primary_project}`
  / `{location}` placeholder substitution; SMIL keyTimes math: 12% type / 62% hold
  / 10% erase / 16% off per line).
- **`cortex.builders.tech_cards`** — 3×2 glassmorphism skill cards driven by
  `brain.regions`. Domain-keyed presets fill any blank visual fields so the
  simple case still looks polished. Mastery levels (EXPERT/ADVANCED/PROFICIENT/
  GROWING) drive proficiency-bar widths.
- **`cortex.builders.timeline`** — auto-extending career timeline with N year
  cards, breathing borders, and a pulsing LIVE badge on the current calendar
  year (auto-detected from `datetime.date.today()` — no Jan 1 config edit
  needed).
- **`cortex.builders.focus`** — Netflix-style "now playing" tile dashboard
  with status pills, accent stripes, descriptions (greedy word-wrapped to
  ≤3 lines), and tech pills (auto-sized by label width).

### Schema additions
- `BrainRegion` gains optional `emoji`, `caption`, `tagline`, `mastery`, `stats`.
- `cards.yearly_highlights` gains optional `years: list[YearEntry]` (max 6).
- `FocusTile` gains optional `emoji`, `description`, `tech` (max 4 pills).
- `examples/extreme.yml` extended with rich data demonstrating every new field.

### Changed
- `cortex.builders.brain` no longer carries the v0.1 stub-mate label.
- CLI: "(not implemented in v0.1)" → "(builder not on disk yet)" — the version
  pin was misleading once we shipped builders incrementally.

### Verified
- All 6 widgets emit valid XML end-to-end via `cortex build` against
  `examples/extreme.yml` (~70 ms total wall clock).

## [0.1.0] — TBD (initial alpha, not yet released)

### Added
- Composite Action `action.yml` at repo root.
- `packages/cortex-core` — Python builders ported from
  [@AbdullahBakir97/AbdullahBakir97](https://github.com/AbdullahBakir97/AbdullahBakir97):
  - Anatomical neon brain (Wikimedia source recolored)
  - Tech-stack glassmorphism cards
  - Yearly highlights career timeline
  - Current focus dashboard
  - Multi-color cycling typing SVGs (about + motto)
  - Custom GitHub icon with pulsing halo
  - Animated section divider
- `packages/cortex-cli` — `cortex build`, `cortex validate`, `cortex init` commands.
- `packages/cortex-schema` — JSON Schema for `cortex.yml` (powers IDE autocomplete).
- `packages/cortex-3d` — Three.js + OrbitControls viewer template (Vite project).
- Daily marker auto-refresh: ACTIVITY · LATEST_RELEASES · QUOTE · GITGRAPH ·
  PAGESPEED · WAKATIME · SKYLINE_GRID · CITY_GRID · STL_LINKS · GITCITY_LINKS.
- `examples/{minimal,standard,extreme}.yml` configs.
- `templates/` directory with archetype starter packs.
- Brain anatomy attribution at `LICENSES/BRAIN-ANATOMY-CC-BY-SA-3.0.txt`.

[Unreleased]: https://github.com/AbdullahBakir97/cortex/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/AbdullahBakir97/cortex/releases/tag/v0.2.1
[0.2.0]: https://github.com/AbdullahBakir97/cortex/releases/tag/v0.2.0
[0.1.0]: https://github.com/AbdullahBakir97/cortex/releases/tag/v0.1.0
