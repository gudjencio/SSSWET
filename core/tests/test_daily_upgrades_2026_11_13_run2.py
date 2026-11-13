from __future__ import annotations

import pytest

from ssswet_core.hypothesis_testability import assess_hypothesis
from ssswet_core.replication_registry import ReplicationRegistry
from ssswet_core.evidence_coverage import audit_claim_coverage
from ssswet_core.source_audit_calibration import summarize_source_audits
from ssswet_core.dataset_shift import compare_dataset_summaries
from ssswet_core.dependency_readiness import analyze_dependencies
from ssswet_core.pareto_design_frontier import compare_designs
from ssswet_core.safety_case_graph import audit_safety_case
from ssswet_core.vtt_local_frame_alignment import fit_local_frame_alignment
from ssswet_core.rescue_route_accessibility import review_route_accessibility


D1 = "a" * 64
D2 = "b" * 64


def valid_hypothesis():
    return {
        "research_question": "Does treatment X change measured output Y?",
        "system_scope": "Bench-scale non-human material under controlled conditions",
        "comparator": "Matched untreated control",
        "time_horizon": "24 hours",
        "measurement_context": "Calibrated instrument with documented resolution",
        "independent_variables": [
            {"name": "treatment concentration", "unit": "mg/L", "operational_definition": "Measured concentration in prepared solution"}
        ],
        "outcomes": [
            {"name": "output Y", "unit": "mmol/L", "measurement_method": "Validated assay with replicate readings"}
        ],
        "falsification_conditions": ["No difference within the predeclared equivalence margin"],
        "alternative_explanations": ["Instrument drift", "Batch variation"],
        "safety_constraints": ["No human or animal subjects; institutional review before any scope change"],
    }


def test_hypothesis_operationalisation_and_non_claim():
    result = assess_hypothesis(valid_hypothesis())
    assert result["complete_for_protocol_review"] is True
    assert result["status"] == "ready_for_protocol_review"
    assert result["scientific_validity_established"] is False
    assert result["hypothesis_tested"] is False


def test_hypothesis_reports_missing_fields_and_rejects_nonfinite():
    result = assess_hypothesis({"research_question": "A question"})
    assert "safety_constraints" in result["missing_or_invalid_fields"]
    with pytest.raises(ValueError):
        assess_hypothesis({"research_question": "x", "bad": float("nan")})


def test_hypothesis_rejects_duplicate_variables():
    spec = valid_hypothesis()
    spec["independent_variables"].append(dict(spec["independent_variables"][0]))
    with pytest.raises(ValueError):
        assess_hypothesis(spec)


def test_replication_registry_preserves_negative_and_compares_inputs():
    registry = ReplicationRegistry()
    registry.record_attempt(
        run_id="run-a", protocol_fingerprint=D1, dataset_fingerprints=[D2],
        environment_fingerprint=D1, analysis_fingerprint=D2, outcome="negative",
    )
    registry.record_attempt(
        run_id="run-b", protocol_fingerprint=D1, dataset_fingerprints=[D2],
        environment_fingerprint=D1, analysis_fingerprint=D2, outcome="inconclusive",
    )
    result = registry.compare("run-a", "run-b")
    assert result["comparability"] == "same_declared_inputs_and_method"
    assert result["outcomes"] == {"left": "negative", "right": "inconclusive"}
    assert result["replication_success_established"] is False
    with pytest.raises(ValueError):
        registry.record_attempt(
            run_id="run-a", protocol_fingerprint=D1, dataset_fingerprints=[],
            environment_fingerprint=D1, analysis_fingerprint=D1, outcome="positive",
        )


def test_replication_registry_rejects_bad_digest_and_exposes_mismatch():
    registry = ReplicationRegistry()
    with pytest.raises(ValueError):
        registry.record_attempt(
            run_id="bad", protocol_fingerprint="not-a-digest", dataset_fingerprints=[],
            environment_fingerprint=D1, analysis_fingerprint=D1, outcome="failed",
        )
    registry.record_attempt(
        run_id="a", protocol_fingerprint=D1, dataset_fingerprints=[],
        environment_fingerprint=D1, analysis_fingerprint=D1, outcome="positive",
    )
    registry.record_attempt(
        run_id="b", protocol_fingerprint=D2, dataset_fingerprints=[],
        environment_fingerprint=D1, analysis_fingerprint=D1, outcome="positive",
    )
    assert registry.compare("a", "b")["comparability"] == "protocol_mismatch"


