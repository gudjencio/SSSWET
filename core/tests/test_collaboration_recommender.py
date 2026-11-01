from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.collaboration_recommender import CollaborationRecommender
from ssswet_core.knowledge_graph import KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore


def _active(store, cid, title, objective, domain="physics"):
    campaign = create_campaign(
        cid, title, objective, domain,
        [CampaignMilestone("m1", "Review", objective)],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))


def test_recommender_suggests_relevant_target_without_creating_transfer(tmp_path):
    store = SQLiteResearchStore(tmp_path / "recommend.sqlite3")
    _active(store, "source", "Wave study", "Study wave propagation", "physics")
    _active(store, "target", "Wave measurement", "Develop wave propagation measurement methods", "engineering")
    _active(store, "unrelated", "Botany", "Study plant pollination", "biology")
    store.add_knowledge_node(KnowledgeNode(
        "wave-finding", "finding", "Wave propagation measurements",
        "Methods for measuring wave propagation",
        verification_state="unverified",
        metadata={"campaign_id": "source"},
    ))

    recommendations = CollaborationRecommender(store).recommend()
    assert len(recommendations) == 1
    item = recommendations[0]
    assert item.source_campaign_id == "source"
    assert item.target_campaign_id == "target"
    assert "wave" in item.matched_terms
    assert item.verification_state == "unverified"
    assert item.requires_human_review is True
    assert item.transfer_created is False
    assert store.knowledge_transfer_history() == []


def test_transfer_is_created_only_after_explicit_request(tmp_path):
    store = SQLiteResearchStore(tmp_path / "explicit-transfer.sqlite3")
    _active(store, "source", "Wave study", "Study wave propagation")
    _active(store, "target", "Wave measurement", "Measure wave propagation")
    store.add_knowledge_node(KnowledgeNode(
        "wave-finding", "finding", "Wave propagation methods",
        metadata={"campaign_id": "source"},
    ))
    recommender = CollaborationRecommender(store)
    item = recommender.recommend()[0]
    transfer = recommender.create_transfer(item.recommendation_id, "research-operator")
    assert transfer["state"] == "pending"
    assert transfer["requested_by"] == "research-operator"
    assert store.knowledge_transfer_history()[0]["node_id"] == "wave-finding"
    assert store.knowledge_graph()["nodes"][0]["verification_state"] == "unverified"


def test_recommendations_skip_paused_campaigns_and_pending_transfers(tmp_path):
    store = SQLiteResearchStore(tmp_path / "eligibility.sqlite3")
    _active(store, "source", "Wave study", "Study wave propagation")
    _active(store, "target", "Wave measurement", "Measure wave propagation")
    store.add_knowledge_node(KnowledgeNode(
        "wave-finding", "finding", "Wave propagation methods",
        metadata={"campaign_id": "source"},
    ))
    recommender = CollaborationRecommender(store)
    item = recommender.recommend()[0]
    recommender.create_transfer(item.recommendation_id, "operator")
    assert recommender.recommend() == []
    campaign = next(x for x in store.campaign_history() if x["campaign_id"] == "target")
    from ssswet_core.campaigns import set_campaign_state
    from dataclasses import fields
    # Transition the target to paused through its persisted dataclass representation.
    from ssswet_core.campaigns import ResearchCampaign, CampaignMilestone
    milestones = tuple(CampaignMilestone(**m) for m in campaign["milestones"])
    paused = set_campaign_state(
        ResearchCampaign(campaign["campaign_id"], campaign["title"], campaign["objective"],
                         campaign["domain"], campaign["state"], milestones),
        "paused",
    )
    store.save_campaign(paused)
    assert recommender.recommend() == []
