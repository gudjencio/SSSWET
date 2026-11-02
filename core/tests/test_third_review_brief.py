import pytest

from ssswet_core.evidence_dossiers import EvidenceDossierService
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.scientific_review_board import ScientificReviewBoard
from ssswet_core.third_review_brief import ThirdReviewBriefService


def _dossier(store):
    return EvidenceDossierService(store).assemble(
        "dossier-third-look",
        "A provisional materials result",
        "A reported change in a material property requires independent assessment.",
    )


def _review(board, reviewer, verdict, refs, campaign="campaign-" ):
    return board.submit(
        dossier_id="dossier-third-look",
        reviewer_id=reviewer,
        reviewer_campaign_id=campaign + reviewer,
        verdict=verdict,
        conflict_status="none_declared",
        rationale=f"{reviewer} assessment with evidence-linked reasoning.",
        methods_assessment="Methods and measurement conditions require comparison.",
        limitations="The available record does not establish real-world performance.",
        evidence_refs=refs,
    )


def test_third_review_brief_recommends_independent_review_on_disagreement(tmp_path):
    store = SQLiteResearchStore(tmp_path / "third-review.sqlite3")
    _dossier(store)
    board = ScientificReviewBoard(store)
    _review(board, "reviewer-a", "supports", ["source-1", "source-2"])
    _review(board, "reviewer-b", "challenges", ["source-2", "source-3"])

    brief = ThirdReviewBriefService(store).build("dossier-third-look")

    assert brief["ready_for_third_review"] is True
    assert brief["third_review_status"] == "recommended_due_to_disagreement"
    assert brief["prior_verdict_counts"] == {"challenges": 1, "supports": 1}
    assert brief["prior_reviewers_to_exclude"] == ["reviewer-a", "reviewer-b"]
    assert brief["shared_evidence_refs"] == ["source-2"]
    assert brief["majority_vote_used"] is False
    assert brief["scientific_validity_established"] is False
    assert len(brief["third_reviewer_instructions"]) >= 8


def test_third_review_brief_marks_one_review_as_not_ready(tmp_path):
    store = SQLiteResearchStore(tmp_path / "third-review-not-ready.sqlite3")
    _dossier(store)
    board = ScientificReviewBoard(store)
    _review(board, "reviewer-a", "supports", ["source-1"])

    brief = ThirdReviewBriefService(store).build("dossier-third-look")

    assert brief["ready_for_third_review"] is False
    assert brief["third_review_status"] == "not_ready_fewer_than_two_prior_reviews"
    assert brief["automatic_reviewer_assignment"] is False


def test_third_review_brief_rejects_unknown_dossier(tmp_path):
    store = SQLiteResearchStore(tmp_path / "third-review-unknown.sqlite3")
    with pytest.raises(ValueError, match="unknown evidence dossier"):
        ThirdReviewBriefService(store).build("missing")


def test_third_review_brief_requires_dossier_id(tmp_path):
    store = SQLiteResearchStore(tmp_path / "third-review-empty.sqlite3")
    with pytest.raises(ValueError, match="dossier_id is required"):
        ThirdReviewBriefService(store).build(" ")
