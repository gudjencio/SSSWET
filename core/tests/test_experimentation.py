import pytest

from ssswet_core.experimentation import (
    compare_record_to_prediction,
    draft_experiment_plan,
    make_experiment_record,
    validate_experiment_plan,
)


def test_hypothesis_generates_incomplete_honest_plan():
    plan = draft_experiment_plan("exp-1", "hyp-1", "Material X expands when heated")
    missing = validate_experiment_plan(plan)
    assert plan.state == "draft"
    assert "independent_variables" in missing
    assert "falsification_criteria" in missing
    assert "RESEARCHER INPUT REQUIRED" in plan.prediction


def test_ready_plan_has_no_missing_required_fields():
    plan = draft_experiment_plan("exp-2", "hyp-2", "A predicts B")
    from dataclasses import replace
    complete = replace(
        plan,
        prediction="B increases when A increases",
        independent_variables=("A",),
        dependent_variables=("B",),
        controlled_variables=("temperature",),
        protocol=("Measure baseline", "Vary A", "Record B"),
        controls_and_baselines=("Baseline condition",),
        falsification_criteria=("B does not change across repeated trials",),
        missing_information=(),
        state="ready_for_review",
    )
    assert validate_experiment_plan(complete) == []


def test_simulation_and_real_observation_are_distinct():
    simulated = make_experiment_record("sim-1", "exp-1", "simulation", {"y": 4}, "model v1")
    observed = make_experiment_record("obs-1", "exp-1", "real_observation", {"y": 4}, "lab protocol v1")
    assert simulated.kind == "simulation"
    assert observed.kind == "real_observation"


def test_comparison_is_explicit_and_never_declares_hypothesis_true():
    record = make_experiment_record("sim-2", "exp-2", "simulation", {"temperature": 22.1}, "toy model")
    result = compare_record_to_prediction(record, "temperature", 22.0, tolerance=0.2)
    assert result.state == "consistent_with_prediction"
    assert result.requires_human_review is True
    assert "does not establish or refute" in result.explanation


def test_missing_observation_is_inconclusive():
    record = make_experiment_record("obs-2", "exp-3", "real_observation", {}, "instrument log")
    result = compare_record_to_prediction(record, "x", 3)
    assert result.state == "inconclusive"


def test_rejects_unsupported_execution_kind_and_negative_tolerance():
    with pytest.raises(ValueError, match="Unsupported execution kind"):
        make_experiment_record("x", "e", "imaginary", {}, "method")
    record = make_experiment_record("r", "e", "simulation", {"x": 1}, "model")
    with pytest.raises(ValueError, match="non-negative"):
        compare_record_to_prediction(record, "x", 1, tolerance=-1)
