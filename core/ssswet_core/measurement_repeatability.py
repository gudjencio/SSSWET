"""Balanced repeated-measurement variance decomposition for lab QA."""
from __future__ import annotations

from math import isfinite, sqrt

MAX_GROUPS = 100
MAX_REPLICATES = 1_000


def analyze_repeatability(groups: list[dict]) -> dict:
    if not isinstance(groups, list) or not 2 <= len(groups) <= MAX_GROUPS:
        raise ValueError(f"groups must contain 2 to {MAX_GROUPS} groups")
    normalized, replicate_count = [], None
    seen = set()
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("each group must be an object")
        group_id = group.get("group_id")
        values = group.get("values")
        if not isinstance(group_id, str) or not group_id.strip() or group_id in seen:
            raise ValueError("group_id values must be unique non-empty strings")
        seen.add(group_id)
        if not isinstance(values, list) or not 2 <= len(values) <= MAX_REPLICATES:
            raise ValueError(f"each group needs 2 to {MAX_REPLICATES} replicate values")
        if replicate_count is None:
            replicate_count = len(values)
        elif len(values) != replicate_count:
            raise ValueError("balanced repeatability analysis requires equal replicate counts")
        numbers = []
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("replicate values must be finite numbers")
            numbers.append(float(value))
        mean = sum(numbers) / len(numbers)
        normalized.append((group_id, numbers, mean))
    group_count = len(normalized)
    within_ss = sum(sum((value - mean) ** 2 for value in values) for _, values, mean in normalized)
    df_within = group_count * (replicate_count - 1)
    ms_within = within_ss / df_within
    grand_mean = sum(mean for _, _, mean in normalized) / group_count
    between_ss = replicate_count * sum((mean - grand_mean) ** 2 for _, _, mean in normalized)
    df_between = group_count - 1
    ms_between = between_ss / df_between
    variance_within = ms_within
    variance_between = max(0.0, (ms_between - ms_within) / replicate_count)
    total_variance = variance_within + variance_between
    return {
        "method": "balanced_one_way_random_effects_moment_estimate",
        "group_count": group_count,
        "replicates_per_group": replicate_count,
        "grand_mean": grand_mean,
        "repeatability_standard_deviation": sqrt(variance_within),
        "between_group_standard_deviation": sqrt(variance_between),
        "combined_standard_deviation": sqrt(total_variance),
        "between_group_variance_fraction": variance_between / total_variance if total_variance else None,
        "within_degrees_of_freedom": df_within,
        "between_degrees_of_freedom": df_between,
        "balanced_design_required": True,
        "accreditation_or_standard_conformance_claimed": False,
    }
