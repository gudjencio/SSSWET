#!/usr/bin/env python3
"""Repeatable bounded-workload latency guard for the research workbench."""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

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

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
BUDGET_SECONDS = 5.0
REPEATS = 3


def workload_hypothesis():
    spec = {
        "research_question": "Does intervention A change outcome B?",
        "system_scope": "A bounded laboratory system",
        "comparator": "Matched baseline",
        "time_horizon": "24 hours",
        "measurement_context": "Calibrated instrument",
        "independent_variables": [{"name": "dose", "unit": "mg/L", "operational_definition": "Measured concentration"}],
        "outcomes": [{"name": "response", "unit": "mmol/L", "measurement_method": "Validated assay"}],
        "falsification_conditions": ["No change beyond the predeclared margin"],
        "alternative_explanations": ["Instrument drift"],
        "safety_constraints": ["No human or animal subjects"],
    }
    result = None
    for _ in range(100):
        result = assess_hypothesis(spec)
    return {"assessments": 100, "last_status": result["status"]}


def workload_replication():
    registry = ReplicationRegistry()
    for index in range(500):
        registry.record_attempt(
            run_id=f"run-{index:04d}", protocol_fingerprint=DIGEST_A,
            dataset_fingerprints=[DIGEST_B], environment_fingerprint=DIGEST_A,
            analysis_fingerprint=DIGEST_B, outcome="inconclusive",
        )
    comparison = registry.compare("run-0000", "run-0499")
    export_250 = json.dumps(registry.export(limit=250), sort_keys=True, separators=(",", ":")).encode("utf-8")
    export_500 = json.dumps(registry.export(limit=500), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "records": 500, "protocol_match": comparison["protocol_match"],
        "serialized_bytes_250": len(export_250), "serialized_bytes_500": len(export_500),
        "serialized_bytes_per_record_at_500": round(len(export_500) / 500, 2),
        "storage_measurement": "canonical_json_export_bytes_not_heap_or_database_size",
    }


def workload_evidence_coverage():
    claims = [{"claim_id": f"c-{i}", "text": f"Claim {i}"} for i in range(500)]
    evidence = [{
        "evidence_id": f"e-{i}", "source_id": f"s-{i}",
        "provenance_group": f"group-{i}",
    } for i in range(1000)]
    links = []
    for i in range(500):
        links.append({"claim_id": f"c-{i}", "evidence_id": f"e-{2*i}", "stance": "supports"})
        links.append({"claim_id": f"c-{i}", "evidence_id": f"e-{2*i+1}", "stance": "contradicts"})
    result = audit_claim_coverage(claims, evidence, links)
    return {
        "claims": result["claim_count"],
        "supporting_independent_groups": sum(item["supporting_independent_group_count"] for item in result["claims"]),
        "contradicting_independent_groups": sum(item["contradicting_independent_group_count"] for item in result["claims"]),
        "contested_claims": len(result["contested_claim_ids"]),
        "dangling_links": len(result["dangling_links"]),
    }


def workload_source_audits():
    records = [{
        "audit_id": f"a-{i}", "source_id": f"s-{i // 5}",
        "domain": "materials", "field": "title",
        "observed_correct": i % 7 != 0,
    } for i in range(5000)]
    result = summarize_source_audits(records, minimum_sample=5)
    return {
        "audit_records": result["audit_count"], "source_field_groups": result["group_count"],
        "sufficient_sample_groups": sum(item["wilson_95_interval"] is not None for item in result["groups"]),
    }


def workload_dataset_shift():
    reference_features, candidate_features = [], []
    for i in range(300):
        reference_features.append({
            "name": f"feature-{i:03d}", "kind": "numeric", "unit": "unit",
            "count": 1000, "missing_count": 0, "mean": float(i), "stddev": 2.0,
        })
        candidate_features.append({
            "name": f"feature-{i:03d}", "kind": "numeric", "unit": "unit",
            "count": 1000, "missing_count": 10, "mean": float(i) + 0.5, "stddev": 2.1,
        })
    result = compare_dataset_summaries({"features": reference_features}, {"features": candidate_features})
    return {
        "features": len(result["feature_comparisons"]),
        "flagged_features": sum(bool(item["flags"]) for item in result["feature_comparisons"]),
        "row_level_data_used": result["row_level_data_used"],
    }


def workload_dependency_plan():
    tasks = [{
        "task_id": f"task-{i:04d}", "duration_hours": 1.0,
        "depends_on": [f"task-{i-1:04d}"] if i else [],
    } for i in range(500)]
    result = analyze_dependencies(tasks)
    return {
        "tasks": len(tasks), "critical_path_hours": result["critical_path_duration_hours"],
        "schedule_computable": result["schedule_computable"],
    }


