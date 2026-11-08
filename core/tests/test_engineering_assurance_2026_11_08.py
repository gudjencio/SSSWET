from __future__ import annotations

import io
import zipfile

import pytest

from ssswet_core.sensor_clock_alignment import align_observations, fit_clock_map
from ssswet_core.uncertainty_budget import propagate_linear
from ssswet_core.calibration_registry import assess_calibration, audit_registry
from ssswet_core.reliability_survival import kaplan_meier
from ssswet_core.measurement_repeatability import analyze_repeatability
from ssswet_core.failure_mode_review import assess_failure_modes
from ssswet_core.robust_pareto import analyze_frontier
from ssswet_core.requirements_traceability import build_traceability_matrix
from ssswet_core.lifecycle_inventory import aggregate_inventory
from ssswet_core.reproducible_bundle import build_bundle, verify_bundle


def test_sensor_clock_alignment_is_robust_bounded_and_preserves_original_times():
    anchors = [
        {"source_id": f"sync-{i}", "sensor_seconds": i * 100.0,
         "reference_seconds": 7.0 + i * 100.001 + (0.2 if i == 2 else 0.0),
         "uncertainty_seconds": 0.01}
        for i in range(5)
    ]
    clock = fit_clock_map(anchors)
    assert clock["method"] == "theil_sen_pairwise_median"
    assert clock["slope"] == pytest.approx(1.00001)
    assert clock["offset_seconds"] == pytest.approx(7.0)
    result = align_observations([
        {"source_id": "gps-1", "sensor_seconds": 50, "uncertainty_seconds": 0.02},
        {"source_id": "gps-outside", "sensor_seconds": 500},
    ], clock)
    assert result["aligned_count"] == 1
    assert result["aligned"][0]["original_sensor_seconds"] == 50
    assert result["aligned"][0]["source_timestamp_preserved"] is True
    assert result["rejected"][0]["reason"] == "outside_anchor_interval"
    assert result["extrapolated_count"] == 0
    with pytest.raises(ValueError):
        fit_clock_map([anchors[0], anchors[0]])


def test_uncertainty_budget_includes_covariance_and_rejects_invalid_matrix():
    components = [
        {"name": "length", "sensitivity": 1.0, "standard_uncertainty": 1.0},
        {"name": "offset", "sensitivity": 1.0, "standard_uncertainty": 1.0},
    ]
    independent = propagate_linear(components)
    correlated = propagate_linear(components, [[1.0, 0.5], [0.5, 1.0]])
    assert independent["combined_standard_uncertainty"] == pytest.approx(2 ** 0.5)
    assert correlated["combined_standard_uncertainty"] == pytest.approx(3 ** 0.5)
    assert correlated["worst_case_absolute_bound"] == 2.0
    with pytest.raises(ValueError, match=r"values in \[-1, 1\]"):
        propagate_linear(components, [[1.0, 1.5], [1.5, 1.0]])
    three = components + [{"name": "gain", "sensitivity": 1.0, "standard_uncertainty": 1.0}]
    invalid_psd = [[1.0, 0.9, 0.9], [0.9, 1.0, -0.9], [0.9, -0.9, 1.0]]
    with pytest.raises(ValueError, match="positive semidefinite"):
        propagate_linear(three, invalid_psd)


def test_calibration_registry_checks_validity_review_and_traceability():
    record = {
        "instrument_id": "sensor-01", "calibration_id": "cal-2026-01",
        "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z",
        "certificate_sha256": "a" * 64, "calibration_provider": "Independent Lab",
        "traceability_refs": ["standard:SI-01"], "expanded_uncertainty": 0.02,
        "uncertainty_unit": "mm", "review_state": "reviewed", "reviewer": "reviewer-1", "reviewed_at": "2026-01-01T00:00:00Z",
    }
    valid = assess_calibration(record, at="2026-11-08T09:00:00+01:00", max_uncertainty=0.03)
    assert valid["metadata_complete_for_review"] is True
    assert valid["certificate_content_verified"] is False
    expired = assess_calibration(record, at="2027-01-01T00:00:00Z")
    assert "outside_validity_window" in expired["reasons"]
    pending = {**record, "review_state": "pending", "traceability_refs": []}
    assert audit_registry([pending], at="2026-11-08T00:00:00Z")["metadata_complete_count"] == 0
    with pytest.raises(ValueError):
        assess_calibration({**record, "certificate_sha256": "not-a-digest"}, at="2026-11-08T00:00:00Z")


