from ssswet_core.models import Finding, VerificationState
from ssswet_core.orchestrator import ResearchOrchestrator
from ssswet_core.safety import SafetyGate
from ssswet_core.verification import VerificationEngine


def test_task_is_scheduled_to_a_bot():
    system = ResearchOrchestrator()
    task = system.submit("Solve a harmless mathematical problem")
    assignments = system.schedule()
    assert assignments
    assert assignments[0][1] == task.id


def test_two_independent_checks_can_verify_a_finding():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    finding = engine.independent_check(
        finding, "independent calculation A", "source-a",
        independence_group="calculation-method-a", independence_confirmed=True,
    )
    finding = engine.independent_check(
        finding, "independent calculation B", "source-b",
        independence_group="calculation-method-b", independence_confirmed=True,
    )
    assert finding.verification == VerificationState.INDEPENDENTLY_VERIFIED
    assert engine.is_publishable(finding)


def test_unverified_result_is_not_publishable():
    finding = Finding(task_id="t1", summary="candidate")
    allowed, reasons = SafetyGate().assess(finding)
    assert not allowed
    assert reasons
