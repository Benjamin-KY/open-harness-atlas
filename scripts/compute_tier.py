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
``landmark``    ≥30k stars AND last-commit ≤547 d            Full opacity · larger radius
                **OR** ≥2 yr age AND ≥5k stars                · solid outline
                AND last-commit ≤30 d
``canonical``   ``archived: true`` AND ≥5k stars             Full opacity · slightly larger
                **OR** ≥5k stars AND ≥1 yr age AND            · solid outline · distinct
                last-commit >180 d (quiet stable /            purple swatch — signals
                quiet iconic reference impl)                  "reference impl / feature-
                                                              complete" rather than dim
                                                              long-tail
``established`` ≥1k stars · ≥1 yr age · last-commit ≤180 d   Full opacity · normal radius
                **OR** ≥20k stars · last-commit ≤365 d
                (relaxed-recency path for foundational
                projects with a slow cadence)
                **OR** ≥2k stars · ≥1 yr · last-commit ≤365 d
                (LLM-era research-cadence path — catches
                academic / lab harnesses with quarterly
                rather than weekly commits)
``emerging``    ≥100 stars · ≥3 mo age · last-commit ≤180 d  70% opacity · normal radius
                **OR** ≥200 stars · ≥6 mo age · ≤365 d
                (LLM-era research-cadence path; higher
                star floor compensates for relaxed recency)
``dormant``     last-commit >18 mo AND not captured by       50% opacity · normal radius
                canonical above (low-star quiet projects     · solid outline · slate swatch
                that still pass inclusion criteria but
                show no recent maintenance signal)
``frontier``    everything else that passes inclusion        40% opacity · dashed outline
                criteria                                      · smaller radius
``unknown``     sidecar missing or fetch failed              40% opacity · dotted outline
                                                              · the graph payload sets
                                                              ``data_missing: true`` so
                                                              the viewer can distinguish
                                                              "no signal yet" from
                                                              "data unavailable"
==============  ===========================================  ============================

The thresholds are deliberately conservative to keep ``landmark`` rare
(target ~10-15% of the catalog, matching the live distribution) and to
keep ``frontier`` visually honest about what it means: an entry that
passes inclusion criteria but has not yet accumulated independent
adoption signal.

The 2-year age requirement (Phase 5 calibration; previously 3-year)
relaxes just enough to admit LLM-era harnesses (autogen, langgraph,
crewai) without admitting fast-rising single-year hype projects.

The ``canonical`` tier (Phase 6 v0.4.0 expansion) catches two cohorts:
(1) archived household-name reference impls (``huggingface/text-generation-inference``,
``microsoft/TaskWeaver``) and (2) non-archived but quiet-stable / quiet-iconic
projects with ≥5k stars and >180d since last commit (``agentgpt``,
``storm``, ``karpathy/minGPT``, ``generative-agents-stanford``). Both
cohorts are reference impls every reader expects to find; without the
canonical tier they collapsed into ``frontier`` and rendered as dim
long-tail nodes.

The ``dormant`` tier (Phase 6 v0.4.0) catches entries past 18 months
since their last commit that did not earn canonical above. It is
visually distinct from frontier because a dormant entry has a history
the catalogue can vouch for; it just hasn't been touched recently. A
frontier entry, by contrast, is one that might earn its first big
commit any day. Conflating the two under ``frontier`` left ~150 eval
shelf entries (LLM-era research benchmarks that publish-and-don't-update
by design) visually indistinguishable from genuinely-pre-adoption work.

The LLM-era research-cadence paths in ``established`` (≥2k stars + 1yr
+ 365d recency) and ``emerging`` (≥200 stars + 6mo + 365d recency) are
the second half of the Phase 6 recalibration — they admit the academic /
lab harnesses whose maintainers ship quarterly rather than weekly,
without admitting fast-rising hype projects with no track record.

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

try:
    # Module-style invocation: ``python -m scripts.compute_tier``.
    from scripts._atomic import atomic_write_text
