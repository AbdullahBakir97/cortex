"""Custom GitHub icon — pulsing brand-glow halo around an orange Octocat disc.

Tiny standalone widget. Brand colors come from config.brand.colors so the
icon always matches the rest of the profile palette.
"""

from __future__ import annotations

from pathlib import Path

from ..schema import Config


def build(config: Config, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    secondary = config.brand.colors.secondary  # default #FF652F (orange)
    bg = config.brand.colors.background  # default #0D1117 (dark blue-black)
    user = config.identity.github_user

    # Jewel-tone halo color — same palette as the brain DNA + aurora flow,
    # so the icon ties visually to the rest of the composition. (Replaces the
    # previous brand-primary halo, which was always saturated red and clashed
    # with the rest of the polished widgets.)
    halo = "#7B5EAA"  # violet (jewel)

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96" role="img" aria-label="GitHub @{user}">\n'
        "  <defs>\n"
        f'    <radialGradient id="ghGlow" cx="50%" cy="50%" r="50%">\n'
        f'      <stop offset="0%"   stop-color="{halo}" stop-opacity="0.85"/>\n'
        f'      <stop offset="55%"  stop-color="{halo}" stop-opacity="0.30"/>\n'
        f'      <stop offset="100%" stop-color="{halo}" stop-opacity="0"/>\n'
        "    </radialGradient>\n"
        f'    <radialGradient id="ghDisc" cx="38%" cy="32%" r="70%">\n'
        f'      <stop offset="0%"   stop-color="#FF8A50"/>\n'
        f'      <stop offset="100%" stop-color="{secondary}"/>\n'
        "    </radialGradient>\n"
        "    <filter id=\"ghGlowSoft\" x=\"-30%\" y=\"-30%\" width=\"160%\" height=\"160%\">\n"
        '      <feGaussianBlur stdDeviation="1.5"/>\n'
        "    </filter>\n"
        "  </defs>\n"
        '  <circle cx="48" cy="48" r="38" fill="url(#ghGlow)" filter="url(#ghGlowSoft)">\n'
        # Ease-in-out keyTimes/keySplines for smoother breathing pulse.
        '    <animate attributeName="r"       values="32;44;32"     dur="3.6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>\n'
        '    <animate attributeName="opacity" values="0.55;1;0.55" dur="3.6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>\n'
        "  </circle>\n"
        f'  <circle cx="48" cy="48" r="28" fill="url(#ghDisc)" stroke="{halo}" stroke-width="1.5" stroke-opacity="0.7"/>\n'
        '  <g transform="translate(32,32) scale(2)">\n'
        f'    <path fill="{bg}" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>\n'
        "  </g>\n"
        "</svg>\n"
    )
    out.write_text(svg, encoding="utf-8")
    return out
