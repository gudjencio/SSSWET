import pytest

from ssswet_core.disputes import DisputeResolutionService, detect_disputes
from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore


def _store(tmp_path):
    store = SQLiteResearchStore(tmp_path / "disputes.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "claim-a", "finding", "Wave speed is constant",
        verification_state="unverified",
        metadata={"campaign_id": "campaign-a", "source_ids": ["paper-a"]},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "claim-b", "finding", "Wave speed varies",
        verification_state="candidate",
        metadata={"campaign_id": "campaign-b", "source_ids": ["paper-b"]},
    ))
    store.add_knowledge_edge(KnowledgeEdge(
        "claim-a", "claim-b", "contradicts", "Different reported conditions", 0.8,
    ))
    return store


def test_detection_is_repeatable_and_does_not_mutate_claims(tmp_path):
    store = _store(tmp_path)
    service = DisputeResolutionService(store)
    first, second = service.detected(), service.detected()
    assert first == second
    assert first[0]["requires_human_review"] is True
    assert first[0]["scientific_conclusion"] is None
    assert store.dispute_history() == []
    states = {x["node_id"]: x["verification_state"] for x in store.knowledge_graph()["nodes"]}
    assert states == {"claim-a": "unverified", "claim-b": "candidate"}


def test_case_open_and_review_are_audited_without_changing_graph(tmp_path):
    store = _store(tmp_path)
    service = DisputeResolutionService(store)
    candidate = service.detected()[0]
    opened = service.open_case(candidate["case_id"])
    assert opened["state"] == "open"
    assert opened["source_ids"] == ("paper-a", "paper-b")
    with pytest.raises(ValueError, match="note"):
        service.review(opened["case_id"], "resolved", "", "reviewer")
    reviewed = service.review(
        opened["case_id"], "insufficient_evidence",
        "The source methods and measurement conditions cannot yet be compared.",
        "independent-reviewer",
    )
    assert reviewed["state"] == "insufficient_evidence"
    assert reviewed["reviewer"] == "independent-reviewer"
    states = {x["node_id"]: x["verification_state"] for x in store.knowledge_graph()["nodes"]}
    assert states == {"claim-a": "unverified", "claim-b": "candidate"}


def test_resolved_case_is_closed_and_duplicate_open_is_rejected(tmp_path):
    store = _store(tmp_path)
    service = DisputeResolutionService(store)
    case_id = service.detected()[0]["case_id"]
    service.open_case(case_id)
    with pytest.raises(ValueError, match="already exists"):
        service.open_case(case_id)
    service.review(case_id, "resolved", "Methods reconciled by review.", "reviewer")
    with pytest.raises(ValueError, match="closed"):
        service.review(case_id, "unresolved", "Changed view.", "reviewer")


def test_only_explicit_contradiction_edges_are_detected():
    graph = {
        "nodes": [
            {"node_id": "a", "label": "A", "metadata": {}},
            {"node_id": "b", "label": "B", "metadata": {}},
        ],
        "edges": [{"source_id": "a", "target_id": "b", "relation": "supports"}],
    }
    assert detect_disputes(graph) == []
