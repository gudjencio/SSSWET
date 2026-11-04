import math
import pytest
from ssswet_core.agent_handoff import build_handoff_packet
from ssswet_core.bounded_retention import RetentionPolicy, compact_records_with_audit
from ssswet_core.collective_memory import search_collective_memory
from ssswet_core.context_aware_claim_comparison import ClaimContext, ContextAwareClaimComparator
from ssswet_core.contradiction import ResearchClaim
from ssswet_core.evidence_packet_validator import validate_packet
from ssswet_core.provenance import ProvenanceRecord, content_digest, provenance_digest, verify_chain
from ssswet_core.research_checkpoint import CheckpointLedger
from ssswet_core.rescue_resource_planner import plan_fair_resources
from ssswet_core.retrieval_evaluation import compare_retrieval_evaluations, evaluate_retrieval
from ssswet_core.virtual_time_mapping import TemporalObservation, VirtualTimeMap

def test_provenance_verification_rejects_non_genesis_parent_and_duplicate_source():
    first = ProvenanceRecord("source-1", "paper", "doi:example/1", content_digest("first"),
                             parent_digest=content_digest("orphan"))
    second = ProvenanceRecord("source-1", "dataset", "dataset:1", content_digest("second"),
                              parent_digest=provenance_digest(first))
    result = verify_chain([first, second])
    assert result["valid"] is False
    assert result["break_indices"] == [0, 1]
    assert result["duplicate_source_ids"] == ["source-1"]
    assert {item["code"] for item in result["issues"]} == {"genesis_parent_must_be_null", "duplicate_source_id"}

def test_provenance_verification_accepts_a_well_formed_chain():
    first = ProvenanceRecord("s1", "paper", "doi:example/1", content_digest("a"))
    second = ProvenanceRecord("s2", "dataset", "dataset:2", content_digest("b"), provenance_digest(first))
    assert verify_chain([first, second])["valid"] is True

def _legacy_memory_search(records, query):
    import re
    query_tokens = {token.casefold() for token in re.findall(r"[\w'-]{2,}", query, flags=re.UNICODE)}
    ranked = []
    for record in records:
        searchable = " ".join((str(record.get("topic", "")), str(record.get("statement", "")),
                               str(record.get("campaign_id", "")), " ".join(record.get("source_ids", []))))
        record_tokens = {token.casefold() for token in re.findall(r"[\w'-]{2,}", searchable, flags=re.UNICODE)}
        overlap = query_tokens & record_tokens
        if overlap:
            score = 0.7 * len(overlap) / len(query_tokens) + 0.3 * len(overlap) / len(record_tokens)
            ranked.append((score, record["memory_id"]))
    ranked.sort(reverse=True)
    return [memory_id for _, memory_id in ranked]

def test_memory_retrieval_uses_research_text_and_exact_metadata_filters():
    records = [
        {"memory_id": "relevant", "topic": "Thermal fatigue",
         "statement": "Protective coating adhesion changes under repeated thermal cycling and fatigue testing.",
         "campaign_id": "materials", "source_ids": ["source-relevant"], "status": "reviewed"},
        {"memory_id": "noise", "topic": "Weekly note", "statement": "Unrelated equipment maintenance log.",
         "campaign_id": "operations", "source_ids": ["thermal-fatigue-coating-reference"], "status": "reviewed"},
    ]
    before_ids = _legacy_memory_search(records, "thermal fatigue coating")
    after = search_collective_memory(records, "thermal fatigue coating")
    assert before_ids[0] == "noise"
    assert after[0]["memory_id"] == "relevant"
    assert after[0]["retrieval_method"] == "field_weighted_bm25"
    assert after[0]["retrieval_version"] == "bm25-field-weighted-v2"
    assert search_collective_memory(records, "maintenance", source_id="thermal-fatigue-coating-reference")[0]["memory_id"] == "noise"
    assert search_collective_memory(records, "thermal fatigue", campaign_id="materials")[0]["memory_id"] == "relevant"

