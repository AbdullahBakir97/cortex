# cortex-profile (CLI)

Command-line interface for [Cortex](https://github.com/AbdullahBakir97/cortex).

## Install

```bash
pip install cortex-profile
```

## Commands

```bash
cortex init              # scaffold a starter cortex.yml in the current repo
cortex validate          # check your cortex.yml against the schema
cortex build             # render every enabled SVG to assets/
cortex update-readme     # rewrite README marker blocks (ACTIVITY, QUOTE, etc.)
cortex viewer            # build the Three.js 3D viewer for /docs publishing
cortex --help            # full help text
```

## Quickstart

```bash
# 1. Scaffold a starter config:
cortex init --template full-stack

# 2. Edit .github/cortex.yml to taste

# 3. Validate:
cortex validate

# 4. Build everything:
cortex build --output assets/
cortex update-readme --readme README.md

# 5. (Optional) build the 3D viewer:
cortex viewer --output docs/
```

## CI usage

In a GitHub Actions workflow you don't usually call the CLI directly — use the
[Cortex composite Action](https://github.com/AbdullahBakir97/cortex#installation-30-seconds)
which wraps everything in three steps. The CLI is for local iteration and
power users who want fine-grained control.

## License

MIT.
