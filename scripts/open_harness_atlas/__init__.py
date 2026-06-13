"""open-harness-atlas — scripts package.

The package is intentionally tiny: it provides a small console entry
point (`oha-validate` / `oha-refresh` / `oha-build`) that wraps the
standalone `scripts/*.py` modules so they can be invoked from a fresh
`pip install -e .` without remembering full script paths.

The core curation surface is the YAML registry; Python is purely
machinery.
"""

__version__ = "0.1.0-dev"