def test_retrieval_metrics_quantify_before_and_after_ranking():
    records = [
        {"memory_id": "relevant", "topic": "Thermal fatigue",
         "statement": "Protective coating adhesion changes under repeated thermal cycling and fatigue testing.",
         "campaign_id": "materials", "source_ids": ["source-relevant"]},
        {"memory_id": "noise", "topic": "Weekly note", "statement": "Unrelated equipment maintenance log.",
         "campaign_id": "operations", "source_ids": ["thermal-fatigue-coating-reference"]},
    ]
    before = evaluate_retrieval({"thermal": _legacy_memory_search(records, "thermal fatigue coating")},
                               {"thermal": {"relevant"}}, k=1)
    after = evaluate_retrieval({"thermal": [item["memory_id"] for item in search_collective_memory(records, "thermal fatigue coating")]},
                              {"thermal": {"relevant"}}, k=1)
    comparison = compare_retrieval_evaluations(before, after)
    assert before["mrr_at_k"] == 0.0
    assert after["mrr_at_k"] == 1.0
    assert comparison["deltas"]["mrr_at_k"] == 1.0
    assert comparison["non_regression_on_recall"] is True

def test_evidence_packet_validator_checks_types_and_resolves_source_ids():
    packet = {"title": "Coating durability", "summary": "A bounded materials observation.",
              "source_ids": ["paper-1"], "method": "Repeated-cycle laboratory test.",
              "limitations": "One sample family; no field validation."}
    result = validate_packet(packet, known_source_ids={"paper-1", "dataset-1"})
    assert result["valid_for_review"] is True
    assert result["source_link_status"] == "resolved"
    assert result["warnings"]
    unresolved = validate_packet(packet, known_source_ids={"dataset-1"})
    assert unresolved["valid_for_review"] is False
    assert unresolved["unresolved_source_ids"] == ["paper-1"]

def test_context_audit_separates_units_and_reports_same_context_conflicts():
    claims = [
        ClaimContext(ResearchClaim("coating", "thickness", "120", "s1"), scope="sample", unit="um"),
        ClaimContext(ResearchClaim("coating", "thickness", "0.12", "s2"), scope="sample", unit="mm"),
        ClaimContext(ResearchClaim("coating", "thickness", "105", "s3"), scope="sample", unit="um"),
    ]
    audit = ContextAwareClaimComparator().audit_contexts(claims)
    assert len(audit["context_mismatches"]) == 1
    assert audit["context_mismatches"][0]["classification"] == "context_mismatch_not_compared"
    assert len(audit["conflicts"]) == 1
    assert audit["conflicts"][0]["classification"] == "potential_conflict"
    assert audit["scientific_validity_established"] is False

def test_agent_handoff_preserves_status_provenance_and_stays_bounded():
    memories = [
        {"memory_id": "m1", "topic": "Thermal fatigue",
         "statement": "Protective coating fatigue requires repeated thermal-cycle testing.",
         "status": "contested", "source_ids": ["paper-1", "dataset-1"],
         "provenance_group": "lab-a", "review_note": "Independent review requested."},
        {"memory_id": "m2", "topic": "Agriculture", "statement": "Soil moisture affects crop yield.",
         "status": "reviewed", "source_ids": ["paper-2"]},
    ]
    packet = build_handoff_packet("task-1", "Review thermal fatigue in protective coatings", memories,
        required_capabilities=["materials science", "independent verification"],
        open_questions=["Does the effect persist after ageing?"],
        constraints=["No human testing without ethics approval."], max_chars=5000)
    assert packet["memories"][0]["memory_id"] == "m1"
    assert packet["memories"][0]["status"] == "contested"
    assert packet["source_refs"] == ["dataset-1", "paper-1"]
    assert packet["provenance_groups"] == ["lab-a"]
    assert packet["autonomous_execution_authorized"] is False
    assert packet["scientific_validity_established"] is False
    assert packet["context_characters"] <= 5000

