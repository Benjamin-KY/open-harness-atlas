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
