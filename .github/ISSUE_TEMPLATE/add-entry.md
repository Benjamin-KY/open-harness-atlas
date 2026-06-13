---
name: Add a registry entry
about: Propose a new OSS harness or free education resource for inclusion
title: "Add entry: <project name>"
labels: ["add-entry", "needs-triage"]
---

## Project

- **Name.**
- **Repo URL.**
- **Homepage.** (if separate from repo)
- **License.** (SPDX, e.g., `Apache-2.0`, `MIT`, `BSD-3-Clause`, `MPL-2.0`)
- **Primary language.**
- **Maintainer type.** `individual` / `community` / `company` / `institution`

## Category

Pick exactly one (see [`CONTRIBUTING.md`](../CONTRIBUTING.md) for definitions):

- [ ] governance
- [ ] agent
- [ ] eval
- [ ] redteam
- [ ] routing
- [ ] education

## Why it qualifies

A 1–2 paragraph case explaining how the project meets all six inclusion
criteria in [`GOVERNANCE.md`](../GOVERNANCE.md) §1 (open licence, free,
maintained, in scope, verifiable, non-deceptive).

## Five-component coverage (governance entries only)

For each component, score `none` / `partial` / `native` with a
one-sentence justification:

- **Policy Router.**
- **Source Authority.**
- **Prompt Composer.**
- **Output Contract.**
- **Audit Log + FSM Escalation.**

## Sovereignty / model-agnosticism notes

1–3 sentences justifying the proposed `model_agnostic_score` (0–5). See
[`docs/sovereignty-rubric.md`](../docs/sovereignty-rubric.md).

## Adjacent entries

List any existing registry entries this project relates to (replaces,
complements, depends on).

## Conflict of interest

- [ ] I am a maintainer of this project. (If yes, see GOVERNANCE.md §5.)
- [ ] I have no affiliation with this project.
