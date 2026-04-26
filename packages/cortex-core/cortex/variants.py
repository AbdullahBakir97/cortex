"""Variant renderer — builds one SVG per showcase-catalog recipe.

The showcase block in the README references ``assets/variants/<base>__<slug>.svg``
for each recipe. This module produces those SVGs by:

  1. Parsing each variant's yaml snippet
  2. Deep-merging it into the user's base config (so identity, palette, etc.
     come from the user; only the variant-specific keys override)
  3. Calling the appropriate builder with the merged config and a unique
     filename like ``header-banner__wave-drift.svg``

Disabled variants (``enabled: false``) are skipped — no SVG output, but the
showcase markdown still lists the recipe so users see the config snippet.

Run from the CLI via ``cortex build`` (variants render alongside the main
SVGs) or programmatically via ``cortex.variants.build_variants(config, ...)``.
"""

from __future__ import annotations

import importlib
from copy import deepcopy
from pathlib import Path

import yaml as _yaml

from .schema import Config


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursive dict merge — override wins for leaf values, dicts merge in place."""
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_variant(base_config: Config, variant_yaml: str) -> Config | None:
    """Merge a variant yaml snippet into the base config; return new validated Config.

    Returns None when:
      - The yaml is empty / comment-only (e.g. divider's "no config" variant)
      - Parsing or validation fails (logged to caller for visibility)
    """
    if not variant_yaml.strip():
        return None
    # Strip comment-only snippets (divider, github_icon variants)
    non_comment = "\n".join(
        line
        for line in variant_yaml.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    if not non_comment.strip():
        return None
    try:
        parsed = _yaml.safe_load(variant_yaml)
    except _yaml.YAMLError:
        return None
    if not isinstance(parsed, dict):
        return None
    base_dict = base_config.model_dump()
    merged = _deep_merge(base_dict, parsed)
    try:
        return Config.model_validate(merged)
    except Exception:
        return None


def _is_enabled_for(builder_module: str, builder_func: str, cfg: Config) -> bool:
    """Check if the variant config has the relevant widget enabled.
    Disabled widgets skip rendering — user sees the config snippet but no SVG.
    """
    if builder_module == "brain":
        return cfg.brain.enabled
    if builder_module == "tech_cards":
        return cfg.cards.tech_stack.enabled
    if builder_module == "focus":
        return cfg.cards.current_focus.enabled
    if builder_module == "timeline":
        return cfg.cards.yearly_highlights.enabled
    if builder_module == "typing":
        if builder_func == "build_about":
            return cfg.typing.about.enabled
        if builder_func == "build_motto":
            return cfg.typing.motto.enabled
    if builder_module == "banner":
        if builder_func == "build_header":
            return cfg.cards.header.enabled
        if builder_func == "build_footer":
            return cfg.cards.footer.enabled
    return True  # github_icon, divider always render


def build_variants(config: Config, output_dir: str | Path = "assets/variants") -> dict[str, str]:
    """Render one SVG per showcase-catalog variant.

    Returns ``{filename: status}`` where status is one of:
      "built"        — SVG written
      "no-config"    — variant yaml is empty/comment-only (divider, github_icon)
      "disabled"     — variant config has the widget disabled
      "config-error" — yaml parse or schema validation failed
      "render-error: <msg>" — builder raised an exception

    Output goes to ``<output_dir>/<base>__<slug>.svg`` (e.g.
    ``assets/variants/header-banner__wave-drift.svg``).
    """
    # Lazy import to avoid circular dependency (markers.py imports from us).
    from .markers import _WIDGET_CATALOG

    out_root = Path(output_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    results: dict[str, str] = {}
    for entry in _WIDGET_CATALOG:
        base_stem = entry.filename.replace(".svg", "")
        for variant in entry.variants:
            variant_filename = f"{base_stem}__{variant.slug}.svg"
            variant_cfg = _apply_variant(config, variant.yaml)
            if variant_cfg is None:
                results[variant_filename] = "no-config"
                continue
            if not _is_enabled_for(entry.builder_module, entry.builder_func, variant_cfg):
                results[variant_filename] = "disabled"
                continue
            try:
                mod = importlib.import_module(f"cortex.builders.{entry.builder_module}")
                func = getattr(mod, entry.builder_func)
                func(variant_cfg, output=str(out_root / variant_filename))
                results[variant_filename] = "built"
            except Exception as e:
                results[variant_filename] = f"render-error: {e}"
    return results
