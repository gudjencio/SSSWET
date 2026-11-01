import pytest

from ssswet_core.campaigns import (
    CampaignMilestone,
    create_campaign,
    set_campaign_state,
    update_milestone,
)
from ssswet_core.persistence import SQLiteResearchStore


def _campaign():
    return create_campaign(
        "campaign-1", "Wave propagation study", "Compare measurement methods",
        "physics",
        [
            CampaignMilestone("m1", "Literature review", "Map existing methods"),
            CampaignMilestone("m2", "Simulation", "Compare bounded models"),
        ],
    )


def test_campaign_requires_all_milestones_before_completion():
    campaign = set_campaign_state(_campaign(), "active")
    with pytest.raises(ValueError, match="All milestones"):
        set_campaign_state(campaign, "completed")


def test_campaign_milestone_updates_and_state_transitions():
    campaign = set_campaign_state(_campaign(), "active")
    campaign = update_milestone(
        campaign, "m1", "completed", linked_study_ids=("study-a",),
        notes="Reviewed by operator",
    )
    campaign = update_milestone(campaign, "m2", "completed")
    campaign = set_campaign_state(campaign, "completed")
    assert campaign.state == "completed"
    assert campaign.milestones[0].linked_study_ids == ("study-a",)


def test_campaign_rejects_invalid_transition_and_unknown_milestone():
    campaign = _campaign()
    with pytest.raises(ValueError, match="Invalid campaign transition"):
        set_campaign_state(campaign, "completed")
    with pytest.raises(ValueError, match="Unknown milestone"):
        update_milestone(campaign, "missing", "completed")


def test_campaign_persistence_survives_reopen(tmp_path):
    path = tmp_path / "campaign.sqlite3"
    store = SQLiteResearchStore(path)
    campaign = set_campaign_state(_campaign(), "active")
    store.save_campaign(campaign)
    reopened = SQLiteResearchStore(path)
    saved = reopened.get_campaign("campaign-1")
    assert saved["state"] == "active"
    assert len(reopened.campaign_history()) == 1
