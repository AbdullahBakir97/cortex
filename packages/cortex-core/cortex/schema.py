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
