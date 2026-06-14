# Pattern 4 — Audit-log FSM escalation

## Problem

You're shipping an agent — something that takes actions on the user's
behalf, calls tools, or modifies state in external systems. A reviewer
(auditor, security team, the agent's eventual user) asks: "what did
the agent do, in what order, why, and who approved the irreversible
steps?". If your agent is a chain of LLM calls with no recorded state
machine, you have **no answer**. The agent's reasoning is the agent's
reasoning. The user's recourse is "trust me bro".

## Forces

| Pull                                                  | Counter-pull                                       |
|-------------------------------------------------------|----------------------------------------------------|
| Let the agent decide every step                       | Some steps must be human-approved (writes, payments) |
| Log everything                                        | Logs explode in volume; need a sane sampling story |
| One trace store                                       | Audit log and observability trace are different products |
| Hide reasoning from the user (cleaner UX)             | Reasoning IS the audit trail                       |
| Block on every uncertain step                         | Latency tanks; users quit                          |

## Shape

The agent is modelled as a finite-state machine. Every state transition
emits a structured audit-log record. States are tagged
`reversible` / `irreversible`. Transitions into `irreversible` states
that fail a confidence check are **escalated** — paused for human
review, with the FSM snapshot attached.

```
  ┌─────────────┐
  │  Planner    │──┐
  └─────────────┘   │ emits {state, action, confidence, rationale}
                    ▼
  ┌──────────────────────────────────┐
  │ Append-only audit log            │  ◀── reviewable, signed
  └──────────────────────────────────┘
                    │
       ┌────────────┴────────────┐
       │                          │
       ▼                          ▼
  ┌────────────┐         ┌────────────────────────┐
  │ Reversible │         │ Irreversible (gated)    │
  │ tool call  │         │ → confidence < θ ?      │
  └────────────┘         │   yes → escalation queue│
                         │   no  → execute         │
                         └────────────────────────┘
```

The **append-only** log is the contract with the auditor; the **gate
on irreversible actions** is the contract with the operator; the
**escalation queue** is the contract with the human reviewer.

## Realising the shape (atlas entries)

The agent runtime, the gate, and the audit log are typically three
different components. Pick one from each row.

| Role                          | Recommended            | Alternatives                          |
|-------------------------------|------------------------|---------------------------------------|
| Agent framework (FSM-shaped)  | `langgraph`            | `crewai`, `autogen`, `taskweaver`     |
| Structured / typed outputs    | `instructor`           | `outlines`, `baml`                    |
| Policy validator (gate)       | `guardrails-ai`        | `nemo-guardrails`, `llm-guard`        |
| Append-only audit log         | `langfuse`             | `arize-phoenix`, `opik`, `openllmetry`|
| Eval / red-team for the agent | `agentdojo`            | `agentbench-thudm`, `swe-bench`       |
| Recording / replay            | `inspect-evals`        | `langsmith-otel`                      |

## Anti-patterns

1. **Treating the LLM trace as the audit log** — the trace records
   model calls; the audit log records *decisions*. Different
   granularities, different retention.
2. **Mutable log** — if a row can be retroactively edited, the log is
   useless for audit.
3. **Confidence theatre** — using the LLM's self-reported confidence
   without calibration. Cross-check against an external scorer
   (judge or eval suite) before gating on it.
4. **Async escalation that nobody reads** — escalations need an SLA,
   on-call, and a metric (queue depth, time-to-review).
5. **One log per environment** — dev, staging, and prod logs that don't
   share a schema; you can't replay a prod incident in dev.
6. **No state model at all** — "the agent just runs in a loop" is the
   case this pattern exists to prevent.

## See also

- [Pattern 3 — Red-team then harden](redteam-then-harden.md) — the adversarial inputs that justify the gate.
- [Pattern 5 — Multi-tenant policy isolation](multi-tenant-policy-isolation.md) — when escalation routing depends on tenant.
- Use case: `build-an-agent` and `monitor-llm-in-prod`.
