from __future__ import annotations

import copy
import pytest

from ssswet_core.agent_handoff_contract import build_handoff, validate_handoff
from ssswet_core.research_memory_snapshot import build_memory_snapshot, compare_memory_snapshots, retrieve_memory, verify_memory_snapshot
from ssswet_core.media_source_lineage import analyze_source_lineage
from ssswet_core.claim_context_audit import compare_claim_contexts
from ssswet_core.translation_integrity import audit_translation_integrity
from ssswet_core.reviewer_concordance import measure_reviewer_concordance
from ssswet_core.temporal_evidence_window import audit_temporal_window
from ssswet_core.vtt_spatial_uncertainty import transform_point_with_covariance
from ssswet_core.rescue_route_redundancy import analyze_route_redundancy

D = "a" * 64


def test_agent_handoff_contract_is_versioned_bounded_and_never_authorizes_execution():
    raw = {
        "handoff_id": "handoff-1", "created_at": "2026-11-14T08:00:00Z", "expires_at": "2026-11-14T09:00:00Z",
        "from_agent": "literature-agent", "to_agent": "materials-agent", "objective": "Compare reported fatigue measurements",
        "constraints": ["Use public sources only", "Preserve contradictory results"],
        "source_refs": [{"source_id": "paper-1", "sha256": D, "source_type": "publication"}],
        "requested_outputs": ["context comparison"], "requires_human_review": True,
        "safety_state": "review_required", "budget": {"max_steps": 20, "max_runtime_seconds": 120, "max_output_chars": 10000},
    }
    built = build_handoff(raw)
    assert built["schema_version"] == 1
    with pytest.raises(ValueError, match="object"):
        validate_handoff(None)
    assert len(built["handoff_sha256"]) == 64
    assert validate_handoff(built, now="2026-11-14T08:30:00Z")["ready_for_human_review"] is True
    assert validate_handoff(built, now="2026-11-14T10:00:00Z")["expired"] is True
    assert validate_handoff(built)["execution_authorized"] is False
    changed = copy.deepcopy(built)
    changed["objective"] = "Different objective"
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_handoff(changed)
    for invalid in [dict(raw, safety_state="authorized"), dict(raw, expires_at="2026-11-14T07:00:00Z"), dict(raw, budget={"max_steps": 0, "max_runtime_seconds": 2, "max_output_chars": 2})]:
        with pytest.raises(ValueError):
            build_handoff(invalid)
    with pytest.raises(ValueError, match="unique"):
        build_handoff(dict(raw, source_refs=raw["source_refs"] * 2))
    with pytest.raises(ValueError, match="at most"):
        build_handoff(dict(raw, constraints=["x"] * 51))


def memory(memory_id, body, stance="unspecified", state="unreviewed"):
    return {"memory_id": memory_id, "text": body, "created_at": "2026-11-13T10:00:00Z", "stance": stance, "review_state": state, "source_refs": [{"source_id": "src-" + memory_id, "sha256": D}], "tags": ["materials"]}


