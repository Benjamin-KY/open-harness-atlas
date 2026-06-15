# Charter — why `open-harness-atlas` exists

> **TL;DR.** Closed-weights model providers are tightening into political
> and regulatory gardens. The technical pattern that absorbs this shock —
> already explained in *The Harness Paradigm* and operationalised in
> *Harmless Harnesses* — is the **harness**: the structural scaffolding
> *around* the model that lets you swap providers, jurisdictions, and
> weights classes without re-architecting the system. This atlas exists
> so that anyone, anywhere, can find the free OSS layer that makes that
> swap practical.

---

## 1. The triggering event — Fable / Mythos, 2026-06-13

**17:21 ET, 2026-06-13.** The US government issued an export-control
directive on national-security authority suspending API access to Claude
*Fable 5* and *Mythos 5* for all foreign nationals — both abroad and
inside the United States, including Anthropic's own non-US-citizen
employees.

Because no provider can segregate users by nationality reliably in real
time, Anthropic disabled both models for **all customers worldwide**
within hours. Anthropic publicly disagreed with the underlying
threat assessment but was legally compelled to comply.

This is the first time US export controls have explicitly targeted
**AI model API access**, not just hardware shipments, source code, or
downloadable weights. The precedent is now established: any cutting-edge
closed-weights model can, in principle, be removed from worldwide service
on national-security authority of a single jurisdiction within hours.

**Operationally**, every deployment whose *only* model tier was
`claude-fable-5` or `claude-mythos-5` paged its operators inside an hour.
Every deployment whose architecture treated the model as a swappable
backend behind a harness ran a config edit, reran a smoke suite, and
continued serving.

This atlas catalogues the OSS layer of that second pattern.

> 📖 The full worked example, with timeline + which course surfaces fired
> simultaneously, lives in
> [`harmless-harnesses/docs/SOTA_2026.md` §3.7][fable-mythos] and is
> reproduced in atlas-specific form (which *registry entries* absorbed
> the shock) at [`docs/fable-mythos-pattern-fire.md`](docs/fable-mythos-pattern-fire.md).

[fable-mythos]: https://github.com/Benjamin-KY/Harmless-Harnesses/blob/main/docs/SOTA_2026.md#37-worked-example--the-fable--mythos-export-control-recall-2026-06-13

---

## 2. The broader trend — closed gardens, not isolated incidents

Fable / Mythos is the load-bearing recent example, but the trend predates
it and survives it:

| Year | Event | Pattern |
|------|-------|---------|
| 2023–2024 | US BIS export-controls on advanced GPUs to specific jurisdictions | Hardware-tier restriction |
| 2024 | Multiple closed-weights providers add per-country / per-tenant pricing tiers | Commercial garden formation |
| 2024–2025 | Per-country availability of frontier models (waitlists, "select markets") | Geographic-tier restriction |
| 2025 | Provider-specific safety classifier APIs become non-portable | Component-tier lock-in |
| **2026-06-13** | **Fable / Mythos** — first explicit nationality-tier API recall | **User-identity-tier restriction** |

The vector keeps tightening: hardware → geography → commercial tier →
component tier → user identity. Each tightening eliminates a degree of
freedom for *downstream operators* — particularly those without standing
in the controlling jurisdiction.

A harness — the discipline of treating the model as a swappable backend
behind a structured governance scaffold — is the architectural posture
that survives this trend.

---

## 3. Indigenous-data-governance framing

The author of this atlas — Ben Kereopa-Yorke — is an Indigenous Australian
scholar and author of *The Harness Paradigm*. The Indigenous data
sovereignty (IDSov) framing motivating this atlas is the same as the one
documented in:

- [`sa-sovereign-llm-harness/docs/the-harness-paradigm.md`](https://github.com/Benjamin-KY/sa-sovereign-llm-harness/blob/main/docs/the-harness-paradigm.md) §"Indigenous communities" *(sibling repo currently private; public release planned alongside Harmless Harnesses v2.0 — see `docs/the-harness-paradigm-summary.md` in this repo for the self-contained version that motivates the atlas)*
- [`harmless-harnesses/course/00_foundation/F0_the_paradigm/`](https://github.com/Benjamin-KY/Harmless-Harnesses/blob/main/course/00_foundation/F0_the_paradigm/README.md) §6 *(sibling repo currently private; F0 module ships at harmless-harnesses v1.7+)*
- The CARE Principles for Indigenous Data Governance ([Tynan 2023](https://datasciencejournal.codata.org/articles/10.5334/dsj-2023-019); Maiam nayri Wingara)
- IEEE 2890-2025 *Recommended Practice for Provenance of Indigenous Peoples' Data*

Two distinctions matter and are preserved throughout this atlas:

1. **Individual standing vs. community gatekeeping.** The author has
   standing to *write* structural critique and *catalog* OSS tooling. A
   downstream operator who *deploys against* an Indigenous community's
   data still needs that community's free, prior, informed consent —
   this atlas does not grant or substitute for it.
2. **Closed-garden harm is not symmetric.** When a single jurisdiction
   pulls a model worldwide, the people first locked out are the ones with
   no standing in that jurisdiction — non-US nationals, Global South
   operators, Indigenous data stewards reliant on overseas-hosted
   infrastructure. The OSS harness layer reduces this asymmetry. The
   atlas exists to make it findable.

This positionality is *motivating context*, not a gatekeeping criterion:
entries are included on technical merit (open licence, model-agnostic,
free education resource) regardless of maintainer nationality or origin
country. US-origin OSS (LiteLLM, `lm-evaluation-harness`, PyRIT, etc.) is
catalogued alongside non-US-origin OSS without distinction in inclusion.

The framing is **anti-closed-garden**, not anti-anyone.

---

## 4. What this atlas is — and is not

**This atlas IS:**

- A curated catalog of free, open-source harnesses across 6 categories
  (governance, agent, eval, red-team, routing, education).
- A structured registry with a machine-readable schema, so other tools
  (procurement reviewers, knowledge-graph apps, dependency scanners) can
  consume it.
- A set of comparison matrices scoring each entry against the Harmless
  Harnesses five-component spec (Policy Router · Source Authority ·
  Prompt Composer · Output Contract · Audit Log + FSM) and a
  model-agnosticism / sovereignty rubric.
- A set of data-driven visuals — banner infographic, force-directed
  knowledge graph, five-component coverage overlay, plus an interactive
  3D / 2D WebGL viewer — all rebuildable from the registry on every
  push.
- Optionally, an interactive Neo4j-backed knowledge graph (the
  `companion/` app, generated by `create-context-graph` from the registry).

**This atlas IS NOT:**

- A benchmark or ranking. The matrices show *capabilities*, not winners.
- A replacement for `harmless-harnesses` (the course teaches *how* to
  build a harness) or `sa-sovereign-llm-harness` (the research repo
  provides primary evidence). Strict separation of concerns.
- A hosted service. The static repo and optional companion run locally.
  Nothing depends on a centralised endpoint we control.
- An exhaustive directory. Inclusion is a curation decision with
  documented policy in [`GOVERNANCE.md`](GOVERNANCE.md). The medium-scope
  cut deliberately excludes pure-RAG cores and observability stacks
  (linked as adjacencies in [`docs/adjacencies.md`](docs/adjacencies.md)).
- A policy document or legal advice. Sovereignty notes are descriptive of
  technical posture; consult counsel for jurisdictional questions.

---

## 5. Design commitments

| Commitment | Mechanism |
|---|---|
| **Free.** Every catalogued resource must be obtainable at zero cost. | `GOVERNANCE.md` inclusion policy + registry schema requires `free: true` for education entries. |
| **Open source.** Every catalogued harness must be under an OSI-approved licence. | `scripts/validate_registry.py` checks `license` field against an SPDX allowlist of OSI-approved licences. |
| **Jurisdiction-neutral by default.** Technical descriptions do not privilege any country, vendor, or political bloc. | `BRAND.md` voice section ("field guide. Neutral. Citation-heavy."); CHARTER framing is *anti-closed-garden*, not anti-jurisdiction. |
| **Mirror-able.** The atlas works as a plain GitHub render without any infrastructure. | Static-first architecture; markdown + SVG + Mermaid; no required servers, no required API keys. |
| **Drift-resistant.** Stars and dates do not silently rot. | Weekly `refresh_metadata.yml` action; "last refreshed" badge per entry. |
| **Curated, not crowd-scored.** Inclusion is editorial; metrics are factual. | `GOVERNANCE.md` curation policy; PRs reviewed against rubric, not against star-count. |
| **Reproducible.** Every visual and matrix is rebuildable from the registry. | `scripts/build_matrices.py --check` and `scripts/build_visuals.py --check` gate every PR. |

---

## 6. Reading order

If you have 5 minutes: read this charter, then [`README.md`](README.md).

If you have 30 minutes: read the charter, then
[`docs/taxonomy.md`](docs/taxonomy.md), then
[`docs/sovereignty-rubric.md`](docs/sovereignty-rubric.md), then skim
[`docs/governance-matrix.md`](docs/governance-matrix.md) and
[`docs/agent-matrix.md`](docs/agent-matrix.md).

If you have 2 hours: read everything above plus *The Harness Paradigm*
— the self-contained motivating context lives in
[`docs/the-harness-paradigm-summary.md`](docs/the-harness-paradigm-summary.md);
the full canonical doc lives in
`sa-sovereign-llm-harness/docs/the-harness-paradigm.md` *(sibling repo
currently private; public release planned)*. Then the Foundation track
of `harmless-harnesses` (F0 → F1 → F2 → F3) *(sibling repo currently
private; ships at harmless-harnesses v1.7+)*.

If you came here from the Fable / Mythos news cycle: jump straight to
[`docs/fable-mythos-pattern-fire.md`](docs/fable-mythos-pattern-fire.md)
for the worked example showing which atlas entries absorbed the shock.

---

> *— Ben Kereopa-Yorke, 2026-06-13*
