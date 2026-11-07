import sqlite3
import pytest

from ssswet_core.accessibility_contrast import audit_contrast_pairs, contrast_ratio
from ssswet_core.agent_benchmark import compare_benchmark_reports, evaluate_agent_benchmark
from ssswet_core.dataset_drift import compare_dataset_summaries
from ssswet_core.locale_fallback import canonicalize_locale, resolve_locale
from ssswet_core.memory_retrieval import benchmark_retrieval, evaluate_retrieval, rank_memories
from ssswet_core.protective_test_comparison import compare_protective_tests
from ssswet_core.protocol_quality import assess_protocol_quality
from ssswet_core.rescue_inventory import plan_fresh_inventory
from ssswet_core.research_toolkit import execute_toolkit, toolkit_catalogue
from ssswet_core.spatiotemporal_mapping import SpatialObservation, interpolate_between, segment_track
from ssswet_core.storage_health import backup_sqlite, inspect_sqlite

def test_memory_retrieval_is_bounded_deterministic_and_provenance_preserving():
    records = [
        {"version_id": "m2", "topic": "thermal materials", "statement": "Thermal conductivity comparison", "source_ids": ["s2", "s1"], "experiment_ids": ["e1"], "status": "contested"},
        {"version_id": "m1", "topic": "orbital mechanics", "statement": "Orbital transfer windows", "source_ids": ["s3"]},
    ]
    result = rank_memories(records, "thermal conductivity")
    assert result["results"][0]["memory_id"] == "m2"
    assert result["results"][0]["provenance"]["source_ids"] == ["s2", "s1"]
    assert result["results"][0]["status"] == "contested"
    assert result["contested_records_suppressed"] is False
    assert rank_memories(records, "thermal conductivity")["results"] == result["results"]
    with pytest.raises(ValueError, match="500"):
        rank_memories(records * 251, "thermal")

def test_memory_retrieval_metrics_and_latency_are_reported_without_intelligence_claim():
    metrics = evaluate_retrieval([
        {"case_id": "q1", "relevant_ids": ["a"], "retrieved_ids": ["a", "b"]},
        {"case_id": "q2", "relevant_ids": ["c"], "retrieved_ids": ["x", "c"]},
    ], k=2)
    assert metrics["macro_metrics"]["recall_at_k"] == 1.0
    assert metrics["macro_metrics"]["reciprocal_rank"] == 0.75
    assert metrics["intelligence_claim"] is False
    records = [{"memory_id": f"m{i}", "statement": f"thermal research item {i}", "source_ids": [f"s{i}"]} for i in range(500)]
    measured = benchmark_retrieval(records, ["thermal research", "item 250"], repeats=3)
    assert measured["stable_rankings"] is True
    assert measured["median_latency_ms"] >= 0
    assert measured["p95_latency_ms"] >= measured["median_latency_ms"]

def test_agent_benchmark_is_versioned_auditable_and_compares_like_for_like():
    cases = [{"case_id": "c1", "capability": "materials", "weight": 2}, {"case_id": "c2", "capability": "statistics", "weight": 1}]
    reviews = [
        {"case_id": "c1", "outcome": "correct", "confidence": 0.9, "reviewer_id": "reviewer-a"},
        {"case_id": "c2", "outcome": "abstained", "confidence": 0.2, "reviewer_id": "reviewer-b"},
    ]
    first = evaluate_agent_benchmark(benchmark_id="core", version="1.0", cases=cases, reviews=reviews)
    second = evaluate_agent_benchmark(benchmark_id="core", version="1.1", cases=cases, reviews=[reviews[0], {**reviews[1], "outcome": "partial"}])
    assert first["case_set_sha256"] == second["case_set_sha256"]
    changed = evaluate_agent_benchmark(benchmark_id="core", version="1.2", cases=[{**cases[0], "prompt": "A changed task definition"}, cases[1]], reviews=reviews)
    assert changed["case_set_sha256"] != first["case_set_sha256"]
    assert first["weighted_score"] == pytest.approx(2 / 3)
    assert first["coverage"] == 1
    assert first["capability_scores"]["materials"]["weighted_score"] == 1
    assert first["capability_scores"]["statistics"]["coverage"] == 1
    assert first["general_intelligence_or_real_world_competence_claim"] is False
    diff = compare_benchmark_reports(first, second)
    assert diff["comparison_is_like_for_like"] is True
    assert diff["changed_cases"][0]["case_id"] == "c2"
    with pytest.raises(ValueError, match="reviewer_id"):
        evaluate_agent_benchmark(benchmark_id="x", version="1", cases=cases, reviews=[{"case_id": "c1", "outcome": "correct", "confidence": 1}])

