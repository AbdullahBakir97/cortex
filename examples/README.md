# Cortex Examples

Pre-baked configurations for common archetypes. Pick the one closest to your
profile, copy it to `.github/cortex.yml`, edit identity fields, push.

| File | Lines | Use when |
|---|---|---|
| [`minimal.yml`](./minimal.yml) | ~25 | You want a quick win — brain + 1 card, English only |
| [`standard.yml`](./standard.yml) | ~60 | The default. Brain + 3 cards + 30-line typing in 1 language |
| [`extreme.yml`](./extreme.yml) | ~120 | Everything on. The reference profile [@AbdullahBakir97](https://github.com/AbdullahBakir97) |

## Quickstart

```bash
# Pick one and drop it into your profile repo:
curl -fsSL https://raw.githubusercontent.com/AbdullahBakir97/cortex/main/examples/standard.yml \
  -o .github/cortex.yml

# Edit identity:
$EDITOR .github/cortex.yml

# Validate:
cortex validate

# Build:
cortex build
```
