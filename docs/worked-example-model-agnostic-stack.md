# Worked example — a model-agnostic, locally-deployable LLM stack

A long-form walkthrough that takes a real scenario and assembles a
production stack from the atlas, **without locking the design to any
single model provider** and **with deployment posture as a first-class
design dimension**.

This doc is the connective tissue between three other surfaces:

| You want to…                                          | Read                                              |
|--------------------------------------------------------|---------------------------------------------------|
| Find harnesses for a specific job                      | [`companion/use_cases.yaml`](../companion/use_cases.yaml) |
| Copy a validated 3-7 step stack                        | [`companion/supply_chains.yaml`](../companion/supply_chains.yaml) |
| Understand the design pattern behind a stack           | [`docs/patterns/`](patterns/README.md)            |
| **Watch a stack get built end-to-end with reasoning**  | **This document**                                 |
| Filter by where each component runs                    | [`docs/deployment-posture.md`](deployment-posture.md) |

## The scenario

> An Australian government agency wants an internal LLM assistant. Hard
> constraints: (a) every byte of customer data must stay in Australia,
> (b) the platform must support multiple internal teams with different
> retention rules, (c) the agency cannot ship a feature it cannot audit,
> (d) it must survive the loss of any single model provider.

We'll build the stack in seven steps. At each step we identify the
**design pattern** that applies, narrow to **`deployment_posture`-
compatible** atlas entries, and pick a concrete tool — but also list
two or three alternatives so the design stays model-agnostic.

You can follow along in the live atlas:

- 3D viewer: <https://benjamin-ky.github.io/open-harness-atlas/>
- 2D viewer: <https://benjamin-ky.github.io/open-harness-atlas/2d.html>

Click the **Deployment posture** panel and untick `cloud-first` and
`api-only`. Or just click the **"Local-possible only"** quick-chip.
That collapses the catalogue to the 736 entries (92.8%) that can run
inside the agency's trust boundary.

---

## Step 1 — Inference engine

**Pattern**: [Pattern 7 — Local-possible spine](patterns/local-possible-spine.md)

**Constraint mapping**: hard constraint (a) — data residency — eliminates
every `api-only` and most `cloud-first` inference paths. We need a
model server we can run on our own GPU pool.

**Filter the atlas**: category=routing, deployment_posture=local-only OR
local-first, subcategory ∈ {inference-server, serving}.

**Pick**: `vllm` (`deployment_posture=local-first`, ~28k★, OpenAI-shaped
HTTP API, runs every popular open-weights family).

**Alternatives surfaced by the atlas**:
- `sglang` — high-throughput, similar shape.
- `tensorrt-llm` — NVIDIA-specific, fastest where the hardware matches.
- `ollama` — laptop / edge deployment, model-pull UX.
- `lmdeploy` — competitive throughput in the Chinese ecosystem.

**Why this is model-agnostic**: vLLM serves Llama, Qwen, Mistral, Phi,
DeepSeek, Gemma — any architecture vLLM has merged. Swapping which
weights we serve is a config change.

**Why this is sovereignty-preserving**: vLLM runs in the agency's VPC
(or air-gapped pool). No bytes leave.

---

## Step 2 — Gateway / router

**Pattern**: [Pattern 2 — Sovereignty-preserving routing](patterns/sovereignty-preserving-routing.md)

**Why we need it**: even with one model, we want a chokepoint for
budgets, rate-limits, logs, and the ability to add a second model
without a code change. Hard constraint (d) — survive provider loss —
makes this non-negotiable.

**Filter the atlas**: category=routing, deployment_posture ∈ {local-only,
local-first}, subcategory ∈ {llm-gateway, llm-proxy, llm-router}.

**Pick**: `litellm` (~15k★, drop-in OpenAI shape, supports 100+
providers including self-hosted vLLM, has a router with priority and
fallback).

**Alternatives surfaced by the atlas**:
- `portkey-gateway` — strong observability, hybrid posture.
- `gateway` (BifrostAI) — Indian-maintained, plugin-friendly.
- `helicone` — open-source observability + gateway.

