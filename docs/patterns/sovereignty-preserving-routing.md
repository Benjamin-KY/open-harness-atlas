# Pattern 2 — Sovereignty-preserving routing

## Problem

Your application talks to a model. You will eventually need to (a) swap
the model, (b) add a second model for a different task, (c) move some
traffic to a self-hosted model for a sovereignty/cost reason, or
(d) prove to an auditor that you logged every call. If your code
imports a specific provider SDK directly, every one of those changes
is a refactor. If you don't have a single chokepoint, you also have
no place to enforce policy or count tokens.

## Forces

| Pull                                            | Counter-pull                                              |
|-------------------------------------------------|-----------------------------------------------------------|
| Use the official provider SDK; it's well-typed  | Hard-couples you to one provider's API shape              |
| Add a gateway "later, when we need it"          | Every existing call has to be rewritten when "later" arrives |
| One unified provider abstraction (OpenAI shape) | Lossy: lose provider-specific features (caching, function-calling dialects) |
| Always go through the gateway                   | Adds a hop; adds an operator surface to monitor           |
| Self-host everything for sovereignty            | Capacity, capability, capex                               |

## Shape

```
   ┌─────────────────────────┐
   │ Application code (one   │
   │ OpenAI-shaped client)   │
   └────────────┬────────────┘
                │
                ▼
   ┌─────────────────────────┐    ┌─────────────────────────────┐
   │  LLM gateway / router   │───▶│ Self-host inference (vLLM)  │
   │  (cost, policy, logs)   │    └─────────────────────────────┘
   └────────────┬────────────┘    ┌─────────────────────────────┐
                │                  │ Anthropic / OpenAI / Bedrock│
                ├─────────────────▶│ etc. (cloud providers)      │
                │                  └─────────────────────────────┘
                ▼
   ┌─────────────────────────┐
   │ Telemetry sink (traces, │
   │ tokens, latency, errors)│
   └─────────────────────────┘
```

The gateway is the **only** thing that knows about providers. The
application code knows only the OpenAI-shaped HTTP API. The eval and
guardrail layers sit upstream of the gateway and never see provider
details. **Sovereignty becomes a configuration concern** — swapping a
cloud model for a self-hosted one is a gateway route change, not a code
change.

## Realising the shape (atlas entries)

| Role                          | Recommended           | Alternatives                                  |
|-------------------------------|-----------------------|-----------------------------------------------|
| LLM gateway / router          | `litellm`             | `portkey-gateway`, `gateway` (BifrostAI), `helicone` |
| Self-host inference engine    | `vllm`                | `sglang`, `ollama`, `tensorrt-llm`, `lmdeploy` |
| OpenAI-compatible serving     | `vllm` (OpenAI API)   | `sglang`, `text-generation-inference`         |
| Telemetry sink                | `openllmetry`         | `langfuse`, `arize-phoenix`, `opik`           |
| Policy point (optional)       | `guardrails-ai`       | `nemo-guardrails`, `llm-guard`                |

## Anti-patterns

1. **Direct SDK imports scattered through 40 files** — pay the migration
   cost up front; it only gets worse.
2. **Gateway with no rate-limit / budget** — turns a routing layer into a
   billing surprise.
3. **Two gateways** — one team adds Portkey, another team adds litellm,
   nobody owns the abstraction. Pick one.
4. **No fallback** — single-provider gateway is still a single point of
   failure (see [Pattern 6](provider-fallback-chain.md)).
5. **Local-first as an afterthought** — if you want sovereignty to be a
   one-line change, the gateway and the self-hosted inference server
   need to be live from day one, even if they handle 1% of traffic.

## See also

- [Pattern 6 — Provider fallback chain](provider-fallback-chain.md) — adds the failover layer to this same gateway.
- [Pattern 5 — Multi-tenant policy isolation](multi-tenant-policy-isolation.md) — extends this pattern when you have N tenants.
- [Pattern 7 — Local-possible spine](local-possible-spine.md) — when the answer to "where does it run" is *only* local.
- Supply chain: `serve-and-ship-agent`.
- Use case: `route-llm-traffic`.
- Filter: deployment posture chip → tighten to local-first / local-only / hybrid.
