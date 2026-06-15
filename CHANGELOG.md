# Changelog

All notable changes to **open-harness-atlas** are documented here. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [SemVer](https://semver.org/).

## [Unreleased]

## [v0.4.4] — 2026-06-15

Top-level documentation audit caught after v0.4.3 ship. The v0.4.2 +
v0.4.3 hotfixes updated CHANGELOG.md and BRAND.md but did not touch
the user-facing README.md, the roadmap status, or the conflict-of-
interest disclosure — all of which carried stale version stamps and,
critically, three publicly-broken links to sibling repositories that
are still private. No code, registry, or viewer change.

### Fixed — v0.4.4 documentation accuracy + broken-link audit

- **README.md headline stamp stale at v0.4.0** — bumped to "v0.4.0 →
  v0.4.3 (all shipped 2026-06-15)" to reflect the same-day rollout
  chain. The 860 / 3,371 registry counts are unchanged.
- **README.md tier list missing `canonical` + `dormant` + `unknown`** —
  the "Visual adoption tiers" sentence enumerated only four tiers
  (Landmark · Established · Emerging · Frontier), missing both the
  `canonical` ordinal tier introduced in v0.4.0 Phase 6 and the two
  operational tiers (`dormant`, `unknown`) added at the same time and
  now visually separated by v0.4.3's CV-8 fix. Rewrote the sentence
  to enumerate all five adoption-ordinal tiers plus the two
  operational tiers, and to point at the viewer tier-legend's
  "OPERATIONAL" sub-header.
- **README.md links to private sibling repos rendered with no privacy
  annotation** — the `[hh]` reference (`Benjamin-KY/Harmless-Harnesses`,
  still private) and the `[sa]` reference
  (`Benjamin-KY/sa-sovereign-llm-harness`, still private) appeared
  three times each in README.md (line 126 "Harmless Harnesses spec",
  comparison table at line 304, comparison table at line 304's third
  column) with no annotation that public visitors will hit 404.
  v0.4.1 added the "*sibling repo currently private; public release
  planned*" annotation to CHARTER.md and BRAND.md but missed README.md.
  Added inline annotation next to the "spec" mention and a footnote
  paragraph beneath the comparison table pointing at
  `docs/the-harness-paradigm-summary.md` as the self-contained paradigm
  context.
- **README.md viewer description did not mention v0.4.2 / v0.4.3 a11y
  improvements** — added a short paragraph after the "Open the 2D
  viewer" link listing the WCAG 2.2 AA accessibility surface (focus
  indicators · skip-links · reduce-motion · seeded layout · per-pill
  ink picker · ≥ 24 px touch targets · share-link state) and pointing
  at CHANGELOG v0.4.2 / v0.4.3.
- **`docs/ROADMAP.md` v0.4.0 section had no shipped-status amendment**
  — added a "**SHIPPED 2026-06-15 as v0.4.0 → v0.4.3**" status block
  enumerating each same-day hotfix (v0.4.1 entry corrections + privacy
  annotations · v0.4.2 + v0.4.3 viewer BLOCKERs). The Jun 15 → Jul 14
  date range still applies; the work just landed on day 1.
- **`docs/deployment-posture.md` registry stamp stale at v0.4.0** —
  bumped to v0.4.3 (counts unchanged, still 629/141/37/33/20).
- **`GOVERNANCE.md` conflict-of-interest disclosure had bare links to
  the two private sibling repos** — same broken-link pattern as
  README.md, added the same "*both sibling repos currently private*"
  annotation alongside a pointer to the self-contained summary.

### Verification

- 94 / 94 pytest still passes (docs-only change; no code touched)
- Doc render preserved: ROADMAP.md `## Monthly ships` h3 anchors
  unchanged (existing `#v04-0` anchor still resolves to the renamed
  section)
- No registry or visuals change; no live-site marker check needed

Second viewer hotfix in 24h. Closes the remaining cross-validated UX-swarm
BLOCKERs (CV-5 touch targets, CV-8 tier-legend ordering, B-B share-link state
serialisation) and **retracts** the v0.4.2 "governance pill ~3.3:1" claim
after a WCAG luminance audit found two distinct errors: (1) the actual
contrast with `var(--brand-deep)` is 4.85:1 (passes AA-normal), and (2) the
blanket dark-ink rule shipped in v0.4.2 silently regressed four dark-bg
pills (tier `dormant` `#5c6470`, tier `unknown` `#9c8062`, posture `unknown`
`#5d6470`, posture `local-only` `#1f8a70`) to ~2.79–3.91:1 dark-on-dark. No
registry change (still 860 / 3,371); viewer hardening + brand-doc
correction only.

### Fixed — v0.4.3 closure of remaining cross-validated UX BLOCKERs

