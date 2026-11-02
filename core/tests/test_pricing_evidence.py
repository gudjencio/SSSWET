import pytest

from ssswet_core.provisional_pricing import REQUIRED_COST_CATEGORIES
from ssswet_core.pricing_evidence import build_agent_pricing_estimate
from ssswet_core.engine import SSSWETEngine


def _submissions():
    roles = [
        "general_researcher", "systems_engineer", "materials_scientist",
        "data_analyst", "medical_researcher", "futures_analyst",
        "ethics_reviewer", "systems_engineer", "general_researcher",
    ]
    return [
        {
            "submission_id": f"cost-{index}",
            "agent_id": f"agent-{index}",
            "agent_role": roles[index],
            "category": category,
            "low": "10",
            "base": "20",
            "high": "30",
            "source_ref": f"source:{category}",
            "source_verified": True,
        }
        for index, category in enumerate(REQUIRED_COST_CATEGORIES)
    ]


def _review():
    return {
        "estimate_id": "estimate-001",
        "reviewer_agent_id": "elias",
        "reviewer_role": "independent_verifier",
        "approved": True,
        "review_reference": "review:estimate-001",
    }


def _build(**overrides):
    args = {
        "estimate_id": "estimate-001",
        "submissions": _submissions(),
        "independent_review": _review(),
        "currency": "EUR",
        "uncertainty_rate": "0.05",
        "tax_rate": "0.20",
        "confidence": "0.90",
    }
    args.update(overrides)
    return build_agent_pricing_estimate(**args)


def test_agent_evidence_is_aggregated_and_separate_reviewer_can_approve():
    result = _build()
    assert result["publishable"] is True
    assert result["agent_submission_count"] == 9
    assert result["independent_review_status"] == "independent_review_approved"
    assert result["cost_subtotals"]["base"] == "180.00"
    assert result["commercial_offer_authorized"] is False


def test_agent_submissions_alone_never_satisfy_independent_review():
    result = _build(independent_review=None)
    assert result["publishable"] is False
    assert result["independent_review_status"] == "independent_review_missing"


def test_reviewer_cannot_review_their_own_cost_submission():
    review = _review()
    review["reviewer_agent_id"] = "agent-0"
    result = _build(independent_review=review)
    assert result["publishable"] is False
    assert result["independent_review_status"] == "reviewer_also_authored_cost_submission"


def test_review_must_target_exact_estimate():
    review = _review()
    review["estimate_id"] = "different-estimate"
    result = _build(independent_review=review)
    assert result["publishable"] is False
    assert result["independent_review_status"] == "review_targets_different_estimate"


def test_unverified_agent_source_withholds_publication():
    submissions = _submissions()
    submissions[0]["source_verified"] = False
    result = _build(submissions=submissions)
    assert result["publishable"] is False
    assert result["source_evidence_complete"] is False


def test_unknown_agent_role_is_rejected():
    submissions = _submissions()
    submissions[0]["agent_role"] = "unregistered_role"
    with pytest.raises(ValueError, match="known agent role"):
        _build(submissions=submissions)


def test_independent_verifier_cannot_submit_costs():
    submissions = _submissions()
    submissions[0]["agent_role"] = "independent_verifier"
    with pytest.raises(ValueError, match="cannot submit"):
        _build(submissions=submissions)


def test_duplicate_submission_ids_are_rejected():
    submissions = _submissions()
    submissions[1]["submission_id"] = submissions[0]["submission_id"]
    with pytest.raises(ValueError, match="unique"):
        _build(submissions=submissions)


def test_missing_category_is_not_filled_with_an_invented_zero():
    submissions = _submissions()[:-1]
    result = _build(submissions=submissions)
    assert result["publishable"] is False
    assert "fulfilment" in result["missing_categories"]


def test_estimate_must_have_unique_id():
    with pytest.raises(ValueError, match="estimate_id"):
        _build(estimate_id="")

def test_research_engine_exposes_the_agent_pricing_workflow():
    engine = SSSWETEngine()
    result = engine.estimate_technology_costs(
        estimate_id="estimate-001",
        submissions=_submissions(),
        independent_review=_review(),
        currency="EUR",
        uncertainty_rate="0.05",
        tax_rate="0.20",
        confidence="0.90",
    )
    assert result["publishable"] is True
    assert result["estimate_id"] == "estimate-001"
