# Worked example — the 2026-06-13 Fable / Mythos pattern fire

> On **2026-06-13** a US national-security directive recalled the two
> Anthropic frontier models **Claude Fable 5** and **Claude Mythos 5**
> from worldwide service for any deployment serving foreign nationals.
> Anthropic disabled the affected endpoints globally within hours to
> comply.
>
> This page is the worked example the atlas exists for: **which
> patterns absorbed the shock, and which patterns paged their
> operators inside the hour.**

## What broke

Any deployment whose request path baked in the model identity:

```python
# pattern that paged
from anthropic import Anthropic
client = Anthropic()
resp = client.messages.create(
    model="claude-fable-5",
    messages=[...],
    system="You are ...",
)
```

When `claude-fable-5` returned `404 model_not_found` worldwide, every
calling service threw. The blast radius was as wide as the deployment's
fan-out: agents whose tool-call loop depended on this client paged;
chatbots whose only completion call was this client served HTTP 503;
batch evaluation pipelines whose grader was this model halted mid-run.

The fault was not in the provider call — the fault was that **the model
identity was a constant in application code** instead of an input to a
routing layer.

## What survived

Any deployment whose request path routed through a thin model-agnostic
layer:

```python
# pattern that survived — routing via litellm
from litellm import completion
resp = completion(
    model=os.environ["LLM_MODEL"],   # e.g. "anthropic/claude-fable-5"
    messages=[...],
    system="You are ...",
)
```

When `claude-fable-5` went away, the operator changed the environment
variable to (for example) `anthropic/claude-opus-4-1`, `openai/gpt-5`,
or `ollama/llama-3.3-70b` and the same code path served the same
contract. **The model tier became a config string, not a constant.**

## Map to the atlas

The atlas catalogs precisely the OSS layer that made the second
pattern possible.

### Routing layer (the immediate fix)

| Atlas entry | What it does in this scenario |
|---|---|
| [`litellm`](../registry/routing/litellm.yaml) | Single SDK / proxy abstracts every provider; `model:` is a config string. |
| [`routellm`](../registry/routing/routellm.yaml) | Pre-trained routers pick the strong-vs-weak tier dynamically — if Fable was the strong tier, RouteLLM swaps it. |
| [`aisuite`](../registry/routing/aisuite.yaml) | Minimal-SDK alternative to LiteLLM with the same swap-the-model invariant. |
| [`portkey-gateway`](../registry/routing/portkey-gateway.yaml) | Production AI gateway — config-driven fallbacks, conditional routing, retries. |
| [`envoy-ai-gateway`](../registry/routing/envoy-ai-gateway.yaml) | CNCF / Kubernetes-native — same swap-the-model invariant at the cluster edge. |
| [`helicone`](../registry/routing/helicone.yaml) | Observability-first proxy — same swap surface, plus the audit-log substrate. |

### Governance layer (the regression gate)

Routing alone gets the system back online. **Governance** ensures the
swapped model still meets the application's output contract:

| Atlas entry | What it does in this scenario |
|---|---|
| [`guardrails-ai`](../registry/governance/guardrails-ai.yaml) | Output-contract enforcement — the swapped model is held to the same schema. |
| [`nemo-guardrails`](../registry/governance/nemo-guardrails.yaml) | Policy router on the input side — the swap doesn't change what's allowed in. |
| [`harmless-harnesses`](../registry/governance/harmless-harnesses.yaml) | Reference implementation covering all five components — designed against this exact failure pattern. |

### Eval layer (the proof the swap was safe)

Once the model is swapped, an eval pass on the application's contract
surface is the receipt that the swap did not regress quality:

| Atlas entry | What it does in this scenario |
|---|---|
| [`promptfoo`](../registry/eval/promptfoo.yaml) | Side-by-side `old-model vs new-model` matrix on the application's test set. |
| [`deepeval`](../registry/eval/deepeval.yaml) | Pytest-style regression suite over the contract surface. |
| [`inspect-ai`](../registry/eval/inspect-ai.yaml) | UK AISI-grade safety eval to confirm the swap didn't change safety posture. |

### Red-team layer (the proof the swap was robust)

A swap of model tier is also a potential change in adversarial
behaviour. A red-team pass catches surprises before they ship:

| Atlas entry | What it does in this scenario |
|---|---|
| [`pyrit`](../registry/redteam/pyrit.yaml) | Microsoft AI Red Team's framework — re-run multi-turn attacks against the new tier. |
| [`garak`](../registry/redteam/garak.yaml) | Probe battery — quick "nmap-style" baseline. |
| [`agentdojo`](../registry/redteam/agentdojo.yaml) | Agent-security benchmark — if the system is agentic, re-run injection scenarios. |

## What this is not

This worked example is **not anti-Anthropic** and **not anti-US**. Many
of the projects above (PyRIT, garak, litellm, deepeval, promptfoo,
helm, lm-evaluation-harness, inspect-ai, openai-evals) originated in
US-incorporated companies or US / UK academic institutions. The atlas
includes them on technical merit.

The point is structural: **the model tier is a sovereignty surface**,
and the OSS catalogued here is the layer that makes that surface
manageable. The 2026-06-13 event was the moment the field saw this with
unusual clarity. There will be others.

For the broader framing — including the
Indigenous-data-governance positioning (CARE, Maiam nayri Wingara,
IEEE 2890-2025) that motivates the "sovereign" framing in
[`CHARTER.md`](../CHARTER.md) — see *The Harness Paradigm*
(Kereopa-Yorke, 2026, in `sa-sovereign-llm-harness`).

## What you can do today

If your deployment looks like the first code block above:

1. Add a routing layer (start with `litellm` — one-line install,
   one-line client change).
2. Move the model identity into config, not code.
3. Add an eval pass over your contract surface so the next swap is a
   receipt, not a leap of faith.
4. Add a red-team pass for the same reason.

The atlas exists so step 1 is a 30-second decision and the remaining
steps are 30-minute decisions. That is what "sovereign by construction"
looks like in practice.
