"""Tiny CLI surface for the open-harness-atlas helper scripts.

Exposed entry points (via pyproject.toml [project.scripts]):

  oha-validate  -> scripts/validate_registry.py:main
  oha-refresh   -> scripts/refresh_metadata.py:main
  oha-build     -> runs build_matrices then build_visuals

These are deliberately minimal wrappers so the imperative scripts under
`scripts/*.py` remain runnable as plain `python scripts/<name>.py` for
contributors who don't want to install the package.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _add_scripts_to_path() -> None:
    scripts_dir = Path(__file__).resolve().parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


def validate() -> int:
    _add_scripts_to_path()
    mod = importlib.import_module("validate_registry")
    return int(mod.main())


def refresh() -> int:
    _add_scripts_to_path()
    mod = importlib.import_module("refresh_metadata")
    return int(mod.main())


def build() -> int:
    _add_scripts_to_path()
    matrices = importlib.import_module("build_matrices")
    visuals = importlib.import_module("build_visuals")
    rc = int(matrices.main())
    if rc != 0:
        return rc
    return int(visuals.main())
