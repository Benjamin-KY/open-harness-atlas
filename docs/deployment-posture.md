# Deployment posture

> "Where does it run?" is the question this dimension answers.

Every entry in the registry has a `deployment_posture` field with one of five values. The dimension exists to make a single question first-class: **if I install this today, can I run it locally, or am I tied to someone else's infrastructure?**

| Posture | Means | Litmus test |
|---|---|---|
| `local-only` | Air-gappable. No network egress required after install. | Does it run with the network cable unplugged? |
| `local-first` | Self-host is the documented default. Cloud is optional. | Does `docker compose up` or `pip install && python -m` work without a SaaS account? |
| `hybrid` | **Requires both** local and cloud at runtime, by design. | Does it call a third-party API as part of its normal flow (e.g. local classifier → cloud generator)? |
| `cloud-first` | SaaS is the primary path. Self-host docs are thin or labelled-advanced. | Is the "Getting Started" page a SaaS sign-up? |
| `api-only` | No local path exists. | If the third-party API goes down, is the project unusable? |

## Why this dimension exists

The Atlas was built in response to the **closed-garden trend** — managed-only AI infrastructure where the "open source" label conceals a SaaS-only path. The model-agnostic score (`mas`) already captures provider-portability, but a project can score MAS 5 (works with any model) and still be `cloud-first` (only runs on their managed platform).

`deployment_posture` is the orthogonal axis: **provider-portability × infrastructure-portability**. The two together describe the actual sovereignty story.

## How it's computed

1. **Heuristic baseline** (`scripts/compute_deployment_posture.py`) — regex over `description + sovereignty_notes + tagline + tags`. Looks for:
   - `air-gap`, `offline`, `self-contained` → `local-only`
   - `docker compose`, `helm`, `ollama`, `local model` → `local-first`
   - "managed service", "SaaS", "sign up at" → `cloud-first`
   - "API key", explicit "no local path" → `api-only`
   - Containerization alone is **not** a hybrid signal (it's table-stakes for almost everything in the registry)
2. **3-model ensemble curation** for low-confidence cases (heuristic confidence < 0.7).
   - 447 entries went through three independent reviewers: `claude-sonnet-4.5`, `claude-opus-4.7-xhigh`, `gpt-5.4`.
   - Each reviewer read the YAML + (where available) the project README and emitted a `{posture, confidence, rationale}` JSON.
   - Consensus rule: **3/3 same** = strong (applied), **2/3 same** = majority (applied), **3 distinct** = split (heuristic kept, `needs_human_review: true`).
3. **Tie-breaker policy** when reviewers were ambiguous: lean toward the **less optimistic** value. A project sitting between `local-first` and `cloud-first` with no clear self-host story is `cloud-first`. This keeps the dimension honest — sovereignty claims need evidence, not benefit-of-the-doubt.

## Distribution

Current registry (860 entries, 2026-06-15 v0.4.3):

| Posture | Count | % |
|---|---:|---:|
| `local-first` | 630 | 73% |
| `local-only` | 140 | 16% |
| `cloud-first` | 37 | 4% |
| `hybrid` | 33 | 4% |
| `api-only` | 20 | 2% |

Exact counts vary as the registry grows; the live values are in `visuals/graph-data.json` under `meta.deployment_posture`.

## How to use the dimension

### In the 3D / 2D viewer
- The **Deployment posture** panel in the right rail lists all five postures with counts. Click any row to hide that posture.
- The **Local-possible only** quick chip filters to `local-only + local-first + hybrid` — i.e. anything you can realistically self-host (even if cloud is in the loop somewhere).
- The per-node detail panel shows the posture as a coloured pill alongside the category, tier and license pills.

### In your own code
```python
import yaml, pathlib
local = [
    y for p in pathlib.Path("registry").glob("*.yaml")
    if (y := yaml.safe_load(p.read_text(encoding="utf-8")))
    and y.get("deployment_posture") in ("local-only", "local-first")
]
```

### As a curator
- An entry with `needs_human_review: true` in `registry/_metadata/_deployment.json` had a three-way reviewer split — it's the highest-value entry to inspect and correct.
- To override a posture, edit the YAML directly: `deployment_posture: local-first`. The next `compute_deployment_posture.py` run will respect explicit overrides if you also add a sentence to `sovereignty_notes` (and remove the `auto-ingested` boilerplate).

## Relationship to other dimensions

| Dimension | What it measures | Why posture is different |
|---|---|---|
| `model_agnostic_score` (MAS) | Can I swap the underlying LLM provider? | Posture asks the **infrastructure** question: where does the harness itself live, regardless of which model it talks to. |
| `tier` (adoption) | How mature / widely-adopted? | Posture is independent of adoption — a 50k-star project can still be `api-only` (e.g. a CLI wrapper around a closed API) and a 50-star project can be `local-only`. |
| `category` (governance/agent/eval/redteam/routing/education) | What does it do? | Posture is a cross-cutting concern; every category contains all five postures. |
| `maturity` | Release stage? | Posture is about runtime, not lifecycle. |

## Caveats

- **Heuristic baseline is intentionally conservative.** When in doubt, the classifier picked `local-first` (the modal posture). The ensemble corrected 142 entries (32% of the 447 reviewed) where the heuristic was wrong.
- **Posture can change over time.** A project that ships a managed-cloud edition later may drift from `local-first` to `cloud-first`. Periodic re-curation is required.
- **"Local" includes "on a server you control."** A model that requires a 96-GB H200 to run is technically `local-only` even though most readers can't actually run it on a laptop. The dimension is about *who owns the infrastructure*, not *how big it is*.
- **`hybrid` is rare** (≈9% of entries) because it has a specific meaning: both local **and** cloud are required at runtime by design. A project where cloud is optional is `local-first`, not `hybrid`.

## Source

- Schema: `registry/_schema.yaml` → `deployment_posture` enum
- Heuristic classifier: `scripts/compute_deployment_posture.py`
- Per-entry record: `registry/_metadata/_deployment.json`
- Live counts: `visuals/graph-data.json` → `meta.deployment_posture`
- Ensemble run notes: `docs/CURATION_BACKLOG.md`
