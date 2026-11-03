from ssswet_core.fast_coordination import coordinate_batch
from ssswet_core.models import Agent, AgentStatus, Task


def test_coordinate_batch_prioritizes_tasks_within_budget():
    tasks = [Task("low", "l", priority=1), Task("high", "h", priority=9)]
    agents = [Agent("a1", "researcher", status=AgentStatus.WAITING)]
    result = coordinate_batch(tasks, agents, budget_ms=100)
    assert result.assignments == [("a1", "high")]
    assert result.elapsed_ms <= 100


def test_coordinate_batch_rejects_invalid_budget():
    try:
        coordinate_batch([], [], budget_ms=0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
