#!/usr/bin/env python3
"""Regenerate the auto-marker sections of CONTEXT.md.

Runs locally (`python scripts/refresh_context.py`) and in CI (via
`.github/workflows/refresh-context.yml`, which commits any diff back as
`cortex-bot[bot]` with `[skip ci]`).

Marker contract:
  Each auto-section in CONTEXT.md is bounded by HTML comments of the form
  `<!-- AUTO:NAME:START -->` and `<!-- AUTO:NAME:END -->`. This script
  replaces the content between matching markers. Anything outside the
  markers is preserved verbatim — humans own those sections.

Add a new auto-section by:
  1. Adding the marker pair in CONTEXT.md
  2. Computing a new body in `main()`
  3. Calling `_replace_marker(text, "NAME", body)`
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT / "CONTEXT.md"


def _git(*args: str) -> str:
    """Run a git command in the repo root and return stdout (stripped).

    Force UTF-8 decoding — git emits UTF-8, but subprocess on Windows
    defaults to the system codepage (cp1252) which mangles em-dashes and
    other non-ASCII characters in commit messages.
    """
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace"
    ).strip()


def _recent_commits(n: int = 12) -> str:
    """One-line summaries of the last n commits with relative date + author."""
    raw = _git("log", "-n", str(n), "--pretty=format:- `%h` %s _(%ar by %an)_")
    return raw or "_(no commits yet)_"


def _replace_marker(text: str, name: str, body: str) -> str:
    """Replace content between `<!-- AUTO:NAME:START -->` and `<!-- AUTO:NAME:END -->`."""
    pattern = re.compile(
        rf"(<!-- AUTO:{re.escape(name)}:START -->)(.*?)(<!-- AUTO:{re.escape(name)}:END -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(
            f"Marker AUTO:{name} not found in {CONTEXT.name}. "
            f"Add `<!-- AUTO:{name}:START -->` and `<!-- AUTO:{name}:END -->` first."
        )
    return pattern.sub(rf"\1\n{body}\n\3", text)


def main() -> int:
    if not CONTEXT.exists():
        print(f"[ERR] {CONTEXT} does not exist", file=sys.stderr)
        return 1
    before = CONTEXT.read_text(encoding="utf-8")
    after = _replace_marker(before, "RECENT_COMMITS", _recent_commits())
    if after == before:
        print("[OK] CONTEXT.md auto sections already current — no change.")
        return 0
    CONTEXT.write_text(after, encoding="utf-8")
    print("[OK] Refreshed CONTEXT.md auto sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