def test_kaplan_meier_handles_tied_events_and_right_censoring():
    result = kaplan_meier([
        {"observation_id": "a", "duration": 1, "event_observed": True},
        {"observation_id": "b", "duration": 2, "event_observed": False},
        {"observation_id": "c", "duration": 3, "event_observed": True},
        {"observation_id": "d", "duration": 3, "event_observed": True},
    ])
    assert result["event_count"] == 3
    assert result["censored_count"] == 1
    assert result["curve"][0]["survival_probability"] == pytest.approx(0.75)
    assert result["curve"][-1]["survival_probability"] == 0.0
    assert result["median_event_time"] == 3
    assert result["parametric_extrapolation_performed"] is False
    with pytest.raises(ValueError):
        kaplan_meier([{"observation_id": "x", "duration": -1, "event_observed": True}])


def test_repeatability_requires_balanced_replicates_and_reports_components():
    result = analyze_repeatability([
        {"group_id": "operator-a", "values": [1, 2, 3]},
        {"group_id": "operator-b", "values": [2, 3, 4]},
    ])
    assert result["repeatability_standard_deviation"] == pytest.approx(1.0)
    assert result["between_group_standard_deviation"] > 0
    assert result["accreditation_or_standard_conformance_claimed"] is False
    with pytest.raises(ValueError, match="equal replicate counts"):
        analyze_repeatability([
            {"group_id": "a", "values": [1, 2]},
            {"group_id": "b", "values": [1, 2, 3]},
        ])


def test_failure_mode_review_keeps_separate_ratings_and_requires_closure_evidence():
    result = assess_failure_modes([{
        "mode_id": "seal-leak", "subsystem": "housing", "failure_mode": "seal leakage",
        "effect": "loss of enclosure integrity", "cause": "wear", "severity": 4,
        "occurrence": 2, "detectability": 3, "controls": [], "evidence_refs": ["test:17"],
    }])
    assert result["requires_human_attention_count"] == 1
    assert result["results"][0]["composite_risk_priority_number"] is None
    with pytest.raises(ValueError, match="closure evidence"):
        assess_failure_modes([{
            "mode_id": "x", "subsystem": "s", "failure_mode": "f", "effect": "e", "cause": "c",
            "severity": 1, "occurrence": 1, "detectability": 1, "action_state": "closed",
        }])


def test_interval_pareto_frontier_does_not_force_a_single_winner():
    result = analyze_frontier([
        {"alternative_id": "A", "metrics": {"cost": {"value": 1}, "performance": {"value": 9}}},
        {"alternative_id": "B", "metrics": {"cost": {"value": 2}, "performance": {"value": 8}}},
        {"alternative_id": "C", "metrics": {"cost": {"value": 1.5, "uncertainty": 0.5}, "performance": {"value": 9, "uncertainty": 1}}},
    ], [
        {"name": "cost", "direction": "minimize"},
        {"name": "performance", "direction": "maximize"},
    ])
    assert result["pareto_frontier_ids"] == ["A", "C"]
    assert {(p["dominant"], p["dominated"]) for p in result["dominance_pairs"]} == {("A", "B")}
    assert result["single_best_alternative_selected"] is False


def test_requirements_traceability_surfaces_broken_orphan_and_inconclusive_evidence():
    result = build_traceability_matrix([
        {"requirement_id": "REQ-1", "description": "retain enclosure", "verification_method": "test", "evidence_refs": ["EV-1"]},
        {"requirement_id": "REQ-2", "description": "support service access", "verification_method": "inspection", "evidence_refs": ["MISSING"]},
    ], [
        {"evidence_id": "EV-1", "result": "pass", "reviewer": "reviewer-1", "provenance_ref": "run:123"},
        {"evidence_id": "ORPHAN", "result": "inconclusive"},
    ])
    assert result["reviewed_pass_count"] == 1
    assert result["broken_evidence_refs"] == ["MISSING"]
    assert result["orphan_evidence_ids"] == ["ORPHAN"]
    assert result["design_certification_or_safety_approval_granted"] is False


