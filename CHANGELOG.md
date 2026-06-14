# Changelog

All notable changes to **open-harness-atlas** are documented here. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [SemVer](https://semver.org/).

## [Unreleased]

### Added — Harness design patterns + worked-example walkthrough (2026-06-14)

- **`docs/patterns/`** — seven named, reusable harness design patterns.
  Each follows the same skeleton (problem · forces · shape · realising
  the shape with atlas entries · anti-patterns · see also) so they're
  trivial to scan:
    1. **Eval-driven gate** — regression-gate every model / prompt
       change in CI before merge.
    2. **Sovereignty-preserving routing** — gateway-first design so the
       provider becomes a config concern, not a code concern.
    3. **Red-team then harden** — probe → schema → guard → re-probe
       loop; close the loop on adversarial findings.
    4. **Audit-log FSM escalation** — agent as finite-state machine with
       append-only audit log and human-review queue on irreversible
       actions.
    5. **Multi-tenant policy isolation** — one platform, N tenants,
       per-tenant policy packs in the gateway.
    6. **Provider fallback chain** — ordered failover with per-step
       budget and a terminal safe default.
    7. **Local-possible spine** — assemble the entire stack from
       `deployment_posture ∈ {local-only, local-first, hybrid}` entries
       (92.8% of the atlas).
- **`docs/worked-example-model-agnostic-stack.md`** — long-form
  walkthrough that takes a real scenario (Australian government
  agency: data residency, multi-team, auditable, multi-provider
  resilient) and assembles a 10-component stack from the atlas step
  by step, citing the design pattern, the posture filter, and the
  picks at each layer. Includes a 6-question decision tree.
- README updated to link both the patterns folder and the worked
  example from the "Browse" section.

### Added — Discovery sweep infrastructure (2026-06-14)

- **`scripts/discovery/search_recent.py`** — recency-biased GitHub
  search (`--created>=YYYY-MM-DD`, default 2024-06-01) over 33
  free-text queries spanning all six categories. Closes the
  "18-24mo recency gap" surfaced by the Phase 4 curation-coverage
  swarm agent. First run produced 289 unique candidates.
- **`scripts/discovery/parse_awesome_lists.py`** — parses the
  README of 20 high-quality awesome-* curated lists (LLMOps,
  agents, evaluation, security, prompt engineering, …), extracts
  every `github.com/<owner>/<repo>` link, applies the same filter
  chain as `search_github.py` (not archived · pushed ≤ 18 months ·
  OSI licence · not already in `existing-ids.txt`), and emits
  `candidates.awesome.jsonl`.
- Both scripts reuse the OSI allowlist, freshness cutoff, alias
  table, and `existing-ids.txt` from `search_github.py` for full
  consistency with the v0.2.0 sweep.
- `scripts/discovery/existing-ids.txt` refreshed to 793 lines
  (matching the current registry size).
- `.tmp-discovery/` added to `.gitignore` as a scratch directory
  for discovery logs.

### Added — Deployment-posture dimension (2026-06-14)

- **New `deployment_posture` field** on every entry. Five-value enum:
  `local-only` (air-gappable) · `local-first` (`docker compose up`
  works out of the box; cloud optional) · `hybrid` (requires both
  local and cloud at runtime by design) · `cloud-first` (SaaS is the
  primary path, self-host docs are thin / advanced) · `api-only`
  (no local path exists). Added to `registry/_schema.yaml` and made
  **required** after backfill (all 793 entries now declare the field).
- **Heuristic classifier** (`scripts/compute_deployment_posture.py`)
  emits `registry/_metadata/_deployment.json` with per-entry posture
  + confidence + signals. Containerisation alone is **not** a hybrid
  signal — almost everything in the registry is containerised, so
  Docker/Helm presence pushes to `local-first`, not `hybrid`.
- **3-model ensemble curation** of the 447 low-confidence cases by
  Claude Sonnet 4.5 + Claude Opus 4.7 (extra-high reasoning) + GPT-5.4.
  15 background agents (5 batches × 3 reviewers, ~90 entries each).
  Consensus: 229 strong (3/3 agree) + 193 majority (2/3 agree) +
  25 split (kept heuristic + `needs_human_review: true`) — **94%
  ensemble-confirmed**, 168 corrections applied (overwhelmingly
  `hybrid -> local-first` where the heuristic over-flagged).
- **Final distribution**: local-first 573 (72.3%) · local-only 133
  (16.8%) · cloud-first 37 (4.7%) · hybrid 30 (3.8%) · api-only 20
  (2.5%). 92.8% of the catalogue is realistically self-hostable.
- **Viewer wiring** (both 3D and 2D):
  - New "Deployment posture" panel in the right rail with five
    clickable legend rows (posture-coloured swatch + count).
  - New "Local-possible only" quick-filter chip — filters to
    local-only + local-first + hybrid in one click.
  - Posture pill appears in the per-entry detail panel beside the
    category, tier, maturity and license pills.
  - Palette is a neutral warm-teal → cool-blue gradient (not a
    good/bad ramp): cloud-first and api-only are valid choices,
    the dimension exists to surface them, not to value-judge.
- **New visual**: `visuals/deployment-posture.svg` — per-category
  stacked horizontal bar chart with a top-row total + five-posture
  legend. Generated by `_build_deployment_posture()` in
  `scripts/build_visuals.py`; protected by `--check` drift gate.
- **New docs page**: `docs/deployment-posture.md` — full methodology,
  litmus tests for each posture, distribution table, viewer usage,
  caveats.
- **README** updated with posture distribution above the fold and a
  new bullet under "Browse" linking the docs page.

### Added — Three-model ensemble curation pass (Phase 3a closeout, 2026-06-14)

- **Multi-model consensus review of 445 backlog entries** by
  Claude Sonnet 4.6 + Claude Opus 4.7 (extra-high reasoning) + GPT-5.4,
  each independently scoring the same entry against `GOVERNANCE.md` §1-§8.
  1,335 reviews total (42 batches of ~32 entries × 3 reviewers), each
  agent reading the source repo via raw.githubusercontent / gh CLI and
  emitting strict-schema JSON with action / field_changes / new_sovereignty_notes
  / rationale / confidence. Consensus rules: action requires ≥2/3 agreement
  (else deferred to human review); field values require ≥2/3 same value
  (or ±1 median for numeric scores); sovereignty_notes picks the longest
  proposal from agreeing reviewers; full audit trail preserved per entry,
  per reviewer in the session report. **Outcome: 91 keep / 312 revise /
  21 remove / 21 three-way-dissent** at mean reviewer confidence ≈ 0.87.
  391 field corrections applied (maintainer.type, origin_country,
  model_agnostic_score, primary_language, five_component_coverage shape);
  28 entries moved between categories (e.g. `defender` redteam→governance,
  `casdoor` agent→routing, `principles-of-ai-llms` redteam→education);
  21 entries removed for §8 violations (binary-only distros, single-vendor
  monitors, workload-trace datasets, RL training infra mislabelled as
  agent runtimes, planning-only repos with no code, paid-SaaS client SDKs);
  79 adjacency files cleaned of references to removed entries.
- **`docs/CURATION_BACKLOG.md` reduced from 447 → 23 entries** — the
  remaining 23 are the 21 three-way-dissent cases plus 2 pilot deferrals
  whose evidence was too thin for any reviewer to render confident action.
  Curator-reviewed proportion: **770 of 793 entries (97%)**, up from 45%.
- Registry now: **793 entries** across six categories (governance 101 ·
  agent 231 · eval 203 · redteam 94 · routing 92 · education 72) ·
  **3,148 adjacency edges** · tier distribution
  landmark=124 / canonical=3 / established=176 / emerging=118 / frontier=372.

### Added — Pre-launch polish (Phase 7, 2026-06-14)

- **Tier-stratified hero infographic** (`visuals/hero.svg`) — 1200×630
  LinkedIn-social-card banner emitted by `scripts/build_visuals.py`.
  Header (816 total) + six category tiles (icon, name, blurb, count,
  tier-stacked horizontal bar, tier micro-legend, four featured
  landmark names) + footer (repo / Pages URL / tier legend). Curator-
  vetted `HERO_CATEGORIES` allowlist guards against top-stars surfacing
  Phase-4-flagged outliers on launch-day artefacts. Auto-rebuilt by the
  same pipeline as `graph.svg` / matrices — counts cannot silently drift.
- **Live 3D viewer screenshot** (`visuals/viewer-3d-screenshot.png`,
  1600×900 @2×) inserted into README as the "this is what it looks like"
  visual above the force-directed static layout. Captured headless via
  Playwright against the deployed Pages site (clean image, no devtools).
- Both viewer `<meta name="description">` + `<meta property="og:description">`
  refreshed to **816** entries / **3,358** edges; `og:image` repointed
  from `graph.png` to `hero.svg` so LinkedIn / Slack / Discord link
  previews surface the scannable infographic, not the dense graph dot.
- README counts table refreshed end-to-end (badge `entries=816`,
  governance 107 / agent 251 / eval 210 / redteam 102 / routing 95 /
  education 51 = 816) — six stale "804" / "3,338" references replaced.

### Fixed

- **Hand-authored visuals that drifted from data and looked dated**: the
  README's lower-half static SVGs (`visuals/taxonomy.svg`, the bubble
  diagram, and `visuals/five-component-overlay.svg`, the heatmap)
  predated the Phase 7 design language and one had factually drifted
  from the YAML (guardrails-ai.policy_router rendered "partial" while
  `registry/governance/guardrails-ai.yaml` says "none"). The taxonomy
  bubble is now strictly redundant with `hero.svg` (which already shows
  all six categories with landmarks, counts, and tier mix) so it has
  been deleted from the repo and removed from both README and
  `docs/taxonomy.md` (replaced with a pointer to the hero). The
  five-component overlay has been re-implemented as `_build_overlay()`
  in `scripts/build_visuals.py` — clean 1200×720 layout, 2×2 legend
  (no clipped labels), brighter "aligned" colour for readable cell
  text, regenerated from `registry/governance/*.yaml` on every build
  and drift-checked via `build_visuals.py --check`.
