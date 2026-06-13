# Changelog

All notable changes to **open-harness-atlas** are documented here. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Initial repository skeleton: directory layout, dual licensing
  (Apache-2.0 code + CC BY-SA 4.0 content), `pyproject.toml`, `Makefile`,
  `.gitignore`, `.env.example`, GitHub issue templates.
- `CHARTER.md` — motivating context (Fable / Mythos 2026-06-13 export-control
  recall; closed-garden trend; Indigenous-data-governance positioning).
- Registry YAML schema and per-category folders (governance, agent, eval,
  redteam, routing, education).
- Validation script + pytest harness for registry schema and uniqueness.
- Metadata refresh script with weekly GitHub Actions cron.
- Initial entries (~46) across the six categories.
- Hand-authored `visuals/taxonomy.svg` and `visuals/five-component-overlay.svg`.
- Generated comparison matrices for governance and agent categories.
- `docs/sovereignty-rubric.md` scoring methodology.
- `companion/` skeleton with `open-harnesses` custom domain for
  `create-context-graph`.

---

The first tagged release will be **v0.1.0**.
