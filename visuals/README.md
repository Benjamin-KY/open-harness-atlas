# `visuals/` — design notes

All visuals here are released under **CC BY-SA 4.0** (`LICENSE-DOCS`), like
the rest of the catalog content. The accompanying generator code under
`scripts/` is Apache-2.0.

Every SVG below is **data-driven**: rebuilt on every push from the
registry YAMLs by `scripts/build_visuals.py`, then drift-checked in CI
via `python scripts/build_visuals.py --check`. Hand-edited SVGs do not
survive the next build — change the generator (or the YAML source) instead.

## Frontline assets (referenced from README + meta tags)

| File | Generator | Purpose |
|------|-----------|---------|
| `hero.svg` | `_build_hero()` in `scripts/build_visuals.py` | 1200×630 LinkedIn-social-card banner. Header (816 total) + six category tiles (icon, label, count, tier-stacked horizontal bar, four featured landmark names) + footer with repo + Pages URL. Set as the OpenGraph `og:image` for both viewers. |
| `graph.svg` / `graph.png` | `scripts/build_graph.py` | Force-directed static layout of the full 816-node / 3,358-edge graph. Used as the long-form "scientific layout" image in the README. |
| `graph-data.json` | `scripts/build_graph.py` | The same graph as a JSON payload, consumed by `index.html` (3D) and `2d.html` (2D) interactive viewers. |
| `five-component-overlay.svg` | `_build_overlay()` in `scripts/build_visuals.py` | 1200×720 heatmap mapping the 5 Harmless Harnesses components to 6 reference OSS governance projects. Cell values come directly from each project's `registry/governance/<id>.yaml` `five_component_coverage` field. |
| `viewer-3d/preview.png` | Headless Playwright capture of the live deployed 3D viewer | "What it looks like when you open it" screenshot for the README. |
| `model-agnostic-spectrum.svg` | `_build_spectrum()` in `scripts/build_visuals.py` | Per-entry `model_agnostic_score` bar across the full catalogue. Generated for downstream consumers; not currently surfaced in the README. |

## Interactive viewers

| File | Notes |
|------|-------|
| `index.html` | Primary 3D WebGL viewer (3d-force-graph + Three.js, bundled). Camera orbit, fly-to-focus, particle-flow edges, faceted filters, 8-lens "I need a harness for…" entry points, 6 curated supply-chain overlays, BFS path finder, CSV export, share link, deep-link via URL fragment. |
| `2d.html` | Classic 2D layout (D3 force-directed). Same data + same filter/search/lens/chain UX as the 3D viewer; adds mini-map, compare mode, cluster-layout toggle, PNG export. |

Both viewers consume `graph-data.json` + `companion/use_cases.yaml` +
`companion/supply_chains.yaml`. They are served by the GitHub Pages
deployment from `.github/workflows/pages.yml` on every push to `main`.

## Palette (mirrors `harmless-harnesses` `BRAND.md`)

| Hex       | Role |
|-----------|------|
| `#1f3a5f` | Spine / harness / governance |
| `#28a745` | Deterministic logic / eval / `native` cells |
| `#d68910` | LLM / stochastic component / agent / `partial` cells |
| `#7d3c98` | Data store / education / knowledge |
| `#c0392b` | Failure mode / adversarial / red-team |
| `#4a6fa5` | `aligned` cells (mid-blue, readable with white text) |
| `#e6e9ee` | `none` / out-of-scope cells (light grey, dark text) |

Adoption-tier ramp used by `hero.svg` and the viewers:

| Hex       | Tier |
|-----------|------|
| `#1f3a5f` | `landmark` |
| `#4a6fa5` | `established` |
| `#8aa6c8` | `emerging` |
| `#c8d3e0` | `frontier` |
| `#e8ecf0` | `unknown` (data not yet refreshed) |

All visuals render on a `#ffffff` background and use system fonts so they
work in dark / light browser themes without baking in a font dependency.

## Raster previews

PNG previews live at `visuals/<name>/preview.png` (allowlisted in
`.gitignore` via `!visuals/**/preview.png`). Generated raster exports of
SVGs are not checked in by default — `git status` should never show a
new `*.png` outside this convention.

## Why SVG over PNG

SVG is text-diffable, scales cleanly on retina / hi-DPI screens, can be
inspected from a screen reader (each SVG has `<title>` + `<desc>`), and
keeps the registry-to-visual provenance auditable — you can see the value
of every cell in plain XML.
