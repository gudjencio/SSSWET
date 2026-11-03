"""Evaluate probabilistic binary predictions with Brier score and equal-width ECE."""
from __future__ import annotations
import math

def evaluate(probabilities: list[float], outcomes: list[int], bins: int = 10) -> dict:
    if not isinstance(probabilities, list) or not isinstance(outcomes, list) or not probabilities or len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must be non-empty lists of equal length")
    if len(probabilities) > 1_000_000:
        raise ValueError("input exceeds the 1000000-observation limit")
    if isinstance(bins, bool) or not isinstance(bins, int) or not 1 <= bins <= 100:
        raise ValueError("bins must be an integer from 1 to 100")
    for p in probabilities:
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError("probabilities must be finite values from 0 to 1")
    if any(type(y) is not int or y not in (0, 1) for y in outcomes):
        raise ValueError("outcomes must contain only integer 0 or 1 values")
    n = len(probabilities)
    brier = sum((float(p) - y) ** 2 for p, y in zip(probabilities, outcomes)) / n
    rows, ece = [], 0.0
    for index in range(bins):
        members = [(float(p), y) for p, y in zip(probabilities, outcomes) if index / bins <= p < (index + 1) / bins or (index == bins - 1 and p == 1)]
        if members:
            confidence = sum(p for p, _ in members) / len(members)
            accuracy = sum(y for _, y in members) / len(members)
            gap = abs(confidence - accuracy)
            ece += len(members) / n * gap
        else:
            confidence = accuracy = gap = None
        rows.append({"bin": index, "count": len(members), "mean_confidence": confidence, "observed_frequency": accuracy, "absolute_gap": gap})
    return {"count": n, "brier_score": brier, "expected_calibration_error": ece, "bins": rows, "interpretation": "Descriptive calibration metrics; not a guarantee of future performance."}