except ModuleNotFoundError:
    # Direct-script invocation: ``python scripts/compute_tier.py`` (CI).
    # The script's own directory is on sys.path; the helper lives there.
    from _atomic import atomic_write_text  # type: ignore[no-redef]

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
METADATA_DIR = REGISTRY_DIR / "_metadata"
TIERS_PATH = METADATA_DIR / "_tiers.json"

TIER_LANDMARK = "landmark"
TIER_CANONICAL = "canonical"
TIER_ESTABLISHED = "established"
TIER_EMERGING = "emerging"
TIER_DORMANT = "dormant"
TIER_FRONTIER = "frontier"
TIER_UNKNOWN = "unknown"


def _now() -> datetime:
    """Wall-clock UTC midnight — used only as a *fallback* reference date.

    The primary reference for age/recency is each entry's own
    ``refreshed_at`` (see :func:`_reference_date`). This wall-clock value is
    used only when a sidecar has no ``refreshed_at`` (legacy data, or the
    truth-table unit metas). Pinned to midnight so two consecutive process
    invocations in the same day agree.
    """
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


NOW = _now()


def _reference_date(meta: dict[str, Any]) -> datetime:
    """As-of date for age/recency: the entry's own metadata-snapshot date.

    Pinned to the data (``refreshed_at``), not wall-clock, so a tier is a
    pure function of the committed sidecar and changes *only* when a
    metadata refresh changes the underlying data. Without this, an entry
    sitting near an age/recency threshold (e.g. ``tambo`` at the 730-day
    landmark floor) flips tier as wall-clock time advances — drifting
    ``_tiers.json`` away from the committed snapshot and breaking the
    ``compute_tier.py --check`` gate on *any* push, with zero code or data
    changes. Falls back to wall-clock UTC midnight only when ``refreshed_at``
    is absent (truth-table unit metas, or sidecars predating the field).
    """
    ref = _parse_iso(meta.get("refreshed_at"))
    if ref is not None:
        return ref.replace(hour=0, minute=0, second=0, microsecond=0)
    return NOW


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


def _age_days(
    ref: datetime, created_at: str | None, last_commit_at: str | None
) -> tuple[int | None, int | None]:
    """Return (age_days_since_first_seen, days_since_last_commit) as of ``ref``."""
    created = _parse_iso(created_at)
    last = _parse_iso(last_commit_at)
    age = (ref - created).days if created else None
    recency = (ref - last).days if last else None
    return age, recency


