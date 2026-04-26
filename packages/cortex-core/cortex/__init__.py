"""Cortex Core — SVG generators and marker rewriting.

Public surface:

    >>> from cortex import Config, build_all
    >>> config = Config.from_yaml(".github/cortex.yml")
    >>> build_all(config, output_dir="assets/")

For lower-level access to individual builders, see ``cortex.builders``.
"""

from cortex.schema import (
    AutoUpdate,
    Brain,
    Brand,
    Cards,
    Config,
    Identity,
    Typing,
)

__all__ = [
    "AutoUpdate",
    "Brain",
    "Brand",
    "Cards",
    "Config",
    "Identity",
    "Typing",
    "__version__",
    "build_all",
    "build_variants",
]


def build_variants(config, output_dir="assets/variants"):  # type: ignore[no-untyped-def]
    """Re-export of :func:`cortex.variants.build_variants` for CLI / programmatic use."""
    from cortex.variants import build_variants as _bv

    return _bv(config, output_dir)


__version__ = "0.2.1"


def build_all(config: Config, output_dir: str = "assets") -> dict[str, str]:
    """Run every enabled builder against ``config`` and write SVGs to ``output_dir``.

    Returns a dict of {widget_name: status} where status is one of:
      "built"        — SVG was generated and written
      "disabled"     — config has the widget disabled
      "not-implemented" — builder ships in a later version

    v0.2 ships the full core widget set: brain, tech_cards, timeline, focus,
    typing-about, typing-motto. Future widgets that aren't on disk yet still
    report "not-implemented" so users see a clear progress signal.
    """
    import importlib
    import os

    os.makedirs(output_dir, exist_ok=True)

    # (enabled_flag, builder_module, builder_func, output_filename)
    plan: list[tuple[bool, str, str, str]] = [
        (config.cards.header.enabled, "banner", "build_header", "header-banner.svg"),
        (config.brain.enabled, "brain", "build", "brain-anatomical.svg"),
        (config.cards.tech_stack.enabled, "tech_cards", "build", "tech-cards.svg"),
        (config.cards.yearly_highlights.enabled, "timeline", "build", "yearly-highlights.svg"),
        (config.cards.current_focus.enabled, "focus", "build", "current-focus.svg"),
        (config.typing.about.enabled, "typing", "build_about", "about-typing.svg"),
        (config.typing.motto.enabled, "typing", "build_motto", "motto-typing.svg"),
        (True, "github_icon", "build", "github-icon.svg"),
        (True, "divider", "build", "animated-divider.svg"),
        (config.cards.footer.enabled, "banner", "build_footer", "footer-banner.svg"),
    ]

    results: dict[str, str] = {}
    for enabled, module_name, func_name, filename in plan:
        if not enabled:
            results[filename] = "disabled"
            continue
        try:
            mod = importlib.import_module(f"cortex.builders.{module_name}")
        except ModuleNotFoundError:
            results[filename] = "not-implemented"
            continue
        func = getattr(mod, func_name, None)
        if func is None:
            results[filename] = "not-implemented"
            continue
        func(config, output=os.path.join(output_dir, filename))
        results[filename] = "built"

    # Variant gallery — render every showcase-catalog recipe to its own SVG so
    # the SHOWCASE marker block in the README can show actual previews per
    # recipe (not just code snippets). Goes into <output_dir>/variants/.
    from cortex.variants import build_variants as _bv

    variant_results = _bv(config, output_dir=os.path.join(output_dir, "variants"))
    # Mark variants in the result dict with "variants/" prefix so callers can
    # tell them apart from main builds.
    for fname, status in variant_results.items():
        results[f"variants/{fname}"] = status

    return results