def test_dataset_drift_uses_aggregate_statistics_and_flags_shift():
    baseline = {"features": {"temperature": {"kind": "numeric", "count": 100, "mean": 20, "stddev": 2}, "region": {"kind": "categorical", "counts": {"north": 80, "south": 20}}}}
    current = {"features": {"temperature": {"kind": "numeric", "count": 120, "mean": 25, "stddev": 2}, "region": {"kind": "categorical", "counts": {"north": 20, "south": 80}}}}
    result = compare_dataset_summaries(baseline, current)
    assert result["features_flagged_for_review"] == 2
    assert result["raw_rows_received"] is False
    assert result["drift_is_not_causality_or_data_invalidity"] is True
    constant = {"features": {"constant": {"kind": "numeric", "count": 10, "mean": 1, "stddev": 0}}}
    variance = {"features": {"constant": {"kind": "numeric", "count": 10, "mean": 1, "stddev": 2}}}
    assert compare_dataset_summaries(constant, variance)["results"][0]["constant_baseline_variance_added"] is True
    with pytest.raises(ValueError, match="finite"):
        compare_dataset_summaries({"features": {"x": {"kind": "numeric", "count": 2, "mean": float("nan"), "stddev": 1}}}, current)

def _observation(identifier, lat, lon, time, accuracy=8):
    return SpatialObservation(identifier, lat, lon, time, accuracy, f"source:{identifier}")

def test_spatiotemporal_mapping_segments_bad_gaps_and_only_interpolates_inside_interval():
    a = _observation("a", 48.0, 2.0, "2026-11-07T10:00:00Z")
    b = _observation("b", 48.0005, 2.0005, "2026-11-07T10:01:00Z")
    c = _observation("c", 48.001, 2.001, "2026-11-07T11:00:00Z")
    result = segment_track([c, a, b])
    assert result["segment_count"] == 2
    assert result["breaks"][0]["reason"] == "time_gap_exceeds_threshold"
    point = interpolate_between(a, b, "2026-11-07T10:00:30Z")
    assert point["derived"] is True and point["not_an_observation"] is True
    assert point["source_refs"] == ["source:a", "source:b"]
    with pytest.raises(ValueError, match="strictly between"):
        interpolate_between(a, b, "2026-11-07T10:00:00Z")
    with pytest.raises(ValueError, match="max_gap_seconds"):
        interpolate_between(a, b, "2026-11-07T10:00:30Z", max_gap_seconds=float("nan"))
    with pytest.raises(ValueError, match="timezone-naive"):
        _observation("naive", 48, 2, "2026-11-07T10:00:00")

def test_rescue_inventory_excludes_expired_quarantined_and_unverified_lots():
    lots = [
        {"lot_id": "late", "resource": "water", "quantity": 8, "expires_on": "2027-01-01", "inspected_on": "2026-11-01", "storage_status": "verified"},
        {"lot_id": "early", "resource": "water", "quantity": 4, "expires_on": "2026-12-01", "inspected_on": "2026-11-06", "storage_status": "verified"},
        {"lot_id": "expired", "resource": "water", "quantity": 50, "expires_on": "2026-11-06", "inspected_on": "2026-11-06", "storage_status": "verified"},
        {"lot_id": "quarantine", "resource": "water", "quantity": 50, "expires_on": "2027-01-01", "inspected_on": "2026-11-06", "storage_status": "verified", "quarantined": True},
    ]
    requests = [{"request_id": "r1", "priority": 5, "needs": {"water": 6}}, {"request_id": "r2", "priority": 5, "needs": {"water": 6}}]
    result = plan_fresh_inventory(lots, requests, as_of="2026-11-07")
    assert {item["lot_id"] for item in result["excluded_lots"]} == {"expired", "quarantine"}
    assert result["requests"][0]["allocations"]["water"][0]["lot_id"] == "early"
    assert sum(item["granted_totals"].get("water", 0) for item in result["requests"]) == 12
    assert result["requires_human_dispatch"] is True

