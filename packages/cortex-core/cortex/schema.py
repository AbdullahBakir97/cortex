"""Pydantic v2 models for the cortex.yml config file.

These models give us:
  • Runtime validation with helpful error messages
  • IDE autocomplete (when paired with cortex-schema/schema.json)
  • A single source of truth for what the config DSL accepts
  • Forward-compatible schema versioning via the top-level ``version`` field
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# ── Schema versioning ────────────────────────────────────────────────────
# Bump on breaking changes. ``Config.from_yaml`` rejects mismatched configs
# with a helpful migration hint pointing to the docs.
CURRENT_SCHEMA_VERSION = 1


class _Strict(BaseModel):
    """Base for all config models — forbid unknown keys to catch typos early."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


# ── Identity ─────────────────────────────────────────────────────────────
class Socials(_Strict):
    linkedin: str | None = None
    telegram: str | None = None
    instagram: str | None = None
    twitter: str | None = None


class Identity(_Strict):
    name: str
    github_user: str = Field(..., min_length=1, max_length=39, description="GitHub username")
    tagline: str = ""
    location: str = ""
    pronouns: str = ""
    email: str = ""
    socials: Socials = Field(default_factory=Socials)


# ── Brand ────────────────────────────────────────────────────────────────
PaletteName = Literal["neon-rainbow", "monochrome", "cyberpunk", "minimal", "retro"]


class BrandColors(_Strict):
    primary: str = "#F90001"
    secondary: str = "#FF652F"
    accent_a: str = "#22D3EE"
    accent_b: str = "#A78BFA"
    accent_c: str = "#FFD23F"
    accent_d: str = "#34D399"
    background: str = "#0D1117"


class Typography(_Strict):
    display: str = "Inter"
    mono: str = "JetBrains Mono"
    # Global font-size multiplier — proportionally scales every widget's text.
    # Useful for users embedding Cortex in narrower contexts (e.g. organisation
    # READMEs). 1.0 = builder defaults, 0.85 = compact, 1.15 = comfortable.
    scale: float = Field(default=1.0, ge=0.5, le=1.5)


class Animations(_Strict):
    enabled: bool = True
    intensity: Literal["off", "subtle", "medium", "high"] = "high"
    # Global animation duration multiplier. >1.0 slows everything down
    # (good for accessibility / reduced-motion preferences); <1.0 speeds up.
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class Brand(_Strict):
    palette: PaletteName = "neon-rainbow"
    colors: BrandColors = Field(default_factory=BrandColors)
    typography: Typography = Field(default_factory=Typography)
    animations: Animations = Field(default_factory=Animations)


# ── Brain ────────────────────────────────────────────────────────────────
MasteryLevel = Literal["EXPERT", "ADVANCED", "PROFICIENT", "GROWING"]


class StatEntry(_Strict):
    num: str
    label: str


class BrainRegion(_Strict):
    domain: str
    tools: list[str] = Field(default_factory=list)
    # Optional visual metadata — blank values fall back to domain-keyed presets in
    # cortex.builders.tech_cards (so simple configs still get a polished card).
    emoji: str = ""
    caption: str = ""
    tagline: str = ""
    mastery: MasteryLevel | None = None
    stats: list[StatEntry] = Field(default_factory=list, max_length=3)


class BrainRegions(_Strict):
    """Six anatomical regions, each mapped to a skill domain."""

    frontal: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="Backend"))
    parietal: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="Architecture"))
    occipital: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="Frontend"))
    temporal: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="Data Layer"))
    cerebellum: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="DevOps"))
    brainstem: BrainRegion = Field(default_factory=lambda: BrainRegion(domain="AI & Data"))


class BrainThreeD(_Strict):
    enabled: bool = True
    auto_rotate: bool = True
    custom_domain: str | None = None  # Pro: brain.you.dev


class BrainHeatmap(_Strict):
    """Pro feature: lobes glow brighter where you actually contribute."""

    enabled: bool = False


