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



def test_pipeline_reports_live_agent_activity():
    pipeline = ResearchPipeline()
    updates = []
    task_id, steps = pipeline.start(
        "Study a harmless mathematical optimization problem",
        "math",
        progress_callback=updates.append,
    )

    assert task_id
    assert len(steps) == 2
    working = [item for item in updates if item["phase"] == "agent_working"]
    completed = [item for item in updates if item["phase"] == "agent_pass_completed"]
    assert len(working) == 2
    assert len(completed) == 2
    assert sorted(len(item["active_agents"]) for item in working) == [1, 2]
    assert sorted(len(item["active_agents"]) for item in completed) == [0, 1]



def test_pipeline_runs_independent_peer_review_searches(tmp_path):
    from ssswet_core.persistence import SQLiteResearchStore
    store = SQLiteResearchStore(tmp_path / "peer-handoffs.sqlite3")
    pipeline = ResearchPipeline(store=store)
    task_id, steps = pipeline.start(
        "Study a harmless mathematical optimization problem", "math"
    )
    messages = store.recent_agent_messages(task_id=task_id)
    requests = [item for item in messages if item["message_type"] == "peer_review_request"]
    responses = [item for item in messages if item["message_type"] == "peer_review_response"]
    assert len(steps) == 2
    assert len(requests) == 2
    assert len(responses) == 2
    assert all(item["sender_agent_id"] != item["recipient_agent_id"] for item in messages)
    assert all("not approval or verification" in item["content"] for item in responses)
    assert all(item["review_state"] == "awaiting_review" for item in requests)


class SourcedProvider:
    name = "sourced-test-provider"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            summary="A provisional note grounded in a traceable bibliographic record.",
            evidence=("A source record was located for independent inspection.",),
            uncertainty=0.8,
            source_ids=("https://doi.org/10.1000/example-record",),
        )


def test_pipeline_persists_source_linked_agent_notes_and_observed_peer_review(tmp_path):
    from ssswet_core.agent_identity import AgentIdentityRegistry
    from ssswet_core.persistence import SQLiteResearchStore

    store = SQLiteResearchStore(tmp_path / "agent-memory-pipeline.sqlite3")
    pipeline = ResearchPipeline(provider=SourcedProvider(), store=store)
    task_id, steps = pipeline.start(
        "Study a harmless mathematical optimization problem", "math"
    )

    registry = AgentIdentityRegistry(store)
    researcher_notes = registry.memories("ssswet:general_researcher")
    verifier_notes = registry.memories("ssswet:independent_verifier")
    overview = registry.overview()

    assert len(steps) == 2
    assert len(researcher_notes) == 1
    assert len(verifier_notes) == 1
    assert all(item["source_reference"].startswith(f"task:{task_id};sources:") for item in researcher_notes + verifier_notes)
    assert all("https://doi.org/10.1000/example-record" in item["content"] for item in researcher_notes + verifier_notes)

    records = {item["agent_id"]: item for item in overview["persistent_agent_records"]}
    assert records["ssswet:independent_verifier"]["collaboration_history"][0]["observable_event"] == "peer_review"
    assert records["ssswet:independent_verifier"]["collaboration_history"][0]["other_agent_id"] == "ssswet:general_researcher"