def test_protective_test_comparison_only_groups_matching_conditions_and_normalizes_units():
    base = {"test_method": "drop-test-v1", "configuration": "panel-a", "conditioning": "dry-23c", "orientation": "normal", "metric": "absorbed_energy", "replicates": 3, "source_ref": "report:1"}
    result = compare_protective_tests([
        {"test_id": "t1", **base, "unit": "J", "value": 100, "uncertainty": 5},
        {"test_id": "t2", **{**base, "source_ref": "report:2"}, "unit": "kJ", "value": 0.11, "uncertainty": 0.005},
        {"test_id": "t3", **{**base, "conditioning": "wet-23c", "source_ref": "report:3"}, "unit": "J", "value": 150},
    ])
    assert result["group_count"] == 2
    assert result["comparable_group_count"] == 1
    comparable = next(item for item in result["groups"] if item["comparable_records_present"])
    assert comparable["mean_base_unit"] == pytest.approx(105)
    assert result["certification_or_safety_rating_established"] is False

def test_protocol_quality_requires_explicit_design_rationales_and_never_approves():
    protocol = {field: f"Documented {field}" for field in (
        "research_question", "hypotheses", "primary_outcome", "method", "analysis_plan", "sample_size_rationale",
        "inclusion_criteria", "exclusion_criteria", "stopping_rule", "missing_data_plan", "safety_review_reference", "deviations_policy")}
    protocol.update({"randomization": {"status": "not_applicable", "reason": "Observational study."}, "blinding": {"status": "not_applicable", "reason": "No intervention is assigned."}})
    result = assess_protocol_quality(protocol)
    assert result["structurally_ready_for_independent_review"] is True
    assert result["ethics_or_safety_approval_granted"] is False
    del protocol["safety_review_reference"]
    assert assess_protocol_quality(protocol)["structurally_ready_for_independent_review"] is False

def test_storage_health_is_read_only_and_backup_is_verified_without_overwrite(tmp_path):
    source = tmp_path / "research.sqlite3"
    connection = sqlite3.connect(source)
    connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, label TEXT)")
    connection.execute("INSERT INTO notes(label) VALUES ('private-content-not-returned')")
    connection.commit()
    connection.close()
    before = source.read_bytes()
    report = inspect_sqlite(source)
    assert report["integrity_ok"] is True
    assert report["tables"] == [{"table": "notes", "row_count": 1, "sampled_at_least_1001": False, "sample_limit": 1000}]
    assert report["database_rows_or_content_exposed"] is False
    assert source.read_bytes() == before
    backup = backup_sqlite(source, tmp_path / "backup.sqlite3")
    assert backup["verified"] is True and backup["sha256"]
    with pytest.raises(FileExistsError):
        backup_sqlite(source, tmp_path / "backup.sqlite3")

def test_accessibility_contrast_checks_wcag_aa_and_rejects_unsupported_colors():
    assert contrast_ratio("#000", "#fff") == pytest.approx(21)
    result = audit_contrast_pairs([
        {"name": "body", "foreground": "#777777", "background": "#ffffff", "usage": "normal_text"},
        {"name": "icon", "foreground": "rgb(0,0,0)", "background": "#fff", "usage": "ui_component"},
        {"name": "gradient", "foreground": "transparent", "background": "#fff"},
    ])
    assert result["results"][0]["wcag_aa_pass"] is False
    assert result["results"][1]["wcag_aa_pass"] is True
    assert result["results"][2]["valid"] is False
    assert result["full_accessibility_conformance_established"] is False

def test_locale_fallback_is_bcp47_aware_and_preserves_rtl_direction():
    assert canonicalize_locale("zh_hant_tw") == "zh-Hant-TW"
    result = resolve_locale("ar-EG", ["en", "ar", "fr"], fallback="en")
    assert result["resolved"] == "ar" and result["direction"] == "rtl"
    fallback = resolve_locale("fr-CA", ["en", "fr"], fallback="en")
    assert fallback["resolved"] == "fr" and fallback["fallback_used"] is True
    assert fallback["automatic_translation_performed"] is False

def test_local_toolkit_dispatch_exposes_exactly_ten_operations_and_is_non_mutating(tmp_path):
    catalogue = toolkit_catalogue()
    assert catalogue["operation_count"] == 10
    catalogue["operations"].clear()
    assert toolkit_catalogue()["operation_count"] == 10
    result = execute_toolkit({"tool": "locale_resolve", "requested": "fr-CA", "available": ["en", "fr"]})
    assert result["resolved"] == "fr"
    db = tmp_path / "health.sqlite3"
    sqlite3.connect(db).close()
    assert execute_toolkit({"tool": "storage_health"}, database_path=db)["integrity_ok"] is True
    with pytest.raises(ValueError, match="unknown"):
        execute_toolkit({"tool": "unknown"})