class BrainAtmosphere(_Strict):
    """Optional ambient-effect toggles for the anatomical brain widget.

    Each flag controls one visual layer added in the brain atmosphere pass.
    Defaults match the v0.3 reference look; turn flags off for a cleaner,
    more minimal brain (useful for users on slower connections or with
    reduced-motion accessibility preferences).
    """

    show_particles: bool = True  # 16 ambient drifting particles behind brain
    show_aura: bool = True  # pink/purple radial glow centered on canvas
    show_halos: bool = True  # static rings at leader-line endpoints
    wobble: bool = True  # 3D scaleX/skewY animation on brain anatomy


class Brain(_Strict):
    enabled: bool = True
    source: Literal["wikimedia", "abstract", "custom"] = "wikimedia"
    regions: BrainRegions = Field(default_factory=BrainRegions)
    three_d: BrainThreeD = Field(default_factory=BrainThreeD)
    heatmap: BrainHeatmap = Field(default_factory=BrainHeatmap)
    atmosphere: BrainAtmosphere = Field(default_factory=BrainAtmosphere)


# ── Typing ───────────────────────────────────────────────────────────────
class TypingHeader(_Strict):
    enabled: bool = True
    languages: list[str] = Field(default_factory=lambda: ["en"])
    lines_per_language: int = Field(default=10, ge=1, le=30)
    cycle: Literal["fast", "medium", "slow"] = "medium"


class TypingBody(_Strict):
    enabled: bool = True
    lines: int = Field(default=30, ge=3, le=100)
    include: list[Literal["personal", "generic"]] = Field(
        default_factory=lambda: ["personal", "generic"]
    )


class Typing(_Strict):
    header: TypingHeader = Field(default_factory=TypingHeader)
    about: TypingBody = Field(default_factory=lambda: TypingBody(lines=30))
    motto: TypingBody = Field(default_factory=lambda: TypingBody(lines=30))


# ── Cards ────────────────────────────────────────────────────────────────
class TechStackCard(_Strict):
    enabled: bool = True
    show_stats: bool = True
    categories: list[str] | None = None  # auto-inferred from brain.regions


class FocusTile(_Strict):
    project: str
    status: Literal["ACTIVE", "SHIPPING", "EXPLORING", "MAINTAINING", "BUILDING"] = "ACTIVE"
    accent: Literal["red", "orange", "green", "gold", "cyan", "purple"] = "red"
    emoji: str = ""
    description: str = ""  # word-wrapped to ≤3 lines
    tech: list[str] = Field(default_factory=list, max_length=4)


class CurrentFocusCard(_Strict):
    enabled: bool = True
    tiles: list[FocusTile] = Field(default_factory=list, max_length=6)


class YearEntry(_Strict):
    year: int = Field(..., ge=2008, le=2100)
    label: str = ""  # e.g. "ORIGIN", "GROWTH", "CURRENT YEAR"
    headline: str = ""  # e.g. "First Steps"
    bullets: list[str] = Field(default_factory=list, max_length=8)
    stats: list[StatEntry] = Field(default_factory=list, max_length=3)


class YearlyHighlightsCard(_Strict):
    enabled: bool = True
    start_year: int = Field(default=2023, ge=2008)
    bullets_per_year: int = Field(default=3, ge=1, le=8)
    years: list[YearEntry] = Field(default_factory=list, max_length=6)


# ── Header / Footer banner ───────────────────────────────────────────────
# Capsule-render replacement: animated banner with configurable shape, palette,
# and animation style. Renders as a wide SVG used at the top/bottom of the
# README. Colors default to the jewel-tone palette that ties to the brain
# DNA / aurora / divider; can be overridden via `colors` list.
class BannerConfig(_Strict):
    enabled: bool = True
    shape: Literal["wave", "slice", "rect"] = "wave"
    title: str = ""
    subtitle: str = ""
    # Banner height in px. Header default 220, footer 160 — but each spec
    # overrides this default via factory below.
    height: int = 220
    # Optional explicit hex colors (3-5 stops). Empty → use jewel-tone defaults.
    colors: list[str] = Field(default_factory=list)
    # Animation style. "drift" = gradient stops translate left↔right.
    # "pulse" = opacity breathes. "static" = no animation.
    animation: Literal["drift", "pulse", "static"] = "drift"


