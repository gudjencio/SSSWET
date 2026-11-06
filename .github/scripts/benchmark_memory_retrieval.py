"""Repeatable synthetic latency probe for bounded scientific-memory retrieval.

Run from the repository root: python .github/scripts/benchmark_memory_retrieval.py
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.memory_intelligence import benchmark_memory_retrieval  # noqa: E402


def main() -> None:
    records = [
        {
            "version_id": f"benchmark-v{index:04d}",
            "memory_key": f"benchmark-key-{index:04d}",
            "version_number": 1,
            "is_current": True,
            "topic": f"{('materials', 'thermal', 'acoustic', 'mapping', 'rescue')[index % 5]} research topic {index % 37}",
            "statement": (
                f"Evaluate measurement methods, uncertainty and reproducibility "
                f"for research sample {index} in category {index % 23}"
            ),
            "campaign_id": f"campaign-{index % 11}",
            "created_at": f"2026-01-{index % 28 + 1:02d}T00:00:00+00:00",
        }
        for index in range(500)
    ]
    report = benchmark_memory_retrieval(
        records,
        [
            "materials measurement uncertainty",
            "thermal reproducibility",
            "acoustic research methods",
            "mapping sample uncertainty",
            "rescue measurement methods",
        ],
        repeats=5,
        limit=20,
    )
    report["python_version"] = platform.python_version()
    report["platform"] = platform.platform()
    report["dataset"] = "500 deterministic synthetic records"
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