def test_memory_snapshot_preserves_conflicts_provenance_and_deterministic_bounded_retrieval():
    rows = [memory("m1", "Alloy fatigue under thermal cycling", "supports"), memory("m2", "Alloy fatigue under thermal cycling", "contradicts"), memory("m3", "Ocean salinity observation", "neutral")]
    snapshot = build_memory_snapshot(rows)
    assert verify_memory_snapshot(snapshot)["valid"]
    assert snapshot["schema_version"] == 1
    assert snapshot["memory_count"] == 3
    assert snapshot["source_reference_count"] == 3
    assert snapshot["memories_deleted_or_merged"] is False
    assert len(snapshot["exact_text_match_groups"]) == 1
    result = retrieve_memory(snapshot, "alloy fatigue", limit=2)
    assert [row["memory"]["memory_id"] for row in result["results"]] == ["m1", "m2"]
    assert {row["memory"]["stance"] for row in result["results"]} == {"supports", "contradicts"}
    assert len(retrieve_memory(snapshot, "alloy", limit=1)["results"]) == 1
    assert build_memory_snapshot(list(reversed(rows)))["manifest_sha256"] == snapshot["manifest_sha256"]
    corrupt = copy.deepcopy(snapshot)
    corrupt["memories"][0]["text"] = "tampered"
    with pytest.raises(ValueError, match="digest"):
        verify_memory_snapshot(corrupt)
    newer = build_memory_snapshot([rows[0], memory("m4", "New observation")])
    diff = compare_memory_snapshots(snapshot, newer)
    assert diff["added_memory_ids"] == ["m4"]
    assert diff["absent_from_current_snapshot_ids"] == ["m2", "m3"]
    assert diff["absence_is_not_retraction"] is True
    with pytest.raises(ValueError, match="unique"):
        build_memory_snapshot([rows[0], rows[0]])
    with pytest.raises(ValueError, match="between"):
        retrieve_memory(snapshot, "alloy", limit=51)
    with pytest.raises(ValueError, match="at most"):
        build_memory_snapshot([memory(str(i), "x") for i in range(1001)])


def test_source_lineage_uses_declared_edges_and_never_equates_duplicate_text_with_origin():
    rows = [
        {"source_id": "a", "platform": "youtube", "content_sha256": D},
        {"source_id": "b", "platform": "x", "content_sha256": D, "parent_source_id": "a", "relation_type": "repost"},
        {"source_id": "c", "platform": "reddit", "content_sha256": "b" * 64, "parent_source_id": "missing", "relation_type": "quotation"},
    ]
    result = analyze_source_lineage(rows)
    assert result["schema_version"] == 1
    assert result["source_count"] == 3
    assert result["root_by_source_id"]["b"] == "a"
    assert result["missing_parent_source_ids"] == ["missing"]
    assert len(result["exact_text_match_groups"]) == 1
    assert result["exact_text_match_groups"][0]["origin_equivalence_inferred"] is False
    assert result["scientific_independence_established"] is False
    cycle = analyze_source_lineage([
        {"source_id": "a", "platform": "x", "parent_source_id": "b", "relation_type": "repost"},
        {"source_id": "b", "platform": "x", "parent_source_id": "a", "relation_type": "repost"},
    ])
    assert cycle["cycles"] == [["a", "b"]]
    assert cycle["root_by_source_id"]["a"] is None
    with pytest.raises(ValueError, match="supported"):
        analyze_source_lineage([{"source_id": "x", "platform": "x", "parent_source_id": "y", "relation_type": "copy"}])
    with pytest.raises(ValueError, match="unique"):
        analyze_source_lineage([{"source_id": "x", "platform": "x"}, {"source_id": "x", "platform": "y"}])
    with pytest.raises(ValueError, match="at most"):
        analyze_source_lineage([{"source_id": str(i), "platform": "x"} for i in range(501)])


def claim(cid, value, **changes):
    row = {"claim_id": cid, "metric": "fatigue life", "value": value, "unit": "cycles", "population": "alloy A batch 4", "condition": "20 C dry air", "method": "three point bend", "observation_window": "2025-Q1", "source_ids": ["paper-" + cid]}
    row.update(changes)
    return row


def test_claim_context_comparison_blocks_incompatible_contexts_without_calling_contradictions():
    result = compare_claim_contexts([claim("a", 100), claim("b", 120), claim("c", 120, condition="80 C humid air"), claim("d", 150, unit="hours")])
    assert result["schema_version"] == 1
    by_pair = {(row["left_claim_id"], row["right_claim_id"]): row for row in result["comparisons"]}
    assert by_pair[("a", "b")]["status"] == "comparable_for_human_review"
    assert by_pair[("a", "b")]["value_disagreement_for_review"] is True
    assert by_pair[("a", "c")]["status"] == "incomparable_context"
    assert by_pair[("a", "d")]["status"] == "incomparable_context"
    assert all(row["contradiction_inferred"] is False for row in result["comparisons"])
    incomplete = claim("e", 80, method=None)
    assert compare_claim_contexts([incomplete, claim("f", 80)])["comparisons"][0]["status"] == "insufficient_context"
    with pytest.raises(ValueError, match="unique"):
        compare_claim_contexts([claim("x", 1), claim("x", 2)])
    with pytest.raises(ValueError, match="finite"):
        compare_claim_contexts([claim("x", float("nan"))])
    with pytest.raises(ValueError, match="at most"):
        compare_claim_contexts([claim(str(i), i) for i in range(201)])


