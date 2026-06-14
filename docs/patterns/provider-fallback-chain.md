# Pattern 6 — Provider fallback chain

## Problem

Your model provider has an outage. Or rate-limits you mid-launch. Or
deprecates the model on a tight clock. Or starts blocking your country
of operation. Or spikes the price 4×. If your application's
availability is bounded by one provider's availability, you've made
your business a leaf node in someone else's reliability graph.

## Forces

| Pull                                                | Counter-pull                                                |
|-----------------------------------------------------|-------------------------------------------------------------|
| Use the best provider for each task                 | Best-of-N providers means N integrations to maintain        |
| Failover automatically                              | Failover model isn't capability-identical; silent quality drop |
| Cap spend per model                                 | Spend caps that flip too eagerly cause cascading failover storms |
| Same code, swap provider                            | Provider-specific features (caching, structured outputs) leak through |
| Mandatory self-hosted fallback for sovereignty      | Self-host capacity has to be standing-by, not provisioned-on-failure |

## Shape

The fallback chain is **ordered**, with a **per-step latency / error
budget**, and a **terminal step** that is either a self-hosted model or
an explicit "no model, return a safe default".

```
   ┌──────────────────┐
   │ Application call │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────────────────────────────────┐
   │ Gateway (litellm / portkey / gateway)        │
   │                                              │
   │   Step 1: primary    (e.g. Anthropic Sonnet) │
   │   Step 2: secondary  (e.g. OpenAI 4o)        │
   │   Step 3: tertiary   (e.g. self-host vLLM)   │
   │   Step 4: hard fail  (safe default / 503)    │
   │                                              │
   │   per-step budget: latency, errors, cost     │
   └────────┬─────────────────────────────────────┘
            │
            ▼
   ┌──────────────────────────────────────────────┐
   │ Telemetry (which step served, why we failed)│
   └──────────────────────────────────────────────┘
```

The terminal "hard fail" matters: a fallback chain with no termination
just keeps rolling forward into ever-worse models. **Decide the worst
acceptable response shape** — degraded answer, cached answer, refusal —
and put it at step N+1.

## Realising the shape (atlas entries)

| Role                              | Recommended           | Alternatives                              |
|-----------------------------------|-----------------------|-------------------------------------------|
| Gateway with fallback policy      | `litellm`             | `portkey-gateway`, `gateway`, `helicone`  |
| Self-host fallback inference      | `vllm`                | `sglang`, `ollama`, `tensorrt-llm`        |
| Semantic cache (degradation step) | `gptcache`            | (atlas: routing → semantic-cache)         |
| Telemetry (which step served)     | `openllmetry`         | `langfuse`, `arize-phoenix`, `opik`       |
| Regression gate (catches drift)   | `promptfoo`           | `deepeval`                                |

## Anti-patterns

1. **Round-robin instead of ordered** — the cheapest model becomes the
   primary by accident; quality drops without anyone shipping a change.
2. **Failover with no quality probe** — if the secondary model gives
   worse answers, you've traded availability for accuracy without
   noticing. Run a small eval suite against each fallback step.
3. **All steps cloud, no self-host** — your "fallback chain" is still
   one cloud-provider failure away from total outage. Include a local-
   first step.
4. **Hidden retries on top of gateway retries** — the SDK retries 3×,
   the gateway retries 3×, and you fail at the worst possible time
   with a 9× billing spike.
5. **Cost caps that don't include the failover** — caps applied per-step
   but not per-call let a failover cascade quietly blow the daily budget.
6. **Failover for any 5xx** — some 5xxs (rate-limit, transient) are
   retry-worthy; others (model deprecated) are routing changes. Don't
   treat them the same.

## See also

- [Pattern 2 — Sovereignty-preserving routing](sovereignty-preserving-routing.md) — the gateway pattern this extends.
- [Pattern 5 — Multi-tenant policy isolation](multi-tenant-policy-isolation.md) — multi-tenant + multi-provider is the common production reality.
- [Pattern 7 — Local-possible spine](local-possible-spine.md) — when the fallback chain ends at self-host.
- Use case: `route-llm-traffic`.
