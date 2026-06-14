"""Recency-biased GitHub search: catch 2025/2026 emerging entries.

Most of the canonical AI-harness vocabulary stabilised in 2022-2024.
The default search_github.py matrix is topic-driven, which favours
repos that adopted the canonical tags early. This script uses
``gh search repos`` with a ``created>=YYYY-MM-DD`` filter to surface
newer projects that may not carry a canonical topic yet but show
strong star-velocity in the last 18-24 months — closing the
"recency gap" surfaced by the curation-coverage swarm agent.

Output:
  scripts/discovery/candidates.recent.jsonl

Same filter chain as search_github.py: not archived, fresh (≤18mo),
OSI licence, not already in existing-ids.txt.

Run::

    python -m scripts.discovery.search_recent
    python -m scripts.discovery.search_recent --since 2025-01-01
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime

from scripts.discovery.search_github import (
    DISCOVERY_DIR,
    freshness_cutoff,
    is_fresh,
    is_osi,
    load_existing_ids,
    repo_to_candidate_id,
)

OUT_PATH = DISCOVERY_DIR / "candidates.recent.jsonl"


def collision_aware_id(full_name: str, existing: set[str]) -> tuple[str, bool]:
    """Return a candidate_id that does not collide with the existing registry.

    If the natural repo-slug id collides, fall back to owner-slug + repo-slug
    (e.g. ``ai-twinkle/Eval`` → ``eval`` (collision) → ``ai-twinkle-eval``).
    Returns ``(id, was_aliased)``.
    """
    natural = repo_to_candidate_id(full_name)
    if natural not in existing:
        return natural, False
    owner = full_name.split("/", 1)[0].lower()
    owner_slug = "".join(c if c.isalnum() else "-" for c in owner).strip("-")
    aliased = f"{owner_slug}-{natural}"[:60].rstrip("-")
    return aliased, True

# Free-text queries (kept short — long boolean strings break gh's quoting).
# Each tuple: (query string, primary category, subcategory hint).
RECENT_QUERIES: list[tuple[str, str, str]] = [
    # agent
    ("ai agent framework",                     "agent",      "agent-framework"),
    ("autonomous agents",                      "agent",      "autonomous-agent"),
    ("multi-agent system",                     "agent",      "multi-agent"),
    ("browser agent",                          "agent",      "browser-agent"),
    ("coding agent",                           "agent",      "code-agent"),
    ("computer use agent",                     "agent",      "computer-use-agent"),
    ("mcp server",                             "agent",      "mcp-server"),
    ("agentic workflow",                       "agent",      "agent-workflow"),
    # eval
    ("llm benchmark",                          "eval",       "benchmark"),
    ("llm evaluation framework",               "eval",       "eval-framework"),
    ("agent benchmark",                        "eval",       "agent-eval"),
    ("rag evaluation",                         "eval",       "rag-eval"),
    ("contamination-free benchmark",           "eval",       "contamination-free"),
    ("reasoning benchmark",                    "eval",       "reasoning-eval"),
    # redteam
    ("llm red team",                           "redteam",    "red-team"),
    ("prompt injection",                       "redteam",    "prompt-injection"),
    ("agent attack",                           "redteam",    "agent-attack"),
    ("jailbreak benchmark",                    "redteam",    "jailbreak-eval"),
    ("ai security benchmark",                  "redteam",    "ai-security"),
    # routing
    ("llm gateway",                            "routing",    "llm-gateway"),
    ("model router",                           "routing",    "model-router"),
    ("inference server",                       "routing",    "inference-server"),
    ("vllm proxy",                             "routing",    "vllm-proxy"),
    ("semantic cache",                         "routing",    "semantic-cache"),
    # governance
    ("llm guardrails",                         "governance", "guardrails"),
    ("ai policy enforcement",                  "governance", "policy-enforcement"),
    ("pii redaction llm",                      "governance", "pii-redaction"),
    ("content moderation llm",                 "governance", "content-moderation"),
    ("ai responsible deployment",              "governance", "responsible-ai"),
    # education
    ("llm from scratch",                       "education",  "from-scratch"),
    ("agentic ai course",                      "education",  "course"),
    ("ai engineering bootcamp",                "education",  "course"),
    ("rag tutorial",                           "education",  "rag-tutorial"),
]


def run_recent_query(qstr: str, since: str, limit: int) -> list[dict]:
    cmd = [
        "gh", "search", "repos", qstr,
        "--limit", str(limit),
        "--created", f">={since}",
        "--sort", "stars",
        "--json",
        "fullName,description,url,stargazersCount,language,license,pushedAt,isArchived,homepage,owner,forksCount",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, check=False,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        print(f"  [timeout] {qstr!r}", file=sys.stderr)
        return []
    if proc.returncode != 0:
        print(f"  [error rc={proc.returncode}] {qstr!r}: {proc.stderr.strip()[:160]}",
              file=sys.stderr)
        return []
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"  [parse-error] {qstr!r}: {exc}", file=sys.stderr)
        return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recency-biased GitHub sweep.")
    parser.add_argument("--since", default="2025-01-01",
                        help="ISO date; only consider repos created >= this date.")
    parser.add_argument("--limit", type=int, default=80,
                        help="Per-query result limit (max 100).")
    parser.add_argument("--only-categories", default=None,
                        help="Comma-separated list of categories to include "
                             "(e.g. 'eval,redteam,routing,governance,education'). "
                             "If omitted, all categories run.")
    parser.add_argument("--output", default=None,
                        help="Override output path (default: candidates.recent.jsonl).")
    args = parser.parse_args(argv)

    # Validate the date so we fail loud, not silent.
    try:
        datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"--since must be YYYY-MM-DD, got {args.since!r}") from exc

    only_cats: set[str] | None = None
    if args.only_categories:
        only_cats = {c.strip().lower() for c in args.only_categories.split(",") if c.strip()}

    out_path = DISCOVERY_DIR / args.output if args.output else OUT_PATH

    existing = load_existing_ids()
    cutoff = freshness_cutoff()
    print(f"recency since={args.since}  existing={len(existing)}  fresh-cutoff={cutoff.date()}")
    if only_cats:
        print(f"  only-categories={sorted(only_cats)}")

    seen: dict[str, dict] = {}
    aliased_count = 0
    for qstr, category, subcategory in RECENT_QUERIES:
        if only_cats and category not in only_cats:
            continue
        print(f"  -> [{category}] {qstr!r}")
        hits = run_recent_query(qstr, args.since, args.limit)
        for hit in hits:
            full_name = hit.get("fullName")
            if not full_name:
                continue
            if hit.get("isArchived"):
                continue
            pushed = hit.get("pushedAt")
            if not is_fresh(pushed, cutoff):
                continue
            licence = ((hit.get("license") or {}).get("key") or "").lower()
            if not is_osi(licence):
                continue
            candidate_id, was_aliased = collision_aware_id(full_name, existing)
            if was_aliased:
                aliased_count += 1
            if candidate_id in existing:
                continue
            if candidate_id in seen:
                seen[candidate_id].setdefault("matched_categories", set()).add(category)
                seen[candidate_id].setdefault("matched_subcategories", set()).add(subcategory)
                seen[candidate_id].setdefault("matched_queries", []).append(qstr)
            else:
                seen[candidate_id] = {
                    "category": category,
                    "primary_category": category,
                    "subcategory": subcategory,
                    "source_query": qstr,
                    "full_name": full_name,
                    "url": hit.get("url"),
                    "homepage": (hit.get("homepage") or "").strip() or None,
                    "description": (hit.get("description") or "").strip() or None,
                    "language": (hit.get("language") or "").strip() or None,
                    "license_key": licence,
                    "license_name": (hit.get("license") or {}).get("name"),
                    "pushed_at": pushed,
                    "stars": hit.get("stargazersCount") or 0,
                    "forks": hit.get("forksCount") or 0,
                    "is_archived": False,
                    "owner_login": ((hit.get("owner") or {}).get("login") or "").strip() or None,
                    "candidate_id": candidate_id,
                    "id_aliased": was_aliased,
                    "matched_categories": {category},
                    "matched_subcategories": {subcategory},
                    "matched_queries": [qstr],
                }

    out = []
    for rec in seen.values():
        rec["matched_categories"] = sorted(rec["matched_categories"])
        rec["matched_subcategories"] = sorted(rec["matched_subcategories"])
        out.append(rec)
    out.sort(key=lambda r: (-(r.get("stars") or 0), r["candidate_id"]))

    out_path.write_text(
        "\n".join(json.dumps(r) for r in out) + ("\n" if out else ""),
        encoding="utf-8",
    )
    rel = out_path.relative_to(DISCOVERY_DIR.parent.parent)
    print(f"\nwrote {len(out)} unique recent candidates to {rel}")
    print(f"  ({aliased_count} ids needed owner-prefix to avoid collision)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