**Why this is model-agnostic**: every model — vLLM, an Australian
Anthropic-via-Bedrock failover, an OpenAI account for non-sensitive
work — sits behind the same OpenAI-shaped API.

---

## Step 3 — Agent / orchestrator

**Pattern**: [Pattern 4 — Audit-log FSM escalation](patterns/audit-log-fsm-escalation.md)

**Why we need it**: hard constraint (c) — auditable — means the
agent's state machine must be inspectable, not "a chain that loops
until done". `LangGraph` is built around a FSM.

**Filter the atlas**: category=agent, deployment_posture=local-first,
subcategory ∈ {agent-framework, multi-agent}.

**Pick**: `langgraph` (~10k★, FSM-shaped, supports checkpointed state,
human-in-the-loop interrupts, full state replay).

**Alternatives surfaced by the atlas**:
- `crewai` — role-based multi-agent.
- `autogen` — Microsoft's multi-agent framework.
- `haystack` — long-running, pipeline-shaped (closer to RAG).

**Audit-log integration** comes from step 7 — every state transition is
emitted with a structured record.

---

## Step 4 — Structured outputs

**Pattern**: enables [Pattern 3 — Red-team then harden](patterns/redteam-then-harden.md) and [Pattern 4](patterns/audit-log-fsm-escalation.md)

**Why we need it**: the agent's decisions must be machine-parseable to
audit. Free-text outputs are an auditor's nightmare. Structured outputs
also enable the policy validator in the next step.

**Filter the atlas**: category=governance, deployment_posture ∈
{local-only, local-first}, subcategory ∈ {structured-output, validator}.

**Pick**: `instructor` (~10k★, Pydantic-shaped, model-agnostic).

**Alternatives**:
- `outlines` — constrained decoding (works inside vLLM).
- `baml` — schema-first prompt language.
- `jsonformer` — guaranteed JSON output.

---

## Step 5 — Policy validator (per-tenant)

**Pattern**: [Pattern 5 — Multi-tenant policy isolation](patterns/multi-tenant-policy-isolation.md)

**Constraint mapping**: hard constraint (b) — multi-team, different
retention — means we need a policy validator that loads a *different
configuration* per tenant.

**Filter the atlas**: category=governance, deployment_posture=local-first,
subcategory ∈ {guardrails, validator, policy-as-code}.

**Pick**: `guardrails-ai` (~5k★, validator-shaped, supports loading per-
tenant `Guard` packs, integrates with the gateway).

**Alternatives**:
- `nemo-guardrails` — NVIDIA's framework, more opinionated.
- `llm-guard` — heavy on PII / output sanitisation.

**PII layer**: chain `presidio` (~25k★, local-only) ahead of the model
call for healthcare / classified tenants.

---

## Step 6 — Red-team probe + regression gate

**Pattern**: [Pattern 3 — Red-team then harden](patterns/redteam-then-harden.md) plus [Pattern 1 — Eval-driven gate](patterns/eval-driven-gate.md)

**Why we need it**: the only honest answer to "is the guardrail working"
is "what happens when we attack it". Probe -> guardrail -> regress is
the loop.

**Filter the atlas**: category=redteam (probes) and category=eval
(regression), deployment_posture=local-first.

**Pick (probe)**: `garak` — NVIDIA's adversarial probe suite, fully
local, ships hundreds of attack templates.

**Pick (agent attack)**: `agentdojo` — academic agent-attack simulator.

**Pick (regression gate in CI)**: `promptfoo` — declarative test
runner, CI-friendly, supports local + remote models.

**Alternatives**: `pyrit`, `giskard`, `deepeval`, `ragas`,
`sorry-bench`, `or-bench`, `salad-bench`.

---

## Step 7 — Telemetry / audit log

**Pattern**: [Pattern 4 — Audit-log FSM escalation](patterns/audit-log-fsm-escalation.md)

**Constraint mapping**: hard constraint (c) — auditable — means an
append-only log with per-tenant retention and a way for the operator to
prove a tenant's data was deleted.

