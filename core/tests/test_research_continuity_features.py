from __future__ import annotations

import json
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from ssswet_core.dataset_registry import DatasetRegistry, DatasetVersion
from ssswet_core.governed_reproducibility import build_governed_manifest
from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.knowledge_graph_neighborhood import build_neighborhood
from ssswet_core.literature_watch import LiteratureWatchReport, WatchCandidate
from ssswet_core.literature_watch_diff import compare_watch_reports
from ssswet_core.memory_retrieval_evaluation import evaluate_retrieval
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.reproducibility_manifest import verify_manifest
from ssswet_core.research_context_pack import build_research_context
from ssswet_core.research_review_queue import build_review_queue
from ssswet_core.scientific_memory import ScientificMemoryService, ScientificMemoryVersion
from ssswet_core.server import make_handler
from ssswet_core.sources import SourceRecord


def _campaign(store, campaign_id="campaign-a"):
    from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
    campaign = create_campaign(
        campaign_id, campaign_id, "Research continuity test", "general",
        [CampaignMilestone("m1", "Review", "Review evidence")],
    )
    store.save_campaign(set_campaign_state(campaign, "active"))


def _source(store, source_id="paper-1"):
    store.register_source(SourceRecord(
        source_id=source_id,
        title="A recorded source about wave propagation",
        url="https://example.org/paper",
        source_type="journal",
        doi="10.1234/waves",
        provenance_group="publisher-a",
    ))


def _memory_fixture(tmp_path):
    store = SQLiteResearchStore(tmp_path / "context.sqlite3")
    store.add_knowledge_node(KnowledgeNode("claim-a", "finding", "Candidate wave speed"))
    store.add_knowledge_node(KnowledgeNode("claim-b", "finding", "Conflicting wave speed"))
    store.add_knowledge_edge(KnowledgeEdge(
        "claim-a", "claim-b", "contradicts",
        note="Different measurement methods", confidence=0.7,
    ))
    _source(store)
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "memory-v1", "wave-speed", "Wave propagation",
        "A candidate wave-speed statement for review",
        graph_node_ids=("claim-a",), source_ids=("paper-1",),
    ))
    return store


def test_research_context_pack_keeps_provenance_and_linked_contradictions(tmp_path):
    store = _memory_fixture(tmp_path)
    first = build_research_context(store, "wave propagation", limit=10, max_chars=8_000)
    second = build_research_context(store, "wave propagation", limit=10, max_chars=8_000)
    assert first["memories"][0]["version_id"] == "memory-v1"
    assert first["sources"][0]["source_id"] == "paper-1"
    assert first["contradictions"][0]["target_id"] == "claim-b"
    assert first["context_sha256"] == second["context_sha256"]
    assert first["used_chars"] <= first["budget_chars"]
    assert first["scientific_validity_established"] is False
    assert first["automatic_adjudication"] is False


def test_context_pack_retrieval_quality_provenance_contradiction_latency_and_storage(tmp_path):
    store = _memory_fixture(tmp_path)
    started = time.perf_counter()
    pack = build_research_context(store, "wave propagation", limit=10, max_chars=8_000)
    latency_ms = (time.perf_counter() - started) * 1000
    retrieved_ids = [item["version_id"] for item in pack["memories"]]
    metrics = evaluate_retrieval(
        [{
            "query_id": "wave-propagation",
            "relevant_ids": ["memory-v1"],
            "retrieved_ids": retrieved_ids,
            "contradictory_ids": ["memory-v1"],
            "latency_ms": latency_ms,
        }],
        top_k=10,
        provenance_groups={"memory-v1": "publisher-a"},
        storage_bytes=store.path.stat().st_size,
    )
    assert metrics["aggregate"]["precision_at_k"] > 0
    assert metrics["aggregate"]["recall_at_k"] == 1.0
    assert metrics["aggregate"]["provenance_group_recall_at_k"] == 1.0
    assert metrics["aggregate"]["contradiction_retention_at_k"] == 1.0
    assert metrics["latency_ms"]["sample_count"] == 1
    assert metrics["storage_bytes"] > 0


