from ssswet_core.model_comparison import MultiModelComparator


def test_two_models_are_compared_without_truth_voting():
    result = MultiModelComparator().compare(
        "cmp-1", "Explain a testable question",
        {
            "model-a": ("provider-a", lambda prompt: "Hypothesis A"),
            "model-b": ("provider-b", lambda prompt: "Hypothesis B"),
        },
    )
    assert result.agreement == "divergent_outputs"
    assert result.distinct_output_count == 2
    assert any("not independent scientific evidence" in warning for warning in result.warnings)


def test_identical_outputs_are_not_promoted_to_verified():
    result = MultiModelComparator().compare(
        "cmp-2", "Question",
        {
            "model-a": ("provider-a", lambda prompt: "same result"),
            "model-b": ("provider-b", lambda prompt: "same result"),
        },
    )
    assert result.agreement == "identical_outputs"
    assert "does not validate" in result.interpretation


def test_failed_model_makes_comparison_incomplete():
    def fail(prompt):
        raise TimeoutError()
    result = MultiModelComparator().compare(
        "cmp-3", "Question",
        {
            "model-a": ("provider-a", lambda prompt: "answer"),
            "model-b": ("provider-b", fail),
        },
    )
    assert result.agreement == "insufficient_outputs"
    assert result.outputs[1].error_type == "TimeoutError"


def test_requires_two_models_and_prompt():
    import pytest
    comparator = MultiModelComparator()
    with pytest.raises(ValueError, match="At least two"):
        comparator.compare("cmp", "prompt", {"one": ("p", lambda x: x)})
    with pytest.raises(ValueError, match="required"):
        comparator.compare("cmp", "", {"one": ("p", lambda x: x), "two": ("q", lambda x: x)})
