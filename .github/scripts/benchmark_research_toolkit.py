"""Repeatable synthetic probes for the bounded research toolkit.

Numbers are runner-specific diagnostics, not field performance guarantees.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))

from ssswet_core.dataset_drift import compare_dataset_summaries
from ssswet_core.memory_retrieval import benchmark_retrieval
from ssswet_core.spatiotemporal_mapping import SpatialObservation, segment_track

def main() -> None:
    records = [
        {"memory_id": f"memory-{index:04d}", "topic": f"research domain {index % 12}",
         "statement": f"synthetic thermal materials observation {index}",
         "source_ids": [f"source-{index:04d}"], "status": "candidate"}
        for index in range(500)
    ]
    retrieval = benchmark_retrieval(records, ["thermal materials", "observation 250", "research domain 4"], repeats=5, limit=20)
    if not retrieval["stable_rankings"] or retrieval["p95_latency_ms"] > 2000:
        raise SystemExit("bounded memory retrieval benchmark failed its determinism/2s CI guard")
    baseline = {"features": {f"feature-{index:03d}": {"kind": "numeric", "count": 1000, "mean": float(index), "stddev": 2.0} for index in range(100)}}
    current = {"features": {f"feature-{index:03d}": {"kind": "numeric", "count": 1100, "mean": float(index) + 0.1, "stddev": 2.1} for index in range(100)}}
    started = perf_counter()
    drift = compare_dataset_summaries(baseline, current)
    drift_ms = (perf_counter() - started) * 1000
    observations = [
        SpatialObservation(f"gps-{index:04d}", 48.0 + index * 0.00001, 2.0 + index * 0.00001,
                           f"2026-11-07T10:{index // 60:02d}:{index % 60:02d}+00:00", 8.0, f"source:gps-{index:04d}")
        for index in range(1500)
    ]
    started = perf_counter()
    track = segment_track(observations)
    track_ms = (perf_counter() - started) * 1000
    if track["accepted_count"] != 1500:
        raise SystemExit("spatiotemporal segmentation lost synthetic observations")
    print(json.dumps({
        "benchmark": "SSSWET research toolkit synthetic probe",
        "retrieval_500_records": retrieval,
        "dataset_drift_100_features_ms": round(drift_ms, 4),
        "dataset_drift_flags": drift["features_flagged_for_review"],
        "spatiotemporal_1500_observations_ms": round(track_ms, 4),
        "spatiotemporal_segments": track["segment_count"],
        "runner_specific": True, "field_performance_guarantee": False,
    }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
