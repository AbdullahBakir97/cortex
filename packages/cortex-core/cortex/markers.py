"""Daily README marker rewriter.

A README contains marker blocks like::

    <!-- CORTEX:QUOTE:START -->
    ...rendered content...
    <!-- CORTEX:QUOTE:END -->

`cortex update-readme` (or programmatic ``cortex.markers.update``) walks the
README and re-renders each block from live data — recent activity, the
quote-of-the-day, contribution skylines, and so on. Failed sections leave
their existing block intact instead of crashing the whole run.

Marker prefix is always ``CORTEX:`` so we never collide with user-written
markers. Sections are toggled via ``config.auto_update.markers.*``.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .github_api import GitHubClient
from .schema import Config


# ── Marker block replacement ────────────────────────────────────────────
def _replace_block(text: str, marker: str, new_body: str) -> tuple[str, bool]:
    """Swap the body of a single CORTEX marker block.

    Returns (new_text, was_found). Missing markers leave the text unchanged
    so the rewriter is safe to run against any README — users opt in by
    pasting the marker pair where they want each widget to appear.
    """
    pattern = re.compile(
        rf"(<!--\s*CORTEX:{re.escape(marker)}:START\s*-->)(.*?)(<!--\s*CORTEX:{re.escape(marker)}:END\s*-->)",
        flags=re.DOTALL,
    )
    if not pattern.search(text):
        return text, False
    return pattern.sub(rf"\1\n{new_body}\n\3", text, count=1), True


# ── Helpers shared across sections ──────────────────────────────────────
def _repo_link(name: str) -> str:
    return f"[`{name}`](https://github.com/{name})"


def _current_year() -> int:
    return dt.datetime.now(dt.timezone.utc).year


def _years_for(start_year: int) -> list[int]:
    cy = _current_year()
    if cy < start_year:
        return [cy]
    return list(range(start_year, cy + 1))


# ── Section renderers (token-free) ──────────────────────────────────────
QUOTES: list[tuple[str, str]] = [
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("The best error message is the one that never shows up.", "Thomas Fuchs"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Walking on water and developing software from a specification are easy if both are frozen.", "Edward V. Berard"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("There are only two kinds of languages: the ones people complain about and the ones nobody uses.", "Bjarne Stroustrup"),
    ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("If debugging is the process of removing software bugs, then programming must be the process of putting them in.", "Edsger W. Dijkstra"),
    ("Truth can only be found in one place: the code.", "Robert C. Martin"),
    ("Programming isn't about what you know; it's about what you can figure out.", "Chris Pine"),
    ("It's not a bug — it's an undocumented feature.", "Anonymous"),
    ("The most damaging phrase in the language is: 'We've always done it this way!'", "Grace Hopper"),
    ("Software is a great combination of artistry and engineering.", "Bill Gates"),
    ("Java is to JavaScript what car is to carpet.", "Chris Heilmann"),
    ("Good code is its own best documentation.", "Steve McConnell"),
    ("In order to be irreplaceable, one must always be different.", "Coco Chanel"),
    ("Don't comment bad code — rewrite it.", "Brian Kernighan"),
    ("Programs are meant to be read by humans and only incidentally for computers to execute.", "Donald Knuth"),
    ("The function of good software is to make the complex appear to be simple.", "Grady Booch"),
    ("Code never lies, comments sometimes do.", "Ron Jeffries"),
    ("Quality is more important than quantity. One home run is much better than two doubles.", "Steve Jobs"),
    ("Software undergoes beta testing shortly before it's released. Beta is Latin for 'still doesn't work'.", "Anonymous"),
    ("Real programmers count from 0.", "Anonymous"),
    ("Programming is the art of telling another human being what one wants the computer to do.", "Donald Knuth"),
    ("If you don't fail at least 90% of the time, you're not aiming high enough.", "Alan Kay"),
    ("The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie"),
    ("Computers are good at following instructions, but not at reading your mind.", "Donald Knuth"),
]


def quote_of_the_day(_config: Config, _client: GitHubClient) -> str:
    """Pick a quote indexed by day-of-year so it rotates daily and stays stable for the day."""
    day = dt.datetime.now(dt.timezone.utc).timetuple().tm_yday
    quote, author = QUOTES[day % len(QUOTES)]
    return (
        '<p align="center">\n'
        f'  <i>"{quote}"</i><br/>\n'
        f'  <sub>— <b>{author}</b></sub>\n'
        '</p>'
    )


# ── Activity / gitGraph (REST, public, token-optional) ──────────────────
def _push_event(e: dict) -> str | None:
    commits = e["payload"].get("commits") or []
    if not commits:
        return None
    return f"⬆️ Pushed {len(commits)} commit(s) to {_repo_link(e['repo']['name'])}"


def _pr_event(e: dict) -> str:
    pr = e["payload"]["pull_request"]
    repo = e["repo"]["name"]
    url = pr.get("html_url") or f"https://github.com/{repo}/pull/{pr['number']}"
    return f"🔀 {e['payload']['action'].title()} PR [#{pr['number']}]({url}) in {_repo_link(repo)}"


def _issue_event(e: dict) -> str:
    issue = e["payload"]["issue"]
    repo = e["repo"]["name"]
    url = issue.get("html_url") or f"https://github.com/{repo}/issues/{issue['number']}"
    return f"❗ {e['payload']['action'].title()} issue [#{issue['number']}]({url}) in {_repo_link(repo)}"


def _release_event(e: dict) -> str:
    rel = e["payload"]["release"]
    repo = e["repo"]["name"]
    url = rel.get("html_url") or f"https://github.com/{repo}/releases/tag/{rel.get('tag_name', '')}"
    return f"📦 Released [`{rel.get('tag_name', '?')}`]({url}) of {_repo_link(repo)}"


def _create_event(e: dict) -> str | None:
    ref_type = e["payload"].get("ref_type")
    if ref_type not in ("repository", "tag"):
        return None
    return f"✨ Created {ref_type} {_repo_link(e['repo']['name'])}"


def _fork_event(e: dict) -> str:
    return f"🍴 Forked {_repo_link(e['repo']['name'])}"


_EVENT_FORMATTERS: dict[str, Callable[[dict], str | None]] = {
    "PushEvent": _push_event,
    "PullRequestEvent": _pr_event,
    "IssuesEvent": _issue_event,
    "ReleaseEvent": _release_event,
    "CreateEvent": _create_event,
    "ForkEvent": _fork_event,
}


def activity(_config: Config, client: GitHubClient, *, limit: int = 8) -> str:
    """Last N notable public events as a bullet list."""
    events = client.public_events(per_page=30)
    lines: list[str] = []
    for event in events:
        formatter = _EVENT_FORMATTERS.get(event["type"])
        if not formatter:
            continue
        line = formatter(event)
        if line:
            lines.append(f"- {line}")
        if len(lines) >= limit:
            break
    return "\n".join(lines) if lines else "_No recent public activity._"


def gitgraph(_config: Config, client: GitHubClient, *, limit: int = 8) -> str:
    """Render a small Mermaid gitGraph from recent PushEvents."""
    events = client.public_events(per_page=50)
    pushes: list[tuple[str, int]] = []
    seen: set[str] = set()
    for event in events:
        if event["type"] != "PushEvent":
            continue
        commits = event["payload"].get("commits") or []
        if not commits:
            continue
        repo_short = event["repo"]["name"].split("/")[-1]
        if repo_short in seen:
            continue
        seen.add(repo_short)
        pushes.append((repo_short, len(commits)))
        if len(pushes) >= limit:
            break

    if not pushes:
        return "_No recent push events to visualize._"

    lines = ["```mermaid", "gitGraph", '   commit id: "main"']
    for repo, count in pushes:
        branch = re.sub(r"[^a-zA-Z0-9_-]", "-", repo)[:30] or "branch"
        lines.append(f"   branch {branch}")
        lines.append(f"   checkout {branch}")
        for i in range(min(count, 4)):
            lines.append(f'   commit id: "c{i + 1}"')
        lines.append("   checkout main")
        lines.append(f"   merge {branch}")
    lines.append("```")
    return "\n".join(lines)


# ── Skyline / city grids (no API — pure URL composition) ────────────────
def _grid(years: list[int], href_for: Callable[[int], str], svg_for: Callable[[int], str], alt_kind: str) -> str:
    if not years:
        return f"_No {alt_kind.lower()} years configured._"
    cy = _current_year()
    width = 100 // len(years)
    cells = []
    for y in years:
        label = f"{y} <sub>(live)</sub>" if y == cy else str(y)
        cells.append(
            f'<td width="{width}%" align="center">'
            f'<a href="{href_for(y)}">'
            f'<img src="{svg_for(y)}" width="100%" alt="{alt_kind} {y}">'
            f'</a><p><b>{label}</b></p></td>'
        )
    return '<table align="center" width="100%"><tr>' + "".join(cells) + "</tr></table>"


def _resolved_skyline_years(config: Config) -> list[int]:
    if config.contributions.skylines.years is not None:
        return list(config.contributions.skylines.years)
    return _years_for(config.cards.yearly_highlights.start_year)


def _resolved_city_years(config: Config) -> list[int]:
    if config.contributions.cities.years is not None:
        return list(config.contributions.cities.years)
    return _years_for(config.cards.yearly_highlights.start_year)


def skyline_grid(config: Config, _client: GitHubClient) -> str:
    user = config.identity.github_user
    raw_base = f"https://raw.githubusercontent.com/{user}/{user}/metrics-output"
    return _grid(
        _resolved_skyline_years(config),
        href_for=lambda y: f"https://skyline.github.com/{user}/{y}",
        svg_for=lambda y: f"{raw_base}/github-metrics-skyline-{y}.svg",
        alt_kind="GitHub Skyline",
    )


def city_grid(config: Config, _client: GitHubClient) -> str:
    user = config.identity.github_user
    raw_base = f"https://raw.githubusercontent.com/{user}/{user}/metrics-output"
    return _grid(
        _resolved_city_years(config),
        href_for=lambda y: f"https://honzaap.github.io/GithubCity?name={user}&year={y}",
        svg_for=lambda y: f"{raw_base}/github-metrics-city-{y}.svg",
        alt_kind="GitHub City",
    )


def _link_bar(years: list[int], prefix: str, href_for: Callable[[int], str], label_for: Callable[[int], str]) -> str:
    if not years:
        return f'<p align="center"><b>{prefix}</b> <em>none configured</em></p>'
    cy = _current_year()
    parts = []
    for y in years:
        suffix = " <sub>(live)</sub>" if y == cy else ""
        parts.append(f'<a href="{href_for(y)}">{label_for(y)}{suffix}</a>')
    return f'<p align="center"><b>{prefix}</b> ' + " · ".join(parts) + "</p>"


def stl_links(config: Config, _client: GitHubClient) -> str:
    user = config.identity.github_user
    base = f"https://github.com/{user}/{user}/blob/metrics-output"
    return _link_bar(
        _resolved_skyline_years(config),
        prefix="📐 Spin a 3D model:",
        href_for=lambda y: f"{base}/skyline-{y}.stl",
        label_for=lambda y: f"{y} STL",
    )


def gitcity_links(config: Config, _client: GitHubClient) -> str:
    user = config.identity.github_user
    return _link_bar(
        _resolved_city_years(config),
        prefix="🚗 Drive through:",
        href_for=lambda y: f"https://honzaap.github.io/GithubCity?name={user}&year={y}",
        label_for=lambda y: f"{y} city",
    )


# ── Section renderers (token-required) ──────────────────────────────────
_RELEASES_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        url
        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { name tagName publishedAt url }
        }
      }
    }
  }
}
"""