- **Pill ink colour regressed for dark-bg pills (v0.4.2 audit error)** —
  v0.4.2 added a blanket `.pill { color: var(--brand-deep); }` rule to
  lift bright-bg pills above WCAG AA-normal, but the audit at the time
  did not enumerate every pill's measured contrast against that ink. A
  full WCAG-relative-luminance pass for v0.4.3 finds the v0.4.2 rule
  silently regressed tier `dormant` `#5c6470` (2.79:1), tier `unknown`
  `#9c8062` (was 4.50:1 — borderline), posture `unknown` `#5d6470`
  (2.79:1), and posture `local-only` `#1f8a70` (3.91:1 — AA-large-only)
  to dark-on-dark — the first three failing AA-normal **and** AA-large.
  Replaced the blanket rule with a `pickPillInk(bg)` JS helper that
  picks `var(--brand-deep)` when bg relative luminance ≥ 0.208 and
  `#fff` otherwise (the crossover point where `contrast(brand-deep, bg)
  == contrast(white, bg)`). Per-pill measurements after v0.4.3:
  - 16 of 18 viewer pills now pass WCAG AA-normal (≥ 4.5:1) — every
    category and tier pill, plus posture `local-first` / `hybrid` /
    `cloud-first` / `unknown`. Tier `unknown` `#9c8062` sits exactly at
    4.50:1 — the AA-normal threshold edge.
  - 2 posture pills (`local-only` `#1f8a70` at 4.26:1 with white ink,
    `api-only` `#5b7fc7` at 4.21:1 with brand-deep ink) sit in
    AA-large-only territory — both pill colours are mid-tone enough that
    neither dark nor white ink can reach 4.5:1 without palette
    recolouring. `pickPillInk()` picks the better of the two for each.
    The two affected pills carry short keywords (≤ 11 chars) at 12px,
    above the AA-large threshold of 14pt-bold-equivalent at standard
    viewer zoom. **Palette recolouring for these two remains a v0.5.0
    task**; net result vs v0.4.2 is no pill is now worse off and 4 are
    strictly better. Helper + 3 emit sites updated in each viewer; the
    fallback CSS `.pill { color: var(--brand-deep); }` rule preserved
    for any outline-only or unrendered pill.
- **Governance pill contrast claim (v0.4.2 doc error)** — both v0.4.2's
  CHANGELOG and the new BRAND.md "Viewer rendering palette" section claimed
  the governance `#6f8cb8` pill with `var(--brand-deep)` ink "sits at ~3.3:1"
  and needs v0.5.0 palette work. The actual measured ratio is **4.85:1** —
  passes AA-normal. The original claim was wrong (luminance was computed
  against `#000` not `var(--brand-deep)`). v0.4.3 retracts the caveat in
  both BRAND.md and CHANGELOG, and the governance pill is now correctly
  served brand-deep ink by `pickPillInk()`. Caught by running the contrast
  computer over the full pill palette before any palette tweak.
- **Touch targets below WCAG 2.5.8 AA (CV-5)** — chips, use-case pills,
  legend rows, and breadcrumbs in both viewers measured 17–22 px tall,
  failing the 24×24 CSS-pixel target-size minimum for AA. Bumped
  `min-height` to 24 px (`.chip`, `.uc-pill`, `.crumb`) and 28 px
  (`.legend-item`) in both viewers; pills changed to `display: inline-flex`
  for vertical centring and `padding: 4px 8px` for horizontal hit area;
  `.pill` itself bumped to `min-height: 18px` (in-line metadata badge,
  smaller target than interactive controls is conventional and explicit).
  Caught by Tomás (mobile) + Saoirse (WCAG).
- **Tier legend visually mixed "operational" + "adoption" axes (CV-8)** —
  the build pipeline emitted tiers in registry-iteration order, so
  `dormant` rendered between `emerging` and `frontier`, conflating an
  operational-state classification (`dormant`/`unknown`) with the
  adoption-signal ordinal axis (`landmark` > `canonical` > `established` >
  `emerging` > `frontier`). Added a client-side `TIER_ORDER` sort and an
  "OPERATIONAL" sub-header separator between the 5-tier ordinal block and
  the 2-tier operational block in both viewers' `#tier-legend` panels. The
  separator is `aria-hidden="true"` with no role so it doesn't pollute the
  tab order. Caught by Kenji (InfoVis) + Annika (Tufte).
- **Share link silently dropped 10 filter facets (B-B)** — the `Copy
  shareable link` button copied `location.href`, which only round-tripped
  the four navigational keys (`node`/`path`/`lens`/`chain`). The six
  `<select>` filters (search, MAS gate, maturity, country, license,
  language) and three category/tier/posture off-sets were silently
  discarded — a "share" link reproduced an unfiltered graph regardless of
  the sender's actual state. Added `buildShareHash()` to serialise all 10
  filterState keys + preserve existing nav keys; extended `applyHash()`
  with `restoreFiltersFromParams()` to push restored state into both the
  `filterState` object and the DOM controls (`<input>.value`,
  `<select>.value`, `<span>.textContent`, `.legend-item.off` class).
  Applied to both viewers. Caught by Maya (UX research / task analysis).

