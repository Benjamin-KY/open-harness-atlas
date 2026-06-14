"""Discovery harness for open-harness-atlas Phase 2 registry expansion.

Modules:
  existing_ids  — dump the IDs of every YAML already in the registry
                  so the candidate search never proposes a duplicate.
  search_github — drive `gh search repos` across a planned matrix of
                  topics; emit JSONL of candidates (one record per line)
                  with the metadata needed to build a registry entry.
  generate_entries — convert curated candidate JSON → schema-valid YAML
                     under registry/<category>/<id>.yaml with conservative
                     defaults (per GOVERNANCE.md §2 "conservative scoring").
  candidates_schema — JSON Schema (informational) for the candidate record.

All scripts are intentionally hermetic where possible (no LLM calls,
deterministic transforms). The only side-effects:
  - search_github invokes `gh search repos` (network).
  - generate_entries writes YAML files under registry/.
"""
