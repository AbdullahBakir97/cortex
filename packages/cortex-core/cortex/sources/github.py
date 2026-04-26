"""GitHub-derived data sources for Cortex widgets.

Wraps ``GitHubClient`` with widget-shaped queries. Every function:

  • Has a clearly-typed return value (the exact shape its builder consumes)
  • Falls back to a sensible default on network failure rather than raising
  • Is pure-data (no SVG, no Config mutation)
"""

from __future__ import annotations

from typing import Any

from cortex.github_api import GitHubClient
from cortex.schema import StatCube

# ── Stat cubes (PRs / commits / stars / etc) ─────────────────────────────


# Default fallback when GraphQL is unavailable (no token, network error, etc).
# Using "—" rather than fabricated numbers so users notice degradation.
_CUBES_FALLBACK: list[StatCube] = [
    StatCube(label="PRs", value="—"),
    StatCube(label="Commits", value="—"),
    StatCube(label="Stars", value="—"),
    StatCube(label="Repos", value="—"),
    StatCube(label="Issues", value="—"),
]


_CUBES_QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests        { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
    }
    starredRepositories { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
  }
}
"""


def _fmt_count(n: int) -> str:
    """Render a count like '8.4k' or '1.2M' — keeps cube faces compact."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def stats_cubes_from_github(client: GitHubClient) -> list[StatCube]:
    """Fetch profile-wide totals for cubes widget. Returns 5 cubes."""
    if not client.token:
        # Anonymous queries can't hit GraphQL; degrade silently.
        return list(_CUBES_FALLBACK)
    try:
        data = client.graphql(_CUBES_QUERY, {"login": client.user})
    except Exception:
        return list(_CUBES_FALLBACK)
    user = data.get("user")
    if not user:
        return list(_CUBES_FALLBACK)

    contrib = user.get("contributionsCollection", {})
    return [
        StatCube(label="PRs", value=_fmt_count(user.get("pullRequests", {}).get("totalCount", 0))),
        StatCube(
            label="Commits",
            value=_fmt_count(contrib.get("totalCommitContributions", 0)),
        ),
        StatCube(
            label="Stars",
            value=_fmt_count(user.get("starredRepositories", {}).get("totalCount", 0)),
        ),
        StatCube(
            label="Repos", value=_fmt_count(user.get("repositories", {}).get("totalCount", 0))
        ),
        StatCube(
            label="Issues",
            value=_fmt_count(contrib.get("totalIssueContributions", 0)),
        ),
    ]


# ── Contribution heatmap (7 days x N weeks intensity matrix) ─────────────


_CONTRIB_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""


def _intensity_for(count: int) -> int:
    """Map raw daily commit count to a 0..4 intensity bucket."""
    if count == 0:
        return 0
    if count < 3:
        return 1
    if count < 8:
        return 2
    if count < 16:
        return 3
    return 4


def contribution_grid_from_github(client: GitHubClient, weeks: int = 52) -> list[list[int]]:
    """Fetch a real 7xweeks contribution intensity matrix.

    Returns a 7-row list (Sun..Sat) x ``weeks`` columns of intensities 0..4.
    Returns an empty list on failure — the heatmap builder will then fall
    back to its deterministic mock generator.
    """
    if not client.token:
        return []
    try:
        data = client.graphql(_CONTRIB_QUERY, {"login": client.user})
    except Exception:
        return []
    contrib_weeks = (
        data.get("user", {})
        .get("contributionsCollection", {})
        .get("contributionCalendar", {})
        .get("weeks", [])
    )
    if not contrib_weeks:
        return []

    # GitHub returns the most-recent weeks last. Take the trailing N.
    contrib_weeks = contrib_weeks[-weeks:]

    grid: list[list[int]] = [[0] * weeks for _ in range(7)]
    for col, week in enumerate(contrib_weeks):
        for day in week.get("contributionDays", []):
            weekday = day.get("weekday", 0)  # 0 = Sun, 6 = Sat
            count = day.get("contributionCount", 0)
            grid[weekday][col] = _intensity_for(count)
    return grid


# ── Top languages (used by galaxy / dna / badges in future PRs) ──────────


_LANGS_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def top_languages_from_github(client: GitHubClient, top_n: int = 8) -> list[dict[str, Any]]:
    """Return ``top_n`` languages by total bytes across the user's public repos.

    Each entry: ``{"name": "Python", "color": "#3572A5", "bytes": 1234567}``.
    Empty list on failure or no token.
    """
    if not client.token:
        return []
    try:
        data = client.graphql(_LANGS_QUERY, {"login": client.user})
    except Exception:
        return []
    nodes = data.get("user", {}).get("repositories", {}).get("nodes", [])
    totals: dict[str, dict[str, Any]] = {}
    for repo in nodes:
        for edge in repo.get("languages", {}).get("edges", []):
            lang = edge.get("node", {})
            name = lang.get("name")
            if not name:
                continue
            entry = totals.setdefault(
                name, {"name": name, "color": lang.get("color") or "", "bytes": 0}
            )
            entry["bytes"] += int(edge.get("size", 0))
    ranked = sorted(totals.values(), key=lambda x: -x["bytes"])
    return ranked[:top_n]