def test_translation_integrity_flags_numbers_units_negation_and_protected_terms():
    good = audit_translation_integrity("The sample did not exceed 12.5 mm.", "L'échantillon n'a pas dépassé 12,5 mm.", source_language="en", target_language="fr", protected_terms=["mm"])
    assert good["schema_version"] == 1
    assert "numeric_tokens_differ" not in good["flags"]
    assert "unit_tokens_differ" not in good["flags"]
    assert "possible_negation_omission" not in good["flags"]
    assert good["translation_accuracy_established"] is False
    bad = audit_translation_integrity("The sample did not exceed 12.5 mm.", "L'échantillon a dépassé 13 cm.", source_language="en", target_language="fr", protected_terms=["mm"])
    assert {"numeric_tokens_differ", "unit_tokens_differ", "possible_negation_omission", "protected_terms_missing"}.issubset(set(bad["flags"]))
    with pytest.raises(ValueError, match="differ"):
        audit_translation_integrity("a", "b", source_language="en", target_language="en")
    with pytest.raises(ValueError, match="supported"):
        audit_translation_integrity("a", "b", source_language="xx", target_language="fr")
    with pytest.raises(ValueError, match="at most"):
        audit_translation_integrity("a", "b", source_language="en", target_language="fr", protected_terms=["x"] * 101)


def test_reviewer_concordance_reports_pairwise_kappa_and_prevalence_caveat():
    ratings = []
    for i in range(10):
        label = "accept" if i < 8 else "needs_revision"
        ratings.extend([{"item_id": f"i{i}", "reviewer_id": "r1", "decision": label}, {"item_id": f"i{i}", "reviewer_id": "r2", "decision": label}])
    result = measure_reviewer_concordance(ratings)
    assert result["schema_version"] == 1
    pair = result["pairwise_results"][0]
    assert pair["matched_item_count"] == 10
    assert pair["raw_agreement"] == 1.0
    assert pair["cohen_kappa"] == 1.0
    assert "prevalence" in pair["prevalence_caveat"]
    assert result["agreement_is_correctness"] is False
    small = measure_reviewer_concordance(ratings[:8])
    assert small["pairwise_results"][0]["cohen_kappa"] is None
    assert small["pairwise_results"][0]["minimum_sample_met"] is False
    with pytest.raises(ValueError, match="only once"):
        measure_reviewer_concordance([{"item_id": "i", "reviewer_id": "r", "decision": "accept"}] * 2)
    with pytest.raises(ValueError, match="unsupported"):
        measure_reviewer_concordance([{"item_id": "i", "reviewer_id": "r", "decision": "true"}])


