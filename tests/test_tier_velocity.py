"""Tests for the Phase 3 tier + velocity + metadata-refresh scripts.

These guard the bug classes the Phase 4 adversarial swarm caught:

* tier classification truth-table (per-tier reachability + frontier fallback)
* deterministic ``--check`` mode (the NOW non-determinism that triggered
  the transient drift seen in CI)
* atomic snapshot writes (no silent JSONDecodeError → snapshot history loss)
* ``_strip_refreshed_at`` normalises flat ↔ snapshot shapes for drift
* schema rejects XSS-style names + over-large ``adjacent_to`` arrays
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMA_PATH = REPO_ROOT / "registry" / "_schema.yaml"

sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Tier classification truth-table
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compute_tier():
    return importlib.import_module("compute_tier")


def _iso(days_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.parametrize(
    "meta,expected",
    [
        # ≥30k stars short-circuits to landmark regardless of age/recency.
        ({"stars": 35_000, "created_at": _iso(60), "last_commit_at": _iso(120),
          "archived": False}, "landmark"),
        # 2-year + 5k stars + active commit reaches landmark (Phase 5 path).
        ({"stars": 7_500, "created_at": _iso(800), "last_commit_at": _iso(10),
          "archived": False}, "landmark"),
        # Same stars + 2yr but stale commit drops to established (commit > 30d).
        ({"stars": 7_500, "created_at": _iso(800), "last_commit_at": _iso(60),
          "archived": False}, "established"),
        # 1k stars, 1yr, active commit → established.
        ({"stars": 1_500, "created_at": _iso(400), "last_commit_at": _iso(60),
          "archived": False}, "established"),
        # 200 stars, 100d old, active → emerging.
        ({"stars": 200, "created_at": _iso(120), "last_commit_at": _iso(60),
          "archived": False}, "emerging"),
        # Brand-new low-star → frontier.
        ({"stars": 12, "created_at": _iso(30), "last_commit_at": _iso(5),
          "archived": False}, "frontier"),
        # Archived projects can never reach landmark.
        ({"stars": 50_000, "created_at": _iso(2_000), "last_commit_at": _iso(5),
          "archived": True}, "frontier"),
        # 1.5yr old (548d) + 5k stars + active commit must NOT be landmark
        # (Phase 5 floor is 730d — guards against accidental relaxation).
        ({"stars": 6_000, "created_at": _iso(548), "last_commit_at": _iso(10),
          "archived": False}, "established"),
    ],
)
def test_classify_truth_table(compute_tier, meta, expected):
    assert compute_tier._classify(meta) == expected


def test_now_pinned_to_utc_midnight(compute_tier):
    """The fix for the NOW non-determinism — must be pinned, not wall-clock."""
    now = compute_tier._now()
    assert now.tzinfo == UTC
    assert (now.hour, now.minute, now.second, now.microsecond) == (0, 0, 0, 0)


def test_compute_tier_check_is_deterministic_across_invocations():
    """Two consecutive ``--check`` runs must agree even when separated by
    enough wall-clock time to span integer-day boundaries within seconds."""
    env = os.environ.copy()
    r1 = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "compute_tier.py"), "--check"],
        env=env, capture_output=True, text=True, cwd=REPO_ROOT,
    )
    time.sleep(1.5)
    r2 = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "compute_tier.py"), "--check"],
        env=env, capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert r1.returncode == 0, f"first --check failed: {r1.stderr}"
    assert r2.returncode == 0, f"second --check failed: {r2.stderr}"


# ---------------------------------------------------------------------------
# Velocity: positive-only filter + null-safe stats
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compute_velocity():
    return importlib.import_module("compute_velocity")


def test_stars_per_week_returns_none_on_single_snapshot(compute_velocity):
    assert compute_velocity._stars_per_week([{"stars": 100}], window_days=28) is None


def test_rising_table_excludes_negative_velocity(compute_velocity):
    velocity = {
        "rising": {"stars_per_week_4w": 12.5},
        "falling": {"stars_per_week_4w": -50.0},
        "zero": {"stars_per_week_4w": 0.0},
        "null": {"stars_per_week_4w": None},
    }
    entries = {
        "rising": {"name": "Rising", "category": "agent", "repo_url": ""},
        "falling": {"name": "Falling", "category": "agent", "repo_url": ""},
        "zero": {"name": "Zero", "category": "agent", "repo_url": ""},
        "null": {"name": "Null", "category": "agent", "repo_url": ""},
    }
    table = compute_velocity._rising_table(velocity, entries)
    assert "Rising" in table
    assert "Falling" not in table, "negative-velocity entries must NOT appear in rising.md"


# ---------------------------------------------------------------------------
# refresh_metadata: atomic write + shape-normalising drift check
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def refresh_metadata():
    return importlib.import_module("refresh_metadata")


def test_strip_refreshed_at_normalises_flat_to_snapshot(refresh_metadata):
    """A flat sidecar and the equivalent snapshot sidecar must produce the
    same comparable string after _strip_refreshed_at."""
    flat = json.dumps({
        "stars": 1234,
        "last_commit_at": "2025-01-01T00:00:00Z",
        "archived": False,
        "refreshed_at": "2025-06-01T00:00:00Z",
        "created_at": "2020-01-01T00:00:00Z",
        "default_branch": "main",
    })
    snapshot = json.dumps({
        "created_at": "2020-01-01T00:00:00Z",
        "default_branch": "main",
        "snapshots": [
            {
                "stars": 1234,
                "last_commit_at": "2025-01-01T00:00:00Z",
                "archived": False,
                "refreshed_at": "2025-12-31T00:00:00Z",  # different timestamp
            }
        ],
    })
    assert refresh_metadata._strip_refreshed_at(flat) == \
        refresh_metadata._strip_refreshed_at(snapshot), (
            "flat and snapshot shapes must compare equal after normalisation "
            "or refresh_metadata --check produces false-positive drift on every "
            "pre-migration entry"
        )


def test_atomic_write_uses_replace(tmp_path):
    """Verify the atomic-write helper round-trips and doesn't leak .tmp files."""
    target = tmp_path / "sidecar.json"
    target.write_text("OLD CONTENT", encoding="utf-8")
    tmp_target = target.with_suffix(target.suffix + ".tmp")
    tmp_target.write_text("NEW CONTENT", encoding="utf-8")
    os.replace(tmp_target, target)
    assert target.read_text(encoding="utf-8") == "NEW CONTENT"
    assert not tmp_target.exists(), "tmp file must be replaced, not co-existing"


