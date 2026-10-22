"""graph-art: read a GitHub contribution graph like a story and like a drawing.

Original concept and design: Abdullah Bakir (@AbdullahBakir97), 2026.

Three layers, all working on real days only:

* ``calendar``  - load daily contribution counts (GitHub GraphQL, saved JSON,
                   or heatmap SVGs with ``<title>N on YYYY-MM-DD</title>``).
* ``analysis``  - per-year story: quiet / steady / busy stretches, longest
                   streak, biggest day, best month.
* ``detect``    - find shapes hiding in the grid (faces from empty "eye"
                   cells, plus pixel-art templates) and suggest them as
                   figures a person can confirm or edit.
* ``figures``   - the figures.json format and an honesty check: a figure
                   may only colour days that really had contributions, or
                   mark empty days as holes (eyes, mouths).
* ``render``    - SVGs that work inside GitHub's image proxy: the year story
                   and a gallery of confirmed figures.
"""

from .analysis import YearSummary, summarize_year
from .calendar import Calendar
from .figures import Figure, load_figures, save_figures, validate_figure

__all__ = [
    "Calendar",
    "Figure",
    "YearSummary",
    "load_figures",
    "save_figures",
    "summarize_year",
    "validate_figure",
]
