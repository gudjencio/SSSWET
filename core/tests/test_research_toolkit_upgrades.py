import hashlib
import sqlite3
import pytest

from ssswet_core.accessibility_contrast import audit_contrast_pairs, contrast_ratio
from ssswet_core.agent_benchmark import compare_benchmark_reports, evaluate_agent_benchmark
from ssswet_core.dataset_drift import compare_dataset_summaries
from ssswet_core.locale_fallback import canonicalize_locale, resolve_locale
from ssswet_core.memory_revision_diff import compare_memory_revisions
from ssswet_core.protective_test_comparison import compare_protective_tests
from ssswet_core.protocol_quality import assess_protocol_quality
from ssswet_core.rescue_inventory import plan_fresh_inventory
from ssswet_core.research_toolkit import execute_toolkit, toolkit_catalogue
from ssswet_core.spatiotemporal_mapping import SpatialObservation, interpolate_between, segment_track
from ssswet_core.storage_health import backup_sqlite, inspect_sqlite


def test_memory_revision_diff_tracks_claim_review_provenance_and_untracked_fields():
    previous = {
        "snapshot_id": "snapshot-1",
        "records": [
            {"memory_id": "m1", "memory_key": "thermal", "statement": "Old claim", "status": "candidate",
             "source_ids": ["s1", "s2"], "provenance_group": "group-a", "custom_metadata": {"revision": 1}},
            {"memory_id": "m2", "statement": "Retained only in the previous snapshot", "source_ids": ["s3"]},
        ],
    }
    current = {
        "snapshot_id": "snapshot-2",
        "records": [
            {"memory_id": "m1", "memory_key": "thermal", "statement": "Revised claim", "status": "contested",
             "source_ids": ["s2", "s4"], "provenance_group": "group-b", "custom_metadata": {"revision": 2}},
            {"memory_id": "m3", "statement": "New record", "review_refs": ["review-1"]},
        ],
    }
    result = compare_memory_revisions(previous, current)
    changed = result["changed_records"][0]
    assert result["added_memory_ids"] == ["m3"]
    assert result["absent_from_current_snapshot_ids"] == ["m2"]
    assert result["absent_records_are_not_deleted_by_this_tool"] is True
    assert changed["claim_text_changed"] is True
    assert changed["review_state_changed"] is True
    assert changed["provenance_delta"]["source_ids"] == {"added": ["s4"], "removed": ["s1"]}
    assert changed["provenance_delta"]["provenance_group"] == {"previous": "group-a", "current": "group-b"}
    assert changed["untracked_fields_changed"] == ["custom_metadata"]
    assert changed["previous_record_sha256"] != changed["current_record_sha256"]
    assert result["records_or_review_states_modified"] is False


def test_memory_revision_diff_rejects_duplicates_and_oversized_snapshots():
    duplicate = {"snapshot_id": "x", "records": [{"memory_id": "same"}, {"memory_id": "same"}]}
    with pytest.raises(ValueError, match="duplicate"):
        compare_memory_revisions(duplicate, {"snapshot_id": "y", "records": []})
    oversized = {"snapshot_id": "large", "records": [{"memory_id": f"m{i}"} for i in range(501)]}
    with pytest.raises(ValueError, match="500"):
        compare_memory_revisions(oversized, {"snapshot_id": "small", "records": []})


def test_agent_benchmark_is_versioned_auditable_and_compares_only_identical_case_sets():
    cases = [{"case_id": "c1", "capability": "materials", "weight": 2}, {"case_id": "c2", "capability": "statistics", "weight": 1}]
    reviews = [
        {"case_id": "c1", "outcome": "correct", "confidence": 0.9, "reviewer_id": "reviewer-a"},
        {"case_id": "c2", "outcome": "abstained", "confidence": 0.2, "reviewer_id": "reviewer-b"},
    ]
    first = evaluate_agent_benchmark(benchmark_id="core", version="1.0", cases=cases, reviews=reviews)
    second = evaluate_agent_benchmark(benchmark_id="core", version="1.1", cases=cases, reviews=[reviews[0], {**reviews[1], "outcome": "partial"}])
    assert first["case_set_sha256"] == second["case_set_sha256"]
    assert first["weighted_score"] == pytest.approx(2 / 3)
    assert first["coverage"] == 1
    assert first["capability_scores"]["materials"]["weighted_score"] == 1
    assert first["capability_scores"]["statistics"]["coverage"] == 1
    assert first["general_intelligence_or_real_world_competence_claim"] is False
    diff = compare_benchmark_reports(first, second)
    assert diff["comparison_is_like_for_like"] is True
    assert diff["changed_cases"][0]["case_id"] == "c2"
    changed_cases = [{**cases[0], "prompt": "A changed task definition"}, cases[1]]
    changed = evaluate_agent_benchmark(benchmark_id="core", version="1.2", cases=changed_cases, reviews=reviews)
    changed_diff = compare_benchmark_reports(first, changed)
    assert changed_diff["comparison_is_like_for_like"] is False
    assert changed_diff["changed_case_definition_ids"] == ["c1"]
    assert changed_diff["weighted_score_delta"] is None
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
    with pytest.raises(ValueError, match="integer"):
        compare_dataset_summaries({"features": {"x": {"kind": "numeric", "count": 1.5, "mean": 1, "stddev": 1}}}, current)


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
    too_many = (_observation(f"gps-{i}", 48, 2, "2026-11-07T10:00:00Z") for i in range(5001))
    with pytest.raises(ValueError, match="5000"):
        segment_track(too_many)


