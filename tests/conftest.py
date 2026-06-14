"""Shared pytest setup.

Adds the repo root to ``sys.path`` so modules under ``scripts/`` can use
``from scripts._atomic import atomic_write_text`` style imports without
breaking the existing pattern of ``importlib.import_module("compute_tier")``
that test files rely on (which assumes ``scripts/`` is also on the path).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