def test_evidence_coverage_deduplicates_provenance_and_keeps_counterevidence():
    claims = [{"claim_id": "c1", "text": "Claim one"}]
    evidence = [
        {"evidence_id": "e1", "source_id": "s1", "provenance_group": "publisher-a"},
        {"evidence_id": "e2", "source_id": "s2", "provenance_group": "publisher-a"},
        {"evidence_id": "e3", "source_id": "s3", "provenance_group": "publisher-b"},
        {"evidence_id": "e4", "source_id": "s4", "provenance_group": "publisher-c", "state": "withdrawn"},
        {"evidence_id": "e5", "source_id": "s5", "provenance_group": "publisher-d", "state": "under_review"},
    ]
    links = [
        {"claim_id": "c1", "evidence_id": "e1", "stance": "supports"},
        {"claim_id": "c1", "evidence_id": "e2", "stance": "supports"},
        {"claim_id": "c1", "evidence_id": "e3", "stance": "contradicts"},
        {"claim_id": "c1", "evidence_id": "e4", "stance": "supports"},
        {"claim_id": "c1", "evidence_id": "missing", "stance": "supports"},
        {"claim_id": "c1", "evidence_id": "e5", "stance": "supports"},
    ]
    result = audit_claim_coverage(claims, evidence, links)
    row = result["claims"][0]
    assert row["supporting_independent_group_count"] == 1
    assert row["contradicting_independent_group_count"] == 1
    assert row["under_review_group_count"] == 1
    assert row["contested"] is True
    assert row["withdrawn_evidence_ids"] == ["e4"]
    assert len(result["dangling_links"]) == 1
    assert result["scientific_truth_score"] is None


def test_evidence_coverage_rejects_duplicate_ids():
    with pytest.raises(ValueError):
        audit_claim_coverage(
            [{"claim_id": "c", "text": "A"}, {"claim_id": "c", "text": "B"}],
            [], [],
        )


def test_source_audit_calibration_suppresses_small_samples():
    records = [
        {"audit_id": f"a{i}", "source_id": "s1", "domain": "materials",
         "field": "date", "observed_correct": i < 4}
        for i in range(4)
    ]
    result = summarize_source_audits(records, minimum_sample=5)
    row = result["groups"][0]
    assert row["status"] == "insufficient_sample"
    assert row["observed_agreement_rate"] is None
    assert row["wilson_95_interval"] is None
    assert result["composite_trust_score"] is None


def test_source_audit_calibration_reports_wilson_interval_when_sufficient():
    records = [
        {"audit_id": f"a{i}", "source_id": "s1", "domain": "physics",
         "field": "title", "observed_correct": i < 9}
        for i in range(10)
    ]
    row = summarize_source_audits(records, minimum_sample=5)["groups"][0]
    assert row["observed_agreement_rate"] == 0.9
    assert row["wilson_95_interval"][0] < 0.9 < row["wilson_95_interval"][1]


def test_source_audit_calibration_rejects_non_boolean_outcome():
    with pytest.raises(ValueError):
        summarize_source_audits([{
            "audit_id": "a", "source_id": "s", "domain": "d",
            "field": "f", "observed_correct": 1,
        }])


