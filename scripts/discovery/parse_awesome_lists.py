"""Parse curated 'awesome-*' README lists for candidate repos.

Awesome lists are curated catalogues (typically a README.md with a long
list of `[name](https://github.com/owner/repo) — description.` lines).
They surface long-tail entries that don't carry the canonical topic tags
the GitHub-search-driven sweep relies on.

For each list, this script:
  1. Fetches the raw README via the GitHub Contents API.
  2. Extracts every `github.com/<owner>/<repo>` link in markdown
     `[text](url)` form (skipping the awesome-list itself).
  3. Queries `gh api repos/<owner>/<repo>` for each unique repo to get
     stars, last commit, licence, archived flag.
  4. Applies the same filters as search_github.py (not archived,
     pushed within 18 months, OSI licence, not already in
     existing-ids.txt).
  5. Tags each surviving record with the awesome-list it came from
     (`source_list`) and a heuristic primary category derived from the
     list's own topic.

Output:
  scripts/discovery/candidates.awesome.jsonl

Reuses `repo_to_candidate_id`, the OSI allowlist, freshness window, and
the existing-ids set from `search_github.py` to stay consistent with
the rest of the pipeline.

Run::

    python -m scripts.discovery.parse_awesome_lists
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time

from scripts.discovery.search_github import (
    DISCOVERY_DIR,
    freshness_cutoff,
    is_fresh,
    is_osi,
    load_existing_ids,
    repo_to_candidate_id,
)

OUT_PATH = DISCOVERY_DIR / "candidates.awesome.jsonl"

# Each entry: (repo "owner/name", README path, primary category hint).
# Lists were chosen for high curation quality and explicit harness focus.
AWESOME_LISTS: list[tuple[str, str, str]] = [
    ("steven2358/awesome-generative-ai",        "README.md", "agent"),
    ("kyrolabs/awesome-langchain",              "README.md", "agent"),
    ("e2b-dev/awesome-ai-agents",               "README.md", "agent"),
    ("jbmoelker/awesome-llms",                  "README.md", "agent"),
    ("hannibal046/Awesome-LLM",                 "README.md", "agent"),
    ("Hannibal046/Awesome-LLM",                 "README.md", "agent"),  # case alt
    ("tensorchord/Awesome-LLMOps",              "README.md", "routing"),
    ("KennethanCeyer/awesome-llmops",           "README.md", "routing"),
    ("imaurer/awesome-llm-json",                "README.md", "governance"),
    ("PrincetonNLP/awesome-llm-attribution",    "README.md", "eval"),
    ("microsoft/AILab-redteam",                 "README.md", "redteam"),  # may 404; tolerated
    ("corca-ai/awesome-llm-security",           "README.md", "redteam"),
    ("luban-agi/Awesome-LLM-Eval",              "README.md", "eval"),
    ("MoonshotAI/Awesome-LLM-Evaluation",       "README.md", "eval"),
    ("Yangjiaxi/Awesome-LLM-Inference",         "README.md", "routing"),
    ("DefTruth/Awesome-LLM-Inference",          "README.md", "routing"),
    ("openmoss/awesome-prompt-engineering",     "README.md", "governance"),
    ("dair-ai/Prompt-Engineering-Guide",        "README.md", "education"),
    ("microsoft/generative-ai-for-beginners",   "README.md", "education"),
    ("mlabonne/llm-course",                     "README.md", "education"),
]


GH_LINK_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:/|\)|\s|#|\?|\.git|$)"
)


def fetch_readme(owner_repo: str, path: str) -> str | None:
    """Fetch a README via gh api raw."""
    try:
        proc = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw",
             f"repos/{owner_repo}/contents/{path}"],
            capture_output=True, text=True, timeout=60, check=False,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        print(f"  [timeout] readme {owner_repo}", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(f"  [skip] {owner_repo}: rc={proc.returncode}", file=sys.stderr)
        return None
    return proc.stdout


def extract_github_links(text: str, self_repo: str) -> set[str]:
    """Return {owner/repo} pairs found in raw text, excluding self."""
    found: set[str] = set()
    self_lower = self_repo.lower()
    for m in GH_LINK_RE.finditer(text):
        owner, repo = m.group(1), m.group(2)
        if not owner or not repo:
            continue
        # Trim trailing punctuation like .md, .git
        if repo.endswith((".md", ".git", ".html")):
            repo = repo.rsplit(".", 1)[0]
        if not repo:
            continue
        # Skip self + GitHub system paths
        if owner.lower() in {"orgs", "topics", "trending", "marketplace",
                              "settings", "features", "about", "pricing",
                              "site", "issues", "pulls"}:
            continue
        pair = f"{owner}/{repo}"
        if pair.lower() == self_lower:
            continue
        found.add(pair)
    return found


def fetch_repo_meta(owner_repo: str) -> dict | None:
    """Fetch full repo metadata via gh api repos/owner/repo."""
    try:
        proc = subprocess.run(
            ["gh", "api", f"repos/{owner_repo}"],
            capture_output=True, text=True, timeout=30, check=False,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse awesome-* lists for candidates.")
    parser.add_argument("--limit-lists", type=int, default=len(AWESOME_LISTS),
                        help="Limit how many lists to process (debug).")
    parser.add_argument("--limit-per-list", type=int, default=300,
                        help="Cap candidates fetched per list (rate-limit guard).")
    args = parser.parse_args(argv)

    existing = load_existing_ids()
    cutoff = freshness_cutoff()
    print(f"existing ids: {len(existing)}  freshness-cutoff: {cutoff.date()}")

    all_records: list[dict] = []
    seen_ids: dict[str, dict] = {}

    for owner_repo, readme_path, hint_category in AWESOME_LISTS[: args.limit_lists]:
        print(f"\n-> {owner_repo}  (hint={hint_category})")
        body = fetch_readme(owner_repo, readme_path)
        if not body:
            continue
        links = extract_github_links(body, owner_repo)
        print(f"   {len(links)} unique github.com links found")

        for i, pair in enumerate(sorted(links)[: args.limit_per_list]):
            candidate_id = repo_to_candidate_id(pair)
            if candidate_id in existing:
                continue
            if candidate_id in seen_ids:
                seen_ids[candidate_id].setdefault("source_lists", set()).add(owner_repo)
                seen_ids[candidate_id].setdefault("hint_categories", set()).add(hint_category)
                continue
            meta = fetch_repo_meta(pair)
            if not meta:
                continue
            if meta.get("archived"):
                continue
            pushed = meta.get("pushed_at")
            if not is_fresh(pushed, cutoff):
                continue
            licence = ((meta.get("license") or {}).get("spdx_id") or "").lower()
            if not is_osi(licence):
                continue
            record = {
                "category": hint_category,
                "primary_category": hint_category,
                "subcategory": "from-awesome-list",
                "full_name": meta.get("full_name") or pair,
                "url": meta.get("html_url"),
                "homepage": (meta.get("homepage") or "").strip() or None,
                "description": (meta.get("description") or "").strip() or None,
                "language": meta.get("language"),
                "license_key": licence,
                "license_name": (meta.get("license") or {}).get("name"),
                "pushed_at": pushed,
                "stars": meta.get("stargazers_count") or 0,
                "forks": meta.get("forks_count") or 0,
                "is_archived": False,
                "owner_login": ((meta.get("owner") or {}).get("login") or "").strip() or None,
                "candidate_id": candidate_id,
                "source_lists": {owner_repo},
                "hint_categories": {hint_category},
                "matched_categories": [hint_category],
                "matched_subcategories": ["from-awesome-list"],
                "matched_queries": [f"awesome-list:{owner_repo}"],
            }
            seen_ids[candidate_id] = record
            all_records.append(record)
            if (i + 1) % 50 == 0:
                print(f"   processed {i + 1} ...")
                time.sleep(0.3)

    # Materialise set fields for JSON serialisation
    out = []
    for rec in seen_ids.values():
        rec["source_lists"] = sorted(rec["source_lists"])
        rec["hint_categories"] = sorted(rec["hint_categories"])
        out.append(rec)
    out.sort(key=lambda r: (-(r.get("stars") or 0), r["candidate_id"]))

    OUT_PATH.write_text(
        "\n".join(json.dumps(r) for r in out) + ("\n" if out else ""),
        encoding="utf-8",
    )
    print(f"\nwrote {len(out)} unique candidates to {OUT_PATH.relative_to(DISCOVERY_DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
