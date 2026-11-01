from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion
from ssswet_core.research_timeline import ResearchTimeline


def test_timeline_combines_memory_graph_and_campaign_scoped_events(tmp_path):
    store = SQLiteResearchStore(tmp_path / "timeline.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "claim-a", "finding", "Recorded finding",
        created_at="2026-10-01T10:00:00+00:00",
        metadata={"campaign_id": "campaign-a"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "claim-b", "finding", "Other finding",
        created_at="2026-10-02T10:00:00+00:00",
        metadata={"campaign_id": "campaign-b"},
    ))
    ScientificMemoryService(store).add_version(ScientificMemoryVersion.create(
        "memory-v1", "memory-a", "Wave research", "A candidate statement",
        campaign_id="campaign-a",
    ))
    all_events = ResearchTimeline(store).build()
    assert {event["kind"] for event in all_events["events"]} >= {
        "knowledge_recorded", "memory_version"
    }
    filtered = ResearchTimeline(store).build(campaign_id="campaign-a")
    assert all(event["campaign_id"] == "campaign-a" for event in filtered["events"])
    assert filtered["chronology_is_not_validation"] is True


def test_timeline_omits_records_without_grounded_timestamps(tmp_path):
    store = SQLiteResearchStore(tmp_path / "undated.sqlite3")
    store.add_knowledge_node(KnowledgeNode("undated", "finding", "No date"))
    result = ResearchTimeline(store).build()
    assert result["events"] == []
    assert result["undated_records_omitted"] is True


def test_timeline_marks_contradiction_edges_as_events_not_conclusions(tmp_path):
    store = SQLiteResearchStore(tmp_path / "edge.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "a", "finding", "A", created_at="2026-01-01T00:00:00+00:00"
    ))
    store.add_knowledge_node(KnowledgeNode(
        "b", "finding", "B", created_at="2026-01-02T00:00:00+00:00"
    ))
    store.add_knowledge_edge(KnowledgeEdge(
        "a", "b", "contradicts", note="Recorded contradiction",
        created_at="2026-01-03T00:00:00+00:00",
    ))
    result = ResearchTimeline(store).build()
    edge = next(event for event in result["events"] if event["kind"] == "relationship_recorded")
    assert edge["title"] == "contradicts"
    assert edge["scientific_validity_established"] is False
