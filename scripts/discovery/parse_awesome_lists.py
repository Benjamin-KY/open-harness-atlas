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
# Probed 2026-06-14: removed 8 lists that 404 or are SAML-gated.
AWESOME_LISTS: list[tuple[str, str, str]] = [
    ("steven2358/awesome-generative-ai",        "README.md", "agent"),
    ("kyrolabs/awesome-langchain",              "README.md", "agent"),
    ("e2b-dev/awesome-ai-agents",               "README.md", "agent"),
    ("Hannibal046/Awesome-LLM",                 "README.md", "agent"),
    ("tensorchord/Awesome-LLMOps",              "README.md", "routing"),
    ("KennethanCeyer/awesome-llmops",           "README.md", "routing"),
    ("imaurer/awesome-llm-json",                "README.md", "governance"),
    ("corca-ai/awesome-llm-security",           "README.md", "redteam"),
    ("DefTruth/Awesome-LLM-Inference",          "README.md", "routing"),
    ("dair-ai/Prompt-Engineering-Guide",        "README.md", "education"),
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
    """Fetch full repo metadata via gh api repos/owner/repo. (Legacy / fallback.)"""
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


_GRAPHQL_REPO_FRAGMENT = """
fragment RepoMeta on Repository {
  nameWithOwner
  url
  homepageUrl
  description
  primaryLanguage { name }
  licenseInfo { key spdxId name }
  pushedAt
  stargazerCount
  forkCount
  isArchived
  owner { login }
}
"""


def _alias_for(idx: int) -> str:
    """Return a GraphQL-safe alias for the idx-th repo in a batch."""
    return f"r{idx}"


def fetch_repo_meta_batch(pairs: list[str]) -> dict[str, dict]:
    """Fetch metadata for up to ~80 repos in a single GraphQL request.

    Returns {owner/repo (lowercased): meta_dict}. Missing repos (404, renamed,
    private, SAML-protected, etc.) are silently absent from the returned dict.

    GitHub's GraphQL endpoint returns rc=1 from ``gh api graphql`` when ANY
    aliased field errors, but the response body still contains ``data`` for
    every alias that DID resolve. We therefore parse stdout regardless of
    exit code and only fall back to REST if no usable data came back.
    """
    if not pairs:
        return {}
    aliased_fields = []
    for i, pair in enumerate(pairs):
        if "/" not in pair:
            continue
        owner, repo = pair.split("/", 1)
        owner_esc = owner.replace('"', '\\"')
        repo_esc = repo.replace('"', '\\"')
        aliased_fields.append(
            f'  {_alias_for(i)}: repository(owner: "{owner_esc}", name: "{repo_esc}") '
            f'{{ ...RepoMeta }}'
        )
    if not aliased_fields:
        return {}
    query = "query BatchRepos {\n" + "\n".join(aliased_fields) + "\n}" + _GRAPHQL_REPO_FRAGMENT
    try:
        proc = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}"],
            capture_output=True, text=True, timeout=120, check=False,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        print("  [timeout] graphql batch", file=sys.stderr)
        return {}

    # Try to parse stdout even on non-zero rc — GitHub returns partial data
    # alongside errors, and that data is the whole point of this exercise.
    payload = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None

    if payload is None:
        print(f"  [graphql no-data rc={proc.returncode}] falling back to REST for "
              f"batch of {len(pairs)}", file=sys.stderr)
        out: dict[str, dict] = {}
        for pair in pairs:
            meta = fetch_repo_meta(pair)
            if meta:
                out[pair.lower()] = _normalise_rest_meta(meta)
        return out

    data = payload.get("data") or {}
    errors = payload.get("errors") or []
    out_map: dict[str, dict] = {}
    missing_pairs: list[str] = []
    for i, pair in enumerate(pairs):
        node = data.get(_alias_for(i)) if isinstance(data, dict) else None
        if node:
            out_map[pair.lower()] = _normalise_gql_meta(node)
        else:
            # Either errored out or the alias key was absent — try REST once.
            missing_pairs.append(pair)
    if errors:
        first = errors[0] if isinstance(errors, list) and errors else {}
        msg = first.get("message", str(first))[:160] if isinstance(first, dict) else str(first)[:160]
        print(f"  [graphql partial-error rc={proc.returncode}] {len(out_map)}/{len(pairs)} "
              f"resolved; first-error: {msg}", file=sys.stderr)
    # REST-fallback only the ones that came back empty
    for pair in missing_pairs[:20]:  # cap REST hops so a bad batch can't tank latency
        meta = fetch_repo_meta(pair)
        if meta:
            out_map[pair.lower()] = _normalise_rest_meta(meta)
    return out_map


def _normalise_gql_meta(node: dict) -> dict:
    """Project a GraphQL Repository node into the REST-shaped dict the rest
    of the script expects."""
    lic = node.get("licenseInfo") or {}
    return {
        "full_name": node.get("nameWithOwner"),
        "html_url": node.get("url"),
        "homepage": node.get("homepageUrl"),
        "description": node.get("description"),
        "language": (node.get("primaryLanguage") or {}).get("name"),
        "license": {
            "key": (lic.get("key") or "").lower() or None,
            "spdx_id": lic.get("spdxId"),
            "name": lic.get("name"),
        },
        "pushed_at": node.get("pushedAt"),
        "stargazers_count": node.get("stargazerCount") or 0,
        "forks_count": node.get("forkCount") or 0,
        "archived": bool(node.get("isArchived")),
        "owner": {"login": (node.get("owner") or {}).get("login")},
    }


