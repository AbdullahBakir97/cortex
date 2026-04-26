"""Cortex SVG builders.

Each builder accepts a ``Config`` instance and writes one SVG file. Builders
share gradient/filter snippets via small helper modules under
``cortex.builders._common``.

Builder API contract:

    def build(config: Config, output: str) -> Path:
        \"\"\"Render to ``output``, return the resolved Path.\"\"\"

Importable builders:
"""

from cortex.builders import brain

# Future:
# from cortex.builders import tech_cards, timeline, focus, typing, github_icon

__all__ = ["brain"]