def test_research_context_pack_is_bounded_and_rejects_invalid_budgets(tmp_path):
    store = _memory_fixture(tmp_path)
    result = build_research_context(store, "wave", limit=1, max_chars=2_000)
    assert result["used_chars"] <= 2_000
    assert result["budget_chars"] == 2_000
    with pytest.raises(ValueError):
        build_research_context(store, "wave", limit=0)
    with pytest.raises(ValueError):
        build_research_context(store, "wave", max_chars=100)


def test_graph_neighborhood_traverses_bounded_edges_and_keeps_contradictions():
    graph = {
        "nodes": [
            {"node_id": "a", "label": "A"},
            {"node_id": "b", "label": "B"},
            {"node_id": "c", "label": "C"},
            {"node_id": "d", "label": "D"},
        ],
        "edges": [
            {"source_id": "a", "target_id": "b", "relation": "supports"},
            {"source_id": "a", "target_id": "c", "relation": "contradicts"},
            {"source_id": "c", "target_id": "d", "relation": "related_to"},
        ],
    }
    result = build_neighborhood(graph, ["a"], depth=1, max_nodes=10, max_edges=10)
    assert {item["node_id"] for item in result["nodes"]} == {"a", "b", "c"}
    assert result["edges"][0]["relation"] == "contradicts"
    assert result["contradiction_edge_count"] == 1
    assert result["scientific_validity_established"] is False


def test_graph_neighborhood_reports_missing_seeds_and_truncation():
    graph = {
        "nodes": [{"node_id": "a"}, {"node_id": "b"}, {"node_id": "c"}],
        "edges": [
            {"source_id": "a", "target_id": "b", "relation": "supports"},
            {"source_id": "a", "target_id": "c", "relation": "contradicts"},
        ],
    }
    result = build_neighborhood(graph, ["a", "missing"], depth=2, max_nodes=1, max_edges=1)
    assert result["missing_seed_ids"] == ["missing"]
    assert result["node_count"] == 1
    assert result["truncated"] is True
    with pytest.raises(ValueError):
        build_neighborhood(graph, ["a"], depth=4)


def test_review_queue_prioritizes_contradictions_and_dataset_governance(tmp_path):
    store = _memory_fixture(tmp_path)
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "sensitive-set", 1, "Sensitive research metadata",
        "Metadata-only record", "campaign-a", "CC-BY-4.0", ("paper-1",),
        "a" * 64, privacy_classification="personal_data",
        consent_status="pending", retention_policy="Review after 30 days",
        access_scope="restricted",
    ))
    report = build_review_queue(store, limit=50)
    memory_item = next(item for item in report["items"] if item["entity_id"] == "memory-v1")
    dataset_item = next(item for item in report["items"] if item["entity_id"] == "sensitive-set@1")
    assert memory_item["priority"] == "critical"
    assert "linked_graph_contradiction" in memory_item["reason_codes"]
    assert dataset_item["priority"] == "high"
    assert "dataset_governance_review" in dataset_item["reason_codes"]
    assert report["automatic_task_creation"] is False
    assert report["scientific_validity_established"] is False


def test_review_queue_is_bounded_and_deterministic(tmp_path):
    store = _memory_fixture(tmp_path)
    first = build_review_queue(store, limit=1)
    second = build_review_queue(store, limit=1)
    assert first["items"] == second["items"]
    assert first["item_count"] <= 1
    with pytest.raises(ValueError):
        build_review_queue(store, limit=0)


def _watch(watch_id, candidates, created_at):
    return {
        "watch_id": watch_id,
        "query": "wave propagation",
        "created_at": created_at,
        "candidates": candidates,
    }


