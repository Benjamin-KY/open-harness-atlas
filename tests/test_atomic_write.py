"""Tests for the shared atomic-write helper.

Pins three properties of ``scripts._atomic.atomic_write_text``:

1. **Round-trip** — happy-path write produces exactly the requested text,
   leaves no orphan ``.tmp`` file, creates the target if missing.

2. **Crash safety** — if ``os.replace`` raises mid-write (simulating a
   disk-full / killed process / EIO at the rename step), the original
   target file is left untouched. This is the entire reason the helper
   exists: a partial write would silently nuke the snapshot history of
   every refresh_metadata sidecar via the JSONDecodeError → ``{}``
   fallback in ``_load_existing``.

3. **Regression pin** — each of the five critical writers
   (compute_tier, compute_velocity, build_graph, compute_deployment_posture,
   refresh_metadata) imports the helper. If a future refactor reverts any
   of them to raw ``.write_text``, this test fails immediately rather
   than waiting for a real mid-write crash in CI or in a curator's
   terminal.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_atomic_write_text_round_trip(tmp_path):
    from scripts._atomic import atomic_write_text

    target = tmp_path / "out.json"
    payload = '{"snapshots": [1, 2, 3]}\n'
    atomic_write_text(target, payload)

    assert target.read_text(encoding="utf-8") == payload
    assert not list(tmp_path.glob("*.tmp")), "no .tmp orphan after happy-path write"


def test_atomic_write_text_overwrite_preserves_old_on_crash(tmp_path, monkeypatch):
    """The whole point of the helper: a failed replace leaves the target intact."""
    from scripts import _atomic
    from scripts._atomic import atomic_write_text

    target = tmp_path / "tiers.json"
    target.write_text("ORIGINAL CONTENT\n", encoding="utf-8")

    def boom(src, dst):
        raise OSError("simulated disk-full at rename(2)")

    monkeypatch.setattr(_atomic.os, "replace", boom)

    with pytest.raises(OSError, match="simulated disk-full"):
        atomic_write_text(target, "NEW CONTENT THAT MUST NOT LAND\n")

    # The original target survives the crash — that is the contract.
    assert target.read_text(encoding="utf-8") == "ORIGINAL CONTENT\n"
    # The .tmp may or may not survive (implementation detail of OS error
    # handling). What matters is the target file remains the previous
    # known-good content.


def test_atomic_write_text_creates_new_file(tmp_path):
    from scripts._atomic import atomic_write_text

    target = tmp_path / "subdir-must-exist" / "out.txt"
    target.parent.mkdir()
    atomic_write_text(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"


@pytest.mark.parametrize(
    "module_name",
    [
        "scripts.compute_tier",
        "scripts.compute_velocity",
        "scripts.build_graph",
        "scripts.compute_deployment_posture",
        "scripts.refresh_metadata",
    ],
)
def test_critical_writer_uses_atomic_helper(module_name):
    """Regression pin: every source-of-truth writer must import the helper.

    The set of "critical" writers is the set of scripts that write a file
    consumed by downstream tooling (CI gates, viewers, matrix tables,
    curator overrides). Each one was migrated together; any future PR
    that strips the import and reverts to raw ``.write_text`` will trip
    this test rather than introducing a silent partial-write regression.
    """
    module = importlib.import_module(module_name)
    assert hasattr(module, "atomic_write_text"), (
        f"{module_name} must `from scripts._atomic import atomic_write_text` "
        "to use the shared crash-safe writer. If you're intentionally "
        "removing this dependency, also remove this regression pin and "
        "explain why in the commit message."
    )
