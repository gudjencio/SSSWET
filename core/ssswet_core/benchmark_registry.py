"""Repeatable capability benchmarks with explicit baselines and no intelligence claims."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class BenchmarkResult:
    benchmark_id: str
    value: float
    unit: str
    sample_count: int

class BenchmarkRegistry:
    def __init__(self) -> None:
        self._results: dict[str, list[BenchmarkResult]] = {}

    def record(self, result: BenchmarkResult) -> None:
        if not result.benchmark_id.strip() or result.sample_count < 1:
            raise ValueError("benchmark_id and positive sample_count are required")
        self._results.setdefault(result.benchmark_id, []).append(result)

    def compare(self, benchmark_id: str, baseline: float) -> dict:
        if benchmark_id not in self._results:
            return {"benchmark_id": benchmark_id, "available": False, "improvement": None, "claim_of_intelligence": False}
        latest = self._results[benchmark_id][-1]
        delta = latest.value - baseline
        relative = None if baseline == 0 else delta / abs(baseline)
        return {"benchmark_id": benchmark_id, "available": True, "latest": latest.value, "baseline": baseline, "delta": delta, "relative_change": relative, "sample_count": latest.sample_count, "repeatable_measurement_required": True, "claim_of_intelligence": False}