def test_literature_watch_diff_distinguishes_new_absent_and_changed_records():
    older = _watch("old", [
        {"candidate_id": "a1", "source_id": "10.1234/a", "doi": "10.1234/a",
         "title": "Original title", "provider": "crossref", "classification": "candidate_for_review"},
        {"candidate_id": "b1", "source_id": "10.1234/b", "doi": "10.1234/b",
         "title": "No longer listed", "provider": "crossref"},
    ], "2026-11-10T00:00:00+00:00")
    newer = _watch("new", [
        {"candidate_id": "a2", "source_id": "10.1234/a", "doi": "10.1234/a",
         "title": "Revised metadata title", "provider": "crossref", "classification": "candidate_for_review"},
        {"candidate_id": "c1", "source_id": "10.1234/c", "doi": "10.1234/c",
         "title": "New paper", "provider": "openalex"},
    ], "2026-11-11T00:00:00+00:00")
    result = compare_watch_reports(older, newer)
    assert result["counts"] == {
        "added": 1, "absent_from_newer": 1, "metadata_changed": 1, "ambiguous": 0,
    }
    assert result["absence_is_not_retraction"] is True
    assert result["metadata_change_is_not_a_correction"] is True
    assert result["memory_changed"] is False


def test_literature_watch_diff_flags_ambiguous_identity_without_merging():
    report = _watch("same", [
        {"source_id": "10.1234/x", "doi": "10.1234/x", "title": "One"},
        {"source_id": "doi:10.1234/x", "doi": "10.1234/x", "title": "Two"},
    ], "2026-11-11T00:00:00+00:00")
    result = compare_watch_reports(report, report)
    assert result["counts"]["ambiguous"] == 1
    assert result["added"] == []
    with pytest.raises(ValueError):
        compare_watch_reports({}, {"candidates": [None]})


def test_dataset_governance_gate_creates_verifiable_manifest_for_public_dataset(tmp_path):
    store = SQLiteResearchStore(tmp_path / "governed.sqlite3")
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "public-data", 1, "Public environmental observations",
        "Public metadata-only dataset", "campaign-a", "CC-BY-4.0", ("paper-1",),
        "b" * 64, privacy_classification="public",
        consent_status="not_required", retention_policy="Public archive",
        access_scope="public",
    ))
    result = build_governed_manifest(
        store,
        protocol_id="protocol-1",
        protocol_version=1,
        dataset_refs=[{"dataset_id": "public-data", "version": 1}],
        software_version="SSSWET test",
        parameters={"method": "deterministic"},
        source_ids=["paper-1"],
        publication_scope="public",
        random_seed=42,
    )
    assert result["eligible_for_manifest"] is True
    assert result["manifest_created"] is True
    assert verify_manifest(result["manifest"])["valid"] is True
    assert result["legal_compliance_established"] is False


def test_dataset_governance_gate_blocks_withdrawn_and_unapproved_personal_data(tmp_path):
    store = SQLiteResearchStore(tmp_path / "governed-block.sqlite3")
    _campaign(store)
    registry = DatasetRegistry(store)
    registry.register_version(DatasetVersion(
        "pending-personal", 1, "Personal dataset",
        "Restricted test record", "campaign-a", "CC-BY-4.0", (),
        "c" * 64, privacy_classification="personal_data",
        consent_status="pending", retention_policy="Review",
        access_scope="restricted",
    ))
    registry.register_version(DatasetVersion(
        "withdrawn-public", 1, "Withdrawn dataset",
        "Public-looking test record", "campaign-a", "CC-BY-4.0", (),
        "d" * 64, privacy_classification="public",
        consent_status="withdrawn", retention_policy="Review",
        access_scope="public",
    ))
    pending = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "pending-personal", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="project",
    )
    withdrawn = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "withdrawn-public", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="public",
    )
    assert pending["manifest_created"] is False
    assert "personal_or_sensitive_data_lacks_recorded_basis" in {
        item["code"] for item in pending["blocking_issues"]
    }
    assert withdrawn["manifest_created"] is False
    assert "consent_withdrawn" in {item["code"] for item in withdrawn["blocking_issues"]}


