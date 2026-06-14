# Pattern 3 — Red-team then harden

## Problem

Your LLM-backed feature is going to be attacked. Not maybe — definitely.
Prompt injection, jailbreaks, tool misuse, multi-turn coercion, training-
data extraction. If you stand up a guardrail layer **before** you've
attacked your own system, the guardrails defend against the threats you
imagined, not the ones that exist. If you red-team **without** a
guardrail loop, every finding is a one-shot fix that the next attacker
trivially routes around.

## Forces

| Pull                                          | Counter-pull                                       |
|-----------------------------------------------|----------------------------------------------------|
| Ship the feature, attack it later             | Public incident teaches the threat model the hard way |
| Buy a hosted "AI security" service            | Closed-box guardrails are themselves a black box   |
| One-shot security review                      | LLM behaviour drifts; one-shot review goes stale within weeks |
| Block on every flagged output                 | Refusal regressions are also a user-experience harm |

## Shape

A loop, not a checklist. Four components, run in CI on every prompt /
model change:

```
  ┌──────────────────┐     ┌──────────────────┐    ┌────────────────────┐
  │ 1. Adversarial    │ ──▶│ 2. Schema-validated│──▶│ 3. Policy validator │
  │    probe suite    │    │    output (structured)│   │    (guardrails)    │
  └──────────────────┘     └──────────────────┘    └──────────┬──────────┘
            ▲                                                  │
            │                                                  ▼
            │                                       ┌────────────────────┐
            └───────────────────────────────────────│ 4. Re-probe in CI  │
                                                    │    (fail on regress) │
                                                    └────────────────────┘
```

The output of step 1 (the failing probes) becomes the input of step 4
(the regression set). The loop closes when a probe that once succeeded
is now caught by step 3.

## Realising the shape (atlas entries)

| Role                          | Recommended           | Alternatives                                |
|-------------------------------|-----------------------|---------------------------------------------|
| Adversarial probe suite       | `garak`               | `pyrit`, `giskard`, `promptmap`             |
| Agentic-attack simulator      | `agentdojo`           | `llm-attacks`, `rebuff`                     |
| Schema-validated output       | `instructor`          | `outlines`, `baml`, `jsonformer`            |
| Policy validator              | `guardrails-ai`       | `nemo-guardrails`, `llm-guard`, `lakera`    |
| Regression gate (CI)          | `promptfoo`           | `deepeval`                                  |
| Prompt-injection eval         | `sorry-bench`         | `or-bench`, `salad-bench`                   |

Filter the live atlas to this shape:

- 3D: <https://benjamin-ky.github.io/open-harness-atlas/#chain=redteam-then-harden>
- 2D: <https://benjamin-ky.github.io/open-harness-atlas/2d.html#chain=redteam-then-harden>

## Anti-patterns

1. **Probe once, ship, never re-probe** — the probe set decays in
   relevance the moment the model or prompt changes.
2. **Guardrail layer that only matches keywords** — adversarial inputs
   are written to evade keyword filters by construction.
3. **"We use $vendor for safety"** — vendor classifiers can fail; you
   still need a regression suite that catches your own domain failures.
4. **Over-blocking** — a guardrail that refuses every borderline prompt
   teaches users to phrase around it. Track refusal rate as a quality
   metric, not just attack success rate.
5. **No human-in-the-loop on the worst cases** — automated guard +
   adversarial probe is necessary but not sufficient; route the
   highest-severity cases to a reviewer (see [Pattern 4](audit-log-fsm-escalation.md)).
6. **Conflating eval and red-team** — eval is "is the answer good?";
   red-team is "can the answer be made unsafe?". Different suites,
   different metrics, often different toolchains.

## See also

- [Pattern 1 — Eval-driven gate](eval-driven-gate.md) — same CI discipline, applied to quality.
- [Pattern 4 — Audit-log FSM escalation](audit-log-fsm-escalation.md) — the human-review fallback this pattern leans on.
- Supply chain: `redteam-then-harden`.
- Use case: `redteam-ai-system`.
