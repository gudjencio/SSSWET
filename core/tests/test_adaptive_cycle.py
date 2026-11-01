import pytest

from ssswet_core.adaptive_cycle import propose_from_study
from ssswet_core.simulation_study import (
    MultiModelSimulationRunner,
    SimulationScenario,
)


def _study():
    return MultiModelSimulationRunner().run(
        "study-cycle",
        "Compare toy functions",
        [
            SimulationScenario("s0", {"x": 0}),
            SimulationScenario("s1", {"x": 5}),
            SimulationScenario("s2", {"x": 10}),
        ],
        {
            "model-a": ("local-a", lambda p: {"score": p["x"]}),
            "model-b": ("local-b", lambda p: {"score": p["x"] + 1}),
        },
    )


def test_adaptive_cycle_requires_human_scores_and_completed_model_runs():
    study = _study()
    candidates = [
        SimulationScenario("s0", {"x": 0}),
        SimulationScenario("s1", {"x": 5}),
        SimulationScenario("s2", {"x": 10}),
    ]
    cycle = propose_from_study(
        study, candidates, {"s0": 0.5, "s1": 5.5}, count=2
    )
    assert cycle.study_id == "study-cycle"
    assert cycle.reviewed_scenario_ids == ("s0", "s1")
    assert all(item.scenario_id not in {"s0", "s1"} for item in cycle.report.proposals)


def test_adaptive_cycle_rejects_scores_without_two_successful_runs():
    study = _study()
    broken = type(study)(
        study.study_id, study.objective,
        tuple(run for run in study.runs if not (
            run.scenario_id == "s0" and run.model_id == "model-b"
        )),
        study.scenario_agreement, study.warnings,
    )
    with pytest.raises(ValueError, match="two completed"):
        propose_from_study(
            broken,
            [SimulationScenario("s0", {"x": 0}), SimulationScenario("s1", {"x": 5})],
            {"s0": 0.2},
        )


def test_adaptive_cycle_is_proposal_only():
    from ssswet_core.adaptive_cycle import adaptive_cycle_to_dict
    cycle = propose_from_study(
        _study(),
        [
            SimulationScenario("s0", {"x": 0}),
            SimulationScenario("s1", {"x": 5}),
            SimulationScenario("s2", {"x": 10}),
        ],
        {"s0": 1.0},
    )
    payload = adaptive_cycle_to_dict(cycle)
    assert payload["execution_state"] == "proposal_only"
    assert payload["requires_human_approval_before_execution"] is True