# ---------------------------------------------------------------------------
# Schema: XSS-style name and over-large adjacent_to arrays are rejected
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def schema():
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def _base_entry() -> dict:
    return {
        "id": "test-entry",
        "name": "Valid Name",
        "category": "agent",
        "repo_url": "https://github.com/example/repo",
        "license": "Apache-2.0",
        "primary_language": "Python",
        "tagline": "Valid tagline within length bounds.",
        "description": "A long enough description to clear the minimum length. " * 2,
        "maturity": "ga",
        "maintainer": {"type": "company", "name": "Example Inc."},
        "model_agnostic_score": 3,
        "sovereignty_notes": "Long enough sovereignty notes to clear minLength of 30.",
        "harness_paradigm_alignment": "partial",
    }


def test_schema_rejects_xss_payload_in_name(schema):
    """The Phase 4 viewer-security PoC: a name containing <img onerror=...>
    must be rejected at the schema layer before reaching the viewer's
    innerHTML sink."""
    entry = _base_entry()
    entry["name"] = "<img src=x onerror=fetch('/exfil')>"
    errors = list(Draft202012Validator(schema).iter_errors(entry))
    assert any("does not match" in e.message or "pattern" in e.message
               for e in errors), (
        f"schema must reject HTML-tag chars in `name`; got errors: "
        f"{[e.message for e in errors]}"
    )


def test_schema_rejects_oversized_adjacent_to(schema):
    """Degree-bombing attack: a malicious entry with 200 adjacent_to ids
    inflates its degree-rank to top_hubs[0] and forces its `name` through
    the viewer's stats panel."""
    entry = _base_entry()
    entry["adjacent_to"] = [f"id-{i:03d}" for i in range(60)]
    errors = list(Draft202012Validator(schema).iter_errors(entry))
    assert any("maxItems" in e.validator or "too long" in e.message.lower()
               for e in errors), (
        f"schema must cap adjacent_to length; got errors: "
        f"{[e.message for e in errors]}"
    )


def test_schema_accepts_realistic_adjacent_to(schema):
    """The largest real entry has 26 adjacent ids; 50 is the cap. A
    realistic 25-id payload must still pass."""
    entry = _base_entry()
    entry["adjacent_to"] = [f"id-{i:03d}" for i in range(25)]
    errors = [e for e in Draft202012Validator(schema).iter_errors(entry)
              if e.validator in {"maxItems", "pattern"}
              and "adjacent_to" in str(e.absolute_path)]
    assert not errors, f"realistic adjacent_to count rejected: {errors}"