def test_rescue_inventory_excludes_unfit_stock_and_respects_priority_and_fairness():
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
    priority_result = plan_fresh_inventory(
        [{"lot_id": "w1", "resource": "water", "quantity": 5, "expires_on": "2027-01-01", "inspected_on": "2026-11-07", "storage_status": "verified"}],
        [{"request_id": "urgent", "priority": 5, "needs": {"water": 5}},
         {"request_id": "later", "priority": 1, "needs": {"water": 5}}],
        as_of="2026-11-07",
    )
    grants = {item["request_id"]: item["granted_totals"].get("water", 0) for item in priority_result["requests"]}
    assert grants == {"urgent": 5, "later": 0}
    assert sum(grants.values()) <= 5


def test_protective_test_comparison_matches_conditions_and_weights_reported_replicates():
    base = {"test_method": "drop-test-v1", "configuration": "panel-a", "conditioning": "dry-23c", "orientation": "normal", "metric": "absorbed_energy", "source_ref": "report:1"}
    result = compare_protective_tests([
        {"test_id": "t1", **base, "unit": "J", "value": 100, "replicates": 3, "uncertainty": 5},
        {"test_id": "t2", **{**base, "source_ref": "report:2"}, "unit": "kJ", "value": 0.11, "replicates": 1},
        {"test_id": "t3", **{**base, "conditioning": "wet-23c", "source_ref": "report:3"}, "unit": "J", "value": 150, "replicates": 1},
    ])
    assert result["group_count"] == 2
    assert result["comparable_group_count"] == 1
    comparable = next(item for item in result["groups"] if item["comparable_records_present"])
    assert comparable["mean_base_unit"] == pytest.approx(102.5)
    assert comparable["mean_record_value_base_unit"] == pytest.approx(105)
    assert comparable["uncertainty_declared_for_all_records"] is False
    assert comparable["mean_declared_measurement_uncertainty_base_unit"] == pytest.approx(5)
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


def test_storage_health_is_read_only_and_backup_is_hash_verified_without_overwrite(tmp_path):
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
    backup_path = tmp_path / "backup.sqlite3"
    backup = backup_sqlite(source, backup_path)
    assert backup["verified"] is True and backup["destination_hash_verified"] is True
    assert hashlib.sha256(backup_path.read_bytes()).hexdigest() == backup["sha256"]
    with pytest.raises(FileExistsError):
        backup_sqlite(source, backup_path)


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


def test_locale_fallback_respects_explicit_script_direction():
    assert canonicalize_locale("zh_hant_tw") == "zh-Hant-TW"
    arabic = resolve_locale("ar-EG", ["en", "ar", "fr"], fallback="en")
    assert arabic["resolved"] == "ar" and arabic["direction"] == "rtl"
    fallback = resolve_locale("fr-CA", ["en", "fr"], fallback="en")
    assert fallback["resolved"] == "fr" and fallback["fallback_used"] is True
    assert fallback["automatic_translation_performed"] is False
    assert resolve_locale("ku-Latn", ["en", "ku-Latn"], fallback="en")["direction"] == "ltr"
    assert resolve_locale("ku-Arab", ["en", "ku-Arab"], fallback="en")["direction"] == "rtl"
    assert resolve_locale("pa-Arab", ["en", "pa-Arab"], fallback="en")["direction"] == "rtl"
    assert resolve_locale("pa-Guru", ["en", "pa-Guru"], fallback="en")["direction"] == "ltr"


def test_local_toolkit_dispatch_exposes_exactly_ten_operations_and_is_non_mutating(tmp_path):
    catalogue = toolkit_catalogue()
    assert catalogue["operation_count"] == 10
    assert "memory_revision_diff" in catalogue["operations"]
    catalogue["operations"].clear()
    assert toolkit_catalogue()["operation_count"] == 10
    previous = {"snapshot_id": "a", "records": [{"memory_id": "m1", "statement": "old"}]}
    current = {"snapshot_id": "b", "records": [{"memory_id": "m1", "statement": "new"}]}
    diff = execute_toolkit({"tool": "memory_revision_diff", "previous": previous, "current": current})
    assert diff["changed_records"][0]["claim_text_changed"] is True
    result = execute_toolkit({"tool": "locale_resolve", "requested": "fr-CA", "available": ["en", "fr"]})
    assert result["resolved"] == "fr"
    db = tmp_path / "health.sqlite3"
    sqlite3.connect(db).close()
    assert execute_toolkit({"tool": "storage_health"}, database_path=db)["integrity_ok"] is True
    with pytest.raises(ValueError, match="unknown"):
        execute_toolkit({"tool": "unknown"})
