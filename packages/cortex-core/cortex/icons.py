"""Built-in icon glyph library for the badges widget.

Each known slug maps to a brand color and a 1-2 letter monogram. Monograms are
deliberately used instead of brand-replica icons because:

  • Trademark-safe (no risk of inaccurate or unauthorized brand reproduction)
  • Look uniformly clean at any size with cortex's gradient/glow polish
  • Stay tiny (no embedded path data — generated on render)

Users who want exact brand iconography can supply ``icon_svg`` (raw SVG path
``d`` string) per badge, which overrides the monogram entirely.
"""

from __future__ import annotations

# Slug → (monogram, brand_color). Monogram is 1-2 uppercase letters.
KNOWN_ICONS: dict[str, tuple[str, str]] = {
    # Languages
    "python": ("PY", "#3776AB"),
    "javascript": ("JS", "#F7DF1E"),
    "typescript": ("TS", "#3178C6"),
    "rust": ("RS", "#CE422B"),
    "go": ("GO", "#00ADD8"),
    "ruby": ("RB", "#CC342D"),
    "java": ("JV", "#ED8B00"),
    "kotlin": ("KT", "#7F52FF"),
    "swift": ("SW", "#FA7343"),
    "c": ("C", "#A8B9CC"),
    "cpp": ("C++", "#00599C"),
    "csharp": ("C#", "#239120"),
    "php": ("PHP", "#777BB4"),
    # Frontend
    "react": ("R", "#61DAFB"),
    "vue": ("V", "#4FC08D"),
    "svelte": ("S", "#FF3E00"),
    "angular": ("NG", "#DD0031"),
    "nextjs": ("N", "#000000"),
    "tailwind": ("TW", "#06B6D4"),
    # Backend / runtimes
    "nodejs": ("N", "#5FA04E"),
    "deno": ("D", "#000000"),
    "django": ("DJ", "#092E20"),
    "flask": ("FL", "#000000"),
    "fastapi": ("FA", "#009688"),
    # Cloud
    "aws": ("AWS", "#FF9900"),
    "gcp": ("GCP", "#4285F4"),
    "azure": ("AZ", "#0078D4"),
    "vercel": ("V", "#000000"),
    "cloudflare": ("CF", "#F38020"),
    # Databases
    "postgres": ("PG", "#4169E1"),
    "mongodb": ("M", "#47A248"),
    "redis": ("R", "#DC382D"),
    # DevOps
    "docker": ("DK", "#2496ED"),
    "kubernetes": ("K8", "#326CE5"),
    "terraform": ("TF", "#7B42BC"),
    "git": ("G", "#F05032"),
    "github": ("GH", "#181717"),
    # ML / Data
    "tensorflow": ("TF", "#FF6F00"),
    "pytorch": ("PT", "#EE4C2C"),
    "pandas": ("PD", "#150458"),
    # Tools
    "linux": ("LX", "#000000"),
    "vscode": ("VS", "#007ACC"),
}


def lookup(slug: str) -> tuple[str, str] | None:
    """Return (monogram, color) for a known slug, or None if unknown."""
    return KNOWN_ICONS.get(slug.lower())


def derive_monogram(label: str) -> str:
    """Build a 1-2 letter monogram from a free-form label.

    "PostgreSQL" → "PO", "Vue" → "V", "C#" → "C#", "Rust 1.73" → "RU".
    """
    label = label.strip()
    if not label:
        return "?"
    # Preserve symbol-bearing names like "C#", "C++"
    if any(c in label for c in "+#"):
        return label[:3].upper()
    # First two letters, uppercase
    return label[:2].upper() if len(label) >= 2 else label[:1].upper()
