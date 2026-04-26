"""End-to-end build determinism — same input → byte-equal output."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cortex.builders.brain import build
from cortex.schema import Config


@pytest.fixture(scope="module")
def extreme_config() -> Config:
    """Load the extreme example config — known-good kitchen-sink config."""
    repo_root = Path(__file__).resolve().parents[3]  # src/
    config_path = repo_root / "examples" / "extreme.yml"
    return Config.model_validate(yaml.safe_load(config_path.read_text(encoding="utf-8")))


def test_build_is_deterministic(tmp_path: Path, extreme_config: Config) -> None:
    """Two builds with the same config produce byte-identical SVG output."""
    out_a = tmp_path / "a.svg"
    out_b = tmp_path / "b.svg"
    build(extreme_config, out_a)
    build(extreme_config, out_b)
    assert out_a.read_bytes() == out_b.read_bytes()


def test_build_output_is_well_formed_xml(tmp_path: Path, extreme_config: Config) -> None:
    """Built SVG parses as valid XML."""
    import xml.etree.ElementTree as ET

    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    # Will raise ParseError if malformed
    tree = ET.parse(out)
    root = tree.getroot()
    assert root.tag.endswith("svg")


def test_no_legacy_source_hex_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """The five legacy source-SVG fill hexes must all be substituted."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    for legacy in ("fill:#fff0cd", "fill:#fdd99b", "fill:#d9bb7a", "fill:#ffffff", "fill:#816647"):
        assert legacy not in text.lower(), f"legacy fill {legacy} not substituted"


def test_no_legacy_gradient_ids_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """Only brainGrad_unified should remain — per-lobe gradients deleted in R6."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    # Truly legacy ids that must never appear
    for legacy in (
        'id="brainGrad"', 'id="brainGradAlt"', 'id="brainGrad_specular"',
        'id="brainGrad_frontal"', 'id="brainGrad_parietal"',
        'id="brainGrad_occipital"', 'id="brainGrad_temporal"',
        'id="brainGrad_cerebellum"', 'id="brainGrad_brainstem"',
    ):
        assert legacy not in text, f"legacy gradient {legacy} still in output"
    # Unified gradient must remain (carries the rose body color)
    assert 'id="brainGrad_unified"' in text


def test_overlay_layer_present_with_six_lobe_classes(tmp_path: Path, extreme_config: Config) -> None:
    """Stroke overlay must be wired in — one .ls-<lobe> class per lobe."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    assert 'class="lobe-stroke-layer"' in text
    for lobe in ("frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem"):
        assert f'ls-{lobe}' in text, f"missing overlay class for {lobe}"
