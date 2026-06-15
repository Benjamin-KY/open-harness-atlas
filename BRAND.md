# Brand & visual conventions — open-harness-atlas

This file is the single source of truth for naming, palette, typography,
diagram conventions, and visual style across the atlas. Conventions
deliberately mirror **`harmless-harnesses/BRAND.md`** so the two repositories
read as siblings.

---

## Name

- **Atlas title.** open-harness-atlas
- **Tagline.** *The OSS layer that makes model-agnostic AI workloads possible.*
  - Short form (hero / social): *Open harnesses for sovereign AI.*
  - Long form (procurement / scholarly): *A curated, jurisdiction-neutral
    catalog and knowledge graph of free, open-source harnesses (governance,
    agent, evaluation, red-team, routing) and free education resources,
    scored against the Harmless Harnesses five-component spec and a
    model-agnosticism / sovereignty rubric.*
- **Repo name.** `open-harness-atlas` (kebab-case).
- **Distribution name (PyPI for the validate/refresh scripts).** `open-harness-atlas`.
- **Module name (scripts package).** `open_harness_atlas`.

---

## License

- **Code** (`scripts/`, `tests/`, `*.py`) — **Apache-2.0**. See `LICENSE`.
- **Catalog content & visuals** (`registry/`, `docs/`, `visuals/`,
  top-level Markdown) — **CC BY-SA 4.0**. See `LICENSE-DOCS`.

Override these in one place if you fork (top-level `LICENSE` + `LICENSE-DOCS`
+ README license section + `pyproject.toml` `[project] license`).

---

## Visual palette

Mirrors the `harmless-harnesses` palette so atlas figures sit next to course
figures without colour clash.

| Role                          | Hex       | Use in this atlas                                  |
|-------------------------------|-----------|----------------------------------------------------|
| **Harness / spine**           | `#1f3a5f` | Category headers, taxonomy root, "harness" labels  |
| **Symbolic / deterministic**  | `#28a745` | Eval harnesses, deterministic test runners         |
| **LLM / stochastic**          | `#d68910` | Agent frameworks, model-tier entries               |
| **Typed data store**          | `#7d3c98` | Registry entities (Project / Maintainer / License) |
| **Baseline / failure mode**   | `#c0392b` | Closed-garden / restricted-access entries; warnings |
| **Background**                | `#ffffff` | White throughout                                    |
| **Body text**                 | `#222222` | Near-black                                          |
| **Muted / secondary text**    | `#555555` | Footnotes, captions, last-refreshed timestamps     |
| **Accent / call-out**         | `#f4ecf7` | Pull-quote backgrounds, charter highlights         |

All diagrams use white backgrounds and ship as SVG (canonical, vector,
scalable). Raster previews are optional and live under
`visuals/<name>/preview.png` (excluded from `.gitignore` allow-list).

---

## Viewer rendering palette (interactive graph)

The static-SVG palette above is the **brand contract** for figures shipped
alongside prose (READMEs, docs, the harmless-harnesses course). It assumes a
white background and high-contrast print/PDF rendering.

The interactive 2D + 3D graph viewers (`visuals/index.html`,
`visuals/2d.html`) ship a **distinct rendering palette** tuned for dark
canvas backgrounds + WCAG large-text contrast on coloured pills. The viewer
JS is the **single source of truth** for these values — this table is
regenerated from `NODE_COLOR_MAP` / `TIER_COLOR_MAP` / `POSTURE_COLOR_MAP`
in `visuals/index.html` (lines 794-870). If a swatch below disagrees with
the viewer JS, the JS is correct and this table is stale.

**Category palette** — bound to the registry `category` field. CVD-safe;
each hue is visually distinct under deuteranopia + protanopia simulation.

| Category    | Hex       | Used for                                       |
|-------------|-----------|------------------------------------------------|
| governance  | `#6f8cb8` | Governance harnesses (Tier-A/B/C/D wrappers)   |
| agent       | `#f0a634` | Agent frameworks, model-tier scaffolding       |
| eval        | `#4dd07a` | Evaluation suites, benchmarks, scorecards      |
| redteam     | `#e57063` | Red-team toolkits, adversarial probes          |
| routing     | `#5fb6f0` | Model-routing layers, request brokers          |
| education   | `#b478d4` | Free education resources (courses, textbooks)  |

**Tier palette** — bound to the computed `tier` field. Distinct hues
(not a sequential ramp) plus stroke-pattern differentiation in the graph
node outline (solid / dashed / dotted) so each tier remains
distinguishable under achromatopsia / monochrome rendering.

| Tier         | Hex       | Meaning                                       |
|--------------|-----------|-----------------------------------------------|
| landmark     | `#f0b35a` | ≥30k★, or ≥2yr at 5k+★ with active commits   |
| canonical    | `#b08acc` | Reference implementation — archived ≥5k★, or non-archived ≥5k★ + 1yr+ + idle >180d |
| established  | `#5fb6f0` | ≥1k★ + 1yr+ + active                          |
| emerging     | `#6fb59a` | ≥100★ + 3mo+ + active                         |
| dormant      | `#5c6470` | >18mo since last commit, not iconic           |
| frontier     | `#7e8a9c` | Passes inclusion, no independent adoption yet |
| unknown      | `#9c8062` | Metadata fetch failed (operational, not signal-low) |

