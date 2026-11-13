"""Aggregate-only dataset shift diagnostics; row-level data is never accepted."""
from __future__ import annotations

from math import isfinite, sqrt
from typing import Any

MAX_FEATURES = 300
MAX_CATEGORIES = 200


def _number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f"{field} must be finite and within range")
    return result


def _integer(value: Any, field: str) -> int:
    number = _number(value, field, minimum=0)
    if not number.is_integer():
        raise ValueError(f"{field} must be an integer")
    return int(number)


def _summary(dataset: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(dataset, dict):
        raise ValueError(f"{label} must be an aggregate summary object")
    features = dataset.get("features")
    if not isinstance(features, list) or len(features) > MAX_FEATURES:
        raise ValueError(f"{label}.features must be a list of at most {MAX_FEATURES}")
    result = {}
    for item in features:
        if not isinstance(item, dict):
            raise ValueError("every feature summary must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 160:
            raise ValueError("feature name must contain 1 to 160 characters")
        name = name.strip()
        if name in result:
            raise ValueError("feature names must be unique")
        kind = item.get("kind")
        if kind not in {"numeric", "categorical"}:
            raise ValueError("feature kind must be numeric or categorical")
        count = _integer(item.get("count"), f"{name}.count")
        missing = _integer(item.get("missing_count"), f"{name}.missing_count")
        if missing > count:
            raise ValueError(f"{name}.missing_count cannot exceed count")
        unit = item.get("unit", "")
        if not isinstance(unit, str) or len(unit) > 80:
            raise ValueError(f"{name}.unit must be text of at most 80 characters")
        normalized = {
            "name": name, "kind": kind, "unit": unit.strip(),
            "count": count, "missing_count": missing,
            "missing_rate": missing / count if count else None,
            "observed_count": count - missing,
        }
        if kind == "numeric":
            normalized["mean"] = _number(item.get("mean"), f"{name}.mean")
            normalized["stddev"] = _number(item.get("stddev"), f"{name}.stddev", minimum=0)
        else:
            counts = item.get("category_counts")
            if not isinstance(counts, dict) or len(counts) > MAX_CATEGORIES:
                raise ValueError(f"{name}.category_counts must be an object with at most {MAX_CATEGORIES} categories")
            clean_counts = {}
            for category, raw_count in counts.items():
                if not isinstance(category, str) or not category or len(category) > 160:
                    raise ValueError("category labels must contain 1 to 160 characters")
                clean_counts[category] = _integer(raw_count, f"{name}.{category}")
            if sum(clean_counts.values()) != count - missing:
                raise ValueError(f"{name}.category_counts must sum to the non-missing count")
            normalized["category_counts"] = clean_counts
        result[name] = normalized
    return result


def compare_dataset_summaries(
    reference: dict[str, Any], candidate: dict[str, Any], *,
    numeric_smd_threshold: float = 0.1,
    missingness_delta_threshold: float = 0.1,
    categorical_tvd_threshold: float = 0.1,
) -> dict[str, Any]:
    """Compare schema and aggregate distributions without ingesting individual rows."""
    thresholds = {
        "numeric_smd": _number(numeric_smd_threshold, "numeric_smd_threshold", minimum=0),
        "missingness_delta": _number(missingness_delta_threshold, "missingness_delta_threshold", minimum=0),
        "categorical_tvd": _number(categorical_tvd_threshold, "categorical_tvd_threshold", minimum=0),
    }
    left, right = _summary(reference, "reference"), _summary(candidate, "candidate")
    added = sorted(set(right) - set(left))
    removed = sorted(set(left) - set(right))
    comparisons = []
    for name in sorted(set(left) & set(right)):
        a, b = left[name], right[name]
        flags = []
        row = {"feature": name, "reference_kind": a["kind"], "candidate_kind": b["kind"]}
        if a["kind"] != b["kind"]:
            row["status"] = "type_changed"
            flags.append("feature_type_changed")
        elif a["unit"] != b["unit"]:
            row["status"] = "unit_changed"
            flags.append("unit_mismatch")
        else:
            row["status"] = "comparable"
            if a["missing_rate"] is not None and b["missing_rate"] is not None:
                delta = b["missing_rate"] - a["missing_rate"]
                row["missingness_delta"] = delta
                if abs(delta) > thresholds["missingness_delta"]:
                    flags.append("missingness_shift")
            else:
                row["missingness_delta"] = None
                flags.append("missingness_unavailable")
            if a["kind"] == "numeric":
                n1, n2 = a["observed_count"], b["observed_count"]
                pooled_variance = (
                    ((n1 - 1) * a["stddev"] ** 2 + (n2 - 1) * b["stddev"] ** 2) / (n1 + n2 - 2)
                    if n1 + n2 > 2 else 0.0
                )
                pooled_sd = sqrt(max(0.0, pooled_variance))
                delta = b["mean"] - a["mean"]
                row["mean_delta"] = delta
                row["standardized_mean_difference"] = abs(delta) / pooled_sd if pooled_sd > 0 else (0.0 if delta == 0 else None)
                if row["standardized_mean_difference"] is None:
                    flags.append("standardized_difference_undefined_zero_variance")
                elif row["standardized_mean_difference"] > thresholds["numeric_smd"]:
                    flags.append("numeric_distribution_shift")
            else:
                n1, n2 = a["observed_count"], b["observed_count"]
                if n1 and n2:
                    categories = set(a["category_counts"]) | set(b["category_counts"])
                    tvd = 0.5 * sum(
                        abs(a["category_counts"].get(key, 0) / n1 - b["category_counts"].get(key, 0) / n2)
                        for key in categories
                    )
                    row["categorical_total_variation_distance"] = tvd
                    if tvd > thresholds["categorical_tvd"]:
                        flags.append("categorical_distribution_shift")
                else:
                    row["categorical_total_variation_distance"] = None
                    flags.append("categorical_distribution_unavailable")
        row["flags"] = flags
        comparisons.append(row)
    return {
        "reference_dataset_id": reference.get("dataset_id"),
        "candidate_dataset_id": candidate.get("dataset_id"),
        "added_features": added, "removed_features": removed,
        "feature_comparisons": comparisons,
        "thresholds": thresholds,
        "row_level_data_used": False,
        "causal_change_inferred": False,
        "scientific_validity_established": False,
    }
