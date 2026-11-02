import pytest
from ssswet_core.review_assignment import IndependentReviewerSelector, ReviewerCandidate

def test_selector_excludes_prior_reviewers_lead_and_conflicted_candidates():
    candidates = [
        ReviewerCandidate("lead", "general_researcher", "c1"),
        ReviewerCandidate("prior", "independent_verifier", "c2"),
        ReviewerCandidate("conflicted", "data_analyst", "c3", "potential"),
        ReviewerCandidate("fresh-a", "independent_verifier", "c4"),
        ReviewerCandidate("fresh-b", "ethics_reviewer", "c5"),
    ]
    result = IndependentReviewerSelector().propose(
        candidates, lead_researcher_id="lead", excluded_reviewer_ids={"prior"}, required_count=2,
    )
    assert result["status"] == "proposed"
    assert [item["agent_id"] for item in result["selected_reviewers"]] == ["fresh-a", "fresh-b"]
    assert {item["reason"] for item in result["excluded_candidates"]} >= {
        "prior_reviewer_or_lead_researcher", "conflict_not_cleared"
    }

def test_selector_requires_distinct_campaigns_and_reports_shortfall():
    candidates = [
        ReviewerCandidate("a", "independent_verifier", "campaign-x"),
        ReviewerCandidate("b", "data_analyst", "campaign-x"),
    ]
    result = IndependentReviewerSelector().propose(candidates, required_count=2)
    assert result["status"] == "insufficient_independent_candidates"
    assert result["selected_count"] == 1
    assert result["excluded_candidates"][0]["reason"] == "campaign_already_represented"

def test_shared_sources_are_disclosed_not_silently_hidden():
    candidates = [
        ReviewerCandidate("a", "independent_verifier", "x", source_refs=("source-1", "source-2")),
        ReviewerCandidate("b", "data_analyst", "y", source_refs=("source-3",)),
    ]
    result = IndependentReviewerSelector().propose(candidates, prior_source_refs={"source-1"}, required_count=2)
    assert result["shared_sources_must_be_disclosed"] is True
    assert result["selected_reviewers"][0]["shared_source_refs_to_disclose"] == ["source-1"]

def test_selector_validates_candidate_and_count():
    with pytest.raises(ValueError, match="required_count"):
        IndependentReviewerSelector().propose([], required_count=0)
    with pytest.raises(ValueError, match="ReviewerCandidate"):
        IndependentReviewerSelector().propose([{"agent_id": "a"}])

def test_conflict_confirmation_is_required_to_be_clear():
    result = IndependentReviewerSelector().propose([
        ReviewerCandidate("a", "independent_verifier", "a", "confirmed"),
    ], required_count=1)
    assert result["selected_count"] == 0
    assert result["independence_certified"] is False
