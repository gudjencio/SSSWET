"""Privacy-minimised distribution-drift checks over aggregate summaries only."""
from __future__ import annotations
from math import isfinite, log

MAX_FEATURES = 100
MAX_CATEGORIES = 100
MAX_COUNT = 1_000_000_000_000

def _number(value, field, *, minimum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    try:
        numeric = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{field} must be a finite number") from None
    if not isfinite(numeric):
        raise ValueError(f"{field} must be a finite number")
    if minimum is not None and numeric < minimum:
        raise ValueError(f"{field} must be at least {minimum}")
    return numeric

def _count(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_COUNT:
        raise ValueError(f"{field} must be an integer between 1 and {MAX_COUNT}")
    return value

def _js_divergence(left: dict[str, float], right: dict[str, float]) -> float:
    keys = sorted(set(left) | set(right))
    left_total, right_total = sum(left.values()), sum(right.values())
    if not isfinite(left_total) or not isfinite(right_total) or left_total <= 0 or right_total <= 0:
        raise ValueError("categorical summaries must have finite positive total counts")
    p = {key: left.get(key, 0.0) / left_total for key in keys}
    q = {key: right.get(key, 0.0) / right_total for key in keys}
    midpoint = {key: (p[key] + q[key]) / 2 for key in keys}
    def kl(distribution):
        return sum(value * log(value / midpoint[key]) for key, value in distribution.items() if value > 0)
    return (kl(p) + kl(q)) / 2

def _validate_summary(summary: dict, label: str) -> dict:
    if not isinstance(summary, dict) or not isinstance(summary.get("features"), dict):
        raise ValueError(f"{label} must contain a features object")
    features = summary["features"]
    if len(features) > MAX_FEATURES:
        raise ValueError(f"{label} exceeds {MAX_FEATURES} features")
    clean = {}
    for name, feature in features.items():
        if not isinstance(name, str) or not name.strip() or len(name) > 120 or not isinstance(feature, dict):
            raise ValueError("feature names and summaries must be valid and bounded")
        kind = feature.get("kind")
        if kind == "numeric":
            clean[name] = {
                "kind": kind,
                "count": _count(feature.get("count"), f"{name}.count"),
                "mean": _number(feature.get("mean"), f"{name}.mean"),
                "stddev": _number(feature.get("stddev"), f"{name}.stddev", minimum=0),
            }
        elif kind == "categorical":
            counts = feature.get("counts")
            if not isinstance(counts, dict) or not 1 <= len(counts) <= MAX_CATEGORIES:
                raise ValueError(f"{name}.counts must contain 1 to {MAX_CATEGORIES} categories")
            clean_counts = {}
            for category, count in counts.items():
                if not isinstance(category, str) or not category or len(category) > 200:
                    raise ValueError("category names must be non-empty strings of at most 200 characters")
                clean_counts[category] = _number(count, f"{name}.{category}", minimum=0)
            total = sum(clean_counts.values())
            if not isfinite(total) or total <= 0:
                raise ValueError(f"{name} must have finite positive categorical count")
            clean[name] = {"kind": kind, "counts": clean_counts}
        else:
            raise ValueError(f"{name}.kind must be numeric or categorical")
    return clean

def compare_dataset_summaries(baseline: dict, current: dict, *, numeric_shift_threshold: float = 0.5, categorical_js_threshold: float = 0.1) -> dict:
    """Compare pre-aggregated summaries; no row-level data is accepted or stored."""
    numeric_threshold = _number(numeric_shift_threshold, "numeric_shift_threshold", minimum=0)
    categorical_threshold = _number(categorical_js_threshold, "categorical_js_threshold", minimum=0)
    if numeric_threshold > 10 or categorical_threshold > 1:
        raise ValueError("drift thresholds are outside supported bounds")
    left, right = _validate_summary(baseline, "baseline"), _validate_summary(current, "current")
    results = []
    for name in sorted(set(left) | set(right)):
        if name not in left or name not in right:
            results.append({"feature": name, "status": "missing_on_one_side", "review_required": True})
            continue
        a, b = left[name], right[name]
        if a["kind"] != b["kind"]:
            results.append({"feature": name, "status": "type_mismatch", "review_required": True})
            continue
        if a["kind"] == "numeric":
            pooled = ((a["stddev"] ** 2 + b["stddev"] ** 2) / 2) ** 0.5
            shift = abs(b["mean"] - a["mean"]) / pooled if pooled else (0.0 if a["mean"] == b["mean"] else None)
            ratio = None if a["stddev"] == 0 else b["stddev"] / a["stddev"]
            constant_added = a["stddev"] == 0 and b["stddev"] > 0
            flagged = shift is None or shift > numeric_threshold or constant_added or (ratio is not None and (ratio > 2 or ratio < 0.5))
            results.append({
                "feature": name, "kind": "numeric",
                "standardized_mean_shift": round(shift, 6) if shift is not None else None,
                "stddev_ratio": round(ratio, 6) if ratio is not None else None,
                "constant_baseline_variance_added": constant_added, "review_required": flagged,
            })
        else:
            divergence = _js_divergence(a["counts"], b["counts"])
            results.append({
                "feature": name, "kind": "categorical",
                "jensen_shannon_divergence_nats": round(divergence, 8),
                "review_required": divergence > categorical_threshold,
            })
    flagged = sum(bool(item["review_required"]) for item in results)
    return {
        "features_compared": len(results), "features_flagged_for_review": flagged, "results": results,
        "aggregate_only": True, "raw_rows_received": False,
        "drift_is_not_causality_or_data_invalidity": True,
        "thresholds": {"numeric_standardized_mean_shift": numeric_threshold,
                       "categorical_js_divergence_nats": categorical_threshold},
    }
