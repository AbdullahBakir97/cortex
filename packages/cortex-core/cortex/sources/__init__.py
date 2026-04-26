"""Data sources that auto-populate widget configs from external APIs.

Each function takes a ``GitHubClient`` (or other source-specific client) and
returns the data shape a widget builder needs — e.g., a list of StatCubes
for the cubes widget, a 7x52 intensity matrix for the heatmap.

Source functions are deliberately pure-data (no SVG, no schema mutation):
they return the values, the builder decides what to do with them. This
keeps builders testable without hitting the network and lets users override
any field manually.

Network failures degrade gracefully — every helper has an explicit fallback
return value documented in its docstring.
"""

from cortex.sources.github import (
    contribution_grid_from_github,
    stats_cubes_from_github,
    top_languages_from_github,
)

__all__ = [
    "contribution_grid_from_github",
    "stats_cubes_from_github",
    "top_languages_from_github",
]
