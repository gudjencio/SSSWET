import pytest

from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.coordinator import CampaignCoordinator
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.resource_manager import ResourceManager


def _active_campaign(store):
    campaign = create_campaign(
        "campaign-coordination",
        "Materials research",
        "Compare candidate material properties",
        "materials",
        [
            CampaignMilestone(
                "literature",
                "Review literature",
                "Identify published measurement approaches",
            ),
            CampaignMilestone(
                "simulation",
                "Compare simulations",
                "Run approved bounded computational comparisons",
            ),
        ],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))


def test_coordinator_dispatches_work_and_requires_explicit_milestone_approval(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(
        store, ResourceManager(max_active_assignments=2, max_attempts=2)
    )
    coordinator.configure_campaign("campaign-coordination", max_parallel=2, max_units=10)

    request = coordinator.enqueue_milestone(
        "campaign-coordination", "literature", "literature_analyst",
        estimated_units=2, priority=2,
    )
    assert request.milestone_id == "literature"
    assignments = coordinator.dispatch()
    assert len(assignments) == 1
    saved = store.get_campaign("campaign-coordination")
    assert saved["milestones"][0]["state"] == "in_progress"

    coordinator.finish_assignment(request.task_id, success=True, actual_units=1.5)
    saved = store.get_campaign("campaign-coordination")
    assert saved["milestones"][0]["state"] == "in_progress"

    with pytest.raises(ValueError, match="successfully"):
        coordinator.approve_milestone_completion(
            "campaign-coordination", "simulation"
        )
    coordinator.approve_milestone_completion(
        "campaign-coordination", "literature"
    )
    saved = store.get_campaign("campaign-coordination")
    assert saved["milestones"][0]["state"] == "completed"


def test_coordinator_retries_then_marks_exhausted_milestone_blocked(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator-retry.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(
        store, ResourceManager(max_active_assignments=1, max_attempts=1)
    )
    coordinator.enqueue_milestone(
        "campaign-coordination", "literature", "literature_analyst"
    )
    assignment = coordinator.dispatch()[0]
    coordinator.finish_assignment(assignment.request.task_id, success=False)
    saved = store.get_campaign("campaign-coordination")
    assert saved["milestones"][0]["state"] == "blocked"
    assert saved["milestones"][0]["notes"]


def test_coordinator_refuses_inactive_or_completed_milestones(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator-state.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(store)
    campaign = store.get_campaign("campaign-coordination")
    assert campaign["state"] == "active"
    with pytest.raises(ValueError, match="Unknown milestone"):
        coordinator.enqueue_milestone(
            "campaign-coordination", "missing", "analyst"
        )
    with pytest.raises(ValueError, match="Only active campaigns"):
        from ssswet_core.campaigns import set_campaign_state
        from ssswet_core.campaigns import CampaignMilestone, ResearchCampaign
        saved = coordinator._campaign("campaign-coordination")
        store.save_campaign(set_campaign_state(saved, "paused"))
        coordinator.enqueue_milestone(
            "campaign-coordination", "literature", "analyst"
        )


def test_coordinator_persists_resource_snapshots(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator-snapshot.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(store)
    coordinator.enqueue_milestone(
        "campaign-coordination", "literature", "analyst"
    )
    coordinator.dispatch()
    history = store.resource_snapshot_history()
    assert history
    assert history[0]["snapshot"]["active"][0]["milestone_id"] == "literature"
