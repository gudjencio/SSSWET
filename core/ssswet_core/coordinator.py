"""Human-supervised coordinator for campaign milestones and bounded resources."""

from __future__ import annotations

from uuid import uuid4

from .campaigns import (
    CampaignMilestone,
    ResearchCampaign,
    campaign_to_dict,
    update_milestone,
)
from .persistence import SQLiteResearchStore
from .resource_manager import ResourceManager, WorkAssignment, WorkRequest


class CampaignCoordinator:
    """Connect campaign milestones to the bounded local resource scheduler.

    Dispatch reserves local agent/resource capacity only. It does not invoke
    model providers, run experiments, or decide that research is scientifically
    complete. Milestone completion requires a separate operator approval.
    """

    def __init__(
        self,
        store: SQLiteResearchStore,
        resource_manager: ResourceManager | None = None,
    ) -> None:
        self.store = store
        self.resources = resource_manager or ResourceManager()

    def _campaign(self, campaign_id: str) -> ResearchCampaign:
        saved = self.store.get_campaign(campaign_id)
        if saved is None:
            raise ValueError(f"Unknown campaign: {campaign_id}")
        milestones = tuple(
            CampaignMilestone(
                item["milestone_id"],
                item["title"],
                item["objective"],
                item.get("state", "pending"),
                tuple(item.get("linked_study_ids", ())),
                item.get("notes", ""),
            )
            for item in saved.get("milestones", [])
        )
        return ResearchCampaign(
            saved["campaign_id"],
            saved["title"],
            saved["objective"],
            saved["domain"],
            saved["state"],
            milestones,
            tuple(saved.get("warnings", ())),
        )

    def configure_campaign(
        self, campaign_id: str, max_parallel: int = 4, max_units: float = 100.0
    ) -> None:
        self._campaign(campaign_id)
        self.resources.configure_campaign(campaign_id, max_parallel, max_units)

    def enqueue_milestone(
        self,
        campaign_id: str,
        milestone_id: str,
        role: str,
        *,
        estimated_units: float = 1.0,
        priority: int = 5,
    ) -> WorkRequest:
        campaign = self._campaign(campaign_id)
        if campaign.state != "active":
            raise ValueError("Only active campaigns can enqueue milestone work")
        milestone = next(
            (item for item in campaign.milestones if item.milestone_id == milestone_id),
            None,
        )
        if milestone is None:
            raise ValueError(f"Unknown milestone: {milestone_id}")
        if milestone.state not in {"pending", "in_progress"}:
            raise ValueError("Only pending or in-progress milestones can be queued")
        task_id = f"{campaign_id}::{milestone_id}"
        request = WorkRequest(
            task_id=task_id,
            campaign_id=campaign_id,
            objective=milestone.objective,
            role=role,
            estimated_units=estimated_units,
            priority=priority,
            deduplication_key=task_id,
            milestone_id=milestone_id,
        )
        self.resources.submit(request)
        return request

    def dispatch(self) -> list[WorkAssignment]:
        assignments = self.resources.dispatch()
        changed: dict[str, ResearchCampaign] = {}
        for assignment in assignments:
            request = assignment.request
            campaign = changed.get(request.campaign_id) or self._campaign(request.campaign_id)
            milestone = next(
                item for item in campaign.milestones
                if item.milestone_id == request.milestone_id
            )
            if milestone.state == "pending":
                campaign = update_milestone(
                    campaign, request.milestone_id, "in_progress"
                )
                changed[request.campaign_id] = campaign
        for campaign in changed.values():
            self.store.save_campaign(campaign)
        self._save_snapshot()
        return assignments

    def finish_assignment(
        self,
        task_id: str,
        *,
        success: bool,
        actual_units: float | None = None,
    ) -> None:
        assignment = self.resources.assignments.get(task_id)
        if assignment is None:
            raise ValueError("No active assignment exists for this task")
        request = assignment.request
        self.resources.finish(task_id, success=success, actual_units=actual_units)
        if not success and task_id in self.resources.failed:
            campaign = self._campaign(request.campaign_id)
            campaign = update_milestone(
                campaign, request.milestone_id, "blocked",
                notes="Resource attempts exhausted; operator review is required.",
            )
            self.store.save_campaign(campaign)
        self._save_snapshot()

    def approve_milestone_completion(self, campaign_id: str, milestone_id: str) -> None:
        """Record an explicit operator decision after successful scheduled work."""
        task_id = f"{campaign_id}::{milestone_id}"
        if task_id not in self.resources.completed:
            raise ValueError("Scheduled work must finish successfully before approval")
        if task_id in self.resources.assignments or any(
            item.task_id == task_id for item in self.resources.queue
        ):
            raise ValueError("Milestone still has active or queued work")
        campaign = self._campaign(campaign_id)
        campaign = update_milestone(campaign, milestone_id, "completed")
        self.store.save_campaign(campaign)
        self._save_snapshot()

    def snapshot(self) -> dict:
        return self.resources.snapshot()

    def _save_snapshot(self) -> None:
        self.store.save_resource_snapshot(
            f"coordinator-{uuid4()}",
            self.resources.snapshot(),
        )
