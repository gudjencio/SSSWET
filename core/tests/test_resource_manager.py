import pytest

from ssswet_core.orchestrator import BotManager
from ssswet_core.resource_manager import ResourceManager, WorkRequest


def _request(task_id="task-1", campaign="campaign-a", units=2.0, priority=5, key=""):
    return WorkRequest(
        task_id, campaign, f"Investigate {task_id}", "analyst",
        estimated_units=units, priority=priority, deduplication_key=key,
    )


def test_dispatch_respects_campaign_parallel_and_global_limits():
    manager = ResourceManager(BotManager(max_agents=5), max_active_assignments=1)
    manager.configure_campaign("campaign-a", max_parallel=4, max_units=20)
    manager.submit(_request("task-1"))
    manager.submit(_request("task-2"))
    first = manager.dispatch()
    assert len(first) == 1
    assert len(manager.dispatch()) == 0
    assert manager.snapshot()["campaign_quotas"]["campaign-a"]["reserved_units"] == 2.0


def test_campaign_quota_blocks_overcommitment():
    manager = ResourceManager(BotManager(max_agents=4))
    manager.configure_campaign("campaign-a", max_parallel=4, max_units=3)
    manager.submit(_request("task-1", units=2))
    manager.submit(_request("task-2", units=2))
    assert len(manager.dispatch()) == 1
    assert len(manager.queue) == 1


def test_duplicate_work_is_rejected():
    manager = ResourceManager()
    manager.submit(_request("task-1", key="same-source-task"))
    with pytest.raises(ValueError, match="Duplicate work"):
        manager.submit(_request("task-2", key="same-source-task"))


def test_failed_assignment_is_retried_and_history_preserved():
    manager = ResourceManager(BotManager(max_agents=3), max_attempts=2)
    manager.submit(_request())
    first = manager.dispatch()[0]
    manager.finish("task-1", success=False)
    assert manager.queue[0].task_id == "task-1"
    second = manager.dispatch()[0]
    assert second.attempt == 2
    manager.finish("task-1", success=False)
    snapshot = manager.snapshot()
    assert snapshot["failed_task_ids"] == ["task-1"]
    assert [item["state"] for item in snapshot["attempt_history"]["task-1"]] == [
        "failed", "failed"
    ]


def test_success_releases_agent_and_charges_actual_usage():
    manager = ResourceManager(BotManager(max_agents=2))
    manager.configure_campaign("campaign-a", max_parallel=2, max_units=10)
    manager.submit(_request(units=3))
    assignment = manager.dispatch()[0]
    manager.finish("task-1", success=True, actual_units=1.5)
    agent = manager.bot_manager.agents[assignment.agent_id]
    assert agent.status.value == "waiting"
    assert agent.completed_tasks == 1
    assert manager.snapshot()["campaign_quotas"]["campaign-a"]["consumed_units"] == 1.5


def test_invalid_actual_usage_does_not_lose_assignment():
    manager = ResourceManager(BotManager(max_agents=2))
    manager.submit(_request(units=3))
    manager.dispatch()
    with pytest.raises(ValueError, match="cannot be negative"):
        manager.finish("task-1", success=False, actual_units=-1)
    assert "task-1" in manager.assignments
    assert manager.snapshot()["campaign_quotas"]["campaign-a"]["reserved_units"] == 3


def test_actual_usage_cannot_exceed_quota():
    manager = ResourceManager(BotManager(max_agents=2))
    manager.configure_campaign("campaign-a", max_parallel=1, max_units=3)
    manager.submit(_request(units=2))
    manager.dispatch()
    with pytest.raises(ValueError, match="exceeds"):
        manager.finish("task-1", success=True, actual_units=4)
    assert "task-1" in manager.assignments
    assert manager.snapshot()["campaign_quotas"]["campaign-a"]["reserved_units"] == 2
