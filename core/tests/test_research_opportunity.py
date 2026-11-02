import pytest

from ssswet_core.research_opportunity import (
    evaluate_research_opportunity, rank_research_opportunities,
)


def graph():
    return {"relations": [
        {"state": "supported", "relation_type": "prerequisite",
         "prerequisite_id": "energy", "dependent_id": "propulsion"},
        {"state": "proposed", "relation_type": "prerequisite",
         "prerequisite_id": "energy", "dependent_id": "habitat"},
        {"state": "supported", "relation_type": "enables",
         "prerequisite_id": "energy", "dependent_id": "storage"},
    ]}


def inputs(**overrides):
    value = {
        "evidence_maturity": 4,
        "technical_feasibility": 3,
        "next_experiment_readiness": 4,
        "resource_efficiency": 3,
        "safety_legal_readiness": 5,
        "dependency_review_complete": True,
    }
    value.update(overrides)
    return value


def test_opportunity_uses_only_supported_downstream_edges():
    result = evaluate_research_opportunity("energy", inputs(), graph())
    assert result["downstream_programmes_unlocked"] == 2
    assert result["scores"]["dependency_leverage"] == 2
    assert result["rank_eligible"] is True
    assert result["automatic_funding_decisions"] is False


def test_incomplete_inputs_are_not_ranked_or_filled_with_zero():
    result = evaluate_research_opportunity(
        "energy", inputs(evidence_maturity=None), graph()
    )
    assert result["score"] is None
    assert result["scores"]["evidence_maturity"] is None
    assert "evidence_maturity" in result["missing_criteria"]


def test_unreviewed_dependency_graph_blocks_comparable_score():
    result = evaluate_research_opportunity(
        "energy", inputs(dependency_review_complete=False), None
    )
    assert result["score"] is None
    assert "dependency_leverage" in result["missing_criteria"]


def test_graph_required_when_declared_complete():
    with pytest.raises(ValueError, match="graph is required"):
        evaluate_research_opportunity("energy", inputs(), None)


def test_rank_is_deterministic_and_keeps_incomplete_visible():
    report = rank_research_opportunities([
        {"programme_id": "zeta", "inputs": inputs()},
        {"programme_id": "alpha", "inputs": inputs(evidence_maturity=5)},
        {"programme_id": "unknown", "inputs": inputs(safety_legal_readiness=None)},
    ], graph())
    assert [x["programme_id"] for x in report["ranked"]] == ["alpha", "zeta"]
    assert report["incomplete"][0]["programme_id"] == "unknown"


@pytest.mark.parametrize("value", [-1, 5.1, True, "4"])
def test_out_of_range_or_non_numeric_inputs_are_rejected(value):
    with pytest.raises(ValueError):
        evaluate_research_opportunity("energy", inputs(technical_feasibility=value), graph())


def test_duplicate_programmes_are_rejected():
    item = {"programme_id": "same", "inputs": inputs()}
    with pytest.raises(ValueError, match="unique"):
        rank_research_opportunities([item, item], graph())
