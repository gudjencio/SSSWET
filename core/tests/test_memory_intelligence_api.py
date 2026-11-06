import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.memory_intelligence import verify_memory_snapshot
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion
from ssswet_core.server import SSSWETEngine, make_handler
from ssswet_core.sources import SourceRecord


def test_scientific_memory_intelligence_read_only_endpoints(tmp_path):
    store = SQLiteResearchStore(tmp_path / "memory-intelligence-api.sqlite3")
    store.register_source(SourceRecord(
        "paper-1", "Wave propagation measurement", provenance_group="lab-a"
    ))
    store.register_source(SourceRecord(
        "paper-2", "Wave propagation measurement replication", provenance_group="lab-b"
    ))
    store.add_knowledge_node(KnowledgeNode("claim-a", "hypothesis", "Initial wave claim"))
    store.add_knowledge_node(KnowledgeNode("claim-b", "finding", "Conflicting wave observation"))
    store.add_knowledge_edge(KnowledgeEdge(
        "claim-a", "claim-b", "contradicts",
        note="A later observation reports a different value.", confidence=0.7,
    ))
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "wave-v1", "wave-claim", "Wave propagation",
        "Measured wave speed in water", source_ids=("paper-1",),
        graph_node_ids=("claim-a",), status="contested",
    ))
    service.add_version(ScientificMemoryVersion.create(
        "wave-copy-v1", "wave-claim-copy", "Wave propagation",
        "Measured wave speed in water", source_ids=("paper-2",),
    ))

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/scientific-memory/search?q=wave%20speed") as response:
            search = json.loads(response.read())
        assert search["retrieval_method"] == "weighted_fielded_lexical_v1"
        assert len(search["results"]) == 2
        assert search["results"][0]["version_id"] == "wave-v1"

        with urlopen(base + "/api/scientific-memory/context?q=wave&token_budget=1000") as response:
            context = json.loads(response.read())
        assert context["record_count"] == 2
        assert context["provenance_retained"] is True
        assert all(item["source_ids"] for item in context["records"])

        with urlopen(base + "/api/scientific-memory/integrity") as response:
            integrity = json.loads(response.read())
        assert integrity["records_audited"] == 2
        assert integrity["missing_link_counts"]["source_ids"] == 0
        assert integrity["independence_established"] is False

        with urlopen(base + "/api/scientific-memory/duplicates?threshold=0.8") as response:
            duplicates = json.loads(response.read())
        assert duplicates["candidate_count"] == 1
        assert duplicates["automatic_merge"] is False

        with urlopen(base + "/api/scientific-memory/conflicts") as response:
            conflicts = json.loads(response.read())
        assert conflicts["case_count"] == 1
        assert conflicts["cases"][0]["version_id"] == "wave-v1"
        assert conflicts["automatic_adjudication"] is False

        with urlopen(base + "/api/scientific-memory/snapshot") as response:
            snapshot = json.loads(response.read())
        assert snapshot["record_count"] == 2
        assert verify_memory_snapshot(snapshot)["valid"] is True

        try:
            urlopen(base + "/api/scientific-memory/search")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An empty memory search must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