def test_temporal_window_retains_stale_future_and_missing_timestamps():
    rows = [
        {"source_id": "fresh", "published_at": "2026-11-13T00:00:00Z", "captured_at": "2026-11-13T01:00:00Z"},
        {"source_id": "old", "published_at": "2020-01-01T00:00:00Z", "captured_at": "2020-01-02T00:00:00Z"},
        {"source_id": "future", "published_at": "2026-11-16T00:00:00Z"},
        {"source_id": "unknown"},
        {"source_id": "bad-order", "published_at": "2026-11-13T00:00:00Z", "captured_at": "2026-11-12T00:00:00Z"},
    ]
    result = audit_temporal_window(rows, now="2026-11-14T00:00:00Z", maximum_age_days=30)
    assert result["schema_version"] == 1
    by_id = {row["source_id"]: row for row in result["records"]}
    assert by_id["fresh"]["status"] == "within_window"
    assert by_id["old"]["status"] == "older_than_window"
    assert by_id["future"]["status"] == "future_dated"
    tolerated = audit_temporal_window([{"source_id": "slight", "published_at": "2026-11-14T00:02:00Z"}], now="2026-11-14T00:00:00Z", maximum_age_days=1)
    assert "publication_timestamp_slightly_future_within_tolerance" in tolerated["records"][0]["flags"]
    assert by_id["unknown"]["status"] == "unknown_publication_time"
    assert "capture_precedes_publication" in by_id["bad-order"]["flags"]
    assert result["records_discarded"] == 0
    assert result["recency_is_reliability"] is False
    with pytest.raises(ValueError, match="timezone-aware"):
        audit_temporal_window([{"source_id": "x", "published_at": "2026-11-14T10:00:00"}], now="2026-11-14T00:00:00Z", maximum_age_days=1)
    with pytest.raises(ValueError, match="unique"):
        audit_temporal_window([{"source_id": "x"}, {"source_id": "x"}], now="2026-11-14T00:00:00Z", maximum_age_days=1)


def test_vtt_spatial_uncertainty_propagates_covariance_and_rejects_invalid_rotations():
    result = transform_point_with_covariance([1, 0], [[0, -1], [1, 0]], [10, 20], [[4, 0], [0, 1]], [[1, 0], [0, 1]], coordinate_unit="m")
    assert result["schema_version"] == 1
    assert result["transformed_point"] == [10.0, 21.0]
    assert result["covariance"] == [[2.0, 0.0], [0.0, 5.0]]
    assert result["major_95_ellipse_axis"] > result["minor_95_ellipse_axis"]
    assert result["geographic_conversion_performed"] is False
    with pytest.raises(ValueError, match="proper orthonormal"):
        transform_point_with_covariance([0, 0], [[2, 0], [0, 1]], [0, 0], [[1, 0], [0, 1]], [[0, 0], [0, 0]], coordinate_unit="m")
    with pytest.raises(ValueError, match="positive semidefinite"):
        transform_point_with_covariance([0, 0], [[1, 0], [0, 1]], [0, 0], [[1, 2], [2, 1]], [[0, 0], [0, 0]], coordinate_unit="m")
    with pytest.raises(ValueError, match="symmetric"):
        transform_point_with_covariance([0, 0], [[1, 0], [0, 1]], [0, 0], [[1, 0], [1, 1]], [[0, 0], [0, 0]], coordinate_unit="m")


def test_rescue_route_redundancy_finds_edge_disjoint_paths_and_unknown_cut_edges():
    segments = [
        {"segment_id": "a", "from_node": "S", "to_node": "A", "status": "open"},
        {"segment_id": "b", "from_node": "A", "to_node": "T", "status": "open"},
        {"segment_id": "c", "from_node": "S", "to_node": "B", "status": "open"},
        {"segment_id": "d", "from_node": "B", "to_node": "T", "status": "open"},
        {"segment_id": "e", "from_node": "S", "to_node": "T", "status": "unknown"},
        {"segment_id": "f", "from_node": "S", "to_node": "C", "status": "blocked"},
    ]
    result = analyze_route_redundancy(segments, start_node="S", destination_node="T")
    assert result["schema_version"] == 1
    assert result["maximum_edge_disjoint_path_count"] == 2
    assert result["status"] == "multiple_edge_disjoint_paths"
    assert result["unknown_segment_ids"] == ["e"]
    assert result["blocked_segment_ids"] == ["f"]
    assert result["unknown_segments_treated_as_open"] is False
    assert result["route_generated"] is False
    bottleneck = analyze_route_redundancy([
        {"segment_id": "a", "from_node": "S", "to_node": "A", "status": "open"},
        {"segment_id": "b", "from_node": "A", "to_node": "T", "status": "open"},
        {"segment_id": "c", "from_node": "S", "to_node": "B", "status": "open"},
        {"segment_id": "d", "from_node": "B", "to_node": "A", "status": "open"},
    ], start_node="S", destination_node="T")
    assert bottleneck["maximum_edge_disjoint_path_count"] == 1
    assert "b" in bottleneck["minimum_cut_segment_ids"]
    no_path = analyze_route_redundancy([{"segment_id": "x", "from_node": "S", "to_node": "T", "status": "unknown"}], start_node="S", destination_node="T")
    assert no_path["status"] == "no_verified_path"
    with pytest.raises(ValueError, match="unique"):
        analyze_route_redundancy([{"segment_id": "x", "from_node": "S", "to_node": "T", "status": "open"}] * 2, start_node="S", destination_node="T")
    with pytest.raises(ValueError, match="differ"):
        analyze_route_redundancy([], start_node="S", destination_node="S")
    with pytest.raises(ValueError, match="at most"):
        analyze_route_redundancy([{"segment_id": str(i), "from_node": "a", "to_node": "b", "status": "open"} for i in range(1001)], start_node="a", destination_node="b")

