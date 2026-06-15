# Roadmap — open-harness-atlas

_Published 2026-06-14. Covers Jun 15 → Dec 14, 2026._

This roadmap is a public commitment, not a wish list. Each month has
one **headline ship** plus 2–3 quality threads. Exit criteria are
concrete and externally verifiable. If a month slips, the headline
slips with it; quality gates do not.

Sequencing principle: ship what unblocks the next ship. Editorial
integrity unblocks DOI; DOI unblocks paper citation; per-entry pages
unblock newsletter; CLI + API unblock ecosystem reuse.

---

## Where we are (baseline, 2026-06-14)

- **860 entries** across six categories: governance 103 · agent 264
  · eval 207 · redteam 109 · routing 104 · education 73.
- **3,371 adjacency edges** rendered in both a primary 3D WebGL viewer
  and a preserved 2D classic viewer.
- **93.4% self-hostable** by deployment_posture
  (`local-only`/`local-first`/`hybrid`), classified by heuristic +
  three-model ensemble (claude-sonnet-4.5 + claude-opus-4.7-xhigh +
  gpt-5.4).
- **97.3% curator-reviewed** (367 by hand, 403 via three-model
  ensemble pass, 67 hand-curated via the three 2026-06-14 / 2026-06-15
  recency-biased + fresh-discovery sweeps). 23 entries explicitly tracked
  in [`docs/CURATION_BACKLOG.md`](CURATION_BACKLOG.md).
- **Patterns layer**: seven named design patterns in
  [`docs/patterns/`](patterns/), one worked example
  ([`worked-example-model-agnostic-stack.md`](worked-example-model-agnostic-stack.md)),
  eight entry-point lenses, six supply-chain stacks.
- **Discovery infrastructure**: recency-biased GitHub sweep with
  collision-aware ID resolution, plus a GraphQL-batched
  awesome-list parser (~3 min on 11 lists vs the prior ~5 h REST
  path).
- **Quality gates always green** on `main`: validate_registry,
  pytest, ruff, build_visuals `--check`, build_matrices `--check`,
  compute_tier `--check`, build_graph orphan check, CI validate +
  pages.

## What's still soft

Six credibility-risk surfaces drive the roadmap:

1. **~60% of catalogue** still carries an `auto-curated default`
   sovereignty_notes line. The §8 inclusion test cannot be applied
   to entries no one has read end to end.
2. **No per-entry destination** — every node click is a side panel;
   you cannot send a colleague the URL of one harness page.
3. **Velocity sparklines empty** — only one snapshot exists. Needs
   2–4 weekly refreshes before the "rising" surface is real.
4. **Companion app is a stub** — `companion/` directory exists but
   is not built.
5. **Not citable** — no DOI; the two planned papers cannot deep-link
   into the atlas yet.
6. **No reason to return weekly** — no newsletter, no RSS, no digest.

---

## Monthly ships

### v0.4.0 — Polish & Coverage (Jun 15 → Jul 14)

**Headline.** Tier intelligence v2 + Coverage Expansion one-shot.

- Introduce `canonical` and `dormant` tiers. Fixes 24 entries
  currently mis-rendered as long-tail
  (`agentgpt`, `storm`, `karpathy-mingpt`,
  `generative-agents-stanford`, …).
- Add `data_missing: true` visual encoding. Fixes the autogen
  40k★ rendering as a dim hobby repo.
- Recalibrate the landmark age threshold for LLM-era projects
  (born 2022–24). Target eval distribution ≤ 60% frontier.
- Coverage Expansion: ingest the 23 named missing entries
  surfaced by the curation-coverage agent (Anthropic/courses
  21.8k★, huggingface/trl 18.6k★, NVIDIA/TensorRT-LLM 13.8k★,
  bentoml/BentoML 8.6k★, ARC-AGI 4.7k★, AdalFlow 4.1k★,
  textgrad 3.6k★, LiveBench 1.2k★, openai/preparedness 1.2k★,
  …) plus anything named in launch comments.
