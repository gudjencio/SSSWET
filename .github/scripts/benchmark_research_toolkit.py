"""Repeatable synthetic probes for the bounded research toolkit.

Numbers are runner-specific diagnostics, not field performance guarantees.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from time import perf_counter_ns

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))

from ssswet_core.dataset_drift import compare_dataset_summaries
from ssswet_core.memory_revision_diff import compare_memory_revisions
from ssswet_core.spatiotemporal_mapping import SpatialObservation, segment_track

def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(0.95 * len(ordered) + 0.999999) - 1))
    return ordered[index]

def main() -> None:
    previous_records = [
        {"memory_id": f"memory-{index:04d}", "memory_key": f"domain-{index % 12}",
         "statement": f"synthetic research statement {index}", "source_ids": [f"source-{index:04d}"],
         "status": "candidate"}
        for index in range(500)
    ]
    current_records = [
        {**record, "statement": record["statement"] + " revised", "source_ids": record["source_ids"] + ["source-review"]}
        if index % 20 == 0 else dict(record)
        for index, record in enumerate(previous_records)
    ]
    previous = {"snapshot_id": "benchmark-before", "records": previous_records}
    current = {"snapshot_id": "benchmark-after", "records": current_records}
    diff_durations, first_diff = [], None
    for _ in range(5):
        started = perf_counter_ns()
        result = compare_memory_revisions(previous, current)
        diff_durations.append((perf_counter_ns() - started) / 1_000_000)
        if first_diff is None:
            first_diff = result
        elif result != first_diff:
            raise SystemExit("memory revision diff is not deterministic")
    if first_diff["changed_count"] != 25 or first_diff["records_or_review_states_modified"]:
        raise SystemExit("bounded memory revision diff failed its synthetic integrity probe")
    diff_median = sorted(diff_durations)[len(diff_durations) // 2]
    diff_p95 = _p95(diff_durations)
    if diff_p95 > 2000:
        raise SystemExit("bounded memory revision diff exceeded its 2s CI guard")

    baseline = {"features": {f"feature-{index:03d}": {"kind": "numeric", "count": 1000, "mean": float(index), "stddev": 2.0} for index in range(100)}}
    current_summary = {"features": {f"feature-{index:03d}": {"kind": "numeric", "count": 1100, "mean": float(index) + 0.1, "stddev": 2.1} for index in range(100)}}
    started = perf_counter_ns()
    drift = compare_dataset_summaries(baseline, current_summary)
    drift_ms = (perf_counter_ns() - started) / 1_000_000

    observations = [
        SpatialObservation(f"gps-{index:04d}", 48.0 + index * 0.00001, 2.0 + index * 0.00001,
                           f"2026-11-07T10:{index // 60:02d}:{index % 60:02d}+00:00", 8.0, f"source:gps-{index:04d}")
        for index in range(1500)
    ]
    started = perf_counter_ns()
    track = segment_track(observations)
    track_ms = (perf_counter_ns() - started) / 1_000_000
    if track["accepted_count"] != 1500:
        raise SystemExit("spatiotemporal segmentation lost synthetic observations")
    print(json.dumps({
        "benchmark": "SSSWET research toolkit synthetic probe",
        "memory_revision_diff_500_records": {
            "median_latency_ms": round(diff_median, 4),
            "p95_latency_ms": round(diff_p95, 4),
            "changed_records": first_diff["changed_count"],
            "deterministic": True,
        },
        "dataset_drift_100_features_ms": round(drift_ms, 4),
        "dataset_drift_flags": drift["features_flagged_for_review"],
        "spatiotemporal_1500_observations_ms": round(track_ms, 4),
        "spatiotemporal_segments": track["segment_count"],
        "runner_specific": True, "field_performance_guarantee": False,
    }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
