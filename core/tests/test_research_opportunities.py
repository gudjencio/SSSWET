from ssswet_core.knowledge_graph import KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_opportunities import ResearchOpportunitySynthesizer


def test_synthesis_combines_graph_gaps_and_cross_campaign_links(tmp_path):
    store = SQLiteResearchStore(tmp_path / "opportunities.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "hypothesis-a", "hypothesis", "Wave propagation measurement",
        "Estimate wave speed from repeated observations",
        metadata={"campaign_id": "physics"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "finding-b", "finding", "Wave propagation measurement",
        "Estimate wave speed from repeated observations",
        metadata={"campaign_id": "engineering"},
    ))

    report = ResearchOpportunitySynthesizer(store).build()
    assert report["signal_counts"]["research_gaps"] >= 1
    assert report["signal_counts"]["interdisciplinary_links"] == 1
    assert any(item["kind"] == "research_gap" for item in report["opportunities"])
    link = next(item for item in report["opportunities"]
                if item["kind"] == "interdisciplinary_link")
    assert link["campaign_ids"] == ["engineering", "physics"]
    gap = next(item for item in report["opportunities"]
               if item["kind"] == "research_gap" and "hypothesis-a" in item["graph_node_ids"])
    assert link["opportunity_id"] in gap["related_opportunity_ids"]
    assert report["requires_human_review"] is True
    assert report["automatic_task_creation"] is False
    assert report["graph_mutated"] is False
    assert report["scientific_validity_established"] is False


def test_synthesis_is_stable_and_limit_is_bounded(tmp_path):
    store = SQLiteResearchStore(tmp_path / "stable-opportunities.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "question-a", "question", "How is wave speed measured?",
        metadata={"campaign_id": "physics"},
    ))
    service = ResearchOpportunitySynthesizer(store)
    first = service.build(limit=500)
    second = service.build(limit=500)
    assert [x["opportunity_id"] for x in first["opportunities"]] == [
        x["opportunity_id"] for x in second["opportunities"]
    ]
    assert service.build(limit=1)["returned"] == 1
