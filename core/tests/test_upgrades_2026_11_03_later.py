from ssswet_core.uncertainty_propagation import combine_independent_additive, combine_worst_case
from ssswet_core.reproducibility_manifest import build_manifest, compare_manifests
from ssswet_core.benchmark_registry import BenchmarkRegistry, BenchmarkResult
from ssswet_core.accessibility_audit import audit_html
from ssswet_core.temporal_snapshot_diff import diff_snapshots
from ssswet_core.research_queue import prioritize
from ssswet_core.agent_capability_registry import AgentCapabilityRegistry
from ssswet_core.rescue_resource_planner import plan_resources
from ssswet_core.memory_compaction import compact
from ssswet_core.evidence_packet_validator import validate_packet


def test_uncertainty_methods_are_distinct_and_bounded():
    assert combine_independent_additive([(10, 3), (4, 4)])["uncertainty"] == 5.0
    assert combine_worst_case([(10, 3), (4, 4)])["uncertainty"] == 7


def test_manifest_is_deterministic():
    a = build_manifest(protocol_id="p", protocol_version=1, dataset_refs=[], software_version="x", parameters={"a": 1}, source_ids=["s"])
    b = build_manifest(protocol_id="p", protocol_version=1, dataset_refs=[], software_version="x", parameters={"a": 1}, source_ids=["s"])
    assert a["canonical_sha256"] == b["canonical_sha256"]
    assert compare_manifests(a, b)["identical"]


def test_benchmark_requires_repeatable_measurement():
    registry = BenchmarkRegistry()
    registry.record(BenchmarkResult("latency", 12.0, "ms", 10))
    assert registry.compare("latency", 15.0)["relative_change"] < 0


def test_accessibility_audit_detects_missing_alt():
    report = audit_html('<main><img src="x"></main>')
    assert report["issue_count"] == 1


def test_temporal_diff_is_observation_only():
    report = diff_snapshots([{"source_id": "s", "timestamp": "1"}], [{"source_id": "s", "timestamp": "1"}, {"source_id": "t", "timestamp": "2"}])
    assert len(report["added"]) == 1
    assert not report["unrecorded_history_recovered"]


def test_queue_prioritizes_safety_and_evidence_gaps():
    result = prioritize([{"id": "a", "missing_evidence": 1}, {"id": "b", "safety_gate": True, "contradictions": 2}])
    assert result[0]["id"] == "b"


def test_capability_registry_reports_missing_roles():
    registry = AgentCapabilityRegistry()
    registry.register("a", ["statistics"])
    assert registry.coverage(["statistics", "materials"])["missing"] == ["materials"]


def test_rescue_planner_never_allocates_more_than_stock():
    result = plan_resources({"water": 10}, {"water": 4})
    assert result["allocations"]["water"] == 4
    assert result["shortages"]["water"] == 6


def test_memory_compaction_is_bounded_and_prefers_validated():
    records = [{"memory_id": "a", "statement": "Same claim", "validated": False, "updated_at": "2"}, {"memory_id": "b", "statement": "same claim", "validated": True, "updated_at": "1"}]
    result = compact(records, max_records=1)
    assert result["retained_count"] == 1
    assert result["records"][0]["memory_id"] == "b"


def test_evidence_packet_validator_rejects_duplicates():
    result = validate_packet({"title": "x", "summary": "y", "source_ids": ["s", "s"], "method": "m", "limitations": "l"})
    assert not result["valid_for_review"]
