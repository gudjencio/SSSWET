import pytest

from ssswet_core.simulation_study import (
    MultiModelSimulationRunner,
    SimulationScenario,
)


def test_models_receive_same_explicit_parameters_and_are_compared():
    seen = []
    scenarios = [SimulationScenario("baseline", {"speed": 2, "mass": 3})]

    def model_a(parameters):
        seen.append(("a", parameters))
        return {"energy": parameters["speed"] * parameters["mass"]}

    def model_b(parameters):
        seen.append(("b", parameters))
        return {"energy": parameters["mass"] * parameters["speed"]}

    result = MultiModelSimulationRunner().run(
        "study-1", "Compare two illustrative models", scenarios,
        {"a": ("local-a", model_a), "b": ("local-b", model_b)},
    )

    assert result.scenario_agreement == {"baseline": "identical_outputs"}
    assert len(result.runs) == 2
    assert all(run.status == "completed" for run in result.runs)
    assert seen == [
        ("a", {"speed": 2, "mass": 3}),
        ("b", {"speed": 2, "mass": 3}),
    ]
    assert any("not real-world observations" in warning for warning in result.warnings)


def test_parameter_variants_are_recorded_separately():
    runner = MultiModelSimulationRunner()
    result = runner.run(
        "study-2", "Inspect sensitivity",
        [
            SimulationScenario("low", {"input": 1}),
            SimulationScenario("high", {"input": 10}),
        ],
        {
            "a": ("p", lambda p: {"output": p["input"] * 2}),
            "b": ("q", lambda p: {"output": p["input"] * 3}),
        },
    )
    assert result.scenario_agreement == {
        "low": "divergent_outputs",
        "high": "divergent_outputs",
    }
    assert {run.parameters_json for run in result.runs} == {
        '{"input":1}', '{"input":10}'
    }


def test_failed_runs_are_preserved_and_comparison_can_be_incomplete():
    def fail(parameters):
        raise TimeoutError()

    result = MultiModelSimulationRunner().run(
        "study-3", "Failure handling",
        [SimulationScenario("case", {"x": 1})],
        {"a": ("p", fail), "b": ("q", lambda p: {"y": 2})},
    )
    assert result.scenario_agreement["case"] == "insufficient_outputs"
    assert result.runs[0].status == "failed"
    assert result.runs[0].error_type == "TimeoutError"
    assert any("failed" in warning for warning in result.warnings)


def test_requires_bounded_explicit_inputs():
    runner = MultiModelSimulationRunner()
    models = {"a": ("p", lambda p: p), "b": ("q", lambda p: p)}
    with pytest.raises(ValueError, match="scenario"):
        runner.run("id", "objective", [], models)
    with pytest.raises(ValueError, match="two configured"):
        runner.run("id", "objective", [SimulationScenario("s", {})], {"a": ("p", lambda p: p)})
    with pytest.raises(ValueError, match="unique"):
        runner.run(
            "id", "objective",
            [SimulationScenario("s", {}), SimulationScenario("s", {})],
            models,
        )
    with pytest.raises(ValueError, match="100 scenarios"):
        runner.run(
            "id", "objective",
            [SimulationScenario(str(i), {}) for i in range(101)],
            models,
        )


def test_rejects_non_finite_json_parameters():
    with pytest.raises(ValueError):
        MultiModelSimulationRunner().run(
            "id", "objective", [SimulationScenario("s", {"x": float("nan")})],
            {"a": ("p", lambda p: p), "b": ("q", lambda p: p)},
        )
