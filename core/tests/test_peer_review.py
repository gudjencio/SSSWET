import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.knowledge_graph import KnowledgeNode
from ssswet_core.peer_review import PeerReviewService
from ssswet_core.persistence import SQLiteResearchStore


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "peer-review.sqlite3")
    for cid in ("source", "reviewer-a", "reviewer-b"):
        campaign = create_campaign(
            cid, cid, "Study wave propagation", "physics",
            [CampaignMilestone("m1", "Review", "Review evidence")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    store.add_knowledge_node(KnowledgeNode(
        "claim-1", "finding", "Candidate wave claim",
        metadata={"campaign_id": "source", "provenance_group": "source-lab"},
    ))
    return store


def test_peer_review_requires_other_campaigns_and_collects_independent_assessment(tmp_path):
    store = setup(tmp_path)
    service = PeerReviewService(store)
    case = service.request(
        "review-1", "source", "claim-1", ["reviewer-a", "reviewer-b"],
        "coordinator", "Can the reported wave method be reproduced?",
    )
    assert case["status"] == "open"
    submission = service.submit(
        "submission-1", "review-1", "reviewer-a", "supports",
        "The stated method is internally consistent with our independent analysis.",
        "Independent analytical derivation and comparison",
        source_ids=("review-paper-1",), provenance_group="reviewer-lab",
        independence_confirmed=True,
    )
    assert submission["outcome"] == "supports"
    report = service.report()
    item = report["reviews"][0]
    assert item["submission_count"] == 1
    assert item["all_reviewers_declared_independence"] is True
    assert item["independence_independently_verified"] is False
    assert item["scientific_validity_established"] is False
    assert store.knowledge_graph()["nodes"][0]["verification_state"] == "unverified"


def test_peer_review_rejects_same_campaign_or_unassigned_reviewer(tmp_path):
    store = setup(tmp_path)
    service = PeerReviewService(store)
    with pytest.raises(ValueError, match="different campaign"):
        service.request("bad", "source", "claim-1", ["source"], "operator", "Review?")
    service.request("review-1", "source", "claim-1", ["reviewer-a"], "operator", "Review?")
    with pytest.raises(ValueError, match="not assigned"):
        service.submit(
            "submission-1", "review-1", "reviewer-b", "supports", "Assessment",
            "Method", independence_confirmed=True,
        )


def test_peer_review_submission_is_append_only_and_one_per_assigned_campaign(tmp_path):
    store = setup(tmp_path)
    service = PeerReviewService(store)
    service.request("review-1", "source", "claim-1", ["reviewer-a"], "operator", "Review?")
    service.submit(
        "submission-1", "review-1", "reviewer-a", "inconclusive", "More data needed",
        "Independent literature comparison", independence_confirmed=False,
    )
    with pytest.raises(ValueError, match="already submitted"):
        service.submit(
            "submission-2", "review-1", "reviewer-a", "supports", "Second assessment",
            "Different method", independence_confirmed=True,
        )


def test_peer_review_requires_note_and_method(tmp_path):
    store = setup(tmp_path)
    service = PeerReviewService(store)
    service.request("review-1", "source", "claim-1", ["reviewer-a"], "operator", "Review?")
    with pytest.raises(ValueError, match="assessment and method"):
        service.submit(
            "submission-1", "review-1", "reviewer-a", "supports", "", "Method",
            independence_confirmed=True,
        )


def test_peer_review_synthesis_exposes_disagreement_and_shared_provenance(tmp_path):
    store = setup(tmp_path)
    service = PeerReviewService(store)
    service.request(
        "review-synthesis", "source", "claim-1",
        ["reviewer-a", "reviewer-b"], "coordinator",
        "Do independent methods support the claim?",
    )
    service.submit(
        "submission-a", "review-synthesis", "reviewer-a", "supports",
        "The derivation is plausible but needs a larger sample.",
        "Independent analytical derivation", source_ids=("shared-paper", "paper-a"),
        provenance_group="shared-lab", independence_confirmed=True,
        limitations="Small sample size",
    )
    service.submit(
        "submission-b", "review-synthesis", "reviewer-b", "challenges",
        "The derivation depends on an untested boundary condition.",
        "Independent numerical sensitivity analysis", source_ids=("shared-paper", "paper-b"),
        provenance_group="shared-lab", independence_confirmed=True,
        limitations="Boundary condition not measured",
    )
    report = service.report()
    item = report["reviews"][0]
    synthesis = item["review_synthesis"]
    assert synthesis["outcome_pattern"] == "mixed"
    assert synthesis["distinct_outcomes"] == ["challenges", "supports"]
    assert synthesis["reviewer_campaign_count"] == 2
    assert synthesis["shared_source_ids"] == ["shared-paper"]
    assert synthesis["shared_provenance_groups"] == ["shared-lab"]
    assert len(synthesis["distinct_methods"]) == 2
    assert synthesis["submissions_with_limitations"] == 2
    assert synthesis["majority_vote_used_for_adjudication"] is False
    assert item["scientific_validity_established"] is False
    assert report["automatic_adjudication"] is False
