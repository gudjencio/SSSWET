"""Synthetic performance probes for the ten engineering-assurance features.

Run from the repository root. Results are diagnostics, not field guarantees.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.sensor_clock_alignment import align_observations, fit_clock_map  # noqa: E402
from ssswet_core.uncertainty_budget import propagate_linear  # noqa: E402
from ssswet_core.calibration_registry import audit_registry  # noqa: E402
from ssswet_core.reliability_survival import kaplan_meier  # noqa: E402
from ssswet_core.measurement_repeatability import analyze_repeatability  # noqa: E402
from ssswet_core.failure_mode_review import assess_failure_modes  # noqa: E402
from ssswet_core.robust_pareto import analyze_frontier  # noqa: E402
from ssswet_core.requirements_traceability import build_traceability_matrix  # noqa: E402
from ssswet_core.lifecycle_inventory import aggregate_inventory  # noqa: E402
from ssswet_core.reproducible_bundle import build_bundle, verify_bundle  # noqa: E402


def measure(function, repeats: int = 3) -> dict:
    samples = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter_ns()
        result = function()
        samples.append((time.perf_counter_ns() - started) / 1_000_000)
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]
    return {"median_ms": round(statistics.median(samples), 4), "p95_ms": round(p95, 4), "samples": repeats, "result": result}


def main() -> None:
    anchors = [
        {"source_id": f"anchor-{i}", "sensor_seconds": float(i * 60), "reference_seconds": 12.0 + i * 60.0006, "uncertainty_seconds": 0.002}
        for i in range(200)
    ]
    clock = fit_clock_map(anchors)
    observations = [{"source_id": f"gps-{i}", "sensor_seconds": float(i * 1.19), "uncertainty_seconds": 0.01} for i in range(10_000)]
    clock_probe = measure(lambda: align_observations(observations, clock))
    assert clock_probe["result"]["aligned_count"] > 0

    components = [{"name": f"input-{i}", "sensitivity": 1.0 + i / 100, "standard_uncertainty": 0.01} for i in range(30)]
    uncertainty_probe = measure(lambda: propagate_linear(components))
    assert uncertainty_probe["result"]["component_count"] == 30

    calibration_records = [{
        "instrument_id": f"instrument-{i}", "calibration_id": f"calibration-{i}",
        "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z",
        "certificate_sha256": f"{i:064x}", "calibration_provider": "Synthetic Lab",
        "traceability_refs": ["standard:synthetic"], "expanded_uncertainty": 0.02,
        "uncertainty_unit": "mm", "review_state": "reviewed",
    } for i in range(500)]
    calibration_probe = measure(lambda: audit_registry(calibration_records, at="2026-11-08T00:00:00Z"))
    assert calibration_probe["result"]["metadata_complete_count"] == 500

    survival_rows = [{"observation_id": f"unit-{i}", "duration": float(i + 1), "event_observed": i % 5 != 0} for i in range(10_000)]
    survival_probe = measure(lambda: kaplan_meier(survival_rows))
    assert survival_probe["result"]["observation_count"] == 10_000

    repeatability_groups = [{"group_id": f"operator-{i}", "values": [float(i) + j / 10 for j in range(10)]} for i in range(100)]
    repeatability_probe = measure(lambda: analyze_repeatability(repeatability_groups))
    assert repeatability_probe["result"]["group_count"] == 100

    failure_modes = [{
        "mode_id": f"mode-{i}", "subsystem": "synthetic", "failure_mode": "declared test mode",
        "effect": "review only", "cause": "synthetic input", "severity": 2,
        "occurrence": 2, "detectability": 2, "controls": ["test control"],
        "evidence_refs": [f"evidence-{i}"],
    } for i in range(500)]
    failure_probe = measure(lambda: assess_failure_modes(failure_modes))
    assert failure_probe["result"]["mode_count"] == 500

    objective_names = [f"metric-{i}" for i in range(8)]
    alternatives = [{
        "alternative_id": f"alternative-{i}",
        "metrics": {name: {"value": float((i * (j + 3)) % 101), "uncertainty": 0.1} for j, name in enumerate(objective_names)},
    } for i in range(200)]
    objectives = [{"name": name, "direction": "minimize" if index % 2 == 0 else "maximize"} for index, name in enumerate(objective_names)]
    pareto_probe = measure(lambda: analyze_frontier(alternatives, objectives))
    assert pareto_probe["result"]["alternative_count"] == 200

    evidence = [{"evidence_id": f"evidence-{i}", "result": "pass", "reviewer": "reviewer", "provenance_ref": f"run:{i}"} for i in range(1000)]
    requirements = [{"requirement_id": f"requirement-{i}", "description": "Synthetic requirement", "verification_method": "test", "evidence_refs": [f"evidence-{i}"]} for i in range(1000)]
    traceability_probe = measure(lambda: build_traceability_matrix(requirements, evidence))
    assert traceability_probe["result"]["reviewed_pass_count"] == 1000

    flows = [{
        "flow_id": f"flow-{i}", "phase": f"phase-{i % 5}", "quantity": 1.0 + i / 100,
        "quantity_unit": "kg", "factor_basis_unit": "kg", "factor_value": 2.0,
        "quantity_uncertainty": 0.01, "factor_uncertainty": 0.02,
        "impact_unit": "kgCO2e", "factor_source_id": f"factor-db-{i % 10}", "factor_version": "synthetic-v1",
    } for i in range(5000)]
    lifecycle_probe = measure(lambda: aggregate_inventory(flows))
    assert lifecycle_probe["result"]["flow_count"] == 5000

    bundle_files = {f"data/part-{i:02d}.json": json.dumps({"index": i, "payload": "x" * 50_000}) for i in range(20)}
    def bundle_roundtrip() -> dict:
        archive = build_bundle(bundle_files)
        verification = verify_bundle(archive)
        if not verification["valid"]:
            raise SystemExit("deterministic bundle verification failed")
        return {"archive_bytes": len(archive), "files": verification["file_count"], "total_size_bytes": verification["total_size_bytes"]}
    bundle_probe = measure(bundle_roundtrip)

    probes = {
        "clock_alignment_10000_observations": clock_probe,
        "covariance_uncertainty_30_components": uncertainty_probe,
        "calibration_registry_500_records": calibration_probe,
        "kaplan_meier_10000_observations": survival_probe,
        "repeatability_100_groups": repeatability_probe,
        "failure_mode_review_500_modes": failure_probe,
        "pareto_200_alternatives_8_objectives": pareto_probe,
        "requirements_traceability_1000_requirements": traceability_probe,
        "lifecycle_inventory_5000_flows": lifecycle_probe,
        "reproducible_bundle_1mb_input": bundle_probe,
    }
    for probe in probes.values():
        probe.pop("result", None)
    print(json.dumps({
        "benchmark": "SSSWET engineering assurance synthetic workloads",
        "probes": probes,
        "p95_ci_guard_ms": 5000,
        "runner_specific": True,
        "field_performance_guarantee": False,
        "scientific_validity_or_agent_intelligence_established": False,
    }, sort_keys=True))
    if any(item["p95_ms"] > 5000 for item in probes.values()):
        raise SystemExit("engineering assurance benchmark exceeded the broad 5s CI guard")


if __name__ == "__main__":
    main()