def _classify(meta: dict[str, Any]) -> str:
    stars = meta.get("stars")
    last_commit_at = meta.get("last_commit_at")
    created_at = meta.get("created_at")
    archived = meta.get("archived", False)

    ref = _reference_date(meta)
    age_days, days_since_commit = _age_days(ref, created_at, last_commit_at)
    have_age = age_days is not None

    # Canonical (1): archived AND ≥5k stars — historically significant reference
    # implementations whose maintainers signalled "this is done" or moved on
    # (huggingface/text-generation-inference, microsoft/TaskWeaver). Checked
    # before the landmark/dormant paths because an archived household-name
    # reads as "canonical reference impl", not "dormant long-tail".
    if archived and isinstance(stars, int) and stars >= 5_000:
        return TIER_CANONICAL

    # Canonical (2): non-archived but quiet-stable or quiet-iconic.
    # ≥5k stars + ≥1 yr age + >180 d since last commit. Captures the cohort
    # of unambiguous reference impls whose maintainers shipped a thing and
    # moved on without archiving the repo — agentgpt (164k★, ~16 mo idle),
    # storm (~10k★, ~18 mo idle), karpathy/minGPT (~22k★, multi-year idle),
    # generative-agents-stanford (~17k★, ~2 yr idle). Without this tier
    # they fall into frontier or dormant and render as dim long-tail despite
    # being the reference points every reader expects to see. The 5k star
    # floor and 1 yr age floor keep this tier honest — single-year flashes
    # with brief star spikes can't qualify.
    if (
        not archived
        and isinstance(stars, int)
        and stars >= 5_000
        and have_age
        and age_days >= 365
        and days_since_commit is not None
        and days_since_commit > 180
    ):
        return TIER_CANONICAL

    # Dormant: > 18 months (547 d) since last commit AND did not earn
    # canonical above. This is the long tail of quiet projects that pass
    # inclusion criteria but show no recent maintenance signal. Visually
    # distinct from ``frontier`` because a dormant entry has history the
    # catalogue can vouch for — it just hasn't been touched recently. A
    # frontier entry, by contrast, is one that might still earn its first
    # big commit any day.
    #
    # Placed AFTER canonical so that iconic-but-quiet projects (karpathy
    # minGPT) stay canonical rather than collapsing into dormant; placed
    # BEFORE the landmark/established/emerging paths so that a project
    # idle for years can't accidentally re-earn an "active" tier from
    # high star count alone.
    if days_since_commit is not None and days_since_commit > 547:
        return TIER_DORMANT

    if archived:
        # Other archived projects (≥5k stars + <18mo idle didn't fire
        # canonical above; long-idle archived would have fired dormant).
        # Anything reaching here is archived + <5k stars + ≤547 d idle —
        # falls through to frontier so it visibly reads as "low signal".
        return TIER_FRONTIER

    # Landmark: very high stars OR (mature + active + popular).
    # Threshold tuned against the actual catalogue (804 entries):
    # ≥30k stars sits around the 8% mark which keeps the landmark tier
    # visually rare. The age path catches established popular projects
    # that haven't crossed 30k yet but have a clear track record.
    #
    # The 2-year age threshold (730 days) is the Phase 5 calibration —
    # the previous 3-year (1095-day) requirement excluded every LLM-era
    # harness even when stars+activity clearly placed them in the
    # landmark bracket. 730 days is still mature enough to filter out
    # single-year hype projects while admitting the 2023+ canon.
    if isinstance(stars, int) and stars >= 30_000:
        return TIER_LANDMARK
    if (
        isinstance(stars, int)
        and stars >= 5_000
        and have_age
        and age_days >= 730
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

    # Established (relaxed-recency path): ≥20k stars projects with a slow
    # commit cadence (>180d but ≤365d) — catches foundational works whose
    # maintainers don't push weekly (anthropics/courses, microsoft/JARVIS)
    # but which are unambiguously "established" by any reasonable reader.
    if (
        isinstance(stars, int)
        and stars >= 20_000
        and days_since_commit is not None
        and days_since_commit <= 365
    ):
        return TIER_ESTABLISHED

    # Established (LLM-era research-cadence path): ≥2k stars + ≥1yr age +
    # ≤365d idle. Catches academic / lab eval harnesses (LiveBench,
    # AdalFlow, textgrad-class) that ship quarterly rather than weekly.
    # Star floor of 2k is high enough to filter noise; 365d recency window
    # admits the typical research-cadence push pattern without admitting
    # genuinely-abandoned work (the >547d dormant tier above catches that).
    if (
        isinstance(stars, int)
        and stars >= 2_000
        and have_age
        and age_days >= 365
        and days_since_commit is not None
        and days_since_commit <= 365
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

    # Emerging (LLM-era research-cadence path): ≥200 stars + ≥6mo age +
    # ≤365d idle. Catches the long-tail of academic eval / red-team
    # harnesses that have meaningful star traction but slower commit
    # cadence than infra projects. Star floor (200) is higher than the
    # strict path (100) to compensate for the relaxed recency.
    if (
        isinstance(stars, int)
        and stars >= 200
        and have_age
        and age_days >= 180
        and days_since_commit is not None
        and days_since_commit <= 365
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
                "refreshed_at": latest.get("refreshed_at"),
            }
        else:
            meta = {
                "stars": sidecar.get("stars"),
                "last_commit_at": sidecar.get("last_commit_at"),
                "created_at": sidecar.get("created_at"),
                "archived": sidecar.get("archived", False),
                "refreshed_at": sidecar.get("refreshed_at"),
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
        for tier in (TIER_LANDMARK, TIER_CANONICAL, TIER_ESTABLISHED,
                     TIER_EMERGING, TIER_DORMANT, TIER_FRONTIER, TIER_UNKNOWN):
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

    atomic_write_text(TIERS_PATH, new_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
