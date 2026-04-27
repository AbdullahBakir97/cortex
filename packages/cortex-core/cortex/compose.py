"""Stack multiple widget SVGs into a single composite SVG.

Use case: a profile README often wants ONE image to drop in (a hero stack
of header-banner + brain + badges + footer-banner) rather than 17 separate
references. ``cortex.compose.compose(config, widgets, output)`` builds each
listed widget in-memory, then concatenates them into a single SVG with
consistent vertical padding.

This is content-aware: each child SVG keeps its own viewBox, and the parent
SVG nests them via ``<svg x="0" y="<offset>" ...>`` elements so the renderer
treats each as an independent coordinate space. No path-rewriting needed.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from cortex.schema import Config

# Map widget slug -> (builder_module, builder_func, output_filename).
# Mirrors the plan list in cortex.__init__.build_all but accessible by name.
_WIDGET_REGISTRY: dict[str, tuple[str, str, str]] = {
    "header-banner": ("banner", "build_header", "header-banner.svg"),
    "synthwave-banner": ("synthwave", "build", "synthwave-banner.svg"),
    "brain-anatomical": ("brain", "build", "brain-anatomical.svg"),
    "skill-galaxy": ("galaxy", "build", "skill-galaxy.svg"),
    "tech-cards": ("tech_cards", "build", "tech-cards.svg"),
    "yearly-highlights": ("timeline", "build", "yearly-highlights.svg"),
    "code-roadmap": ("roadmap", "build", "code-roadmap.svg"),
    "current-focus": ("focus", "build", "current-focus.svg"),
    "badges": ("badges", "build", "badges.svg"),
    "skill-radar": ("radar", "build", "skill-radar.svg"),
    "activity-heatmap": ("heatmap", "build", "activity-heatmap.svg"),
    "stat-cubes": ("cubes", "build", "stat-cubes.svg"),
    "achievement-wall": ("trophies", "build", "achievement-wall.svg"),
    "code-dna": ("dna", "build", "code-dna.svg"),
    "skill-globe": ("globe", "build", "skill-globe.svg"),
    "particle-cloud": ("particles", "build", "particle-cloud.svg"),
    "now-playing": ("now_playing", "build", "now-playing.svg"),
    "about-typing": ("typing", "build_about", "about-typing.svg"),
    "motto-typing": ("typing", "build_motto", "motto-typing.svg"),
    "github-icon": ("github_icon", "build", "github-icon.svg"),
    "animated-divider": ("divider", "build", "animated-divider.svg"),
    "footer-banner": ("banner", "build_footer", "footer-banner.svg"),
}

# Pattern matching the viewBox attribute on an outer <svg>. We need it to
# size each row in the composite. The 4 numbers may be int or float.
_VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)"')


def list_available() -> list[str]:
    """Return the slugs that can be composed."""
    return sorted(_WIDGET_REGISTRY.keys())


def _build_widget_svg(slug: str, config: Config, tmp_dir: Path) -> tuple[str, float]:
    """Build the named widget into ``tmp_dir`` and return (svg_text, intrinsic_height)."""
    if slug not in _WIDGET_REGISTRY:
        raise ValueError(f"Unknown widget slug '{slug}'. Available: {', '.join(list_available())}")
    module_name, func_name, filename = _WIDGET_REGISTRY[slug]
    mod = importlib.import_module(f"cortex.builders.{module_name}")
    func = getattr(mod, func_name)
    out_path = tmp_dir / filename
    func(config, output=out_path)
    text = out_path.read_text(encoding="utf-8")

    # Extract intrinsic height from viewBox so the composite knows how
    # tall to make each row.
    m = _VIEWBOX_RE.search(text)
    if m:
        height = float(m.group(4))
    else:
        # Fallback: parse the height attribute directly.
        try:
            root = ET.fromstring(text)
            h_attr = root.get("height", "200")
            height = float(re.match(r"[\d.]+", h_attr or "200").group(0))  # type: ignore[union-attr]
        except (ET.ParseError, AttributeError, ValueError):
            height = 200.0
    return text, height


def _strip_xml_decl(svg: str) -> str:
    """Remove leading <?xml ...?> declaration so we can nest the SVG."""
    if svg.startswith("<?xml"):
        end = svg.find("?>")
        if end != -1:
            return svg[end + 2 :].lstrip()
    return svg


def _nest_svg(svg_text: str, x: float, y: float, width: float, height: float) -> str:
    """Wrap a child SVG inside an outer ``<svg x=.. y=..>`` for composition.

    The outer dimensions force the child's content into the given box;
    SVG renderers handle the coordinate-system mapping automatically.
    """
    inner = _strip_xml_decl(svg_text)
    # Strip the outermost <svg ...> opening tag and replace its position +
    # dimensions. We keep the original viewBox / xmlns attributes intact
    # so the child renders correctly at its natural aspect.
    m = re.match(r"<svg([^>]*)>", inner, flags=re.IGNORECASE)
    if not m:
        return inner
    inner_attrs = m.group(1)
    # Drop any existing width/height on the inner — we set ours.
    inner_attrs = re.sub(r'\s(width|height)="[^"]*"', "", inner_attrs)
    body = inner[m.end() :]
    return (
        f'<svg x="{x:.0f}" y="{y:.0f}" width="{width:.0f}" '
        f'height="{height:.0f}"{inner_attrs}>{body}'
    )


def compose(config: Config, widgets: list[str], output: str | Path, *, gap: int = 12) -> Path:
    """Build each widget in ``widgets`` and stack them vertically into one SVG.

    Args:
        config:  The user's loaded Config.
        widgets: Ordered list of widget slugs (see list_available()).
        output:  Output path for the composite SVG.
        gap:     Vertical pixel gap between widgets.

    Returns the output path.
    """
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = out_path.parent / ".compose-cache"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # All widgets are 1200 wide by convention.
    canvas_w = 1200
    rows: list[tuple[str, float]] = []
    for slug in widgets:
        svg_text, h = _build_widget_svg(slug, config, tmp_dir)
        rows.append((svg_text, h))

    total_h = sum(h for _, h in rows) + gap * max(0, len(rows) - 1)

    nested: list[str] = []
    y_cursor = 0.0
    for svg_text, h in rows:
        nested.append(_nest_svg(svg_text, x=0, y=y_cursor, width=canvas_w, height=h))
        y_cursor += h + gap

    composed = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="100%" viewBox="0 0 {canvas_w} {total_h:.0f}" '
        f'preserveAspectRatio="xMidYMin meet" '
        f'role="img" aria-label="Cortex composite">\n'
        f"{chr(10).join(nested)}\n"
        f"</svg>\n"
    )
    out_path.write_text(composed, encoding="utf-8")
    return out_path
