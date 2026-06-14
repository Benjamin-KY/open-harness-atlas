# Pattern 5 — Multi-tenant policy isolation

## Problem

One LLM platform, N tenants. Tenant A is a healthcare client with HIPAA-
shaped PII rules. Tenant B is a marketing agency that absolutely wants
those rules turned off so it can pass campaign copy through. Tenant C
is internal and gets a $20/day budget; tenant A's budget is per-seat.
If your platform applies one global guardrail config and one global
budget, you can't onboard A and B at the same time without forking the
deployment.

## Forces

| Pull                                                | Counter-pull                                              |
|-----------------------------------------------------|-----------------------------------------------------------|
| One global policy is simpler to reason about        | A real platform has heterogeneous tenants by definition   |
| Per-tenant policy in code                           | Policy changes shouldn't require a deploy                 |
| Strict per-tenant token caps                        | Bursty workloads (eval runs, model swaps) blow the cap    |
| One trace store across tenants                      | Some tenants need data residency / per-tenant retention   |
| Self-serve policy editing                           | Self-serve = footgun unless validated                     |

## Shape

```
                ┌──────────────────────────────┐
                │  API gateway (auth, tenant   │
                │  resolution, per-tenant key) │
                └──────────────┬───────────────┘
                               │
                               ▼
        ┌────────────────────────────────────────────┐
        │     LLM gateway (per-tenant route, key,    │
        │     budget, RPM, fallback chain)           │
        └──────────────┬─────────────────────────────┘
                       │
        ┌──────────────┼─────────────────────────────┐
        ▼              ▼                              ▼
  ┌─────────┐   ┌──────────────────┐         ┌──────────────────┐
  │ Tenant A │   │ Tenant B          │   ...   │ Tenant N         │
  │ policy   │   │ policy            │         │ policy           │
  │ pack     │   │ pack              │         │ pack             │
  └────┬─────┘   └────┬─────────────┘         └────┬─────────────┘
       │             │                              │
       └──────────────┴──────────────┬───────────────┘
                                     ▼
                  ┌───────────────────────────────────┐
                  │ Trace store (per-tenant retention, │
                  │ per-tenant export, audit log)      │
                  └───────────────────────────────────┘
```

Each tenant has a **policy pack** — a versioned bundle of (model,
budget, rate-limit, guardrail config, retention). The gateway is the
single chokepoint that loads the right pack per request.

## Realising the shape (atlas entries)

| Role                                       | Recommended           | Alternatives                                  |
|--------------------------------------------|-----------------------|-----------------------------------------------|
| API gateway (auth, tenant resolution)      | `kong`                | `apache-apisix`, `higress`, `kgateway`        |
| LLM gateway (router, budget, RPM)          | `litellm`             | `portkey-gateway`, `gateway`, `helicone`      |
| Per-tenant guardrails                      | `guardrails-ai`       | `nemo-guardrails`, `llm-guard`                |
| PII redaction (data residency)             | `presidio`            | `llm-guard` (PII module)                      |
| Trace store (per-tenant retention)         | `openllmetry`         | `langfuse`, `arize-phoenix`, `opik`           |
| Policy as code                             | `opa` (out-of-atlas)  | Tenant policy packs as YAML in source control |

Filter the live atlas to this shape:

- 3D: <https://benjamin-ky.github.io/open-harness-atlas/#chain=multi-tenant-gateway>
- 2D: <https://benjamin-ky.github.io/open-harness-atlas/2d.html#chain=multi-tenant-gateway>

## Anti-patterns

1. **One config, N if-branches** — `if tenant == "healthcare": ...`
   sprinkled through the codebase. Untestable, unauditable, and one
   typo away from cross-tenant leak.
2. **Shared trace store with no tenant tag** — you can't honour a
   delete-my-data request, can't show a tenant their own data, can't
   bill correctly.
3. **Budget enforcement in application code** — budgets enforced at
   the gateway can't be circumvented by a buggy app; budgets enforced
   in the app are subject to every bug in the app.
4. **Per-tenant prompts hard-coded into the model layer** — the model
   layer should be policy-blind. The tenant policy pack provides the
   system prompt, the redaction rules, and the allowed tools.
5. **No tenant-tagged eval set** — quality regressions can be tenant-
   specific; one global regression suite hides them.

## See also

- [Pattern 2 — Sovereignty-preserving routing](sovereignty-preserving-routing.md) — the gateway abstraction this pattern extends.
- [Pattern 6 — Provider fallback chain](provider-fallback-chain.md) — multi-tenant gateways usually multi-provider too.
- [Pattern 4 — Audit-log FSM escalation](audit-log-fsm-escalation.md) — escalation routing depends on tenant.
- Supply chain: `multi-tenant-gateway`.
