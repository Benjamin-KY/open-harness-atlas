"""Tests for the data_missing visual-encoding logic in scripts/build_graph.

Pins three properties:

1. ``_sidecar_latest_refresh`` correctly parses both the snapshot shape
   (current) and the legacy flat shape (pre-Phase-4 entries) and
   returns ``None`` on missing / unparseable / no-timestamp.

2. ``is_sidecar_stale`` fires when the sidecar's latest refresh is
   older than ``SIDECAR_STALE_DAYS`` (default 60) and stays silent
   for fresh sidecars and for the missing-sidecar case (which is
   intentionally handled via the tier=unknown branch instead).

3. The committed ``visuals/graph-data.json`` produced by ``build_graph``
   sets ``data_missing=True`` and ``tier_outline="dotted"`` exactly for
   the union of unknown-tier entries and stale-sidecar entries — so
   the viewer's existing dotted-outline / faded-opacity render path
   covers both operational cases without needing viewer changes.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.build_graph import (
    SIDECAR_STALE_DAYS,
    _sidecar_latest_refresh,
    is_sidecar_stale,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# _sidecar_latest_refresh — shape coverage
# ---------------------------------------------------------------------------


def _write_sidecar(tmp_path: Path, name: str, payload: dict) -> Path:
    sidecar = tmp_path / f"{name}.json"
    sidecar.write_text(json.dumps(payload), encoding="utf-8")
    return sidecar


def test_latest_refresh_snapshot_shape(tmp_path):
    _write_sidecar(tmp_path, "foo", {
        "created_at": "2024-01-01T00:00:00Z",
        "snapshots": [
            {"refreshed_at": "2025-01-01T00:00:00Z", "stars": 100},
            {"refreshed_at": "2026-06-01T00:00:00Z", "stars": 200},
        ],
    })
    got = _sidecar_latest_refresh("foo", metadata_dir=tmp_path)
    assert got is not None
    assert got.year == 2026 and got.month == 6 and got.day == 1


def test_latest_refresh_flat_legacy_shape(tmp_path):
    """Pre-Phase-4 sidecars store ``refreshed_at`` at top level."""
    _write_sidecar(tmp_path, "legacy", {
        "created_at": "2023-08-30T12:06:57Z",
        "refreshed_at": "2026-06-10T01:49:19Z",
        "stars": 1603,
    })
    got = _sidecar_latest_refresh("legacy", metadata_dir=tmp_path)
    assert got is not None
    assert got.year == 2026 and got.month == 6 and got.day == 10


def test_latest_refresh_missing_sidecar(tmp_path):
    assert _sidecar_latest_refresh("does-not-exist", metadata_dir=tmp_path) is None


def test_latest_refresh_unparseable_json(tmp_path):
    sidecar = tmp_path / "bad.json"
    sidecar.write_text("{not valid json", encoding="utf-8")
    assert _sidecar_latest_refresh("bad", metadata_dir=tmp_path) is None


def test_latest_refresh_no_timestamp(tmp_path):
    _write_sidecar(tmp_path, "nots", {"created_at": "2024-01-01T00:00:00Z"})
    assert _sidecar_latest_refresh("nots", metadata_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# is_sidecar_stale — threshold + missing fallthrough
# ---------------------------------------------------------------------------


@pytest.fixture
def reference_now():
    """Pin to UTC midnight so day-arithmetic doesn't drift on test runs."""
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


def test_stale_fires_above_threshold(tmp_path, reference_now):
    ts = (reference_now - timedelta(days=SIDECAR_STALE_DAYS + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_sidecar(tmp_path, "stale", {"snapshots": [{"refreshed_at": ts}]})
    assert is_sidecar_stale("stale", now=reference_now, metadata_dir=tmp_path) is True


def test_stale_silent_at_threshold(tmp_path, reference_now):
    """Exactly at SIDECAR_STALE_DAYS should NOT yet be stale (strict >)."""
    ts = (reference_now - timedelta(days=SIDECAR_STALE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_sidecar(tmp_path, "edge", {"snapshots": [{"refreshed_at": ts}]})
    assert is_sidecar_stale("edge", now=reference_now, metadata_dir=tmp_path) is False


def test_stale_silent_when_fresh(tmp_path, reference_now):
    ts = (reference_now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_sidecar(tmp_path, "fresh", {"snapshots": [{"refreshed_at": ts}]})
    assert is_sidecar_stale("fresh", now=reference_now, metadata_dir=tmp_path) is False


def test_stale_silent_when_missing(tmp_path, reference_now):
    """Missing sidecar is the tier-unknown branch, not the stale branch.

    The two branches should be independently testable so future refactors
    can re-route one without disturbing the other.
    """
    assert is_sidecar_stale("nope", now=reference_now, metadata_dir=tmp_path) is False


def test_stale_silent_on_flat_fresh(tmp_path, reference_now):
    """Legacy flat-shape sidecars are honoured by the staleness check too."""
    ts = (reference_now - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_sidecar(tmp_path, "legacy", {"refreshed_at": ts, "stars": 500})
    assert is_sidecar_stale("legacy", now=reference_now, metadata_dir=tmp_path) is False


# ---------------------------------------------------------------------------
# End-to-end: committed graph-data.json must encode the union correctly
# ---------------------------------------------------------------------------


def test_graph_data_data_missing_matches_unknown_tier():
    """Today every catalogue sidecar is fresh, so data_missing == (tier == unknown).

    This pin breaks if either side of the union drifts unexpectedly
    (e.g. someone reverts the stale-sidecar branch, or someone changes
    the unknown-tier branch). A real stale sidecar landing in registry
    will also trip this — which is intentional: we want curators to
    refresh metadata or migrate the entry, not silently accept drift.
    """
    payload = json.loads(
        (REPO_ROOT / "visuals" / "graph-data.json").read_text(encoding="utf-8")
    )
    mismatched = [
        n["id"]
        for n in payload["nodes"]
        if n["data_missing"] != (n["tier"] == "unknown")
    ]
    assert mismatched == [], (
        f"{len(mismatched)} entries have data_missing != (tier == unknown). "
        "Either a stale sidecar slipped in (refresh metadata or accept the "
        "stale flag) or the unknown-tier path was modified without updating "
        "this pin."
    )


def test_graph_data_outline_and_opacity_clamped_on_data_missing():
    payload = json.loads(
        (REPO_ROOT / "visuals" / "graph-data.json").read_text(encoding="utf-8")
    )
    for node in payload["nodes"]:
        if node["data_missing"]:
            assert node["tier_outline"] == "dotted", (
                f"{node['id']}: data_missing nodes must render dotted, "
                f"got {node['tier_outline']!r}"
            )
            assert node["tier_opacity"] <= 0.40, (
                f"{node['id']}: data_missing nodes must fade to <=0.40, "
                f"got {node['tier_opacity']}"
            )
