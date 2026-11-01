import pytest

from ssswet_core.simulation_study import SimulationScenario
from ssswet_core.adaptive_optimization import (
    AdaptiveScenarioOptimizer,
    ScenarioObservation,
)


def test_optimizer_excludes_observed_and_returns_only_supplied_candidates():
    candidates = [
        SimulationScenario("low", {"x": 0}),
        SimulationScenario("mid", {"x": 5}),
        SimulationScenario("high", {"x": 10}),
    ]
    report = AdaptiveScenarioOptimizer().propose(
        candidates,
        [ScenarioObservation("low", 1), ScenarioObservation("high", 9)],
        count=2,
        direction="maximize",
    )
    assert report.excluded_observed == ("high", "low")
    assert [item.scenario_id for item in report.proposals] == ["mid"]
    assert report.proposals[0].predicted_score in {1, 9}
    assert "heuristic" in report.proposals[0].rationale


def test_optimizer_prefers_exploration_when_neighbour_scores_tie():
    candidates = [
        SimulationScenario("seen-a", {"x": 0}),
        SimulationScenario("near", {"x": 1}),
        SimulationScenario("far", {"x": 10}),
    ]
    report = AdaptiveScenarioOptimizer().propose(
        candidates,
        [ScenarioObservation("seen-a", 5)],
        count=2,
    )
    assert report.proposals[0].scenario_id == "far"
    assert report.proposals[0].exploration_score > report.proposals[1].exploration_score


def test_minimize_direction_changes_objective_preference():
    candidates = [
        SimulationScenario("a", {"x": 0}),
        SimulationScenario("b", {"x": 5}),
        SimulationScenario("c", {"x": 10}),
    ]
    report = AdaptiveScenarioOptimizer().propose(
        candidates,
        [ScenarioObservation("a", 10), ScenarioObservation("c", 1)],
        count=2,
        direction="minimize",
    )
    assert report.proposals[0].predicted_score == 1


def test_candidate_parameters_are_recorded_and_stable():
    candidates = [
        SimulationScenario("observed", {"x": 1, "y": 2}),
        SimulationScenario("next", {"y": 4, "x": 3}),
    ]
    report = AdaptiveScenarioOptimizer().propose(
        candidates, [ScenarioObservation("observed", 7)]
    )
    assert report.proposals[0].parameters == {"y": 4, "x": 3}
    assert report.proposals[0].nearest_observation_id == "observed"


def test_invalid_or_ambiguous_inputs_are_rejected():
    optimizer = AdaptiveScenarioOptimizer()
    candidate = [SimulationScenario("s", {"x": 1})]
    observation = [ScenarioObservation("s", 2)]
    with pytest.raises(ValueError, match="direction"):
        optimizer.propose(candidate, observation, direction="guess")
    with pytest.raises(ValueError, match="positive"):
        optimizer.propose(candidate, observation, count=0)
    with pytest.raises(ValueError, match="finite"):
        optimizer.propose(candidate, [ScenarioObservation("s", float("nan"))])
    with pytest.raises(ValueError, match="numeric"):
        optimizer.propose(
            [SimulationScenario("s", {"label": "a"})],
            [ScenarioObservation("s", 2)],
        )
    with pytest.raises(ValueError, match="refer to a candidate"):
        optimizer.propose(
            [SimulationScenario("s", {"x": 1})],
            [ScenarioObservation("unknown", 2)],
        )
