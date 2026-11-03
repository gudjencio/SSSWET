"""Compare numeric feature distributions with transparent standardized shifts."""
from __future__ import annotations
import math
from statistics import fmean, pstdev

def compare(reference: dict[str, list[float]], current: dict[str, list[float]], threshold: float = 0.5) -> dict:
    if not isinstance(reference, dict) or not isinstance(current, dict) or set(reference) != set(current):
        raise ValueError("reference and current must contain the same feature names")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")
    features = {}
    for name in sorted(reference):
        left, right = reference[name], current[name]
        if not isinstance(name, str) or not name or not isinstance(left, list) or not isinstance(right, list) or not left or not right:
            raise ValueError("each feature requires a name and two non-empty numeric lists")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in left + right):
            raise ValueError("feature values must be finite numbers")
        mean_a, mean_b = fmean(left), fmean(right)
        scale = math.sqrt((pstdev(left) ** 2 + pstdev(right) ** 2) / 2)
        shift = abs(mean_b - mean_a) / scale if scale else (0.0 if mean_a == mean_b else None)
        features[name] = {"reference_count": len(left), "current_count": len(right), "reference_mean": mean_a, "current_mean": mean_b, "standardized_mean_shift": shift, "shift_detected": shift is not None and shift >= threshold, "constant_distributions_differ": shift is None}
    return {"features": features, "feature_count": len(features), "shifted_feature_count": sum(1 for item in features.values() if item["shift_detected"]), "threshold": threshold, "causal_change_inferred": False}
