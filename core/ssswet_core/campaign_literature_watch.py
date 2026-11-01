"""Per-campaign, interval-based scholarly metadata monitoring.

This module runs due searches only when explicitly invoked by a local operator
or scheduler. It records novelty relative to prior watch reports; it never
imports publications into the source registry or changes campaign knowledge.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import uuid

from .literature_watch import LiteratureWatchService, LiteratureWatchReport


@dataclass(frozen=True)
class CampaignWatchSubscription:
    subscription_id: str
    campaign_id: str
    query: str
    interval_minutes: int
    enabled: bool
    created_at: str
    last_run_at: str = ""
    next_run_at: str = ""


@dataclass(frozen=True)
class CampaignWatchRun:
    run_id: str
    subscription_id: str
    campaign_id: str
    query: str
    watch_id: str
    created_at: str
    candidate_count: int
    new_candidate_ids: tuple[str, ...]
    previously_seen_ids: tuple[str, ...]
    provider: str
    error: str = ""
    scientific_validity_established: bool = False
    memory_changed: bool = False
    campaign_changed: bool = False


class CampaignLiteratureWatch:
    def __init__(self, store: object, provider: object):
        self.store, self.provider = store, provider

    def subscribe(
        self, campaign_id: str, query: str, interval_minutes: int = 1440,
        *, enabled: bool = True, now: datetime | None = None,
    ) -> CampaignWatchSubscription:
        campaign = self.store.get_campaign(campaign_id)
        if campaign is None:
            raise ValueError("Unknown campaign")
        if campaign.get("state") != "active":
            raise ValueError("Only active campaigns can enable literature monitoring")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A non-empty watch query is required")
        if isinstance(interval_minutes, bool) or not isinstance(interval_minutes, int):
            raise ValueError("interval_minutes must be an integer")
        if not 60 <= interval_minutes <= 43200:
            raise ValueError("Monitoring interval must be between 60 minutes and 30 days")
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        subscription = CampaignWatchSubscription(
            subscription_id=str(uuid.uuid4()), campaign_id=campaign_id,
            query=query.strip(), interval_minutes=interval_minutes,
            enabled=enabled, created_at=stamp.isoformat(),
            next_run_at=stamp.isoformat() if enabled else "",
        )
        self.store.save_campaign_watch_subscription(subscription)
        return subscription

    def set_enabled(
        self, subscription_id: str, enabled: bool, *,
        now: datetime | None = None,
    ) -> CampaignWatchSubscription:
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        current = self.store.get_campaign_watch_subscription(subscription_id)
        if current is None:
            raise ValueError("Unknown campaign watch subscription")
        campaign = self.store.get_campaign(current["campaign_id"])
        if enabled and (campaign is None or campaign.get("state") != "active"):
            raise ValueError("Only active campaigns can enable literature monitoring")
        stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        next_run = current.get("next_run_at", "")
        if enabled and not current.get("enabled"):
            next_run = stamp.isoformat()
        if not enabled:
            next_run = ""
        updated = CampaignWatchSubscription(
            subscription_id=current["subscription_id"],
            campaign_id=current["campaign_id"], query=current["query"],
            interval_minutes=current["interval_minutes"], enabled=enabled,
            created_at=current["created_at"], last_run_at=current.get("last_run_at", ""),
            next_run_at=next_run,
        )
        self.store.save_campaign_watch_subscription(updated)
        return updated

    def run_due(self, *, now: datetime | None = None, limit: int = 20) -> list[CampaignWatchRun]:
        stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        due = self.store.due_campaign_watch_subscriptions(stamp.isoformat(), limit=limit)
        runs = []
        for subscription in due:
            campaign = self.store.get_campaign(subscription["campaign_id"])
            if campaign is None or campaign.get("state") != "active":
                self.set_enabled(subscription["subscription_id"], False, now=stamp)
                continue
            try:
                report: LiteratureWatchReport = LiteratureWatchService(
                    self.provider, self.store
                ).run(subscription["query"])
                previous = self.store.campaign_watch_seen_ids(
                    subscription["campaign_id"], subscription["subscription_id"]
                )
                observed = {candidate.doi.casefold() or candidate.source_id.casefold()
                            for candidate in report.candidates}
                observed.discard("")
                new_ids = tuple(sorted(observed - previous))
                seen_ids = tuple(sorted(observed & previous))
                run = CampaignWatchRun(
                    run_id=str(uuid.uuid4()), subscription_id=subscription["subscription_id"],
                    campaign_id=subscription["campaign_id"], query=subscription["query"],
                    watch_id=report.watch_id, created_at=stamp.isoformat(),
                    candidate_count=len(report.candidates), new_candidate_ids=new_ids,
                    previously_seen_ids=seen_ids, provider=report.provider,
                )
            except Exception as exc:
                run = CampaignWatchRun(
                    run_id=str(uuid.uuid4()), subscription_id=subscription["subscription_id"],
                    campaign_id=subscription["campaign_id"], query=subscription["query"],
                    watch_id="", created_at=stamp.isoformat(), candidate_count=0,
                    new_candidate_ids=(), previously_seen_ids=(),
                    provider=getattr(self.provider, "name", "unknown"),
                    error=type(exc).__name__,
                )
            self.store.save_campaign_watch_run(run)
            next_time = (stamp + timedelta(minutes=subscription["interval_minutes"])).isoformat()
            self.store.mark_campaign_watch_run(
                subscription["subscription_id"], stamp.isoformat(), next_time
            )
            runs.append(run)
        return runs


def subscription_to_dict(item: CampaignWatchSubscription) -> dict:
    return asdict(item)


def run_to_dict(item: CampaignWatchRun) -> dict:
    return asdict(item)
