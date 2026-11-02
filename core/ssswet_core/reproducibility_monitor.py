"""Reproducibility metadata checks for recorded research runs.

This monitor checks completeness and consistency of supplied run records. It
does not execute experiments, reproduce results, or certify scientific validity.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


class ResearchReproducibilityMonitor:
    """Flag metadata gaps and comparable-run differences for human follow-up."""

    REQUIRED_FIELDS = ("run_id", "protocol_id", "protocol_version", "dataset_id",
                       "dataset_version", "parameters", "environment", "result_fingerprint")

    def analyze(self, runs: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(runs, list):
            raise ValueError("runs must be a list")
        if any(not isinstance(run, dict) for run in runs):
            raise ValueError("each run must be a dictionary")

        findings: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

        for index, run in enumerate(runs):
            run_id = run.get("run_id")
            label = run_id if isinstance(run_id, str) and run_id.strip() else f"record at index {index}"
            missing = []
            for field in self.REQUIRED_FIELDS:
                value = run.get(field)
                if value is None or value == "" or value == [] or value == {}:
                    missing.append(field)
            if missing:
                findings.append({
                    "category": "incomplete_run_metadata",
                    "priority": "high",
                    "run_id": run_id,
                    "title": f"Run metadata incomplete: {label}",
                    "missing_fields": missing,
                    "reason": "The supplied record omits fields needed to compare or independently inspect this run.",
                    "suggested_action": "Complete the run record from its original logs; do not infer missing values.",
                })
            if isinstance(run_id, str) and run_id.strip():
                if run_id in seen_ids:
                    findings.append({
                        "category": "duplicate_run_identifier",
                        "priority": "high",
                        "run_id": run_id,
                        "title": f"Duplicate run identifier: {run_id}",
                        "missing_fields": [],
                        "reason": "More than one supplied record uses the same run identifier.",
                        "suggested_action": "Resolve the identifier collision against the originating run registry.",
                    })
                seen_ids.add(run_id)

            key_fields = ("protocol_id", "protocol_version", "dataset_id",
                          "dataset_version", "parameters", "environment")
            if all(run.get(field) not in (None, "", [], {}) for field in key_fields):
                key = tuple(run[field] if field not in {"parameters", "environment"}
                            else repr(sorted(run[field].items())) if isinstance(run[field], dict)
                            else repr(run[field]) for field in key_fields)
                groups[key].append(run)

        for group in groups.values():
            if len(group) < 2:
                continue
            fingerprints = {
                item.get("result_fingerprint") for item in group
                if isinstance(item.get("result_fingerprint"), str)
                and item.get("result_fingerprint").strip()
            }
            if len(fingerprints) > 1:
                findings.append({
                    "category": "different_outputs_under_matching_recorded_conditions",
                    "priority": "high",
                    "run_ids": [item.get("run_id") for item in group],
                    "title": "Recorded outputs differ under matching recorded conditions",
                    "missing_fields": [],
                    "reason": "Runs share the same recorded protocol, dataset, parameters and environment identifiers but have different result fingerprints. Hidden state, nondeterminism or incomplete metadata may explain the difference.",
                    "suggested_action": "Inspect original logs, random seeds, software versions, hardware details and measurement uncertainty; perform an independently controlled rerun if appropriate.",
                })

        order = {"high": 0, "medium": 1, "low": 2}
        findings.sort(key=lambda item: (order[item["priority"]], item["category"],
                                        str(item.get("run_id", item.get("run_ids", "")))))
        return {
            "findings": findings,
            "total": len(findings),
            "run_count": len(runs),
            "priority_counts": {level: sum(item["priority"] == level for item in findings)
                                for level in ("high", "medium", "low")},
            "reproducibility_established": False,
            "experiments_executed": False,
            "notice": (
                "This report checks only the supplied metadata. Matching records do not prove "
                "that conditions were truly identical, and matching fingerprints do not establish "
                "independent reproducibility or scientific validity."
            ),
        }