def test_dataset_shift_detects_numeric_categorical_and_missingness_changes():
    reference = {
        "dataset_id": "base",
        "features": [
            {"name": "mass", "kind": "numeric", "unit": "kg", "count": 100,
             "missing_count": 0, "mean": 10, "stddev": 2},
            {"name": "class", "kind": "categorical", "unit": "", "count": 100,
             "missing_count": 0, "category_counts": {"A": 80, "B": 20}},
            {"name": "removed", "kind": "numeric", "unit": "s", "count": 10,
             "missing_count": 0, "mean": 1, "stddev": 1},
        ],
    }
    candidate = {
        "dataset_id": "new",
        "features": [
            {"name": "mass", "kind": "numeric", "unit": "kg", "count": 100,
             "missing_count": 20, "mean": 12, "stddev": 2},
            {"name": "class", "kind": "categorical", "unit": "", "count": 100,
             "missing_count": 0, "category_counts": {"A": 50, "B": 50}},
            {"name": "temperature", "kind": "numeric", "unit": "K", "count": 10,
             "missing_count": 0, "mean": 300, "stddev": 1},
        ],
    }
    result = compare_dataset_summaries(reference, candidate)
    assert result["added_features"] == ["temperature"]
    assert result["removed_features"] == ["removed"]
    by_name = {row["feature"]: row for row in result["feature_comparisons"]}
    mass, classes = by_name["mass"], by_name["class"]
    assert "numeric_distribution_shift" in mass["flags"]
    assert "missingness_shift" in mass["flags"]
    assert classes["categorical_total_variation_distance"] == pytest.approx(0.3)
    assert result["row_level_data_used"] is False


def test_dataset_shift_flags_unit_changes_and_rejects_bad_counts():
    a = {"features": [{"name": "x", "kind": "numeric", "unit": "m", "count": 2, "missing_count": 0, "mean": 1, "stddev": 1}]}
    b = {"features": [{"name": "x", "kind": "numeric", "unit": "cm", "count": 2, "missing_count": 1, "mean": 1, "stddev": 1}]}
    unit_result = compare_dataset_summaries(a, b)["feature_comparisons"][0]
    assert "unit_mismatch" in unit_result["flags"]
    assert "missingness_shift" in unit_result["flags"]
    bad = {"features": [{"name": "x", "kind": "numeric", "unit": "m", "count": 2, "missing_count": 3, "mean": 1, "stddev": 1}]}
    with pytest.raises(ValueError):
        compare_dataset_summaries(a, bad)


def test_dependency_readiness_computes_critical_path_and_blockers():
    result = analyze_dependencies([
        {"task_id": "a", "duration_hours": 2, "depends_on": []},
        {"task_id": "b", "duration_hours": 3, "depends_on": ["a"]},
        {"task_id": "c", "duration_hours": 1, "depends_on": ["a"], "gate_status": "pending"},
    ])
    assert result["topological_order"] == ["a", "b", "c"]
    assert result["critical_path_task_ids"] == ["a", "b"]
    assert result["critical_path_duration_hours"] == 5
    assert "c" in result["tasks_blocked_from_ready_state"]
    assert result["task_execution_started"] is False


def test_dependency_readiness_reports_missing_and_cycles():
    result = analyze_dependencies([
        {"task_id": "a", "duration_hours": 1, "depends_on": ["b"]},
        {"task_id": "b", "duration_hours": 1, "depends_on": ["a"]},
        {"task_id": "c", "duration_hours": 1, "depends_on": ["missing"]},
    ])
    assert result["cycle_task_ids"] == ["a", "b"]
    assert result["missing_dependency_ids"] == ["missing"]
    assert result["schedule_computable"] is False


def test_pareto_frontier_has_no_composite_score_and_respects_safety_floor():
    result = compare_designs(
        [
            {"candidate_id": "A", "metrics": {"mass": 5, "durability": 8}},
            {"candidate_id": "B", "metrics": {"mass": 6, "durability": 9}},
            {"candidate_id": "C", "metrics": {"mass": 7, "durability": 7}},
            {"candidate_id": "E", "metrics": {"mass": 3, "durability": 6}},
            {"candidate_id": "D", "metrics": {"mass": 4, "durability": 7}},
        ],
        [{"name": "mass", "direction": "minimize"}, {"name": "durability", "direction": "maximize"}],
        safety_floors=[{"metric": "durability", "operator": "min", "value": 7}],
    )
    assert result["pareto_frontier"] == ["A", "B", "D"]
    assert result["dominated_by"]["C"] == ["A", "B", "D"]
    assert "E" in result["ineligible"]
    assert result["weighted_composite_score"] is None
    assert result["safety_certification_granted"] is False