def _default_footer() -> BannerConfig:
    return BannerConfig(height=160, title="", subtitle="")


class BadgeItem(_Strict):
    """Single badge spec inside the badges widget.

    ``icon`` picks a built-in monogram + brand color from cortex.icons.
    Pass ``icon_svg`` (raw SVG path ``d`` string) for full custom iconography
    — that overrides the monogram. ``color`` overrides the auto-resolved
    brand color. ``value`` is an optional sublabel below the main label
    (e.g. "Senior", "85%", "Certified").
    """

    label: str
    icon: str = ""
    icon_svg: str = ""
    color: str = ""
    value: str = ""
    href: str = ""


class BadgesConfig(_Strict):
    """Compact tech / skill / achievement badges widget.

    Designed as the "skills strip" most profile READMEs need. Fills the gap
    between the brain (everything) and tech_cards (deep dive on 6 skills).
    """

    enabled: bool = False
    # Visual shape of each badge.
    shape: Literal["pill", "hex", "shield", "circle"] = "pill"
    # Layout strategy. ``row`` wraps to width; ``grid`` uses ``columns``;
    # ``marquee`` scrolls horizontally on a single line.
    layout: Literal["row", "grid", "marquee"] = "row"
    # Columns when layout=grid.
    columns: int = 6
    # Animation. Combinable in spirit but only one is rendered at a time.
    animation: Literal["stagger", "shimmer", "pulse", "static"] = "stagger"
    # The list of badges. 1-30 items.
    items: list[BadgeItem] = Field(default_factory=list)


# ── Tier-1 widgets ───────────────────────────────────────────────────────


class StarSpec(_Strict):
    """Single star in the Skill Galaxy."""

    label: str
    color: str = ""  # auto from cortex jewel-tone if empty
    size: int = 4  # base radius in px (2-12)


class GalaxyConfig(_Strict):
    """Skill Galaxy / Constellation widget — stars + connections drifting in space."""

    enabled: bool = False
    title: str = ""
    stars: list[StarSpec] = Field(default_factory=list)
    # Pairs of star labels; each pair draws a faint connecting line.
    connections: list[list[str]] = Field(default_factory=list)
    background: Literal["deep-space", "nebula", "void"] = "deep-space"
    twinkle_speed: float = 1.0
    drift_speed: float = 1.0
    height: int = 540


class SynthwaveConfig(_Strict):
    """Synthwave Horizon hero banner — receding grid, sun, mountains."""

    enabled: bool = False
    title: str = ""
    subtitle: str = ""
    height: int = 320
    palette: Literal["sunset", "neon", "miami", "outrun"] = "outrun"
    show_grid: bool = True
    show_sun: bool = True
    show_mountains: bool = True


class RadarAxis(_Strict):
    label: str
    value: float = 50.0  # 0-100


class RadarConfig(_Strict):
    """Skill Radar / Polar Chart — translucent polygon over polar grid."""

    enabled: bool = False
    title: str = ""
    axes: list[RadarAxis] = Field(default_factory=list)
    max_value: float = 100.0
    color: str = ""  # default jewel-tone violet
    breathe: bool = True
    height: int = 480


class MetroStation(_Strict):
    label: str
    year: int = 0  # for x-position; 0 = auto-evenly-spaced
    is_current: bool = False


class MetroLine(_Strict):
    name: str
    color: str = ""
    stations: list[MetroStation] = Field(default_factory=list)


class RoadmapConfig(_Strict):
    """Code Roadmap — metro/subway-style multi-line career map."""

    enabled: bool = False
    title: str = ""
    lines: list[MetroLine] = Field(default_factory=list)
    show_legend: bool = True
    height: int = 360


# ── Tier-2 widgets ───────────────────────────────────────────────────────


class HeatmapConfig(_Strict):
    """Activity Heatmap — 7x52 contribution grid with neon glow."""

    enabled: bool = False
    weeks: int = 52
    # Optional intensity matrix (rows=days 0..6, cols=weeks). Empty → mock.
    data: list[list[int]] = Field(default_factory=list)
    palette: Literal["neon-green", "neon-cyan", "neon-rainbow", "rose"] = "neon-green"
    glow: bool = True
    height: int = 200