def test_checkpoint_hash_chain_and_version_diff_are_auditable():
    ledger = CheckpointLedger()
    ledger.save("task-1", "hypothesis", source_refs=["s1"], unresolved_questions=["q1"])
    ledger.save("task-1", "review", source_refs=["s1", "s2"], unresolved_questions=["q2"])
    assert ledger.verify("task-1")["valid"] is True
    difference = ledger.diff("task-1", 1, 2)
    assert difference["state_changed"] is True
    assert difference["source_refs_added"] == ["s2"]
    assert difference["questions_opened"] == ["q2"]
    assert difference["questions_resolved_or_removed"] == ["q1"]
    assert ledger.history("task-1")[1]["digest"]

def test_temporal_mapping_queries_uncertainty_intervals_and_prevents_overwrite():
    mapping = VirtualTimeMap()
    mapping.add(TemporalObservation("2026-01-01T12:00:00Z", "Sensor observation", "sensor-1", 3600))
    mapping.add(TemporalObservation("2026-01-01T18:00:00Z", "Later event", "sensor-2", 0))
    assert [item.source_id for item in mapping.window_between("2026-01-01T12:30:00Z", "2026-01-01T13:00:00Z")] == ["sensor-1"]
    assert mapping.window_between("2026-01-01T12:30:00Z", "2026-01-01T13:00:00Z", include_uncertainty=False) == []
    with pytest.raises(ValueError, match="already exists"):
        mapping.add(TemporalObservation("2026-01-02T12:00:00Z", "Replacement", "sensor-1", 0))
    with pytest.raises(ValueError, match="finite"):
        mapping.add(TemporalObservation("2026-01-01", "Invalid", "sensor-3", math.nan))

def test_rescue_resource_planning_prioritizes_then_fairly_splits_ties():
    result = plan_fair_resources([
        {"request_id": "urgent", "priority": 5, "needs": {"water": 4}},
        {"request_id": "shelter-a", "priority": 3, "needs": {"water": 4}},
        {"request_id": "shelter-b", "priority": 3, "needs": {"water": 4}},
    ], {"water": 6})
    assert result["allocations_by_request"]["urgent"]["water"] == 4
    assert result["allocations_by_request"]["shelter-a"]["water"] == 1
    assert result["allocations_by_request"]["shelter-b"]["water"] == 1
    assert result["automated_dispatch"] is False
    assert result["requires_human_review"] is True

def test_retention_preview_preserves_lineage_and_protects_contested_records():
    records = [
        {"record_id": "a1", "key": "a", "status": "archived", "source_ids": ["s1"]},
        {"record_id": "a2", "key": "a", "status": "reviewed", "source_ids": ["s2"]},
        {"record_id": "b1", "key": "b", "status": "contested", "source_ids": ["s3"]},
        {"record_id": "c1", "key": "c", "status": "reviewed", "source_ids": ["s4"]},
    ]
    snapshot = [dict(item) for item in records]
    result = compact_records_with_audit(records, key_field="key", policy=RetentionPolicy(max_items=2))
    by_key = {item["key"]: item for item in result["records"]}
    assert set(by_key) == {"a", "b"}
    assert by_key["a"]["record_id"] == "a2"
    assert by_key["a"]["retention_source_ids"] == ["s1", "s2"]
    assert by_key["b"]["retention_protected"] is True
    assert result["provenance_retention_ratio"] == 0.75
    assert result["source_records_deleted"] is False
    assert records == snapshot

def test_retention_protected_overflow_is_reported_not_silently_dropped():
    records = [{"record_id": "a", "key": "a", "status": "contested"},
               {"record_id": "b", "key": "b", "status": "candidate"}]
    result = compact_records_with_audit(records, policy=RetentionPolicy(max_items=1))
    assert result["retained_group_count"] == 2
    assert result["capacity_exceeded"] is True
    assert result["omitted_group_count"] == 0


def test_engine_exposes_agent_handoff_packet_facade():
    from ssswet_core.engine import SSSWETEngine
    packet = SSSWETEngine().build_agent_handoff_packet(
        "engine-task", "Review thermal coating fatigue",
        [{"memory_id": "m", "topic": "Thermal fatigue",
          "statement": "Protective coating fatigue under repeated thermal cycling.",
          "source_ids": ["source-1"], "status": "candidate"}],
    )
    assert packet["task_id"] == "engine-task"
    assert packet["source_refs"] == ["source-1"]
    assert packet["autonomous_execution_authorized"] is False