def test_scientific_memory_lineage_pages_are_bounded_and_complete_without_overlap(tmp_path):
    store = SQLiteResearchStore(tmp_path / "lineage.sqlite3")
    service = ScientificMemoryService(store)
    service.add_version(ScientificMemoryVersion.create(
        "version-0", "memory-key", "Research topic", "Initial candidate statement",
    ))
    previous = "version-0"
    for index in range(1, 36):
        current = f"version-{index}"
        service.revise(
            previous, current,
            statement=f"Revision {index}",
            review_note=f"Recorded review note {index}",
        )
        previous = current

    first = service.lineage_page("version-35", limit=10)
    assert first["page_count"] == 10
    assert first["items"][0]["version_id"] == "version-35"
    pages = [first]
    while pages[-1]["has_more_predecessors"]:
        pages.append(service.lineage_page(
            "version-35", limit=10,
            before_version_number=pages[-1]["next_before_version_number"],
        ))
    ids = [item["version_id"] for page in pages for item in page["items"]]
    assert len(ids) == 36
    assert len(set(ids)) == 36
    assert first["retrieval_is_sql_bounded"] is True
    assert pages[-1]["revision_chain_is_complete"] is True
    with pytest.raises(ValueError):
        service.lineage_page("version-35", limit=101)


def test_governed_manifest_requires_a_traceable_basis_for_personal_data(tmp_path):
    store = SQLiteResearchStore(tmp_path / "personal-governed.sqlite3")
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "personal-approved", 1, "Restricted personal dataset",
        "Metadata-only governance record", "campaign-a", "CC-BY-4.0", (),
        "e" * 64, metadata={"consent_basis_reference": "internal-review-record-2026-11"},
        privacy_classification="personal_data", consent_status="documented",
        retention_policy="Project review date recorded", access_scope="project",
    ))
    result = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "personal-approved", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="project",
    )
    assert result["manifest_created"] is True
    assert result["manifest"]["dataset_refs"][0]["privacy_classification"] == "personal_data"

    store2 = SQLiteResearchStore(tmp_path / "personal-no-reference.sqlite3")
    _campaign(store2)
    DatasetRegistry(store2).register_version(DatasetVersion(
        "personal-no-reference", 1, "Personal dataset",
        "Metadata-only governance record", "campaign-a", "CC-BY-4.0", (),
        "f" * 64, privacy_classification="personal_data", consent_status="documented",
        retention_policy="Project review date recorded", access_scope="project",
    ))
    blocked = build_governed_manifest(
        store2, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "personal-no-reference", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="project",
    )
    assert blocked["manifest_created"] is False
    assert "consent_basis_reference_missing" in {
        item["code"] for item in blocked["blocking_issues"]
    }


def test_governed_manifest_requires_dataset_content_digest(tmp_path):
    store = SQLiteResearchStore(tmp_path / "missing-digest.sqlite3")
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "no-digest", 1, "Public dataset without a digest",
        "Metadata-only governance record", "campaign-a", "CC-BY-4.0", (),
        privacy_classification="public", consent_status="not_required",
        retention_policy="Public archive", access_scope="public",
    ))
    result = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "no-digest", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="public",
    )
    assert result["manifest_created"] is False
    assert "content_digest_not_recorded" in {
        item["code"] for item in result["blocking_issues"]
    }


def test_governed_manifest_blocks_tampered_dataset_record(tmp_path, monkeypatch):
    store = SQLiteResearchStore(tmp_path / "tampered.sqlite3")
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "tampered-data", 1, "Public dataset",
        "Metadata-only governance record", "campaign-a", "CC-BY-4.0", (),
        "1" * 64, privacy_classification="public", consent_status="not_required",
        retention_policy="Public archive", access_scope="public",
    ))
    original = store.get_lab_dataset
    def tampered(dataset_id, version):
        record = original(dataset_id, version)
        record["license"] = "CC0-1.0"
        return record
    monkeypatch.setattr(store, "get_lab_dataset", tampered)
    result = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "tampered-data", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="public",
    )
    assert result["manifest_created"] is False
    assert result["blocking_issues"][0]["code"] == "dataset_record_integrity_failed"


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit=-1):
        return self.payload[:limit]


