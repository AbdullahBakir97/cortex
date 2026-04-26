"""pytest config: ensure the cortex-core package is importable from tests."""

from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent  # packages/cortex-core
_SRC = _PKG_ROOT / "cortex"

# Add the package root so `import cortex` resolves to packages/cortex-core/cortex
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
