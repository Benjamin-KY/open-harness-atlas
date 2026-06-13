# open-harness-atlas

### **The OSS layer that makes model-agnostic AI workloads possible.**

*A curated, jurisdiction-neutral catalog and knowledge graph of free,
open-source harnesses — governance, agent, evaluation, red-team,
routing — and free education resources.*

[![License: Apache 2.0](https://img.shields.io/badge/code-Apache--2.0-blue?style=flat-square)](LICENSE)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/content-CC%20BY--SA%204.0-d68910?style=flat-square)](LICENSE-DOCS)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square)](pyproject.toml)

> ⚠ **Pre-release (v0.1.0-dev).** Registry seeded with **44 entries**
> across six categories. Schema, governance policy, charter, and the
> two front-door visuals are stable. The first tagged release
> (**v0.1.0**) is the current state; v0.2.0+ adds the data-driven
> spectrum / radial visuals and adjacencies page (see `CHANGELOG.md`).
>
> **Deferred from v0.1.0** (deliberate, with reasons recorded):
> Llama Guard 3 and ShieldGemma (non-OSI licenses fail
> `GOVERNANCE.md` §1.1); `sa-sovereign-llm-harness` (upstream has no
> `LICENSE` file yet — entry lands once that ships); DeepLearning.AI
> shorts (no underlying OSS repo).

---

## Why this exists

The **2026-06-13 Fable / Mythos export-control recall** removed two
frontier Anthropic models from worldwide access in hours under a US
national-security directive. Every deployment whose only model tier was
`claude-fable-5` or `claude-mythos-5` paged its operators inside the
hour. Every deployment that treated the model as a swappable backend
behind a harness ran a config edit and kept serving.

This atlas catalogues the OSS layer of that second pattern. Read
[`CHARTER.md`](CHARTER.md) for the full motivating context (the
broader closed-garden trend, the Indigenous-data-governance framing, and
why "jurisdiction-neutral" is a design commitment, not a slogan).

---

## How harnesses are the foundation for model-agnostic workloads

![Six-category taxonomy](visuals/taxonomy.svg)

A **harness** is the structural scaffolding *around* the model that
makes the model itself swappable. In the [Harmless Harnesses][hh] spec,
a harness has five components, each enforcing one invariant:

| # | Component | Invariant |
|---|---|---|
| 1 | **Policy Router** | Every request is classified into a known route before the model is called. |
| 2 | **Source Authority** | Every claim cites an allow-listed source; the knowledge base is truth. |
| 3 | **Prompt Composer** | The governance-prompt template is the only system-role surface. |
| 4 | **Output Contract** | Malformed or out-of-policy output is non-shippable. |
| 5 | **Audit Log + FSM Escalation** | Refusal and escalation are deterministic, not stochastic. |

When these five hold, **the model is one input among many** — and you
can swap it. The atlas catalogues which OSS projects implement which
components, side by side:

![Which OSS governance harnesses cover which Harmless Harnesses components](visuals/five-component-overlay.svg)

The atlas exists to make the *open* components of this pattern
(governance harnesses, agent frameworks, eval harnesses, red-team
harnesses, routing infrastructure, free education) findable and
comparable.

[hh]: https://github.com/Benjamin-KY/Harmless-Harnesses

---

## The six categories (launch scope)

| Category | What's catalogued | Launch entries |
|---|---|---|
| 🛡  **Governance harnesses** | Output-contract / citation / refusal / audit frameworks | 6 |
| 🤖 **Agent frameworks** | Tool-using multi-turn agent runtimes | 10 |
| 📏 **Eval harnesses** | Behaviour measurement runners | 8 |
| 🎯 **Red-team / safety harnesses** | Adversarial probes & attack-class coverage | 6 |
| 🔀 **Routing / model-agnostic infra** | Provider gateways & swappable backends | 6 |
| 🎓 **Free education** | Courses · tutorials · cookbooks at zero cost | 8 |
| | **Total** | **44** |

**Out-of-scope by design** (linked as adjacencies, not catalog entries):
pure RAG cores · observability stacks · vector databases as
infrastructure. See [`GOVERNANCE.md`](GOVERNANCE.md) §8.

---

## Use this atlas

**Browse** (no tooling required — works on GitHub from anywhere):

- Start with [`CHARTER.md`](CHARTER.md) for context.
- Open [`docs/taxonomy.md`](docs/taxonomy.md) for the 6-category map.
- Open [`docs/sovereignty-rubric.md`](docs/sovereignty-rubric.md) for
  the scoring methodology.
- Open the comparison matrices: [`docs/governance-matrix.md`](docs/governance-matrix.md),
  [`docs/agent-matrix.md`](docs/agent-matrix.md), and the four others
  under [`docs/`](docs/).
- Came here from the Fable / Mythos news? Jump to
  [`docs/fable-mythos-pattern-fire.md`](docs/fable-mythos-pattern-fire.md).

**Contribute** an entry:

```powershell
git clone https://github.com/Benjamin-KY/open-harness-atlas
cd open-harness-atlas
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item registry\_TEMPLATE.yaml registry\<category>\<my-entry>.yaml
# edit, then:
python scripts\validate_registry.py
python -m pytest -q
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full PR flow and the
inclusion rubric in [`GOVERNANCE.md`](GOVERNANCE.md).

**Run the interactive companion** (optional — requires Docker + Neo4j):

```powershell
make neo4j-local        # launches Neo4j 5 on bolt://localhost:7687
make companion          # emits companion/domain/open-harnesses.yaml
cd companion ; create-context-graph ./app --domain ./domain/open-harnesses.yaml --framework pydanticai --demo-data
```

The companion is a [`create-context-graph`][ccg]-generated FastAPI + Next.js
app with NVL graph visualization, backed by Neo4j, queryable via the
PydanticAI agent. The fixtures are derived from this repo's registry —
*not* LLM-fabricated. See [`companion/README.md`](companion/README.md).

[ccg]: https://github.com/Benjamin-KY/create-context-graph

---

## Repository map

```
open-harness-atlas/
├── CHARTER.md                 # Why this exists — Fable/Mythos, closed-garden, IDSov framing
├── CONTRIBUTING.md            # How to add an entry
├── GOVERNANCE.md              # Inclusion / scoring / removal policy
├── BRAND.md                   # Palette, typography, diagram conventions (mirrors harmless-harnesses)
├── CITATION.cff               # Academic citation metadata
├── CHANGELOG.md               # Per-release changes
├── registry/                  # SINGLE SOURCE OF TRUTH — one YAML per entry
│   ├── _schema.yaml           # JSON schema for entry validation
│   ├── _TEMPLATE.yaml         # Copy this to add a new entry
│   ├── _metadata/             # Auto-refreshed JSON sidecars (bot-owned, do not hand-edit)
│   ├── governance/            # Governance harnesses
│   ├── agent/                 # Agent frameworks
│   ├── eval/                  # Eval harnesses
│   ├── redteam/               # Red-team / safety harnesses
│   ├── routing/               # Routing / model-agnostic infra
│   └── education/             # Free education resources
├── docs/                      # Taxonomy, matrices, rubrics, worked examples
├── visuals/                   # Canonical SVGs (taxonomy, overlay, spectrum, radial, worked example)
├── scripts/                   # Validate / refresh / build (Python 3.11+)
├── companion/                 # Optional create-context-graph companion app
├── tests/                     # pytest — hermetic by default
└── .github/                   # Workflows + issue templates
```

---

## Verification

Every PR must pass:

```powershell
python -m pytest -q                # schema · uniqueness · matrices consistency · visuals build
python scripts\validate_registry.py
ruff check scripts tests
```

The weekly `refresh-metadata.yml` action pulls fresh GitHub metadata
into `registry/_metadata/<id>.json` and opens a PR with the diff. The
hermetic test suite never reaches the network; the optional link-check
runs on a separate weekly schedule.

---

## Where this atlas fits

| | This atlas | [Harmless Harnesses][hh] | [sa-sovereign-llm-harness][sa] |
|---|---|---|---|
| **Role** | Catalog the OSS layer | Teach how to build a harness | Research-grade prototype + evidence |
| **Voice** | Field guide. Neutral. Citation-heavy. | Pedagogical. Practitioner. | Research. IMRAD. Primary-source-grounded. |
| **Updates** | Continuous (weekly metadata refresh) | Tagged releases | Tagged releases |
| **You exit here to…** | The course (to learn how to build) · the research repo (for primary evidence) | The atlas (to find an OSS implementation) | The atlas (for adjacent tooling) |

Strict separation of concerns — no duplication. Cross-links land at
v1.0.0.

[sa]: https://github.com/Benjamin-KY/sa-sovereign-llm-harness

---

## License

Dual-licensed:

- **Code** (`scripts/`, `tests/`, `*.py`) — **Apache-2.0**. See
  [`LICENSE`](LICENSE).
- **Catalog content & visuals** (`registry/`, `docs/`, `visuals/`,
  top-level Markdown) — **CC BY-SA 4.0**. See [`LICENSE-DOCS`](LICENSE-DOCS).

---

## Citation

```
Kereopa-Yorke, B. (2026). open-harness-atlas: a jurisdiction-neutral
catalog and knowledge graph of free, open-source harnesses for
model-agnostic AI workloads. https://github.com/Benjamin-KY/open-harness-atlas
```

Machine-readable metadata in [`CITATION.cff`](CITATION.cff).

---

<div align="center">
  <sub>
    Also known as / search terms:
    OSS LLM harness catalog · open-source AI safety frameworks ·
    model-agnostic AI infrastructure · sovereign AI tooling ·
    awesome harnesses · LLM governance frameworks · agent framework
    comparison · LLM eval harness directory · LLM red-team tooling ·
    AI model routing.
  </sub>
</div>
