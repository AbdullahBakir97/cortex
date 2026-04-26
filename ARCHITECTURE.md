# Cortex — Architecture

> **What this is**: the reference architecture for the `cortex` repo. Every piece in the current `Abdullah-Readme/src` repo gets a clean home here, plus the new infrastructure (CLI, schema validation, Pages viewer packaging) needed to ship as a distributable product.

---

## 1. Repo layout

```
cortex/                                    # ← new public repo, MIT-licensed (CC-BY-SA-3.0 for brain anatomy only)
│
├── action.yml                             # GitHub composite Action entry point
├── package.json                           # npm workspace root
├── pnpm-workspace.yaml                    # monorepo orchestration
├── pyproject.toml                         # Python deps shared across packages
├── LICENSE                                # MIT
├── LICENSES/                              # third-party license texts
│   └── BRAIN-ANATOMY-CC-BY-SA-3.0.txt    # Wikimedia attribution
├── README.md                              # Marketing page (the launch hero)
├── CHANGELOG.md                           # Keep-a-Changelog format
│
├── packages/                              # ← monorepo packages
│   ├── cortex-core/                       # Python — SVG generators
│   │   ├── pyproject.toml
│   │   ├── cortex/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py                  # YAML → typed Config
│   │   │   ├── builders/
│   │   │   │   ├── brain.py               # build_anatomical_brain.py from current repo
│   │   │   │   ├── tech_cards.py
│   │   │   │   ├── timeline.py            # yearly-highlights
│   │   │   │   ├── focus.py               # current-focus
│   │   │   │   ├── typing.py              # build_typing_svgs.py
│   │   │   │   ├── github_icon.py
│   │   │   │   └── divider.py
│   │   │   ├── markers.py                 # update_readme.py — marker rewriter
│   │   │   ├── github_api.py              # GraphQL + REST clients
│   │   │   ├── palettes.py                # named palettes (neon-rainbow, mono…)
│   │   │   └── templates/                 # Jinja2 SVG templates
│   │   └── tests/
│   │
│   ├── cortex-cli/                        # Python CLI wrapper
│   │   ├── pyproject.toml
│   │   └── cortex_cli/
│   │       ├── __main__.py                # `cortex build|validate|viewer|preview`
│   │       └── commands/
│   │
│   ├── cortex-3d/                         # JavaScript — Three.js viewer template
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── src/
│   │   │   ├── main.ts                    # docs/index.html from current repo
│   │   │   ├── scene.ts
│   │   │   ├── controls.ts
│   │   │   └── styles.css
│   │   └── dist/                          # built static site copied to user's /docs
│   │
│   └── cortex-schema/                     # JSON Schema for cortex.yml (powers IDE autocomplete)
│       ├── schema.json
│       └── README.md                      # how to use with VS Code YAML extension
│
├── apps/                                  # standalone deployments
│   ├── docs/                              # Mintlify documentation site
│   │   └── docs.json
│   └── dashboard/                         # Next.js SaaS (Pro tier — Phase 4+)
│       └── (placeholder until Phase 4)
│
├── examples/                              # sample cortex.yml configs
│   ├── minimal.yml                        # 2-minute setup
│   ├── standard.yml                       # default template
│   ├── extreme.yml                        # everything on (Abdullah's reference)
│   └── README.md                          # gallery of resulting profile screenshots
│
├── templates/                             # `cortex init` starter packs by archetype
│   ├── backend-engineer/
│   ├── full-stack/
│   ├── frontend-specialist/
│   ├── data-scientist/
│   ├── devops/
│   └── student/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                         # lint + typecheck + tests on PR
│   │   ├── release.yml                    # tag → npm publish + marketplace
│   │   ├── e2e.yml                        # nightly: run Action against test profile, diff result
│   │   └── docs-deploy.yml                # apps/docs → docs.cortex.dev
│   └── ISSUE_TEMPLATE/
│       ├── bug.yml
│       ├── feature.yml
│       └── showcase.yml                   # users submit their Cortex profiles
│
└── scripts/
    ├── release.py                         # bump version + tag + push
    ├── benchmark.py                       # measure build time per config
    └── update_brain_anatomy.py            # refresh Wikimedia source on demand
```

---

## 2. Data flow (one Action run)

