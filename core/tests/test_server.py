import pytest
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



def test_literature_watch_history_endpoint_is_read_only(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.literature_watch import LiteratureWatchService
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.providers import ProviderResult
    from ssswet_core.server import make_handler

    class Provider:
        name = "test-provider"
        def investigate(self, objective, strategy):
            return ProviderResult("Metadata only", evidence=("A paper | DOI: 10.55/test",), source_ids=("10.55/test",))

    store = SQLiteResearchStore(tmp_path / "watch-api.sqlite3")
    report = LiteratureWatchService(Provider(), store).run("test topic")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/literature-watch") as response:
            payload = json.loads(response.read())
        assert payload["reports"][0]["watch_id"] == report.watch_id
        assert payload["reports"][0]["scientific_validity_established"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_scientific_memory_api_exposes_versions_and_review_suggestions(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "scientific-memory-api.sqlite3")
    store.add_knowledge_node(KnowledgeNode("claim-a", "finding", "Claim A"))
    store.add_knowledge_node(KnowledgeNode("claim-b", "finding", "Claim B"))
    store.add_knowledge_edge(KnowledgeEdge("claim-a", "claim-b", "contradicts"))
    ScientificMemoryService(store).add_version(ScientificMemoryVersion.create(
        "version-a1", "claim-a-memory", "Claim A", "A candidate wave-speed claim",
        graph_node_ids=("claim-a",),
    ))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/scientific-memory?q=wave%20speed") as response:
            payload = json.loads(response.read())
        assert payload["versions"][0]["version_id"] == "version-a1"
        assert payload["versions"][0]["contested_by_graph"] is True
        assert payload["scientific_validity_established"] is False

        with urlopen(base + "/api/scientific-memory/suggestions") as response:
            suggestions = json.loads(response.read())
        assert suggestions["contested_memory"][0]["version_id"] == "version-a1"
        assert suggestions["automatic_task_creation"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_research_timeline_endpoint_returns_chronological_records(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.knowledge_graph import KnowledgeNode
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler
    from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion

    store = SQLiteResearchStore(tmp_path / "timeline-api.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "finding-1", "finding", "First recorded finding",
        created_at="2026-09-01T12:00:00+00:00",
    ))
    ScientificMemoryService(store).add_version(ScientificMemoryVersion.create(
        "memory-1", "wave-topic", "Wave topic", "A candidate research statement",
    ))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/research-timeline") as response:
            payload = json.loads(response.read())
        assert payload["total_events"] == 2
        assert payload["chronology_is_not_validation"] is True
        assert {item["kind"] for item in payload["events"]} == {
            "knowledge_recorded", "memory_version"
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_peer_review_api_reports_assessments_without_verifying_claims(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.knowledge_graph import KnowledgeNode
    from ssswet_core.peer_review import PeerReviewService
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "peer-review-api.sqlite3")
    for cid in ("source", "reviewer"):
        campaign = create_campaign(
            cid, cid, "Review wave propagation", "physics",
            [CampaignMilestone("m1", "Review", "Review methods")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    store.add_knowledge_node(KnowledgeNode(
        "claim", "finding", "Candidate claim",
        metadata={"campaign_id": "source"},
    ))
    service = PeerReviewService(store)
    service.request(
        "review", "source", "claim", ["reviewer"], "operator",
        "Can the method be independently reproduced?",
    )
    service.submit(
        "submission", "review", "reviewer", "inconclusive",
        "The available information is insufficient.",
        "Independent method review", independence_confirmed=True,
    )
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/collaboration/peer-reviews") as response:
            payload = json.loads(response.read())
        assert payload["reviews"][0]["submission_count"] == 1
        assert payload["reviews"][0]["outcome_summary"]["inconclusive"] == 1
        assert payload["reviews"][0]["independence_independently_verified"] is False
        assert payload["scientific_validity_established"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_digital_lab_api_lists_published_protocols_and_recorded_runs(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.digital_lab import DigitalLabService, LabProtocol, LabRun
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "digital-lab-api.sqlite3")
    for cid in ("owner", "replica", "replica-2"):
        campaign = create_campaign(
            cid, cid, "Digital laboratory testing", "computational science",
            [CampaignMilestone("m1", "Review", "Review protocol")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    service = DigitalLabService(store)
    service.publish_protocol(LabProtocol(
        "protocol-api", 1, "API protocol", "Test a simple calculation", "owner",
        ("Set input", "Calculate output"), ("x",), ("y",), {"x": "unitless"},
        ("Same initial conditions",), ("Illustrative model only",),
        ("No physical experiment is performed",), "published",
        "reviewer", "Reviewed for clarity.",
    ))
    service.record_run(LabRun(
        "run-api", "protocol-api", 1, "replica", "simulation",
        {"x": 2}, {"y": 4}, "y = 2x", {"runtime": "Python"},
        "model-v1", "replica-group", True,
    ))
    service.record_run(LabRun(
        "run-api-2", "protocol-api", 1, "replica-2", "simulation",
        {"x": 2}, {"y": 4}, "y = 2x", {"runtime": "Python"},
        "model-v1", "replica-2-group", True,
    ))
    service.compare_runs("run-api", "run-api-2")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/digital-lab") as response:
            payload = json.loads(response.read())
        assert payload["protocol_count"] == 1
        assert payload["run_count"] == 2
        assert payload["comparison_count"] == 1
        assert payload["comparisons"][0]["scientific_validity_established"] is False
        assert payload["protocols"][0]["content_hash"]
        assert payload["runs"][0]["record_hash"]
        assert payload["automatic_execution"] is False
        assert payload["scientific_validity_established"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_digital_lab_reproduction_matrix_endpoint_is_read_only(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.digital_lab import DigitalLabService, LabProtocol, LabRun
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "reproduction-matrix-api.sqlite3")
    for campaign_id in ("source", "team-a", "team-b"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Reproduction study", "computational science",
            [CampaignMilestone("m1", "Review", "Review protocol")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    service = DigitalLabService(store)
    service.publish_protocol(LabProtocol(
        "protocol", 1, "Numerical protocol", "Compare an illustrative output",
        "source", ("Apply declared equation",), ("input",), ("output",),
        {}, ("Same input",), ("Illustrative only",), ("No physical experiment",),
        "published", "reviewer", "Reviewed for clarity",
    ))
    for run_id, campaign_id in (("run-a", "team-a"), ("run-b", "team-b")):
        service.record_run(LabRun(
            run_id, "protocol", 1, campaign_id, "simulation",
            {"input": 2}, {"output": 4}, "y=2x", {"runtime": "Python"},
            "model-v1", campaign_id + "-lab", True,
        ))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/digital-lab/reproduction-matrix") as response:
            payload = json.loads(response.read())
        group = payload["protocol_groups"][0]
        assert group["distinct_campaign_count"] == 2
        assert group["pending_comparison_count"] == 1
        assert payload["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/digital-lab/reproduction-matrix?limit=invalid")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("Invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_digital_lab_protocol_proposals_api_is_read_only(tmp_path):
    import json
    import threading
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.digital_lab import DigitalLabService, LabProtocol
    from ssswet_core.protocol_proposals import ProtocolProposalService
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "protocol-proposals-api.sqlite3")
    for campaign_id in ("owner", "proposer"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Protocol review", "computational science",
            [CampaignMilestone("m1", "Review", "Review protocol")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    DigitalLabService(store).publish_protocol(LabProtocol(
        "shared-protocol", 1, "Shared model", "Record a numerical output",
        "owner", ("Run declared equation",), ("input",), ("output",),
        {}, ("same input",), ("Illustrative only",), ("No physical experiment",),
        "published", "reviewer", "Reviewed for clarity",
    ))
    ProtocolProposalService(store).submit(
        "proposal-api", "shared-protocol", 1, "proposer",
        {"objective": "Record and compare a numerical output"},
        "Clarify the objective.",
    )
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/digital-lab/proposals") as response:
            payload = json.loads(response.read())
        assert payload["pending_count"] == 1
        assert payload["proposals"][0]["proposal_id"] == "proposal-api"
        assert payload["proposal_acceptance_establishes_scientific_validity"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_research_opportunities_endpoint_combines_review_leads(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.knowledge_graph import KnowledgeNode
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "research-opportunities-api.sqlite3")
    store.add_knowledge_node(KnowledgeNode(
        "hypothesis-api", "hypothesis", "Wave propagation measurement",
        "Estimate wave speed from repeated observations",
        metadata={"campaign_id": "physics"},
    ))
    store.add_knowledge_node(KnowledgeNode(
        "finding-api", "finding", "Wave propagation measurement",
        "Estimate wave speed from repeated observations",
        metadata={"campaign_id": "engineering"},
    ))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/research-opportunities") as response:
            payload = json.loads(response.read())
        assert payload["signal_counts"]["interdisciplinary_links"] == 1
        assert payload["requires_human_review"] is True
        assert payload["automatic_task_creation"] is False
        assert payload["graph_mutated"] is False
        assert payload["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/research-opportunities?limit=invalid")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("Invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_lab_verification_plans_endpoint_is_read_only(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.digital_lab import DigitalLabService, LabProtocol, LabRun
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "lab-verification-api.sqlite3")
    for campaign_id in ("owner", "team-a", "team-b"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Verification planning", "computational science",
            [CampaignMilestone("m1", "Review", "Review the recorded model")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    service = DigitalLabService(store)
    service.publish_protocol(LabProtocol(
        "verification-protocol", 1, "Numerical model", "Compare declared outputs",
        "owner", ("Record input", "Run model"), ("input",), ("output",),
        {}, ("same initial condition",), ("Illustrative only",),
        ("No physical execution is performed",), "published", "reviewer", "Reviewed",
    ))
    def run(run_id, campaign_id, output, environment):
        return LabRun(
            run_id, "verification-protocol", 1, campaign_id, "simulation",
            {"input": 1}, {"output": output}, "Declared numerical model",
            environment, "model-v1", campaign_id + "-provenance", True,
        )
    service.record_run(run("run-a", "team-a", 1, {"runtime": "A"}))
    service.record_run(run("run-b", "team-b", 2, {"runtime": "B"}))
    service.compare_runs("run-a", "run-b", tolerance=0.0)

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/lab-verification-plans") as response:
            payload = json.loads(response.read())
        assert payload["count"] == 1
        codes = {item["code"] for item in payload["plans"][0]["checks"]}
        assert "environment" in codes
        assert "measurement_and_tolerance" in codes
        assert payload["automatic_execution"] is False
        assert payload["automatic_task_creation"] is False
        assert payload["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/lab-verification-plans?limit=invalid")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("Invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_scientific_review_board_api_preserves_independent_reviews(tmp_path):
    import json
    import threading
    from urllib.request import Request, urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.evidence_dossiers import EvidenceDossierService
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "scientific-review-api.sqlite3")
    EvidenceDossierService(store).assemble("dossier-api", "Evidence dossier", "A recorded result.")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        for reviewer, verdict in (("reviewer-a", "supports"), ("reviewer-b", "challenges")):
            body = json.dumps({
                "dossier_id": "dossier-api", "reviewer_id": reviewer,
                "verdict": verdict, "conflict_status": "none_declared",
                "rationale": "Assessment based on the dossier records.",
                "methods_assessment": "The method is described but needs independent scrutiny.",
                "limitations": "The assessment is limited to the supplied dossier.",
                "evidence_refs": ["source-1"],
            }).encode()
            request = Request(base + "/api/scientific-review-board/reviews", data=body,
                              headers={"Content-Type": "application/json", **auth}, method="POST")
            with urlopen(request) as response:
                assert response.status == 201
        with urlopen(base + "/api/scientific-review-board?dossier_id=dossier-api") as response:
            report = json.loads(response.read())
        assert report["count"] == 2
        assert report["summaries"][0]["disagreement_recorded"] is True
        assert report["automatic_adjudication"] is False
        assert report["scientific_validity_established"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_reproducibility_intelligence_api_returns_read_only_report(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "reproducibility-api.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/reproducibility-intelligence") as response:
            report = json.loads(response.read())
        assert report["protocols"] == []
        assert report["read_only"] is True
        assert report["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/reproducibility-intelligence?limit=0")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_parameter_sensitivity_plans_api_is_read_only(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "parameter-sensitivity-api.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/parameter-sensitivity-plans") as response:
            report = json.loads(response.read())
        assert report["plans"] == []
        assert report["read_only"] is True
        assert report["automatic_execution"] is False
        assert report["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/parameter-sensitivity-plans?limit=0")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_parameter_interaction_plans_api_is_read_only(tmp_path):
    import json
    import threading
    from http.server import ThreadingHTTPServer
    from urllib.error import HTTPError
    from urllib.request import urlopen

    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "parameter-interaction-api.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/parameter-interaction-plans") as response:
            report = json.loads(response.read())
        assert report["plans"] == []
        assert report["read_only"] is True
        assert report["automatic_execution"] is False
        assert report["scientific_validity_established"] is False
        try:
            urlopen(base + "/api/parameter-interaction-plans?limit=0")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_lab_statistical_summaries_api_is_read_only(tmp_path):
    import json
    import threading
    from http.server import ThreadingHTTPServer
    from urllib.error import HTTPError
    from urllib.request import urlopen

    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "lab-statistics-api.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/lab-statistical-summaries") as response:
            report = json.loads(response.read())
        assert report["summaries"] == []
        assert report["read_only"] is True
        assert report["automatic_data_exclusion"] is False
        assert report["inferential_tests_performed"] is False
        try:
            urlopen(base + "/api/lab-statistical-summaries?limit=0")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("An invalid limit must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_research_journal_api_lists_entries_and_accepts_local_append(tmp_path):
    import json
    import threading
    from urllib.request import Request, urlopen
    from http.server import ThreadingHTTPServer
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "journal-api.sqlite3")
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        payload = {
            "technology": "timetravel", "event_type": "research_question",
            "title": "Causality review", "summary": "Document known constraints first.",
            "classification": "hypothesis", "evidence_refs": ["doi:10.example/1"],
        }
        request = Request(base + "/api/research-journal", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request) as response:
            created = json.loads(response.read())
            assert response.status == 201
        assert created["scientific_validity_established"] is False
        with urlopen(base + "/api/research-journal?technology=timetravel") as response:
            report = json.loads(response.read())
        assert report["count"] == 1
        assert report["chain_integrity"]["chain_intact"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_private_order_api_is_loopback_only_and_tracks_verified_payments(tmp_path):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    from http.server import ThreadingHTTPServer

    from ssswet_core.order_registry import PrivateOrderRegistry
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "orders-api-research.sqlite3")
    orders = PrivateOrderRegistry(tmp_path / "orders-api.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(SSSWETEngine(store=store), store, orders, "test-admin-token-that-is-at-least-32-characters"),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(HTTPError) as unauthorized:
            urlopen(base + "/api/private/orders")
        assert unauthorized.value.code == 401
        auth = {"X-SSSWET-Admin-Token": "test-admin-token-that-is-at-least-32-characters"}
        request = Request(
            base + "/api/private/orders",
            data=json.dumps({
                "technology": "time-travel", "currency": "EUR",
                "base_price": "80.00", "access_contribution": "8.00",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            order = json.loads(response.read())["order"]
            assert response.status == 201
        order_id = order["order_id"]

        payment = Request(
            base + f"/api/private/orders/{order_id}/payments",
            data=json.dumps({
                "amount": "88.00", "currency": "EUR", "provider": "PayPal",
                "provider_reference": "verified-ref-1", "verified_by": "local operator",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(payment) as response:
            result = json.loads(response.read())["order"]
        assert result["state"] == "paid"
        assert result["balance_minor"] == 0

        with urlopen(Request(base + f"/api/private/orders/{order_id}", headers=auth)) as response:
            detail = json.loads(response.read())
        assert detail["delivery_address_stored"] is False
        assert detail["payments"][0]["provider_reference"] == "verified-ref-1"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
