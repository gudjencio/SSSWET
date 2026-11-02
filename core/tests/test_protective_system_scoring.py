import pytest

from ssswet_core.protective_system_scoring import (
    DIMENSIONS,
    DimensionScore,
    calculate_protective_system_score,
    rank_protective_systems,
)


def complete_dimensions(value=4.0):
    return {
        name: DimensionScore(value, (f"source:{name}",), "verified")
        for name in DIMENSIONS
    }


def complete_gates():
    return {
        "intended_use_defined": True,
        "hazards_defined": True,
        "measurable_test_plan_defined": True,
        "safety_review_complete": True,
    }


def test_complete_verified_candidate_is_rankable():
    result = calculate_protective_system_score(
        "aegis-modular",
        revision="standard-r1",
        dimensions=complete_dimensions(),
        gates=complete_gates(),
    )
    assert result.readiness == "rankable"
    assert result.weighted_score == 4.0
    assert result.reasons == ()


def test_missing_dimension_stays_unknown_and_is_not_zero():
    dimensions = complete_dimensions()
    dimensions["mobility"] = DimensionScore(None)
    result = calculate_protective_system_score(
        "bastion-impact",
        revision="r1",
        dimensions=dimensions,
        gates=complete_gates(),
    )
    assert result.weighted_score is None
    assert result.readiness == "not_ready"
    assert "missing dimensions: mobility" in result.reasons


def test_missing_safety_gate_blocks_ranking():
    gates = complete_gates()
    gates["safety_review_complete"] = False
    result = calculate_protective_system_score(
        "atlas-assist",
        revision="active-r1",
        dimensions=complete_dimensions(),
        gates=gates,
    )
    assert result.weighted_score is None
    assert result.readiness == "not_ready"
    assert any("safety_review_complete" in reason for reason in result.reasons)


def test_observed_and_verified_scores_require_sources():
    dimensions = complete_dimensions()
    dimensions["safety"] = DimensionScore(4.5, (), "verified")
    with pytest.raises(ValueError):
        calculate_protective_system_score(
            "lifeline-rescue",
            revision="compact-r1",
            dimensions=dimensions,
            gates=complete_gates(),
        )


def test_out_of_range_score_is_rejected():
    with pytest.raises(ValueError):
        DimensionScore(5.1, ("source:test",), "verified")


def test_ranking_excludes_not_ready_candidates():
    first = calculate_protective_system_score(
        "aegis-modular",
        revision="r1",
        dimensions=complete_dimensions(4.2),
        gates=complete_gates(),
    )
    second = calculate_protective_system_score(
        "guardian-monitor",
        revision="r1",
        dimensions=complete_dimensions(4.7),
        gates=complete_gates(),
    )
    blocked_gates = complete_gates()
    blocked_gates["measurable_test_plan_defined"] = False
    blocked = calculate_protective_system_score(
        "sentinel-environment",
        revision="r1",
        dimensions=complete_dimensions(5.0),
        gates=blocked_gates,
    )

    ranked = rank_protective_systems([first, blocked, second])
    assert [item.system_id for item in ranked] == ["guardian-monitor", "aegis-modular"]
    assert blocked not in ranked
