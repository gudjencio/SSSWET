from types import SimpleNamespace

import pytest

from ssswet_core.campaign_coordinator import CampaignCoordinator
from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.resource_manager import ResourceManager


def _active_campaign(store):
    campaign = create_campaign(
        "campaign-coordinator", "Materials study", "Compare material properties",
        "materials", [
            CampaignMilestone("milestone-1", "Initial review", "Review available evidence")
        ],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))


def test_coordinator_queues_and_dispatches_role_matched_subtasks(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(store, ResourceManager(max_active_assignments=2))
    subtasks = [
        SimpleNamespace(objective="Review published material data", role="materials_scientist", priority=4),
        SimpleNamespace(objective="Independently challenge the review", role="independent_verifier", priority=5),
    ]

    ids = coordinator.queue_subtasks(
        "campaign-coordinator", "milestone-1", "parent-1", subtasks
    )
    assignments = coordinator.dispatch()

    assert ids == ["parent-1:001", "parent-1:002"]
    assert {item.request.milestone_id for item in assignments} == {"milestone-1"}
    assert {item.request.role for item in assignments} == {
        "materials_scientist", "independent_verifier"
    }
    saved = store.get_campaign("campaign-coordinator")
    assert saved["milestones"][0]["state"] == "in_progress"


def test_coordinator_rejects_inactive_campaign_and_unavailable_milestone(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator.sqlite3")
    campaign = create_campaign(
        "campaign-draft", "Draft", "Objective", "general",
        [CampaignMilestone("m1", "Review", "Review evidence")],
    )
    store.save_campaign(campaign)
    coordinator = CampaignCoordinator(store)

    with pytest.raises(ValueError, match="must be active"):
        coordinator.queue_subtasks(
            "campaign-draft", "m1", "parent",
            [SimpleNamespace(objective="Review", role="researcher", priority=5)],
        )


def test_coordinator_persists_each_resource_transition(tmp_path):
    store = SQLiteResearchStore(tmp_path / "coordinator.sqlite3")
    _active_campaign(store)
    coordinator = CampaignCoordinator(store)
    coordinator.queue_subtasks(
        "campaign-coordinator", "milestone-1", "parent-2",
        [SimpleNamespace(objective="Review", role="researcher", priority=5)],
    )
    assignment = coordinator.dispatch()[0]
    coordinator.finish(assignment.request.task_id, success=True)

    history = store.resource_snapshot_history()
    assert len(history) >= 3
    assert history[0]["snapshot"]["completed_task_ids"] == ["parent-2:001"]
