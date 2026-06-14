r"""Curate scripts/discovery/candidates.recent.jsonl down to a high-signal set.

Filters applied (top to bottom, conservative):

  1. Drop archived or low-stars-and-no-description noise.
  2. Drop "spec" / "skills" repos masquerading as harnesses:
       - names matching /^skills?$|^agent-?skills?$|^agents?\.md$|^design\.md$/
       - descriptions of the form "a format for ..." or "library of skills"
  3. Drop "coding-agent wrapper" repos with no harness substrate:
       - description mentions {claude code, cursor, codex, copilot}
         AND does NOT mention {framework, gateway, eval, benchmark, audit}
  4. Drop generic "awesome-X" aggregators (already covered by parse_awesome).
  5. Drop entries whose stars look implausible vs. created date
       (heuristic: > 50k stars AND created in last 6 months and no clear value).
  6. Per-category cap (target ~80 total).
  7. Sort by composite signal (multi-topic match, stars, freshness).

Output:
  scripts/discovery/candidates.recent.curated.jsonl

This file is hand-reviewable; downstream the multi-model ensemble pass
treats every surviving entry as a candidate for the registry.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IN_PATH = REPO / "scripts" / "discovery" / "candidates.recent.jsonl"
OUT_PATH = REPO / "scripts" / "discovery" / "candidates.recent.curated.jsonl"

NAME_BLOCK_RE = re.compile(
    r"^(skills?|agent-?skills?|agents?\.md|design\.md|claude-?skills?|"
    r"awesome[-_].*|cursor[-_]rules?|cursor[-_]tips?|cursor[-_]templates?)$",
    re.IGNORECASE,
)

WRAPPER_HINTS = re.compile(
    r"\b(claude code|cursor|codex|copilot|kilo|gemini-cli|aider|continue\.dev)\b",
    re.IGNORECASE,
)
HARNESS_SUBSTRATE_HINTS = re.compile(
    r"\b(framework|gateway|router|harness|benchmark|eval|evaluation|audit|"
    r"guardrail|policy|finite-state|orchestrat(or|ion)|sdk|server|engine|"
    r"proxy|observ|telemetry|trace|redteam|red-team|jailbreak|attack|"
    r"safety|alignment|fine-tun|rlhf|distill|prompt-opt|inference|"
    r"validat|sanitiz|moderat|secur)\b",
    re.IGNORECASE,
)
SPEC_DOC_RE = re.compile(
    r"\b(a (simple |open )?format|specification for|library of|"
    r"collection of (skills|prompts|templates|design|examples)|"
    r"reference (architecture|implementation))\b",
    re.IGNORECASE,
)

CATEGORY_CAP = {
    "agent":      30,
    "eval":       15,
    "redteam":    15,
    "routing":    10,
    "governance": 10,
    "education":  10,
}


def implausible_stars(stars: int, pushed_at: str | None) -> bool:
    """Drop entries with >50k stars created within last 6 months
    (proxy for inflated/fake-stars repos; real superstar projects
    are typically older than that)."""
    if stars < 50_000 or not pushed_at:
        return False
    try:
        dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    age_days = (datetime.now(UTC) - dt).days
    return age_days < 180


def looks_like_wrapper(desc: str | None) -> bool:
    if not desc:
        return False
    return bool(WRAPPER_HINTS.search(desc) and not HARNESS_SUBSTRATE_HINTS.search(desc))


def looks_like_spec_doc(desc: str | None, name: str) -> bool:
    if NAME_BLOCK_RE.match(name):
        return True
    if not desc:
        return False
    return bool(SPEC_DOC_RE.search(desc))


def composite_score(rec: dict) -> float:
    s = rec.get("stars") or 0
    multi = len(rec.get("matched_queries") or [])
    bonus = 1.0 if (rec.get("description") or "") and HARNESS_SUBSTRATE_HINTS.search(
        rec.get("description") or "") else 0.0
    return s * (1 + 0.1 * multi) + bonus * 1000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Curate the recent-search output.")
    parser.add_argument("--input", default=str(IN_PATH), type=str)
    parser.add_argument("--output", default=str(OUT_PATH), type=str)
    parser.add_argument("--target-total", type=int, default=90,
                        help="Soft cap on total surviving candidates.")
    args = parser.parse_args(argv)

    raw_lines = Path(args.input).read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in raw_lines if line.strip()]
    print(f"input: {len(records)} candidates")

    survivors: list[dict] = []
    drops = {"low-signal": 0, "spec-doc": 0, "wrapper": 0, "implausible-stars": 0}

    for rec in records:
        name = (rec.get("full_name") or "").split("/", 1)[-1]
        desc = rec.get("description")
        stars = rec.get("stars") or 0

        if not desc and stars < 200:
            drops["low-signal"] += 1
            continue
        if looks_like_spec_doc(desc, name):
            drops["spec-doc"] += 1
            continue
        if looks_like_wrapper(desc):
            drops["wrapper"] += 1
            continue
        if implausible_stars(stars, rec.get("pushed_at")):
            drops["implausible-stars"] += 1
            continue
        survivors.append(rec)

    print(f"after heuristics: {len(survivors)} (drops: {drops})")

    # Sort by composite score; apply per-category caps.
    survivors.sort(key=composite_score, reverse=True)
    capped: list[dict] = []
    cat_counts: dict[str, int] = {}
    for rec in survivors:
        cat = rec.get("primary_category", "agent")
        cap = CATEGORY_CAP.get(cat, 10)
        used = cat_counts.get(cat, 0)
        if used >= cap:
            continue
        capped.append(rec)
        cat_counts[cat] = used + 1
        if len(capped) >= args.target_total:
            break

    print(f"after caps: {len(capped)} (per-category: {cat_counts})")

    Path(args.output).write_text(
        "\n".join(json.dumps(r) for r in capped) + ("\n" if capped else ""),
        encoding="utf-8",
    )
    rel = Path(args.output).relative_to(REPO) if Path(args.output).is_absolute() else args.output
    print(f"wrote {len(capped)} curated candidates to {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