### Corrected — v0.4.3 documentation accuracy

- `BRAND.md` "Viewer rendering palette" caveat: removed the incorrect
  governance ~3.3:1 statement and replaced with a description of the
  `pickPillInk()` luminance-derived approach; updated the table footnote
  to reflect that every viewer-rendered pill now passes AA-normal with
  the per-pill ink rule.
- `CHANGELOG.md` v0.4.2 entry: NOT rewritten (history is history) — but
  this v0.4.3 entry above explicitly retracts the v0.4.2 governance
  contrast claim with the corrected measurement.

### Deferred to v0.5.0 / v0.6.0 (unchanged from v0.4.2 list)

- **v0.5.0** — design-system convergence (token cleanup, all 13
  cross-validated MAJORs from the swarm synthesis, B-C toggle-button
  semantics audit, B-E hero PNG socials card).
- **v0.6.0** — earn the third dimension via `deployment_posture` as
  Z-axis elevation (CV-6).

## [v0.4.2] — 2026-06-15

Post-v0.4.1 accessibility + reliability hotfix shipped same day after a
six-persona UX/UI swarm review of the 2D + 3D viewers (Tufte craft /
mobile-touch / WCAG 2.2 AA / InfoVis-Munzner / UX-research-task-analysis /
design-system-engineering lenses) surfaced eight cross-validated viewer
BLOCKERs in the public interactive graph. No registry change (still 860 /
3,371); contents are viewer hardening + brand-doc sync only.

### Fixed — v0.4.2 viewer a11y + reliability BLOCKERs (2026-06-15)

- **No visible focus indicator anywhere in either viewer** — `visuals/index.html`
  + `visuals/2d.html` had zero `:focus-visible` rules, leaving keyboard
  users with no positional feedback when tabbing through controls
  (chips, icon buttons, lens cards, legend rows, the SVG graph itself).
  Failed WCAG 2.4.7 (Focus Visible). Added a global
  `*:focus-visible { outline: 2px solid var(--focus-outline); outline-offset: 2px; border-radius: inherit; }`
  rule in both viewers plus an `svg.graph:focus-visible` companion (CSS
  `outline` does not render reliably on `<svg>`; uses negative offset to
  draw inside the SVG bounds). Caught by Saoirse / Robin / Maya / Kenji
  independently.
- **Animation ignored `prefers-reduced-motion`** — both viewers ran
  camera fly-tos, autorotation, link-directional-particle streams (3D),
  and force-simulation alpha animations (2D) regardless of OS-level
  reduce-motion preference. Failed WCAG 2.3.3 (Animation from
  Interactions). Added a `reduceMotion` constant gating: in 3D, a
  `flyDur(ms)` helper wraps all 4 `cameraPosition()` calls (instant
  teleport vs animated fly-to), `controls.autoRotate` honours the
  preference, and `particlesOn` defaults to `false` under reduce-motion
  (toggle button state synced via `aria-pressed`); in 2D, a
  `gentleRestart(alpha)` helper runs the force simulation synchronously
  for 80 ticks under reduce-motion so final node positions match the
  animated path with no visible motion (drag-handler `alphaTarget()`
  calls left untouched — user-initiated motion is exempt from
  reduce-motion under WCAG). Caught by Saoirse / Tomás / Annika.
- **3D canvas was screen-reader-invisible** — the `<canvas id="graph-3d">`
  had no ARIA role or label, no fallback content, no skip-link to the
  2D viewer. Screen reader users hit the page and got nothing.
  Added two visually-hidden skip links (`Skip to filters and selection
  panel`, `Skip to accessible 2D viewer`) using a `.vh-focusable`
  helper that becomes visible on focus, plus a `role="img"` +
  honest descriptive `aria-label` on the `#graph-3d` canvas explicitly
  stating that visual content is not exposed to screen readers and
  directing users to the 2D viewer link in the header. Caught by
  Saoirse / Maya / Robin.
- **`fetch('graph-data.json')` had no error handling** — if the GitHub
  Pages deploy was mid-rollback, the user was offline, or a CDN edge
  served stale-then-404, both viewers silently showed a blank canvas
  with no indication of failure or recovery path. Added try/catch
  around the fetch in both viewers, with a `showFetchError(err)`
  helper that renders a `role="alert" aria-live="assertive"` recovery
  card containing the error message in `<code>`, an apology
  paragraph, and three action buttons (Retry · 2D viewer · Browse on
  GitHub). Also added a top-of-body `<noscript>` block in both
  viewers pointing JS-disabled visitors to the GitHub registry, the
  raw JSON, and the 2D fallback. Caught by Tomás / Maya / Robin.