- **Git author attribution**: rewrote every commit on `main` to
  `99622824+Benjamin-KY@users.noreply.github.com`. Prior commits used
  `benke@users.noreply.github.com` which GitHub mistakenly routed to an
  unrelated public user. No code or content changed — metadata-only.

### Added — Phase 2 (registry expansion to 804 entries)

- **+491 registry entries** (governance +60 · agent +170 · eval +130 ·
  redteam +57 · routing +60 · education +14) via the new
  `scripts/discovery/` curation harness — taking the catalog from
  313 → **804** entries (governance 106 · agent 249 · eval 206 ·
  redteam 101 · routing 92 · education 50).
- `scripts/discovery/` — systematic, reproducible candidate-discovery
  pipeline (NOT from-memory shortlists):
  - `existing_ids.py` snapshots every catalogued id for dedupe.
  - `search_github.py` sweeps a planned topic matrix (≈ 90 GitHub topics
    across the 6 in-scope categories) via `gh search repos`; filters
    archived / non-OSI / >18-month-old; emits `candidates.dedup.jsonl`.
  - `curate_candidates.py` applies an AI-context regex per category
    plus an out-of-scope deny-list (per `GOVERNANCE.md` §8: pure RAG
    cores, observability stacks, vector DBs, off-domain ML benchmarks,
    cybersecurity tooling without LLM context, awesome-list aggregators,
    etc.). Per-category caps land the total at ≈ 500.
  - `generate_entries.py` emits schema-valid YAMLs with conservative
    defaults (`model_agnostic_score=3`, `harness_paradigm_alignment=partial`,
    governance `five_component_coverage` all `none` unless the description
    explicitly proves a `partial` posture). Auto-generated
    `sovereignty_notes` carry a "conservative auto-curated default —
    refine on first manual README review" flag.
  - `add_adjacencies.py` cross-links each new entry to up to 4 siblings
    in the same (category, subcategory) bucket plus one well-known
    category anchor, ensuring the new entries land inside the main
    connected component of the knowledge graph (now 804 nodes, 3,338 edges).