- Operational hygiene: CSP + SRI on viewer CDN scripts; atomic
  writes in `refresh_metadata.py`; spectrum.svg redesigned as
  horizontal small-multiples per category.

**Exit criteria.** Registry ≥ 860 entries · canonical tier
populated · no `data_missing` regressions · viewer-security
agent re-run clean · CSP + SRI active.

### v0.5.0 — Per-entry pages + JSON API (Jul 15 → Aug 14)

**Headline.** Every harness gets a permalink page and a JSON
endpoint.

- `/entry/<id>` route, statically rendered from YAML at build
  time: tagline · description · stars sparkline · five-component
  coverage · sovereignty notes · adjacencies graph · "used in
  stacks" backlinks · share link · canonical OpenGraph card.
- JSON API surface (zero-cost on Pages):
  `/api/entry/<id>.json` · `/api/lens/<id>.json` ·
  `/api/chain/<id>.json` · `/api/category/<cat>.json`. CORS-open.
- Editorial sweep half 1 (~250 of the boilerplate entries):
  rotate through agent + eval shelves; refine sovereignty_notes
  to the §8 standard; remove the 8 definite §8 fails
  (trident, atidraw, aigc-interview-book, awesome-agentic-ai-zh,
  agency-agents-zh, seca, weird-ai-test-museum, patent-creator).

**Exit criteria.** Every entry has a permalink page resolving on
Pages · API endpoints documented in README · boilerplate share
↓ from ~60% to ≤ 35%.

### v0.6.0 — CLI + editorial finish (Aug 15 → Sep 14)

**Headline.** `oha` CLI on PyPI + editorial integrity sweep complete.

- `pipx install open-harness-atlas`, then:
  `oha lens red-team-an-ai-system`,
  `oha chain local-first-rag`,
  `oha compare garak pyrit harmbench`,
  `oha entry langfuse --json`. Ships with shell completion.
- Editorial sweep half 2 (remaining ~250): governance, redteam,
  routing shelves. Curator-reviewed share → ≥ 99%.
- 14 entries needing curator notes addressed (firecrawl-mcp-server,
  ida-pro-mcp, openllmetry, tokencost, langchain,
  ms-generative-ai-for-beginners, bifrost,
  responsible-ai-workshop, yukiko, vibe-trading + 4 more).
- 9 miscategorised entries moved to correct shelves.
- 2–3 new curated tours: `build-rag-that-survives-recall`,
  `sovereignty-preserving-eval-pipeline`.

**Exit criteria.** ≥ 99% curator-reviewed · CLI installable from
PyPI · `CURATION_BACKLOG.md` shrunk to single-digit deferrals.

### v0.7.0 — Velocity dashboard + executable notebook (Sep 15 → Oct 14)

**Headline.** Live velocity surface + the worked example becomes
runnable code.

- 3–4 months of weekly snapshots = populated sparklines.
  [`docs/rising.md`](rising.md) on Pages with a dedicated
  "Rising" sort view in both viewers.
- Weekly newsletter / RSS: "5 new entries · 2 archived · top 5
  risers this week · 1 pattern of the week." Manually edited
  first; the auto-generation frame ships in the same milestone.
- `examples/model-agnostic-rag.ipynb` — 4–5 graph entries wired
  end-to-end (TGI embeddings → llama-cpp generation → ragas eval
  → langfuse trace → llm-guard policy) so the worked example
  becomes executable, not just architectural.
- Per-language discovery adapters
  (`scripts/discovery/sources/{arxiv,hf,pwc,gitee}.py`) close
  the China / HF / PwC blind spots Phase 4 surfaced.

**Exit criteria.** Sparklines render on ≥ 90% of entries ·
newsletter issue #1 out · notebook executable on a fresh clone
in < 10 min · new discovery adapters return non-zero candidates.

### v0.8.0 — Companion stand-up + DOI (Oct 15 → Nov 14)

**Headline.** v0.3.0 companion app + Zenodo DOI + Paper #2
submission packet.

