"""Aggregate validation findings without converting them into truth claims."""
from __future__ import annotations


def summarize(checks: list[dict]) -> dict:
    total = len(checks)
    passed = sum(1 for check in checks if check.get("passed") is True)
    failed = total - passed
    return {"total_checks": total, "passed": passed, "failed": failed, "pass_ratio": passed / total if total else 1.0, "scientific_truth_established": False}
