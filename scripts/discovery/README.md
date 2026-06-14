# scripts/discovery/ — Phase 2 candidate-discovery harness

This folder is the curation infrastructure used to expand the
`open-harness-atlas` registry from 313 (v0.1.0) to 804 entries
through **systematic GitHub topic discovery** — not from-memory
shortlists.

The discovery pipeline is reproducible from a clean checkout:

```bash
# 1. Snapshot every id already in the registry (dedupe input).
python scripts/discovery/existing_ids.py

# 2. Sweep the planned topic matrix via `gh search repos`.
#    Output: candidates.raw.jsonl + candidates.dedup.jsonl
python -m scripts.discovery.search_github

# 3. Filter to ~500 high-signal, in-scope candidates with
#    per-category caps and conservative AI/LLM context regex.
#    Output: candidates.curated.jsonl  (the *committed* dedupe artefact).
python -m scripts.discovery.curate_candidates

# 4. Emit one schema-valid registry YAML per curated candidate
#    with conservative defaults (model_agnostic_score=3,
#    harness_paradigm_alignment=partial, governance fcc=all `none`).
python -m scripts.discovery.generate_entries

# 5. Connect each new entry to siblings + a category anchor.
python -m scripts.discovery.add_adjacencies

# 6. Validate.
python scripts/validate_registry.py
python -m pytest -q
python scripts/build_visuals.py --check
python scripts/build_matrices.py --check
python scripts/build_graph.py    # regenerate visuals/graph-data.json
```

## Files

| File                          | Role                                                     | Git-tracked? |
|------------------------------|----------------------------------------------------------|--------------|
| `existing_ids.py`            | Dump every catalogued id → `existing-ids.txt`            | Yes          |
| `existing-ids.txt`           | One id per line; dedupe input for search                 | Yes          |
| `search_github.py`           | Sweep planned topic matrix via `gh search repos`         | Yes          |
| `curate_candidates.py`       | Apply OSI / AI-context / per-category filters            | Yes          |
| `candidates.raw.jsonl`       | All raw GH hits (regenerable)                            | No (gitignored) |
| `candidates.dedup.jsonl`     | Per-fullName deduped + filtered (regenerable)            | No (gitignored) |
| `candidates.curated.jsonl`   | The **input** to `generate_entries.py`                   | Yes          |
| `generate_entries.py`        | candidate JSON → registry/<cat>/<id>.yaml                | Yes          |
| `add_adjacencies.py`         | Cluster new entries into the graph                       | Yes          |

## Curation policy (per GOVERNANCE.md §1, §8)

- **Inclusion**: OSI-approved licence; last commit ≤18 months; in one of
  six in-scope categories; verifiable from the project's own README.
- **Exclusion**: archived; non-OSI; off-topic (pure RAG cores, pure
  observability stacks, vector DBs as infra, closed-source); generic
  benchmarks that happen to share vocabulary with LLM benchmarks
  (HTTP/database/system benchmarks); cybersecurity tooling without
  explicit LLM/AI context.
- **Conservative defaults**: `model_agnostic_score=3` (median),
  `harness_paradigm_alignment=partial`, governance `five_component_coverage`
  all `none` unless the description explicitly proves a stronger posture.
- **Sovereignty score is intentionally conservative** — every auto-generated
  entry includes a one-line `sovereignty_notes` flag that the score is an
  auto-curated default and should be refined on first manual README review.

## Re-running on a different date

GitHub star counts and topic memberships drift. Re-running steps 2-3 on
a different date will produce a different `candidates.curated.jsonl` and
therefore a different set of generated entries. The committed
`candidates.curated.jsonl` is the source-of-truth deterministic input
that pairs with the v0.2.0+ registry entries.
