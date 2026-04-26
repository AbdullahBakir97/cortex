# Changelog

All notable changes to Cortex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/AbdullahBakir97/cortex/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/AbdullahBakir97/cortex/releases/tag/v0.2.0
[0.1.0]: https://github.com/AbdullahBakir97/cortex/releases/tag/v0.1.0
