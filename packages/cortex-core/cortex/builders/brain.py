"""Anatomical neon brain builder.

Pipeline:
  1. Read the cached Wikimedia ``Human-brain.SVG`` (Hugh Guiney, CC-BY-SA-3.0)
     from ``cortex/assets/brain-source.svg``.
  2. Extract the ``<g id="brain">`` element via bracket-balanced parsing.
  3. Recolor every fill/stroke to the configured neon palette.
  4. Embed inside a hand-crafted wrapper SVG with title, leader lines, labels,
     and animations driven by the user's ``cortex.yml``.
  5. Write to the provided output path.

Ported from the prototype at:
  https://github.com/AbdullahBakir97/AbdullahBakir97/blob/main/scripts/build_anatomical_brain.py
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from cortex.palettes import resolve_palette
from cortex.schema import BrainRegion, Config


def _x(text: str) -> str:
    """XML-escape user-provided text before injection into the SVG template."""
    return xml_escape(text, {"'": "&apos;", '"': "&quot;"})


# ── Color replacement maps (Wikimedia source uses these specific hexes) ──
# Fallback: paths the per-lobe classifier doesn't recognize fall through here
# and get the global brainGrad. Should rarely fire after classification.
_FILL_REPLACEMENTS: dict[str, str] = {
    "#fff0cd": "url(#brainGrad_unified)",
    "#fdd99b": "url(#brainGrad_unified)",
    "#d9bb7a": "url(#brainGrad_unified)",
    "#ffffff": "url(#brainGrad_unified)",
    "#816647": "url(#brainGrad_unified)",
}


def _stroke_replacements(palette_primary: str, palette_secondary: str) -> dict[str, str]:
    return {
        "#816647": palette_primary,  # main brown outline → palette primary
        "#000000": palette_secondary,  # any black outlines → palette secondary
    }


# ── Anatomical classification of brain-source.svg paths ──────────────────
# Brain source orientation: viewBox 0 0 1024 732, brain faces LEFT.
# - cerebrum: 149 paths with no semantic IDs → classified spatially below
# - cerebellum: nested INSIDE brain-stem group in this source (50 paths)
# - brain-stem: 51 paths once cerebellum is subtracted
#
# Cerebrum classification thresholds (brain-local coords):
#   frontal:   cx < 350         (front of brain, low x)
#   occipital: cx > 700         (back of brain, high x)
#   parietal:  350 <= cx <= 700 AND cy < 300  (top middle)
#   temporal:  350 <= cx <= 700 AND cy >= 300 (bottom middle)
#
# Brain group transform in the wrapper SVG is translate(332,152) scale(0.7),
# so canvas centroid = brain-local centroid * 0.7 + (332, 152).

_LOBE_KEYS = ("frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem")
_LOBE_PATH_IDS: dict[str, set[str]] | None = None  # populated lazily
_LOBE_CENTROIDS: dict[str, tuple[int, int]] | None = None  # canvas-space
_LOBE_BBOXES: dict[str, tuple[float, float, float, float]] | None = None  # brain-local (xmin,ymin,xmax,ymax)
_LOBE_PATHS_BY_LOBE: dict[str, list[tuple[str, str]]] | None = None


def _path_centroid_d(d_attr: str) -> tuple[float, float] | None:
    """Approximate centroid of an SVG path by averaging its numeric d-coordinates."""
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d_attr)]
    if len(nums) < 4:
        return None
    return (sum(nums[::2]) / len(nums[::2]), sum(nums[1::2]) / len(nums[1::2]))


def _extract_g_by_id(svg: str, gid: str) -> str:
    """Extract content between <g id="gid">...</g> via bracket-balanced walk."""
    m = re.search(rf'<g\s[^>]*?id="{re.escape(gid)}"[^>]*?>', svg, re.DOTALL)
    if not m:
        return ""
    start = m.end()
    pos = start
    depth = 1
    while depth > 0 and pos < len(svg):
        no = svg.find("<g", pos)
        nc = svg.find("</g>", pos)
        if nc == -1:
            break
        if no != -1 and no < nc:
            after = svg[no + 2 : no + 3]
            if after in (" ", ">", "\n", "\t", "\r"):
                depth += 1
            pos = no + 2
        else:
            depth -= 1
            pos = nc + 4
    return svg[start : pos - 4]


def _iter_paths(group: str):
    """Yield (id, d) pairs for each <path/> in a group fragment."""
    for pm in re.finditer(r"<path\b[^>]*?/>", group, re.DOTALL):
        block = pm.group(0)
        dm = re.search(r'\sd="([^"]+)"', block)
        im = re.search(r'\sid="([^"]+)"', block)
        if dm and im:
            yield im.group(1), dm.group(1)


def _seed_from_name(name: str) -> int:
    """Stable 32-bit seed derived from the identity name. Deterministic per user."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _random_cells_in_bbox(
    bbox: tuple[float, float, float, float],
    n: int,
    rng: random.Random,
) -> list[tuple[int, int]]:
    """Return n cells at random normalized offsets in [0.15, 0.85] inside bbox.

    Inset 15% from each edge so cells sit well inside the lobe rather than on its edge.
    Coords are returned as ints (SVG tolerates floats but ints render slightly tighter).
    """
    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    out: list[tuple[int, int]] = []
    for _ in range(n):
        nx = rng.uniform(0.15, 0.85)
        ny = rng.uniform(0.15, 0.85)
        out.append((round(xmin + nx * w), round(ymin + ny * h)))
    return out


@dataclass(frozen=True)
class _Arc:
    """One randomized synaptic arc between two cells, with Bezier control point."""
    x1: int
    y1: int
    x2: int
    y2: int
    cx: int   # quadratic Bezier control point x
    cy: int   # quadratic Bezier control point y
    color: str
    begin_s: float
    dur_s: float


def _random_arc_network(
    cells_by_lobe: dict[str, list[tuple[int, int]]],
    n: int,
    rng: random.Random,
    lobe_colors: dict[str, str],
) -> list[_Arc]:
    """n random arcs across the union of cells, colored by source lobe.

    Each arc:
      - source cell picked uniformly from the union of all lobes' cells
      - target cell picked uniformly from the union (resampled if equal to source)
      - color = source-lobe's accent
      - quadratic Bezier control point at midpoint + random offset (±60px each axis)
      - begin_s in [0, 12), dur_s in [0.8, 1.6)
    """
    cell_lobe: list[tuple[tuple[int, int], str]] = []
    for lobe, cells in cells_by_lobe.items():
        for c in cells:
            cell_lobe.append((c, lobe))

    arcs: list[_Arc] = []
    for _ in range(n):
        (p1, lobe1) = rng.choice(cell_lobe)
        (p2, _lobe2) = rng.choice(cell_lobe)
        # Resample if we drew the same cell twice (no self-loops)
        attempts = 0
        while p2 == p1 and attempts < 5:
            (p2, _lobe2) = rng.choice(cell_lobe)
            attempts += 1
        if p2 == p1:
            # Pathological: skip rather than emit a degenerate arc.
            continue
        mid_x = (p1[0] + p2[0]) // 2
        mid_y = (p1[1] + p2[1]) // 2
        cx = mid_x + rng.randint(-60, 60)
        cy = mid_y + rng.randint(-60, 60)
        arcs.append(_Arc(
            x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1],
            cx=cx, cy=cy,
            color=lobe_colors[lobe1],
            begin_s=rng.uniform(0.0, 12.0),
            dur_s=rng.uniform(0.8, 1.6),
        ))
    return arcs


