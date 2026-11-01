"""Read-only descriptive summaries of recorded numeric laboratory outputs.

This module does not perform inferential tests, causal analysis, or scientific
validation. Potential outliers are flagged for review and never removed.
"""
from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean, median, stdev
from typing import Any


def _quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


class LabStatisticalSummarizer:
    """Summarize recorded numeric outputs by protocol version and output key."""

    def __init__(self, store):
        self.store = store

    def build(self, limit: int = 200) -> dict[str, Any]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")

        runs = self.store.lab_run_history(limit=limit)
        groups: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
        ignored = 0
        for run in runs:
            outputs = run.get("outputs")
            if not isinstance(outputs, dict):
                ignored += 1
                continue
            protocol_id = run.get("protocol_id")
            version = run.get("protocol_version")
            if not isinstance(protocol_id, str) or not protocol_id.strip():
                ignored += 1
                continue
            if isinstance(version, bool) or not isinstance(version, int) or version < 1:
                ignored += 1
                continue
            for name, value in outputs.items():
                if not isinstance(name, str) or not name.strip():
                    ignored += 1
                    continue
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    ignored += 1
                    continue
                number = float(value)
                if not math.isfinite(number):
                    ignored += 1
                    continue
                groups[(protocol_id, version, name)].append({
                    "value": number,
                    "run_id": run.get("run_id"),
                    "campaign_id": run.get("campaign_id"),
                    "kind": run.get("kind"),
                    "provenance_group": run.get("provenance_group"),
                    "independence_declared": run.get("independence_declared") is True,
                })

        summaries = []
        for (protocol_id, version, output_name), records in sorted(groups.items()):
            values = [record["value"] for record in records]
            count = len(values)
            q1 = _quantile(values, 0.25)
            q3 = _quantile(values, 0.75)
            iqr = q3 - q1
            outlier_candidates = []
            if count >= 4:
                lower_fence = q1 - 1.5 * iqr
                upper_fence = q3 + 1.5 * iqr
                outlier_candidates = [
                    {
                        "run_id": record["run_id"],
                        "value": record["value"],
                        "reason": "outside_1_5_iqr_fence",
                    }
                    for record in records
                    if record["value"] < lower_fence or record["value"] > upper_fence
                ]

            summaries.append({
                "protocol_id": protocol_id,
                "protocol_version": version,
                "output_name": output_name,
                "sample_size": count,
                "mean": mean(values),
                "median": median(values),
                "minimum": min(values),
                "maximum": max(values),
                "range": max(values) - min(values),
                "sample_standard_deviation": stdev(values) if count >= 2 else None,
                "q1": q1,
                "q3": q3,
                "interquartile_range": iqr,
                "outlier_candidates": outlier_candidates,
                "run_ids": [record["run_id"] for record in records if record["run_id"]][:20],
                "distinct_campaign_count": len({
                    record["campaign_id"] for record in records
                    if isinstance(record["campaign_id"], str) and record["campaign_id"]
                }),
                "declared_independent_run_count": sum(
                    record["independence_declared"] for record in records
                ),
                "provenance_groups": sorted({
                    record["provenance_group"] for record in records
                    if isinstance(record["provenance_group"], str) and record["provenance_group"]
                }),
                "classification": "descriptive_only" if count >= 2 else "single_observation",
                "inferential_test_performed": False,
                "causal_effect_established": False,
                "scientific_validity_established": False,
                "interpretation": (
                    "Descriptive summary of recorded numeric values only. "
                    "Potential outliers are review flags, not errors or exclusions."
                    if count >= 2 else
                    "One numeric observation is recorded; dispersion cannot be estimated."
                ),
            })

        return {
            "summaries": summaries,
            "summary_count": len(summaries),
            "runs_examined": len(runs),
            "non_numeric_or_invalid_values_ignored": ignored,
            "read_only": True,
            "automatic_data_exclusion": False,
            "inferential_tests_performed": False,
            "causal_effects_established": False,
            "scientific_validity_established": False,
            "disclaimer": (
                "Descriptive statistics do not establish causality, statistical significance, "
                "measurement validity, independent replication, or scientific truth. "
                "Interpretation requires protocol, units, measurement uncertainty and qualified review."
            ),
        }
