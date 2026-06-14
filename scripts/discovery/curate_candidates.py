"""Curate scripts/discovery/candidates.dedup.jsonl down to ~500 high-signal entries.

Filtering policy (top-to-bottom, conservative):

  1. Drop obvious noise:
       - description missing AND stars < 500
       - owner login on a small blocklist (off-topic personal forks)
       - description matches a generic-repo regex (Java guide, system-design
         notes, awesome-list aggregator, etc.) that has no LLM relevance.

  2. Per-category relevance regex on description: at least one match OR
     a strong signal from `matched_subcategories` (>= 2 topics surfaced
     the candidate).

  3. Out-of-scope filter (per GOVERNANCE.md §8):
       - pure observability/tracing stacks unless they ship a harness layer
       - pure vector DB infrastructure
       - pure RAG core libraries
       - closed-source service shims

  4. Per-category cap to land near a 500-entry budget overall.
     The cap is applied after sorting each category by a composite score
     (stars, freshness, multi-topic-match), so the cap takes the strongest
     candidates first.

Output:
  scripts/discovery/candidates.curated.jsonl

Run::

    python -m scripts.discovery.curate_candidates \
        --target-per-category agent=160 eval=120 redteam=80 routing=50 \
            governance=50 education=40

The defaults shipped below match the Phase-2 plan.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IN_PATH = REPO / "scripts" / "discovery" / "candidates.dedup.jsonl"
OUT_PATH = REPO / "scripts" / "discovery" / "candidates.curated.jsonl"


# Blocklist of owners that contribute high-noise off-topic repos (e.g.
# "awesome" aggregators with no harness, personal interview-prep guides).
OWNER_BLOCKLIST = {
    "snailclimb",            # Java interview guide
    "donnemartin",           # system-design primer
    "trekhleb",              # ML algorithms tutorial
    "labuladong",            # algorithm interview guide
    "dair-ai",               # ML prompt-engineering guide (already catalogued? — alias)
}

# Per-category description keyword filters. The regex must match at least
# one descriptor token AND one AI/LLM context token. This eliminates generic
# benchmarks, JSON-schema form builders, web pentest toolkits, etc. that
# accidentally matched on shared vocabulary.

AI_CONTEXT = re.compile(
    r"\b("
    r"llm|llms|large[- ]?language[- ]?model|gpt|chatgpt|claude|gemini|"
    r"anthropic|openai|mistral|qwen|deepseek|llama|"
    r"foundation[- ]?model|generative[- ]?ai|"
    r"\bai\b|artificial[- ]?intelligence|"
    r"transformer|prompt|prompting|chatbot|"
    r"machine[- ]?learning|deep[- ]?learning|nlp|natural[- ]?language|"
    r"agent|agentic|copilot|"
    r"text[- ]?to[- ]?text|text[- ]?gen|"
    r"hugging[- ]?face|langchain|llamaindex|crewai|autogen"
    r")\b",
    re.IGNORECASE,
)

CATEGORY_DESCRIPTOR: dict[str, re.Pattern[str]] = {
    "agent": re.compile(
        r"\b(agent|agentic|autonom\w*|orchestrat\w*|workflow|tool[- ]?use|"
        r"function[- ]?call\w*|react|planner|swarm|crew|"
        r"mcp|model[- ]?context[- ]?protocol|"
        r"computer[- ]?use|browser[- ]?use|web[- ]?agent|copilot|"
        r"task[- ]?automat\w*|assistant)\b",
        re.IGNORECASE,
    ),
    "eval": re.compile(
        r"\b(eval\w*|benchmark\w*|leaderboard|judge|score|metric\w*|"
        r"correctness|llm[- ]?as[- ]?judge|"
        r"bigbench|mmlu|humaneval|hellaswag|truthfulqa|mt[- ]?bench|"
        r"arena|win[- ]?rate|prompt[- ]?test\w*|response[- ]?qualit\w*)\b",
        re.IGNORECASE,
    ),
    "redteam": re.compile(
        r"\b(red[- ]?team\w*|jailbreak\w*|prompt[- ]?inject\w*|"
        r"adversarial[- ]?(?:prompt|attack|examples?|llm|nlp|ml)|"
        r"poison\w*|backdoor|watermark|membership[- ]?inference|"
        r"model[- ]?steal\w*|llm[- ]?(?:attack|security|safety|exploit)|"
        r"safety[- ]?(?:benchmark|eval|test)|"
        r"data[- ]?extraction|prompt[- ]?leak\w*)\b",
        re.IGNORECASE,
    ),
    "routing": re.compile(
        r"\b(llm[- ]?(?:gateway|proxy|router|routing|cache|serv\w*)|"
        r"ai[- ]?gateway|model[- ]?router|model[- ]?serv\w*|"
        r"openai[- ]?compat\w*|inference[- ]?(?:server|engine|router|gateway)|"
        r"semantic[- ]?cache|prompt[- ]?cache|"
        r"multi[- ]?provider|provider[- ]?abstract\w*)\b",
        re.IGNORECASE,
    ),
    "governance": re.compile(
        r"\b(guardrail\w*|llm[- ]?(?:safety|guard\w*)|"
        r"prompt[- ]?(?:manag\w*|template|library|registry|version|engineer\w*)|"
        r"structured[- ]?(?:output|generation)|constrained[- ]?(?:decoding|generation)|"
        r"pii[- ]?(?:detect\w*|redact\w*)|content[- ]?moderat\w*|"
        r"toxic\w*|hate[- ]?speech|"
        r"validator|json[- ]?schema|"
        r"function[- ]?call\w*|"
        r"responsible[- ]?ai|ai[- ]?(?:policy|govern\w*|fairness|explain\w*)|"
        r"hallucin\w*|fact[- ]?check\w*)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"\b(course|tutorial|workshop|bootcamp|notebook\w*|lesson\w*|"
        r"cookbook|from[- ]?scratch|hands[- ]?on|"
        r"learn|teach\w*|build[- ]?your[- ]?own|guide|"
        r"crash[- ]?course|fundamentals)\b",
        re.IGNORECASE,
    ),
}

# Out-of-scope description patterns (per GOVERNANCE.md §8). If matched,
# the candidate is dropped regardless of category.
OUT_OF_SCOPE = re.compile(
    r"\b("
    r"system[- ]?design|interview[- ]?prep|leetcode|algorithm[s]? cheat[- ]?sheet|"
    r"awesome[- ]?list|awesome[- ]?(?:agent|llm|ai|tools?|rag|mcp|prompt|osint|"
    r"hacker|security|red[- ]?team|jailbreak|knowledge|memory)|"
    r"a curated list of|a collection of (?:mcp|awesome)|"
    r"curated collection of (?:ai|llm|agent|prompt)|"
    r"500 ai agents projects|"
    r"vector[- ]?(?:db|database|store|index)\b|"
    r"document[- ]?(?:loader|store)|"
    r"observability[- ]?(?:stack|platform)|"
    r"crypto|blockchain|nft|web3|"
    r"warcraft|minecraft|league of legends|"
    r"chrome[- ]?extension only|"
    r"discord[- ]?bot$|telegram[- ]?bot$|"
    r"pose[- ]?estimation|video[- ]?understanding|"
    r"web[- ]?application[- ]?security|"
    r"unix|gtfobins|cyber[- ]?security all[- ]?in[- ]?one|"
    r"adversary[- ]?emulation|"
    r"ios.{0,30}jailbreak|"
    r"http\(s\) benchmark|database.*benchmark|api.*benchmark|"
    r"react component|cross[- ]?(?:device|platform) form|"
    r"computer[- ]?vision (?:xai|explain\w*|library|toolbox|model|task)|"
    r"computer vision (?:and|for)|for computer[- ]?vision|"
    r"data engine|data[- ]?science[- ]?team|"
    r"penetration testing|"
    r"osint (?:tools?|collection|framework)|"
    r"forensics?|incident[- ]?response|"
    r"image[- ]?(?:classification|recognition|segmentation|generation)|"
    r"object[- ]?detection|stable[- ]?diffusion ui|"
    r"text[- ]?to[- ]?image|image[- ]?to[- ]?image"
    r")",
    re.IGNORECASE,
)

# Pure RAG cores: still useful but excluded by policy. We *do* catalog
# RAG evaluators (e.g. ragas, deepeval) — those should pass the eval regex
# above and the OOS pattern here should not match.
RAG_CORE = re.compile(
    r"\b("
    r"llama[- ]?index|haystack$|^txtai$|"
    r"retrieval[- ]?augmented[- ]?generation (?:engine|library|framework|core)|"
    r"^rag (?:engine|library|framework|core)|"
    r"rag[- ]?flow"
    r")\b",
    re.IGNORECASE,
)


def score_candidate(rec: dict) -> float:
    """Composite ranking score used inside per-category caps.

    Higher = stronger candidate. Pure stars is too biased toward giants; we
    add a fresh-push bonus and a multi-topic-match bonus.
    """
    stars = rec.get("stars", 0) or 0
    multi = len(rec.get("matched_subcategories") or [])
    # Log-ish star bucket so 1000 → 3.0 and 100000 → 5.0 ish.
    log_stars = 0.0
    s = stars
    while s >= 10 and log_stars < 6:
        s //= 10
        log_stars += 1
    # Recency bonus: max 1.0 if pushed in the last 30 days.
    pushed = rec.get("pushed_at")
    rec_bonus = 0.0
    if pushed:
        try:
            dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
            days_ago = (datetime.now(UTC) - dt).days
            rec_bonus = max(0.0, 1.0 - days_ago / 540.0)
        except ValueError:
            pass
    return log_stars + 0.5 * (multi - 1) + rec_bonus


def description_passes(rec: dict) -> bool:
    desc = (rec.get("description") or "").strip()
    if not desc:
        # No description = no way to verify. Require strong signal.
        return (rec.get("stars") or 0) >= 1000 and len(rec.get("matched_subcategories") or []) >= 2
    if OUT_OF_SCOPE.search(desc):
        return False
    if RAG_CORE.search(desc):
        return False

    cat = rec["primary_category"]
    descriptor = CATEGORY_DESCRIPTOR.get(cat)
    if descriptor is None:
        return False
    if not descriptor.search(desc):
        return False

    # Education entries get a relaxed AI-context check because many courses
    # are titled "from-scratch transformers" without saying "AI".
    if cat == "education":
        # Education needs a learning-format word AND an AI/ML context word
        # OR a strong topic-multi-match.
        if AI_CONTEXT.search(desc):
            return True
        return len(rec.get("matched_subcategories") or []) >= 2

    # Every other category MUST have AI/LLM context in the description.
    if not AI_CONTEXT.search(desc):
        # Allow only if the candidate was surfaced by >=3 topics in this
        # category (very strong taxonomy signal — likely a real harness
        # with a terse description).
        return len(rec.get("matched_subcategories") or []) >= 3

    return True


def owner_passes(rec: dict) -> bool:
    owner = (rec.get("owner_login") or "").lower()
    return owner not in OWNER_BLOCKLIST


def parse_target_caps(raw: list[str]) -> dict[str, int]:
    caps: dict[str, int] = {}
    for kv in raw:
        if "=" not in kv:
            raise SystemExit(f"--target-per-category expects KEY=N, got {kv!r}")
        k, v = kv.split("=", 1)
        caps[k.strip()] = int(v)
    return caps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Curate discovered candidates to a ~500-entry budget.")
    parser.add_argument(
        "--target-per-category", nargs="*", default=[
            "agent=170", "eval=130", "redteam=80",
            "routing=60", "governance=60", "education=40",
        ],
    )
    args = parser.parse_args(argv)
    caps = parse_target_caps(args.target_per_category)

    cands: list[dict] = []
    for line in IN_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cands.append(json.loads(line))

    print(f"loaded {len(cands)} dedup candidates")
    by_cat: dict[str, list[dict]] = {c: [] for c in caps}
    dropped = 0
    for rec in cands:
        cat = rec.get("primary_category")
        if cat not in by_cat:
            continue
        if not owner_passes(rec):
            dropped += 1
            continue
        if not description_passes(rec):
            dropped += 1
            continue
        by_cat[cat].append(rec)
    print(f"dropped {dropped} via filters")

    curated: list[dict] = []
    for cat, target in caps.items():
        pool = by_cat[cat]
        pool.sort(key=score_candidate, reverse=True)
        keep = pool[:target]
        print(f"  [{cat}] candidates={len(pool):>4}  cap={target:>3}  kept={len(keep):>3}")
        curated.extend(keep)

    curated.sort(key=lambda r: (r["primary_category"], r["candidate_id"]))
    OUT_PATH.write_text(
        "\n".join(json.dumps(r) for r in curated) + ("\n" if curated else ""),
        encoding="utf-8",
    )
    print(f"\nwrote {len(curated)} curated candidates to {OUT_PATH.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