def test_lifecycle_inventory_aggregates_only_explicitly_compatible_units_and_sources():
    result = aggregate_inventory([
        {"flow_id": "steel", "phase": "manufacture", "quantity": 10, "quantity_unit": "kg", "factor_basis_unit": "kg", "factor_value": 2, "factor_uncertainty": 0.1, "quantity_uncertainty": 1, "impact_unit": "kgCO2e", "factor_source_id": "db:1", "factor_version": "v1"},
        {"flow_id": "polymer", "phase": "manufacture", "quantity": 5, "quantity_unit": "kg", "factor_basis_unit": "kg", "factor_value": 3, "impact_unit": "kgCO2e", "factor_source_id": "db:2", "factor_version": "v2"},
    ])
    total = result["phase_totals"][0]
    assert total["impact_total"] == pytest.approx(35)
    assert total["combined_standard_uncertainty"] == pytest.approx(5 ** 0.5)
    assert result["source_count"] == 2
    with pytest.raises(ValueError, match="must exactly match"):
        aggregate_inventory([{"flow_id": "bad", "phase": "use", "quantity": 1, "quantity_unit": "g", "factor_basis_unit": "kg", "factor_value": 2, "impact_unit": "kgCO2e", "factor_source_id": "db", "factor_version": "1"}])


def test_reproducible_bundle_is_deterministic_and_detects_tampering():
    files = {"data/observations.json": '{"count":2}', "protocol.md": "Reviewed protocol"}
    first = build_bundle(files)
    second = build_bundle(files)
    assert first == second
    assert verify_bundle(first)["valid"] is True
    with zipfile.ZipFile(io.BytesIO(first), "r") as source:
        entries = {name: source.read(name) for name in source.namelist()}
    entries["protocol.md"] = b"Changed after bundling"
    tampered = io.BytesIO()
    with zipfile.ZipFile(tampered, "w") as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    result = verify_bundle(tampered.getvalue())
    assert result["valid"] is False
    assert result["reason"] == "size_or_digest_mismatch"
    with pytest.raises(ValueError, match="path traversal"):
        build_bundle({"../escape.txt": "no"})
    with pytest.raises(ValueError, match="private key"):
        build_bundle({"notes.txt": "-----BEGIN RSA PRIVATE KEY-----"})


def test_sensor_clock_alignment_rejects_excess_drift_and_non_monotonic_mapping():
    anchors = [
        {"source_id": "a", "sensor_seconds": 0, "reference_seconds": 0},
        {"source_id": "b", "sensor_seconds": 100, "reference_seconds": 101},
    ]
    with pytest.raises(ValueError, match="drift"):
        fit_clock_map(anchors, max_drift_ppm=100)
    with pytest.raises(ValueError, match="forward-running"):
        fit_clock_map([
            {"source_id": "a", "sensor_seconds": 0, "reference_seconds": 10},
            {"source_id": "b", "sensor_seconds": 1, "reference_seconds": 9},
        ])


def test_uncertainty_budget_rejects_non_finite_and_negative_uncertainties():
    with pytest.raises(ValueError):
        propagate_linear([{"name": "x", "sensitivity": 1, "standard_uncertainty": float("nan")}])
    with pytest.raises(ValueError, match="cannot be negative"):
        propagate_linear([{"name": "x", "sensitivity": 1, "standard_uncertainty": -0.1}])


def test_calibration_registry_rejects_naive_dates_and_duplicate_instruments():
    record = {
        "instrument_id": "sensor-01", "calibration_id": "cal-1",
        "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z",
        "certificate_sha256": "b" * 64, "calibration_provider": "Lab",
        "traceability_refs": ["ref:1"], "expanded_uncertainty": 0.1,
        "uncertainty_unit": "mm", "review_state": "reviewed",
    }
    with pytest.raises(ValueError, match="timezone"):
        assess_calibration({**record, "valid_from": "2026-01-01T00:00:00"}, at="2026-02-01T00:00:00Z")
    with pytest.raises(ValueError, match="only once"):
        audit_registry([record, record], at="2026-02-01T00:00:00Z")


