"""3D Stat Cubes — isometric blocks displaying numeric stats.

Each cube has 3 visible faces (top, front, right). The top face shows a
label, the front face shows the value. Cubes are laid out in a row with
optional gentle orbit (CSS rotate animation per cube).
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from ..schema import Config, CubesConfig


def _x(s: str) -> str:
    return _xml_escape(s, {"'": "&apos;", '"': "&quot;"})


WIDTH = 1200

# Isometric projection: 30° angles. dx, dy per axis.
ISO_DX = 0.866  # cos(30°)
ISO_DY = 0.5  # sin(30°)


def _cube(
    cx: float, cy: float, size: int, color: str, idx: int
) -> tuple[str, dict[str, list[tuple[float, float]]]]:
    """Compute the 3 visible cube faces in isometric projection.

    Returns (svg_fragment, face_polys) where face_polys maps "top"/"front"/"right"
    to its 4 corner points (used for label placement).
    """
    s = size

    # Project a unit-cube corner (x,y,z in {0,1}) into 2D isometric space.
    # x = right axis, y = depth (into screen), z = up.
    def proj(x: float, y: float, z: float) -> tuple[float, float]:
        return (cx + (x - y) * s * ISO_DX, cy + (x + y) * s * ISO_DY - z * s)

    # 6 corners we need (the 2 hidden bottom-back-left corners are unused).
    p000 = proj(0, 0, 0)
    p100 = proj(1, 0, 0)
    p010 = proj(0, 1, 0)
    p110 = proj(1, 1, 0)
    p001 = proj(0, 0, 1)
    p101 = proj(1, 0, 1)
    p011 = proj(0, 1, 1)
    p111 = proj(1, 1, 1)
    _ = p000, p110  # only used in face-corner lists below

    top_face = [p001, p101, p111, p011]  # top quad
    right_face = [p101, p100, p110, p111]  # right quad (going into screen)
    left_face = [p001, p011, p010, p000]  # left/front quad (visible front)

    def poly(pts: list[tuple[float, float]], fill: str, opacity: float = 1.0) -> str:
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        return f'<path d="{d}" fill="{fill}" fill-opacity="{opacity:.2f}" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1"/>'

    # 3 faces, brightest on top, mid front, dim side.
    svg = poly(top_face, color, 1.0) + poly(left_face, color, 0.72) + poly(right_face, color, 0.48)
    return svg, {"top": top_face, "front": left_face, "right": right_face}


def _render(config: Config) -> str:
    ccfg: CubesConfig = config.cards.cubes
    height = ccfg.height
    cubes = ccfg.cubes
    if not cubes:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
            'role="img" aria-label="Stat cubes (empty)"></svg>\n'
        )

    n = len(cubes)
    cube_size = 80
    spacing = (WIDTH - 80) / max(1, n)
    palette = ["#7B5EAA", "#FF6B9D", "#22D3EE", "#FFD23F", "#34D399", "#F90001"]

    parts: list[str] = []
    for i, c in enumerate(cubes):
        cx = 40 + spacing * i + spacing / 2
        cy = height / 2 + 30
        color = c.color or palette[i % len(palette)]
        cube_svg, faces = _cube(cx, cy, cube_size, color, i)

        # Centroid of each face for label placement.
        def centroid(face: list[tuple[float, float]]) -> tuple[float, float]:
            xs, ys = zip(*face, strict=True)
            return sum(xs) / len(xs), sum(ys) / len(ys)

        top_cx, top_cy = centroid(faces["top"])
        front_cx, front_cy = centroid(faces["front"])

        orbit_anim = ""
        if ccfg.orbit:
            orbit_anim = (
                '<animateTransform attributeName="transform" type="rotate" '
                f'from="-2 {cx:.1f} {cy:.1f}" to="2 {cx:.1f} {cy:.1f}" '
                f'dur="{4 + (i % 3)}s" repeatCount="indefinite" '
                'additive="sum" calcMode="linear" values="-2;2;-2"/>'
            )

        parts.append(
            f"<g>{orbit_anim}{cube_svg}</g>"
            f'<text x="{top_cx:.1f}" y="{top_cy + 2:.1f}" class="cb-label" '
            f'text-anchor="middle">{_x(c.label)}</text>'
            f'<text x="{front_cx:.1f}" y="{front_cy + 6:.1f}" class="cb-value" '
            f'text-anchor="middle">{_x(c.value)}</text>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}"
     viewBox="0 0 {WIDTH} {height}" preserveAspectRatio="xMidYMin meet"
     role="img" aria-label="3D stat cubes">
  <defs>
    <filter id="cb-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>
  <style><![CDATA[
    .cb-label {{ font-family: 'JetBrains Mono','SF Mono','Consolas',monospace; font-weight: 800; font-size: 11px; fill: #FFFFFF; fill-opacity: 0.92; letter-spacing: 0.18em; text-transform: uppercase; }}
    .cb-value {{ font-family: 'Inter','SF Pro Display',sans-serif; font-weight: 900; font-size: 22px; fill: #FFFFFF; }}
  ]]></style>
  <g filter="url(#cb-shadow)">
    {"".join(parts)}
  </g>
</svg>
"""


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(config), encoding="utf-8")
    return out