- Companion app goes from stub to deployable Neo4j-backed query
  layer. Three flagship Cypher queries ship as buttons:
  1. "If X goes away, what covers the same surface?"
  2. "Show me all paths from a governance entry to a red-team
     entry through ≤ 3 hops"
  3. "Which lenses share ≥ 50% of their entries?"
  Docker-compose one-liner.
- Zenodo DOI minted — atlas snapshot becomes citable as a
  dataset. `CITATION.cff` published. README badge.
- Paper #2 (the structural critique, BK solo first author,
  with section 3.3 co-authored via Maiam nayri Wingara outreach
  per the plan in `sa-sovereign-llm-harness/`) submission
  packet uploaded to the FAccT 2027 portal. Atlas + DOI cited.
- 5 reserved curator-judgement BLOCKs from Phase 4 swarm
  resolved (author calls — not delegable).

**Exit criteria.** Companion responds to all 3 flagship queries
on a fresh `docker compose up` · DOI live on Zenodo ·
FAccT 2027 submission packet on file.

### v1.0.0 — State of the Ecosystem (Nov 15 → Dec 14)

**Headline.** v1.0 release + first quarterly report.

- v1.0 release gates (all of these, no exceptions):
  - ≥ 99% curator-reviewed
  - DOI live on Zenodo
  - Companion app live with `docker compose up` quickstart
  - Per-entry pages live for every entry
  - JSON API live for every entry / lens / chain / category
  - ≥ 6 months of velocity history accrued
  - Zero known `GOVERNANCE.md` §8 violations
  - All CI workflows pinned to commit SHAs (supply-chain
    hygiene from Phase 4)
- "State of the OSS AI Harness Ecosystem Q4 2026" report,
  generated from registry + velocity + curator commentary:
  trends, casualties, breakouts, sovereignty posture
  distribution shifts, license-mix changes,
  who-acquired-whom timeline. PDF published with its own
  Zenodo DOI.
- Conference / podcast circuit kickoff packet: slides, talking
  points, demo flow.
- Embeddable widget v0.1 (iframe-friendly mini-viewer) for
  cited use in blog posts and slides.

**Exit criteria.** `v1.0.0` tag on `main` · report PDF
published with DOI · widget embeds without console errors on at
least three external test pages.

---

## Cross-cutting always-on threads

- **Discovery cadence**: weekly recency sweep (cheap now that the
  GraphQL rewrite has landed) + monthly awesome-list sweep +
  quarterly arxiv / HF / PwC adapter run.
- **Quality gates never regress**: CI must stay green first-attempt.
  If a commit breaks CI, that commit blocks the next ship until
  it is fixed forward.
- **Sovereignty positioning never softens**: any cloud-first /
  api-only addition gets an explicit `sovereignty_notes` rationale
  and sits behind the posture filter.
- **Voice stays human**: README, CHANGELOG, newsletter all written
  in author voice. No emoji-laden AI prose, no "delve into", no
  bullet-soup. LinkedIn-style hook openings.

## What gets cut if a month slips

- Embeddable widget (v1.0.0) → pushed to 2027 Q1.
- VS Code extension stays off the roadmap until ecosystem pull is
  demonstrated.
- Real-time companion: fall back to Neo4j Aura if self-host proves
  operationally heavy.

## What gets added if a month finishes early

- Widget brought forward.
- IDSov outreach to Maiam nayri Wingara surfaced earlier (the
  outreach window per the paper plan is Jul–Oct 2026 anyway).
- Per-pattern executable notebooks (one per pattern, not just the
  worked example).

## What success looks like on Dec 14

- ~1,000 entries, ≥ 99% curator-reviewed.
- Atlas + Companion + CLI + API + Widget + Newsletter = a small
  ecosystem, not a single website.
- Cited by Paper #2 (in submission), DOI'd, deep-linkable.
- Positioned as **the** primary source for OSS AI harnesses
  across governance, agent, evaluation, red-team, routing, and
  education — multidimensional and curated, not a static
  awesome-list dump.

---

_The roadmap is versioned. Updates ship as ordinary commits. If a
month's exit criteria change, the change lands here with a
rationale._