def _build_lobe_stroke_overlay(
    paths_by_lobe: dict[str, list[tuple[str, str]]],
    lobe_colors: dict[str, str],
    n_per_lobe: int = 8,
) -> list[str]:
    """Build per-lobe duplicate <path/> elements for the stroke-draw animation.

    For each lobe, emit the top n_per_lobe paths (ranked by len(d), descending)
    as fresh <path> elements with:
      - d="<original d>" (geometry copied from the source path)
      - fill="none" + stroke=<lobe_color> + stroke-width=2.2
      - pathLength="100" + stroke-dasharray="100 100" (so dashoffset animation
        works without per-path length measurement)
      - class="lobe-stroke ls-<lobe>" (CSS keyframes provide the draw-in/out)

    The overlay layer (parent <g>) gets filter="url(#electricGlow)" applied
    once, not per-path.
    """
    out: list[str] = []
    for lobe, pairs in paths_by_lobe.items():
        if not pairs:
            continue
        color = lobe_colors[lobe]
        ranked = sorted(pairs, key=lambda p: len(p[1]), reverse=True)
        for _pid, d in ranked[:n_per_lobe]:
            out.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" '
                f'pathLength="100" stroke-dasharray="100 100" '
                f'class="lobe-stroke ls-{lobe}"/>'
            )
    return out


def _dna_helix_paths(
    cx: int, cy: int,
    width: int = 80, height: int = 170,
    samples: int = 24,
) -> tuple[str, str, list[tuple[tuple[int, int], tuple[int, int]]]]:
    """Generate two intertwining sine paths + base-pair rung connectors for a DNA helix.

    Returns (strand_a_path_d, strand_b_path_d, rungs).
    Strand A: cosine wave (one phase). Strand B: -cosine (anti-phase, mirrored).
    Rungs: horizontal connectors at every 6th sample point (excluding endpoints).
    """
    points_a: list[tuple[int, int]] = []
    points_b: list[tuple[int, int]] = []
    rungs: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(samples + 1):
        t = i / samples
        y = round(cy + (t - 0.5) * height)
        offset = round(math.cos(t * 2 * math.pi * 2) * (width / 2))
        ax = cx + offset
        bx = cx - offset
        points_a.append((ax, y))
        points_b.append((bx, y))
        if i % 6 == 0 and i not in (0, samples):
            rungs.append(((ax, y), (bx, y)))

    strand_a = "M" + " L".join(f"{x},{y}" for x, y in points_a)
    strand_b = "M" + " L".join(f"{x},{y}" for x, y in points_b)
    return strand_a, strand_b, rungs


def _classify_brain_paths(
    svg: str,
) -> tuple[
    dict[str, set[str]],
    dict[str, tuple[int, int]],
    dict[str, tuple[float, float, float, float]],
    dict[str, list[tuple[str, str]]],
]:
    """Classify every brain path into one of 6 lobes; return paths/centroids/bboxes/pairs.

    Returns a 4-tuple:
      classification: lobe -> set of path IDs
      centroids:      lobe -> (cx, cy) in CANVAS space (after wrapper transform)
      bboxes:         lobe -> (xmin, ymin, xmax, ymax) in BRAIN-LOCAL space
      paths_by_lobe:  lobe -> list of (id, d) tuples
    """
    # Cerebellum first (it's nested inside brain-stem in this source SVG).
    cere_g = _extract_g_by_id(svg, "cerebellum")
    cere_ids: set[str] = set()
    cere_centroids: list[tuple[float, float]] = []
    cere_pairs: list[tuple[str, str]] = []
    for pid, d in _iter_paths(cere_g):
        cere_ids.add(pid)
        cere_pairs.append((pid, d))
        c = _path_centroid_d(d)
        if c is not None:
            cere_centroids.append(c)

    # Brain-stem: extract everything, subtract cerebellum.
    bs_g = _extract_g_by_id(svg, "brain-stem")
    bs_ids: set[str] = set()
    bs_centroids: list[tuple[float, float]] = []
    bs_pairs: list[tuple[str, str]] = []
    for pid, d in _iter_paths(bs_g):
        if pid in cere_ids:
            continue
        bs_ids.add(pid)
        bs_pairs.append((pid, d))
        c = _path_centroid_d(d)
        if c is not None:
            bs_centroids.append(c)

    # Cerebrum: classified by spatial centroid into 4 lobes.
    cb_g = _extract_g_by_id(svg, "cerebrum")
    classification: dict[str, set[str]] = {k: set() for k in _LOBE_KEYS}
    centroids_by_lobe: dict[str, list[tuple[float, float]]] = {k: [] for k in _LOBE_KEYS}
    paths_by_lobe: dict[str, list[tuple[str, str]]] = {k: [] for k in _LOBE_KEYS}
    for pid, d in _iter_paths(cb_g):
        c = _path_centroid_d(d)
        if c is None:
            continue
        cx, cy = c
        if cx < 350:
            lobe = "frontal"
        elif cx > 700:
            lobe = "occipital"
        elif cy < 300:
            lobe = "parietal"
        else:
            lobe = "temporal"
        classification[lobe].add(pid)
        paths_by_lobe[lobe].append((pid, d))
        centroids_by_lobe[lobe].append(c)

    classification["cerebellum"] = cere_ids
    classification["brainstem"] = bs_ids
    centroids_by_lobe["cerebellum"] = cere_centroids
    centroids_by_lobe["brainstem"] = bs_centroids
    paths_by_lobe["cerebellum"] = cere_pairs
    paths_by_lobe["brainstem"] = bs_pairs

    # Convert each lobe's centroid average to canvas space.
    # Brain group transform: translate(332, 152) scale(0.7).
    canvas_centroids: dict[str, tuple[int, int]] = {}
    bboxes: dict[str, tuple[float, float, float, float]] = {}
    for lobe, cs in centroids_by_lobe.items():
        if cs:
            ax = sum(c[0] for c in cs) / len(cs)
            ay = sum(c[1] for c in cs) / len(cs)
            canvas_centroids[lobe] = (round(ax * 0.7 + 332), round(ay * 0.7 + 152))
            xs = [c[0] for c in cs]
            ys = [c[1] for c in cs]
            bboxes[lobe] = (min(xs), min(ys), max(xs), max(ys))
        else:
            canvas_centroids[lobe] = (700, 400)  # fallback to brain center
            bboxes[lobe] = (400.0, 300.0, 600.0, 500.0)  # fallback bbox

    return classification, canvas_centroids, bboxes, paths_by_lobe


