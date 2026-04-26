# Cortex — Vision & Strategy

> The longform "where this project is going and why" doc. Decays slowly; revisit when phase boundaries change. Companion to [`CONTEXT.md`](./CONTEXT.md) (which is "where it is right now" and decays fast).

---

## Vision in one sentence
Cortex is the **first** GitHub-profile-README generator that produces something a developer would print and frame — not "a cleaner stats card", but a coordinated cinematic portrait built from a single YAML file.

## What "winning" looks like
- 5,000+ stars within 12 months of v1.0
- Top-3 result on `awesome-github-profile-readme` lists
- Featured in at least one of: GitHub Blog, JetBrains Day, FreeCodeCamp, Hacker News front page
- 50+ user-submitted showcase profiles linked from `examples/README.md`
- One-click "deploy your profile" from `app.cortex.dev` with no YAML editing required
- Cited as a reference for "what a developer profile can be" in dev-twitter discourse

---

## Why this is winnable (competitive landscape)

The profile-README ecosystem is mature on the *data* side and immature on the *art* side. We're not building another stats card.

| Competitor | Stars | Approach | Where Cortex beats it |
|---|---|---|---|
| `lowlighter/metrics` | 14k★ | Server-rendered SVG with many plugins, query-string-configured | We're **brain-shaped, not metric-shaped**. Visual identity, not a chart density race. |
| `anuraghazra/github-readme-stats` | 73k★ | One card per stat, plug-and-play | They make stats; we make a **portrait**. Cortex composes a coordinated set with shared visual language. |
| `yoshi389111/github-profile-3d-contrib` | 1.4k★ | One thing well — a 3D contribution skyline | We embed it AND build the rest of the README around it. Cortex is the conductor; they're a section. |
| `kyechan99/capsule-render` | 3k★ | Animated SVG header/footer banners | We use it today; v0.3+ ships our own `cortex banner` so we own the brand top-to-bottom. |
| `DenverCoder1/readme-typing-svg` | 6k★ | Animated typing SVG | Cortex's typing widget handles **30+ multilingual lines per language** in 10+ scripts; theirs handles ~3 ASCII lines. |
| `ashutosh00710/github-readme-activity-graph` | 2k★ | Activity graph as a card | We integrate the graph as one of ten widgets, not the headline. |

**Strategic read**: visual quality is the moat. Tools that ship cinematic motion go viral. Tools that ship more configuration knobs plateau.

---

## Trends to ride (2025–2026)

1. **Generative aesthetics** — neon, brutalist, glassmorphism, particle systems. The bar for "developer portfolio" has risen sharply since 2023; SVG art is now expected, not exceptional.
2. **3D-in-2D illusions** — wobble, parallax, isometric tricks that *suggest* depth without WebGL. Cortex's brain already does SMIL transforms here; we should push further (parallax leader lines, ambient particle drift, lobe shimmer).
3. **AI-augmented profiles** — "AI-generated portrait", "digital twin chatbot", "skill DNA from commit history" are the breakout hooks. Already in our roadmap.
4. **Multilingual identity** — Arabic, Chinese, Japanese support is rare in profile tools and a major differentiator for global devs. We already lead here.
5. **Live data over static** — GitHub stats / WakaTime / recent activity / PageSpeed scores as auto-refreshing markers. Already in `markers.py`.
6. **One-click setup** — friction kills adoption. Phase B.3 web playground addresses this.
7. **Brand-as-product for individuals** — devs treat their profile READMEs like personal sites. Tools that lean into "designed product, not toy" win.

---

## Go-viral strategy (what we ship to make this happen)

The shareable moments — each one is a feature decision:

| Moment | Feature it requires |
|---|---|
| **Hero screenshot on Twitter/X** | Brain SVG works at 600×400 thumbnail crop without losing identity. (Pass current font-scale work has us close.) |
| **Time-lapse setup video** | `cortex init` → first build → README populated should fit cleanly in a 30-second screencap. (Already true; we just need to record it.) |
| **"Built with Cortex" footer** | Auto-injected linkback in every generated README. **Network effect.** Easy to build (footer marker section). |
| **Weekly showcase** | Curated profile of the week pinned in README + GitHub Discussions. **Manual but high-leverage.** |
| **Show HN / Product Hunt launch** | Coordinated v1.0 ship: polished hero, 30-sec demo video, 10 example profiles, blog post on the brain anatomy story (Wikimedia → neon). |
| **"Holy s*** that's a brain" reaction** | Brain atmosphere upgrade — particle system, depth, ambient motion. Currently flat-ish; needs Phase C work. |

---

## Phase roadmap (concrete, sequenced)

### Done
- **v0.1.0** — Initial alpha (action.yml + builders ported from Abdullah-Readme repo)
- **v0.2.0** — Full core widget set (typing, tech_cards, timeline, focus, divider, github_icon)
- **v0.2.1** — Marker rewriter (10 sections: ACTIVITY · LATEST_RELEASES · QUOTE · GITGRAPH · PAGESPEED · WAKATIME · SKYLINE_GRID · CITY_GRID · STL_LINKS · GITCITY_LINKS · HIGHLIGHTS_STATS)
- **Phase A** (apr 2026) — Marketing README backed by live-rendered SVGs + auto-render workflow + font scale-up for legibility

