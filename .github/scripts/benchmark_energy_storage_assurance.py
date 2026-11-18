"""Synthetic performance regression probes for field energy assurance.

Run from the repository root. These workloads are not battery tests or safety
evaluations and do not establish scientific validity.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.energy_storage_assurance import (  # noqa: E402
    build_evidence_packet,
    capacity_fade,
    cell_imbalance,
    compare_protocols,
    detect_signal_anomalies,
    integrate_capacity,
    round_trip_efficiency,
    segment_cycles,
    temperature_excursions,
    validate_energy_samples,
)


def measure(function, repeats=5):
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        function()
        samples.append((time.perf_counter() - started) * 1000.0)
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(p95, 3),
        "samples": repeats,
    }


def make_samples(cycles=100):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for cycle in range(cycles):
        for index in range(20):
            global_index = cycle * 20 + index
            mode = "charge" if index < 10 else "discharge"
            current = 1.5 if mode == "charge" else 1.0
            temperature = 45.0 if global_index == 550 else 25.0
            if global_index == 777:
                current = 9.0
            cells = [4.10, 4.09, 4.11]
            if global_index == 888:
                cells = [4.10, 3.80, 4.11]
            rows.append({
                "sample_id": f"sample-{cycle}-{index}",
                "session_id": "synthetic-session",
                "cycle_id": f"cycle-{cycle}",
                "source_id": "synthetic-sensor",
                "timestamp_utc": (base + timedelta(seconds=global_index * 60)).isoformat(),
                "mode": mode,
                "current_a": current,
                "voltage_v": 12.4,
                "temperature_c": temperature,
                "cell_voltages_v": cells,
                "calibration_refs": ["synthetic-calibration"],
            })
    return rows


def main():
    rows = make_samples()
    protocol_a = {"schema": 1, "sample_rate_hz": 1, "limits": {"low": -20, "high": 40}}
    protocol_b = {"schema": 1, "sample_rate_hz": 2, "limits": {"low": -20, "high": 38}}
    fade = [{"cycle_number": n, "capacity_ah": 2.0 - n * 0.001} for n in range(1, 101)]

    workloads = {
        "validated_ingestion": lambda: validate_energy_samples(rows),
        "cycle_segmentation": lambda: segment_cycles(rows),
        "capacity_integration": lambda: integrate_capacity(
            rows, "cycle-0", "discharge", "synthetic-session", 120
        ),
        "energy_and_round_trip": lambda: round_trip_efficiency(
            rows, "cycle-0", "synthetic-session", 120
        ),
        "capacity_fade": lambda: capacity_fade(fade),
        "temperature_excursions": lambda: temperature_excursions(rows, -20, 40, 120),
        "cell_imbalance": lambda: cell_imbalance(rows, 0.05),
        "signal_anomaly_screen": lambda: detect_signal_anomalies(rows),
        "protocol_revision_diff": lambda: compare_protocols(protocol_a, protocol_b),
        "evidence_packet": lambda: build_evidence_packet(
            rows, protocol_a, {"synthetic_rows": len(rows)}, ["synthetic-calibration"]
        ),
    }
    results = {name: measure(function) for name, function in workloads.items()}
    for name, result in results.items():
        if result["p95_ms"] >= 2000:
            raise SystemExit(f"{name} exceeded the 2000 ms p95 regression ceiling")
    packet = build_evidence_packet(rows, protocol_a, {"synthetic_rows": len(rows)}, ["synthetic-calibration"])
    print(json.dumps({
        "sample_count": len(rows),
        "workloads": results,
        "evidence_packet_bytes": len(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        "p95_ceiling_ms": 2000,
        "synthetic_benchmark_only": True,
        "battery_safety_or_scientific_validity_established": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