def test_arxiv_provider_parses_public_metadata_and_rejects_dtd():
    from ssswet_core.providers import ArxivProvider
    atom = b"""<?xml version='1.0'?>
    <feed xmlns='http://www.w3.org/2005/Atom' xmlns:arxiv='http://arxiv.org/schemas/atom'>
      <entry>
        <id>https://arxiv.org/abs/2401.01234v2</id>
        <title>  A bounded scientific result </title>
        <published>2026-01-02T00:00:00Z</published>
        <author><name>Author One</name></author>
        <arxiv:doi>10.5555/example</arxiv:doi>
      </entry>
    </feed>"""
    result = ArxivProvider(opener=lambda *args, **kwargs: _FakeResponse(atom)).investigate("wave propagation", "test")
    assert result.source_ids == ("arxiv:2401.01234",), result.summary
    assert "10.5555/example" in result.evidence[0]
    assert result.provenance[0]["provider"] == "arxiv-public-search"

    malicious = b"<!DOCTYPE feed [<!ENTITY x 'boom'>]><feed/>"
    rejected = ArxivProvider(opener=lambda *args, **kwargs: _FakeResponse(malicious)).investigate("wave propagation", "test")
    assert rejected.evidence == ()
    assert "ValueError" in rejected.summary


def test_arxiv_provider_rejects_untrusted_redirects_and_oversized_responses():
    from ssswet_core.providers import ArxivProvider

    class RedirectResponse(_FakeResponse):
        def geturl(self):
            return "http://127.0.0.1/internal"

    redirect = ArxivProvider(
        opener=lambda *args, **kwargs: RedirectResponse(b"<feed/>")
    ).investigate("wave propagation", "test")
    assert redirect.evidence == ()
    assert "ValueError" in redirect.summary

    oversized = ArxivProvider(
        opener=lambda *args, **kwargs: _FakeResponse(b"x" * 2_000_001)
    ).investigate("wave propagation", "test")
    assert oversized.evidence == ()
    assert "ValueError" in oversized.summary

    with pytest.raises(ValueError):
        ArxivProvider().investigate("x" * 1_001, "test")


def test_europe_pmc_provider_parses_public_metadata():
    from ssswet_core.providers import EuropePMCProvider
    payload = {
        "resultList": {"result": [{
            "title": "A biomedical methods paper",
            "doi": "10.5555/biomed",
            "pmid": "123456",
            "authorString": "Author A, Author B",
            "firstPublicationDate": "2025-03-01",
            "journalTitle": "Methods Journal",
        }]}
    }
    result = EuropePMCProvider(
        opener=lambda *args, **kwargs: _FakeResponse(json.dumps(payload).encode())
    ).investigate("biomedical methods", "test")
    assert result.source_ids == ("10.5555/biomed",)
    assert "PMID: 123456" in result.evidence[0]
    assert result.provenance[0]["provider"] == "europe-pmc-public-search"


def test_broad_scholarly_provider_preserves_provider_observations_and_conflicts(tmp_path):
    from ssswet_core.literature_watch import LiteratureWatchReport
    from ssswet_core.providers import BroadScholarlyLiteratureProvider, ProviderResult

    class FixtureProvider:
        def __init__(self, name, title, year):
            self.name, self.title, self.year = name, title, year
        def investigate(self, objective, strategy):
            evidence = (
                f"{self.title} | Author | {self.year} | Journal "
                "| DOI: 10.7777/shared | URL: https://example.org/shared",
            )
            return ProviderResult("Fixture metadata", evidence, 1.0, ("10.7777/shared",))

    provider = BroadScholarlyLiteratureProvider(providers=[
        FixtureProvider("index-a", "A shared paper", "2024"),
        FixtureProvider("index-b", "A differently titled record", "2025"),
    ])
    result = provider.investigate("shared paper", "test")
    assert len(result.evidence) == 1
    assert len(result.provenance[0]["provider_records"]) == 2
    report = LiteratureWatchReport.create("shared paper", provider.name, result,
                                           SQLiteResearchStore(tmp_path / "provider.sqlite3"))
    candidate = report.candidates[0]
    assert set(candidate.provider.split("+")) == {"index-a", "index-b"}
    assert set(candidate.metadata_conflicts) >= {"title", "year"}
    assert len(candidate.provider_observations) == 2
    assert report.scientific_validity_established is False



