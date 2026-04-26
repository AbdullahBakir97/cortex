# cortex-core

The SVG generators, GitHub API clients, and marker-rewriting engine that power
[Cortex](https://github.com/AbdullahBakir97/cortex).

This package is pure Python and is consumed by `cortex-cli` (the user-facing
command-line tool) and the `cortex` GitHub Action.

## Public API (subject to change in v0.x)

```python
from cortex import Config, build_all

config = Config.from_yaml(".github/cortex.yml")
build_all(config, output_dir="assets/")
```

```python
from cortex.builders import brain, typing, tech_cards
from cortex.markers import update_readme

brain.build(config, output="assets/brain-anatomical.svg")
typing.build_about(config, output="assets/about-typing.svg")
update_readme(config, readme_path="README.md")
```

## Builders included

| Builder | Output | Source data |
|---|---|---|
| `brain` | Anatomical neon brain SVG | Wikimedia (cached) + config palette |
| `tech_cards` | 6-card glassmorphism grid | Config + GraphQL stats |
| `timeline` | Yearly highlights career timeline | Config + commit history |
| `focus` | Current-focus dashboard | Config |
| `typing` | Cycling typing SVGs (about + motto) | Config |
| `github_icon` | Pulsing red-halo Octocat | Config palette |
| `divider` | Animated section divider | Config palette |

## Markers (auto-rewritten daily)

`ACTIVITY` · `LATEST_RELEASES` · `PAGESPEED` · `HIGHLIGHTS_STATS` · `SKYLINE_GRID` ·
`STL_LINKS` · `CITY_GRID` · `GITCITY_LINKS` · `QUOTE` · `GITGRAPH`

## License

MIT (see repo root). Brain anatomy source SVG is CC-BY-SA-3.0.
