import sqlite3

import pytest

from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_knowledge_graph import ResearchKnowledgeGraph


def make_graph(tmp_path):
    return ResearchKnowledgeGraph(SQLiteResearchStore(tmp_path / "knowledge-graph.sqlite3"))


def node(graph, node_id, node_type="claim"):
    return graph.add_node(node_id=node_id, node_type=node_type, label=node_id, actor_id="mira", source_refs=[f"source:{node_id}"])


def test_nodes_are_typed_and_immutable(tmp_path):
    graph = make_graph(tmp_path)
    saved = node(graph, "claim-a")
    assert saved["node_type"] == "claim"
    assert saved["source_refs"] == ["source:claim-a"]
    with pytest.raises(ValueError, match="already exists"):
        node(graph, "claim-a")
    with graph.store._connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("UPDATE research_knowledge_nodes SET label='changed' WHERE node_id='claim-a'")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM research_knowledge_nodes WHERE node_id='claim-a'")


def test_relationship_requires_provenance_and_known_nodes(tmp_path):
    graph = make_graph(tmp_path)
    node(graph, "evidence-a", "evidence")
    node(graph, "claim-a")
    with pytest.raises(ValueError, match="evidence references"):
        graph.link(source_id="evidence-a", target_id="claim-a", relation="supports", actor_id="elias", rationale="Review")
    with pytest.raises(ValueError, match="does not exist"):
        graph.link(source_id="missing", target_id="claim-a", relation="supports", actor_id="elias", rationale="Review", evidence_refs=["review:1"])
    edge = graph.link(source_id="evidence-a", target_id="claim-a", relation="supports", actor_id="elias", rationale="Independent source supports the claim.", evidence_refs=["review:1"], state="reviewed")
    assert edge["state"] == "reviewed"


def test_acyclic_derived_from_relationships(tmp_path):
    graph = make_graph(tmp_path)
    for value in ("a", "b", "c"):
        node(graph, value)
    graph.link(source_id="a", target_id="b", relation="derived_from", actor_id="mira", rationale="A derives from B.", evidence_refs=["source:a-b"])
    graph.link(source_id="b", target_id="c", relation="derived_from", actor_id="mira", rationale="B derives from C.", evidence_refs=["source:b-c"])
    with pytest.raises(ValueError, match="cycle"):
        graph.link(source_id="c", target_id="a", relation="derived_from", actor_id="mira", rationale="Invalid cycle.", evidence_refs=["source:c-a"])


def test_impact_is_bounded_and_excludes_withdrawn_edges(tmp_path):
    graph = make_graph(tmp_path)
    node(graph, "evidence", "evidence")
    node(graph, "claim")
    node(graph, "decision", "decision")
    node(graph, "experiment", "experiment")
    graph.link(source_id="evidence", target_id="claim", relation="supports", actor_id="elias", rationale="Evidence supports claim.", evidence_refs=["source:e-c"])
    graph.link(source_id="claim", target_id="decision", relation="informs", actor_id="mira", rationale="Claim informs decision.", evidence_refs=["source:c-d"])
    graph.link(source_id="decision", target_id="experiment", relation="motivates", actor_id="jun", rationale="Decision motivates experiment.", evidence_refs=["source:d-e"])
    withdrawn = graph.link(source_id="evidence", target_id="experiment", relation="documents", actor_id="mira", rationale="Withdrawn association.", evidence_refs=["source:e-x"], state="withdrawn")
    impact = graph.impact("evidence", max_depth=3, limit=2)
    assert [item["node"]["node_id"] for item in impact] == ["claim", "decision"]
    assert all(item["edge_id"] != withdrawn["edge_id"] for item in impact)


def test_impact_validates_bounds(tmp_path):
    graph = make_graph(tmp_path)
    node(graph, "claim")
    with pytest.raises(ValueError, match="max_depth"):
        graph.impact("claim", max_depth=21)
    with pytest.raises(ValueError, match="limit"):
        graph.impact("claim", limit=0)
