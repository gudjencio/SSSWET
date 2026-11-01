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


def test_timeline_uses_database_recording_timestamp_when_node_date_is_omitted(tmp_path):
    store = SQLiteResearchStore(tmp_path / "undated.sqlite3")
    store.add_knowledge_node(KnowledgeNode("undated", "finding", "No supplied date"))
    result = ResearchTimeline(store).build()
    assert len(result["events"]) == 1
    assert result["events"][0]["event_id"] == "graph-node:undated"
    assert result["events"][0]["occurred_at"]
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


def test_timeline_includes_experiment_plan_and_record_database_timestamps(tmp_path):
    from ssswet_core.experimentation import draft_experiment_plan, make_experiment_record

    store = SQLiteResearchStore(tmp_path / "experiment-timeline.sqlite3")
    plan = draft_experiment_plan("experiment-1", "hypothesis-1", "A testable hypothesis")
    store.save_experiment_plan(plan)
    record = make_experiment_record(
        "record-1", "experiment-1", "simulation",
        {"output": 3}, "A documented simulation method",
    )
    store.save_experiment_record(record)
    result = ResearchTimeline(store).build()
    kinds = {event["kind"] for event in result["events"]}
    assert "experiment_plan_updated" in kinds
    assert "experiment_recorded" in kinds
    recorded = next(event for event in result["events"] if event["kind"] == "experiment_recorded")
    assert recorded["references"]["execution_kind"] == "simulation"
    assert recorded["scientific_validity_established"] is False


def test_timeline_includes_peer_review_request_and_submission(tmp_path):
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.peer_review import PeerReviewService

    store = SQLiteResearchStore(tmp_path / "peer-review-timeline.sqlite3")
    for cid in ("source", "reviewer"):
        campaign = create_campaign(
            cid, cid, "Review a research claim", "physics",
            [CampaignMilestone("m1", "Review", "Assess evidence")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    store.add_knowledge_node(KnowledgeNode(
        "claim", "finding", "Candidate claim",
        metadata={"campaign_id": "source"},
    ))
    service = PeerReviewService(store)
    service.request("review-1", "source", "claim", ["reviewer"], "operator", "Can it be reproduced?")
    service.submit(
        "submission-1", "review-1", "reviewer", "inconclusive",
        "Insufficient information.", "Independent method review",
        independence_confirmed=False,
    )
    events = ResearchTimeline(store).build()["events"]
    kinds = {event["kind"] for event in events}
    assert "peer_review_requested" in kinds
    assert "peer_review_submitted" in kinds
