"""Refresh per-entry GitHub metadata sidecars under ``registry/_metadata/``.

Pulls thin, mostly-numeric metadata (stars, last commit, latest release,
license SPDX, archived flag, default branch) from the GitHub REST API and
writes one JSON sidecar per registry entry. Hand-curated YAML is never
modified — sidecars are a separate file so curators and the refresh bot
never conflict.

Sidecar shape
-------------

Each sidecar is append-only::

    {
      "created_at": "2022-10-17T03:34:50Z",   // stable repo birthday
      "default_branch": "main",                // stable-ish
      "snapshots": [
        {"refreshed_at": "...", "stars": 1234, "last_commit_at": "...",
         "latest_release": "v1.2", "license_spdx": "MIT", "archived": false},
        ...                                    // newest at tail
      ]
    }

Older snapshots are pruned to ``MAX_SNAPSHOTS`` (≈26 weekly snapshots
≈ 6 months of history) to keep file size bounded. ``compute_velocity.py``
reads this list; ``compute_tier.py`` reads the latest snapshot.

Sidecars written under the legacy *flat* shape (single-snapshot,
no ``snapshots`` key) are migrated automatically on first refresh — the
old fields become the first snapshot.

Usage:
    python scripts/refresh_metadata.py                # refresh all entries
    python scripts/refresh_metadata.py --only id1 id2 # refresh subset
    python scripts/refresh_metadata.py --check        # exit non-zero on drift

Requires ``GITHUB_TOKEN`` in the environment for higher rate limits (60/h
anonymous → 5000/h authenticated). On rate-limit / 4xx / 5xx the existing
sidecar is preserved; nothing is overwritten with junk.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml

try:
    from scripts._atomic import atomic_write_text
except ModuleNotFoundError:
    from _atomic import atomic_write_text  # type: ignore[no-redef]

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
METADATA_DIR = REGISTRY_DIR / "_metadata"
USER_AGENT = "open-harness-atlas-refresh/0.2 (+https://github.com/)"
GH_API = "https://api.github.com"

# Keep ~6 months of weekly snapshots — enough for 4w and 12w velocity.
MAX_SNAPSHOTS = 26
# Don't append a new snapshot if the last one is younger than this. Stops
# multiple same-day refreshes from inflating the snapshot list.
MIN_SNAPSHOT_INTERVAL_HOURS = 12

# Stable fields live at the top level of the sidecar; everything else
# is per-snapshot.
STABLE_FIELDS = ("created_at", "default_branch")
SNAPSHOT_FIELDS = (
    "refreshed_at",
    "stars",
    "last_commit_at",
    "latest_release",
    "license_spdx",
    "archived",
)


def _gh_request(path: str, token: str | None) -> dict[str, Any] | None:
    """GET ``{GH_API}{path}`` and return parsed JSON or ``None`` on error.

    Falls back to an anonymous request if a token-authenticated request
    returns HTTP 403. This handles the common case where the local token
    has not been SAML-SSO authorised for an org (microsoft, Azure, etc) —
    the public REST endpoints still work anonymously, just at a lower
    rate limit. Without this fallback every SAML-protected org becomes
    invisible to the refresh.
    """

    def _do(use_token: bool) -> tuple[dict[str, Any] | None, int | None]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if use_token and token:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(f"{GH_API}{path}", headers=headers)
        try:
            with urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8")), resp.status
        except HTTPError as exc:
            return None, exc.code
        except (URLError, TimeoutError, OSError) as exc:
            sys.stderr.write(f"  ! GET {path} -> {type(exc).__name__}: {exc}\n")
            return None, None

    data, status = _do(use_token=True)
    if data is not None:
        return data
    if status == 403 and token:
        # Probable SAML-SSO block — retry without the token.
        data, status = _do(use_token=False)
        if data is not None:
            return data
    if status is not None:
        sys.stderr.write(f"  ! GET {path} -> HTTP {status}\n")
    return None


def _parse_repo_url(repo_url: str) -> tuple[str, str] | None:
    """Extract ``(owner, repo)`` from a GitHub HTTPS URL."""
    parsed = urlparse(repo_url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def _fetch_one(owner: str, repo: str, token: str | None) -> dict[str, Any] | None:
    repo_meta = _gh_request(f"/repos/{owner}/{repo}", token)
    if not repo_meta:
        return None
    latest_release = _gh_request(f"/repos/{owner}/{repo}/releases/latest", token)
    return {
        "stars": repo_meta.get("stargazers_count"),
        "created_at": repo_meta.get("created_at"),
        "last_commit_at": repo_meta.get("pushed_at"),
        "latest_release": (latest_release or {}).get("tag_name"),
        "license_spdx": (repo_meta.get("license") or {}).get("spdx_id"),
        "archived": repo_meta.get("archived"),
        "default_branch": repo_meta.get("default_branch"),
        "refreshed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _iter_entries() -> list[tuple[str, Path, dict[str, Any]]]:
    entries: list[tuple[str, Path, dict[str, Any]]] = []
    for path in sorted(REGISTRY_DIR.glob("*/*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict) or "id" not in data:
            continue
        entries.append((data["id"], path, data))
    return entries


def _load_existing(sidecar_path: Path) -> dict[str, Any]:
    if not sidecar_path.exists():
        return {"snapshots": []}
    try:
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"snapshots": []}
    if "snapshots" in data and isinstance(data["snapshots"], list):
        return data
    # Migrate flat shape -> snapshot shape (first run after refactor).
    snapshot = {k: data.get(k) for k in SNAPSHOT_FIELDS if k in data}
    migrated = {k: data.get(k) for k in STABLE_FIELDS if data.get(k) is not None}
    migrated["snapshots"] = [snapshot] if snapshot.get("refreshed_at") else []
    return migrated


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


def _merge_snapshot(existing: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    """Append a new snapshot to ``existing`` and prune to MAX_SNAPSHOTS."""
    merged: dict[str, Any] = {}
    for field in STABLE_FIELDS:
        value = fresh.get(field) or existing.get(field)
        if value is not None:
            merged[field] = value

    snapshots = list(existing.get("snapshots", []))
    new_snapshot = {k: fresh.get(k) for k in SNAPSHOT_FIELDS if k in fresh}

    # Suppress a new snapshot if the last one is too recent — keeps the
    # list bounded against accidental rapid refreshes.
    if snapshots:
        last_refresh = _parse_iso(snapshots[-1].get("refreshed_at"))
        this_refresh = _parse_iso(new_snapshot.get("refreshed_at"))
        if last_refresh and this_refresh:
            delta_hours = (this_refresh - last_refresh).total_seconds() / 3600
            if delta_hours < MIN_SNAPSHOT_INTERVAL_HOURS:
                snapshots[-1] = new_snapshot  # in-place replace
            else:
                snapshots.append(new_snapshot)
        else:
            snapshots.append(new_snapshot)
    else:
        snapshots.append(new_snapshot)

    if len(snapshots) > MAX_SNAPSHOTS:
        snapshots = snapshots[-MAX_SNAPSHOTS:]

    merged["snapshots"] = snapshots
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None,
                        help="Limit to these entry ids (default: all).")
    parser.add_argument("--check", action="store_true",
                        help="Compare against committed sidecars; exit 1 on drift.")
    parser.add_argument("--sleep", type=float, default=0.5,
                        help="Seconds between requests (default 0.5).")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.stderr.write("note: GITHUB_TOKEN not set; using anonymous rate limit (60/h).\n")

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    targets = _iter_entries()
    if args.only:
        wanted = set(args.only)
        targets = [t for t in targets if t[0] in wanted]
        missing = wanted - {t[0] for t in targets}
        for mid in sorted(missing):
            sys.stderr.write(f"  ! unknown id: {mid}\n")

    drifted: list[str] = []
    for entry_id, _entry_path, data in targets:
        parsed = _parse_repo_url(data.get("repo_url", ""))
        if parsed is None:
            sys.stderr.write(f"  - {entry_id}: non-GitHub repo_url, skipping\n")
            continue
        owner, repo = parsed
        print(f"  + {entry_id} ({owner}/{repo})")
        fresh = _fetch_one(owner, repo, token)
        if fresh is None:
            sys.stderr.write(f"  - {entry_id}: fetch failed, sidecar preserved\n")
            time.sleep(args.sleep)
            continue
        sidecar_path = METADATA_DIR / f"{entry_id}.json"
        existing = _load_existing(sidecar_path)
        merged = _merge_snapshot(existing, fresh)
        new_text = json.dumps(merged, indent=2, sort_keys=True) + "\n"
        if args.check:
            existing_text = sidecar_path.read_text(encoding="utf-8") if sidecar_path.exists() else ""
            # Ignore the volatile refreshed_at field on the latest snapshot for the drift check.
            if _strip_refreshed_at(existing_text) != _strip_refreshed_at(new_text):
                drifted.append(entry_id)
        else:
            # Atomic write — see scripts/_atomic.py. Same-directory .tmp +
            # os.replace prevents partial-JSON corruption (and silent
            # snapshot-history loss via the JSONDecodeError fallback in
            # _load_existing) if the process is killed mid-write.
            atomic_write_text(sidecar_path, new_text)
        time.sleep(args.sleep)

    if args.check and drifted:
        sys.stderr.write(
            f"drift detected in {len(drifted)} sidecar(s): {', '.join(sorted(drifted))}\n"
        )
        return 1
    return 0


def _strip_refreshed_at(text: str) -> str:
    """Normalise both flat and snapshot shapes to the same comparable form.

    The drift check (``--check``) needs to compare what is committed against
    what would be written, ignoring the volatile ``refreshed_at`` timestamp
    on the latest snapshot. Because committed sidecars may still be in the
    legacy flat shape while the new write is always snapshot-shape, naive
    JSON comparison reports false-positive drift on every entry.

    We normalise both inputs to snapshot-shape first, then strip
    ``refreshed_at`` from the latest snapshot, then re-serialise. This means
    a flat sidecar is only flagged as drifted if its underlying data
    (stars / last_commit_at / archived / etc) actually changed — which is
    what the check is supposed to detect.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text
    if not isinstance(data, dict):
        return text

    # Normalise flat shape -> snapshot shape so both inputs are comparable.
    if not isinstance(data.get("snapshots"), list):
        snapshot = {k: data.get(k) for k in SNAPSHOT_FIELDS if k in data}
        normalised: dict[str, Any] = {
            k: data.get(k) for k in STABLE_FIELDS if data.get(k) is not None
        }
        normalised["snapshots"] = [snapshot] if snapshot.get("refreshed_at") else []
        data = normalised

    if data["snapshots"]:
        data["snapshots"][-1].pop("refreshed_at", None)
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