- README and visuals updated for the new entry count.
- Regenerated `visuals/graph.svg`, `visuals/graph.png`,
  `visuals/graph-data.json`, `visuals/model-agnostic-spectrum.svg`,
  and the six per-category matrices under `docs/`.

### Phase 2 notes

- The committed `scripts/discovery/candidates.curated.jsonl` is the
  deterministic input that pairs with this batch of generated entries.
  Re-running discovery on a different date will produce a different
  candidate set (GitHub stars / topics drift).
- Strict OSI-license filter retained: every new entry has an SPDX
  identifier mapped from GitHub's reported `license.key`.
- Maturity inferred from upstream signals (`alpha` / `beta` / `ga`).
- Conservative scoring throughout: `model_agnostic_score=3` is the median
  default; `=4` only when the description explicitly states multi-provider
  / OpenAI-compatible. Manual upgrades welcome via PR.

## [Unreleased — Phase 1 (v0.1.0-dev seed, retained below)]

### Added
- Initial repository skeleton: directory layout, dual licensing
  (Apache-2.0 code + CC BY-SA 4.0 content), `pyproject.toml`, `Makefile`,
  `.gitignore`, `.env.example`, GitHub issue templates.
- `CHARTER.md` — motivating context (Fable / Mythos 2026-06-13 export-control
  recall; closed-garden trend; Indigenous-data-governance positioning).