```
   ┌────────────────────────┐
   │ user's profile repo    │
   │ .github/cortex.yml     │ ← user authors
   │ .github/workflows/...  │ ← uses: AbdullahBakir97/cortex@v1
   └──────────┬─────────────┘
              │  cron / workflow_dispatch
              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ Cortex Action (action.yml composite)                         │
   │                                                              │
   │   1. setup-python + pip install cortex-profile               │
   │   2. cortex validate <config>      ← schema check            │
   │   3. cortex build <config>         ← writes to assets/       │
   │       ├─ Fetch GitHub data (GraphQL + REST)                  │
   │       ├─ Builder: brain.py        → assets/brain.svg         │
   │       ├─ Builder: tech_cards.py   → assets/tech-cards.svg    │
   │       ├─ Builder: timeline.py     → assets/yearly-highlights.svg
   │       ├─ Builder: focus.py        → assets/current-focus.svg │
   │       ├─ Builder: typing.py       → assets/about-typing.svg  │
   │       └─ Builder: typing.py       → assets/motto-typing.svg  │
   │   4. cortex update-readme <config> ← rewrites markers        │
   │       └─ ACTIVITY, RELEASES, QUOTE, GITGRAPH, SKYLINE_GRID…  │
   │   5. cortex viewer <config>       → docs/                    │
   │       └─ Templates @cortex/3d build → static HTML+JS         │
   │   6. configure-pages → upload-pages-artifact → deploy-pages  │
   │   7. git commit -am "chore(cortex): refresh profile" + push  │
   └──────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌──────────────────────────┐    ┌─────────────────────────────┐
   │ user's profile repo      │    │ user's GitHub Pages         │
   │ ├─ assets/*.svg (refresh)│    │ brain.user.dev (3D viewer)  │
   │ ├─ README.md  (markers)  │    │ (or username.github.io)     │
   │ └─ docs/       (viewer)  │    └─────────────────────────────┘
   └──────────────────────────┘
```

---

## 3. Package responsibilities

| Package | Language | Owns | Depended-on by |
|---|---|---|---|
| **`cortex-core`** | Python | All SVG generation, marker rewriting, GitHub API clients, palettes | `cortex-cli` |
| **`cortex-cli`** | Python | `cortex build/validate/viewer/init` commands | `action.yml` |
| **`cortex-3d`** | TypeScript / Vite | Three.js viewer source; built into static HTML for any user's `/docs` | `cortex-cli viewer` command |
| **`cortex-schema`** | JSON | `cortex.yml` JSON Schema for IDE autocomplete + validation | `cortex-cli validate` |

---

## 4. External dependencies (kept minimal)

**Runtime (shipped to users)**
- Python 3.10+ (Action runner provides it)
- `requests` (HTTP)
- `PyYAML` (config parsing)
- `Jinja2` (SVG templates)
- `pillow` (only if user enables AI-portrait feature)

**Dev-time (us)**
- `pnpm` for monorepo orchestration
- `vite` for the 3D viewer build
- `pytest` + `mypy` + `ruff` for Python QA
- `vitest` + `tsc` for TS QA
- `mintlify` for docs

**Third-party services (optional, gated by user secrets)**
- WakaTime API
- Google PageSpeed Insights API
- (Pro tier) OpenAI / Anthropic for AI portrait + digital twin

---

## 5. Naming conventions

- **Files**: `snake_case.py`, `kebab-case.ts`, `kebab-case.svg`
- **Public Python API**: `cortex.builders.brain.build()`, never internal `_helpers`
- **CLI commands**: verbs only — `cortex build`, never `cortex builder`
- **SVG asset paths**: `assets/<widget-name>.svg` — never include the user's name in the filename (path is the namespace)
- **Marker comments**: `<!-- CORTEX:WIDGET_NAME:START -->` — namespaced under `CORTEX:` so we never collide with user-written markers

---

## 6. Versioning

- **Semver** on the public Python package (`cortex-profile`)
- **Major.minor tag** on the Action (`@v1`, `@v1.2`) — users pin to `@v1` for auto-updates within v1 line
- **Schema versioning** in `cortex.yml`: top-level `version: 1` field; `cortex validate` rejects mismatches with helpful migration hints

---

## 7. Caching strategy

- **Wikimedia brain SVG** → cached in repo at `packages/cortex-core/cortex/assets/brain-source.svg`. Refresh via `scripts/update_brain_anatomy.py` (manual). User's Action run never hits Wikimedia.
- **GitHub API** → leverage `etag` headers + 1h TTL filesystem cache in `~/.cache/cortex/`
- **Built SVGs** → only re-render when (a) config changed or (b) source data changed (GitHub stats hash)

---

## 8. Security model

- **No code execution from cortex.yml** — strictly declarative; YAML never evaluated
- **No external network in builders** except whitelisted hosts (api.github.com, upload.wikimedia.org, optional opt-in services)
- **No telemetry** in the Free tier. Pro tier opt-in via `analytics: true`
- **Secrets** only via GitHub Action `inputs:` — never logged, never written to commits
- **Pin all dependencies** with hashes in `pyproject.toml` lock files
