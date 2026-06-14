"""Shared atomic-write helper for source-of-truth metadata writers.

Why this exists
---------------
``scripts/refresh_metadata.py`` learned the ``.tmp`` + ``os.replace`` pattern
during Phase 4 (the adversarial swarm caught the partial-write → silent
``JSONDecodeError`` → snapshot-history-loss path). The same correctness
argument applies to every other script that writes a file consumed by
downstream tools:

* ``compute_tier.py`` → ``registry/_metadata/_tiers.json`` (the entire
  viewer tier overlay depends on this; a partial write turns 833 tier
  classifications into nothing).
* ``compute_velocity.py`` → ``registry/_metadata/_velocity.json`` and
  ``docs/rising.md`` (sparkline data + the auto-published rising list).
* ``build_graph.py`` → ``visuals/graph-data.json`` (the entire viewer
  payload; partial write breaks the live site).
* ``compute_deployment_posture.py`` → posture override file
  (one row per registry entry, ingested back into curation).

Each of those scripts previously did ``path.write_text(...)`` directly,
which on a SIGKILL / process crash / disk-full mid-write leaves the
target file either truncated or in a half-serialised state. Downstream
JSON parsers fail with ``JSONDecodeError`` and either return ``{}``
(``_load_existing`` style) — silently nuking real data — or crash later
in some unrelated code path.

API
---
Just one function, deliberately. Everything else lives in the calling
script.

::

    from scripts._atomic import atomic_write_text
    atomic_write_text(path, payload)

The temporary file is written in the same directory as the target so
``os.replace`` stays on the same filesystem (cross-FS rename is not
atomic). On Windows ``os.replace`` is as-atomic-as-the-OS-allows; on
POSIX it is fully atomic by guarantee of ``rename(2)``.
"""

from __future__ import annotations

import os
from pathlib import Path


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Write ``text`` to ``path`` atomically.

    The write happens in a sibling ``.tmp`` file in the same directory as
    ``path``; on success the temp is renamed over ``path`` via
    ``os.replace``. If the process dies mid-write, ``path`` is left
    untouched (the original content survives) and a ``.tmp`` file may be
    left behind — that orphan is harmless and will be overwritten on the
    next successful write.

    Parameters
    ----------
    path
        The target file. Parent directory must exist.
    text
        The full file contents.
    encoding
        Text encoding (default ``utf-8``).
    """
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding=encoding)
    os.replace(tmp_path, path)
