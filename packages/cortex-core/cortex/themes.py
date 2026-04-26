"""Cortex theme system.

A theme is a small dict of named color slots that every widget consults as
its default palette. Users pick one in ``brand.theme`` and every widget on
the page picks up coordinated colors without per-widget configuration.

Each theme defines five slots:

    "primary"     dominant accent (e.g. brain glow, badge fill)
    "secondary"   complementary accent (e.g. radar polygon, divider)
    "warm"        warm complement (e.g. trophies, focus stripes)
    "cool"        cool complement (e.g. radar, particles)
    "atmosphere"  background sweep (e.g. synthwave sky, galaxy nebula)

Widgets use ``resolve_theme(config)`` to fetch the active theme dict, then
read whichever slot fits their visual role. Per-widget explicit ``color``
overrides still win — themes only set defaults.
"""

from __future__ import annotations

from typing import Literal

ThemeName = Literal["outrun", "sunset", "midnight", "minimal", "cyberpunk", "rose"]


# Each theme is a 5-slot palette. Hex strings in #RRGGBB.
_THEMES: dict[str, dict[str, str]] = {
    # outrun — purple → pink → gold synthwave (cortex flagship feel)
    "outrun": {
        "primary": "#7B5EAA",
        "secondary": "#FF6B9D",
        "warm": "#FFD23F",
        "cool": "#22D3EE",
        "atmosphere": "#0E0820",
    },
    # sunset — warm amber-pink palette, softer than outrun
    "sunset": {
        "primary": "#FF6B9D",
        "secondary": "#FFA940",
        "warm": "#FFD23F",
        "cool": "#7B5EAA",
        "atmosphere": "#1A0633",
    },
    # midnight — deep blue/cyan, professional/corporate
    "midnight": {
        "primary": "#3178C6",
        "secondary": "#22D3EE",
        "warm": "#7DD3FC",
        "cool": "#1A1A48",
        "atmosphere": "#0B0218",
    },
    # minimal — restrained, two-tone, looks great in monochrome READMEs
    "minimal": {
        "primary": "#FFFFFF",
        "secondary": "#A0A0A8",
        "warm": "#D4D4D8",
        "cool": "#71717A",
        "atmosphere": "#18181B",
    },
    # cyberpunk — high-contrast pink/cyan/yellow with black bg
    "cyberpunk": {
        "primary": "#F90001",
        "secondary": "#22D3EE",
        "warm": "#FFD23F",
        "cool": "#7C3AED",
        "atmosphere": "#000000",
    },
    # rose — pinks/violets, matches the brain widget's body palette
    "rose": {
        "primary": "#C95E8A",
        "secondary": "#FF6B9D",
        "warm": "#F8C8DC",
        "cool": "#7B5EAA",
        "atmosphere": "#3A1A28",
    },
}

# Default fallback if config has no theme set.
DEFAULT_THEME: ThemeName = "outrun"


def resolve_theme(config: object) -> dict[str, str]:
    """Return the active theme palette for ``config``.

    Looks up ``config.brand.theme`` (a ThemeName) and returns its 5-slot
    color dict. Unknown / missing themes fall through to ``outrun``.
    """
    name = getattr(getattr(config, "brand", None), "theme", DEFAULT_THEME)
    return _THEMES.get(name, _THEMES[DEFAULT_THEME])


def palette_for(name: str) -> dict[str, str]:
    """Direct-access escape hatch — fetch a theme by name without a Config."""
    return _THEMES.get(name, _THEMES[DEFAULT_THEME])


REDUCED_MOTION_CSS = """@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}"""
"""Drop into any widget's <style> block to honor user motion preferences.

Cortex widgets use SMIL <animate>/<animateTransform> for most effects, which
the @media CSS rule cannot directly disable — but for CSS-driven animations
(badges pulse, banner pulse, brain electric-arcs), this rule kills them
under reduced-motion. SMIL elements also get a script-free disable strategy:
each widget gates animations behind a config flag the user can opt out of.
"""
