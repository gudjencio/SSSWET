from dataclasses import dataclass

from .contradiction import ContradictionDetector, ResearchClaim, ClaimConflict
from .context_aware_claim_comparison import ContextAwareClaimComparator, ClaimContext
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
from .research_opportunity import evaluate_research_opportunity, rank_research_opportunities
from .protective_system_scoring import calculate_protective_system_score, rank_protective_systems
from .technology_progression import evaluate_progression, persistence_status
from .agent_identity import AgentIdentityRegistry
from .review_assignment import IndependentReviewerSelector, ReviewerCandidate
from .research_decision_ledger import ResearchDecisionLedger


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
        self.agent_identities = AgentIdentityRegistry(store) if store else None
        self.research_decisions = ResearchDecisionLedger(store) if store else None
        self.independent_reviewer_selector = IndependentReviewerSelector()
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
        self.contextual_claim_comparator = ContextAwareClaimComparator()
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

    def propose_independent_reviewers(
        self, candidates: list[ReviewerCandidate], **selection_constraints
    ) -> dict:
        """Propose a diverse reviewer panel without executing assignments."""
        return self.independent_reviewer_selector.propose(candidates, **selection_constraints)

    def compare_contextual_claims(self, claims: list[ClaimContext]):
        """Compare structured claims without conflating different contexts."""
        return self.contextual_claim_comparator.compare(claims)

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

    def evaluate_research_opportunity(self, programme_id: str, inputs: dict) -> dict:
        if self.technology_dependencies is None:
            raise RuntimeError("A persistent research store is required for dependency-aware prioritisation")
        return evaluate_research_opportunity(
            programme_id, inputs, self.technology_dependencies.graph()
        )

    def rank_research_opportunities(self, opportunities: list[dict]) -> dict:
        if self.technology_dependencies is None:
            raise RuntimeError("A persistent research store is required for dependency-aware prioritisation")
        return rank_research_opportunities(
            opportunities, self.technology_dependencies.graph()
        )


    def record_research_decision(self, **decision_inputs) -> dict:
        """Record a source-linked decision without overwriting its history."""
        if self.research_decisions is None:
            raise RuntimeError("A persistent research store is required for decision lineage")
        return self.research_decisions.record(**decision_inputs)

    def transition_research_decision(self, decision_id: str, **transition_inputs) -> dict:
        """Append a constrained review-state transition to an existing decision."""
        if self.research_decisions is None:
            raise RuntimeError("A persistent research store is required for decision lineage")
        return self.research_decisions.transition(decision_id, **transition_inputs)

    def get_research_decision(self, decision_id: str) -> dict:
        if self.research_decisions is None:
            raise RuntimeError("A persistent research store is required for decision lineage")
        return self.research_decisions.get(decision_id)

    def research_decision_history(self, subject_id: str, *, limit: int = 100) -> list[dict]:
        if self.research_decisions is None:
            raise RuntimeError("A persistent research store is required for decision lineage")
        return self.research_decisions.history(subject_id, limit=limit)

    def record_agent_memory_review(self, **review_inputs) -> dict:
        """Append a provenance-linked review state to an agent memory."""
        if self.agent_identities is None:
            raise RuntimeError("A persistent research store is required for memory review")
        return self.agent_identities.record_memory_review(**review_inputs)
    def search_team_memories(self, query: str, *, limit: int = 12, agent_ids: list[str] | None = None) -> list[dict]:
        """Retrieve bounded, source-linked memories across the research team."""
        if self.agent_identities is None:
            raise RuntimeError("A persistent research store is required for team memory retrieval")
        return self.agent_identities.search_team_memories(
            query, limit=limit, agent_ids=agent_ids
        )

    def estimate_technology_costs(self, **pricing_inputs) -> dict:
        """Validate agent-submitted cost evidence through the independent pricing gate."""
        return build_agent_pricing_estimate(**pricing_inputs)

    def score_protective_system(self, **inputs):
        """Score a protective or assistive system only through evidence gates."""
        return calculate_protective_system_score(**inputs)

    @staticmethod
    def rank_protective_systems(scores):
        return rank_protective_systems(scores)

    @staticmethod
    def evaluate_technology_progression(previous, candidate, *, candidate_safety_gate, candidate_legality_gate):
        """Prevent documented capability regressions between technology revisions."""
        return evaluate_progression(
            previous,
            candidate,
            candidate_safety_gate=candidate_safety_gate,
            candidate_legality_gate=candidate_legality_gate,
        )

    @staticmethod
    def continue_research(reason: str) -> dict:
        """Record persistence without bypassing safety, law, ethics, or evidence."""
        return persistence_status(reason)

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
