"""Bounded performance probes for the research workflow utilities.

Run from the repository root: python .github/scripts/benchmark_research_quality.py
Synthetic workloads are regression probes, not scientific or intelligence evaluations.
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

from ssswet_core.localization_quality import audit_translation_catalogue  # noqa: E402
from ssswet_core.provenance_graph import build as build_graph  # noqa: E402
from ssswet_core.virtual_time_mapping import TemporalObservation, VirtualTimeMap  # noqa: E402


def measure(function, repeats: int = 5) -> dict:
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        function()
        samples.append((time.perf_counter() - started) * 1000)
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]
    return {"median_ms": round(statistics.median(samples), 3), "p95_ms": round(p95, 3), "samples": repeats}


def main() -> None:
    nodes = [{"id": f"n{index:04d}"} for index in range(1200)]
    edges = [(f"n{index:04d}", f"n{index + 1:04d}") for index in range(1199)]
    graph = measure(lambda: build_graph(nodes, edges))
    assert graph["p95_ms"] < 2000

    mapping = VirtualTimeMap()
    for index in range(1500):
        mapping.add(TemporalObservation(
            f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z",
            f"observation-{index}", f"source-{index}", 2.0,
        ))
    temporal = measure(mapping.temporal_clusters)
    assert temporal["p95_ms"] < 2000

    source = {f"key-{index:03d}": f"Research label {index} {{value}}" for index in range(300)}
    translations = {
        language: {key: f"{language.upper()} label {index} {{value}}" for index, key in enumerate(source)}
        for language in ("en", "fr", "es", "pt", "it", "de", "nl", "ja", "ko", "zh", "gcf", "ku", "da", "sv", "jv")
    }
    translations["en"] = source
    locale = measure(lambda: audit_translation_catalogue(source, translations))
    assert locale["p95_ms"] < 2000

    print(json.dumps({
        "workloads": {
            "provenance_graph": {"nodes": len(nodes), "edges": len(edges), **graph},
            "temporal_mapping": {"observations": 1500, **temporal},
            "localization_audit": {"source_keys": len(source), "locales": len(translations), **locale},
        },
        "acceptance_threshold_ms_p95": 2000,
        "synthetic_benchmark_only": True,
        "scientific_validity_or_agent_intelligence_established": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