def latest_releases(config: Config, client: GitHubClient, *, limit: int = 5) -> str:
    """Newest releases across the user's repos, newest first."""
    data = client.graphql(_RELEASES_QUERY, {"login": config.identity.github_user})
    rows = []
    for repo in data["user"]["repositories"]["nodes"]:
        for rel in repo["releases"]["nodes"]:
            rows.append({
                "repo": repo["name"],
                "tag": rel["tagName"],
                "name": rel["name"] or rel["tagName"],
                "url": rel["url"],
                "at": rel["publishedAt"],
            })
    rows.sort(key=lambda r: r["at"], reverse=True)
    if not rows:
        return "_No releases yet._"
    out = []
    for row in rows[:limit]:
        date = row["at"][:10]
        out.append(
            f"- 📦 [`{row['repo']}` `{row['tag']}`]({row['url']}) — {row['name']} "
            f"<sub>({date})</sub>"
        )
    return "\n".join(out)


_STATS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalRepositoriesWithContributedCommits
    }
  }
}
"""


def highlights_stats(config: Config, client: GitHubClient) -> str:
    """Current-year commits/PRs/active-repos/new-repos as a row of badges."""
    user = config.identity.github_user
    cy = _current_year()
    start = f"{cy}-01-01T00:00:00Z"
    end = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = client.graphql(_STATS_QUERY, {"login": user, "from": start, "to": end})
    cc = data["user"]["contributionsCollection"]

    new_repos_count = 0
    try:
        rr = client.search_repos(f"user:{user}+created:>={cy}-01-01")
        new_repos_count = rr.get("total_count", 0)
    except Exception:
        pass  # leave at 0 — partial data is better than no badge row

    return (
        '<p align="center">'
        f'<img src="https://img.shields.io/badge/Commits-{cc["totalCommitContributions"]}-red?style=for-the-badge&logo=git&logoColor=white" alt="Commits" /> '
        f'<img src="https://img.shields.io/badge/PRs-{cc["totalPullRequestContributions"]}-red?style=for-the-badge&logo=github&logoColor=white" alt="PRs" /> '
        f'<img src="https://img.shields.io/badge/New_Repos-{new_repos_count}-red?style=for-the-badge&logo=github&logoColor=white" alt="New repos" /> '
        f'<img src="https://img.shields.io/badge/Active_in-{cc["totalRepositoriesWithContributedCommits"]}_repos-red?style=for-the-badge&logo=github&logoColor=white" alt="Active repos" />'
        "</p>"
    )


def pagespeed(config: Config, _client: GitHubClient) -> str:
    """Render Lighthouse mobile scores from Google PageSpeed Insights."""
    import time
    import urllib.parse
    import requests

    psi_cfg = config.auto_update.markers.pagespeed
    if not psi_cfg.url:
        raise RuntimeError("config.auto_update.markers.pagespeed.url is empty")

    api_key = __import__("os").environ.get("PSI_API_KEY", "")
    categories = ["PERFORMANCE", "ACCESSIBILITY", "BEST_PRACTICES", "SEO"]
    labels = {"PERFORMANCE": "Performance", "ACCESSIBILITY": "Accessibility", "BEST_PRACTICES": "Best_Practices", "SEO": "SEO"}

    params: list[tuple[str, str]] = [("url", psi_cfg.url), ("strategy", "mobile")]
    for cat in categories:
        params.append(("category", cat))
    if api_key:
        params.append(("key", api_key))
    qs = urllib.parse.urlencode(params)
    url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?{qs}"

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 429:
                hint = "" if api_key else " (set PSI_API_KEY to lift rate limits)"
                raise RuntimeError(f"PSI rate-limited{hint}")
            r.raise_for_status()
            payload = r.json()
            break
        except Exception as e:
            last_exc = e
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    else:
        raise last_exc  # type: ignore[misc]

    cats = payload.get("lighthouseResult", {}).get("categories", {})
    scores: dict[str, int] = {}
    for cat in categories:
        node = cats.get(cat.lower().replace("_", "-"))
        if node and node.get("score") is not None:
            scores[cat] = round(node["score"] * 100)
    if not scores:
        return "_PageSpeed scores unavailable._"

    def color(pct: int) -> str:
        if pct >= 90: return "success"
        if pct >= 50: return "yellow"
        return "red"

    badges = []
    rows = []
    for cat in categories:
        if cat not in scores:
            continue
        pct, label = scores[cat], labels[cat]
        badges.append(
            f'<img src="https://img.shields.io/badge/{label}-{pct}%25-{color(pct)}'
            f'?style=for-the-badge&logo=google&logoColor=white" alt="{label}: {pct}%" />'
        )
        rows.append(f'<tr><td>{label.replace("_", " ")}</td><td>{pct}/100</td></tr>')

    today = dt.date.today().isoformat()
    return (
        '<p align="center">' + "\n  ".join(badges) + "</p>\n\n"
        '<table align="center"><tr><th>Metric</th><th>Score</th></tr>\n'
        + "\n".join(rows) +
        "\n</table>\n\n"
        f'<p align="center"><em>Last updated {today} (mobile strategy).</em></p>'
    )


# ── Section registry ────────────────────────────────────────────────────
@dataclass(frozen=True)
class _Section:
    name: str                        # marker name (becomes CORTEX:NAME)
    enabled_attr: str                # field on config.auto_update.markers
    render: Callable[[Config, GitHubClient], str]
    needs_token: bool                # if true, skip cleanly when no token set


_SECTIONS: list[_Section] = [
    _Section("QUOTE",            "quote_of_the_day", quote_of_the_day, needs_token=False),
    _Section("ACTIVITY",         "activity",         activity,         needs_token=False),
    _Section("GITGRAPH",         "gitgraph",         gitgraph,         needs_token=False),
    _Section("SKYLINE_GRID",     "skyline_grid",     skyline_grid,     needs_token=False),
    _Section("CITY_GRID",        "city_grid",        city_grid,        needs_token=False),
    _Section("STL_LINKS",        "stl_links",        stl_links,        needs_token=False),
    _Section("GITCITY_LINKS",    "gitcity_links",    gitcity_links,    needs_token=False),
    _Section("LATEST_RELEASES",  "latest_releases",  latest_releases,  needs_token=True),
    _Section("HIGHLIGHTS_STATS", "highlights_stats", highlights_stats, needs_token=True),
    _Section("PAGESPEED",        "pagespeed",        pagespeed,        needs_token=False),
]


# ── Public entry point ──────────────────────────────────────────────────
@dataclass
class UpdateResult:
    sections_updated: list[str]
    sections_failed:  list[tuple[str, str]]    # (name, error)
    sections_missing: list[str]                 # marker pair not present in README
    sections_skipped: list[tuple[str, str]]     # (name, reason)

    @property
    def changed(self) -> bool:
        return bool(self.sections_updated)


def update(config: Config, readme_path: str | Path, *, client: GitHubClient | None = None) -> UpdateResult:
    """Refresh all enabled marker blocks in ``readme_path`` from live data.

    Returns an ``UpdateResult`` summarizing what changed, what failed, and
    what was missing — caller decides how to surface this. The README file
    is rewritten only if at least one block actually changed.
    """
    path = Path(readme_path)
    text = path.read_text(encoding="utf-8")
    original = text

    if client is None:
        from .github_api import client_from_env
        client = client_from_env(config.identity.github_user)

    result = UpdateResult([], [], [], [])

    for section in _SECTIONS:
        attr = getattr(config.auto_update.markers, section.enabled_attr)
        # Nested config objects (PageSpeedConfig, WakaTimeConfig) carry an
        # .enabled flag; bare bool flags are read directly.
        is_enabled = bool(getattr(attr, "enabled", attr))
        if not is_enabled:
            result.sections_skipped.append((section.name, "disabled in config"))
            continue
        if section.needs_token and not client.token:
            result.sections_skipped.append((section.name, "no GitHub token (set GH_TOKEN)"))
            continue
        try:
            body = section.render(config, client)
        except Exception as e:
            result.sections_failed.append((section.name, str(e)))
            continue
        text, found = _replace_block(text, section.name, body)
        if not found:
            result.sections_missing.append(section.name)
        else:
            result.sections_updated.append(section.name)

    if text != original:
        path.write_text(text, encoding="utf-8")
    return result