def test_pareto_excludes_missing_metrics_and_identifies_dominance():
    result = compare_designs(
        [
            {"candidate_id": "best", "metrics": {"cost": 1, "strength": 10}},
            {"candidate_id": "weak", "metrics": {"cost": 2, "strength": 8}},
            {"candidate_id": "unknown", "metrics": {"cost": 1}},
        ],
        [{"name": "cost", "direction": "minimize"}, {"name": "strength", "direction": "maximize"}],
    )
    assert result["dominated_by"]["weak"] == ["best"]
    assert result["pareto_frontier"] == ["best"]
    assert result["ineligible"]["unknown"]["missing_metrics"] == ["strength"]


def valid_safety_case():
    return {
        "owner_id": "designer",
        "owner_independence_group": "design-team",
        "nodes": [
            {"node_id": "claim", "node_type": "claim"},
            {"node_id": "argument", "node_type": "argument"},
            {"node_id": "evidence", "node_type": "evidence"},
            {"node_id": "hazard", "node_type": "hazard"},
            {"node_id": "control", "node_type": "control"},
        ],
        "edges": [
            {"source_id": "evidence", "target_id": "argument", "relation": "supports"},
            {"source_id": "argument", "target_id": "claim", "relation": "supports"},
            {"source_id": "control", "target_id": "hazard", "relation": "mitigates"},
        ],
        "top_level_claim_ids": ["claim"],
        "reviewers": [
            {"reviewer_id": "reviewer", "independence_group": "external", "reviewed_node_ids": ["claim", "hazard"]}
        ],
    }


def test_safety_case_reports_traceable_structure_without_approval():
    result = audit_safety_case(**valid_safety_case())
    assert result["status"] == "structured_for_independent_review"
    assert result["safety_case_approved"] is False
    assert result["real_world_use_authorized"] is False


def test_safety_case_flags_unsupported_claims_and_conflicted_reviewer():
    case = valid_safety_case()
    case["edges"] = []
    case["reviewers"][0]["independence_group"] = "design-team"
    result = audit_safety_case(**case)
    assert result["unsupported_top_level_claim_ids"] == ["claim"]
    assert result["unmitigated_hazard_ids"] == ["hazard"]
    assert result["independent_review_gaps"] == ["claim", "hazard"]
    assert result["reviewer_conflicts"]


