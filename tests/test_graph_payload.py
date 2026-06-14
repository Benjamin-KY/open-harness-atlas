"""Smoke tests for the knowledge-graph payload that the interactive
viewer (visuals/index.html) loads.

These run only if graph-data.json has been built (build_graph.py).
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PAYLOAD = REPO / "visuals" / "graph-data.json"


pytestmark = pytest.mark.skipif(
    not PAYLOAD.exists(),
    reason="visuals/graph-data.json not built; run scripts/build_graph.py first",
)


@pytest.fixture(scope="module")
def payload():
    return json.loads(PAYLOAD.read_text(encoding="utf-8"))


def test_payload_shape(payload):
    assert {"meta", "nodes", "links"} <= payload.keys()
    assert payload["meta"]["n_nodes"] == len(payload["nodes"])
    assert payload["meta"]["n_edges"] == len(payload["links"])
    assert len(payload["meta"]["categories"]) == 6


def test_every_node_has_required_fields(payload):
    required = {"id", "name", "category", "color", "url", "tagline",
                "degree", "mas"}
    for node in payload["nodes"]:
        assert required <= node.keys(), f"missing fields on {node.get('id')}"
        assert isinstance(node["degree"], int) and node["degree"] >= 0
        assert isinstance(node["mas"], int) and 0 <= node["mas"] <= 5


def test_every_link_resolves(payload):
    ids = {n["id"] for n in payload["nodes"]}
    for link in payload["links"]:
        assert link["source"] in ids, f"unknown source {link['source']}"
        assert link["target"] in ids, f"unknown target {link['target']}"
        assert link["source"] != link["target"], "self-loop in graph"


def test_at_least_95pct_of_nodes_have_edges(payload):
    nodes_with_edges = set()
    for link in payload["links"]:
        nodes_with_edges.add(link["source"])
        nodes_with_edges.add(link["target"])
    n = len(payload["nodes"])
    connected = len(nodes_with_edges)
    ratio = connected / n
    assert ratio >= 0.95, (
        f"only {connected}/{n} ({ratio:.1%}) nodes have adjacency edges; "
        "registry connectivity has regressed"
    )


# ---------------------------------------------------------------------------
# deployment_posture passthrough (dimension shipped 2026-06-14)
# ---------------------------------------------------------------------------
VALID_POSTURES = {"local-only", "local-first", "hybrid", "cloud-first", "api-only"}


def test_every_node_declares_deployment_posture(payload):
    """Every node must carry deployment_posture for the viewer's posture
    filter and the per-node posture pill to render."""
    missing = [n["id"] for n in payload["nodes"]
               if not n.get("deployment_posture")]
    assert not missing, (
        f"{len(missing)} nodes missing deployment_posture: "
        f"{missing[:5]}..."
    )


def test_deployment_posture_values_are_in_enum(payload):
    bad = [(n["id"], n.get("deployment_posture")) for n in payload["nodes"]
           if n.get("deployment_posture") not in VALID_POSTURES]
    assert not bad, f"out-of-enum postures: {bad[:5]}..."


def test_summary_posture_facet_is_present(payload):
    """The meta block must publish the registry-wide posture distribution
    so both viewers can render the Deployment-posture legend panel."""
    facet = payload["meta"].get("deployment_posture")
    assert facet is not None, "meta.deployment_posture missing"
    by_key = dict(facet)
    assert set(by_key) >= VALID_POSTURES, (
        f"meta.deployment_posture missing keys: {VALID_POSTURES - set(by_key)}"
    )
    # The facet must aggregate to the registry total (no entries lost).
    assert sum(by_key.values()) == payload["meta"]["n_nodes"]


def test_local_possible_majority(payload):
    """Sanity: >50% of the catalogue should be local-possible
    (local-only + local-first + hybrid). If this drops below 50%,
    either the curation drifted toward cloud-locked entries (curatorial
    regression) or the classifier has a bug."""
    facet = dict(payload["meta"]["deployment_posture"])
    local_possible = facet.get("local-only", 0) + facet.get("local-first", 0) + facet.get("hybrid", 0)
    total = payload["meta"]["n_nodes"]
    assert local_possible / total > 0.5, (
        f"local-possible share dropped to {local_possible}/{total} "
        f"({local_possible/total:.1%}); investigate curation drift"
    )
