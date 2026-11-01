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


def test_pipeline_executes_decomposed_work_through_campaign_coordinator(tmp_path):
    from ssswet_core.campaign_coordinator import CampaignCoordinator
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.resource_manager import ResourceManager

    store = SQLiteResearchStore(tmp_path / "campaign-pipeline.sqlite3")
    campaign = create_campaign(
        "pipeline-campaign", "Wave study", "Study a harmless wave model", "physics",
        [CampaignMilestone("review", "Research review", "Review the model and challenge it")],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))
    coordinator = CampaignCoordinator(store, ResourceManager(max_active_assignments=2))
    pipeline = ResearchPipeline(store=store, campaign_coordinator=coordinator)

    task_id, steps = pipeline.start_in_campaign(
        "Study a harmless mathematical wave model",
        "pipeline-campaign", "review", "physics",
    )

    assert len(steps) == 2
    assert len({step.agent_id for step in steps}) == 2
    assert all(step.agent_id.startswith("bot-") for step in steps)
    assert all(step.result.summary for step in steps)
    assert task_id
    assert coordinator.snapshot()["completed_task_ids"] == [
        f"{task_id}:001", f"{task_id}:002"
    ]
    assert pipeline.groups.for_task(task_id)
    assert all(step.result.uncertainty >= 0 for step in steps)


def test_campaign_pipeline_preserves_work_after_provider_failure(tmp_path):
    from ssswet_core.campaign_coordinator import CampaignCoordinator
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.resource_manager import ResourceManager

    store = SQLiteResearchStore(tmp_path / "campaign-failure.sqlite3")
    campaign = create_campaign(
        "failure-campaign", "Research", "Study a harmless question", "general",
        [CampaignMilestone("review", "Review", "Review evidence")],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))
    coordinator = CampaignCoordinator(
        store, ResourceManager(max_active_assignments=2, max_attempts=2)
    )
    pipeline = ResearchPipeline(
        provider=BrokenProvider(), store=store, campaign_coordinator=coordinator
    )

    task_id, steps = pipeline.start_in_campaign(
        "Study a harmless question", "failure-campaign", "review"
    )

    assert steps == []
    assert coordinator.snapshot()["failed_task_ids"] == [
        f"{task_id}:001", f"{task_id}:002"
    ]
    assert any(task.id == task_id for task in pipeline.engine.orchestrator.tasks)
    saved_campaign = store.get_campaign("failure-campaign")
    assert saved_campaign["milestones"][0]["state"] == "blocked"
