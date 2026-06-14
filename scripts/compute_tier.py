"""Derive adoption tier per registry entry from metadata sidecars.

Tier is **computed**, not self-reported in YAML — this prevents curators
from inflating their own entries. The tier is consumed by
``build_graph.py`` (visual encoding in the 3D + 2D viewers) and
``build_matrices.py`` (matrix columns).

Tier ladder
-----------

==============  ===========================================  ============================
Tier            Heuristic                                    Visual encoding (viewers)
==============  ===========================================  ============================
``landmark``    ≥30k stars **OR** ≥3 yr age AND ≥5k stars    Full opacity · larger radius
                AND last-commit ≤30 d                         · solid outline
``established`` ≥1k stars · ≥1 yr age · last-commit ≤180 d   Full opacity · normal radius
``emerging``    ≥100 stars · ≥3 mo age · last-commit ≤180 d  70% opacity · normal radius
``frontier``    everything else that passes inclusion        40% opacity · dashed outline
                criteria                                      · smaller radius
``unknown``     sidecar missing or fetch failed              Renders as ``frontier``
==============  ===========================================  ============================

The thresholds are deliberately conservative to keep ``landmark`` rare
(target ~5-10% of the catalog) and to keep ``frontier`` visually
honest about what it means: an entry that passes inclusion criteria
but has not yet accumulated independent adoption signal.

Usage
-----

::

    python scripts/compute_tier.py                # write registry/_metadata/_tiers.json
    python scripts/compute_tier.py --check        # exit 1 on drift
    python scripts/compute_tier.py --report       # print distribution

The output file ``registry/_metadata/_tiers.json`` is the
single-source-of-truth for tier per ``id``; ``build_graph.py`` and
``build_matrices.py`` both read it.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
METADATA_DIR = REGISTRY_DIR / "_metadata"
TIERS_PATH = METADATA_DIR / "_tiers.json"

TIER_LANDMARK = "landmark"
TIER_ESTABLISHED = "established"
TIER_EMERGING = "emerging"
TIER_FRONTIER = "frontier"
TIER_UNKNOWN = "unknown"

NOW = datetime.now(UTC)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None


def _age_days(created_at: str | None, last_commit_at: str | None) -> tuple[int | None, int | None]:
    """Return (age_days_since_first_seen, days_since_last_commit)."""
    created = _parse_iso(created_at)
    last = _parse_iso(last_commit_at)
    age = (NOW - created).days if created else None
    recency = (NOW - last).days if last else None
    return age, recency


def _classify(meta: dict[str, Any]) -> str:
    stars = meta.get("stars")
    last_commit_at = meta.get("last_commit_at")
    created_at = meta.get("created_at")
    archived = meta.get("archived", False)

    if archived:
        # Archived projects can still be referenced but don't earn an active tier.
        return TIER_FRONTIER

    age_days, days_since_commit = _age_days(created_at, last_commit_at)
    have_age = age_days is not None

    # Landmark: very high stars OR (mature + active + popular).
    # Threshold tuned against the actual catalogue (804 entries):
    # ≥30k stars sits around the 8% mark which keeps the landmark tier
    # visually rare. The age path catches established popular projects
    # that haven't crossed 30k yet but have a clear track record.
    if isinstance(stars, int) and stars >= 30_000:
        return TIER_LANDMARK
    if (
        isinstance(stars, int)
        and stars >= 5_000
        and have_age
        and age_days >= 3 * 365
        and days_since_commit is not None
        and days_since_commit <= 30
    ):
        return TIER_LANDMARK

    # Established: solid stars, year-old, actively maintained.
    # Fallback when ``created_at`` is unavailable: require a higher star
    # threshold (3k+) as a proxy for maturity. Most projects don't reach
    # 3k stars in under a year.
    if (
        isinstance(stars, int)
        and days_since_commit is not None
        and days_since_commit <= 180
        and (
            (stars >= 1_000 and have_age and age_days >= 365)
            or (stars >= 3_000 and not have_age)
        )
    ):
        return TIER_ESTABLISHED

    # Emerging: meaningful traction, a few months old, recently active.
    # Fallback when ``created_at`` is unavailable: require a slightly
    # higher star threshold (300+) as a maturity proxy.
    if (
        isinstance(stars, int)
        and days_since_commit is not None
        and days_since_commit <= 180
        and (
            (stars >= 100 and have_age and age_days >= 90)
            or (stars >= 300 and not have_age)
        )
    ):
        return TIER_EMERGING

    # Frontier: passes inclusion criteria but no independent adoption signal yet.
    return TIER_FRONTIER


def _iter_entries() -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for path in sorted(REGISTRY_DIR.glob("*/*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "id" in data:
            out.append((data["id"], path))
    return out


def _load_sidecar(entry_id: str) -> dict[str, Any] | None:
    path = METADATA_DIR / f"{entry_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def compute_all() -> dict[str, str]:
    out: dict[str, str] = {}
    for entry_id, _ in _iter_entries():
        sidecar = _load_sidecar(entry_id)
        if not sidecar:
            out[entry_id] = TIER_UNKNOWN
            continue
        # Support both flat (current) and snapshotted (post-Phase-3d) shapes.
        if "snapshots" in sidecar and sidecar["snapshots"]:
            latest = sidecar["snapshots"][-1]
            meta = {
                "stars": latest.get("stars"),
                "last_commit_at": latest.get("last_commit_at"),
                "created_at": sidecar.get("created_at") or latest.get("created_at"),
                "archived": latest.get("archived", False),
            }
        else:
            meta = {
                "stars": sidecar.get("stars"),
                "last_commit_at": sidecar.get("last_commit_at"),
                "created_at": sidecar.get("created_at"),
                "archived": sidecar.get("archived", False),
            }
        out[entry_id] = _classify(meta)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if computed tiers drift from on-disk _tiers.json")
    parser.add_argument("--report", action="store_true",
                        help="Print tier distribution")
    args = parser.parse_args(argv)

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    tiers = compute_all()

    if args.report:
        dist = Counter(tiers.values())
        total = sum(dist.values())
        print("Tier distribution")
        print("-----------------")
        for tier in (TIER_LANDMARK, TIER_ESTABLISHED, TIER_EMERGING, TIER_FRONTIER, TIER_UNKNOWN):
            count = dist.get(tier, 0)
            pct = 100.0 * count / total if total else 0.0
            print(f"  {tier:13s} {count:4d}  ({pct:5.1f}%)")
        print(f"  {'total':13s} {total:4d}")

    new_text = json.dumps(tiers, indent=2, sort_keys=True) + "\n"

    if args.check:
        existing = TIERS_PATH.read_text(encoding="utf-8") if TIERS_PATH.exists() else ""
        if existing != new_text:
            sys.stderr.write("drift: _tiers.json does not match computed tiers\n")
            return 1
        return 0

    TIERS_PATH.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