- Registry YAML schema and per-category folders (governance, agent, eval,
  redteam, routing, education).
- Validation script + pytest harness for registry schema, uniqueness, and
  adjacency resolution.
- Metadata refresh script (`scripts/refresh_metadata.py`) with weekly
  GitHub Actions cron (`.github/workflows/refresh-metadata.yml`) that
  opens a PR with sidecar drift.
- CI validation workflow (`.github/workflows/validate.yml`) running on every
  PR — schema, pytest, and `build_matrices.py --check` for matrix drift.
- Release workflow (`.github/workflows/release.yml`) — on `v*.*.*` tag:
  validates, rebuilds visuals + matrices, fails on working-tree drift,
  attaches `visuals/` and matrices as release tarballs.
- **313 registry entries** across the six categories
  (governance 46 · agent 79 · eval 76 · redteam 44 · routing 32 · education 36)
  after two systematic-discovery sweeps against awesome-lists, GitHub topic
  searches, and recent survey papers (NeurIPS / ICML / ACL / USENIX 2024–2026):
  - **Initial seed** (44): hand-curated launch lineup.
  - **Systematic-discovery expansion #1** (+192): 6 parallel research agents
    surveyed `corca-ai/awesome-llm-security`, `tensorchord/awesome-llmops`,
    `e2b-dev/awesome-ai-agents`, `kaushikb11/awesome-llm-agents`,
    `yueliu1999/Awesome-Jailbreak-on-LLMs`, `onejune2018/awesome-llm-eval`,
    `Hannibal046/Awesome-LLM`, GitHub topic pages (`llm-evaluation`,
    `llm-benchmark`, `ai-gateway`, `llm-gateway`, `llm-proxy`,
    `openai-compatible`, `llm-judge`, `rag-evaluation`,
    `agent-security-benchmark`, `prompt-injection-scanner`,
    `jailbreak-orchestrator`, `llm-vulnerability-scanner`, etc.),
    vendor OSS catalogs (Microsoft, Alibaba, ByteDance, IBM, NVIDIA,
    Meta, OpenAI, Stanford, AI2, UK AISI, OpenBMB), and per-repo
    license verification. Strict OSI-license filter applied throughout
    — projects with custom non-commercial clauses (NirDiamant's
    RAG_Techniques, anthropics/courses, fastbook prose), missing
    LICENSE files (DataTalksClub zoomcamps, hkproj/pytorch-transformer,
    ARENA_3.0), or non-OSI source-available licenses (Open WebUI,
    Dify, AutoGPT Platform's Polyform Shield) were rejected and
    documented.
  - **Systematic-discovery expansion #2** (+77): 3 follow-up research
    agents targeted known-thin areas surfaced by the v0.1.0-dev graph —
    code-eval / math-reasoning / multimodal eval / agent benchmarks
    (`humaneval`, `bigcodebench`, `livecodebench`, `cruxeval`, `scicode`,
    `math`, `gpqa`, `mmmu`, `vlmeval-kit`, `bfcl`, `mind2web`,
    `appworld`, `t-eval`, `mle-bench`, `wildbench`, `beir`,
    `prometheus-eval`, `judgelm`, `longbench`, `medqa`, `finben`, …);
    observability / structured-output / LLMOps (`openllmetry`,
    `helicone`, `opik`, `langtrace`, `agentops`, `openlit`,
    `langwatch`, `baml`, `xgrammar`, `lm-format-enforcer`, `marvin`,
    `magentic`, `jsonformer`, `funcchain`, `agenta`, `prompttools`,
    `promptimize`, `tokencost`); jailbreak attacks / backdoors /
    adversarial NLP (`deep-inception`, `backdoor-llm`, `openattack`,
    `textattack`, `cleverhans`, `rain-self-alignment`, `jailbreak-hub`,
    `autoprompt-calibration`, `detect-pretrain-mink`,
    `easyedit-knowledge-attacks`, `llm-jailbreaking-defense`); and
    agent frameworks / multi-agent simulations / browser / tool-use
    agents (`ix-autonomous-agent`, `adala-data-agents`,
    `generative-agents-stanford`, `bmtools-tool-platform`,
    `agentlite-salesforce`, `llmcompiler-parallel`,
    `webvoyager-multimodal`, `hugginggpt-jarvis`,
    `chemcrow-science-agent`, `mem0-memory-layer`,
    `tarsier-web-perception`, `agentsims-sandbox`, `agentbench-thudm`,
    `toolbench-tool-learning`, `gorilla-api-llm`, `rd-agent-microsoft`,
    `griptape-framework`).
- Hand-authored `visuals/taxonomy.svg` and `visuals/five-component-overlay.svg`
  in the BRAND palette (mirroring `harmless-harnesses`).
- Data-driven `visuals/model-agnostic-spectrum.svg` generated by
  `scripts/build_visuals.py` from `model_agnostic_score` across the registry.
- **Force-directed knowledge graph** generated by
  `scripts/build_graph.py` (networkx + matplotlib + adjustText):
  `visuals/graph.svg`, `visuals/graph.png`, and
  `visuals/graph-data.json` (the D3 viewer payload). Layout is
  deterministic (`spring_layout` seed=42, k=0.55, iter=180).
- **Interactive D3 v7 viewer** (`visuals/index.html`) with search,
  clickable-legend category filtering, click-to-focus + neighbour
  highlight, drag, zoom, and a detail panel with neighbour links by
  category. Self-contained except for D3 CDN.
- **GitHub Pages deployment** (`.github/workflows/pages.yml`):
  two-job (build → deploy) workflow that rebuilds the graph from the
  live registry on every push touching `visuals/`, `registry/`, or
  the graph builder, and publishes to
  https://benjamin-ky.github.io/open-harness-atlas/.
- Generated comparison matrices for **all six** categories under `docs/`.
- `docs/taxonomy.md`, `docs/five-component-overlay.md`,
  `docs/fable-mythos-pattern-fire.md` (the 2026-06-13 worked example),
  `docs/sovereignty-rubric.md`.
- `companion/` skeleton with `open-harnesses` custom domain for
  `create-context-graph` (full graph build deferred to v0.3.0).

### Out of scope for the registry (not deferred — by design)
- **Closed-source projects.** The atlas catalogs *open* infrastructure.
- **Non-OSI licenses.** Llama Guard 3 (Llama Community License) and
  ShieldGemma (Gemma License) — technically capable but fail
  `GOVERNANCE.md` §1.1. Will be named in `docs/adjacencies.md` at v0.2.0
  with the reason, not added to the registry.
- **Internal / unreleased projects.** The author's research repo
  `sa-sovereign-llm-harness` is referenced as the canonical source of
  the framing in `CHARTER.md` and `docs/sovereignty-rubric.md` but is
  *not* a registry candidate — the registry catalogs released OSS
  third-party projects, not internal work-in-progress.
- **Resources without an underlying OSS repository.** DeepLearning.AI
  shorts and similar — do not satisfy the registry schema's
  `repo_url` requirement. The education lineup is filled with eight
  OSS-licensed alternatives instead.

### Deferred to later releases (genuinely deferred, will land)
- `docs/adjacencies.md` (named adjacencies with reasons) — v0.2.0.
- `visuals/sovereignty-radial.svg` — v0.2.0.
- `visuals/fable-mythos-pattern-fire.svg` illustration — v0.4.0
  (the *text* worked example shipped in v0.1.0).
- Full registry-driven companion domain generation — v0.3.0.

---

The first tagged release will be **v0.1.0**.
