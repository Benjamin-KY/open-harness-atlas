"""Validate every registry YAML against `registry/_schema.yaml`.

Usage:
    python scripts/validate_registry.py [--registry registry]

Exits non-zero on the first failure, printing a Rich-formatted error
that names the file, the JSON pointer to the offending node, and the
schema rule that failed.

Hermetic: no network, no LLM, no Neo4j. Safe to run in CI without
secrets.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from rich.console import Console
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
SCHEMA_PATH = REGISTRY_DIR / "_schema.yaml"

CATEGORIES = ("governance", "agent", "eval", "redteam", "routing", "education")

console = Console()


def load_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iter_entry_files(registry: Path) -> list[Path]:
    files: list[Path] = []
    for category in CATEGORIES:
        cat_dir = registry / category
        if not cat_dir.is_dir():
            continue
        for child in sorted(cat_dir.glob("*.yaml")):
            if child.name.startswith("_"):
                continue
            files.append(child)
    return files


def load_entry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return data


def validate_filename_matches_id(path: Path, entry: dict[str, Any]) -> str | None:
    """Returns an error message if filename ≠ id, else None."""
    expected_stem = entry.get("id")
    if not isinstance(expected_stem, str):
        return f"{path}: missing or non-string `id`"
    if path.stem != expected_stem:
        return f"{path}: filename stem '{path.stem}' must equal `id` '{expected_stem}'"
    return None


def validate_category_matches_folder(path: Path, entry: dict[str, Any]) -> str | None:
    folder_category = path.parent.name
    declared_category = entry.get("category")
    if folder_category != declared_category:
        return (
            f"{path}: declared `category: {declared_category}` does not match "
            f"folder `{folder_category}`"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the open-harness-atlas registry.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_DIR,
        help="Path to the registry directory (default: %(default)s).",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=SCHEMA_PATH,
        help="Path to the JSON schema YAML (default: %(default)s).",
    )
    args = parser.parse_args(argv)

    schema = load_schema(args.schema)
    validator = Draft202012Validator(schema)

    files = iter_entry_files(args.registry)
    if not files:
        console.print(
            "[yellow]No registry entries found yet — this is expected during pre-release. "
            "Schema validation passes vacuously.[/yellow]"
        )
        return 0

    errors: list[tuple[Path, str]] = []
    ids_by_file: dict[Path, str] = {}
    all_ids: list[str] = []
    adjacency_refs: dict[str, list[str]] = defaultdict(list)

    for path in files:
        try:
            entry = load_entry(path)
        except Exception as exc:
            errors.append((path, f"YAML parse error: {exc}"))
            continue

        for err in validator.iter_errors(entry):
            pointer = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append((path, f"{pointer}: {err.message}"))

        fn_err = validate_filename_matches_id(path, entry)
        if fn_err:
            errors.append((path, fn_err))

        cat_err = validate_category_matches_folder(path, entry)
        if cat_err:
            errors.append((path, cat_err))

        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            ids_by_file[path] = entry_id
            all_ids.append(entry_id)

        for ref in entry.get("adjacent_to", []) or []:
            if isinstance(ref, str):
                adjacency_refs[ref].append(entry_id or path.name)

    # Uniqueness of ids
    id_counts = Counter(all_ids)
    for id_, count in id_counts.items():
        if count > 1:
            offending = [str(p) for p, eid in ids_by_file.items() if eid == id_]
            errors.append((Path(""), f"duplicate id '{id_}' in: {', '.join(offending)}"))

    # adjacency_to references must resolve to known ids
    known = set(all_ids)
    for ref, sources in adjacency_refs.items():
        if ref not in known:
            errors.append(
                (
                    Path(""),
                    f"unknown adjacency reference '{ref}' from: {', '.join(sources)}",
                )
            )

    if not errors:
        table = Table(title=f"open-harness-atlas — registry OK ({len(files)} entries)")
        table.add_column("Category", style="cyan")
        table.add_column("Entries", justify="right", style="green")
        per_category = Counter(p.parent.name for p in files)
        for cat in CATEGORIES:
            table.add_row(cat, str(per_category.get(cat, 0)))
        console.print(table)
        return 0

    console.print(f"[bold red]registry validation failed ({len(errors)} error(s)):[/bold red]")
    for path, msg in errors:
        loc = str(path) if path != Path("") else "<registry-wide>"
        # ASCII-only marker for Windows cp1252 safety; Rich's colour tags still render.
        console.print(f"  [red]FAIL[/red] {loc}: {msg}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
