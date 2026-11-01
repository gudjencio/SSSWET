from dataclasses import dataclass

from .memory import KnowledgeMemory
from .models import Finding, ResearchEvent, Task, TaskStatus, VerificationState
from .orchestrator import ResearchOrchestrator
from .safety import SafetyGate
from .strategies import StrategySelector
from .verification import VerificationEngine


@dataclass
class EngineSnapshot:
    queued_tasks: int
    active_agents: int
    remembered_items: int
    events: int


class SSSWETEngine:
    """Top-level coordination facade.

    External AI/model providers can be connected later through adapters. The
    core itself remains provider-agnostic and does not self-modify executable
    code at runtime.
    """

    def __init__(self) -> None:
        self.orchestrator = ResearchOrchestrator()
        self.memory = KnowledgeMemory()
        self.verifier = VerificationEngine()
        self.safety = SafetyGate()
        self.strategies = StrategySelector()
        self.simulated_findings: list[Finding] = []

    def submit(self, objective: str, domain: str = "general", priority: int = 5) -> Task:
        return self.orchestrator.submit(objective, domain, priority)

    def tick(self) -> list[tuple[str, str]]:
        """Advance scheduling by one safe orchestration cycle."""
        return self.orchestrator.schedule()

    def prepare_finding(self, task: Task, summary: str) -> Finding:
        finding = Finding(
            task_id=task.id,
            summary=summary,
            metadata={"domain": task.domain},
        )
        self.simulated_findings.append(finding)
        return finding

    def verify_with_independent_evidence(
        self,
        finding: Finding,
        *evidence: str,
        source_ids: tuple[str, ...] = (),
    ) -> Finding:
        current = finding
        for index, item in enumerate(evidence):
            source_id = source_ids[index] if index < len(source_ids) else None
            current = self.verifier.independent_check(current, item, source_id)
        return current

    def record_reproduction(self, finding: Finding, reproduction_id: str) -> Finding:
        return self.verifier.require_reproduction(finding, reproduction_id)

    def publishable(self, finding: Finding) -> tuple[bool, list[str]]:
        return self.safety.assess(finding)

    def snapshot(self) -> EngineSnapshot:
        active = sum(1 for a in self.orchestrator.bot_manager.agents.values() if a.load > 0)
        return EngineSnapshot(
            queued_tasks=len(self.orchestrator.tasks),
            active_agents=active,
            remembered_items=len(self.memory.export()),
            events=len(self.orchestrator.events),
        )