def test_vtt_local_frame_alignment_recovers_declared_rigid_transform():
    landmarks = [
        {"landmark_id": "p1", "source": [0, 0], "target": [10, 20], "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "p2", "source": [1, 0], "target": [10, 21], "source_uncertainty": 0.01, "target_uncertainty": 0.01},
        {"landmark_id": "p3", "source": [0, 1], "target": [9, 20], "source_uncertainty": 0.01, "target_uncertainty": 0.01},
    ]
    result = fit_local_frame_alignment(
        landmarks, source_frame_id="local-a", target_frame_id="local-b", coordinate_unit="m",
    )
    assert result["all_residuals_within_declared_bounds"] is True
    assert result["transform"]["translation"] == pytest.approx([10, 20])
    assert result["transform"]["rotation_radians"] == pytest.approx(1.57079632679)
    assert result["geographic_crs_conversion_performed"] is False


def test_vtt_local_frame_alignment_rejects_degenerate_landmarks():
    landmarks = [
        {"landmark_id": "p1", "source": [1, 1], "target": [2, 2], "source_uncertainty": 0, "target_uncertainty": 0},
        {"landmark_id": "p2", "source": [1, 1], "target": [3, 3], "source_uncertainty": 0, "target_uncertainty": 0},
    ]
    with pytest.raises(ValueError):
        fit_local_frame_alignment(
            landmarks, source_frame_id="a", target_frame_id="b", coordinate_unit="m",
        )


def test_rescue_route_accessibility_screens_segments_and_unknowns():
    criteria = {
        "minimum_clear_width_m": 1.2, "maximum_slope_percent": 8,
        "allowed_surfaces": ["paved", "firm-gravel"], "maximum_obstructions": 0,
    }
    segments = [
        {"segment_id": "s1", "from_node": "A", "to_node": "B", "clear_width_m": 1.5,
         "slope_percent": 4, "surface": "paved", "obstruction_count": 0},
        {"segment_id": "s2", "from_node": "B", "to_node": "C", "clear_width_m": 1.3,
         "slope_percent": 7, "surface": "firm-gravel", "obstruction_count": 0},
    ]
    result = review_route_accessibility(segments, **criteria)
    assert result["status"] == "within_declared_screening_limits"
    assert result["operational_accessibility_certified"] is False
    segments[1]["clear_width_m"] = None
    assert review_route_accessibility(segments, **criteria)["status"] == "incomplete_measurements"


def test_rescue_route_accessibility_reports_failures_and_disconnection():
    result = review_route_accessibility(
        [{"segment_id": "s1", "from_node": "A", "to_node": "B",
          "clear_width_m": 0.5, "slope_percent": 12, "surface": "mud",
          "obstruction_count": 2},
         {"segment_id": "s2", "from_node": "X", "to_node": "Y",
          "clear_width_m": 1.5, "slope_percent": 2, "surface": "paved",
          "obstruction_count": 0}],
        minimum_clear_width_m=1.2, maximum_slope_percent=8,
        allowed_surfaces=["paved"], maximum_obstructions=0,
    )
    assert result["status"] == "route_disconnected"
    assert "clear_width_below_declared_minimum" in result["segments"][0]["criteria_failures"]
    assert len(result["continuity_gaps"]) == 1



def test_dataset_shift_rejects_fractional_row_counts():
    bad = {"features": [{
        "name": "x", "kind": "numeric", "unit": "m",
        "count": 2.5, "missing_count": 0, "mean": 1, "stddev": 1,
    }]}
    with pytest.raises(ValueError):
        compare_dataset_summaries(bad, bad)


def test_dependency_cycle_diagnostics_exclude_downstream_nodes_from_cycle():
    result = analyze_dependencies([
        {"task_id": "a", "duration_hours": 1, "depends_on": ["b"]},
        {"task_id": "b", "duration_hours": 1, "depends_on": ["a"]},
        {"task_id": "c", "duration_hours": 1, "depends_on": ["b"]},
    ])
    assert result["cycle_task_ids"] == ["a", "b"]
    assert result["cycle_affected_task_ids"] == ["a", "b", "c"]


def test_safety_case_rebuttal_prevents_clean_review_status():
    case = valid_safety_case()
    case["edges"].append({"source_id": "evidence", "target_id": "claim", "relation": "rebuts"})
    result = audit_safety_case(**case)
    assert result["claims_with_rebuttals"] == ["claim"]
    assert result["status"] == "review_gaps_found"


def test_rescue_route_rejects_duplicate_segment_ids():
    segment = {
        "segment_id": "same", "from_node": "A", "to_node": "B",
        "clear_width_m": 1.5, "slope_percent": 2, "surface": "paved",
        "obstruction_count": 0,
    }
    with pytest.raises(ValueError):
        review_route_accessibility(
            [segment, {**segment, "from_node": "B", "to_node": "C"}],
            minimum_clear_width_m=1.2, maximum_slope_percent=8,
            allowed_surfaces=["paved"],
        )



def test_vtt_local_frame_alignment_rejects_overflowing_geometry():
    landmarks = [
        {"landmark_id": "p1", "source": [1e308, 0], "target": [0, 0], "source_uncertainty": 0, "target_uncertainty": 0},
        {"landmark_id": "p2", "source": [-1e308, 0], "target": [1, 0], "source_uncertainty": 0, "target_uncertainty": 0},
    ]
    with pytest.raises(ValueError):
        fit_local_frame_alignment(
            landmarks, source_frame_id="a", target_frame_id="b", coordinate_unit="m",
        )