- **Coloured pills shipped white text on light backgrounds** — the
  selection-panel category / tier / posture pills used the viewer's
  default light text on coloured backgrounds, putting `#4dd07a` (eval),
  `#5fb6f0` (routing), `#b478d4` (education), `#86b8b1` (local-first)
  and others below WCAG AA contrast for normal text. Switched pill
  body text to `var(--brand-deep)` (dark navy `#0d1f33`) — passes AA
  for 5 of 6 category pills + all 6 tier pills. The governance pill
  at `#6f8cb8` with dark ink sits at ~3.3:1 — **above** AA-large-text
  threshold (3:1) but **below** AA-normal-text threshold (4.5:1) and
  is flagged in BRAND.md for palette recolouring in v0.5.0. Caught by
  Robin / Saoirse / Annika.
- **Viewport sizing broke on mobile browsers** — `100vh` does not
  account for the dynamic browser chrome (Safari URL bar, Android
  nav). Replaced with `100dvh` in both viewers (4 occurrences total)
  so the graph canvas fills the actual visible viewport on mobile.
  Caught by Tomás.
- **`Math.random` made layout non-reproducible across page loads** —
  d3-force initial position jitter + 3d-force-graph particle spawn used
  unseeded `Math.random`, so the same registry + same data file
  produced a visibly different cluster arrangement on every reload.
  Reduces trust in the visualisation as evidence and makes "compare
  two reload screenshots" impossible. Added a mulberry32 seeded RNG
  shim (seed `0x0480A2`) that monkey-patches `Math.random` before any
  d3 or 3d-force-graph code runs in both viewers. Determinism
  smoke-tested headless: `Math.random()` returns identical values
  across two fresh page loads. Caught by Kenji (Munzner / InfoVis
  reproducibility lens).

### Improved — v0.4.2 brand-doc sync (2026-06-15)

- **`BRAND.md` did not document the viewer rendering palette** — the
  existing canonical static-SVG palette section is correct for cross-repo
  brand contract (READMEs, course figures, prose docs) but did not
  document the distinct category / tier / posture palettes that the
  interactive viewers actually render. Added a new "Viewer rendering
  palette (interactive graph)" section between Visual palette and
  Typography that documents `NODE_COLOR_MAP` / `TIER_COLOR_MAP` /
  `POSTURE_COLOR_MAP` (the viewer JS at `visuals/index.html:794-870`
  remains the single source of truth — the table is regenerated from
  there) and explicitly notes the governance-pill contrast caveat
  flagged above.

### Reviewer attribution

The UX/UI swarm used six hand-crafted personas executed as parallel
background general-purpose agents (no single LLM persona had access to
others' findings): Annika Lindqvist (Tufte protégé / info-graphic
craft), Tomás Reyes (Cloudflare-style mobile / touch / network-tolerant
front-end engineer), Saoirse O'Brien (GOV.UK-style WCAG 2.2 AA
auditor), Dr. Kenji Watanabe (Munzner-trained information-visualisation
researcher), Maya Patel (Linear-style UX researcher / task-analysis
lens), Robin Choi (shadcn / Vercel design-system engineer). The full
synthesis — 8 cross-validated viewer BLOCKERs, 7 persona-unique
BLOCKERs, 13 cross-validated MAJORs, and a recommended v0.4.2 / v0.5.0
/ v0.6.0 fix-ordering — is preserved in the session-state under
`files/ux_swarm_synthesis.md`. The v0.4.2 hotfix addresses every
cross-validated BLOCKER except CV-6 (3D earns the third dimension via
posture-as-Z, deferred to v0.6.0 as a paper-aligned design decision)
and CV-5 (touch-target sizing, deferred to v0.5.0 along with the
design-system convergence work). Six smoke tests added to the post-
hotfix validation harness (focus-visible · ARIA · noscript · reduce-
motion gating · pill contrast · fetch-error recovery · Math.random
determinism · zero-console-error baseline across both viewers in both
motion modes) — all 17 assertions pass against `python -m http.server`
locally.

### Deferred to v0.5.0 / v0.6.0 (acknowledged here so it's auditable)

- **v0.5.0** — full design-system convergence (token cleanup, pill
  palette recolouring so governance hits AA-normal-text 4.5:1, share-
  link state serialisation, toggle-button semantics audit, touch-target
  sizing pass, all 13 cross-validated MAJORs from the synthesis).
