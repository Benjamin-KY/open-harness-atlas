# Pattern 1 — Eval-driven gate

## Problem

You ship a new prompt, a new system message, or swap to a new model —
and something subtly regresses. Not a crash; the answer is just *slightly
worse* on the cases your customers actually care about. The regression
makes it through CI because there are no tests for "quality of LLM output".
You only learn about it from a support ticket.

## Forces

| Pull                                | Counter-pull                                        |
|-------------------------------------|-----------------------------------------------------|
| Move fast, ship prompt changes daily | Quality regressions in LLM outputs are invisible without a baseline |
| Public benchmarks (MMLU, HumanEval) generalise | Public benchmarks don't cover your domain         |
| LLM-as-judge is cheap               | LLM-as-judge introduces its own bias; needs calibration |
| Run the full eval suite on every PR | Eval costs (compute + provider API spend) add up   |

## Shape

Five components, one of them mandatory in CI:

```
   ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
   │ Baseline     │──▶│ Custom domain    │──▶│ Regression    │
   │ benchmark    │    │ eval suite       │    │ gate (CI)    │
   └──────────────┘    └──────────────────┘    └──────┬───────┘
                                                       │
                                                       ▼
                          ┌────────────────────────────────────────┐
                          │ Trace + score store (prod observability)│
                          └────────────────────────────────────────┘
                                                       ▲
                                                       │
                              ┌────────────────────────┴────────────┐
                              │  Production traffic                 │
                              └─────────────────────────────────────┘
```

The hard requirement is step 3 — **regression gate in CI** — that **blocks
merge on quality drop**. The trace store closes the loop so prod
observations feed back into the suite as the eval set grows.

## Realising the shape (atlas entries)

| Role                       | Recommended            | Alternatives                                        |
|----------------------------|------------------------|----------------------------------------------------|
| Baseline benchmark         | `lm-evaluation-harness` | `opencompass`, `helmet`, `livebench`               |
| Custom domain eval suite   | `deepeval`              | `ragas` (if RAG-shaped), `promptfoo`               |
| Regression gate (CI)       | `promptfoo`             | `deepeval`, custom pytest harness                  |
| Trace + score store        | `langfuse`              | `arize-phoenix`, `opik`, `openllmetry`             |
| Adversarial regression     | `garak`                 | `pyrit`, `giskard`                                 |

Filter the live atlas to this shape:

- 3D: <https://benjamin-ky.github.io/open-harness-atlas/#chain=eval-driven-development>
- 2D: <https://benjamin-ky.github.io/open-harness-atlas/2d.html#chain=eval-driven-development>

## Anti-patterns

1. **"We'll eval after launch"** — by the time you have eval coverage you
   have a year of un-tested prompt mutations to back-test.
2. **MMLU-only score** — chasing a single public-benchmark number while
   your domain quality slips. Public benchmarks are necessary, not
   sufficient.
3. **Judge model = candidate model** — never grade with the model you're
   trying to evaluate; use a separate, ideally stronger, judge.
4. **Eval set frozen at v0** — the eval set must grow with prod failures
   captured by the trace store. Otherwise you measure ever-more-distant
   things.
5. **No cost ceiling on the gate** — an unbudgeted eval run blocks
   shipping (and burns the API budget) when the API provider has an
   outage. Cap parallelism and total spend per CI job.

## See also

- [Pattern 3 — Red-team then harden](redteam-then-harden.md) — the adversarial half of "eval everything before merge".
- [Pattern 6 — Provider fallback chain](provider-fallback-chain.md) — eval-gated rollouts are cheaper when you can hot-swap providers.
- Supply chain: `eval-driven-development` (`companion/supply_chains.yaml`).
- Use case: `evaluate-llm`.
