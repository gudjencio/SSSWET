from dataclasses import dataclass

from .contradiction import ContradictionDetector, ResearchClaim, ClaimConflict
from .memory import KnowledgeMemory, MemoryItem
from .persistence import SQLiteResearchStore
from .models import Finding, ResearchEvent, Task
from .orchestrator import ResearchOrchestrator
from .safety import SafetyGate
from .strategies import StrategySelector
from .verification import VerificationEngine
from .pricing_evidence import build_agent_pricing_estimate
from .technology_dossier import TechnologyDossierRegistry
from .technology_catalogue import register_catalogue
from .technology_dependency_graph import TechnologyDependencyGraph


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

    def __init__(self, store: SQLiteResearchStore | None = None) -> None:
        self.store = store
        self.technology_dossiers = TechnologyDossierRegistry(store) if store else None
        self.technology_dependencies = TechnologyDependencyGraph(store) if store else None
        self.orchestrator = ResearchOrchestrator()
        self.memory = KnowledgeMemory()
        if self.store:
            for saved in self.store.knowledge_items():
                self.memory.remember(MemoryItem(**saved))
        self.verifier = VerificationEngine()
        self.safety = SafetyGate()
        self.strategies = StrategySelector()
        self.contradictions = ContradictionDetector()
        self._conflict_review_tasks: dict[tuple[str, str, tuple[str, ...]], str] = {}
        self.simulated_findings: list[Finding] = []

    def remember_knowledge(self, item: MemoryItem) -> None:
        self.memory.remember(item)
        if self.store:
            self.store.save_knowledge(item)

    def submit(self, objective: str, domain: str = "general", priority: int = 5) -> Task:
        return self.orchestrator.submit(objective, domain, priority)

    def tick(self) -> list[tuple[str, str]]:
        """Advance scheduling by one safe orchestration cycle."""
        return self.orchestrator.schedule()

    def prepare_finding(self, task: Task, summary: str) -> Finding:
        finding = Finding(task_id=task.id, summary=summary, metadata={"domain": task.domain})
        self.simulated_findings.append(finding)
        return finding

    def verify_with_independent_evidence(
        self,
        finding: Finding,
        *evidence: str,
        source_ids: tuple[str, ...] = (),
        provenance_groups: tuple[str, ...] = (),
        independence_confirmed: bool = False,
    ) -> Finding:
        current = finding
        for index, item in enumerate(evidence):
            source_id = source_ids[index] if index < len(source_ids) else None
            group = provenance_groups[index] if index < len(provenance_groups) else None
            current = self.verifier.independent_check(
                current,
                item,
                source_id,
                independence_group=group,
                independence_confirmed=independence_confirmed,
            )
        return current

    def record_reproduction(
        self,
        finding: Finding,
        reproduction_id: str,
        *,
        reproduction_confirmed: bool = False,
    ) -> Finding:
        return self.verifier.require_reproduction(
            finding, reproduction_id, reproduction_confirmed=reproduction_confirmed
        )

    def review_claims(
        self,
        claims: list[ResearchClaim],
        parent_task_id: str | None = None,
    ) -> list[ClaimConflict]:
        """Detect explicit disagreements and queue one independent review per conflict."""
        conflicts = self.contradictions.compare(claims)
        for conflict in conflicts:
            signature = (
                conflict.subject,
                conflict.predicate,
                tuple(sorted(conflict.values, key=str.casefold)),
            )
            if signature in self._conflict_review_tasks:
                continue
            objective = (
                f"Independently review conflicting claims about {conflict.subject} "
                f"({conflict.predicate}): {', '.join(conflict.values)}. "
                "Check source quality, methods, context and uncertainty; do not "
                "assume either claim is correct."
            )
            review_task = self.submit(objective, domain="verification", priority=1)
            self._conflict_review_tasks[signature] = review_task.id
            self.orchestrator.events.append(ResearchEvent(
                "disagreement_detected",
                "Conflicting sourced claims detected; an independent review was queued.",
                parent_task_id or review_task.id,
            ))
        return conflicts

    def register_technology_catalogue(self, actor_id: str = "catalogue") -> dict:
        if self.technology_dossiers is None:
            raise RuntimeError("A persistent research store is required for technology dossiers")
        return register_catalogue(self.technology_dossiers, actor_id=actor_id)

    def create_technology_dossier(self, **dossier_inputs) -> dict:
        if self.technology_dossiers is None:
            raise RuntimeError("A persistent research store is required for technology dossiers")
        return self.technology_dossiers.create(**dossier_inputs)

    def record_technology_event(self, **event_inputs) -> dict:
        if self.technology_dossiers is None:
            raise RuntimeError("A persistent research store is required for technology dossiers")
        return self.technology_dossiers.append_event(**event_inputs)

    def get_technology_dossier(self, technology_id: str) -> dict:
        if self.technology_dossiers is None:
            raise RuntimeError("A persistent research store is required for technology dossiers")
        return self.technology_dossiers.get(technology_id)

    def estimate_technology_costs(self, **pricing_inputs) -> dict:
        """Validate agent-submitted cost evidence through the independent pricing gate."""
        return build_agent_pricing_estimate(**pricing_inputs)

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
