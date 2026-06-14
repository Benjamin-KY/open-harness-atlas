"""Tests for the Phase 6 entry-points (use cases) + supply chains feature.

Coverage targets:

* schema rejects unknown IDs in featured / recommended / chain / alternatives
* schema rejects malformed structures (short chains, missing fields)
* ``resolve_use_case_membership`` precedence: featured > recommended > auto
* ``auto_match`` honours both ``categories`` AND ``subcategories`` filters
* companion files in this repo currently validate cleanly
* graph payload after Phase 6 carries the new top-level + per-node fields
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
COMPANION_DIR = REPO_ROOT / "companion"
USE_CASES_PATH = COMPANION_DIR / "use_cases.yaml"
SUPPLY_CHAINS_PATH = COMPANION_DIR / "supply_chains.yaml"
USE_CASES_SCHEMA = COMPANION_DIR / "_use_cases.schema.yaml"
SUPPLY_CHAINS_SCHEMA = COMPANION_DIR / "_supply_chains.schema.yaml"
GRAPH_PATH = REPO_ROOT / "visuals" / "graph-data.json"

sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def build_graph():
    return importlib.import_module("build_graph")


@pytest.fixture(scope="module")
def use_cases_schema():
    return yaml.safe_load(USE_CASES_SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def supply_chains_schema():
    return yaml.safe_load(SUPPLY_CHAINS_SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture
def fake_entries():
    """Tiny synthetic registry for membership tests."""
    return [
        {"id": "alpha", "category": "eval", "subcategory": "benchmark"},
        {"id": "beta", "category": "eval", "subcategory": "redteam"},
        {"id": "gamma", "category": "eval", "subcategory": "benchmark"},
        {"id": "delta", "category": "agent", "subcategory": "framework"},
        {"id": "epsilon", "category": "routing", "subcategory": "inference"},
    ]


# ---------------------------------------------------------------------------
# Schema rejection tests
# ---------------------------------------------------------------------------


def _validate(schema: dict, doc: dict) -> list[str]:
    v = Draft202012Validator(schema)
    return [e.message for e in v.iter_errors(doc)]


def _good_use_case(**overrides) -> dict:
    base = {
        "id": "uc-test",
        "name": "X",
        "icon": "🎯",
        "short": "A short description that is long enough.",
        "description": "Forty-character minimum description for the use-case body.",
        "featured": ["alpha"],
    }
    base.update(overrides)
    return base


def _good_chain(**overrides) -> dict:
    base = {
        "id": "ch-test",
        "name": "X",
        "icon": "🔗",
        "description": "Forty-character minimum description for the supply chain.",
        "chain": [{"id": "alpha", "role": "first"}, {"id": "beta", "role": "second"}],
    }
    base.update(overrides)
    return base


def test_use_case_schema_accepts_well_formed_doc(use_cases_schema):
    doc = {"version": 1, "use_cases": [_good_use_case()]}
    assert _validate(use_cases_schema, doc) == []


def test_use_case_schema_requires_id_name_icon_short_description_featured(use_cases_schema):
    doc = {"version": 1, "use_cases": [{"id": "x"}]}
    errs = _validate(use_cases_schema, doc)
    # Schema demands these top-level fields per item.
    for needle in ("name", "icon", "short", "description", "featured"):
        assert any(needle in e for e in errs), f"missing {needle} not surfaced: {errs}"


def test_use_case_schema_rejects_bad_id_pattern(use_cases_schema):
    doc = {"version": 1, "use_cases": [_good_use_case(id="BAD ID")]}
    errs = _validate(use_cases_schema, doc)
    assert any("pattern" in e.lower() or "match" in e.lower() for e in errs)


def test_use_case_schema_rejects_xss_in_name(use_cases_schema):
    doc = {"version": 1, "use_cases": [_good_use_case(name="<script>alert(1)</script>")]}
    errs = _validate(use_cases_schema, doc)
    assert errs, "name with HTML tags must be rejected"


def test_use_case_schema_rejects_featured_over_cap(use_cases_schema):
    too_many = [f"id-{i}" for i in range(13)]  # cap is 12
    doc = {"version": 1, "use_cases": [_good_use_case(featured=too_many)]}
    errs = _validate(use_cases_schema, doc)
    assert any("12" in e or "maxItems" in e for e in errs), errs


def test_supply_chain_schema_rejects_chain_shorter_than_two(supply_chains_schema):
    doc = {"version": 1, "supply_chains": [
        _good_chain(chain=[{"id": "alpha", "role": "only"}]),
    ]}
    errs = _validate(supply_chains_schema, doc)
    assert any("2" in e or "minItems" in e or "short" in e.lower() for e in errs), errs


def test_supply_chain_schema_requires_role_per_step(supply_chains_schema):
    doc = {"version": 1, "supply_chains": [
        _good_chain(chain=[{"id": "a"}, {"id": "b"}]),
    ]}
    errs = _validate(supply_chains_schema, doc)
    assert any("role" in e for e in errs), errs


def test_supply_chain_schema_rejects_chain_over_cap(supply_chains_schema):
    too_long = [{"id": f"id-{i}", "role": "r"} for i in range(10)]  # cap is 9
    doc = {"version": 1, "supply_chains": [_good_chain(chain=too_long)]}
    errs = _validate(supply_chains_schema, doc)
    assert any("9" in e or "maxItems" in e for e in errs), errs


# ---------------------------------------------------------------------------
# Cross-check: validate_registry rejects unknown IDs in companion files
# ---------------------------------------------------------------------------


def test_validate_registry_rejects_unknown_featured_id(tmp_path, monkeypatch):
    """End-to-end: drop a bad companion file in place + run validator."""
    bad_companion = COMPANION_DIR / "_test_bad_use_cases.yaml"
    bad_companion.write_text(
        yaml.safe_dump({
            "version": 1,
            "use_cases": [
                _good_use_case(
                    id="rogue",
                    featured=["this-id-definitely-does-not-exist-xyz"],
                )
            ],
        }),
        encoding="utf-8",
    )
    try:
        import validate_registry  # type: ignore

        bad_known = {"alpha"}
        errs = validate_registry._validate_companion(
            data_path=bad_companion,
            schema_path=USE_CASES_SCHEMA,
            known_ids=bad_known,
            kind="use_case",
        )
        msgs = [m for _, m in errs]
        assert any("this-id-definitely-does-not-exist-xyz" in m for m in msgs), msgs
    finally:
        bad_companion.unlink(missing_ok=True)


def test_validate_registry_rejects_unknown_alternative_in_chain(tmp_path):
    bad_companion = COMPANION_DIR / "_test_bad_supply_chains.yaml"
    bad_companion.write_text(
        yaml.safe_dump({
            "version": 1,
            "supply_chains": [
                _good_chain(
                    id="rogue-chain",
                    chain=[
                        {"id": "alpha", "role": "first",
                         "alternatives": ["nope-nope-id"]},
                        {"id": "beta", "role": "second"},
                    ],
                )
            ],
        }),
        encoding="utf-8",
    )
    try:
        import validate_registry  # type: ignore

        errs = validate_registry._validate_companion(
            data_path=bad_companion,
            schema_path=SUPPLY_CHAINS_SCHEMA,
            known_ids={"alpha", "beta"},
            kind="supply_chain",
        )
        msgs = [m for _, m in errs]
        assert any("nope-nope-id" in m for m in msgs), msgs
    finally:
        bad_companion.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# resolve_use_case_membership precedence + auto_match correctness
# ---------------------------------------------------------------------------


def test_membership_precedence_featured_over_recommended(build_graph, fake_entries):
    use_cases = [{
        "id": "uc1", "label": "X", "tagline": "Y", "icon": "🎯",
        "featured": ["alpha"],
        "recommended": ["alpha", "beta"],  # alpha here MUST be dropped
    }]
    membership, enriched = build_graph.resolve_use_case_membership(use_cases, fake_entries)
    levels = {m["level"] for m in membership["alpha"]}
    assert levels == {"featured"}, "alpha should ONLY be featured, never recommended"
    levels_beta = {m["level"] for m in membership["beta"]}
    assert levels_beta == {"recommended"}


def test_membership_auto_match_requires_both_categories_and_subcategories(
    build_graph, fake_entries
):
    """auto_match with both filters: only entries matching BOTH should auto-qualify."""
    use_cases = [{
        "id": "narrow", "label": "X", "tagline": "Y", "icon": "🎯",
        "featured": [], "recommended": [],
        "auto_match": {
            "categories": ["eval"],
            "subcategories": ["benchmark"],
        },
    }]
    membership, _ = build_graph.resolve_use_case_membership(use_cases, fake_entries)
    auto_ids = {eid for eid, hits in membership.items()
                for h in hits if h["level"] == "auto" and h["id"] == "narrow"}
    # alpha + gamma are eval AND benchmark; beta is eval+redteam (excluded).
    assert auto_ids == {"alpha", "gamma"}


def test_membership_auto_match_excludes_already_featured(build_graph, fake_entries):
    use_cases = [{
        "id": "broad", "label": "X", "tagline": "Y", "icon": "🎯",
        "featured": ["alpha"],
        "recommended": ["gamma"],
        "auto_match": {"categories": ["eval"]},
    }]
    membership, _ = build_graph.resolve_use_case_membership(use_cases, fake_entries)
    auto_ids = {eid for eid, hits in membership.items()
                for h in hits if h["level"] == "auto" and h["id"] == "broad"}
    # alpha + gamma already pinned; only beta remains under "auto".
    assert auto_ids == {"beta"}


def test_membership_auto_match_only_categories(build_graph, fake_entries):
    use_cases = [{
        "id": "cat-only", "label": "X", "tagline": "Y", "icon": "🎯",
        "featured": [], "recommended": [],
        "auto_match": {"categories": ["agent"]},
    }]
    membership, _ = build_graph.resolve_use_case_membership(use_cases, fake_entries)
    auto_ids = {eid for eid, hits in membership.items()
                for h in hits if h["level"] == "auto"}
    assert auto_ids == {"delta"}


def test_enriched_contains_member_split(build_graph, fake_entries):
    use_cases = [{
        "id": "mixed", "label": "X", "tagline": "Y", "icon": "🎯",
        "featured": ["alpha"], "recommended": ["beta"],
        "auto_match": {"categories": ["routing"]},
    }]
    _, enriched = build_graph.resolve_use_case_membership(use_cases, fake_entries)
    assert len(enriched) == 1
    members = enriched[0]["members"]
    assert members["featured"] == ["alpha"]
    assert members["recommended"] == ["beta"]
    assert members["auto"] == ["epsilon"]


# ---------------------------------------------------------------------------
# In-repo companion files validate cleanly + graph payload carries fields
# ---------------------------------------------------------------------------


def test_repo_use_cases_file_validates(use_cases_schema):
    doc = yaml.safe_load(USE_CASES_PATH.read_text(encoding="utf-8"))
    errs = _validate(use_cases_schema, doc)
    assert errs == [], errs


def test_repo_supply_chains_file_validates(supply_chains_schema):
    doc = yaml.safe_load(SUPPLY_CHAINS_PATH.read_text(encoding="utf-8"))
    errs = _validate(supply_chains_schema, doc)
    assert errs == [], errs


def test_graph_payload_has_use_cases_and_supply_chains():
    """Built graph artefact carries the Phase 6 fields the viewer needs."""
    if not GRAPH_PATH.exists():
        pytest.skip("graph-data.json not built yet")
    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    assert "use_cases" in data
    assert "supply_chains" in data
    assert isinstance(data["use_cases"], list) and data["use_cases"], \
        "use_cases must be a non-empty list"
    assert isinstance(data["supply_chains"], list) and data["supply_chains"], \
        "supply_chains must be a non-empty list"
    # Every node must carry a use_cases array (possibly empty).
    nodes_with_field = sum(1 for n in data["nodes"] if "use_cases" in n)
    assert nodes_with_field == len(data["nodes"]), \
        "every node must carry a use_cases array"
    # Enriched use_cases must include the auto-resolved members field.
    for uc in data["use_cases"]:
        assert "members" in uc and isinstance(uc["members"], dict)
        assert {"featured", "recommended", "auto"} <= set(uc["members"])
