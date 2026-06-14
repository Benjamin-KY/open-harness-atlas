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
    # Pin to UTC midnight so the gap (compute_tier._now() - parsed) is exactly
    # ``days_ago`` integer days regardless of wall-clock time of day. Without
    # this pinning the boundary cases in the truth-table (e.g. exactly 547d
    # or 548d idle for the dormant tier) become flaky depending on when the
    # tests happen to run.
    midnight = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.parametrize(
    "meta,expected",
    [
        # ≥30k stars short-circuits to landmark regardless of age/recency
        # (provided it's still active — the post-canonical-priority dormant
        # rule keeps multi-year-idle high-star projects in canonical/dormant
        # rather than letting them re-enter landmark).
        ({"stars": 35_000, "created_at": _iso(60), "last_commit_at": _iso(120),
          "archived": False}, "landmark"),
        # 2-year + 5k stars + active commit reaches landmark (Phase 5 path).
        ({"stars": 7_500, "created_at": _iso(800), "last_commit_at": _iso(10),
          "archived": False}, "landmark"),
        # Same stars + 2yr but stale commit drops to established (commit > 30d
        # but ≤ 180d still passes the established path).
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
        # Archived projects can never reach landmark — but archived + ≥5k stars
        # earns the ``canonical`` tier (post-launch 2026-06-14 follow-up; previously
        # collapsed into ``frontier`` and rendered as dim long-tail).
        ({"stars": 50_000, "created_at": _iso(2_000), "last_commit_at": _iso(5),
          "archived": True}, "canonical"),
        # Archived but <5k stars and recent commit (≤547d idle) stays in frontier.
        # The dormant tier only catches >547d-idle entries; this one is 60d-idle
        # so it falls through canonical and dormant and lands in frontier.
        ({"stars": 1_200, "created_at": _iso(1_000), "last_commit_at": _iso(60),
          "archived": True}, "frontier"),
        # Archived + exactly 5k stars (canonical floor) still earns canonical.
        ({"stars": 5_000, "created_at": _iso(900), "last_commit_at": _iso(30),
          "archived": True}, "canonical"),
        # Archived + ≥5k stars + multi-year idle stays canonical (canonical
        # takes priority over dormant for iconic reference impls).
        ({"stars": 12_000, "created_at": _iso(2_000), "last_commit_at": _iso(900),
          "archived": True}, "canonical"),
        # Relaxed-recency established path: ≥20k stars + last commit ≤365d
        # would normally rescue foundational projects that don't push weekly
        # (anthropics/courses at 212d, microsoft/JARVIS at 319d). Under the
        # v0.4.0 canonical (2) expansion this case is PRE-EMPTED by canonical
        # for entries that match both — a 22k-star + 800d age + 300d-idle
        # project is quiet-iconic, so canonical wins. The relaxed-established
        # path now only catches stars≥20k + age<365d (e.g. a recent popular
        # fork), which is rare in practice.
        ({"stars": 22_000, "created_at": _iso(800), "last_commit_at": _iso(300),
          "archived": False}, "canonical"),
        # Sub-canonical research-cadence cohort: ≥200 + ≥6mo + ≤365d-idle
        # → emerging via the v0.4.0 research-cadence path. A 1.5k-star
        # project at 300d stale used to fall to frontier; under v0.4.0 it
        # legitimately reads as "emerging-but-quiet" research work and the
        # research-cadence emerging path catches it.
        ({"stars": 1_500, "created_at": _iso(800), "last_commit_at": _iso(300),
          "archived": False}, "emerging"),
        # LLM-era research-cadence established path: ≥2k stars + ≥1yr age +
        # ≤365d idle. Catches LiveBench-class harnesses (research benchmarks
        # that ship quarterly rather than weekly).
        ({"stars": 2_500, "created_at": _iso(500), "last_commit_at": _iso(300),
          "archived": False}, "established"),
        # The research-cadence path is bounded by 365d — at 400d idle it must
        # NOT promote to established (and would land in frontier if not >547d).
        ({"stars": 2_500, "created_at": _iso(500), "last_commit_at": _iso(400),
          "archived": False}, "frontier"),
        # 1.5yr old (548d) + 5k stars + active commit must NOT be landmark
        # (Phase 5 floor is 730d — guards against accidental relaxation).
        ({"stars": 6_000, "created_at": _iso(548), "last_commit_at": _iso(10),
          "archived": False}, "established"),
        # Canonical (2) — non-archived quiet-iconic: ≥5k stars + ≥1yr +
        # >180d idle. agentgpt-class (164k★, ~16mo idle, not archived).
        ({"stars": 164_000, "created_at": _iso(1_200), "last_commit_at": _iso(480),
          "archived": False}, "canonical"),
        # Canonical (2) — quiet-stable: 10k stars + 2yr + 300d idle, not archived.
        # Previously fell to frontier despite being an unambiguous reference impl.
        ({"stars": 10_000, "created_at": _iso(800), "last_commit_at": _iso(300),
          "archived": False}, "canonical"),
        # Canonical (2) lower bound: ≥5k stars + ≥1yr + >180d (not ≥180d).
        # At exactly 180d idle the entry must NOT earn canonical (it should
        # fall to established via the relaxed-recency 7.5k-2yr path, but here
        # we test a 6k-1.5yr entry whose only path would be established-strict
        # — and 180d sits ON the boundary, so by the >180d definition we are
        # checking the strict-180-day established path).
        ({"stars": 6_000, "created_at": _iso(500), "last_commit_at": _iso(180),
          "archived": False}, "established"),
        # Canonical (2) iconic-but-very-quiet: must beat dormant priority.
        # karpathy/minGPT-class (22k★, ~5yr age, ~4yr idle, not archived).
        # >547d idle would normally trigger dormant, but canonical fires first.
        ({"stars": 22_000, "created_at": _iso(2_000), "last_commit_at": _iso(1_500),
          "archived": False}, "canonical"),
        # Dormant — low-star quiet long-tail: 700 stars + 700d age + 700d idle,
        # not archived. Fails canonical (stars < 5k), days_since_commit > 547d
        # so dormant fires. Without this tier these academic-leftover entries
        # were rendering identical to "no signal yet" frontier nodes.
        ({"stars": 700, "created_at": _iso(700), "last_commit_at": _iso(700),
          "archived": False}, "dormant"),
        # Dormant — exactly at 18mo boundary: 547d idle is NOT dormant (must
        # be strictly > 547d). At 548d the entry is dormant.
        ({"stars": 50, "created_at": _iso(800), "last_commit_at": _iso(547),
          "archived": False}, "frontier"),
        ({"stars": 50, "created_at": _iso(800), "last_commit_at": _iso(548),
          "archived": False}, "dormant"),
        # Dormant + archived but <5k: dormant takes the entry first (it's
        # never reached the archived→frontier fallthrough).
        ({"stars": 800, "created_at": _iso(1_000), "last_commit_at": _iso(900),
          "archived": True}, "dormant"),
        # Emerging research-cadence path: ≥200 stars + ≥6mo age + ≤365d idle.
        # 300 stars, 200d age, 200d idle. The strict path fails (idle > 180d
        # for emerging-strict), but the research-cadence path catches it.
        ({"stars": 300, "created_at": _iso(200), "last_commit_at": _iso(200),
          "archived": False}, "emerging"),
        # Emerging research-cadence lower bound: 200 stars + 180d + 365d
        # idle — the boundary case. Must still emerge.
        ({"stars": 200, "created_at": _iso(180), "last_commit_at": _iso(365),
          "archived": False}, "emerging"),
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
    """Verify the inline atomic-write pattern round-trips and doesn't leak .tmp files.

    Kept as a pattern-only check; the actual production wrapper has its
    own focused tests in :mod:`test_atomic_write` (round-trip, crash
    safety, regression pin that each critical writer imports the helper).
    """
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
