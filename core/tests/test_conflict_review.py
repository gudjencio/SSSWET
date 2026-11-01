from ssswet_core.engine import SSSWETEngine
from ssswet_core.contradiction import ResearchClaim


def test_conflicts_queue_one_independent_review_task():
    engine = SSSWETEngine()
    claims = [
        ResearchClaim("sample", "measured_value", "12", "source-a"),
        ResearchClaim("sample", "measured_value", "15", "source-b"),
    ]
    conflicts = engine.review_claims(claims, parent_task_id="original-task")
    assert len(conflicts) == 1
    assert engine.snapshot().queued_tasks == 1
    assert any(event.kind == "disagreement_detected" for event in engine.orchestrator.events)

    # Reprocessing the same conflict must not create an unbounded task loop.
    engine.review_claims(claims, parent_task_id="original-task")
    assert engine.snapshot().queued_tasks == 1
