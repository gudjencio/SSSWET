"""Bounded local resource scheduler for campaign work.

The scheduler allocates existing waiting agents only. It does not execute
research itself, launch experiments, or infer scientific success.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Agent, AgentStatus
from .orchestrator import BotManager


@dataclass(frozen=True)
class WorkRequest:
    task_id: str
    campaign_id: str
    objective: str
    role: str
    estimated_units: float = 1.0
    priority: int = 5
    deduplication_key: str = ""


@dataclass
class WorkAssignment:
    request: WorkRequest
    agent_id: str
    attempt: int
    state: str = "assigned"


@dataclass
class CampaignQuota:
    max_parallel: int = 4
    max_units: float = 100.0
    consumed_units: float = 0.0
    reserved_units: float = 0.0


class ResourceManager:
    """Deterministic queue, quota and retry manager with bounded allocations."""

    def __init__(
        self,
        bot_manager: BotManager | None = None,
        max_active_assignments: int = 12,
        max_attempts: int = 3,
    ) -> None:
        if max_active_assignments < 1 or max_attempts < 1:
            raise ValueError("Resource limits must be positive")
        self.bot_manager = bot_manager or BotManager()
        self.max_active_assignments = max_active_assignments
        self.max_attempts = max_attempts
        self.queue: list[WorkRequest] = []
        self.assignments: dict[str, WorkAssignment] = {}
        self.attempt_history: dict[str, list[dict[str, Any]]] = {}
        self.quotas: dict[str, CampaignQuota] = {}
        self._seen_keys: set[str] = set()
        self._attempts: dict[str, int] = {}
        self.completed: set[str] = set()
        self.failed: set[str] = set()

    def configure_campaign(
        self, campaign_id: str, max_parallel: int = 4, max_units: float = 100.0
    ) -> None:
        if not campaign_id.strip() or max_parallel < 1 or max_units <= 0:
            raise ValueError("Campaign ID and positive resource quotas are required")
        existing = self.quotas.get(campaign_id)
        if existing and (existing.reserved_units > max_units or existing.consumed_units > max_units):
            raise ValueError("New quota cannot be lower than already committed resources")
        self.quotas[campaign_id] = CampaignQuota(
            max_parallel, max_units,
            existing.consumed_units if existing else 0.0,
            existing.reserved_units if existing else 0.0,
        )

    def submit(self, request: WorkRequest) -> None:
        if any(not value.strip() for value in (
            request.task_id, request.campaign_id, request.objective, request.role
        )):
            raise ValueError("Task, campaign, objective and role are required")
        if request.estimated_units <= 0:
            raise ValueError("Estimated resource units must be positive")
        if not 1 <= request.priority <= 10:
            raise ValueError("Priority must be between 1 and 10")
        if request.task_id in self.assignments or request.task_id in self.completed or request.task_id in self.failed:
            raise ValueError("Task is already assigned or completed")
        if any(item.task_id == request.task_id for item in self.queue):
            raise ValueError("Task is already queued")
        key = request.deduplication_key.strip()
        if key and key in self._seen_keys:
            raise ValueError("Duplicate work request detected")
        self._seen_keys.add(key) if key else None
        self.quotas.setdefault(request.campaign_id, CampaignQuota())
        self.queue.append(request)
        self.queue.sort(key=lambda item: (item.priority, item.task_id))

    def dispatch(self) -> list[WorkAssignment]:
        launched: list[WorkAssignment] = []
        while self.queue and len(self.assignments) < self.max_active_assignments:
            selected_index = None
            for index, request in enumerate(self.queue):
                quota = self.quotas[request.campaign_id]
                active_for_campaign = sum(
                    1 for assignment in self.assignments.values()
                    if assignment.request.campaign_id == request.campaign_id
                )
                if active_for_campaign >= quota.max_parallel:
                    continue
                if quota.consumed_units + quota.reserved_units + request.estimated_units > quota.max_units:
                    continue
                if not self.bot_manager.available() and len(self.bot_manager.agents) >= self.bot_manager.max_agents:
                    continue
                selected_index = index
                break
            if selected_index is None:
                break
            request = self.queue.pop(selected_index)
            agent = self._allocate(request.role)
            if agent is None:
                self.queue.insert(selected_index, request)
                break
            quota = self.quotas[request.campaign_id]
            quota.reserved_units += request.estimated_units
            agent.current_task = request.task_id
            attempt = self._attempts.get(request.task_id, 0) + 1
            self._attempts[request.task_id] = attempt
            assignment = WorkAssignment(request, agent.id, attempt)
            self.assignments[request.task_id] = assignment
            self.attempt_history.setdefault(request.task_id, []).append({
                "attempt": attempt, "agent_id": agent.id, "state": "assigned"
            })
            launched.append(assignment)
        return launched

    def _allocate(self, role: str) -> Agent | None:
        waiting = self.bot_manager.available()
        agent = next((item for item in waiting if item.role == role), None)
        if agent is None:
            agent = next((item for item in waiting if item.role == "researcher"), None)
            if agent is not None:
                agent.role = role
        if agent is None and len(self.bot_manager.agents) < self.bot_manager.max_agents:
            agent = self.bot_manager._new_agent(role)
        if agent is None:
            return None
        agent.status = AgentStatus.WORKING
        agent.load = 1.0
        agent.current_task = None
        return agent

    def finish(self, task_id: str, success: bool, actual_units: float | None = None) -> None:
        assignment = self.assignments.get(task_id)
        if assignment is None:
            raise ValueError("No active assignment exists for this task")
        request = assignment.request
        quota = self.quotas[request.campaign_id]
        charge = request.estimated_units if actual_units is None else actual_units
        if charge < 0:
            raise ValueError("Actual resource units cannot be negative")
        self.assignments.pop(task_id)
        quota.reserved_units = max(0.0, quota.reserved_units - request.estimated_units)
        if quota.consumed_units + charge > quota.max_units:
            # Preserve the assignment for operator review instead of silently
            # charging beyond the configured campaign limit.
            self.assignments[task_id] = assignment
            quota.reserved_units += request.estimated_units
            raise ValueError("Actual usage exceeds the campaign resource quota")
        quota.consumed_units += charge
        agent = self.bot_manager.agents[assignment.agent_id]
        self.bot_manager.release(agent.id, completed=success)
        state = "completed" if success else "failed"
        assignment.state = state
        self.attempt_history[task_id][-1]["state"] = state
        if success:
            self.completed.add(task_id)
        elif assignment.attempt < self.max_attempts:
            self.queue.append(request)
            self.queue.sort(key=lambda item: (item.priority, item.task_id))
        else:
            self.failed.add(task_id)

    def snapshot(self) -> dict[str, Any]:
        return {
            "queued": [
                {"task_id": item.task_id, "campaign_id": item.campaign_id,
                 "role": item.role, "priority": item.priority}
                for item in self.queue
            ],
            "active": [
                {"task_id": item.request.task_id, "campaign_id": item.request.campaign_id,
                 "agent_id": item.agent_id, "role": item.request.role,
                 "attempt": item.attempt, "state": item.state}
                for item in self.assignments.values()
            ],
            "campaign_quotas": {
                campaign_id: {
                    "max_parallel": quota.max_parallel,
                    "max_units": quota.max_units,
                    "consumed_units": quota.consumed_units,
                    "reserved_units": quota.reserved_units,
                }
                for campaign_id, quota in self.quotas.items()
            },
            "completed_task_ids": sorted(self.completed),
            "failed_task_ids": sorted(self.failed),
            "attempt_history": self.attempt_history,
        }