def test_broad_scholarly_provider_caps_results_and_reports_partial_provider_failure():
    from ssswet_core.providers import BroadScholarlyLiteratureProvider, ProviderResult

    class ManyProvider:
        name = "many-records"
        def investigate(self, objective, strategy):
            source_ids = tuple("10.9999/paper-" + str(index) for index in range(25))
            evidence = tuple(
                "Paper " + str(index) + " | Author | 2026 | Journal | DOI: " + source_id
                + " | URL: https://example.org/" + str(index)
                for index, source_id in enumerate(source_ids)
            )
            return ProviderResult("Fixture records", evidence, 1.0, source_ids)

    class FailingProvider:
        name = "failing-provider"
        def investigate(self, objective, strategy):
            raise TimeoutError("fixture timeout")

    provider = BroadScholarlyLiteratureProvider(providers=[ManyProvider(), FailingProvider()])
    result = provider.investigate("bounded discovery", "test")
    assert len(result.source_ids) == 20
    assert len(result.evidence) == 20
    assert "failing-provider:TimeoutError" in result.summary
    assert "failing-provider" in result.summary

def test_review_queue_discloses_bounded_source_scan_completeness(monkeypatch):
    from ssswet_core.dataset_registry import DatasetRegistry
    from ssswet_core.research_review_queue import build_review_queue
    from ssswet_core.scientific_memory import ScientificMemoryService

    class FakeStore:
        def literature_watch_history(self, limit=50):
            assert limit == 101
            return [
                {
                    "created_at": "2026-11-12T00:00:00+00:00",
                    "candidates": [
                        {
                            "candidate_id": f"{report_index}-{candidate_index}",
                            "classification": "candidate_for_review",
                        }
                        for candidate_index in range(51)
                    ],
                }
                for report_index in range(101)
            ]

    monkeypatch.setattr(
        ScientificMemoryService,
        "overview",
        lambda self, limit=500: {"versions": [{} for _ in range(500)]},
    )
    monkeypatch.setattr(
        ScientificMemoryService,
        "evolution_alerts",
        lambda self, limit=500: {"alerts": []},
    )
    monkeypatch.setattr(
        DatasetRegistry,
        "overview",
        lambda self, limit=500: {"governance": {"versions": [{} for _ in range(500)]}},
    )

    result = build_review_queue(FakeStore(), limit=10)
    scan = result["source_scan"]
    assert scan["scientific_memory_versions"]["may_be_truncated"] is True
    assert scan["dataset_versions"]["may_be_truncated"] is True
    assert scan["literature_watch_reports"]["may_be_truncated"] is True
    assert scan["literature_candidates"]["omitted_from_scanned_reports"] == 100
    assert result["scan_may_be_incomplete"] is True
    assert result["total_matching_items_scope"] == "scanned_records_only"


def _start_server(tmp_path):
    store = _memory_fixture(tmp_path)
    _campaign(store)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
        __import__("ssswet_core.engine", fromlist=["SSSWETEngine"]).SSSWETEngine(store=store),
        store,
    ))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return store, server, thread, f"http://127.0.0.1:{server.server_port}"