def _normalise_rest_meta(meta: dict) -> dict:
    """REST already matches the shape we want, but ensure license.key is
    normalised the way the GraphQL path does."""
    lic = meta.get("license") or {}
    return {
        "full_name": meta.get("full_name"),
        "html_url": meta.get("html_url"),
        "homepage": meta.get("homepage"),
        "description": meta.get("description"),
        "language": meta.get("language"),
        "license": {
            "key": (lic.get("spdx_id") or lic.get("key") or "").lower() or None,
            "spdx_id": lic.get("spdx_id"),
            "name": lic.get("name"),
        },
        "pushed_at": meta.get("pushed_at"),
        "stargazers_count": meta.get("stargazers_count") or 0,
        "forks_count": meta.get("forks_count") or 0,
        "archived": bool(meta.get("archived")),
        "owner": meta.get("owner") or {},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse awesome-* lists for candidates.")
    parser.add_argument("--limit-lists", type=int, default=len(AWESOME_LISTS),
                        help="Limit how many lists to process (debug).")
    parser.add_argument("--limit-per-list", type=int, default=300,
                        help="Cap candidates fetched per list (rate-limit guard).")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Repos per GraphQL request (max ~80).")
    parser.add_argument("--rest-fallback", action="store_true",
                        help="Use legacy per-repo REST fetch (slow; ~21 calls/min).")
    args = parser.parse_args(argv)

    existing = load_existing_ids()
    cutoff = freshness_cutoff()
    print(f"existing ids: {len(existing)}  freshness-cutoff: {cutoff.date()}"
          f"  mode={'rest' if args.rest_fallback else 'graphql'}  batch={args.batch_size}")

    # Pass 1 — extract every (owner/repo) link from every awesome README,
    # remembering which list(s) it came from and the hint category.
    candidate_sources: dict[str, dict] = {}  # lower(pair) -> {"pair": ..., "lists": set, "hints": set}
    for owner_repo, readme_path, hint_category in AWESOME_LISTS[: args.limit_lists]:
        print(f"\n-> {owner_repo}  (hint={hint_category})")
        body = fetch_readme(owner_repo, readme_path)
        if not body:
            continue
        links = extract_github_links(body, owner_repo)
        print(f"   {len(links)} unique github.com links found")
        for pair in sorted(links)[: args.limit_per_list]:
            key = pair.lower()
            entry = candidate_sources.setdefault(key, {
                "pair": pair, "lists": set(), "hints": set(),
            })
            entry["lists"].add(owner_repo)
            entry["hints"].add(hint_category)

    # Pass 2 — drop pairs whose natural id is already in existing-ids
    # BEFORE we burn any repo-meta call on them.
    to_fetch: list[str] = []
    pre_filtered = 0
    for _key, entry in candidate_sources.items():
        cand_id = repo_to_candidate_id(entry["pair"])
        if cand_id in existing:
            pre_filtered += 1
            continue
        to_fetch.append(entry["pair"])
    print(f"\ntotal unique pairs: {len(candidate_sources)}  "
          f"pre-filtered (id in existing): {pre_filtered}  to-fetch: {len(to_fetch)}")

    # Pass 3 — fetch metadata in batches (or REST if --rest-fallback).
    meta_map: dict[str, dict] = {}
    if args.rest_fallback:
        for i, pair in enumerate(to_fetch):
            if (i + 1) % 50 == 0:
                print(f"   rest progress: {i + 1}/{len(to_fetch)} (~{i+1}/21 = "
                      f"{(i+1)/21:.1f}min)")
            meta = fetch_repo_meta(pair)
            if meta:
                meta_map[pair.lower()] = _normalise_rest_meta(meta)
            time.sleep(0.05)
    else:
        for i in range(0, len(to_fetch), args.batch_size):
            chunk = to_fetch[i:i + args.batch_size]
            print(f"   graphql batch {i // args.batch_size + 1} "
                  f"({i + 1}-{i + len(chunk)} of {len(to_fetch)})")
            meta_map.update(fetch_repo_meta_batch(chunk))

    # Pass 4 — apply OSI / freshness / archived filters; build records.
    seen_ids: dict[str, dict] = {}
    for key, entry in candidate_sources.items():
        if key not in meta_map:
            continue
        pair = entry["pair"]
        meta = meta_map[key]
        if meta.get("archived"):
            continue
        pushed = meta.get("pushed_at")
        if not is_fresh(pushed, cutoff):
            continue
        licence = ((meta.get("license") or {}).get("key") or "").lower()
        if not is_osi(licence):
            continue
        candidate_id = repo_to_candidate_id(pair)
        if candidate_id in existing:
            continue
        # First hint wins for primary_category (stable order from set sort)
        hints_sorted = sorted(entry["hints"])
        primary = hints_sorted[0]
        if candidate_id in seen_ids:
            seen_ids[candidate_id].setdefault("source_lists", set()).update(entry["lists"])
            seen_ids[candidate_id].setdefault("hint_categories", set()).update(entry["hints"])
            continue
        seen_ids[candidate_id] = {
            "category": primary,
            "primary_category": primary,
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
            "owner_login": (meta.get("owner") or {}).get("login"),
            "candidate_id": candidate_id,
            "source_lists": set(entry["lists"]),
            "hint_categories": set(entry["hints"]),
            "matched_categories": hints_sorted,
            "matched_subcategories": ["from-awesome-list"],
            "matched_queries": [f"awesome-list:{lst}" for lst in sorted(entry["lists"])],
        }

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
