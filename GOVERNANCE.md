# Governance — curation policy for `open-harness-atlas`

This document is the binding policy for what enters the registry, what
stays, and what is removed. It is referenced by
[`CONTRIBUTING.md`](CONTRIBUTING.md) and enforced by
`scripts/validate_registry.py` plus reviewer judgement.

---

## 1. Inclusion criteria (all must hold)

A project may be added to the registry if and only if **all** of the
following hold at the time of merge:

1. **Open licence.** The primary work is published under an
   [OSI-approved](https://opensource.org/licenses) licence. SPDX
   identifier required.
2. **Free.** Obtainable at zero monetary cost (donations to the project
   are fine; pay-walled tiers of the *catalogued artefact* are not).
3. **Maintained or reference-quality.** Either:
   - last meaningful commit within the past 18 months, **or**
   - explicitly named in a published peer-reviewed paper / standard
     where its reference-quality status is the reason for inclusion.
4. **In scope.** Fits one of the six categories defined in
   [`CONTRIBUTING.md`](CONTRIBUTING.md). Out-of-scope projects are
   cross-linked in [`docs/adjacencies.md`](docs/adjacencies.md), not
   catalogued.
5. **Verifiable.** All declared fields (`repo_url`, `homepage`,
   `license`, `primary_language`) can be confirmed from the project's
   own canonical source.
6. **Non-deceptive.** The entry's `description` and scoring reflect what
   the project *implements*, not what its marketing claims.

---

## 2. Scoring rubric

### 2.1 `model_agnostic_score` (0–5)

| Score | Meaning |
|-------|---------|
| 0 | Hard-locked to a single model provider; swap requires rewrite. |
| 1 | Single-provider primary; another provider experimentally supported. |
| 2 | Multi-provider via plugin, but limited to commercial APIs. |
| 3 | Multi-provider including at least one local-weights option (Ollama / vLLM / llama.cpp). |
| 4 | Multi-provider, fully OpenAI-compatible-endpoint pluggable, local options first-class. |
| 5 | Provider is a config string; same code path runs against commercial, hosted-OSS, and fully-local backends without behavioural drift. |

Justification (1–3 sentences) **must** appear in `sovereignty_notes`.

### 2.2 `five_component_coverage`

Scored independently for each of the Harmless Harnesses five components:

| Component | What scores `native` |
|---|---|
| **Policy Router** | Explicit routing of inputs to known routes before model call (not just URL routing). |
| **Source Authority** | Citations are checked against an allowlist; un-cited claims are non-shippable. |
| **Prompt Composer** | A single governance-prompt template is the only system-role surface. |
| **Output Contract** | Malformed / out-of-policy output is rejected, not "warned about". |
| **Audit Log + FSM** | Refusal and escalation are deterministic state-machine transitions, not stochastic completions. |

Values: `none` · `partial` · `native`. Conservative scoring is preferred
— a project that *almost* enforces an output contract scores `partial`,
not `native`.

### 2.3 `harness_paradigm_alignment`

A holistic call by the curator:

| Value | Meaning |
|---|---|
| `none` | Project is useful in the ecosystem but does not embody the harness pattern (e.g., a pure routing layer). |
| `partial` | Implements 1–2 components fully or many partially. |
| `aligned` | Implements 3+ components and pitches itself as governance-first. |
| `native` | Built explicitly as a five-component harness from day one (current registry example: `harmless-harnesses`). |

---

## 3. Removal criteria

An entry is removed (or moved to an `archived/` subfolder, retained for
historical reference) when **any** of the following hold:

1. **Archived 12+ months** with no active fork (or the fork itself fails
   inclusion criteria).
2. **Licence change** to a non-OSI licence. The weekly refresh bot
   detects this via SPDX mismatch and opens an auto-issue.
3. **Substantive maintainer request.** A maintainer asks for removal
   in writing (issue or email). Removal is honoured within one week.
4. **Scope drift.** The project pivots out of the six in-scope
   categories.
5. **Sustained misrepresentation.** Marketing claims diverge so far
   from implementation reality that curated `description` and scores
   would mislead readers, and the maintainers will not engage on
   correction.

Removal does not imply a moral judgement — the field changes fast.

---

## 4. Anti-cheerleading discipline

The atlas is a **field guide**, not a marketing channel. To stay that
way:

- **No "winners" in comparison matrices.** Capabilities, not rankings.
- **No emoji-grade reviews.** No 🚀 🔥 ⭐ in entry prose; star counts are
  metadata, not editorial commentary.
- **Neutral tagline / description.** Maximum 200 chars for tagline;
  description written in field-guide voice (see
  [`BRAND.md`](BRAND.md) §Cross-repo brand contract).
- **Vendor disclosures.** If the maintainer is a commercial entity,
  `maintainer.type: company` is required. No special placement or
  badging.
- **No paid promotion.** The atlas accepts no advertising, sponsorship,
  or placement fees. Ever.

---

## 5. Conflict of interest

The current author maintains two projects that are also catalogued:
[`harmless-harnesses`](https://github.com/Benjamin-KY/Harmless-Harnesses)
and
[`sa-sovereign-llm-harness`](https://github.com/Benjamin-KY/sa-sovereign-llm-harness)
*(both sibling repos currently private; public releases planned —
the atlas remains self-contained without them, see
[`docs/the-harness-paradigm-summary.md`](docs/the-harness-paradigm-summary.md))*.
To manage this:

- Both entries follow the same schema and scoring rubric as every other
  entry.
- Both entries are scored conservatively (i.e., never `native` on a
  component unless an external reviewer would agree from the code).
- A PR labelled `coi-self-curation` is required for any change to either
  entry. A non-author reviewer is requested before merge.

---

## 6. Dispute resolution

If a maintainer disagrees with their entry's scoring or framing:

1. Open a GitHub issue labelled `dispute` describing the disagreement
   with specific references to commits / docs.
2. The curator responds within two weeks with either:
   - an acceptance and a PR with the change, or
   - a published-in-issue rationale for the current state, citing the
     rubric.
3. If unresolved, the maintainer may request removal under §3.3.

There is no appeal beyond removal: this is a single-curator atlas, not
a governance body. The
[`CITATION.cff`](CITATION.cff) attribution makes the editorial
responsibility explicit and citable.

---

## 7. Versioning of the policy itself

This file is versioned with the repository. Material policy changes
(new categories, rubric changes, removal trigger changes) are flagged in
[`CHANGELOG.md`](CHANGELOG.md) under a **"Governance"** subheading and
bump the **minor** version of the atlas.

---

## 8. Out-of-scope by design

The following are *deliberately* not catalogued, to keep the atlas
focused:

- **Pure-infrastructure vector databases** (Pinecone-the-database, Weaviate
  core, Qdrant core when used purely as a vector index without an
  agent/eval/governance surface). Cross-linked in
  [`docs/adjacencies.md`](docs/adjacencies.md) when referenced by a
  registered harness.
- **Pure observability / tracing stacks without an eval or governance
  feature surface.** Projects that *only* trace LLM calls without
  eval runners, output-contract validation, or routing intelligence are
  out-of-scope. Projects with eval or governance features (e.g.,
  Langfuse Evals, Arize Phoenix LLM Evals, OpenLLMetry semantic
  conventions enforcing governance contracts) are catalogued under the
  category that matches their primary user-facing harness function.
- **Pure RAG cores without an agent / eval / governance surface.**
  Standalone retrieval pipelines are out-of-scope; the same project
  *becomes* in-scope once it ships agent / eval / governance features
  (e.g., the current Haystack is an agent framework, not the 1.x RAG
  core; txtai now ships LLM-judge eval harness functions).
- **Closed-source services** of any kind. Not cross-linked.
- **Paid courses, paid books, paywalled tutorials.** Not catalogued in
  `registry/education/`.
- **Personal blog posts.** Even excellent ones — too unstable and
  numerous to curate fairly.

The line is **feature surface, not project lineage** — a project earns
inclusion by shipping in-scope features, regardless of what historical
category it's been pigeonholed in. Out-of-scope is not "low value" — it
is "would distort the catalog if included as-is".

**Why this language was tightened in v0.2.0**: the original v0.1.0
phrasing named specific projects as out-of-scope, but several of those
projects (Langfuse, Phoenix, OpenLLMetry, Haystack, txtai, MLflow AI
Gateway) had since shipped substantial eval / governance / routing
features that *did* qualify them. The policy now describes the feature
boundary, and the catalog reflects the lived reality of each project's
current shipping surface, not its historical lineage.

---

## 9. Changes to this policy

Open a PR with the proposed change to this file plus a brief
motivating note in `CHANGELOG.md`. Substantive changes (new
inclusion/removal criteria, new categories) require a 14-day discussion
window via GitHub Discussions before merge.
