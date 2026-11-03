"""IQR-based outlier flags for human review; observations are never removed."""
from __future__ import annotations
import math

def flag_iqr(values: list[float], factor: float = 1.5) -> dict:
    if not isinstance(values, list) or len(values) < 4 or len(values) > 1_000_000:
        raise ValueError("values must contain between 4 and 1000000 observations")
    if isinstance(factor, bool) or not isinstance(factor, (int, float)) or not math.isfinite(factor) or factor <= 0:
        raise ValueError("factor must be a finite positive number")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("values must be finite numbers")
    ordered = sorted(float(v) for v in values)
    mid = len(ordered) // 2
    lower, upper = ordered[:mid], ordered[mid:] if len(ordered) % 2 == 0 else ordered[mid + 1:]
    def median(items):
        m = len(items) // 2
        return items[m] if len(items) % 2 else (items[m - 1] + items[m]) / 2
    q1, q3 = median(lower), median(upper)
    iqr = q3 - q1
    low, high = q1 - factor * iqr, q3 + factor * iqr
    flagged = [{"index": i, "value": value} for i, value in enumerate(values) if value < low or value > high]
    return {"q1": q1, "q3": q3, "iqr": iqr, "lower_fence": low, "upper_fence": high, "flagged": flagged, "flagged_count": len(flagged), "observations_removed": 0, "review_required": bool(flagged)}
