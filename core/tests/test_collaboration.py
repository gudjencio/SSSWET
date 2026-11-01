import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign
from ssswet_core.collaboration import create_transfer, decide_transfer
from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore


def setup_store(tmp_path):
    store = SQLiteResearchStore(tmp_path / "collaboration.sqlite3")
    for campaign_id in ("campaign-a", "campaign-b"):
        store.save_campaign(create_campaign(
            campaign_id, campaign_id, "Research objective", "physics",
            [CampaignMilestone("m1", "Review", "Review evidence")],
        ))
    store.add_knowledge_node(KnowledgeNode(
        "finding-a", "finding", "A candidate finding",
        verification_state="unverified",
        metadata={"campaign_id": "campaign-a"},
    ))
    return store


def test_transfer_requires_existing_campaigns_and_knowledge_node(tmp_path):
    store = setup_store(tmp_path)
    transfer = create_transfer("transfer-1", "campaign-a", "campaign-b", "finding-a", "researcher")
    store.create_knowledge_transfer(transfer)
    saved = store.knowledge_transfer_history()
    assert saved[0]["state"] == "pending"
    with pytest.raises(ValueError, match="Unknown campaign"):
        store.create_knowledge_transfer(create_transfer(
            "transfer-2", "missing", "campaign-b", "finding-a", "researcher"
        ))
    with pytest.raises(ValueError, match="Unknown knowledge node"):
        store.create_knowledge_transfer(create_transfer(
            "transfer-3", "campaign-a", "campaign-b", "missing", "researcher"
        ))


def test_transfer_decision_is_audited_and_does_not_upgrade_claim(tmp_path):
    store = setup_store(tmp_path)
    transfer = create_transfer("transfer-1", "campaign-a", "campaign-b", "finding-a", "researcher")
    store.create_knowledge_transfer(transfer)
    accepted = decide_transfer(transfer, "accepted", "Recipient agrees to review.")
    store.decide_knowledge_transfer(accepted)
    assert store.knowledge_transfer_history("campaign-b")[0]["decision_note"] == "Recipient agrees to review."
    assert store.knowledge_graph()["nodes"][0]["verification_state"] == "unverified"
    with pytest.raises(ValueError, match="Only pending"):
        store.decide_knowledge_transfer(decide_transfer(accepted, "rejected"))


def test_transfer_rejection_is_preserved(tmp_path):
    store = setup_store(tmp_path)
    transfer = create_transfer("transfer-1", "campaign-a", "campaign-b", "finding-a", "researcher")
    store.create_knowledge_transfer(transfer)
    rejected = decide_transfer(transfer, "rejected", "Insufficient supporting material.")
    store.decide_knowledge_transfer(rejected)
    assert store.knowledge_transfer_history()[0]["state"] == "rejected"


def test_campaign_conflict_report_finds_explicit_cross_campaign_contradiction(tmp_path):
    store = setup_store(tmp_path)
    store.add_knowledge_node(KnowledgeNode(
        "finding-b", "finding", "A conflicting candidate",
        verification_state="unverified",
        metadata={"campaign_id": "campaign-b"},
    ))
    store.add_knowledge_edge(KnowledgeEdge(
        "finding-a", "finding-b", "contradicts",
        note="Reported measurements differ.", confidence=0.5,
    ))
    report = store.campaign_conflict_report("campaign-a")
    assert report["count"] == 1
    assert report["contradictions"][0]["requires_human_review"] is True
    assert "not adjudicated" in report["warning"]


def test_same_campaign_transfer_is_rejected():
    with pytest.raises(ValueError, match="different campaigns"):
        create_transfer("transfer-1", "campaign-a", "campaign-a", "finding-a", "researcher")
