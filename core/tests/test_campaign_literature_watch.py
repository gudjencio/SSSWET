from datetime import datetime, timezone, timedelta

from ssswet_core.campaign_literature_watch import CampaignLiteratureWatch
from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.providers import ProviderResult


class FakeProvider:
    name = "fixture-literature"
    def __init__(self):
        self.calls = 0
    def investigate(self, objective, strategy):
        self.calls += 1
        return ProviderResult(
            "Metadata discovery only",
            evidence=("Paper alpha | DOI: 10.777/alpha | URL: https://example.org/a",),
            source_ids=("10.777/alpha",),
        )


def active_campaign(store, state="active"):
    campaign = create_campaign(
        "watch-campaign", "Orbital research", "Study orbital dynamics", "physics",
        [CampaignMilestone("m1", "Literature review", "Review scholarly publications")],
    )
    campaign = set_campaign_state(campaign, "active")
    if state != "active":
        campaign = set_campaign_state(campaign, state)
    store.save_campaign(campaign)


def test_campaign_watch_runs_when_due_and_deduplicates_seen_items(tmp_path):
    store = SQLiteResearchStore(tmp_path / "campaign-watch.sqlite3")
    active_campaign(store)
    provider = FakeProvider()
    service = CampaignLiteratureWatch(store, provider)
    now = datetime(2026, 11, 1, tzinfo=timezone.utc)
    sub = service.subscribe("watch-campaign", "orbital dynamics", 60, now=now)

    first = service.run_due(now=now)
    assert len(first) == 1
    assert first[0].new_candidate_ids == ("10.777/alpha",)
    assert first[0].previously_seen_ids == ()
    assert first[0].scientific_validity_established is False
    assert first[0].memory_changed is False
    assert first[0].campaign_changed is False

    assert service.run_due(now=now + timedelta(minutes=30)) == []
    second = service.run_due(now=now + timedelta(minutes=60))
    assert len(second) == 1
    assert second[0].new_candidate_ids == ()
    assert second[0].previously_seen_ids == ("10.777/alpha",)
    assert provider.calls == 2
    assert len(store.campaign_watch_run_history()) == 2


def test_paused_campaign_cannot_subscribe_or_run(tmp_path):
    import pytest
    store = SQLiteResearchStore(tmp_path / "paused-watch.sqlite3")
    active_campaign(store, "paused")
    service = CampaignLiteratureWatch(store, FakeProvider())
    with pytest.raises(ValueError, match="active campaigns"):
        service.subscribe("watch-campaign", "orbital dynamics")


def test_subscription_interval_is_bounded(tmp_path):
    import pytest
    store = SQLiteResearchStore(tmp_path / "interval-watch.sqlite3")
    active_campaign(store)
    service = CampaignLiteratureWatch(store, FakeProvider())
    with pytest.raises(ValueError, match="between 60 minutes"):
        service.subscribe("watch-campaign", "topic", 5)