def workload_pareto():
    candidates = [{
        "candidate_id": f"design-{i:03d}",
        "metrics": {f"m{j}": float((i * (j + 3)) % 101) for j in range(5)},
    } for i in range(100)]
    objectives = [
        {"name": f"m{j}", "direction": "minimize" if j % 2 == 0 else "maximize"}
        for j in range(5)
    ]
    result = compare_designs(candidates, objectives)
    return {
        "candidates": len(candidates), "pareto_frontier_size": len(result["pareto_frontier"]),
        "ineligible_candidates": len(result["ineligible"]),
    }


def workload_safety_case():
    nodes, edges, top_claims, reviewed = [], [], [], []
    for i in range(100):
        claim, argument, evidence = f"claim-{i}", f"argument-{i}", f"evidence-{i}"
        hazard, control = f"hazard-{i}", f"control-{i}"
        nodes.extend([
            {"node_id": claim, "node_type": "claim"},
            {"node_id": argument, "node_type": "argument"},
            {"node_id": evidence, "node_type": "evidence"},
            {"node_id": hazard, "node_type": "hazard"},
            {"node_id": control, "node_type": "control"},
        ])
        edges.extend([
            {"source_id": evidence, "target_id": argument, "relation": "supports"},
            {"source_id": argument, "target_id": claim, "relation": "supports"},
            {"source_id": control, "target_id": hazard, "relation": "mitigates"},
        ])
        top_claims.append(claim)
        reviewed.extend([claim, hazard])
    result = audit_safety_case(
        owner_id="owner", owner_independence_group="design-team",
        nodes=nodes, edges=edges, top_level_claim_ids=top_claims,
        reviewers=[{"reviewer_id": "independent-reviewer", "independence_group": "external", "reviewed_node_ids": reviewed}],
    )
    return {"nodes": len(nodes), "edges": len(edges), "review_status": result["status"]}


def workload_vtt_alignment():
    landmarks = []
    for i in range(200):
        x, y = float(i % 20), float(i // 20)
        landmarks.append({
            "landmark_id": f"p-{i:03d}", "source": [x, y],
            "target": [100.0 - y, 200.0 + x],
            "source_uncertainty": 0.01, "target_uncertainty": 0.01,
        })
    result = fit_local_frame_alignment(
        landmarks, source_frame_id="frame-a", target_frame_id="frame-b",
        coordinate_unit="m",
    )
    return {
        "landmarks": result["landmark_count"], "rms_residual": result["rms_residual"],
        "all_residuals_within_declared_bounds": result["all_residuals_within_declared_bounds"],
    }


def workload_rescue_route():
    segments = [{
        "segment_id": f"segment-{i:04d}", "from_node": f"n-{i:04d}",
        "to_node": f"n-{i+1:04d}", "clear_width_m": 1.5,
        "slope_percent": 4.0, "surface": "paved", "obstruction_count": 0,
    } for i in range(500)]
    result = review_route_accessibility(
        segments, minimum_clear_width_m=1.2, maximum_slope_percent=8.0,
        allowed_surfaces=["paved"], maximum_obstructions=0,
    )
    return {"segments": len(segments), "screening_status": result["status"]}


WORKLOADS = [
    ("hypothesis_100_assessments", workload_hypothesis),
    ("replication_500_attempts", workload_replication),
    ("evidence_500_claims_1000_links", workload_evidence_coverage),
    ("source_audits_5000_records", workload_source_audits),
    ("dataset_shift_300_features", workload_dataset_shift),
    ("dependency_plan_500_tasks", workload_dependency_plan),
    ("pareto_100_designs_5_objectives", workload_pareto),
    ("safety_case_500_nodes_300_edges", workload_safety_case),
    ("vtt_alignment_200_landmarks", workload_vtt_alignment),
    ("rescue_route_500_segments", workload_rescue_route),
]


def main():
    results = []
    for name, workload in WORKLOADS:
        durations = []
        measurement = None
        for _ in range(REPEATS):
            started = time.perf_counter()
            measurement = workload()
            durations.append(time.perf_counter() - started)
        median = statistics.median(durations)
        maximum = max(durations)
        results.append({
            "workload": name,
            "repeats": REPEATS,
            "median_ms": round(median * 1000, 3),
            "maximum_ms": round(maximum * 1000, 3),
            "budget_ms": int(BUDGET_SECONDS * 1000),
            "within_budget": maximum <= BUDGET_SECONDS,
            "measurement": measurement,
        })
    print(json.dumps({"benchmark": "SSSWET research workbench bounded workloads", "results": results}, indent=2))
    failed = [item["workload"] for item in results if not item["within_budget"]]
    if failed:
        raise SystemExit("Latency budget exceeded: " + ", ".join(failed))


if __name__ == "__main__":
    main()