**Deployment-posture palette** — neutral perceptual gradient (warm teal at
local end, cool blue at cloud end). **Not** a good/bad ramp: cloud-first +
api-only are valid sovereignty postures, the panel only surfaces the dimension.

| Posture      | Hex       | Meaning                                       |
|--------------|-----------|-----------------------------------------------|
| local-only   | `#1f8a70` | No outbound calls, fully offline-capable      |
| local-first  | `#86b8b1` | Local default, cloud opt-in                   |
| hybrid       | `#c9b08c` | Mixed local + cloud paths                     |
| cloud-first  | `#9cb8dd` | Cloud default, local opt-in                   |
| api-only     | `#5b7fc7` | Hosted-only, no local execution               |
| unknown      | `#5d6470` | Posture not yet classified                    |

**Pill text colour** — coloured pills in the selection panel use
`var(--brand-deep)` (dark navy `#0d1f33`) for body text, not white. White
text on the lighter pill hues (eval ~`#4dd07a`, governance ~`#6f8cb8`)
fails WCAG AA contrast for normal text; dark ink passes for 5 of 6
category pills + all 6 tier pills. The governance pill at `#6f8cb8` with
dark ink sits at ~3.3:1 — **above** AA-large-text threshold (3:1) but
**below** AA-normal-text threshold (4.5:1) and is flagged for palette
recolouring in v0.5.0.

---

## Typography

| Use                                | Font                                                       |
|------------------------------------|------------------------------------------------------------|
| Headings (sans)                    | Inter — fallback `system-ui, -apple-system, Segoe UI, sans-serif` |
| Body (sans)                        | Inter — fallback as above                                  |
| Monospace (code, IDs, hashes)      | JetBrains Mono — fallback `Consolas, "Liberation Mono", monospace` |
| Optional serif (long-form prose)   | IBM Plex Serif — fallback `Georgia, serif`                 |

Fonts are referenced via `font-family` stacks only; no font files are
distributed in the repo.

---

## Diagram conventions

1. **Read left-to-right, top-to-bottom.** Flowcharts go LR. Sequence
   diagrams read top-down.
2. **One concept per node.** A registry entry is one node. Categories are
   container nodes.
3. **Colour by role, not by aesthetic.** Use the palette above; never
   colour-code by stars or popularity.
4. **Edges carry verbs.** `implements`, `replaces-for`, `adjacent-to`,
   `maintained-by`, not bare arrows.
5. **Provenance footer.** Every SVG carries a footer with:
   - generator (e.g., `scripts/build_visuals.py::_build_hero`)
   - generation timestamp or last-edited date
   - registry version that produced the data
6. **One source of truth.** Visuals are emitted directly from
   `registry/*/*.yaml` + `companion/*.yaml` by the `scripts/build_*.py`
   generators. No checked-in SVG should ever disagree with the underlying
   YAML — if it does, the generator is wrong and must be fixed.
7. **Atlas-specific overlay.** Where a figure shows the Harmless Harnesses
   five components (Policy Router · Source Authority · Prompt Composer ·
   Output Contract · Audit Log + FSM), use the canonical component glyphs
   from `harmless-harnesses/visuals/spine/N6_five_invariants.svg` — do not
   re-draw them.

---

## Indigenous-data-governance positioning

The atlas adopts the same positionality as `harmless-harnesses` *(sibling
repo currently private; public release planned alongside v1.7+)*. See
[`CHARTER.md`](CHARTER.md) §"Indigenous-data-governance framing" for the
motivating context. The canonical positionality statement (Tynan 2023,
CARE Principles, Maiam nayri Wingara, IEEE 2890-2025) lives in
`sa-sovereign-llm-harness/docs/the-harness-paradigm.md` §"Indigenous
communities" *(sibling repo currently private)*; a self-contained
version that motivates the atlas without requiring sibling-repo access
lives in [`docs/the-harness-paradigm-summary.md`](docs/the-harness-paradigm-summary.md).

Per the author's standing as an Indigenous Australian scholar and author of
*The Harness Paradigm*, structural-critique framing is published without
external scholar gatekeeping. The F0 §6 distinction between **individual
standing** (the author writes; this atlas catalogs) and **community
gatekeeping for specific deployments** (downstream operators who deploy
against an Indigenous community's data still need that community's
consent) holds throughout this repo.

---

## Cross-repo brand contract

| This repo (`open-harness-atlas`) | Sibling (`harmless-harnesses`) | Sibling (`sa-sovereign-llm-harness`) |
|---|---|---|
| **Role.** Curated catalog of OSS harnesses + education. | **Role.** Pedagogical course teaching how to build harnesses. | **Role.** Research-grade prototype + evaluation evidence. |
| **Voice.** Field guide. Neutral. Citation-heavy. | **Voice.** Pedagogical. Practitioner. "Architecture, not hope." | **Voice.** Research. IMRAD. Primary-source-grounded. |
| **Updates.** Continuous (weekly metadata refresh). | **Tagged releases.** | **Tagged releases.** |
| **Reader exits to…** | The course (to learn how to build). | The atlas (to find an OSS implementation). |
| **Visuals.** Taxonomy, comparison matrices, sovereignty radial. | Spine, components, evidence, reskinned. | Diagrams from the research codebase. |
