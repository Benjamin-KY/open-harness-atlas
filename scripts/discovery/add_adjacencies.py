"""Add adjacency edges to newly-generated registry entries.

After ``generate_entries.py`` writes 491 new YAMLs, every new entry is a
disconnected node in the knowledge graph. This script adds a small but
meaningful set of ``adjacent_to`` references to each new entry so the
3D viewer renders connected clusters instead of a halo of singletons.

Heuristic (intentionally conservative — every reference must resolve
to an existing id or the schema validator will fail):

  1. Build an index of all entries grouped by (category, subcategory).
  2. For each new entry:
       a. Pick up to ``--max-edges`` siblings from the same
          (category, subcategory) bucket — preferring siblings that
          themselves have fewer adjacencies (spread the graph).
       b. Optionally connect to ONE well-known anchor in the same
          category (e.g. agent → langgraph, eval → lm-evaluation-harness)
          to ensure the new node is part of the main connected component.
  3. Only update entries that have no existing ``adjacent_to`` field —
     never overwrite a manually-curated adjacency list.

Output: writes the updated YAML files in place.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry"
CURATED = REPO / "scripts" / "discovery" / "candidates.curated.jsonl"


# Category anchors: well-known existing ids that every new entry of that
# category should connect to (if not already linked). Picked because they
# are central hubs in the v0.1.0 graph.
CATEGORY_ANCHORS = {
    "agent": ["langgraph", "autogen", "crewai", "metagpt"],
    "eval": ["lm-evaluation-harness", "deepeval", "promptfoo", "ragas"],
    "redteam": ["pyrit", "garak", "jailbreakbench", "promptmap"],
    "routing": ["litellm", "openrouter-ai", "vllm", "ollama"],
    "governance": ["guardrails-ai", "nemo-guardrails", "instructor", "outlines"],
    "education": ["harmless-harnesses", "huggingface-course", "hugging-face-agents-course"],
}


def load_curated_ids() -> set[str]:
    return {
        json.loads(line)["candidate_id"]
        for line in CURATED.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def load_all_entries() -> list[tuple[Path, dict]]:
    entries: list[tuple[Path, dict]] = []
    for path in sorted(REGISTRY.rglob("*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict):
            entries.append((path, data))
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-edges", type=int, default=4, help="Max sibling edges per new entry.")
    args = parser.parse_args(argv)

    new_ids = load_curated_ids()
    all_entries = load_all_entries()
    by_id = {e["id"]: (p, e) for p, e in all_entries}
    print(f"loaded {len(all_entries)} total entries, of which {len(new_ids)} are new")

    # Index by (category, subcategory).
    by_subcat: dict[tuple[str, str], list[str]] = defaultdict(list)
    for _path, ent in all_entries:
        cat = ent.get("category", "")
        sub = ent.get("subcategory", "") or "unsorted"
        by_subcat[(cat, sub)].append(ent["id"])

    # Track edge degrees so we balance the spread.
    degree: dict[str, int] = defaultdict(int)
    for _path, ent in all_entries:
        for ref in ent.get("adjacent_to") or []:
            degree[ent["id"]] += 1
            degree[ref] += 1

    updated = 0
    for path, ent in all_entries:
        if ent["id"] not in new_ids:
            continue
        if ent.get("adjacent_to"):
            continue
        cat = ent["category"]
        sub = ent.get("subcategory", "") or "unsorted"

        sibling_pool = [
            sid for sid in by_subcat[(cat, sub)]
            if sid != ent["id"] and sid in by_id
        ]
        sibling_pool.sort(key=lambda s: degree[s])
        siblings = sibling_pool[: args.max_edges]

        # Add one category anchor (the first one that exists and isn't already a sibling).
        anchor: str | None = None
        for cand in CATEGORY_ANCHORS.get(cat, []):
            if cand in by_id and cand != ent["id"] and cand not in siblings:
                anchor = cand
                break

        adj: list[str] = sorted(set(siblings + ([anchor] if anchor else [])))
        if not adj:
            continue

        ent["adjacent_to"] = adj
        for ref in adj:
            degree[ent["id"]] += 1
            degree[ref] += 1

        # Re-emit YAML preserving the literal-block style for description / notes.
        class LiteralStr(str):
            pass

        def literal_str_representer(dumper, data):
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

        yaml.add_representer(LiteralStr, literal_str_representer)
        for key in ("description", "sovereignty_notes"):
            if isinstance(ent.get(key), str) and "\n" in ent[key]:
                ent[key] = LiteralStr(ent[key])

        with path.open("w", encoding="utf-8") as fh:
            yaml.dump(ent, fh, sort_keys=False, allow_unicode=True, width=1000)
        updated += 1

    print(f"updated {updated} entries with adjacency edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