def _ensure_classification() -> tuple[
    dict[str, set[str]],
    dict[str, tuple[int, int]],
    dict[str, tuple[float, float, float, float]],
    dict[str, list[tuple[str, str]]],
]:
    """Lazy module-level cache. First call parses + classifies; later calls reuse."""
    global _LOBE_PATH_IDS, _LOBE_CENTROIDS, _LOBE_BBOXES, _LOBE_PATHS_BY_LOBE
    if (
        _LOBE_PATH_IDS is None
        or _LOBE_CENTROIDS is None
        or _LOBE_BBOXES is None
        or _LOBE_PATHS_BY_LOBE is None
    ):
        src_text = (
            resources.files("cortex.assets")
            .joinpath("brain-source.svg")
            .read_text(encoding="utf-8")
        )
        (
            _LOBE_PATH_IDS,
            _LOBE_CENTROIDS,
            _LOBE_BBOXES,
            _LOBE_PATHS_BY_LOBE,
        ) = _classify_brain_paths(src_text)
    return _LOBE_PATH_IDS, _LOBE_CENTROIDS, _LOBE_BBOXES, _LOBE_PATHS_BY_LOBE


def _recolor(
    content: str,
    palette_primary: str,
    palette_secondary: str,
) -> str:
    """All source fills → brainGrad_unified; strokes → palette colors.

    The body fill is unified across the brain (single gradient on every path).
    Lobe identity is conveyed by the stroke-overlay layer added later in the
    composition, not by per-path fill substitution.
    """
    for old, new in _FILL_REPLACEMENTS.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"fill:{variant}", f"fill:{new}")

    strokes = _stroke_replacements(palette_primary, palette_secondary)
    for old, new in strokes.items():
        for variant in (old, old.upper(), old.lower()):
            content = content.replace(f"stroke:{variant}", f"stroke:{new}")
    return content


# ── Region label data (positions on the wrapper canvas) ──────────────────
_REGION_POSITIONS = {
    # Card positions chosen to be on the SAME side of the canvas as the lobe
    # they point to (avoids crisscrossing leader lines). target_xy values are
    # overridden at build time with classified centroids — the values here are
    # fallbacks if classification fails.
    # Brain orientation: faces LEFT, so frontal at canvas-left, occipital at canvas-right.
    "frontal":    {"label_xy": (20,   200), "target_xy": (471, 395), "color": "primary"},   # left  (lobe at canvas left)
    "parietal":   {"label_xy": (540,  130), "target_xy": (710, 260), "color": "accent_d"},  # top center
    "occipital":  {"label_xy": (1060, 200), "target_xy": (909, 398), "color": "secondary"}, # right (lobe at canvas right)
    "temporal":   {"label_xy": (1060, 480), "target_xy": (706, 468), "color": "accent_c"},  # right-mid
    "cerebellum": {"label_xy": (1060, 660), "target_xy": (824, 568), "color": "accent_a"},  # right-bottom
    "brainstem":  {"label_xy": (20,   660), "target_xy": (823, 569), "color": "accent_b"},  # left-bottom
}

_REGION_CAPTIONS = {
    "frontal": "FRONTAL · LOBE",
    "parietal": "PARIETAL · LOBE",
    "occipital": "OCCIPITAL · LOBE",
    "temporal": "TEMPORAL · LOBE",
    "cerebellum": "CEREBELLUM",
    "brainstem": "BRAINSTEM",
}


def _emoji_for_region(region: str) -> str:
    return {
        "frontal": "⚙️",
        "parietal": "🏗️",
        "occipital": "🎨",
        "temporal": "💾",
        "cerebellum": "🛠️",
        "brainstem": "🤖",
    }.get(region, "🧠")


