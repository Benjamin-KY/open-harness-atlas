"""Cross-entry invariants: id uniqueness, adjacency resolution, filename ↔ id."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
from validate_registry import iter_entry_files  # noqa: E402


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_ids_are_unique() -> None:
    entries = iter_entry_files(REGISTRY_DIR)
    if not entries:
        pytest.skip("No entries yet.")
    ids = [_load(p)["id"] for p in entries]
    dupes = [eid for eid, count in Counter(ids).items() if count > 1]
    assert not dupes, f"Duplicate ids: {dupes}"


def test_filename_matches_id() -> None:
    entries = iter_entry_files(REGISTRY_DIR)
    if not entries:
        pytest.skip("No entries yet.")
    mismatches = []
    for path in entries:
        entry = _load(path)
        if path.stem != entry.get("id"):
            mismatches.append(f"{path.relative_to(REPO_ROOT)} ↔ id={entry.get('id')!r}")
    assert not mismatches, "Filename ↔ id mismatches:\n  - " + "\n  - ".join(mismatches)


def test_category_matches_folder() -> None:
    entries = iter_entry_files(REGISTRY_DIR)
    if not entries:
        pytest.skip("No entries yet.")
    mismatches = []
    for path in entries:
        entry = _load(path)
        if path.parent.name != entry.get("category"):
            mismatches.append(
                f"{path.relative_to(REPO_ROOT)}: folder={path.parent.name}, "
                f"category={entry.get('category')!r}"
            )
    assert not mismatches, "Category ↔ folder mismatches:\n  - " + "\n  - ".join(mismatches)


def test_adjacency_references_resolve() -> None:
    entries = iter_entry_files(REGISTRY_DIR)
    if not entries:
        pytest.skip("No entries yet.")
    all_ids = {_load(p)["id"] for p in entries}
    dangling: list[str] = []
    for path in entries:
        entry = _load(path)
        for ref in entry.get("adjacent_to", []) or []:
            if ref not in all_ids:
                dangling.append(f"{entry['id']} -> {ref} (not in registry)")
    assert not dangling, "Unresolved adjacencies:\n  - " + "\n  - ".join(dangling)
