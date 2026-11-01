import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.knowledge_graph import KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_relations import ResearchRelationDiscovery


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "relations.sqlite3")
    for campaign_id in ("physics", "biology"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Interdisciplinary research",
            "research", [CampaignMilestone("m1", "Review", "Review links")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    return store


def test_discovers_explainable_cross_campaign_overlap_without_mutation(tmp_path):
    store = setup(tmp_path)
    store.add_knowledge_node(KnowledgeNode(
        "n1", "hypothesis", "wave propagation", "acoustic wave propagation in fluid",
        metadata={"campaign_id": "physics", "domain": "physics"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "n2", "finding", "fluid wave response", "fluid response to acoustic wave propagation",
        metadata={"campaign_id": "biology", "domain": "biology"},
    ))
    before = store.knowledge_graph()
    report = ResearchRelationDiscovery(store).discover()
    after = store.knowledge_graph()
    assert report["suggestion_count"] == 1
    item = report["suggestions"][0]
    assert "wave" in item["shared_terms"]
    assert item["requires_human_review"] is True
    assert item["graph_edge_created"] is False
    assert report["scientific_validity_established"] is False
    assert before == after


def test_does_not_suggest_same_campaign_or_existing_relationship(tmp_path):
    store = setup(tmp_path)
    store.add_knowledge_node(KnowledgeNode(
        "n1", "concept", "wave propagation", metadata={"campaign_id": "physics"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "n2", "concept", "wave propagation", metadata={"campaign_id": "physics"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "n3", "concept", "wave propagation", metadata={"campaign_id": "biology"},
    ))
    from ssswet_core.knowledge_graph import KnowledgeEdge
    store.add_knowledge_edge(KnowledgeEdge("n1", "n3", "related_to"))
    report = ResearchRelationDiscovery(store).discover()
    pairs = {(item["source_node_id"], item["target_node_id"]) for item in report["suggestions"]}
    assert ("n1", "n2") not in pairs
    assert ("n1", "n3") not in pairs
    assert ("n2", "n3") in pairs


def test_discovery_is_deterministic_and_bounded(tmp_path):
    store = setup(tmp_path)
    for i, campaign in enumerate(("physics", "biology", "chemistry")):
        store.add_knowledge_node(KnowledgeNode(
            f"n{i}", "concept", "shared wave propagation method",
            metadata={"campaign_id": campaign},
        ))
    service = ResearchRelationDiscovery(store)
    assert service.discover(limit=1) == service.discover(limit=1)
    assert len(service.discover(limit=1)["suggestions"]) == 1
