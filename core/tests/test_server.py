from ssswet_core.engine import SSSWETEngine
from ssswet_core.server import public_status, public_events


def test_public_status_reports_real_empty_engine_state():
    engine = SSSWETEngine()
    status = public_status(engine)
    assert status["mode"] == "local_read_only"
    assert status["agents_total"] == 0
    assert status["agents_active"] == 0
    assert status["tasks_queued"] == 0


def test_public_events_contains_only_structured_event_summaries():
    engine = SSSWETEngine()
    engine.submit("A harmless test objective", "math")
    events = public_events(engine)
    assert events[-1]["kind"] == "task_created"
    assert events[-1]["message"] == "New research task queued."