def test_kaplan_meier_reports_unreached_median_when_all_observations_are_censored():
    result = kaplan_meier([
        {"observation_id": "a", "duration": 2, "event_observed": False},
        {"observation_id": "b", "duration": 4, "event_observed": False},
    ])
    assert result["median_not_reached"] is True
    assert result["median_event_time"] is None
    assert result["curve"][-1]["survival_probability"] == 1.0


def test_repeatability_zero_variance_is_reported_without_division_error():
    result = analyze_repeatability([
        {"group_id": "a", "values": [5, 5]},
        {"group_id": "b", "values": [5, 5]},
    ])
    assert result["combined_standard_deviation"] == 0
    assert result["between_group_variance_fraction"] is None


def test_failure_mode_closed_action_is_traceable_but_not_certified():
    result = assess_failure_modes([{
        "mode_id": "seal", "subsystem": "housing", "failure_mode": "leak",
        "effect": "water ingress", "cause": "seal wear", "severity": 4,
        "occurrence": 2, "detectability": 2, "controls": ["inspection"],
        "evidence_refs": ["test:1"], "closure_evidence_refs": ["review:2"],
        "reviewer": "independent-reviewer", "action_state": "closed",
    }])
    assert result["requires_human_attention_count"] == 0
    assert result["safety_certification_or_authorization_granted"] is False


def test_pareto_frontier_rejects_missing_objectives_and_preserves_overlap():
    with pytest.raises(ValueError, match="exactly one metric"):
        analyze_frontier([{"alternative_id": "A", "metrics": {}}], [{"name": "cost", "direction": "minimize"}])
    result = analyze_frontier([
        {"alternative_id": "A", "metrics": {"cost": {"value": 1, "uncertainty": 1}}},
        {"alternative_id": "B", "metrics": {"cost": {"value": 2, "uncertainty": 1}}},
    ], [{"name": "cost", "direction": "minimize"}])
    assert result["pareto_frontier_ids"] == ["A", "B"]
    assert result["dominance_pairs"] == []


def test_traceability_does_not_hide_failures_behind_a_passing_record():
    result = build_traceability_matrix([
        {"requirement_id": "R", "description": "requirement", "verification_method": "test", "evidence_refs": ["PASS", "FAIL"]},
    ], [
        {"evidence_id": "PASS", "result": "pass", "reviewer": "reviewer", "provenance_ref": "run:1"},
        {"evidence_id": "FAIL", "result": "fail", "reviewer": "reviewer", "provenance_ref": "run:2"},
    ])
    assert result["matrix"][0]["state"] == "conflicting_or_inconclusive_evidence"
    assert result["unverified_requirement_ids"] == ["R"]


def test_lifecycle_inventory_rejects_duplicate_flow_ids_and_nan_values():
    flow = {"flow_id": "f", "phase": "use", "quantity": 1, "quantity_unit": "kg", "factor_basis_unit": "kg", "factor_value": 2, "impact_unit": "kgCO2e", "factor_source_id": "db", "factor_version": "1"}
    with pytest.raises(ValueError, match="unique"):
        aggregate_inventory([flow, flow])
    with pytest.raises(ValueError, match="finite"):
        aggregate_inventory([{**flow, "quantity": float("nan")}])


def test_reproducible_bundle_rejects_sensitive_paths_and_oversized_archives():
    with pytest.raises(ValueError, match="sensitive artifact paths"):
        build_bundle({".env": "API_KEY=example"})
    with pytest.raises(ValueError, match="per-file size"):
        build_bundle({"large.bin": b"x" * (5 * 1024 * 1024 + 1)})


def test_calibration_review_cannot_be_marked_complete_without_attribution():
    record = {
        "instrument_id": "sensor-02", "calibration_id": "cal-2",
        "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z",
        "certificate_sha256": "c" * 64, "calibration_provider": "Lab",
        "traceability_refs": ["standard:SI-02"], "expanded_uncertainty": 0.1,
        "uncertainty_unit": "mm", "review_state": "reviewed",
        "reviewed_at": "2026-02-01T00:00:00Z",
    }
    with pytest.raises(ValueError, match="require a reviewer"):
        assess_calibration(record, at="2026-03-01T00:00:00Z")
