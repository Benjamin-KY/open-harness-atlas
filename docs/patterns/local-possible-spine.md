# Pattern 7 — Local-possible spine

## Problem

You have a hard constraint: data must not leave your trust boundary.
Could be regulation (healthcare, defence, government), customer
requirement (sovereign vendor RFP), threat model (air-gap, classified
network), or principle (open-source sovereignty). Every step of your
LLM pipeline must run on infrastructure **you** control. The atlas
makes this a one-filter decision — every entry now carries a
`deployment_posture` field — but composing a *whole* spine
(serve → route → orchestrate → eval → observe) entirely from
local-possible entries is still a design exercise.

## Forces

| Pull                                                | Counter-pull                                              |
|-----------------------------------------------------|-----------------------------------------------------------|
| Use the best model regardless of provider           | The best model may be cloud-only                          |
| One local-only stack                                | Some steps (e.g. judge model for eval) benefit from a stronger cloud model |
| Run on commodity hardware                           | State-of-the-art inference needs accelerators             |
| Prove to an auditor that nothing leaves             | Telemetry sinks are often SaaS                            |
| Roll your own everything                            | Roll-your-own observability is its own footgun            |

## Shape

```
   ┌──────────────────────────────────────────────────────────────┐
   │  Local trust boundary                                        │
   │                                                              │
   │   ┌────────────┐   ┌────────────┐   ┌────────────┐          │
   │   │ Inference  │──▶│ Gateway    │──▶│ Agent /    │          │
   │   │ (vLLM, etc)│   │ (litellm)  │   │ orchestrator│         │
   │   └────────────┘   └────────────┘   └────────────┘          │
   │         ▲                ▲                ▲                  │
   │         │                │                │                  │
   │   ┌────────────┐   ┌────────────┐   ┌────────────┐          │
   │   │ Models     │   │ Policy     │   │ Eval suite │          │
   │   │ (open      │   │ packs      │   │ (local-    │          │
   │   │ weights)   │   │ (YAML)     │   │ deployable)│          │
   │   └────────────┘   └────────────┘   └────────────┘          │
   │                                                              │
   │   ┌──────────────────────────────────────────────────────┐  │
   │   │ Telemetry sink (OTEL / self-hosted Langfuse)         │  │
   │   └──────────────────────────────────────────────────────┘  │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘
```

Critically: **every box must be `deployment_posture ∈ {local-only,
local-first, hybrid}`** in the atlas. Cloud-first and api-only entries
break the spine.

## Realising the shape (atlas entries)

Start from the live filter:

- 3D: <https://benjamin-ky.github.io/open-harness-atlas/#posture=local-only,local-first,hybrid>
- 2D: <https://benjamin-ky.github.io/open-harness-atlas/2d.html#posture=local-only,local-first,hybrid>
- Or click the **"Local-possible only"** quick-chip in either viewer.

| Role                         | Recommended (local-first)     | Alternatives                                            |
|------------------------------|--------------------------------|---------------------------------------------------------|
| Inference engine             | `vllm`                         | `sglang`, `ollama` (CPU/laptop), `tensorrt-llm`, `lmdeploy` |
| Gateway / router             | `litellm` (`local-first`)      | `gateway` (BifrostAI), `helicone` (with self-host opts) |
| Agent / orchestrator         | `langgraph`                    | `crewai`, `autogen`, `haystack`                         |
| Structured output            | `instructor`                   | `outlines`, `baml`                                      |
| Eval suite                   | `deepeval`                     | `promptfoo`, `ragas`, `lm-evaluation-harness`           |
| Red-team probes              | `garak`                        | `pyrit`, `giskard`                                      |
| Policy validator             | `guardrails-ai`                | `nemo-guardrails`, `llm-guard`                          |
| Telemetry (self-hosted)      | `langfuse` (self-host mode)    | `arize-phoenix`, `openllmetry`                          |
| RLHF / fine-tune (optional)  | `huggingface-trl`              | `openrlhf`, `open-instruct`                             |

> **The atlas is 93.4% local-possible** — 803/860 entries have
> `deployment_posture ∈ {local-only, local-first, hybrid}`. You're
> not picking from a niche slice; you're picking from the majority.

## Anti-patterns

1. **Local for serving, SaaS for everything else** — the inference
   engine runs locally, but observability is hosted, eval calls an API
   for the judge, the gateway dials home for licence checks. The
   spine is still cloud-bound.
2. **`local-first` ≠ "I run it without an account"** — many local-first
   tools authenticate to a registry at startup. Check the auth path
   before claiming sovereignty.
3. **`hybrid` as the default** — if you accept hybrid components, treat
   each as a feature: name what gets sent where, and ensure the cloud
   half is optional (turn it off, verify nothing breaks).
4. **Open-weights for inference, closed-judge for eval** — quality
   evaluation by a closed model recreates the dependency you set out to
   avoid.
5. **No model lifecycle plan** — the local model goes stale; without a
   refresh / replacement story you're back to "we must use the cloud
   model" in 12 months.
6. **No GPU / capacity story** — local-possible is a deployment-posture
   claim, not a free-lunch promise; you still need the hardware budget.

## See also

- [Pattern 2 — Sovereignty-preserving routing](sovereignty-preserving-routing.md) — the gateway pattern this spine is built around.
- [Pattern 6 — Provider fallback chain](provider-fallback-chain.md) — when the local model is the *terminal* fallback.
- [`docs/deployment-posture.md`](../deployment-posture.md) — the methodology behind the `deployment_posture` field.
- Use case: `route-llm-traffic` (filter by posture).
