"""Thin GitHub REST + GraphQL client.

Centralizes the few HTTP calls Cortex needs (events, contributions, releases)
behind a small surface so that:

  • Tests can monkey-patch one place.
  • Auth (token vs. anonymous) is decided once.
  • Future caching / rate-limit handling lives in one file.

Anything that needs a GitHub PAT will gracefully degrade when the token is
empty — anonymous calls still work for public REST, just with stricter
rate limits.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class GitHubClient:
    user: str
    token: str = ""
    timeout_s: float = 20.0

    @property
    def headers(self) -> dict[str, str]:
        h = {"Accept": "application/vnd.github+json", "User-Agent": "cortex-cli"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    # ── REST ────────────────────────────────────────────────────────────
    def public_events(self, *, per_page: int = 30) -> list[dict[str, Any]]:
        r = requests.get(
            f"https://api.github.com/users/{self.user}/events/public?per_page={per_page}",
            headers=self.headers,
            timeout=self.timeout_s,
        )
        r.raise_for_status()
        return r.json()

    def search_repos(self, query: str) -> dict[str, Any]:
        r = requests.get(
            f"https://api.github.com/search/repositories?q={query}",
            headers=self.headers,
            timeout=self.timeout_s,
        )
        r.raise_for_status()
        return r.json()

    # ── GraphQL ─────────────────────────────────────────────────────────
    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError(
                "GraphQL queries require a GitHub token — pass --github-token "
                "or set GH_TOKEN/GITHUB_TOKEN."
            )
        r = requests.post(
            "https://api.github.com/graphql",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"query": query, "variables": variables},
            timeout=max(30.0, self.timeout_s),
        )
        r.raise_for_status()
        payload = r.json()
        if "errors" in payload:
            raise RuntimeError(f"GraphQL errors: {payload['errors']}")
        return payload["data"]


def client_from_env(user: str) -> GitHubClient:
    """Build a GitHubClient using whichever token env var is set."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    return GitHubClient(user=user, token=token)
