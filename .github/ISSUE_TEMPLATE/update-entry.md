---
name: Update a registry entry
about: Propose a correction or scoring change for an existing entry
title: "Update entry: <entry-id>"
labels: ["update-entry", "needs-triage"]
---

## Entry

- **Entry ID.** (matches the YAML filename, e.g., `litellm`)
- **File path.** (e.g., `registry/routing/litellm.yaml`)

## Proposed change

Describe the change at a high level. For scoring changes, name which
field(s) and the proposed before → after values.

## Evidence

Link the project's own canonical source (commit, doc page, release notes)
that justifies the change.

## Rubric reference

For scoring changes, cite the specific clause in
[`GOVERNANCE.md`](../GOVERNANCE.md) §2 (rubric) or
[`docs/sovereignty-rubric.md`](../docs/sovereignty-rubric.md) that
supports the new score.

## Conflict of interest

- [ ] I am a maintainer of the catalogued project.
- [ ] I have no affiliation with the catalogued project.

## Auto-refreshed fields

I confirm I am **not** hand-editing `registry/_metadata/*.json` files
(those are bot-owned).

- [ ] confirmed