def test_source_coverage_audit_reports_concentration_and_caller_defined_sampling_gaps():
    from ssswet_core.source_coverage_audit import audit_source_coverage
    rows = [
        {"source_id": "1", "platform": "YouTube", "language": "en-US", "domain": "https://www.example.org/a", "region": "EU", "topic": "materials"},
        {"source_id": "2", "platform": "youtube", "language": "en", "domain": "example.org", "region": "EU", "topic": "materials"},
        {"source_id": "3", "platform": "youtube", "language": "en-GB", "domain": "example.org", "region": "EU", "topic": "materials"},
        {"source_id": "4", "platform": "x", "language": "fr-FR", "domain": "other.net", "region": "NA", "topic": "rescue"},
    ]
    quotas = [
        {"dimension": "platform", "value": "x", "minimum_count": 2},
        {"dimension": "language", "value": "fr", "minimum_count": 2},
        {"dimension": "domain", "value": "other.net", "minimum_count": 2},
    ]
    result = audit_source_coverage(rows, target_quotas=quotas)
    assert result["schema_version"] == 1
    assert result["source_count"] == 4
    assert result["dimension_summaries"]["platform"]["group_count"] == 2
    assert result["dimension_summaries"]["platform"]["hhi_concentration"] == 0.625
    assert result["dimension_summaries"]["language"]["distribution"][0]["value"] == "en"
    assert result["dimension_summaries"]["domain"]["distribution"][0]["value"] == "example.org"
    assert len(result["target_gaps"]) == 3
    assert all(row["deficit"] == 1 for row in result["target_gaps"])
    assert result["sampling_recommendations"] == result["target_gaps"]
    assert result["source_quality_inferred"] is False
    assert result["scientific_independence_established"] is False
    assert result["crawler_or_collection_authorized"] is False
    assert audit_source_coverage(list(reversed(rows)), target_quotas=quotas) == result
    unknown = audit_source_coverage([{"source_id": "u"}])
    assert unknown["dimension_summaries"]["region"]["unknown_count"] == 1
    with pytest.raises(ValueError, match="unique"):
        audit_source_coverage([{"source_id": "x"}, {"source_id": "x"}])
    with pytest.raises(ValueError, match="unsupported dimension"):
        audit_source_coverage(rows, target_quotas=[{"dimension": "trust", "value": "high", "minimum_count": 1}])
    with pytest.raises(ValueError, match="unique"):
        audit_source_coverage(rows, target_quotas=[{"dimension": "platform", "value": "x", "minimum_count": 1}, {"dimension": "platform", "value": "X", "minimum_count": 2}])
    with pytest.raises(ValueError, match="at most"):
        audit_source_coverage([{"source_id": str(i)} for i in range(5001)])

