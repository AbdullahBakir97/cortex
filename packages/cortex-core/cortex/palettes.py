"""Named palette presets — referenced from ``cortex.yml`` via ``brand.palette``.

Each palette is a frozen dict of color tokens. Builders look up colors by
semantic name (``primary``, ``accent_a`` …) so swapping the palette flips
the entire profile's vibe in one config change.
"""
from __future__ import annotations

from typing import Final, TypedDict


class Palette(TypedDict):
    primary:    str
    secondary:  str
    accent_a:   str
    accent_b:   str
    accent_c:   str
    accent_d:   str
    background: str


PALETTES: Final[dict[str, Palette]] = {
    # The reference palette — Abdullah's red+rainbow neon
    "neon-rainbow": {
        "primary":    "#F90001",
        "secondary":  "#FF652F",
        "accent_a":   "#22D3EE",
        "accent_b":   "#A78BFA",
        "accent_c":   "#FFD23F",
        "accent_d":   "#34D399",
        "background": "#0D1117",
    },
    # Subtle, professional, single-accent
    "monochrome": {
        "primary":    "#FFFFFF",
        "secondary":  "#9BA1A6",
        "accent_a":   "#6E7681",
        "accent_b":   "#21262D",
        "accent_c":   "#FFFFFF",
        "accent_d":   "#6E7681",
        "background": "#0D1117",
    },
    # Hot magenta + electric cyan
    "cyberpunk": {
        "primary":    "#FF2E63",
        "secondary":  "#08D9D6",
        "accent_a":   "#A100F2",
        "accent_b":   "#F8FA0A",
        "accent_c":   "#FF2E63",
        "accent_d":   "#08D9D6",
        "background": "#0D0221",
    },
    # Subtle neutrals + one warm accent
    "minimal": {
        "primary":    "#E5E7EB",
        "secondary":  "#9CA3AF",
        "accent_a":   "#F59E0B",
        "accent_b":   "#9CA3AF",
        "accent_c":   "#F59E0B",
        "accent_d":   "#E5E7EB",
        "background": "#111827",
    },
    # Warm 80s-inspired
    "retro": {
        "primary":    "#FF6B35",
        "secondary":  "#F7931E",
        "accent_a":   "#FFD23F",
        "accent_b":   "#06AED5",
        "accent_c":   "#7B2CBF",
        "accent_d":   "#EF476F",
        "background": "#1A0E26",
    },
}


def resolve_palette(name: str) -> Palette:
    """Look up a palette by name. Raises KeyError with a helpful message."""
    try:
        return PALETTES[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown palette {name!r}. Available: {sorted(PALETTES.keys())}. "
            "You can also pass an explicit ``brand.colors`` block in your cortex.yml."
        ) from exc
