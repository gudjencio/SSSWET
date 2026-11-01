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


def test_public_knowledge_graph_endpoint_payload_is_available(tmp_path):
    from ssswet_core.knowledge_graph import KnowledgeNode
    from ssswet_core.persistence import SQLiteResearchStore

    store = SQLiteResearchStore(tmp_path / "public-graph.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        node_id="claim-1", node_type="hypothesis", label="Candidate claim"
    ))
    graph = store.knowledge_graph(limit=500)
    assert graph["nodes"][0]["node_id"] == "claim-1"
    assert graph["nodes"][0]["verification_state"] == "unverified"