def test_new_research_read_endpoints_are_bounded_and_read_only(tmp_path):
    store, server, thread, base = _start_server(tmp_path)
    try:
        with urlopen(base + "/api/research-context?q=wave%20propagation&limit=5&max_chars=8000") as response:
            context = json.loads(response.read())
        assert context["memories"][0]["version_id"] == "memory-v1"

        with urlopen(base + "/api/research-review-queue?limit=10") as response:
            queue = json.loads(response.read())
        assert queue["automatic_task_creation"] is False

        with urlopen(base + "/api/knowledge-graph/neighborhood?node_ids=claim-a&depth=1") as response:
            neighborhood = json.loads(response.read())
        assert neighborhood["contradiction_edge_count"] == 1

        with urlopen(base + "/api/scientific-memory/lineage-page?version_id=memory-v1&limit=10") as response:
            lineage = json.loads(response.read())
        assert lineage["items"][0]["version_id"] == "memory-v1"

        with urlopen(base + "/api/dataset-governance-gate?dataset_id=missing&version=1&scope=public") as response:
            gate = json.loads(response.read())
        assert gate["manifest_created"] is False
        assert "dataset_version_not_registered" in {
            item["code"] for item in gate["blocking_issues"]
        }

        for path in (
            "/api/research-context",
            "/api/knowledge-graph/neighborhood",
            "/api/scientific-memory/lineage-page",
        ):
            try:
                urlopen(base + path)
            except HTTPError as error:
                assert error.code == 400
            else:
                raise AssertionError(f"{path} must reject missing required parameters")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_literature_watch_diff_endpoint_returns_saved_report_comparison(tmp_path):
    store, server, thread, base = _start_server(tmp_path)
    older = LiteratureWatchReport(
        "watch-old", "wave", "2026-11-10T00:00:00+00:00", "fixture",
        "old metadata",
        (WatchCandidate("candidate-old", "fixture", "10.1234/old", "Old paper", doi="10.1234/old"),),
    )
    newer = LiteratureWatchReport(
        "watch-new", "wave", "2026-11-11T00:00:00+00:00", "fixture",
        "new metadata",
        (WatchCandidate("candidate-new", "fixture", "10.1234/new", "New paper", doi="10.1234/new"),),
    )
    store.save_literature_watch(older)
    store.save_literature_watch(newer)
    try:
        with urlopen(base + "/api/literature-watch/diff?older_watch_id=watch-old&newer_watch_id=watch-new") as response:
            result = json.loads(response.read())
        assert result["counts"]["added"] == 1
        assert result["counts"]["absent_from_newer"] == 1
        assert result["absence_is_not_retraction"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_public_provider_redirect_handler_refuses_redirect_targets():
    from urllib.request import Request
    from ssswet_core.providers import _RejectRedirectHandler

    handler = _RejectRedirectHandler()
    request = Request("https://export.arxiv.org/api/query")
    assert handler.redirect_request(
        request, None, 302, "Found", {}, "https://127.0.0.1/internal"
    ) is None
    assert handler.redirect_request(
        request, None, 302, "Found", {}, "https://export.arxiv.org/other"
    ) is None


def test_literature_watch_diff_normalizes_arxiv_version_suffixes():
    older = {"watch_id": "older", "candidates": [{
        "source_id": "arxiv:2401.01234v1", "title": "A preprint",
    }]}
    newer = {"watch_id": "newer", "candidates": [{
        "source_id": "arxiv:2401.01234v3", "title": "A revised preprint",
    }]}
    result = compare_watch_reports(older, newer)
    assert result["counts"]["added"] == 0
    assert result["counts"]["absent_from_newer"] == 0
    assert result["counts"]["metadata_changed"] == 1


def test_governed_manifest_rejects_malformed_dataset_digest(tmp_path):
    store = SQLiteResearchStore(tmp_path / "malformed-digest.sqlite3")
    _campaign(store)
    DatasetRegistry(store).register_version(DatasetVersion(
        "malformed-digest", 1, "Public dataset with malformed digest",
        "Metadata-only governance record", "campaign-a", "CC-BY-4.0", (),
        "not-a-sha256", privacy_classification="public",
        consent_status="not_required", retention_policy="Public archive",
        access_scope="public",
    ))
    result = build_governed_manifest(
        store, protocol_id="p", protocol_version=1,
        dataset_refs=[{"dataset_id": "malformed-digest", "version": 1}],
        software_version="test", parameters={}, source_ids=[],
        publication_scope="public",
    )
    assert result["manifest_created"] is False
    assert "content_digest_invalid" in {
        item["code"] for item in result["blocking_issues"]
    }
