# The Harness Paradigm — Self-Contained Summary

This page is the **self-contained** summary of the motivating thesis
behind open-harness-atlas. It exists so that a reader who arrives at
this repo without access to the author's sibling repositories
(`sa-sovereign-llm-harness`, `harmless-harnesses` — both currently
private with public release planned) still has the conceptual context
they need to use the atlas correctly.

The canonical, fully-cited version of the paradigm essay lives in
`sa-sovereign-llm-harness/docs/the-harness-paradigm.md`. This summary
is shorter, lossy by design, and authored by Ben Kereopa-Yorke.

---

## 1. What the harness paradigm names

The "harness paradigm" is a short name for an emerging architectural
posture in OSS LLM/agent systems:

- **Model providers become interchangeable infrastructure.** The
  difference between OpenAI, Anthropic, Google, Mistral, Qwen, Llama,
  Phi, Granite and the next frontier model becomes a routing decision,
  not a product decision.
- **Application identity moves up the stack** into a *harness*: a
  composed set of evaluations, policy validators, prompt composers,
  tool routers, output contracts, and audit-log finite state machines
  that survives a model swap.
- **Sovereignty, in this frame, is the ability to swap.** A system
  that cannot survive a unilateral model-provider decision (price
  change, region pull, capability removal, licence rewrite) does not
  control its own posture.

The atlas catalogues the **OSS layer** that makes this swap possible.

## 2. Why "harness," not "framework" or "stack"

A *framework* implies one author's opinions you inherit wholesale.
A *stack* implies a vertical commitment.

A *harness* is a piece of equipment a working animal wears so that
human direction can be applied without harming the animal. It implies:

- the model is not the agent (the harness wears the model)
- the harness mediates, it does not generate
- replacing the model does not require replacing the harness
- the harness carries the application's safety properties, not the model

## 3. The five components of a harness

This atlas inherits the five-component decomposition documented in the
sibling-repo reference implementation. Briefly:

1. **Policy router** — decides which model/provider/route serves a
   given intent, given posture and constraints.
2. **Source-of-truth authority** — the read-side scaffold that grounds
   prompts in verifiable context (RAG, knowledge graph, structured store).
3. **Prompt composer** — assembles the prompt from intent + context +
   policy, deterministically, with audit-grade reproducibility.
4. **Output contract** — validates and (where applicable) repairs
   model output against a schema before it reaches the caller.
5. **Audit-log FSM** — every state transition (which model, which
   policy, which retrieved context, which output) is captured into
   a forensically-coherent log.

`docs/five-component-overlay.md` and the governance/agent matrices
show how individual atlas entries cover these components.

## 4. Indigenous-data-sovereignty (IDSov) framing

Two distinctions, preserved throughout the atlas:

1. **Individual standing vs. community gatekeeping.** The atlas author
   is an Indigenous Australian scholar with standing to *write*
   structural critique and *catalog* OSS tooling. A downstream operator
   who *deploys against* an Indigenous community's data still needs
   that community's free, prior, informed consent — this atlas does
   not grant or substitute for it.
2. **Closed-garden harm is not symmetric.** When a single jurisdiction
   pulls a model worldwide, the people first locked out are the ones
   with no standing in that jurisdiction — non-US nationals, Global
   South operators, Indigenous data stewards reliant on overseas-hosted
   infrastructure. The OSS harness layer reduces this asymmetry. The
   atlas exists to make it findable.

References that ground this framing:

- [Tynan 2023 — CARE Principles for Indigenous Data Governance](https://datasciencejournal.codata.org/articles/10.5334/dsj-2023-019)
  (CODATA Data Science Journal)
- Maiam nayri Wingara — Indigenous data sovereignty principles
- IEEE 2890-2025 *Recommended Practice for Provenance of Indigenous
  Peoples' Data*

## 5. What the atlas does and does not claim

The atlas **does** claim:

- 860 OSI-licensed projects across six functional categories at
  v0.4.0, each schema-validated, license-filtered, and curated for
  scope alignment with the harness paradigm.
- A model-agnostic-score (MAS) and deployment-posture per entry,
  computed against documented rubrics.
- Curator-reviewed status disclosed honestly per entry
  (`Auto-ingested` flag → backlog).

The atlas **does not** claim:

- That MAS or tier is a quality ranking (they are signals about
  swappability and adoption, not endorsement).
- That CARE-aligned community consent has been obtained for
  every deployment context implied by the catalogued projects.
- That every entry is suitable for every operator — that judgement
  is downstream of this catalogue.

## 6. How to use this summary

If you came here from `CHARTER.md` or `BRAND.md`'s broken sibling-repo
links, this page is enough to use the atlas without needing the
sibling repos.

If you are reviewing the atlas for academic, procurement, or
governance purposes, you may wish to cite the canonical paradigm
essay once `sa-sovereign-llm-harness` is publicly released; until
then, cite this summary plus the CARE / IEEE 2890-2025 references
above.

---

*— Ben Kereopa-Yorke, 2026-06-15 (summary; full paradigm essay in
`sa-sovereign-llm-harness/docs/the-harness-paradigm.md`)*
