import pytest

from research.evaluation.throughput import ThroughputTarget, completion_ratio, shortfall


def test_targets_match_public_delivery_goal():
    target = ThroughputTarget()
    assert target.major_per_day == 1000
    assert target.fixes_per_hour == 100


def test_completion_ratio_is_bounded():
    assert completion_ratio(25, 100) == 0.25
    assert completion_ratio(150, 100) == 1.0


def test_shortfall_never_becomes_negative():
    assert shortfall(25, 100) == 75
    assert shortfall(150, 100) == 0


@pytest.mark.parametrize("completed,target", [(-1, 100), (1, 0), (1, -1)])
def test_invalid_accounting_inputs_are_rejected(completed, target):
    with pytest.raises(ValueError):
        completion_ratio(completed, target)
