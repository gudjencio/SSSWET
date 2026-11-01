from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    WORKING = "working"
    VERIFYING = "verifying"
    WAITING = "waiting"
    BLOCKED = "blocked"
    PAUSED = "paused"
    RETIRED = "retired"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    VERIFICATION = "verification"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    REJECTED = "rejected"


class VerificationState(str, Enum):
    HYPOTHESIS = "hypothesis"
    CANDIDATE = "candidate"
    SIMULATED = "simulated"
    INDEPENDENTLY_VERIFIED = "independently_verified"
    REPRODUCED = "reproduced"
    REQUIRES_REAL_WORLD_VALIDATION = "requires_real_world_validation"
    REJECTED = "rejected"


@dataclass
class Task:
    id: str
    objective: str
    domain: str = "general"
    priority: int = 5
    status: TaskStatus = TaskStatus.QUEUED
    attempts: int = 0
    strategy_history: list[str] = field(default_factory=list)


@dataclass
class Agent:
    id: str
    role: str
    status: AgentStatus = AgentStatus.WAITING
    load: float = 0.0
    current_task: str | None = None
    completed_tasks: int = 0


@dataclass
class Finding:
    task_id: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    verification: VerificationState = VerificationState.HYPOTHESIS
    uncertainty: float = 1.0
    limitations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchEvent:
    kind: str
    message: str
    task_id: str | None = None
    agent_id: str | None = None
