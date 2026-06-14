# Sovereignty rubric

This document defines how `open-harness-atlas` scores
**`model_agnostic_score`** (0–5) and the axes used in
`visuals/sovereignty-radial.svg`. It is referenced from
[`CONTRIBUTING.md`](../CONTRIBUTING.md) and
[`GOVERNANCE.md`](../GOVERNANCE.md) §2.

> ⚠ **Informational, not normative for *people*.** Country of origin
> (`origin_country` in the registry schema) is included for transparency —
> not as a quality signal, a preference signal, or a political signal.
> The atlas catalogues US-origin OSS (LiteLLM, `lm-evaluation-harness`,
> PyRIT, NeMo Guardrails…) alongside non-US-origin OSS without
> distinction in inclusion. The sovereignty rubric scores the **technical
> posture** of the project (self-hostability, licence openness,
> backend pluggability) — not the politics or nationality of its authors.

---

## 1. `model_agnostic_score` — the primary axis

The atlas's central claim: harnesses are the foundation for
model-agnostic workloads. The `model_agnostic_score` measures how much
freedom a downstream operator has to swap model backends without
re-architecting.

| Score | Definition | Concrete test |
|:---:|---|---|
| **0** | Hard-locked to a single provider; swapping requires source-level rewrite. | Provider name is hard-coded in import paths or function names. |
| **1** | Single-provider primary; another provider supported experimentally or via fork. | Provider config exists but only one is documented / tested. |
| **2** | Multi-provider via plugin / adapter, but limited to commercial hosted APIs. | At least two of {OpenAI, Anthropic, Google, Cohere, etc.} ship as first-party adapters; no local-weights option. |
| **3** | Multi-provider including at least one local-weights option. | Documented support for Ollama, vLLM, llama.cpp, or text-generation-inference. |
| **4** | Multi-provider, fully OpenAI-compatible-endpoint pluggable; local options first-class (CI-tested or named in primary docs). | A single config string (`provider:` or `base_url:`) swaps backend with no code change. |
| **5** | Provider is a config string; same code path runs against commercial, hosted-OSS, and fully-local backends without behavioural drift. | Add a new OpenAI-compatible endpoint and the project works against it without code change, plugin registration, or feature regression. |

**Conservative scoring is required.** A project that *almost* supports
local backends scores 3, not 4. A project where local-backend support
exists but no smoke test covers it scores 4, not 5.

**Justification (1–3 sentences) MUST appear in `sovereignty_notes`** —
schema-enforced.

---

## 2. Sovereignty radial — secondary axes

`visuals/sovereignty-radial.svg` plots each entry across **four axes**.
This is a *visual* tool — none of these axes affect inclusion.

| Axis | Range | Meaning |
|---|---|---|
| **Model-agnosticism** | 0–5 | The score above. |
| **Licence openness** | 0–4 | 0 = source-available non-OSI; 1 = copyleft (GPL/AGPL); 2 = weak copyleft (LGPL/MPL); 3 = permissive (Apache-2.0 / MIT / BSD); 4 = public-domain or CC0. Higher = fewer downstream restrictions on integration. |
| **Self-hostability** | 0–3 | 0 = SaaS only; 1 = self-host requires non-OSS dependency; 2 = self-host fully OSS but requires manual orchestration; 3 = self-host one-liner (Docker / Helm / nix). |
| **Telemetry default** | 0–2 | 0 = phones home by default with no documented opt-out; 1 = phones home by default with documented opt-out; 2 = no telemetry by default. |

The total is **not a single number** — the radial visualises each axis
independently so a reader can see the *shape* of an entry's posture.

---

## 3. What this rubric does **not** score

- **Popularity.** GitHub stars are a separate metadata field; they do
  not enter the rubric.
- **Code quality.** Out of scope.
- **Safety effectiveness.** Different harnesses target different harm
  classes; cross-comparison would be misleading. See
  [`docs/governance-matrix.md`](governance-matrix.md) for *capabilities*
  only, never *winners*.
- **Maintainer organisation type or nationality.** Both are recorded
  for transparency and excluded from scoring per §0.

---

## 4. Worked examples (illustrative — final scores live in the registry)

### Routing — `litellm`

> **`model_agnostic_score: 5`** — single config string changes the
> backend; OpenAI / Anthropic / Cohere / local Ollama / local vLLM /
> local llama.cpp all share one code path; new endpoint integration
> takes a `base_url:` setting and no code change.

### Governance — `nemo-guardrails`

