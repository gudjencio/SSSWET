from ssswet_core.pipeline import ResearchPipeline
from ssswet_core.models import AgentStatus, TaskStatus
from ssswet_core.providers import ProviderResult


class BrokenProvider:
    name = "broken-test-provider"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        raise RuntimeError("test provider unavailable")


def test_pipeline_assigns_distinct_role_matched_agents_and_creates_group():
    pipeline = ResearchPipeline()
    task_id, steps = pipeline.start("Study a harmless mathematical optimization problem", "math")

    assert task_id
    assert len(steps) == 2
    assert steps[0].subtask.role == "mathematician"
    assert steps[1].subtask.role == "independent_verifier"
    assert steps[0].agent_id != steps[1].agent_id
    assert all(step.provider == "deterministic-demo" for step in steps)

    groups = pipeline.groups.for_task(task_id)
    assert len(groups) == 1
    assert set(groups[0].members) == {step.agent_id for step in steps}
    assert all(
        pipeline.engine.orchestrator.bot_manager.agents[step.agent_id].status == AgentStatus.WAITING
        for step in steps
    )


def test_pipeline_records_group_and_research_events():
    pipeline = ResearchPipeline()
    task_id, _ = pipeline.start("Check a harmless arithmetic identity", "math")
    events = [event for event in pipeline.engine.orchestrator.events if event.task_id == task_id]
    kinds = {event.kind for event in events}
    assert "team_created" in kinds
    assert "group_created" in kinds
    assert "research_pass" in kinds
    assert "task_completed" in kinds


def test_provider_failure_preserves_task_and_releases_team():
    pipeline = ResearchPipeline(provider=BrokenProvider())
    try:
        pipeline.start("Study a harmless mathematical optimization problem", "math")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected the test provider to fail")

    queued = list(pipeline.engine.orchestrator.tasks)
    assert len(queued) == 1
    assert queued[0].status == TaskStatus.BLOCKED
    assert all(agent.load == 0 for agent in pipeline.engine.orchestrator.bot_manager.agents.values())
