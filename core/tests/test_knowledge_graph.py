import pytest

from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore


def node(node_id, node_type="finding", label=None, state="unverified"):
    return KnowledgeNode(
        node_id=node_id,
        node_type=node_type,
        label=label or node_id,
        verification_state=state,
    )


def test_graph_persists_nodes_and_edges(tmp_path):
    store = SQLiteResearchStore(tmp_path / "graph.sqlite3")
    store.add_knowledge_node(node("claim-a", label="Wave speed depends on medium"))
    store.add_knowledge_node(node("paper-a", "source", "Primary paper"))
    store.add_knowledge_edge(KnowledgeEdge(
        "paper-a", "claim-a", "supports",
        note="The paper reports a relevant measurement.", confidence=0.6,
    ))
    graph = store.knowledge_graph()
    assert len(graph["nodes"]) == 2
    assert graph["edges"][0]["relation"] == "supports"
    assert graph["edges"][0]["confidence"] == 0.6


def test_graph_upsert_is_idempotent(tmp_path):
    store = SQLiteResearchStore(tmp_path / "upsert.sqlite3")
    store.add_knowledge_node(node("question", "question", "Open question"))
    store.add_knowledge_node(node("question", "question", "Updated question"))
    assert len(store.knowledge_graph()["nodes"]) == 1
    assert store.knowledge_graph()["nodes"][0]["label"] == "Updated question"


def test_edge_requires_existing_nodes(tmp_path):
    store = SQLiteResearchStore(tmp_path / "orphan.sqlite3")
    with pytest.raises(ValueError, match="Both edge endpoints"):
        store.add_knowledge_edge(KnowledgeEdge("missing", "also-missing", "related_to"))


def test_graph_rejects_invalid_relations_and_self_links(tmp_path):
    store = SQLiteResearchStore(tmp_path / "invalid.sqlite3")
    store.add_knowledge_node(node("a"))
    with pytest.raises(ValueError, match="self-referencing"):
        store.add_knowledge_edge(KnowledgeEdge("a", "a", "related_to"))
    with pytest.raises(ValueError, match="Unsupported relation"):
        store.add_knowledge_edge(KnowledgeEdge("a", "b", "proves"))


def test_graph_neighbors_are_directional_and_filterable(tmp_path):
    store = SQLiteResearchStore(tmp_path / "neighbors.sqlite3")
    store.add_knowledge_node(node("claim"))
    store.add_knowledge_node(node("source", "source"))
    store.add_knowledge_node(node("dataset", "dataset"))
    store.add_knowledge_edge(KnowledgeEdge("source", "claim", "supports"))
    store.add_knowledge_edge(KnowledgeEdge("dataset", "claim", "uses_dataset"))
    result = store.knowledge_neighbors("claim", relation="supports")
    assert [edge["source_id"] for edge in result["incoming"]] == ["source"]
    assert result["outgoing"] == []


def test_node_validation_state_is_not_automatically_upgraded(tmp_path):
    store = SQLiteResearchStore(tmp_path / "state.sqlite3")
    store.add_knowledge_node(node("candidate", state="candidate"))
    assert store.knowledge_graph()["nodes"][0]["verification_state"] == "candidate"
