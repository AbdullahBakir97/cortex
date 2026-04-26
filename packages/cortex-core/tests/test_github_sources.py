"""Tests for cortex.sources.github — pure-data helpers + builder integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from cortex.builders import cubes, heatmap
from cortex.github_api import GitHubClient
from cortex.schema import (
    Brand,
    Cards,
    Config,
    CubesConfig,
    HeatmapConfig,
    Identity,
)
from cortex.sources.github import (
    _fmt_count,
    _intensity_for,
    contribution_grid_from_github,
    stats_cubes_from_github,
    top_languages_from_github,
)

# ── Pure helpers ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "n,expected",
    [
        (0, "0"),
        (42, "42"),
        (999, "999"),
        (1000, "1.0k"),
        (1234, "1.2k"),
        (8400, "8.4k"),
        (1_000_000, "1.0M"),
        (3_500_000, "3.5M"),
    ],
)
def test_fmt_count_compact(n: int, expected: str):
    assert _fmt_count(n) == expected


@pytest.mark.parametrize(
    "count,expected",
    [(0, 0), (1, 1), (2, 1), (3, 2), (7, 2), (8, 3), (15, 3), (16, 4), (100, 4)],
)
def test_intensity_for_buckets(count: int, expected: int):
    assert _intensity_for(count) == expected


# ── stats_cubes_from_github ─────────────────────────────────────────────


def test_stats_cubes_returns_fallback_when_no_token():
    """Anonymous client must NOT crash — degrades to placeholder cubes."""
    client = GitHubClient(user="x", token="")
    result = stats_cubes_from_github(client)
    assert len(result) == 5
    assert all(c.value == "—" for c in result)


def test_stats_cubes_returns_fallback_when_graphql_raises(monkeypatch):
    client = GitHubClient(user="x", token="fake-token")
    monkeypatch.setattr(
        client.__class__, "graphql", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    result = stats_cubes_from_github(client)
    assert all(c.value == "—" for c in result)


def test_stats_cubes_parses_real_shape(monkeypatch):
    """Given a realistic GraphQL response, every cube gets a formatted count."""
    fake_response: dict[str, Any] = {
        "user": {
            "pullRequests": {"totalCount": 1234},
            "contributionsCollection": {
                "totalCommitContributions": 8400,
                "totalIssueContributions": 87,
            },
            "starredRepositories": {"totalCount": 3142},
            "repositories": {"totalCount": 47},
        }
    }
    client = GitHubClient(user="x", token="fake")
    monkeypatch.setattr(client.__class__, "graphql", lambda *a, **kw: fake_response)
    result = stats_cubes_from_github(client)
    by_label = {c.label: c.value for c in result}
    assert by_label["PRs"] == "1.2k"
    assert by_label["Commits"] == "8.4k"
    assert by_label["Stars"] == "3.1k"
    assert by_label["Repos"] == "47"
    assert by_label["Issues"] == "87"


# ── contribution_grid_from_github ───────────────────────────────────────


def test_contribution_grid_returns_empty_without_token():
    """No token = no GraphQL = empty grid (heatmap builder will fall back to mock)."""
    client = GitHubClient(user="x", token="")
    assert contribution_grid_from_github(client) == []


def test_contribution_grid_parses_realistic_shape(monkeypatch):
    """Build a 2-week response, verify it lands in the right cells."""
    fake = {
        "user": {
            "contributionsCollection": {
                "contributionCalendar": {
                    "weeks": [
                        {
                            "contributionDays": [
                                {"weekday": 0, "contributionCount": 0},
                                {"weekday": 1, "contributionCount": 5},  # → 2
                                {"weekday": 2, "contributionCount": 20},  # → 4
                            ]
                        },
                        {
                            "contributionDays": [
                                {"weekday": 6, "contributionCount": 1},  # → 1
                            ]
                        },
                    ]
                }
            }
        }
    }
    client = GitHubClient(user="x", token="fake")
    monkeypatch.setattr(client.__class__, "graphql", lambda *a, **kw: fake)
    grid = contribution_grid_from_github(client, weeks=2)
    assert len(grid) == 7
    assert all(len(row) == 2 for row in grid)
    # Sun (0), week 0
    assert grid[0][0] == 0
    # Mon (1), week 0 — count 5 falls in 3..7 bucket = 2
    assert grid[1][0] == 2
    # Tue (2), week 0 — count 20 = bucket 4
    assert grid[2][0] == 4
    # Sat (6), week 1
    assert grid[6][1] == 1


def test_contribution_grid_handles_graphql_error(monkeypatch):
    client = GitHubClient(user="x", token="fake")
    monkeypatch.setattr(
        client.__class__, "graphql", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    assert contribution_grid_from_github(client) == []


# ── top_languages_from_github ────────────────────────────────────────────


def test_top_languages_aggregates_across_repos(monkeypatch):
    fake = {
        "user": {
            "repositories": {
                "nodes": [
                    {
                        "languages": {
                            "edges": [
                                {"size": 1000, "node": {"name": "Python", "color": "#3572A5"}},
                                {"size": 500, "node": {"name": "Shell", "color": "#89e051"}},
                            ]
                        }
                    },
                    {
                        "languages": {
                            "edges": [
                                {"size": 2500, "node": {"name": "Python", "color": "#3572A5"}},
                                {"size": 800, "node": {"name": "Rust", "color": "#dea584"}},
                            ]
                        }
                    },
                ]
            }
        }
    }
    client = GitHubClient(user="x", token="fake")
    monkeypatch.setattr(client.__class__, "graphql", lambda *a, **kw: fake)
    langs = top_languages_from_github(client, top_n=3)
    assert [lang["name"] for lang in langs] == ["Python", "Rust", "Shell"]
    # Python aggregated: 1000 + 2500 = 3500
    assert langs[0]["bytes"] == 3500


def test_top_languages_empty_without_token():
    assert top_languages_from_github(GitHubClient(user="x", token="")) == []


# ── End-to-end builder integration ──────────────────────────────────────


def _config(**cards_kwargs: object) -> Config:
    return Config(
        identity=Identity(name="Test User", github_user="test"),
        brand=Brand(),
        cards=Cards(**cards_kwargs),  # type: ignore[arg-type]
    )


def test_cubes_from_github_calls_source_and_renders(tmp_path: Path, monkeypatch):
    """from_github=True triggers the source call and the result lands in SVG."""
    import cortex.sources as sources_pkg
    from cortex.schema import StatCube

    monkeypatch.setattr(
        sources_pkg,
        "stats_cubes_from_github",
        lambda client: [
            StatCube(label="PRs", value="42"),
            StatCube(label="Stars", value="9001"),
        ],
    )
    cfg = _config(cubes=CubesConfig(enabled=True, from_github=True))
    text = cubes.build(cfg, tmp_path / "c.svg").read_text(encoding="utf-8")
    assert ">42<" in text
    assert ">9001<" in text


def test_heatmap_from_github_uses_returned_grid(tmp_path: Path, monkeypatch):
    """from_github=True with a successful fetch should render real intensities, not mock."""
    import cortex.sources as sources_pkg

    # 7x52 grid where row 1 has all-2s, others all-0 — distinctive pattern.
    fake_grid = [[2 if r == 1 else 0 for _ in range(52)] for r in range(7)]
    monkeypatch.setattr(
        sources_pkg, "contribution_grid_from_github", lambda client, weeks=52: fake_grid
    )
    cfg = _config(heatmap=HeatmapConfig(enabled=True, from_github=True))
    out = heatmap.build(cfg, tmp_path / "h.svg")
    text = out.read_text(encoding="utf-8")
    # Heatmap palette[2] for neon-green = "#2D8659" — should be present.
    assert "#2D8659" in text


def test_heatmap_from_github_falls_back_to_mock_on_empty(tmp_path: Path, monkeypatch):
    """When the source returns empty, the heatmap must still render via mock."""
    import cortex.sources as sources_pkg

    monkeypatch.setattr(sources_pkg, "contribution_grid_from_github", lambda c, weeks=52: [])
    cfg = _config(heatmap=HeatmapConfig(enabled=True, from_github=True))
    text = heatmap.build(cfg, tmp_path / "h.svg").read_text(encoding="utf-8")
    assert "<rect" in text
