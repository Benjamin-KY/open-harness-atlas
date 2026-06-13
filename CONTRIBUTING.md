# Contributing to `open-harness-atlas`

Thanks for considering a contribution. This atlas is **hand-curated**, so
inclusion is an editorial decision — but the schema is open, the
process is transparent, and the bar is low for adding a well-formed entry
for a project that fits the [scope](#what-counts-as-a-harness).

---

## What counts as a harness?

See [`GOVERNANCE.md`](GOVERNANCE.md) for the full policy. In short, the
medium-scope cut covers six categories:

1. **Governance harnesses** — frameworks that enforce output contracts,
   citation discipline, refusal calibration, or audit trails on LLM
   responses (e.g., Guardrails AI, NeMo Guardrails, Llama Guard 3).
2. **Agent frameworks** — runtimes for tool-using, multi-turn agents
   (e.g., PydanticAI, LangGraph, CrewAI).
3. **Eval harnesses** — runners that measure model or system behaviour
   against task suites (e.g., `lm-evaluation-harness`, HELM, promptfoo,
   UK AISI `inspect`).
4. **Red-team / safety harnesses** — adversarial probes and
   attack-class coverage tools (e.g., PyRIT, garak, AgentDojo).
5. **Routing / model-agnostic infrastructure** — proxies and gateways
   that let one application target many providers (e.g., LiteLLM,
   RouteLLM, Aisuite).
6. **Free education resources** — courses, tutorials, cookbooks at
   zero monetary cost (e.g., DeepLearning.AI shorts, Hugging Face
   Agents course, Karpathy nano-series).

Out-of-scope categories — pure RAG cores (LlamaIndex, Haystack) and
observability stacks (Langfuse, Phoenix/Arize) — are not catalogued as
registry entries; they are cross-linked in
[`docs/adjacencies.md`](docs/adjacencies.md).

---

## Quick path — adding an entry

1. **Pick the category folder.** One of
   `registry/{governance,agent,eval,redteam,routing,education}/`.
2. **Copy the template:**
   ```powershell
   Copy-Item registry\_TEMPLATE.yaml registry\<category>\<my-entry>.yaml
   ```
3. **Fill the required fields.** See
   [`registry/_schema.yaml`](registry/_schema.yaml) for the full schema
   and field descriptions.
4. **Validate locally:**
   ```powershell
   python scripts\validate_registry.py
   python -m pytest -q
   ```
5. **Open a PR** using the *Add entry* issue template — the maintainer
   reviews against `GOVERNANCE.md`, runs CI (schema, uniqueness, links),
   and either merges, requests changes, or explains a rejection.

You do not need to run the metadata refresh or generate matrices — both
happen automatically on merge and on a weekly schedule.

---

## What good looks like

A model entry — `registry/routing/litellm.yaml`:

```yaml
id: litellm
name: LiteLLM
category: routing
subcategory: provider-gateway
repo_url: https://github.com/BerriAI/litellm
homepage: https://www.litellm.ai/
license: MIT
primary_language: Python
tagline: Call 100+ LLM APIs in the OpenAI format.
description: |
  LiteLLM is a unified SDK and proxy that normalises calls to most major
  LLM providers (OpenAI, Anthropic, Google, Cohere, Hugging Face, local
  Ollama / vLLM / llama.cpp, etc.) into a single OpenAI-compatible
  interface, with token-budget, retry, fallback, and cost-tracking
  primitives built in.

  In the context of this atlas, LiteLLM is the canonical example of a
  *routing harness*: it does not constrain model output, but it makes
  the model tier itself swappable, which is the necessary precondition
  for every other harness category to be sovereign-by-construction.
maturity: ga
maintainer:
  type: company
  name: BerriAI
origin_country: US
model_agnostic_score: 5
five_component_coverage:
  policy_router: none
  source_authority: none
  prompt_composer: none
  output_contract: none
  audit_log_fsm: partial
education_resources:
  - title: LiteLLM Docs
    url: https://docs.litellm.ai/
    type: docs
    free: true
sovereignty_notes: |
  US-incorporated company; OSS core is MIT-licensed and self-hostable
  (Docker, K8s); supports any OpenAI-compatible local backend including
  Ollama, vLLM, llama.cpp — meaning the swap target can be a fully local
  model with no outbound API call.
harness_paradigm_alignment: partial
adjacent_to:
  - routellm
  - aisuite
```

---

## What a rejected entry looks like

Common reasons we will ask you to change or withdraw a PR:

| Reason | Fix |
|---|---|
| Project is not under an OSI-approved licence | Withdraw or fix at the source project. |
| Project is archived for 12+ months with no fork | Either point at an active fork (`repo_url`) or withdraw. |
| Description is marketing copy or vendor-cheerleading | Rewrite to neutral, citation-style prose per [`BRAND.md`](BRAND.md). |
| `model_agnostic_score` not justified in `sovereignty_notes` | Add 1–3 sentences explaining the score. |
| `five_component_coverage` mis-scored (e.g., marketing claim ≠ implementation) | Adjust to the [scoring rubric](docs/sovereignty-rubric.md). |
| Entry duplicates an existing one (e.g., same project under different name) | Update the existing entry instead. |
| Education entry costs money | Cannot be catalogued in `registry/education/`. Link from a different entry's `education_resources:` if relevant. |

---

## Auto-refreshed fields — do NOT hand-edit

`registry/_metadata/<id>.json` files are refreshed weekly by
`scripts/refresh_metadata.py` running in CI. They contain:

- `stars`
- `last_commit_at`
- `latest_release`
- `license_spdx` (cross-checked against the entry's declared `license`)
- `archived`
- `default_branch`
- `refreshed_at`

If your PR modifies a `_metadata/` file, CI will flag it. The metadata
sidecar is owned by the bot, not by humans.

---

## Updating an existing entry

For corrections (tagline rewording, scoring adjustment, sovereignty notes
update), open a PR using the *Update entry* issue template. The bar is
the same as adding a new entry: schema validation passes, prose is
neutral, scores are justified.

For status changes (project archived, licence change, fork preferred),
the weekly refresh bot will flag most of these automatically.

---

## Visuals and matrices

You typically do not need to touch these by hand — they regenerate from
the registry via `make build`. If you do want to rework a hand-authored
visual (`visuals/taxonomy.svg`, `visuals/five-component-overlay.svg`,
`visuals/fable-mythos-pattern-fire.svg`), follow `BRAND.md` and place
source files under `visuals/source/`.

---

## Code contributions

Scripts under `scripts/` are Apache-2.0. Run `ruff` and the test suite
before opening a PR:

```powershell
ruff check scripts tests
python -m pytest -q
```

CI runs the same gates.

---

## Communication

- **Bug or scoping question** → open a GitHub issue.
- **Adding many entries / proposing a new category** → open a discussion
  first to align on scope, then a PR.
- **Sensitive disclosure (e.g., licence misrepresentation)** → email the
  maintainer rather than opening a public issue.

---

## License of contributions

By submitting a PR you agree your contribution is licensed under the
repository's dual scheme: **Apache-2.0** for code, **CC BY-SA 4.0** for
catalog content and visuals. See [`LICENSE`](LICENSE) and
[`LICENSE-DOCS`](LICENSE-DOCS).
