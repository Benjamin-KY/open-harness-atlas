"""Drive `gh search repos` across a planned topic matrix for Phase 2.

Output:
  scripts/discovery/candidates.raw.jsonl     — every hit from every query
                                                (with the source query annotated)
  scripts/discovery/candidates.dedup.jsonl   — deduped by full_name, with
                                                a `categories` field collecting
                                                every topic that surfaced it

Usage::

    python -m scripts.discovery.search_github            # full sweep
    python -m scripts.discovery.search_github --queries agent eval  # one or two categories

Filters applied here (the script never relaxes them silently):
  - exclude archived repos
  - exclude repos with no commit in the last 18 months
  - exclude non-OSI licences (keep only an SPDX allowlist)
  - exclude repos already present in scripts/discovery/existing-ids.txt
    (matched on slug → kebab-case id, with a small alias table for
    well-known mismatches between repo name and id)

The script is paginated and resilient: if `gh` rate-limits one query, the
others continue and the failure is logged.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DISCOVERY_DIR = REPO / "scripts" / "discovery"
EXISTING_IDS_PATH = DISCOVERY_DIR / "existing-ids.txt"
RAW_OUT = DISCOVERY_DIR / "candidates.raw.jsonl"
DEDUP_OUT = DISCOVERY_DIR / "candidates.dedup.jsonl"

# OSI-approved SPDX subset that we will accept. Conservative — broad enough
# to include the long tail of OSS but tight enough to keep "source-available
# but not OSS" projects out.
OSI_LICENSES = {
    "apache-2.0",
    "mit",
    "bsd-2-clause",
    "bsd-3-clause",
    "bsd-3-clause-clear",
    "mpl-2.0",
    "gpl-2.0",
    "gpl-3.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "agpl-3.0",
    "epl-2.0",
    "epl-1.0",
    "isc",
    "0bsd",
    "unlicense",
    "cc0-1.0",
    # Content licences accepted for education entries only.
    "cc-by-4.0",
    "cc-by-sa-4.0",
}

# 18-month freshness cutoff (per GOVERNANCE.md §1.3).
FRESHNESS_DAYS = 18 * 30

# Category-keyed query matrix. Each entry: list of (gh-search-arg-list, subcategory hint).
# Searches use --topic where possible (high precision) and fall back to free-text
# search for emergent niches with no canonical topic.
QUERY_MATRIX: dict[str, list[tuple[list[str], str]]] = {
    "agent": [
        (["--topic", "llm-agent"], "agent-framework"),
        (["--topic", "agent-framework"], "agent-framework"),
        (["--topic", "ai-agent"], "agent-framework"),
        (["--topic", "ai-agents"], "agent-framework"),
        (["--topic", "autonomous-agents"], "autonomous-agent"),
        (["--topic", "multi-agent"], "multi-agent"),
        (["--topic", "multi-agent-systems"], "multi-agent"),
        (["--topic", "agentic"], "agentic"),
        (["--topic", "agentic-ai"], "agentic"),
        (["--topic", "agentic-workflow"], "agent-workflow"),
        (["--topic", "react-agent"], "react-agent"),
        (["--topic", "tool-use"], "tool-use"),
        (["--topic", "function-calling"], "tool-use"),
        (["--topic", "computer-use"], "computer-use-agent"),
        (["--topic", "browser-use"], "browser-agent"),
        (["--topic", "browser-agent"], "browser-agent"),
        (["--topic", "web-agent"], "browser-agent"),
        (["--topic", "code-agent"], "code-agent"),
        (["--topic", "coding-agent"], "code-agent"),
        (["--topic", "mcp"], "mcp-host"),
        (["--topic", "mcp-server"], "mcp-server"),
        (["--topic", "mcp-client"], "mcp-client"),
        (["--topic", "model-context-protocol"], "mcp"),
    ],
    "eval": [
        (["--topic", "llm-evaluation"], "llm-eval"),
        (["--topic", "llm-eval"], "llm-eval"),
        (["--topic", "llm-benchmark"], "benchmark"),
        (["--topic", "ai-benchmark"], "benchmark"),
        (["--topic", "benchmark"], "benchmark"),
        (["--topic", "evaluation-framework"], "eval-framework"),
        (["--topic", "rag-evaluation"], "rag-eval"),
        (["--topic", "agent-evaluation"], "agent-eval"),
        (["--topic", "llm-as-judge"], "llm-judge"),
        (["--topic", "llm-judge"], "llm-judge"),
        (["--topic", "reward-model"], "reward-model"),
        (["--topic", "reasoning-benchmark"], "reasoning-eval"),
        (["--topic", "code-evaluation"], "code-eval"),
        (["--topic", "code-benchmark"], "code-eval"),
        (["--topic", "math-benchmark"], "math-eval"),
        (["--topic", "tool-use-benchmark"], "tool-use-eval"),
    ],
    "redteam": [
        (["--topic", "red-team"], "red-team"),
        (["--topic", "redteam"], "red-team"),
        (["--topic", "red-teaming"], "red-team"),
        (["--topic", "llm-security"], "llm-security"),
        (["--topic", "ai-security"], "ai-security"),
        (["--topic", "ai-safety"], "ai-safety"),
        (["--topic", "jailbreak"], "jailbreak"),
        (["--topic", "jailbreaking"], "jailbreak"),
        (["--topic", "prompt-injection"], "prompt-injection"),
        (["--topic", "adversarial-attacks"], "adversarial"),
        (["--topic", "adversarial-examples"], "adversarial"),
        (["--topic", "adversarial-ml"], "adversarial-ml"),
        (["--topic", "llm-attack"], "llm-attack"),
        (["--topic", "model-stealing"], "model-stealing"),
        (["--topic", "data-poisoning"], "poisoning"),
        (["--topic", "backdoor-attacks"], "backdoor"),
        (["--topic", "membership-inference"], "membership-inference"),
        (["--topic", "deepfake-detection"], "deepfake-detection"),
        (["--topic", "watermarking"], "watermarking"),
    ],
    "routing": [
        (["--topic", "llm-gateway"], "llm-gateway"),
        (["--topic", "llm-proxy"], "llm-proxy"),
        (["--topic", "llm-router"], "llm-router"),
        (["--topic", "llm-routing"], "llm-router"),
        (["--topic", "ai-gateway"], "ai-gateway"),
        (["--topic", "model-router"], "model-router"),
        (["--topic", "openai-proxy"], "openai-compatible-proxy"),
        (["--topic", "openai-api-compatible"], "openai-compatible"),
        (["--topic", "openai-compatible-api"], "openai-compatible"),
        (["--topic", "inference-server"], "inference-server"),
        (["--topic", "llm-inference"], "inference-server"),
        (["--topic", "llm-serving"], "serving"),
        (["--topic", "model-serving"], "serving"),
        (["--topic", "llm-load-balancer"], "load-balancer"),
        (["--topic", "rate-limit"], "rate-limit"),
        (["--topic", "semantic-cache"], "semantic-cache"),
        (["--topic", "prompt-cache"], "prompt-cache"),
    ],
    "governance": [
        (["--topic", "llm-guardrails"], "guardrails"),
        (["--topic", "guardrails"], "guardrails"),
        (["--topic", "ai-guardrails"], "guardrails"),
        (["--topic", "llm-safety"], "safety-layer"),
        (["--topic", "responsible-ai"], "responsible-ai"),
        (["--topic", "ai-policy"], "ai-policy"),
        (["--topic", "policy-as-code"], "policy-as-code"),
        (["--topic", "constrained-decoding"], "constrained-decoding"),
        (["--topic", "structured-output"], "structured-output"),
        (["--topic", "json-schema"], "structured-output"),
        (["--topic", "function-call"], "structured-output"),
        (["--topic", "validator"], "validator"),
        (["--topic", "prompt-management"], "prompt-management"),
        (["--topic", "prompt-engineering"], "prompt-engineering"),
        (["--topic", "prompt-template"], "prompt-template"),
        (["--topic", "pii-detection"], "pii-detection"),
        (["--topic", "pii-redaction"], "pii-redaction"),
        (["--topic", "data-sanitization"], "data-sanitization"),
        (["--topic", "content-moderation"], "content-moderation"),
        (["--topic", "toxicity"], "toxicity-detection"),
        (["--topic", "hate-speech"], "hate-speech-detection"),
        (["--topic", "fairness"], "fairness"),
        (["--topic", "explainable-ai"], "explainability"),
    ],
    "education": [
        (["--topic", "llm-tutorial"], "tutorial"),
        (["--topic", "llm-course"], "course"),
        (["--topic", "llm-bootcamp"], "course"),
        (["--topic", "ai-engineering"], "ai-engineering-course"),
        (["--topic", "llm-from-scratch"], "from-scratch"),
        (["--topic", "transformer-from-scratch"], "from-scratch"),
        (["--topic", "llm-cookbook"], "cookbook"),
        (["--topic", "rag-tutorial"], "rag-tutorial"),
        (["--topic", "agent-tutorial"], "agent-tutorial"),
        (["--topic", "llm-notebook"], "notebook"),
        (["--topic", "llm-workshop"], "workshop"),
        (["--topic", "ml-course"], "course"),
        (["--topic", "deep-learning-course"], "course"),
    ],
}

# Repo-name → existing registry id rewrites for high-confidence aliases.
# This avoids the candidate filter proposing well-known repos that we already
# have under a slightly different id (e.g. ``CrewAIInc/crewAI`` vs ``crewai``).
NAME_TO_ID_ALIAS: dict[str, str] = {
    "crewaiinc/crewai": "crewai",
    "geekan/metagpt": "metagpt",
    "openbmb/agentverse": "agentverse-openbmb",
    "salesforceairesearch/agentlite": "agentlite-salesforce",
    "thudm/agentbench": "agentbench-thudm",
    "stanford-futuredata/arena-hard-auto": "arena-hard-auto",
    "openai/swarm": "swarm-openai",
    "explosion/spacy-llm": "spacy-llm",
    "guardrails-ai/guardrails": "guardrails-ai",
    "promptfoo/promptfoo": "promptfoo",
    "berriai/litellm": "litellm",
    "mlflow/mlflow": "mlflow-ai-gateway",
}


def repo_to_candidate_id(full_name: str) -> str:
    """Stable id derived from ``owner/repo`` → kebab-case repo slug.

    Used both for dedupe against existing-ids.txt and as the registry
    YAML filename. If the alias table maps the full name to an existing
    id, that id is returned (the candidate will then be discarded as a
    duplicate).
    """
    full = full_name.lower()
    if full in NAME_TO_ID_ALIAS:
        return NAME_TO_ID_ALIAS[full]
    repo = full.split("/", 1)[1] if "/" in full else full
    repo = re.sub(r"[^a-z0-9]+", "-", repo).strip("-")
    if len(repo) > 60:
        repo = repo[:60].rstrip("-")
    # Schema requires first + last char alphanumeric; the regex above
    # already strips trailing dashes but a leading dash is possible if
    # the slug started with non-alnum.
    repo = repo.lstrip("-")
    return repo


def load_existing_ids() -> set[str]:
    if not EXISTING_IDS_PATH.exists():
        raise SystemExit(
            f"existing-ids file missing: {EXISTING_IDS_PATH}. "
            "Run scripts/discovery/existing_ids.py first."
        )
    return {
        line.strip()
        for line in EXISTING_IDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def freshness_cutoff() -> datetime:
    return datetime.now(UTC) - timedelta(days=FRESHNESS_DAYS)


def is_fresh(pushed_at: str | None, cutoff: datetime) -> bool:
    if not pushed_at:
        return False
    try:
        dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return dt >= cutoff


def is_osi(license_key: str | None) -> bool:
    return bool(license_key) and license_key.lower() in OSI_LICENSES


def run_query(args: list[str], limit: int) -> list[dict]:
    """Run one ``gh search repos`` query and return parsed JSON."""
    cmd = [
        "gh", "search", "repos",
        "--limit", str(limit),
        "--json",
        "fullName,description,url,stargazersCount,language,license,pushedAt,isArchived,homepage,owner,forksCount",
        *args,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        print(f"  [timeout] {' '.join(args)}", file=sys.stderr)
        return []
    if proc.returncode != 0:
        stderr = proc.stderr.strip()[:200]
        print(f"  [error rc={proc.returncode}] {' '.join(args)}: {stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"  [parse-error] {' '.join(args)}: {exc}", file=sys.stderr)
        return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search GitHub for harness candidates.")
    parser.add_argument(
        "--queries", nargs="*", default=list(QUERY_MATRIX),
        help="Restrict to these categories (default: all).",
    )
    parser.add_argument("--limit", type=int, default=100, help="Per-query result limit (max 100).")
    args = parser.parse_args(argv)

    existing = load_existing_ids()
    cutoff = freshness_cutoff()

    raw_records: list[dict] = []
    seen: dict[str, dict] = {}  # candidate_id -> deduped record

    selected = [c for c in args.queries if c in QUERY_MATRIX]
    if not selected:
        raise SystemExit(f"no matching categories: {args.queries!r}")
    print(f"sweeping categories: {selected}")

    for category in selected:
        for query_args, subcategory in QUERY_MATRIX[category]:
            label = " ".join(query_args)
            print(f"  -> [{category}] {label}")
            hits = run_query(query_args, args.limit)
            for hit in hits:
                full_name = hit.get("fullName")
                if not full_name:
                    continue
                record = {
                    "category": category,
                    "subcategory": subcategory,
                    "source_query": label,
                    "full_name": full_name,
                    "url": hit.get("url"),
                    "homepage": (hit.get("homepage") or "").strip() or None,
                    "description": (hit.get("description") or "").strip() or None,
                    "language": (hit.get("language") or "").strip() or None,
                    "license_key": ((hit.get("license") or {}).get("key") or "").lower() or None,
                    "license_name": (hit.get("license") or {}).get("name") or None,
                    "pushed_at": hit.get("pushedAt"),
                    "stars": hit.get("stargazersCount") or 0,
                    "forks": hit.get("forksCount") or 0,
                    "is_archived": bool(hit.get("isArchived")),
                    "owner_login": ((hit.get("owner") or {}).get("login") or "").strip() or None,
                }
                raw_records.append(record)

                if record["is_archived"]:
                    continue
                if not is_fresh(record["pushed_at"], cutoff):
                    continue
                if not is_osi(record["license_key"]):
                    continue

                candidate_id = repo_to_candidate_id(full_name)
                if candidate_id in existing:
                    continue

                if candidate_id in seen:
                    existing_record = seen[candidate_id]
                    # Merge: collect every category/subcategory that matched, keep first metadata.
                    existing_record.setdefault("matched_categories", set()).add(category)
                    existing_record.setdefault("matched_subcategories", set()).add(subcategory)
                    existing_record.setdefault("matched_queries", []).append(label)
                else:
                    record_copy = dict(record)
                    record_copy["candidate_id"] = candidate_id
                    record_copy["matched_categories"] = {category}
                    record_copy["matched_subcategories"] = {subcategory}
                    record_copy["matched_queries"] = [label]
                    seen[candidate_id] = record_copy

    RAW_OUT.write_text(
        "\n".join(json.dumps(r) for r in raw_records) + ("\n" if raw_records else ""),
        encoding="utf-8",
    )
    print(f"\nwrote {len(raw_records)} raw hits to {RAW_OUT.relative_to(REPO)}")

    deduped: list[dict] = []
    for rec in seen.values():
        rec["matched_categories"] = sorted(rec["matched_categories"])
        rec["matched_subcategories"] = sorted(rec["matched_subcategories"])
        # Choose the primary category as the first matched category in the
        # canonical ordering used elsewhere in the project.
        category_order = ["governance", "agent", "eval", "redteam", "routing", "education"]
        rec["primary_category"] = next(
            (c for c in category_order if c in rec["matched_categories"]),
            rec["matched_categories"][0],
        )
        deduped.append(rec)

    deduped.sort(key=lambda r: (-(r.get("stars") or 0), r["candidate_id"]))
    DEDUP_OUT.write_text(
        "\n".join(json.dumps(r) for r in deduped) + ("\n" if deduped else ""),
        encoding="utf-8",
    )
    print(f"wrote {len(deduped)} unique candidates to {DEDUP_OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