class StatCube(_Strict):
    label: str
    value: str
    color: str = ""


class CubesConfig(_Strict):
    """3D Stat Cubes — isometric blocks orbiting slowly."""

    enabled: bool = False
    cubes: list[StatCube] = Field(default_factory=list)
    orbit: bool = True
    height: int = 280


class TrophySpec(_Strict):
    label: str
    date: str = ""
    glyph: str = ""  # single emoji or 1-2 letter code
    color: str = ""


class TrophiesConfig(_Strict):
    """Achievement Wall / Trophy Cabinet — bevelled cabinet with mounted trophies."""

    enabled: bool = False
    title: str = ""
    trophies: list[TrophySpec] = Field(default_factory=list)
    columns: int = 4
    height: int = 360


class DnaConfig(_Strict):
    """Code DNA Helix — twin spiral strands with language base-pairs."""

    enabled: bool = False
    title: str = ""
    # Top languages to encode as base pairs. Each shows a color band on the
    # rungs between the two strands.
    languages: list[str] = Field(default_factory=list)
    # Optional explicit colors per language (paired by index). Empty entries
    # fall back to jewel-tone palette.
    colors: list[str] = Field(default_factory=list)
    height: int = 360


class GlobePin(_Strict):
    label: str
    # Polar coordinates on the globe — angles in degrees.
    # lon: 0 = front center; +ve = right (east). Range: -180..180.
    # lat: 0 = equator; +ve = north. Range: -90..90.
    lon: float = 0.0
    lat: float = 0.0
    color: str = ""


class GlobeConfig(_Strict):
    """Stylized 2D globe with neon contribution pins."""

    enabled: bool = False
    title: str = ""
    pins: list[GlobePin] = Field(default_factory=list)
    rotate: bool = True
    height: int = 480


class ParticleSpec(_Strict):
    label: str
    weight: float = 1.0  # relative size; 0.5 - 3.0 typical
    color: str = ""


class ParticlesConfig(_Strict):
    """Drifting particle / tag cloud — items orbit a center point with physics."""

    enabled: bool = False
    title: str = ""
    items: list[ParticleSpec] = Field(default_factory=list)
    height: int = 420


class NowPlayingConfig(_Strict):
    """Spotify-style 'currently coding in' card with waveform + progress bar."""

    enabled: bool = False
    activity: str = "Coding"  # e.g. "Coding", "Building", "Debugging"
    language: str = "Python"  # the "track title"
    project: str = ""  # the "artist line" — repo or product name
    progress: float = 0.62  # 0.0 - 1.0; bar fill ratio
    elapsed: str = "1:24"
    duration: str = "—"
    color: str = ""  # accent color; default jewel-tone violet
    height: int = 220


class ShowcaseConfig(_Strict):
    """Tuning for the auto-generated CORTEX:SHOWCASE block in the README.

    For most users, the defaults work — variant SVGs are written to
    ``assets/variants/`` of their <user>/<user> profile repo and the showcase
    points to that path. Override ``base_url`` only when assets live somewhere
    non-standard (e.g. the cortex project's own marketing README, where
    variants ship in ``examples/rendered/extreme/variants/``).
    """

    # Override the URL prefix the showcase uses for variant image src attrs.
    # Empty → default ``https://raw.githubusercontent.com/<user>/<user>/main/assets``.
    base_url: str = ""


