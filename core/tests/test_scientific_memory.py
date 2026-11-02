import pytest

from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion
from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore


def test_scientific_memory_keeps_immutable_versions_and_marks_current(tmp_path):
    store = SQLiteResearchStore(tmp_path / "scientific.sqlite3")
    service = ScientificMemoryService(store)
    first = ScientificMemoryVersion.create(
        "v1", "wave-speed", "Wave speed", "Initial candidate estimate",
        source_ids=("paper-1",), status="candidate",
    )
    service.add_version(first)
    second = service.revise(
        "v1", "v2", statement="Revised estimate after method review",
        status="reviewed", review_note="Updated after checking the method section.",
    )
    assert second["version_number"] == 2
    overview = service.overview()
    by_id = {item["version_id"]: item for item in overview["versions"]}
    assert by_id["v1"]["is_current"] is False
    assert by_id["v1"]["statement"] == "Initial candidate estimate"
    assert by_id["v2"]["is_current"] is True
    assert by_id["v2"]["supersedes_version_id"] == "v1"
    assert by_id["v2"]["scientific_validity_established"] is False


def test_supersession_requires_note_and_current_parent(tmp_path):
    store = SQLiteResearchStore(tmp_path / "parent.sqlite3")
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "topic", "Topic", "First statement"
    ))
    with pytest.raises(ValueError, match="review note"):
        ScientificMemoryVersion.create(
            "v2", "topic", "Topic", "Second statement",
            supersedes_version_id="v1",
        )
    service.revise("v1", "v2", review_note="Explicit revision.")
    with pytest.raises(ValueError, match="current version"):
        service.revise("v1", "v3", review_note="Stale parent rejected.")


def test_graph_contradiction_marks_linked_memory_contested_without_adjudication(tmp_path):
    store = SQLiteResearchStore(tmp_path / "contested.sqlite3")
    store.add_knowledge_node(KnowledgeNode("claim-a", "finding", "Claim A"))
    store.add_knowledge_node(KnowledgeNode("claim-b", "finding", "Claim B"))
    store.add_knowledge_edge(KnowledgeEdge("claim-a", "claim-b", "contradicts"))
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "claims", "Claims", "A linked research note",
        graph_node_ids=("claim-a",),
    ))
    result = service.overview()["versions"][0]
    assert result["contested_by_graph"] is True
    assert result["contested_graph_node_ids"] == ["claim-a"]
    assert result["status"] == "candidate"
    assert result["scientific_validity_established"] is False


def test_scientific_memory_lexical_search_is_explainable(tmp_path):
    store = SQLiteResearchStore(tmp_path / "search.sqlite3")
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "wave", "Wave propagation", "Repeated wave-speed observations"
    ))
    result = service.overview(query="wave speed")
    assert result["versions"][0]["retrieval_method"] == "lexical_overlap"
    assert result["versions"][0]["matched_terms"] == ["speed", "wave"]
    assert result["scientific_validity_established"] is False


def test_lineage_returns_complete_immutable_chain_for_selected_version(tmp_path):
    store = SQLiteResearchStore(tmp_path / "lineage.sqlite3")
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "relativity", "Relativity", "Initial hypothesis",
        source_ids=("source-a",),
    ))
    service.revise(
        "v1", "v2", statement="Hypothesis narrowed after review",
        status="contested", review_note="A counterexample requires qualification.",
    )
    service.revise(
        "v2", "v3", statement="Revised hypothesis with explicit limits",
        status="candidate", review_note="Scope narrowed to match the available evidence.",
    )

    lineage = service.lineage("v2")
    assert lineage is not None
    assert lineage["predecessors"][0]["version_id"] == "v1"
    assert lineage["selected_version"]["statement"] == "Hypothesis narrowed after review"
    assert lineage["successors"][0]["version_id"] == "v3"
    assert lineage["current_version_id"] == "v3"
    assert lineage["is_current"] is False
    assert lineage["version_count"] == 3
    assert lineage["revision_chain_is_complete"] is True
    assert lineage["scientific_validity_established"] is False


def test_lineage_returns_none_for_unknown_version(tmp_path):
    store = SQLiteResearchStore(tmp_path / "missing-lineage.sqlite3")
    assert ScientificMemoryService(store).lineage("unknown") is None



def test_overview_reports_broken_evidence_links_without_promoting_claims(tmp_path):
    store = SQLiteResearchStore(tmp_path / "integrity.sqlite3")
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "linked-claim", "Linked claim", "A statement with incomplete references",
        source_ids=("source-present", "source-missing"),
        experiment_ids=("experiment-missing",),
        graph_node_ids=("node-present", "node-missing"),
    ))
    store.add_knowledge_node(KnowledgeNode("node-present", "finding", "Existing node"))

    result = service.overview()
    item = result["versions"][0]
    assert item["has_missing_links"] is True
    assert item["missing_links"] == {
        "source_ids": ["source-missing", "source-present"],
        "experiment_ids": ["experiment-missing"],
        "graph_node_ids": ["node-missing"],
    }
    assert result["versions_with_missing_links"] == 1
    assert result["scientific_validity_established"] is False


def test_evolution_alert_flags_only_current_memory_challenged_by_later_record(tmp_path):
    store = SQLiteResearchStore(tmp_path / "evolution-alerts.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "hypothesis-node", "hypothesis", "Initial hypothesis",
        created_at="2026-01-01T00:00:00+00:00",
    ))
    store.add_knowledge_node(KnowledgeNode(
        "later-finding", "finding", "Later contradictory finding",
        created_at="2026-02-01T00:00:00+00:00",
    ))
    store.add_knowledge_edge(KnowledgeEdge(
        "hypothesis-node", "later-finding", "contradicts",
        note="A later observation challenges the earlier model.",
        confidence=0.7,
        created_at="2026-02-01T00:00:00+00:00",
    ))
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "memory-v1", "hypothesis-key", "Initial model",
        "The initial model explains the observations.",
        graph_node_ids=("hypothesis-node",),
    ))
    result = service.evolution_alerts()
    assert result["alert_count"] == 1
    alert = result["alerts"][0]
    assert alert["version_id"] == "memory-v1"
    assert alert["later_contradicting_node_id"] == "later-finding"
    assert alert["automatic_status_change"] is False
    assert result["scientific_validity_established"] is False


def test_evolution_alert_ignores_older_or_unlinked_contradictions(tmp_path):
    store = SQLiteResearchStore(tmp_path / "evolution-alerts-filter.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "hypothesis-node", "hypothesis", "Hypothesis",
        created_at="2026-03-01T00:00:00+00:00",
    ))
    store.add_knowledge_node(KnowledgeNode(
        "older-finding", "finding", "Older finding",
        created_at="2026-02-01T00:00:00+00:00",
    ))
    store.add_knowledge_edge(KnowledgeEdge("hypothesis-node", "older-finding", "contradicts"))
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "v1", "key", "Topic", "Statement", graph_node_ids=("hypothesis-node",),
    ))
    assert service.evolution_alerts()["alerts"] == []
