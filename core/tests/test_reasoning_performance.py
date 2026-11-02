import pytest

from ssswet_core.reasoning_performance import FAST_REASONING_POLICY, ReasoningPerformancePolicy


def test_fast_policy_is_bounded_and_low_latency():
    assert FAST_REASONING_POLICY.max_parallel_agents == 10
    assert FAST_REASONING_POLICY.max_parallel_reviews == 6
    assert FAST_REASONING_POLICY.model_timeout_seconds == 30.0
    assert FAST_REASONING_POLICY.model_max_output_tokens == 700
    assert FAST_REASONING_POLICY.literature_timeout_seconds == 8.0
    assert FAST_REASONING_POLICY.literature_results_per_source == 4


def test_fast_policy_exposes_provider_kwargs():
    policy = ReasoningPerformancePolicy()
    assert policy.model_kwargs() == {"timeout": 30.0, "max_tokens": 700}
    assert policy.literature_kwargs() == {"timeout": 8.0, "max_results": 4}


def test_fast_policy_rejects_unsafe_bounds():
    with pytest.raises(ValueError):
        ReasoningPerformancePolicy(model_timeout_seconds=4.9)
    with pytest.raises(ValueError):
        ReasoningPerformancePolicy(model_max_output_tokens=127)
    with pytest.raises(ValueError):
        ReasoningPerformancePolicy(literature_results_per_source=21)