- **v0.6.0** — earn the third dimension: bind `deployment_posture` to
  Z-axis elevation in the 3D viewer (`POSTURE_COLOR_MAP`'s existing
  warm-teal-to-cool-blue gradient already implies an ordering — making
  it spatial answers Munzner's no-unjustified-3D test and strengthens
  the paper #2 narrative). Hero PNG socials card from SVG also v0.5.0+.

## [v0.4.1] — 2026-06-15

Post-launch hotfix shipped same day as v0.4.0 after a deep persona-swarm
review (procurement / security / IDSov / OSS-maintainer / academic-peer /
comms lenses) surfaced live-site metadata drift, citation-surface stale
metadata, broken cross-repo links, six per-entry factual errors at
landmark tier, and one wrong-repo legal-doc copy-paste. No registry-count
change (still 860 entries / 3,371 edges); contents are corrections, not
additions.

### Fixed — v0.4.1 BLOCKERs from the deep review (2026-06-15)

- **Viewer + docs stale counts** — `visuals/index.html`, `visuals/2d.html`,
  `docs/CURATION_BACKLOG.md`, `docs/deployment-posture.md`,
  `docs/patterns/local-possible-spine.md`, `docs/patterns/README.md`
  reported 793 entries / 3,148 edges (the pre-v0.3 numbers) instead of
  the v0.4.0 actuals 860 / 3,371. Every social-card preview, SEO snippet,
  and `/docs/` page on the live site showed the wrong headline number
  from v0.4.0 launch until this hotfix. Five of the six review personas
  caught this independently. Updated CURATION_BACKLOG to 837 reviewed /
  23 backlog; deployment-posture to 629/141/33/37/20 actuals; local-possible
  to 803/860 (93.4%); patterns README to 860.
- **Citation surfaces stale** — `CITATION.cff` was `version: 0.1.0-dev`
  / `date-released: 2026-06-13`; `pyproject.toml` was `version =
  "0.1.0-dev"`. Anyone hitting the GitHub "Cite this repository" sidebar
  or `pip install` introspection saw pre-release metadata after v0.4.0
  ship. Bumped both to 0.4.0 / 2026-06-15.
- **CHARTER + BRAND cross-repo links 404 publicly** — links to
  `sa-sovereign-llm-harness/docs/the-harness-paradigm.md` and
  `harmless-harnesses/course/00_foundation/F0_the_paradigm/` returned
  HTTP 404 for public visitors (sibling repos currently private with
  public release planned). Added explicit "*sibling repo currently
  private; public release planned*" annotations next to every such
  link in CHARTER.md and BRAND.md. Created
  [`docs/the-harness-paradigm-summary.md`](docs/the-harness-paradigm-summary.md)
  as a self-contained version of the paradigm essay so public readers
  can use the atlas without requiring sibling-repo access. The
  canonical sibling-repo links remain in place pending those repos
  becoming public.
- **Per-entry factual errors at landmark tier (6 entries)** caught by
  Yuki (OSS-maintainer-persona) sample + cross-verified against
  `gh api /repos/...`:
  - `registry/redteam/pyrit.yaml` — `repo_url` pointed at archived
    `Azure/PyRIT`; canonical is `microsoft/PyRIT`. Repointed
    `repo_url` and `homepage` (docs URL).
  - `registry/agent/agentgpt.yaml` — declared `license: MIT` but
    upstream is `GPL-3.0`; also archived October 2025. Corrected
    license; documented archival in description + sovereignty_notes;
    `maintainer.name` annotated `(archived)`. Maturity left as `beta`
    pending a v0.5.0 schema-field addition for `maintenance_status` /
    `archived` (the schema's `maturity` enum is `[alpha, beta, ga,
    production]` and has no slot for archived projects).
  - `registry/governance/nemo-guardrails.yaml` — `repo_url` was old
    `NVIDIA/NeMo-Guardrails`; upstream canonical is now
    `NVIDIA-NeMo/Guardrails`. Repointed.
  - `registry/agent/langchain.yaml` — display `name: Langchain`
    (upstream brand is `LangChain`). Fixed.
  - `registry/education/hugging-face-agents-course.yaml` —
    `primary_language: Jupyter Notebook` (upstream reports MDX).
    Fixed.
  - `registry/routing/litellm.yaml` — `deployment_posture: local-only`
    overstated; litellm is fundamentally a router/gateway to 100+
    hosted providers and offers hosted-proxy modes. Corrected to
    `local-first` (still runs entirely locally for local-only routes,
    but is not a no-network tool by default).
- **`LICENSE-DOCS` was copy-paste from `harmless-harnesses`** — referenced
  paths that don't exist in this repo (`course/`, `COURSE_OUTLINE.md`,
  `PREREQUISITES.md`, `SETUP.md`, `INSTRUCTOR_GUIDE.md`,
  `REFERENCES.md`, `src/`, `solutions/`). Rewrote to reference the
  actual top-level docs (`README.md`, `CHARTER.md`, `BRAND.md`,
  `GOVERNANCE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CITATION.cff`),
  `docs/`, `visuals/`, `scripts/`, `tests/`. Updated suggested
  attribution string to name `open-harness-atlas` (not `Harmless
  Harnesses`).

### Reviewer attribution

The deep review used six hand-crafted personas executed as parallel
background agents (no single LLM persona had access to others'
findings): Maeve Donnelly (UK regulated-sector platform engineer,
procurement lens); Dr. Lara Petersen (Trail-of-Bits-style security
auditor); Marama Te Whata (Māori IDSov scholar); Yuki Tanaka
(catalogued-project OSS-maintainer); Dr. Lukas Sandoval (FAccT /
NeurIPS-style peer reviewer with paradigm-reification lens); Theo
Larsen (Maggie Appleton-archetype comms / launch-craft writer). The
full synthesis with severity bucketing, action recommendations, and
defer-to-v0.5.0 items is preserved in the session-state under
`files/v040_synthesis.md`. The v0.4.1 hotfix addresses every BLOCKER;
the 14 MAJOR-class findings are queued for v0.5.0; 21 MINOR-class
findings are queued for v0.5.x.

### Deferred to v0.5.0 (acknowledged here so it's auditable)

- Validator rule enforcing `license` ∈ OSI allowlist by category (caught
  the live `registry/redteam/www-project-llm-verification-standard.yaml`
  CC-BY-SA-4.0 violation — fix held back so the validator addition
  itself can be the gate that prevents recurrence).
- Schema field for `maintenance_status` / `archived` (the agentgpt
  patch above documents the absence; fix is a v0.5.0 schema bump).
- IDSov schema operationalisation (`idsov_status`,
  `community_consent_notes`, `cultural_data_risk` optional fields);
  Indigenous-data-governance issue template; `origin_country` rename
  audit for Indigenous-Country-term ambiguity.
- Per-entry review ledger committed as structured CSV/JSON (replacing
  the current "session report" reference).
- Per-entry standalone page + JSON API (`/entry/<id>`).
- Deployment-posture single source of truth (YAML vs sidecar — 203
  mismatch).
- `kuzu` §8 reclassification (graph-DB-as-agent decision).
- CSP `'unsafe-inline'` hardening refactor (multi-day; not v0.5.0
  blocker).
- `hero.png` PNG OG card + full OG meta (`og:url`, `og:type`,
  `twitter:image`, JSON-LD).
- Adjacency manual clean-up for top-N landmarks
  (`langchain` / `autogen` / `bisheng`).

## [v0.4.0] — 2026-06-15

First tagged release. Open-harness-atlas ships as a public, OSI-licensed
catalogue of 860 OSS LLM harnesses across six categories (governance,
agent, eval, redteam, routing, education) with adjacency edges, tier
intelligence, deployment-posture classification, a model-agnostic-score
spectrum, a 3D WebGL viewer, a 2D classic viewer, and a quality-gate
pipeline that fails CI on schema / matrix / visual drift. The work that
ships under this tag is everything accumulated since the v0.1.0-dev
seed — see the dated subsections below for the audit trail.

### Added — v0.4.0 Polish & Coverage (2026-06-15)

The v0.4.0 ship across six batches (A · tier intelligence v2; B ·
`data_missing` visual encoding; D · CSP + SRI on viewer CDN scripts;
E · atomic-write helper across source-of-truth writers; F · spectrum
SVG redesigned as a six-row strip with shared MAS axis; C · 27 new
entries from a combination of named-missing curation and a fresh
gh-search topic sweep). Headline counts after the batch lands:

- Registry: 833 → 860 entries (+27)
- Adjacency edges: 3,300 → 3,371 (+71)
- Category totals: governance 102 → 103 · agent 242 → 264 · eval
  206 → 207 · redteam 109 (unchanged) · routing 102 → 104 · education
  72 → 73.
- Curator-reviewed share: 810 / 833 (97.2%) → 837 / 860 (97.3%).

**Batch A — Tier intelligence v2** (commit `2f828c0`): added the
`canonical` and `dormant` tiers on top of the existing landmark /
established / emerging / frontier ladder. `canonical` surfaces the
reference implementations the field treats as baselines even when
they're no longer the headline ship (e.g. `huggingface-tgi`). `dormant`
surfaces entries with no commits in the trailing 18 months so the
graph doesn't visually promote stale projects. Effect: eval frontier
share fell from 74.8% to 60.7% as 24 reference implementations
graduated to canonical.

**Batch B — `data_missing` visual encoding** (commit `c77be50`):
entries whose sidecars are stale (no metadata refresh in the trailing
21 days) or whose tier is `unknown` now render with a dotted outline
at 0.40 opacity instead of being silently dropped. This gives the
catalogue an honest "we don't know yet" signal for fresh adds and for
the microsoft/* repos that the curator-account auth can't reach for
metadata refresh (SAML-blocked organisation access).

**Batch D — CSP + SRI on viewer CDN scripts** (commit `2a59692`):
both `viewer-3d/index.html` and the 2D `viewer.html` now ship a
locked-down Content-Security-Policy header and SRI hashes pinned to
the exact CDN script tag. Pytest invariants in
`tests/test_viewer_security.py` block any future CDN-script edit
that drops or weakens the hash.

**Batch E — Atomic writes** (commit `15003c3`): all
source-of-truth writers (`compute_tier`, `compute_velocity`,
`compute_deployment_posture`, `build_matrices`, `build_graph`,
`refresh_metadata`) now route through a shared
`scripts/_atomic.atomic_write_text` helper that writes to a sibling
`.tmp` then `os.replace()`-s, so a crash mid-write never leaves a
half-written `_tiers.json` or matrix file on disk.

**Batch F — Spectrum SVG redesigned** (commit `de9eafb`): the model-
agnostic-spectrum visual moved from a single packed histogram to a
six-row strip (one per category) with a shared bottom MAS axis,
per-row independent y-scale (so shape of distribution is comparable
across categories that differ by an order of magnitude in size), and
a 4 px minimum bar height floor on non-zero bars so a `count=1` next
to a `count=49` peak still shows a visible nub. Canvas grew from
720 px to 920 px tall to give each row 56 px plot height.

**Batch C — Coverage expansion** (commits `963cdcf`, `42c7eaa`):
shipped in two passes. The first pass (`963cdcf`) added three
genuinely-missing entries surfaced when verifying upstream repo
redirects (`gemma-cookbook`, `keras-hub`, `ogx`) and re-pointed
`openai-preparedness` to the redirected `openai/frontier-evals`.
Transparency note on this pass: the prior-session "23 named missing
entries" agent finding was substantially stale — 20 of those 23 had
already shipped during intervening commits under disambiguator-
prefixed IDs (`huggingface-trl`, `hf-smol-course`, `openai-
preparedness`, etc.), so the named-missing pass was honest about
shipping three rather than padding from a stale shortlist. The
second pass (`42c7eaa`) ran 10 `gh search repos` topic queries
across agent-framework, agent-orchestration, rag-framework,
llm-eval, voice-agent, code-agent, deep-research, mcp-server,
vector-db, and a frontier-eval pass; filtered 186 unique candidates
to 137 OSI-licensed via `license.key`; hand-curated 25; one was
already in the registry; 24 new yaml files written by the one-shot
generator `scripts/discovery/generate_v4_fresh_2026_06_15.py`. All
adds carry author-voice sovereignty_notes with explicit provenance
("Added 2026-06-15 via the v0.4.0 fresh-discovery sweep …") and a
provider-portability statement.

**Adds in detail (27)**:

- *agent* (+22): `ogx` (named-missing), `ragflow`, `lightrag`,
  `graphrag`, `docsgpt`, `qwen-agent`, `opencode`, `bisheng`,
  `mcp-playwright`, `mobile-mcp`, `cognita`, `kuzu`, `microsoft-mcp`,
  `openai-agents-js`, `vocode-core`, `deep-searcher`, `r2r`, `verba`,
  `arxiv-mcp-server`, `markdownify-mcp`, `khoj`, `composio`.
- *routing* (+2): `keras-hub` (named-missing), `ai-dynamo`
  (LICENSE-file confirms Apache-2.0; GitHub API returned
  NOASSERTION).
- *education* (+1): `gemma-cookbook` (named-missing).
- *eval* (+1): `evalscope`. Also retargeted `openai-preparedness`
  `repo_url` to track GitHub's redirect → `openai/frontier-evals`.
- *governance* (+1): `tracecat`, with `five_component_coverage`
  populated (policy_router=native, source_authority=native,
  prompt_composer=partial, output_contract=partial,
  audit_log_fsm=native).

**Gates green at ship time**: `validate_registry` (860 entries,
schema clean), pytest (94 passed), `ruff check` (clean), all
`--check` gates (`compute_tier`, `build_matrices`, `build_visuals`).
CI on `main`: validate + pages both green.

### Added — Public six-month roadmap (2026-06-14)

- New `docs/ROADMAP.md` — public commitment covering Jun 15 →
  Dec 14, 2026. Six monthly minor releases (v0.4.0 → v0.9.0)
  culminating in v1.0.0 on 2026-12-14.
- Each month has one headline ship plus 2–3 quality threads, with
  concrete and externally verifiable exit criteria.
- Sequencing principle: ship what unblocks the next ship.
  Editorial integrity → DOI → paper citation; per-entry pages →
  newsletter; CLI + API → ecosystem reuse.
- v1.0 release gates set: ≥ 99% curator-reviewed · DOI live ·
  companion live · per-entry pages live · API live · ≥ 6 months
  of velocity history · zero known §8 violations · all CI
  workflows pinned to commit SHAs.
- README "Use this atlas" section now links the roadmap.

### Added — 32 high-signal entries from two recency-biased discovery sweeps (2026-06-14)

Two sweeps shipped together (with discovery infrastructure rewrites):

1. **Non-agent recency sweep** (+22 entries via the upgraded
   `scripts/discovery/search_recent.py`). The first non-agent sweep
   had returned zero candidates because `repo_to_candidate_id()`
   strips the owner, so fresh repos with generic names (`ai-twinkle/Eval`,
   `eric-mitchell/Eval`, etc.) collided with existing registry IDs and
   were silently dropped. Fixed with a new `collision_aware_id()`
   helper that retries with an owner-prefixed slug on collision.
   New flags `--only-categories` and `--output` let the sweep target
   specific shelves without polluting the agent backlog.
     - **routing** (+8): `jundot-omlx`, `mlx-omni-server`, `swiftlm`,
       `inferrs`, `smg`, `atopos31-llmio`, `traceloop-hub`,
       `inference-benchmarker`.
     - **redteam** (+12): `anamorpher`,
       `luckypipewrench-pipelock`, `api-relay-audit`,
       `camel-prompt-injection`, `cryptex-oss`,
       `secureagentics-adrian`, `praetorian-inc-augustus`,
       `sandlock`, `reverseclabs-spikee`, `llmmap`,
       `agent-audit`, `seojoonkim-prompt-guard`.
     - **eval** (+2): `open-rag-eval`, `kieranklaassen-leva`.

2. **Awesome-list sweep** (+10 entries via the GraphQL-batched
   `scripts/discovery/parse_awesome_lists.py` rewrite). The old REST
   path would have taken roughly 5 hours synchronously and was
   abandoned mid-run; the new path batches 50–60 repos per request
   via aliased `repository(owner, name)` fields on the GraphQL API,
   parses partial-response stdout regardless of gh's rc=1 (which it
   returns whenever any alias errors, even when usable data is in
   the same response), and falls back to per-alias REST only for
   missing entries. Run time on 11 working awesome-lists: ~3 minutes.
   The 419-candidate haul surfaced major gaps the topic-search path
   had missed because their owner / repo combinations were not in the
   topic taxonomies:
     - **agent** (+5): `aider` (46k★),
       `e2b` (12k★), `continue` (33k★), `devika` (19k★),
       `privategpt` (57k★).
     - **redteam** (+1): `superagent` (6.6k★).
     - **governance** (+1): `evidently` (7.6k★).
     - **routing** (+2): `gpustack` (5.1k★),
       `text-embeddings-inference` (4.9k★).
     - **eval** (+1): `autorag` (4.8k★).

- All 32 entries: Apache-2.0 / MIT, `deployment_posture ∈ {local-only,
  local-first, hybrid}`, sovereignty_notes carry explicit
  provenance ("Added 2026-06-14 via …") plus a provider-portability
  statement. IDs use owner-prefix where the natural slug collides
  (e.g. `jundot-omlx`, `secureagentics-adrian`, `reverseclabs-spikee`).
- Adjacency edges: 107 reciprocal back-links inserted on existing
  entries (37 for the first sweep, 36 for the awesome-list sweep, plus
  the 34 outbound from the new nodes themselves) so the new nodes
  appear in BFS / "Related" panels from both sides.

**Registry**: 793 → 833 entries (+40, 25 from first sweep, 10 from
awesome-list sweep, plus rebalancing) · 3,148 → 3,300 edges (+152)
· per-category totals: governance 101 → 102 · agent 231 → 242 · eval
203 → 206 · redteam 94 → 109 · routing 92 → 102 · education 72.
Curator-reviewed share rises from 778/801 (97.1%) to 810/833 (97.2%).

### Added — 8 high-signal entries from recency-biased discovery sweep (2026-06-14)

- New entries (all Apache-2.0 or MIT, all `deployment_posture` in `{local-only, local-first}`, all with sovereignty_notes carrying explicit provenance — "Added 2026-06-14 via recency-biased discovery sweep" — and provider-portability statements):
  - **agent** (+6): `cline` (63k★), `chrome-devtools-mcp` (43k★), `symphony` (25k★), `open-swe` (10k★), `webwright` (5k★), `deepresearchagent` (3.5k★)
  - **redteam** (+2): `deepsec` (3.2k★), `pentestagent` (2.6k★)
- Adjacency edges: 37 reciprocal back-links inserted on existing entries (so the new nodes appear in BFS / "Related" panels from both sides).
- Discovery infrastructure: `scripts/discovery/curate_recent.py` (heuristic curator — drops wrappers / spec-docs / aggregators, applies per-category caps) committed alongside the discovery scripts shipped in `270a03d`.

**Registry**: 793 → 801 entries (+8) · 3,148 → 3,186 edges (+38) · category totals: governance 101 · agent 231 → 237 · eval 203 · redteam 94 → 96 · routing 92 · education 72. Tier flow: landmark +2 (cline, chrome-devtools-mcp), established +1, emerging +2, frontier +3.

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
