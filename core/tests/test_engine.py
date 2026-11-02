from ssswet_core.engine import SSSWETEngine
from ssswet_core.memory import KnowledgeMemory, MemoryItem
from ssswet_core.models import VerificationState
from ssswet_core.strategies import StrategySelector


def test_engine_creates_and_schedules_work():
    engine = SSSWETEngine()
    task = engine.submit("Compare two harmless mathematical derivations", domain="mathematics")
    assignments = engine.tick()
    assert assignments
    assert assignments[0][1] == task.id


def test_only_validated_memory_is_returned_as_validated():
    memory = KnowledgeMemory()
    memory.remember(MemoryItem("a", "validated statement", "test", validated=True))
    memory.remember(MemoryItem("b", "candidate statement", "test", validated=False))
    assert [item.key for item in memory.validated()] == ["a"]


def test_strategy_changes_when_previous_strategy_is_rejected():
    selector = StrategySelector()
    first = selector.next([])
    second = selector.next([first.name])
    assert second.name != first.name


def test_engine_can_reach_independent_verification():
    engine = SSSWETEngine()
    task = engine.submit("Verify a harmless arithmetic identity", domain="mathematics")
    finding = engine.prepare_finding(task, "candidate identity")
    finding = engine.verify_with_independent_evidence(
        finding,
        "calculation A",
        "calculation B",
        source_ids=("calculation-a", "calculation-b"),
        provenance_groups=("derivation-method-a", "derivation-method-b"),
        independence_confirmed=True,
    )
    assert finding.verification == VerificationState.INDEPENDENTLY_VERIFIED
    assert engine.publishable(finding)[0]


def test_engine_exposes_cross_agent_source_linked_memory_search(tmp_path):
    from ssswet_core.persistence import SQLiteResearchStore

    engine = SSSWETEngine(store=SQLiteResearchStore(tmp_path / "engine-team-memory.sqlite3"))
    saved = engine.agent_identities.remember(
        agent_id="mira-01", role="general_researcher",
        content="Composite materials require fatigue and thermal cycling evidence.",
        source_reference="doi:10.example/composite-fatigue",
    )
    results = engine.search_team_memories("composite materials fatigue thermal", limit=4)
    assert results
    assert results[0]["memory_id"] == saved["memory_id"]
    assert results[0]["source_reference"] == "doi:10.example/composite-fatigue"


def test_engine_requires_persistent_store_for_team_memory_search():
    import pytest

    engine = SSSWETEngine()
    with pytest.raises(RuntimeError, match="persistent research store"):
        engine.search_team_memories("materials")


def test_engine_exposes_context_aware_claim_comparison():
    from ssswet_core.contradiction import ResearchClaim
    from ssswet_core.context_aware_claim_comparison import ClaimContext

    engine = SSSWETEngine()
    claims = [
        ClaimContext(ResearchClaim("coating", "thickness", "120", "source-a"), scope="sample", unit="um"),
        ClaimContext(ResearchClaim("coating", "thickness", "105", "source-b"), scope="sample", unit="um"),
    ]
    result = engine.compare_contextual_claims(claims)
    assert len(result) == 1
    assert result[0].classification == "potential_conflict"


def test_engine_proposes_independent_reviewers_without_executing_assignment():
    from ssswet_core.review_assignment import ReviewerCandidate

    engine = SSSWETEngine()
    result = engine.propose_independent_reviewers(
        [
            ReviewerCandidate("reviewer-a", "independent_verifier", "campaign-a"),
            ReviewerCandidate("reviewer-b", "data_analyst", "campaign-b"),
        ],
        required_count=2,
    )
    assert result["status"] == "proposed"
    assert result["reviewer_assignment_executed"] is False
    assert result["independence_certified"] is False