> **`model_agnostic_score: 4`** — multi-provider via the rails
> configuration (`models:` list supports OpenAI, Anthropic, vLLM,
> Ollama, and any OpenAI-compatible endpoint via `base_url`).
> Conservative 4 not 5 because the rails DSL (Colang) interacts
> differently with model temperatures and stop-token handling across
> providers, so behavioural drift is observable.

### Agent — `pydanticai`

> **`model_agnostic_score: 4`** — first-class adapters for OpenAI,
> Anthropic, Google, Groq, Mistral, Ollama, and arbitrary
> OpenAI-compatible endpoints. Conservative 4 not 5 because some
> structured-output features depend on provider-specific tool-call
> formats.

### Eval — `lm-evaluation-harness`

> **`model_agnostic_score: 5`** — model is a parametrised module
> (`--model hf` / `vllm` / `openai-chat-completions` / `local-completions`);
> hundreds of tasks all run unchanged against any of them. New backends
> are added by writing a small model class against a stable interface.

---

## 5. Re-scoring an existing entry

Per [`GOVERNANCE.md`](../GOVERNANCE.md) §6, anyone (including
maintainers) can propose a re-score by opening an issue with the
*Update entry* template. The PR must:

1. Cite the project's own primary sources (commit, release note, doc
   page) that support the proposed change.
2. Re-justify the new score in 1–3 sentences in `sovereignty_notes`.
3. Pass `python scripts/validate_registry.py` and the test suite.

---

## 6. Why no overall sovereignty score?

A single composite would create a false ranking and pressure the rubric
into being read as a benchmark. The atlas is a **field guide**: each
axis is presented independently so an operator can choose entries
against their *actual* constraint set (e.g., "I need score ≥ 4 on
self-hostability and ≥ 3 on telemetry default; everything else is
flexible").

The Harmless Harnesses course teaches the same discipline in P10 §10:
operators pin to *their* constraints, not to a vendor's preferred
ranking.

---

## 7. Adoption tier overlay (visual caveat)

Curators add entries to the registry as soon as they pass inclusion
criteria — which means the catalogue intentionally mixes landmarks
(LangGraph, lm-evaluation-harness) with brand-new repos that may not
yet have any independent adoption signal. To keep the visualisation
honest about this, every node is tagged with an **adoption tier**
that drives its opacity, radius, and outline style in both the 3D
and 2D viewers.

Tier is **computed**, not self-reported in YAML — this prevents
curators from inflating their own entries. Computation happens in
`scripts/compute_tier.py` from the
[`registry/_metadata/*.json`](../registry/_metadata) sidecars (stars,
created_at, last_commit_at, archived flag).

| Tier | Heuristic | Visual encoding |
|---|---|---|
| **landmark** | ≥ 30k stars **or** ≥ 3 yr age + ≥ 5k stars + commit ≤ 30 d | full opacity · larger radius · solid outline |
| **established** | ≥ 1k stars · ≥ 1 yr age · commit ≤ 180 d | full opacity · normal radius · solid outline |
| **emerging** | ≥ 100 stars · ≥ 3 mo age · commit ≤ 180 d | 70% opacity · normal radius · solid outline |
| **frontier** | passes inclusion criteria but no independent adoption signal yet | 40% opacity · smaller radius · dashed outline |
| **unknown** | sidecar missing or fetch failed (e.g., SSO-restricted org) | renders as `frontier` |

The thresholds are tuned against the live catalogue so `landmark`
stays around 10–15% of entries (visually distinguishable), `frontier`
is the long tail (~45%), and the middle tiers split the rest. When
`created_at` is unavailable, the script falls back to higher star
thresholds as a maturity proxy.

---

## 8. Uptake velocity (the flow measure)

Tier is a **stock** measure (cumulative state). It rewards old projects
and under-counts fast-rising newcomers. To complement it, the atlas
computes **stars-per-week velocity** from the trailing 4-week and
12-week windows of the sidecar snapshot history.

- `scripts/refresh_metadata.py` is append-only: each weekly cron run
  writes a new snapshot to the `snapshots[]` list per sidecar, capped
  at the last 26 snapshots (≈ 6 months).
- `scripts/compute_velocity.py` reads those snapshots and emits
  `registry/_metadata/_velocity.json` plus an auto-generated
  [`docs/rising.md`](rising.md) (top 25 by 4-week velocity).
- The 3D and 2D viewers render a tiny inline-SVG sparkline in each
  node's detail panel and surface `stars / wk (4w)` alongside the
  raw star count.

Like the tier overlay, this is intentionally **not** a leaderboard
(see §6) — it surfaces what's gaining traction *right now* so
operators can decide whether to invest attention in something newer
than the landmarks. Entries with fewer than two snapshots show no
velocity; the data accrues as the scheduled refresh runs.
