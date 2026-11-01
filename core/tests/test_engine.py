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
    )
    assert finding.verification == VerificationState.INDEPENDENTLY_VERIFIED
    assert engine.publishable(finding)[0]
