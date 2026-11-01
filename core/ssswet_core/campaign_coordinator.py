"""Campaign-aware scheduling for decomposed research pipeline work."""
from __future__ import annotations

from uuid import uuid4
from typing import Iterable

from .campaigns import update_milestone
from .persistence import SQLiteResearchStore
from .resource_manager import ResourceManager, WorkAssignment, WorkRequest


class CampaignCoordinator:
    """Connect campaign milestones to bounded role-based resource scheduling.

    The coordinator schedules work only. It does not execute experiments or
    promote provider output to a verified scientific finding.
    """

    def __init__(
        self,
        store: SQLiteResearchStore,
        resources: ResourceManager | None = None,
    ) -> None:
        self.store = store
        self.resources = resources or ResourceManager()

    def queue_subtasks(
        self,
        campaign_id: str,
        milestone_id: str,
        parent_task_id: str,
        subtasks: Iterable[object],
    ) -> list[str]:
        campaign_data = self.store.get_campaign(campaign_id)
        if campaign_data is None:
            raise ValueError(f"Unknown campaign: {campaign_id}")
        if campaign_data.get("state") != "active":
            raise ValueError("Research campaign must be active before work is queued")

        from .campaigns import CampaignMilestone, ResearchCampaign

        campaign = ResearchCampaign(
            campaign_id=campaign_data["campaign_id"],
            title=campaign_data["title"],
            objective=campaign_data["objective"],
            domain=campaign_data["domain"],
            state=campaign_data["state"],
            milestones=tuple(CampaignMilestone(**item) for item in campaign_data["milestones"]),
            warnings=tuple(campaign_data.get("warnings", ())),
        )
        milestone = next(
            (item for item in campaign.milestones if item.milestone_id == milestone_id),
            None,
        )
        if milestone is None:
            raise ValueError(f"Unknown milestone: {milestone_id}")
        if milestone.state not in {"pending", "in_progress"}:
            raise ValueError("Milestone is not available for new work")

        specs = list(subtasks)
        if not specs or len(specs) > 100:
            raise ValueError("A work batch must contain between 1 and 100 subtasks")
        if not parent_task_id.strip():
            raise ValueError("A parent task ID is required")

        if campaign_id not in self.resources.quotas:
            self.resources.configure_campaign(campaign_id)

        requests = []
        for index, spec in enumerate(specs, start=1):
            objective = getattr(spec, "objective", "")
            role = getattr(spec, "role", "")
            priority = getattr(spec, "priority", 5)
            if not isinstance(objective, str) or not objective.strip():
                raise ValueError("Every subtask needs an objective")
            if not isinstance(role, str) or not role.strip():
                raise ValueError("Every subtask needs a specialist role")
            task_id = f"{parent_task_id}:{index:03d}"
            requests.append(WorkRequest(
                task_id=task_id,
                campaign_id=campaign_id,
                objective=objective,
                role=role,
                estimated_units=1.0,
                priority=priority,
                deduplication_key=f"{campaign_id}:{milestone_id}:{task_id}",
                milestone_id=milestone_id,
            ))

        # Validate identifiers before mutating the queue.
        existing_ids = (
            set(self.resources.assignments)
            | self.resources.completed
            | self.resources.failed
            | {item.task_id for item in self.resources.queue}
        )
        if any(item.task_id in existing_ids for item in requests):
            raise ValueError("One or more subtasks have already been scheduled")

        if milestone.state == "pending":
            self.store.save_campaign(update_milestone(
                campaign, milestone_id, "in_progress"
            ))
        for request in requests:
            self.resources.submit(request)

        self._save_snapshot()
        return [item.task_id for item in requests]

    def dispatch(self) -> list[WorkAssignment]:
        assignments = self.resources.dispatch()
        if assignments:
            self._save_snapshot()
        return assignments

    def finish(
        self,
        task_id: str,
        *,
        success: bool,
        actual_units: float | None = None,
    ) -> None:
        self.resources.finish(task_id, success=success, actual_units=actual_units)
        self._save_snapshot()

    def snapshot(self) -> dict:
        return self.resources.snapshot()

    def _save_snapshot(self) -> None:
        self.store.save_resource_snapshot(
            f"coordinator-{uuid4().hex}",
            self.resources.snapshot(),
        )