**Filter the atlas**: category=governance/routing, deployment_posture ∈
{local-only, local-first}, has `audit_log_fsm: full` or `partial` in
five-component-coverage.

**Pick**: `langfuse` (self-host mode) — OpenTelemetry-compatible,
per-trace tenant tagging, retention policy per-project.

**Alternatives surfaced by the atlas**:
- `arize-phoenix` — open-source OTEL traces.
- `opik` — Comet's open-source tracer.
- `openllmetry` — pure OTEL semantic conventions.

---

## The assembled stack

| Step | Role                           | Pick                | Posture       |
|------|--------------------------------|---------------------|---------------|
| 1    | Inference engine               | `vllm`              | local-first   |
| 2    | Gateway / router               | `litellm`           | local-first   |
| 3    | Agent / orchestrator           | `langgraph`         | local-first   |
| 4    | Structured outputs             | `instructor`        | local-first   |
| 5    | Policy validator (per-tenant)  | `guardrails-ai`     | local-first   |
| 5b   | PII layer                       | `presidio`          | local-only    |
| 6a   | Adversarial probe              | `garak`             | local-first   |
| 6b   | Agent-attack simulator         | `agentdojo`         | local-first   |
| 6c   | Regression gate (CI)           | `promptfoo`         | local-first   |
| 7    | Audit-log + traces             | `langfuse` (self-host) | local-first |

Every component is in the atlas with `deployment_posture ∈
{local-only, local-first}`. The agency can deploy the entire stack
inside its own trust boundary, swap the model behind vLLM at any time,
add an Anthropic-via-Bedrock failover for non-sensitive workloads
without rewriting the application, and produce an auditor-ready trace
for any session.

## Decision tree (when to pick what)

```
Q1. Can data leave the boundary?
    no  → drop api-only + cloud-first. Build from local-only/-first/hybrid only.
    yes → all postures available.

Q2. Will there be ≥2 tenants with different policies?
    yes → Pattern 5 (multi-tenant) — per-tenant guardrails + budgets in the gateway.
    no  → single guardrail config in the gateway is enough.

Q3. Does the agent take irreversible actions (writes, payments)?
    yes → Pattern 4 (FSM + audit + escalation) — non-negotiable.
    no  → still log every state, but escalation queue optional.

Q4. Is there a security / compliance audit ahead?
    yes → Pattern 3 (red-team→harden) before launch, not after.
    no  → still do it; "no" usually means "you don't know about it yet".

Q5. Are you a single-provider shop?
    yes → wrap it now with Pattern 2 (gateway). Cheaper than refactoring later.
    no  → Pattern 6 (provider-fallback) plus Pattern 2.

Q6. Is the eval set static?
    static → Pattern 1 (eval gate) is the only honest test.
    growing with prod failures → still Pattern 1, just with a freshness budget.
```

## Atlas filters used in this walkthrough

| What we wanted                                | Filter expression in the viewer                 |
|-----------------------------------------------|-------------------------------------------------|
| Local-possible only                            | `posture=local-only,local-first,hybrid`         |
| Inference engines                              | `category=routing` + `subcategory=inference-server` |
| Gateway / router (self-hostable)               | `posture=local-only,local-first` + chip `Routing` |
| Agent frameworks                               | chip `Agent` (filter chips in right rail)       |
| Audit-log capable governance                   | category=governance + node detail shows `audit_log_fsm` |
| Active 2025/2026 entries (avoid stale)         | tier chip `Frontier` / `Emerging`               |

## See also

- [`docs/patterns/`](patterns/README.md) — the design patterns this walkthrough applies.
- [`companion/supply_chains.yaml`](../companion/supply_chains.yaml) — pre-validated stacks (this walkthrough is a superset of `multi-tenant-gateway` + `redteam-then-harden`).
- [`docs/deployment-posture.md`](deployment-posture.md) — the methodology behind the `deployment_posture` field.
- [`docs/sovereignty-rubric.md`](sovereignty-rubric.md) — how the sovereignty score is computed.
