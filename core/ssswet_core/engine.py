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
from .technology_catalogue_500 import register_catalogue
from .technology_dependency_graph import TechnologyDependencyGraph
from .research_opportunity import evaluate_research_opportunity, rank_research_opportunities
from .protective_system_scoring import calculate_protective_system_score, rank_protective_systems
from .technology_progression import evaluate_progression, persistence_status
from .agent_identity import AgentIdentityRegistry
from .review_assignment import IndependentReviewerSelector, ReviewerCandidate
from .research_decision_ledger import ResearchDecisionLedger
from .research_knowledge_graph import ResearchKnowledgeGraph


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
        self.research_knowledge = ResearchKnowledgeGraph(store) if store else None
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