class Cards(_Strict):
    tech_stack: TechStackCard = Field(default_factory=TechStackCard)
    current_focus: CurrentFocusCard = Field(default_factory=CurrentFocusCard)
    yearly_highlights: YearlyHighlightsCard = Field(default_factory=YearlyHighlightsCard)
    header: BannerConfig = Field(default_factory=BannerConfig)
    footer: BannerConfig = Field(default_factory=_default_footer)
    badges: BadgesConfig = Field(default_factory=BadgesConfig)
    galaxy: GalaxyConfig = Field(default_factory=GalaxyConfig)
    synthwave: SynthwaveConfig = Field(default_factory=SynthwaveConfig)
    radar: RadarConfig = Field(default_factory=RadarConfig)
    roadmap: RoadmapConfig = Field(default_factory=RoadmapConfig)
    heatmap: HeatmapConfig = Field(default_factory=HeatmapConfig)
    cubes: CubesConfig = Field(default_factory=CubesConfig)
    trophies: TrophiesConfig = Field(default_factory=TrophiesConfig)
    dna: DnaConfig = Field(default_factory=DnaConfig)
    globe: GlobeConfig = Field(default_factory=GlobeConfig)
    particles: ParticlesConfig = Field(default_factory=ParticlesConfig)
    now_playing: NowPlayingConfig = Field(default_factory=NowPlayingConfig)
    showcase: ShowcaseConfig = Field(default_factory=ShowcaseConfig)


# ── Auto-update markers ──────────────────────────────────────────────────
class PageSpeedConfig(_Strict):
    enabled: bool = False
    url: str = ""


class WakaTimeConfig(_Strict):
    enabled: bool = False


class Markers(_Strict):
    activity: bool = True
    latest_releases: bool = True
    quote_of_the_day: bool = True
    gitgraph: bool = True
    highlights_stats: bool = True
    skyline_grid: bool = True
    city_grid: bool = True
    stl_links: bool = True
    gitcity_links: bool = True
    # Showcase: auto-generated "What Cortex Generates" section listing every
    # widget with preview + config snippet. Targets a CORTEX:SHOWCASE block
    # in the user's README. Disable if your README documents widgets manually.
    showcase: bool = True
    pagespeed: PageSpeedConfig = Field(default_factory=PageSpeedConfig)
    wakatime: WakaTimeConfig = Field(default_factory=WakaTimeConfig)


class AutoUpdate(_Strict):
    schedule: str = "0 6 * * *"
    markers: Markers = Field(default_factory=Markers)


# ── Contributions ────────────────────────────────────────────────────────
class SkylinesConfig(_Strict):
    years: list[int] | None = None  # None = auto-extend from start_year
    stl: bool = True


class CitiesConfig(_Strict):
    years: list[int] | None = None


class Contributions(_Strict):
    snake: bool = True
    skylines: SkylinesConfig = Field(default_factory=SkylinesConfig)
    cities: CitiesConfig = Field(default_factory=CitiesConfig)
    profile_3d: bool = True


# ── Pro features (gated behind subscription in v2+) ──────────────────────
class ProFeatures(_Strict):
    ai_portrait: bool = False
    skill_dna_strand: bool = False
    project_cards: bool = False
    digital_twin_chat: bool = False
    constellation: bool = False
    sound_reactive: bool = False
    custom_domain: str | None = None
    analytics: bool = False


# ══════════════════════════════════════════════════════════════════════════
# Top-level Config
# ══════════════════════════════════════════════════════════════════════════
class Config(_Strict):
    """The complete cortex.yml schema, validated at load time."""

    version: int = Field(default=CURRENT_SCHEMA_VERSION, ge=1, le=99)
    identity: Identity
    brand: Brand = Field(default_factory=Brand)
    brain: Brain = Field(default_factory=Brain)
    typing: Typing = Field(default_factory=Typing)
    cards: Cards = Field(default_factory=Cards)
    auto_update: AutoUpdate = Field(default_factory=AutoUpdate)
    contributions: Contributions = Field(default_factory=Contributions)
    pro: ProFeatures = Field(default_factory=ProFeatures)

    @field_validator("version")
    @classmethod
    def _check_schema_version(cls, v: int) -> int:
        if v != CURRENT_SCHEMA_VERSION:
            raise ValueError(
                f"cortex.yml schema version is {v}, but this Cortex release "
                f"expects version {CURRENT_SCHEMA_VERSION}. See the migration "
                f"guide at https://docs.cortex.dev/migrations."
            )
        return v

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load and validate a cortex.yml file."""
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        if "version" not in raw:
            raw["version"] = CURRENT_SCHEMA_VERSION
        return cls.model_validate(raw)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls.model_validate(data)
