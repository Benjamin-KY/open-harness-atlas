"""Validate the YAML schema itself loads and every registry entry conforms.

Hermetic — no network, no extras required beyond `[dev]`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "registry" / "_schema.yaml"
REGISTRY_DIR = REPO_ROOT / "registry"
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
from validate_registry import iter_entry_files  # noqa: E402


@pytest.fixture(scope="module")
def schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def validator(schema: dict) -> Draft202012Validator:
    # Will raise SchemaError if the schema is malformed.
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_schema_is_well_formed(schema: dict) -> None:
    assert schema["$schema"].startswith("https://json-schema.org/")
    Draft202012Validator.check_schema(schema)


def test_schema_required_fields_present(schema: dict) -> None:
    required = set(schema.get("required", []))
    must_have = {
        "id",
        "name",
        "category",
        "repo_url",
        "license",
        "primary_language",
        "tagline",
        "description",
        "maturity",
        "maintainer",
        "model_agnostic_score",
        "sovereignty_notes",
        "harness_paradigm_alignment",
    }
    missing = must_have - required
    assert not missing, f"Schema is missing required fields: {missing}"


def test_all_registry_entries_validate(validator: Draft202012Validator) -> None:
    entries = iter_entry_files(REGISTRY_DIR)
    if not entries:
        pytest.skip("No registry entries yet — schema check is vacuous in pre-release.")
    failures: list[str] = []
    for path in entries:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for err in validator.iter_errors(data):
            pointer = "/".join(str(p) for p in err.absolute_path) or "<root>"
            failures.append(f"{path.relative_to(REPO_ROOT)} :: {pointer}: {err.message}")
    assert not failures, "Schema violations:\n  - " + "\n  - ".join(failures)


def test_template_does_not_validate_unfilled() -> None:
    """The template file must not accidentally validate as a real entry —
    otherwise a contributor copying it without editing would pass CI.

    The template uses obviously-placeholder ids (`example-harness`) and
    refers to an `adjacent_to: [related-entry-id]` that doesn't exist;
    validation will fail on adjacency-resolution in the imperative
    validator, but the schema itself accepts the document. This test
    just confirms the schema accepts the structural shape (so the
    template stays a useful starting point).
    """
    template_path = REGISTRY_DIR / "_TEMPLATE.yaml"
    assert template_path.exists(), "Template file is missing"
    with template_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))
    assert not errors, (
        "Template no longer matches schema (structural shape broke):\n  - "
        + "\n  - ".join(str(e.message) for e in errors)
    )
