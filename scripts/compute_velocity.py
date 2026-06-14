"""Derive uptake-velocity stats per entry from sidecar snapshot history.

Reads append-only snapshots from ``registry/_metadata/<id>.json`` and
writes a single ``registry/_metadata/_velocity.json`` that maps each
entry id to numeric velocity stats.

Why
---
Stars alone are a stock measure (cumulative); they over-reward old
projects and under-reward fast-rising newcomers. Velocity is the flow
measure — stars-per-week and commit-recency — that lets the atlas
surface what's gaining traction *right now*, not just what was popular
historically. This is the "uptake velocity" capability the
``layered visibility`` plan asked for.

Output shape
------------

::

    {
      "langgraph": {
        "stars": 34661,
        "stars_per_week_4w": 412.5,    // mean delta over last 4 weeks
        "stars_per_week_12w": 376.2,   // mean delta over last 12 weeks
        "days_since_commit": 0,
        "snapshot_count": 4,           // history depth in this sidecar
        "history_days": 28             // span covered by snapshots
      },
      ...
    }

Entries with fewer than two snapshots get ``stars_per_week_4w: null``
(the data isn't there yet). Sidecars in the legacy flat shape are
treated as a single snapshot.

Usage
-----

::

    python scripts/compute_velocity.py            # write _velocity.json
    python scripts/compute_velocity.py --check    # exit 1 on drift
    python scripts/compute_velocity.py --report   # print top-25 by 4w velocity
    python scripts/compute_velocity.py --rising   # also write docs/rising.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts._atomic import atomic_write_text
except ModuleNotFoundError:
    from _atomic import atomic_write_text  # type: ignore[no-redef]

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
METADATA_DIR = REGISTRY_DIR / "_metadata"
VELOCITY_PATH = METADATA_DIR / "_velocity.json"
RISING_PATH = REPO_ROOT / "docs" / "rising.md"


def _now() -> datetime:
    """Pinned to UTC midnight — see ``compute_tier.py:_now`` for rationale."""
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


NOW = _now()


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


def _snapshots(sidecar: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(sidecar.get("snapshots"), list):
        return sidecar["snapshots"]
    # Legacy flat shape — synthesise one snapshot.
    if sidecar.get("refreshed_at"):
        return [sidecar]
    return []


def _stars_per_week(snapshots: list[dict[str, Any]], window_days: int) -> float | None:
    """Compute mean stars-per-week over the trailing ``window_days``.

    The reference is the latest snapshot. We find the oldest snapshot
    within the window and divide the star delta by the elapsed weeks.
    Returns ``None`` if there are fewer than two snapshots in the window
    or if the time span is too small to be meaningful (<48h).
    """
    if len(snapshots) < 2:
        return None
    latest = snapshots[-1]
    latest_ts = _parse_iso(latest.get("refreshed_at"))
    latest_stars = latest.get("stars")
    if latest_ts is None or not isinstance(latest_stars, int):
        return None
    # Walk back to find the oldest snapshot within ``window_days``.
    window_start = latest_ts.timestamp() - window_days * 86400
    baseline = None
    for snap in snapshots[:-1]:
        ts = _parse_iso(snap.get("refreshed_at"))
        if ts is None:
            continue
        if ts.timestamp() >= window_start:
            baseline = snap
            break
    if baseline is None:
        return None
    baseline_ts = _parse_iso(baseline.get("refreshed_at"))
    baseline_stars = baseline.get("stars")
    if baseline_ts is None or not isinstance(baseline_stars, int):
        return None
    elapsed_seconds = (latest_ts - baseline_ts).total_seconds()
    if elapsed_seconds < 48 * 3600:
        return None
    weeks = elapsed_seconds / (7 * 86400)
    return round((latest_stars - baseline_stars) / weeks, 2)


def _entry_velocity(sidecar: dict[str, Any]) -> dict[str, Any]:
    snapshots = _snapshots(sidecar)
    latest = snapshots[-1] if snapshots else {}
    last_commit = _parse_iso(latest.get("last_commit_at"))
    days_since_commit = (NOW - last_commit).days if last_commit else None

    history_days: int | None = None
    if len(snapshots) >= 2:
        first_ts = _parse_iso(snapshots[0].get("refreshed_at"))
        last_ts = _parse_iso(snapshots[-1].get("refreshed_at"))
        if first_ts and last_ts:
            history_days = max(0, (last_ts - first_ts).days)

    return {
        "stars": latest.get("stars"),
        "stars_per_week_4w": _stars_per_week(snapshots, window_days=28),
        "stars_per_week_12w": _stars_per_week(snapshots, window_days=84),
        "days_since_commit": days_since_commit,
        "snapshot_count": len(snapshots),
        "history_days": history_days,
    }


def _iter_entries() -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(REGISTRY_DIR.glob("*/*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "id" in data:
            out.append((data["id"], data))
    return out


def compute_all() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for entry_id, _ in _iter_entries():
        sidecar_path = METADATA_DIR / f"{entry_id}.json"
        if not sidecar_path.exists():
            continue
        try:
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        out[entry_id] = _entry_velocity(sidecar)
    return out


def _rising_table(
    velocity: dict[str, dict[str, Any]],
    entries: dict[str, dict[str, Any]],
    limit: int = 25,
) -> str:
    # Only include positive-velocity entries: a repo that LOST stars
    # (manipulation, mass-unstar, repo deletion controversy) is not
    # "rising" in the editorial sense the doc title implies.
    ranked = sorted(
        (
            (eid, v)
            for eid, v in velocity.items()
            if isinstance(v.get("stars_per_week_4w"), (int, float))
            and v["stars_per_week_4w"] > 0
        ),
        key=lambda kv: kv[1]["stars_per_week_4w"],
        reverse=True,
    )[:limit]
    lines = [
        "<!-- AUTO-GENERATED by scripts/compute_velocity.py --rising -->",
        "",
        "# Rising harnesses — top 25 by 4-week star velocity",
        "",
        "Velocity is the **flow** measure: stars added per week, averaged over "
        "the trailing 4-week window of refreshed metadata snapshots. It "
        "complements the tier overlay (a **stock** measure: cumulative stars + "
        "age + recency) and surfaces what is gaining traction right now, not "
        "what was popular historically.",
        "",
        "Updated by the scheduled metadata refresh; requires ≥2 weekly "
        "snapshots per entry to compute. Entries with fewer snapshots are "
        "skipped.",
        "",
        "| Rank | Entry | Category | Stars | Stars / week (4w) | Stars / week (12w) | Last commit |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    if not ranked:
        lines.append(
            "| — | _Not enough snapshot history yet._ | | | | | |"
        )
    else:
        for rank, (eid, v) in enumerate(ranked, start=1):
            entry = entries.get(eid, {})
            name = entry.get("name", eid)
            repo_url = entry.get("repo_url", "")
            category = entry.get("category", "")
            stars = v.get("stars")
            spw_4 = v.get("stars_per_week_4w")
            spw_12 = v.get("stars_per_week_12w")
            dsc = v.get("days_since_commit")
            stars_cell = (
                f"{stars / 1000:.1f}k" if isinstance(stars, int) and stars >= 1000 else str(stars or "—")
            )
            spw_4_cell = f"{spw_4:+.1f}" if isinstance(spw_4, (int, float)) else "—"
            spw_12_cell = f"{spw_12:+.1f}" if isinstance(spw_12, (int, float)) else "—"
            dsc_cell = f"{dsc} d ago" if isinstance(dsc, int) else "—"
            link = f"[{name}]({repo_url})" if repo_url else name
            lines.append(
                f"| {rank} | {link} | {category} | {stars_cell} | {spw_4_cell} | {spw_12_cell} | {dsc_cell} |"
            )
    lines.append("")
    lines.append(
        "_Re-run `python scripts/compute_velocity.py --rising` after refreshing "
        "sidecars to update this table._"
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if computed velocity differs from on-disk _velocity.json")
    parser.add_argument("--report", action="store_true",
                        help="Print the top-25 risers by 4-week star velocity")
    parser.add_argument("--rising", action="store_true",
                        help="Also write docs/rising.md (top-25 table)")
    args = parser.parse_args(argv)

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    velocity = compute_all()
    entries_map = {eid: data for eid, data in _iter_entries()}

    if args.report:
        ranked = sorted(
            (
                (eid, v)
                for eid, v in velocity.items()
                if isinstance(v.get("stars_per_week_4w"), (int, float))
                and v["stars_per_week_4w"] > 0
            ),
            key=lambda kv: kv[1]["stars_per_week_4w"],
            reverse=True,
        )[:25]
        if not ranked:
            print("No entries have >=2 snapshots yet -- re-run refresh_metadata.py "
                  "across multiple days to accumulate history.")
        else:
            print(f"{'rank':>4}  {'id':32s}  {'stars':>8s}  {'4w/wk':>8s}  {'12w/wk':>8s}")
            for rank, (eid, v) in enumerate(ranked, start=1):
                print(
                    f"{rank:>4}  {eid:32s}  "
                    f"{v.get('stars') or 0:>8d}  "
                    f"{v.get('stars_per_week_4w') or 0:>8.1f}  "
                    f"{v.get('stars_per_week_12w') or 0:>8.1f}"
                )

    new_text = json.dumps(velocity, indent=2, sort_keys=True) + "\n"

    if args.check:
        existing = VELOCITY_PATH.read_text(encoding="utf-8") if VELOCITY_PATH.exists() else ""
        if existing != new_text:
            sys.stderr.write("drift: _velocity.json does not match computed velocity\n")
            return 1
        if args.rising:
            existing_md = RISING_PATH.read_text(encoding="utf-8") if RISING_PATH.exists() else ""
            rendered = _rising_table(velocity, entries_map) + "\n"
            if existing_md != rendered:
                sys.stderr.write("drift: docs/rising.md does not match computed table\n")
                return 1
        return 0

    atomic_write_text(VELOCITY_PATH, new_text)
    if args.rising:
        RISING_PATH.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(RISING_PATH, _rising_table(velocity, entries_map) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
