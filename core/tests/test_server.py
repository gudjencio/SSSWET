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


def test_collective_memory_search_endpoint_is_read_only_and_traceable(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.collective_memory import CollectiveMemoryRecord
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "memory-api.sqlite3")
    store.save_collective_memory(CollectiveMemoryRecord.create(
        "memory-1", "wave propagation",
        "Compare published wave speed measurement methods",
        source_ids=("paper-1",),
    ))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/memory/search?q=wave%20speed") as response:
            payload = json.loads(response.read())
        assert payload["method"] == "lexical_overlap"
        assert payload["scientific_validity_established"] is False
        assert payload["results"][0]["memory_id"] == "memory-1"

        with urlopen(base + "/api/memory") as response:
            listing = json.loads(response.read())
        assert listing["items"][0]["source_ids"] == ["paper-1"]

        try:
            urlopen(base + "/api/memory/search")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An empty search query must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
