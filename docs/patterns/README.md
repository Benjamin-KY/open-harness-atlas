# Harness design patterns

A small set of named, reusable shapes for assembling open-source AI
harnesses out of the entries in this atlas. Each pattern is **harness
design**, not implementation — what to stand up, in what order, and what
to wire to what — using the registry as the parts bin.

## Why patterns

The atlas tells you which 793 entries exist. The patterns tell you which
4–7 of them to wire together for a given workload. A pattern is short,
opinionated, and biased toward **model-agnostic, deployment-aware**
choices: every step lists realistic alternatives so you can drop in the
inference engine, gateway, or eval framework that matches your sovereignty
and latency posture.

## How patterns relate to other surfaces

| Surface                                   | What it is                                              | What it isn't                                        |
|-------------------------------------------|---------------------------------------------------------|-------------------------------------------------------|
| `companion/use_cases.yaml`                | Entry-point overlay: "I need to do X, show me harnesses" | Wiring instructions                                  |
| `companion/supply_chains.yaml`            | A concrete, validated stack (specific entries by id)    | Tradeoff discussion                                   |
| **This folder (`docs/patterns/`)**        | **Reusable shapes + forces + alternatives + anti-patterns** | A specific deployment                                 |
| [`docs/worked-example-model-agnostic-stack.md`](../worked-example-model-agnostic-stack.md) | Step-by-step walkthrough applying patterns to a real scenario | A generic shape                                      |

## The 7 patterns

| # | Pattern                                                               | Problem it solves                                                                 |
|---|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 1 | [Eval-driven gate](eval-driven-gate.md)                               | Treat releases like code: regression-gate every model/prompt change before merge. |
| 2 | [Sovereignty-preserving routing](sovereignty-preserving-routing.md)   | Keep the gateway in front of providers; tenants and policies stay portable.       |
| 3 | [Red-team then harden](redteam-then-harden.md)                        | Find unsafe outputs first, then close them — adversarial probe → guardrail loop.  |
| 4 | [Audit-log FSM escalation](audit-log-fsm-escalation.md)                | Reviewable agent: every state change recorded; agent can request human review.    |
| 5 | [Multi-tenant policy isolation](multi-tenant-policy-isolation.md)     | One platform, many policies — per-tenant guardrails, budgets, and traces.         |
| 6 | [Provider fallback chain](provider-fallback-chain.md)                  | Don't go down when one provider does — automatic failover with cost ceilings.     |
| 7 | [Local-possible spine](local-possible-spine.md)                        | Build the **whole** stack from `deployment_posture ∈ {local-only, local-first}`.  |

## Pattern template

Each pattern follows this skeleton so they're trivial to scan:

```text
# Name

## Problem
The user-visible failure if you don't do this.

## Forces
The things that pull a design in opposite directions
(latency vs cost, sovereignty vs reach, etc.).

## Shape
The minimum sequence — components by role, not by name.

## Realising the shape (atlas entries)
For each role, a 1-pick recommendation + 2-3 drop-in alternatives,
linked to registry entries. Filterable in the live viewer.

## Anti-patterns
Common ways this design quietly fails.

## See also
Related patterns, supply chains, use cases.
```

## Pattern → supply chain map

The shipped `companion/supply_chains.yaml` already includes 6 of these
patterns as named, validated stacks. Patterns 1, 3, 4, and 5 map directly:

| Pattern                                  | Supply chain (companion) |
|------------------------------------------|---------------------------|
| Eval-driven gate                         | `eval-driven-development` |
| Red-team then harden                     | `redteam-then-harden`     |
| Multi-tenant policy isolation            | `multi-tenant-gateway`    |
| Audit-log FSM escalation                 | (new chain candidate)     |
| Sovereignty-preserving routing           | (subset of `multi-tenant-gateway`) |
| Provider fallback chain                  | (subset of `serve-and-ship-agent`) |
| Local-possible spine                     | (new chain candidate)     |

Patterns 4 and 7 are tracked as candidate supply chains for a follow-up
release.

## Contributing patterns

If you've shipped a harness shape that doesn't fit one of the seven
above, open a PR:

1. Copy `_TEMPLATE.md` (use the skeleton above; live one TBD).
2. Cite at least 4 registry entries by id.
3. Name the failure mode the pattern prevents.
4. Add the new pattern to the table above.

Patterns are curated — they should reflect designs people are actually
running in production, not aspirational architectures.