# ── Wrapper SVG composition ──────────────────────────────────────────────
def _compose_wrapper(brain_content: str, config: Config) -> str:
    """Wrap recolored brain content in the full Cortex composition."""
    palette = (
        resolve_palette(config.brand.palette)
        if config.brand.palette in {"neon-rainbow", "monochrome", "cyberpunk", "minimal", "retro"}
        else None
    )
    if palette is None:
        palette = config.brand.colors.model_dump()  # explicit colors override

    p_primary = palette["primary"]
    p_secondary = palette["secondary"]
    p_accent_a = palette["accent_a"]
    p_accent_b = palette["accent_b"]
    p_accent_c = palette["accent_c"]
    p_accent_d = palette["accent_d"]
    p_background = palette["background"]

    name = _x(config.identity.name)
    atm = config.brain.atmosphere
    brain_3d_class = "brain-3d" if atm.wobble else ""

    # Replace hardcoded target_xy with anatomically-correct centroids computed
    # from the actual classified paths in the source SVG. This fixes the bug
    # where, e.g., the "frontal" leader line pointed to canvas (850, 320) when
    # the actual frontal lobe centroid is at (471, 395).
    _, lobe_centroids, lobe_bboxes, paths_by_lobe = _ensure_classification()
    region_positions: dict[str, dict[str, object]] = {}
    for key, region_data in _REGION_POSITIONS.items():
        region_positions[key] = {
            "label_xy": region_data["label_xy"],
            "target_xy": lobe_centroids.get(
                key, region_data["target_xy"]  # fallback to hardcoded
            ),
            "color": region_data["color"],
        }

    # Region labels (anatomical → user's domain mapping). All endpoint
    # decorations (region glow, halo, spark dot) now live inside brain-3d
    # so they wobble with the brain anatomy in lockstep. The leader line
    # is still in canvas space; its endpoint reads as soft because the
    # leader stroke fades to lower opacity near the brain.
    region_blocks: list[str] = []
    region_lines: list[str] = []
    region_grads: list[str] = []  # one radial gradient per lobe color
    region_glows: list[str] = []  # large soft tint circles in card colors (always rendered)
    halos: list[str] = []  # ring around each spark dot (gated by atm.show_halos)
    spark_dots: list[str] = []  # central dot at each lobe target (always rendered)
    data_packets: list[str] = []  # small dots traveling card->brain along each leader path
    for i, (key, region_data) in enumerate(region_positions.items()):
        region_obj: BrainRegion = getattr(config.brain.regions, key)
        color_token = region_data["color"]
        color = palette[color_token]  # type: ignore[index]
        lx, ly = region_data["label_xy"]
        tx, ty = region_data["target_xy"]
        emoji = _emoji_for_region(key)
        cap = _REGION_CAPTIONS[key]
        domain = _x(region_obj.domain)
        tools_preview = _x(" · ".join(region_obj.tools[:4])) if region_obj.tools else ""

        # Glassmorphism lobe card: base + traveling edge glow + highlight overlay.
        # Matches the visual language of tech-cards.svg (also card-based).
        region_blocks.append(
            f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
            f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardBg)" '
            f'filter="url(#cardShadowStacked)"/>'
            f'<rect x="6" y="6" width="308" height="128" rx="10" '
            f'fill="url(#cardInnerGlow_{key})" class="card-inner-pulse"/>'
            f'<rect x="0" y="0" width="320" height="140" rx="14" fill="none" '
            f'stroke="{color}" stroke-width="2" pathLength="1000" '
            f'class="card-edge ce{i + 1}"/>'
            f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardHighlight)"/>'
            f'<text x="160" y="38" class="t-cat-cap" text-anchor="middle" fill="{color}">{cap}</text>'
            f'<text x="160" y="80" class="t-region" text-anchor="middle">{emoji} {domain}</text>'
            f'<text x="160" y="116" class="t-skill" text-anchor="middle">{tools_preview}</text>'
            f"</g></g>"
        )

        # Per-region radial gradient — used by the region glow inside brain-3d.
        # Soft falloff: full color at center, fading to transparent at edge.
        region_grads.append(
            f'<radialGradient id="rgrad_{key}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.55"/>'
            f'<stop offset="55%"  stop-color="{color}" stop-opacity="0.18"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
            f"</radialGradient>"
        )

        # Leader line from label edge to brain target (canvas space).
        # Stroke opacity reduced from 0.7 to 0.5 — the line softly arrives
        # at the brain region rather than terminating with a hard endpoint.
        # This masks the small visual offset from the wobbling halo+dot below.
        mid_x = (lx + tx) // 2
        mid_y = (ly + 140 + ty) // 2 if ly < 400 else (ly + ty) // 2
        anchor_x = lx if lx > 600 else lx + 320
        anchor_y = ly + 70
        # Leader path morphs between two slightly different control-point
        # positions over 7s — the curve breathes. The mid-point oscillates
        # by ±36px in x and -18px in y (a subtle "lift") on alternating
        # lobes, so the 6 lines don't all sway in unison. Data packets
        # animating along this path via animateMotion follow the morphed d.
        sway_dx = 36 if i % 2 == 0 else -36
        sway_dy = -18
        d_rest = f"M {anchor_x},{anchor_y} Q {mid_x},{mid_y} {tx},{ty}"
        d_inhale = f"M {anchor_x},{anchor_y} Q {mid_x + sway_dx},{mid_y + sway_dy} {tx},{ty}"
        leader_id = f"leaderPath_{key}"
        region_lines.append(
            f'<path id="{leader_id}" d="{d_rest}" '
            f'stroke="{color}" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.5" class="leader-flow">'
            f'<animate attributeName="d" '
            f'values="{d_rest};{d_inhale};{d_rest}" '
            f'dur="7s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
            f"</path>"
        )

        # Data packets — small dots that travel card->brain along the leader path
        # via SMIL animateMotion. Two packets per line, staggered by half-period,
        # so the line reads as a continuous data stream. Fade in/out so they
        # don't pop at the endpoints.
        for pbegin in (0.0, 1.5):
            data_packets.append(
                f'<circle r="3.5" fill="{color}" opacity="0">'
                f'<animateMotion dur="3s" repeatCount="indefinite" begin="{pbegin}s" rotate="auto">'
                f'<mpath href="#{leader_id}"/>'
                f"</animateMotion>"
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" '
                f'dur="3s" begin="{pbegin}s" repeatCount="indefinite"/>'
                f"</circle>"
            )

        # Spark dot, halo, and region color glow all live in BRAIN-LOCAL
        # coordinates inside the brain-3d transform group, so they wobble in
        # lockstep with the brain anatomy. Brain group transform is
        # translate(332,152) scale(0.7), so brain-local = (canvas - 332)/0.7.
        bx = round((tx - 332) / 0.7)
        by = round((ty - 152) / 0.7)

        # Region color glow — a large soft radial gradient circle in the
        # card's color. With mix-blend-mode: screen this tints the brain
        # anatomy underneath without recoloring the source paths.
        region_glows.append(
            f'<circle cx="{bx}" cy="{by}" r="200" fill="url(#rgrad_{key})" '
            f'class="region-glow region-pulse rg{i + 1}"/>'
        )
        # Halo ring — wobbles with brain (r=20 renders as ~14 after 0.7 scale).
        halos.append(
            f'<circle cx="{bx}" cy="{by}" r="20" fill="none" stroke="{color}" '
            f'stroke-width="2.2" class="target-halo" '
            f'style="animation-delay:{i * 0.3}s"/>'
        )
        # Spark dot — r=6 renders as ~4.2 after the 0.7 scale.
        spark_dots.append(
            f'<circle cx="{bx}" cy="{by}" r="6" fill="{color}" class="target-pulse" '
            f'style="animation-delay:{i * 0.3}s"/>'
        )

    # Per-card inner glow — radial gradient in the lobe color, used by the
    # card-inner-pulse rect inside each card.
    card_inner_grads: list[str] = []
    for key, region_data in region_positions.items():
        color = palette[region_data["color"]]  # type: ignore[index]
        card_inner_grads.append(
            f'<radialGradient id="cardInnerGlow_{key}" cx="50%" cy="50%" r="60%">'
            f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.18"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
            f"</radialGradient>"
        )

    # Synaptic firing — 4 micro-cells per lobe placed inside that lobe's
    # actual bounding box (computed from classified path centroids). Each
    # lobe also gets 4 arcs connecting its cells in a quadrilateral so the
    # firing reads as electric impulses traveling between cells WITHIN the
    # same brain region. Each lobe paints in its own accent color, on its
    # own staggered phase so the brain reads as 6 independent micro-networks
    # firing concurrently.
    lobe_color_tokens = {
        "frontal": p_primary,
        "parietal": p_accent_d,
        "occipital": p_secondary,
        "temporal": p_accent_c,
        "cerebellum": p_accent_a,
        "brainstem": p_accent_b,
    }

    # Per-lobe stroke overlay — top 8 paths per lobe, duplicated as colored
    # stroke <path/> elements with stroke-dashoffset animation. Lobe identity
    # comes from this layer, not the body fill.
    lobe_stroke_overlay = _build_lobe_stroke_overlay(
        paths_by_lobe, lobe_color_tokens, n_per_lobe=8,
    )
    # Deterministic-but-disordered RNG seeded by the user's name. Same user →
    # same arc layout every render (so CI diffs of examples/rendered/ are stable
    # across builds); different users → unique signatures.
    rng = random.Random(_seed_from_name(config.identity.name))

    # 6 random cells per lobe inside its bbox.
    cells_by_lobe: dict[str, list[tuple[int, int]]] = {}
    for lobe in _LOBE_KEYS:
        bbox = lobe_bboxes.get(lobe)
        if bbox is None:
            continue
        cells_by_lobe[lobe] = _random_cells_in_bbox(bbox, n=6, rng=rng)

    # 20 random Bezier arcs across the union of all cells.
    arcs = _random_arc_network(cells_by_lobe, n=20, rng=rng,
                                lobe_colors=lobe_color_tokens)

    # Cells render as the existing .lobe-cell synaptic-flash, but at random
    # positions instead of bbox-corner quadrilateral.
    micro_cells: list[str] = []
    cell_offsets = (0.0, 0.6, 1.2, 1.8, 2.4, 3.0)  # 6 cells x 0.6s within-lobe stagger
    lobe_phase = {
        "frontal": 0.0, "parietal": 0.4, "occipital": 0.8,
        "temporal": 1.2, "cerebellum": 1.6, "brainstem": 2.0,
    }
    for lobe, cells in cells_by_lobe.items():
        color = lobe_color_tokens[lobe]
        phase = lobe_phase[lobe]
        for i, (cx, cy) in enumerate(cells):
            delay = phase + cell_offsets[i % len(cell_offsets)]
            micro_cells.append(
                f'<circle cx="{cx}" cy="{cy}" r="4" fill="{color}" '
                f'class="lobe-cell" style="animation-delay:{delay:.2f}s"/>'
            )

    # Arcs render as quadratic Bezier <path/> with the existing .lobe-arc keyframes
    # (arcflow + arcfade). The animation-delay/duration come from the random per-arc
    # values so the network reads as continuous firing.
    lobe_arcs: list[str] = []
    for a in arcs:
        lobe_arcs.append(
            f'<path d="M{a.x1},{a.y1} Q{a.cx},{a.cy} {a.x2},{a.y2}" '
            f'stroke="{a.color}" stroke-width="2.2" fill="none" '
            f'pathLength="100" stroke-dasharray="100 100" '
            f'class="lobe-arc" '
            f'style="animation-delay:{a.begin_s:.2f}s;animation-duration:{a.dur_s:.2f}s"/>'
        )

    # 16 ambient particle positions (must match the render below exactly).
    particle_positions: list[tuple[int, int]] = [
        (120, 180), (260, 540), (380, 120), (420, 760),
        (560, 380), (700, 220), (780, 700), (900, 160),
        (980, 520), (1080, 340), (1180, 780), (1260, 240),
        (160, 780), (340, 660), (640, 80),  (1320, 500),
    ]

    # Constellation lines: connect particles within 220px. Indices into
    # particle_positions. Deterministic by definition since positions are fixed.
    constellation_pairs: list[tuple[int, int]] = []
    threshold_sq = 220 * 220
    for ip in range(len(particle_positions)):
        for jp in range(ip + 1, len(particle_positions)):
            dxp = particle_positions[ip][0] - particle_positions[jp][0]
            dyp = particle_positions[ip][1] - particle_positions[jp][1]
            if dxp * dxp + dyp * dyp <= threshold_sq:
                constellation_pairs.append((ip, jp))

    constellation_lines: list[str] = []
    for n, (ip, jp) in enumerate(constellation_pairs):
        x1c, y1c = particle_positions[ip]
        x2c, y2c = particle_positions[jp]
        constellation_lines.append(
            f'<line x1="{x1c}" y1="{y1c}" x2="{x2c}" y2="{y2c}" '
            f'stroke="{p_accent_b}" stroke-width="0.8" stroke-opacity="0" '
            f'class="constellation-line cl{n + 1}"/>'
        )

    # Far star field — 30 dim points spread deterministically across the canvas.
    # Smaller and dimmer than ambient particles; reads as deep-space depth.
    star_rng = random.Random(_seed_from_name(config.identity.name) ^ 0xDEADBEEF)
    far_stars: list[str] = []
    for _ in range(30):
        sx = star_rng.randint(40, 1360)
        sy = star_rng.randint(40, 860)
        sr = round(star_rng.uniform(0.6, 1.2), 1)
        s_op = round(star_rng.uniform(0.20, 0.50), 2)
        s_dur = star_rng.choice([8, 10, 12, 14])
        far_stars.append(
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#FFFFFF" '
            f'opacity="{s_op}" class="far-star fs{s_dur}"/>'
        )

    # Nebula clouds — 4 large soft blurred radial gradients drifting on
    # staggered phases. More organic than aurora bands (which are flat
    # circles); these have feGaussianBlur for amorphous edges.
    nebula_blocks: list[str] = []
    nebula_specs = [
        ("#EC4899", -100, -100, 38),
        ("#7C3AED", 700, -100, 44),
        ("#22D3EE", -100, 500, 41),
        ("#34D399", 700, 500, 47),
    ]
    for n, (_ncolor, nx, ny, ndur) in enumerate(nebula_specs):
        ndx = -50 if n % 2 == 0 else 50
        ndy = -30 if n < 2 else 30
        nebula_blocks.append(
            f'<g class="nebula" filter="url(#nebulaBlur)">'
            f'<rect x="{nx}" y="{ny}" width="1100" height="1100" fill="url(#nebula_{n})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0; {ndx},{ndy}; 0,0" '
            f'dur="{ndur}s" repeatCount="indefinite"/>'
            f'</rect></g>'
        )

    # DNA helix symbols — 4 double-helix line drawings at canvas corners,
    # each fading in/out + drawing in via stroke-dashoffset on staggered 16s
    # timers. Reads as a scientific/biological motif tying the brain theme
    # to the organic atmosphere (no longer competing with the digital grid,
    # which was removed in R4-2).
    dna_specs = [
        (120, 120,  "#22D3EE", 0),    # top-left,    cyan,   delay 0s
        (1280, 120, "#EC4899", 4),    # top-right,   pink,   delay 4s
        (120, 780,  "#7C3AED", 8),    # bottom-left, purple, delay 8s
        (1280, 780, "#22D3EE", 12),   # bottom-right, cyan,  delay 12s
    ]
    dna_blocks: list[str] = []
    for cx_d, cy_d, dcolor, ddelay in dna_specs:
        strand_a, strand_b, rungs = _dna_helix_paths(cx_d, cy_d)
        rung_lines = "\n".join(
            f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
            f'stroke="{dcolor}" stroke-width="0.8" stroke-opacity="0.5"/>'
            for a, b in rungs
        )
        dna_blocks.append(
            f'<g class="dna" style="animation-delay:{ddelay}s">\n'
            f'    <path d="{strand_a}" stroke="{dcolor}" stroke-width="1.5" '
            f'fill="none" stroke-opacity="0.7" pathLength="100" '
            f'stroke-dasharray="100 100" class="dna-strand"/>\n'
            f'    <path d="{strand_b}" stroke="{dcolor}" stroke-width="1.5" '
            f'fill="none" stroke-opacity="0.7" pathLength="100" '
            f'stroke-dasharray="100 100" class="dna-strand"/>\n'
            f'{rung_lines}\n'
            f'  </g>'
        )

    # Compose the SVG
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  Neural Skill Atlas — anatomical neon brain
    • Brain anatomy by Hugh Guiney, CC-BY-SA-3.0
      (https://commons.wikimedia.org/wiki/File:Human-brain.SVG)
    • Recolored + composed by Cortex (https://github.com/AbdullahBakir97/cortex)
    • Generated for: {name}
-->
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900"
     viewBox="0 0 1400 900" role="img"
     aria-label="Cortex Neural Skill Atlas — {name}">
  <defs>
    <linearGradient id="brainGrad_unified" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="40s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="33%"  stop-color="#4D2438"/>
      <stop offset="66%"  stop-color="#5C2E45"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
    <radialGradient id="bgRadial" cx="50%" cy="50%" r="80%">
      <animate attributeName="r" values="72%;88%;72%" dur="9s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#280816"/>
      <stop offset="60%"  stop-color="#100308"/>
      <stop offset="100%" stop-color="{p_background}"/>
    </radialGradient>
    <radialGradient id="bgAura" cx="50%" cy="50%" r="40%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_0" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_1" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#7C3AED" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_2" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#22D3EE" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_3" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#34D399" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#34D399" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#34D399" stop-opacity="0"/>
    </radialGradient>
    <filter id="nebulaBlur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>
    <radialGradient id="aurora_a" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aurora_b" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#7C3AED" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aurora_c" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#22D3EE" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#1C1428" stop-opacity="0.94"/>
      <stop offset="100%" stop-color="#0A0612" stop-opacity="0.94"/>
    </linearGradient>
    <linearGradient id="cardHighlight" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#FFFFFF" stop-opacity="0.08"/>
      <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    {chr(10).join("    " + g for g in region_grads)}
    {chr(10).join("    " + g for g in card_inner_grads)}
    <filter id="cardShadowStacked" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="2"  stdDeviation="4"  flood-color="#000" flood-opacity="0.30"/>
      <feDropShadow dx="0" dy="6"  stdDeviation="12" flood-color="#000" flood-opacity="0.40"/>
      <feDropShadow dx="0" dy="14" stdDeviation="24" flood-color="#000" flood-opacity="0.30"/>
    </filter>
    <filter id="brainGlow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <!-- Electric glow: dilate the source then blur it then merge under the
         original. Applied to lobe-cells via CSS so each synaptic flash gets
         an electric corona around the dot. -->
    <filter id="electricGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feMorphology operator="dilate" radius="1.5" in="SourceGraphic" result="dilated"/>
      <feGaussianBlur in="dilated" stdDeviation="3" result="blurred"/>
      <feMerge>
        <feMergeNode in="blurred"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style><![CDATA[
      .t-display   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 44px; fill: #FFFFFF; }}
      .t-tag       {{ font-family: 'Inter', sans-serif; font-weight: 600; font-size: 15px; letter-spacing: 0.30em; text-transform: uppercase; fill: {p_accent_b}; }}
      .t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: 0.25em; text-transform: uppercase; }}
      .t-region    {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 22px; fill: #FFFFFF; }}
      .t-skill     {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 16px; fill: #E5E7EB; }}
      .brain-pulse {{ animation: brainPulse 5s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes brainPulse {{
        0%, 100% {{ filter: drop-shadow(0 0 16px rgba(236,72,153,0.45)); }}
        50%      {{ filter: drop-shadow(0 0 32px rgba(236,72,153,0.85)); }}
      }}
      .brain-3d {{ animation: brain3d 16s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes brain3d {{
        0%, 100% {{ transform: scaleX(1)    skewY(0deg); }}
        25%      {{ transform: scaleX(0.92) skewY(-1.5deg); }}
        50%      {{ transform: scaleX(0.82) skewY(0deg); }}
        75%      {{ transform: scaleX(0.92) skewY(1.5deg); }}
      }}
      .leader-flow  {{ stroke-dasharray: 4 6; animation: lflow 1.6s linear infinite; }}
      @keyframes lflow {{ to {{ stroke-dashoffset: -20; }} }}
      .target-pulse {{ animation: tpulse 1.6s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes tpulse {{ 0%,100%{{transform:scale(1);opacity:0.85}} 50%{{transform:scale(1.5);opacity:1}} }}
      .target-halo {{ animation: thalo 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes thalo {{ 0%,100%{{opacity:0.18;transform:scale(0.9)}} 50%{{opacity:0.45;transform:scale(1.25)}} }}
      .label-fade {{ opacity: 0; animation: lfade 0.8s cubic-bezier(0.22,1,0.36,1) forwards; }}
      @keyframes lfade {{ to {{ opacity: 1; }} }}
      .lf1{{animation-delay:0.4s}} .lf2{{animation-delay:0.55s}} .lf3{{animation-delay:0.7s}}
      .lf4{{animation-delay:0.85s}} .lf5{{animation-delay:1.0s}} .lf6{{animation-delay:1.15s}}
      .card-inner-pulse {{ animation: cardPulse 5s ease-in-out infinite; }}
      @keyframes cardPulse {{ 0%, 100% {{ opacity: 0.6; }} 50% {{ opacity: 1.0; }} }}
      .card-edge {{
        stroke-dasharray: 80 1000;
        animation: cardEdgeTravel 4s linear infinite;
        filter: url(#electricGlow);
        opacity: 0.95;
      }}
      @keyframes cardEdgeTravel {{ to {{ stroke-dashoffset: -1080; }} }}
      .ce1 {{ animation-delay: 0s; }}
      .ce2 {{ animation-delay: 0.7s; }}
      .ce3 {{ animation-delay: 1.4s; }}
      .ce4 {{ animation-delay: 2.1s; }}
      .ce5 {{ animation-delay: 2.8s; }}
      .ce6 {{ animation-delay: 3.5s; }}
      .region-glow {{ mix-blend-mode: screen; }}
      .region-pulse {{ animation: rpulse 5s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
      @keyframes rpulse {{
        0%, 100% {{ opacity: 0.65; transform: scale(1); }}
        50%      {{ opacity: 1.0;  transform: scale(1.10); }}
      }}
      .rg1{{animation-delay:0s}}    .rg2{{animation-delay:0.6s}}
      .rg3{{animation-delay:1.2s}}  .rg4{{animation-delay:1.8s}}
      .rg5{{animation-delay:2.4s}}  .rg6{{animation-delay:3.0s}}
      /* Per-lobe synaptic firing — each cell flashes on its lobe's phase
         + within-lobe stagger; the lobe-arcs between cells animate a
         traveling dash so the firing reads as electric impulses moving
         around the lobe's quadrilateral. */
      .lobe-cell {{ animation: lcell 2.4s ease-in-out infinite; transform-origin: center; transform-box: fill-box; opacity: 0; }}
      @keyframes lcell {{
        0%, 100% {{ opacity: 0;   transform: scale(0.6); }}
        10%      {{ opacity: 1;   transform: scale(1.8); filter: drop-shadow(0 0 8px currentColor); }}
        20%      {{ opacity: 0.7; transform: scale(1.2); }}
        30%      {{ opacity: 0;   transform: scale(0.8); }}
      }}
      /* Per-lobe stroke-draw overlay — duplicate paths above the body fill,
         each lobe's outline draws in over 1s, holds, draws out over 1s, rests.
         Six lobes staggered by 1s on a shared 6s cycle. */
      .lobe-stroke {{
        animation: lstroke 6s ease-in-out infinite;
        stroke-dashoffset: 100;
        opacity: 0;
      }}
      @keyframes lstroke {{
        0%   {{ stroke-dashoffset: 100; opacity: 0; }}
        16%  {{ stroke-dashoffset: 0;   opacity: 1; }}
        26%  {{ stroke-dashoffset: 0;   opacity: 1; }}
        43%  {{ stroke-dashoffset:-100; opacity: 0; }}
        100% {{ stroke-dashoffset:-100; opacity: 0; }}
      }}
      .ls-frontal    {{ animation-delay: 0s; }}
      .ls-parietal   {{ animation-delay: 1s; }}
      .ls-occipital  {{ animation-delay: 2s; }}
      .ls-temporal   {{ animation-delay: 3s; }}
      .ls-cerebellum {{ animation-delay: 4s; }}
      .ls-brainstem  {{ animation-delay: 5s; }}
      .lobe-arc {{
        stroke-dasharray: 4 22;
        animation: arcflow 1.6s linear infinite, arcfade 2.4s ease-in-out infinite;
        stroke-opacity: 0;
      }}
      @keyframes arcflow {{ to {{ stroke-dashoffset: -26; }} }}
      @keyframes arcfade {{
        0%, 35%, 100% {{ stroke-opacity: 0; }}
        10%           {{ stroke-opacity: 0.85; }}
        20%           {{ stroke-opacity: 0.45; }}
      }}
      .particle {{ animation: pdrift 14s ease-in-out infinite; transform-box: fill-box; }}
      @keyframes pdrift {{
        0%,100% {{ opacity: 0.18; transform: translate(0, 0); }}
        25%      {{ opacity: 0.55; transform: translate(8px, -10px); }}
        50%      {{ opacity: 0.32; transform: translate(-4px, -22px); }}
        75%      {{ opacity: 0.60; transform: translate(-12px, -8px); }}
      }}
      .p1{{animation-delay:0s;animation-duration:14s}} .p2{{animation-delay:1.5s;animation-duration:18s}}
      .p3{{animation-delay:3s;animation-duration:11s}} .p4{{animation-delay:4.5s;animation-duration:15s}}
      .p5{{animation-delay:6s;animation-duration:13s}} .p6{{animation-delay:7.5s;animation-duration:16s}}
      .p7{{animation-delay:2s;animation-duration:12s}} .p8{{animation-delay:3.5s;animation-duration:17s}}
      .p9{{animation-delay:5s;animation-duration:14s}} .p10{{animation-delay:6.5s;animation-duration:11s}}
      .p11{{animation-delay:0.5s;animation-duration:19s}} .p12{{animation-delay:8s;animation-duration:13s}}
      .p13{{animation-delay:1s;animation-duration:15s}} .p14{{animation-delay:2.5s;animation-duration:18s}}
      .p15{{animation-delay:9s;animation-duration:12s}} .p16{{animation-delay:4s;animation-duration:16s}}
      .constellation-line {{
        animation: clFade 8s ease-in-out infinite;
      }}
      @keyframes clFade {{
        0%, 100% {{ stroke-opacity: 0; }}
        50%      {{ stroke-opacity: 0.30; }}
      }}
      .cl1{{animation-delay:0s}}    .cl2{{animation-delay:0.6s}}
      .cl3{{animation-delay:1.2s}}  .cl4{{animation-delay:1.8s}}
      .cl5{{animation-delay:2.4s}}  .cl6{{animation-delay:3.0s}}
      .cl7{{animation-delay:3.6s}}  .cl8{{animation-delay:4.2s}}
      .cl9{{animation-delay:4.8s}}  .cl10{{animation-delay:5.4s}}
      .cl11{{animation-delay:6.0s}} .cl12{{animation-delay:6.6s}}
      .cl13{{animation-delay:7.2s}} .cl14{{animation-delay:7.8s}}
      .cl15{{animation-delay:0.3s}} .cl16{{animation-delay:1.5s}}
      .far-star {{
        animation-name: starTwinkle;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
      }}
      .fs8  {{ animation-duration:  8s; }}
      .fs10 {{ animation-duration: 10s; }}
      .fs12 {{ animation-duration: 12s; }}
      .fs14 {{ animation-duration: 14s; }}
      @keyframes starTwinkle {{
        0%, 100% {{ opacity: 0.20; }}
        50%      {{ opacity: 0.85; }}
      }}
      .dna {{
        opacity: 0;
        animation: dnaFade 16s ease-in-out infinite;
        transform-origin: center;
        transform-box: fill-box;
      }}
      @keyframes dnaFade {{
        0%, 100% {{ opacity: 0; }}
        10%      {{ opacity: 0; }}
        25%      {{ opacity: 0.85; }}
        50%      {{ opacity: 0.85; }}
        65%      {{ opacity: 0; }}
      }}
      .dna-strand {{
        animation: dnaDraw 16s ease-in-out infinite;
      }}
      @keyframes dnaDraw {{
        0%   {{ stroke-dashoffset: 100; }}
        25%  {{ stroke-dashoffset: 0; }}
        50%  {{ stroke-dashoffset: 0; }}
        65%  {{ stroke-dashoffset: -100; }}
        100% {{ stroke-dashoffset: -100; }}
      }}
    ]]></style>
  </defs>

  <rect width="1400" height="900" fill="url(#bgRadial)"/>
  {('''<rect width="1400" height="900" fill="url(#bgAura)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; 100,80; -60,40; 0,0" dur="40s" repeatCount="indefinite"/>
  </rect>''') if atm.show_aura else ""}
  {('''<!-- Far star field: 30 dim points twinkling at deep-space distance.
       Each star uses a CSS class fs8/fs10/fs12/fs14 for varied twinkle speed. -->
  <g class="stars">
  ''' + chr(10).join("    " + s for s in far_stars) + '''
  </g>''') if atm.show_aura else ""}

  {('''<!-- Nebula clouds: 4 large blurred radial gradients drifting slowly.
       More organic than aurora bands; adds color depth behind the brain. -->
  <g class="nebulae">
  ''' + chr(10).join("    " + nb for nb in nebula_blocks) + '''
  </g>''') if atm.show_aura else ""}

  {('''<!-- DNA helix symbols at canvas corners — fade in/out + draw in
       on staggered 16s timers. 1-2 visible at any moment, others hidden. -->
  <g class="dna-helixes">
  ''' + chr(10).join("    " + db for db in dna_blocks) + '''
  </g>''') if atm.show_aura else ""}

  {('''<!-- Aurora bands: 3 large soft radial gradients drifting across the canvas
       on staggered timers. Replaces the old turbulence plasma fog with smooth
       color flow that reads as atmospheric light, not noise. -->
  <g class="aurora">
    <rect x="-200" y="-200" width="900" height="900" fill="url(#aurora_a)">
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 200,150; 0,0" dur="28s" repeatCount="indefinite"/>
    </rect>
    <rect x="700" y="200" width="900" height="900" fill="url(#aurora_b)">
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; -180,-120; 0,0" dur="35s" repeatCount="indefinite"/>
    </rect>
    <rect x="200" y="500" width="900" height="900" fill="url(#aurora_c)">
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 160,-80; 0,0" dur="31s" repeatCount="indefinite"/>
    </rect>
  </g>''') if atm.show_aura else ""}

  {('''<!-- Constellation lines: thin links between nearby particles, fading in/out
       on staggered timers. Reads as a neural-web behind the brain. -->
  <g class="constellation">
  ''' + chr(10).join("    " + ln for ln in constellation_lines) + '''
  </g>''') if atm.show_particles else ""}

  {('''<!-- Light streaks: 5 thin diagonal lines that traverse the canvas on
       staggered timers, mimicking meteors / lens flares. Each one fires for
       3s then waits 10-13s before repeating. -->
  <g class="streaks">
    <line x1="-100" y1="200"  x2="-50"  y2="220"  stroke="#EC4899" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="0s;13s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="0s;13s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="0s;13s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="450"  x2="-50"  y2="470"  stroke="#A78BFA" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="2s;15s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="2s;15s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="2s;15s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="650"  x2="-50"  y2="670"  stroke="#22D3EE" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="5s;18s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="5s;18s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="5s;18s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="100"  x2="-50"  y2="120"  stroke="#EC4899" stroke-width="1.2"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="8s;21s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="8s;21s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="8s;21s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="780"  x2="-50"  y2="800"  stroke="#A78BFA" stroke-width="1.2"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="11s;24s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="11s;24s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="11s;24s" repeatCount="indefinite"/>
    </line>
  </g>''') if atm.show_particles else ""}

  {('''<!-- Ambient particle drift — atmospheric depth behind the brain -->
  <g fill="''' + p_accent_b + '''">
    <circle cx="120"  cy="180" r="1.8" class="particle p1"/>
    <circle cx="260"  cy="540" r="1.4" class="particle p2"/>
    <circle cx="380"  cy="120" r="2.0" class="particle p3" fill="''' + p_accent_a + '''"/>
    <circle cx="420"  cy="760" r="1.2" class="particle p4"/>
    <circle cx="560"  cy="380" r="1.6" class="particle p5" fill="''' + p_accent_a + '''"/>
    <circle cx="700"  cy="220" r="2.2" class="particle p6"/>
    <circle cx="780"  cy="700" r="1.4" class="particle p7" fill="''' + p_secondary + '''"/>
    <circle cx="900"  cy="160" r="1.8" class="particle p8"/>
    <circle cx="980"  cy="520" r="1.6" class="particle p9" fill="''' + p_accent_a + '''"/>
    <circle cx="1080" cy="340" r="2.0" class="particle p10"/>
    <circle cx="1180" cy="780" r="1.4" class="particle p11"/>
    <circle cx="1260" cy="240" r="1.8" class="particle p12" fill="''' + p_secondary + '''"/>
    <circle cx="160"  cy="780" r="1.6" class="particle p13"/>
    <circle cx="340"  cy="660" r="1.2" class="particle p14" fill="''' + p_accent_a + '''"/>
    <circle cx="640"  cy="80"  r="1.8" class="particle p15"/>
    <circle cx="1320" cy="500" r="1.4" class="particle p16"/>
  </g>''') if atm.show_particles else ""}

  <!-- Title -->
  <text x="700" y="50" class="t-tag" text-anchor="middle">⏵ NEURAL · SKILL · ATLAS · v1.0 ⏴</text>
  <text x="700" y="86" class="t-display" text-anchor="middle">{name}'s Skill Brain</text>

  <!-- Leader lines (drawn behind brain) -->
  <g fill="none">
    {chr(10).join("    " + ln for ln in region_lines)}
  </g>

  <!-- Data packets — small dots traveling card-to-brain along each leader path
       via SMIL animateMotion. Two per line, half-period staggered, fade in/out
       so they don't pop at the endpoints. Reads as continuous data flow. -->
  <g>
    {chr(10).join("    " + dp for dp in data_packets)}
  </g>

  <!-- The neon brain (Wikimedia anatomical, recolored, centered, optionally
       3D-wobbling). All endpoint decorations live INSIDE the wobble group so
       they track the brain anatomy as it moves: per-region color glows tint
       each lobe area in its card's color (mix-blend-mode: screen), halo rings
       wobble around their dots, micro-cells pulse like synaptic firing
       throughout the brain interior. atm.show_halos and atm.show_particles
       gate the optional layers. -->
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        {brain_content}
        {chr(10).join("        " + rg for rg in region_glows)}
        <g class="lobe-stroke-layer" filter="url(#electricGlow)">
        {chr(10).join("          " + lso for lso in lobe_stroke_overlay)}
        </g>
        <g class="arc-network" filter="url(#electricGlow)">
        {chr(10).join("          " + la for la in lobe_arcs)}
        {chr(10).join("          " + mc for mc in micro_cells)}
        </g>
        {chr(10).join("        " + h for h in halos) if atm.show_halos else ""}
        {chr(10).join("        " + sd for sd in spark_dots)}
      </g>
    </g>
  </g>

  <!-- Region labels -->
  {chr(10).join("  " + b for b in region_blocks)}
</svg>
"""


# ── Public API ───────────────────────────────────────────────────────────
def build(config: Config, output: str | Path) -> Path:
    """Build the anatomical neon brain SVG and write it to ``output``."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load the cached source SVG from package data
    src_text = (
        resources.files("cortex.assets").joinpath("brain-source.svg").read_text(encoding="utf-8")
    )

    # Pull just the inner brain group content (paths without the outer <g> wrapper —
    # the wrapper SVG provides its own transform group around this content).
    brain_group = _extract_g_by_id(src_text, "brain")

    # Recolor with the user's palette
    palette = (
        resolve_palette(config.brand.palette)
        if config.brand.palette in {"neon-rainbow", "monochrome", "cyberpunk", "minimal", "retro"}
        else config.brand.colors.model_dump()
    )
    recolored = _recolor(brain_group, palette["primary"], palette["secondary"])

    # Compose into the wrapper
    svg = _compose_wrapper(recolored, config)
    output_path.write_text(svg, encoding="utf-8")

    return output_path
