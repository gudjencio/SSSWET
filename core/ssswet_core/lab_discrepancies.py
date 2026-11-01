"""Read-only screening of recorded digital-lab comparison outcomes.

A divergence is a review lead, not proof that either result is wrong.
Incompatible conditions are kept separate from comparable result divergence.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any


class LabDiscrepancyAnalyzer:
    """Classify explicit comparison records without changing research state."""

    def __init__(self, store: Any):
        self.store = store

    def build(self, limit: int = 200) -> dict:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")

        runs = {
            item["run_id"]: item
            for item in self.store.lab_run_history(limit=limit * 2)
            if item.get("run_id")
        }
        findings = []
        for comparison in self.store.lab_comparison_history(limit=limit):
            left_id = comparison.get("left_run_id") or comparison.get("reference_run_id")
            right_id = comparison.get("right_run_id") or comparison.get("candidate_run_id")
            left, right = runs.get(left_id), runs.get(right_id)
            comparable = comparison.get("comparable")
            matches = comparison.get("outputs_match_within_tolerance")

            if comparable is False:
                classification = "incompatible_conditions"
                reason = "The recorded comparison says the runs are not comparable."
            elif comparable is True and matches is False:
                classification = "recorded_result_divergence"
                reason = "Comparable recorded runs differ beyond the comparison tolerance."
            elif comparable is not True or not isinstance(matches, bool):
                classification = "incomplete_comparison_data"
                reason = "The comparison lacks explicit, complete comparability or output-match fields."
            else:
                continue

            identity = "|".join((str(comparison.get("comparison_id", "")), classification))
            finding_id = "lab-review:" + sha256(identity.encode("utf-8")).hexdigest()[:24]
            findings.append({
                "finding_id": finding_id,
                "classification": classification,
                "comparison_id": comparison.get("comparison_id", ""),
                "left_run_id": left_id or "",
                "right_run_id": right_id or "",
                "protocol_id": (left or right or {}).get("protocol_id", ""),
                "protocol_version": (left or right or {}).get("protocol_version"),
                "left_campaign_id": (left or {}).get("campaign_id", ""),
                "right_campaign_id": (right or {}).get("campaign_id", ""),
                "left_execution_kind": (left or {}).get("kind", ""),
                "right_execution_kind": (right or {}).get("kind", ""),
                "shared_dataset_ids": comparison.get("shared_dataset_ids", []),
                "shared_source_ids": comparison.get("shared_source_ids", []),
                "tolerance": comparison.get("tolerance"),
                "differences": comparison.get("differences", []),
                "reason": reason,
                "requires_human_review": True,
                "scientific_contradiction_established": False,
                "scientific_validity_established": False,
            })

        findings.sort(key=lambda item: (item["classification"], item["finding_id"]))
        counts = {
            key: sum(item["classification"] == key for item in findings)
            for key in (
                "recorded_result_divergence",
                "incompatible_conditions",
                "incomplete_comparison_data",
            )
        }
        return {
            "findings": findings,
            "count": len(findings),
            "counts": counts,
            "read_only": True,
            "automatic_case_creation": False,
            "scientific_contradiction_established": False,
            "scientific_validity_established": False,
            "interpretation": (
                "These are screening results derived only from explicit recorded comparisons. "
                "They do not determine which result is correct or establish a scientific contradiction."
            ),
        }
