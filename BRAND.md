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