### In flight (current sprint)
- **Widget polish pass** — leader-line tracking, atmosphere, current-focus + yearly-highlights readability

### Phase B — Multi-modal customization
The thesis: a single user should be able to customize through whichever surface fits their context — YAML for power users, web UI for everyone, README directives for one-off tweaks. All three converge to the same canonical YAML.

- **B.1 — Theming surface** (foundation; no visible behavior change)
  - Extend `BrainColors` from 4 accents to a full per-widget palette (lobe colors, card stroke, glow intensity)
  - Add per-widget `animation: { speed, easing, intensity }` knobs
  - Add `typography: { display, mono, scale }` knob — a single multiplier that scales every font proportionally so users on smaller READMEs (e.g. embedded in a wider org page) can opt down
  - Add per-widget `layout: { padding, gutter, density: compact|standard|spacious }`
  - Both Pydantic + JSON Schema additions; CI validates examples against both
- **B.2 — Inline README directives** (~1 evening)
  - `<!-- CORTEX:STYLE: palette=cyberpunk; animation=intense -->` parsed by `markers.py` immediately before any widget marker
  - Precedence: directive > YAML > palette default > built-in default
  - Limited keyset (~10 props); strict failure on unknown keys
- **B.3 — Web playground** (`apps/dashboard/`, ~1–2 weeks)
  - Next.js 16 App Router, deployed to `app.cortex.dev` (Vercel)
  - Form bound to JSON Schema (`react-jsonschema-form` or hand-rolled)
  - Live SVG preview using either: (a) Pyodide-compiled Python builders running in the browser, or (b) a server-side build endpoint
  - "Copy YAML" button that emits the canonical `cortex.yml` to paste into the user's repo
  - Optional: GitHub OAuth + auto-PR to user's profile repo (deferred to v2.1)

### Phase C — Atmosphere & viral hooks
- **C.1 — `cortex banner`** — own animated header/footer SVG generator. Drops the capsule-render dep; matches our brand end-to-end.
- **C.2 — Brain ambient layer** — particle drift behind the brain, ambient gradient pulse, depth shading. This is the "holy s*** that's a brain" reaction trigger.
- **C.3 — Leader-line tracking** — leader lines from lobe cards to brain anatomy targets follow the brain's `brain-3d` SMIL wobble. Today they're static while the brain moves; the disconnect is jarring on close inspection.
- **C.4 — Brain heatmap** — lobes glow brighter where the user actually contributes (cross-reference GitHub activity per topic/repo against region domain). Listed in the existing roadmap as v1.1.
- **C.5 — Skill DNA strand** — helix that traces tech-stack progression year-over-year. Listed as v1.2.
- **C.6 — Project trading cards** — Pokemon-style holographic SVG per pinned repo. Listed as v1.3.

### Phase D — Mind-blowing (post-v1.0 differentiators)
- **D.1 — Time-lapse brain** — animated 2018→today rendered as a 30-second video (FFmpeg in CI). Listed as v1.4.
- **D.2 — AI portrait** — turn commit history into a generated portrait via Claude/OpenAI. Listed as v2.1.
- **D.3 — Digital twin chatbot** — visitors ask "what does X work on?" and the README answers via embedded MCP server. Listed as v2.2.
- **D.4 — Constellation viewer** — contribution graph reimagined as a star map.
- **D.5 — Sound-reactive brain** — ambient audio sync. Gimmicky, but the kind of thing that wins demos.

### v1.0 stability gate
- All Phase B done, Phase C polished, PyPI publication automated, Marketplace listing live, `docs.cortex.dev` complete on Mintlify, 10+ showcase profiles linked, Show HN draft ready.

---

## Quality bar (non-negotiable for everything we ship)
- Every widget readable at GitHub README scale (≥13px effective screen size after the ~0.55× downscale)
- Every animation is CSS or SMIL — **never JS** (github strips `<script>` from rendered SVGs)
- Every example yml validates against both Pydantic *and* JSON Schema (CI gate)
- Every push runs `ruff check`, `ruff format --check`, ajv schema validation, and re-renders the showcase
- Every commit message uses Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `style:`, `refactor:`)
- **No `Co-Authored-By` trailers**, no "Generated with Claude Code" footers — all commits authored solely by the human contributor
- Every external dependency pinned in lockfiles
- No telemetry without explicit opt-in (`pro.analytics: true`)
- Every new widget ships with: a Pydantic schema entry, a JSON Schema mirror entry, an example in `extreme.yml`, a rendered example in `examples/rendered/extreme/`, and a README `<details>` showcase block

---

## Decision log (when we change direction, write it here)
- **2026-04-26** — Adopted two-file context model: `CONTEXT.md` (auto-friendly, current state) + `VISION.md` (manual, strategy). Reason: mixing decays both; separating lets each evolve at its natural cadence.
- **2026-04-26** — Locked in "no Claude attribution" globally via `~/.claude/settings.json` after a Co-Authored-By trailer accidentally surfaced "Claude" as a repo contributor.
- **2026-04-26** — Font sizes in builders calibrated for the ~0.55× README downscale rather than 1:1 viewing. All future widgets must follow.
- **2026-04-26** — Pre-rendered showcase SVGs committed to `examples/rendered/extreme/`. Auto-refreshed by `.github/workflows/build-examples.yml`. README embeds these via raw GitHub URLs at `width="100%"`.
