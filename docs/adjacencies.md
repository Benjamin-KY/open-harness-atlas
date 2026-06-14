# Adjacencies — cross-links to out-of-scope projects

This document tracks **projects that are deliberately not catalogued** in
`registry/` per [`GOVERNANCE.md`](../GOVERNANCE.md) §8 but that *are*
ecosystem-adjacent to one or more registered entries. They are listed
here so readers and contributors have a single place to confirm "yes,
this was considered, here's where it sits".

The line between in-scope and adjacent is **feature surface, not
project lineage**: a project becomes in-scope the moment it ships
agent / eval / governance / red-team / routing / free-education features
that qualify under §1; until then, it lives here.

For each adjacency we record:

- **Why adjacent** — what the project does that *is* useful to atlas
  readers
- **Why not in-scope** — which §8 clause excludes it from the registry
- **Registered relatives** — which catalogued entries link to it via
  `adjacent_to` or share users

---

## Pure-infrastructure vector databases

| Project | Why adjacent | Why not in-scope | Registered relatives |
|---|---|---|---|
| **Pinecone** (closed-source service) | Vector backend used by many catalogued RAG-enabled agent frameworks | §8 closed-source; §8 pure infrastructure | autogen, langgraph, openhands |
| **Weaviate core** | Open-source vector DB | §8 pure infrastructure (no agent/eval/governance surface in `weaviate-core`) | haystack, llama-index (when used as RAG-cores; see below) |
| **Qdrant core** | Open-source vector DB | §8 pure infrastructure | metagpt, autogen |
| **Milvus** / **pgvector** / **Chroma** (core) | Open-source vector backends | §8 pure infrastructure | most agent frameworks |

These are catalogued by the [LLMOps surveys](https://github.com/tensorchord/awesome-llmops)
and the [vector-database awesome-list](https://github.com/dangkhoasdc/awesome-vector-database)
if you need the comparison surface they intentionally provide.

---

## Pure observability / tracing stacks without an eval surface

Projects that *only* trace LLM calls without eval runners, output-contract
validation, or routing intelligence are out-of-scope. The current registry
does include observability projects that ship eval or governance features
(e.g., `langfuse`, `arize-phoenix`, `openllmetry`, `mlflow-ai-gateway`)
under whichever category matches their primary user-facing harness
function.

| Project | Why adjacent | Why not in-scope | Registered relatives |
|---|---|---|---|
| **OpenTelemetry GenAI semantic conventions** (the spec, not OpenLLMetry the OSS impl) | Defines the LLM telemetry vocabulary the catalogued tracing tools emit | §8 — a specification, not an implementation users install | openllmetry, arize-phoenix |
| **Grafana Loki** / **Prometheus** / **Tempo** | Generic observability backends often paired with LLM tracing | §8 not LLM-specific | arize-phoenix, langfuse |

---

## Pure RAG cores without agent/eval/governance surface

| Project | Why adjacent | Why not in-scope | Registered relatives |
|---|---|---|---|
| **LlamaIndex Core 0.x** (legacy `gpt_index` era) | Original retrieval-pipeline library | §8 pure RAG core in its early form; the modern `llama-index` ships agent workflows and *is* catalogued under agent | langchain (catalogued as a foundational agent reference) |

Note: the current `haystack` and `txtai` *are* catalogued — they have
shipped agent / eval features since the v0.1.0 seed was authored.

---

## Closed-source services

Not cross-linked per §8. The atlas is jurisdiction-neutral and
OSI-only by design — closed services are visible enough through their
own marketing.

---

## Paid education

Excluded per §8. Coursera "Generative AI" specialisations, Udacity
nanodegrees, paid O'Reilly tracks, etc. The registry's
`education/` category catalogues *free* alternatives covering the
same material wherever possible.

---

## How to add an adjacency entry

If you find an out-of-scope project that a reader would reasonably
expect to be in the atlas, open a PR adding a row to the matching
table above with the four fields. The atlas curator will review.

Adjacencies do **not** appear in the knowledge graph — the graph
shows only catalogued entries to keep the visual surface honest.
