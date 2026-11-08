"""Non-parametric Kaplan-Meier reliability summaries for right-censored tests."""
from __future__ import annotations

from math import isfinite, sqrt

MAX_OBSERVATIONS = 100_000


def kaplan_meier(observations: list[dict]) -> dict:
    if not isinstance(observations, list) or not 1 <= len(observations) <= MAX_OBSERVATIONS:
        raise ValueError(f"observations must contain 1 to {MAX_OBSERVATIONS} items")
    rows, identifiers = [], set()
    for item in observations:
        if not isinstance(item, dict):
            raise ValueError("each observation must be an object")
        identifier = item.get("observation_id")
        duration = item.get("duration")
        event = item.get("event_observed")
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 200 or identifier in identifiers:
            raise ValueError("observation_id values must be unique non-empty strings")
        identifiers.add(identifier)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not isfinite(duration) or duration < 0:
            raise ValueError("duration must be a finite non-negative number")
        if type(event) is not bool:
            raise ValueError("event_observed must be a boolean")
        rows.append((float(duration), event))
    grouped: dict[float, list[int]] = {}
    for duration, event in rows:
        counts = grouped.setdefault(duration, [0, 0])
        counts[0 if event else 1] += 1
    times = sorted(grouped)
    at_risk = len(rows)
    survival = 1.0
    greenwood_sum = 0.0
    curve = []
    median_time = None
    for time in times:
        events, censored = grouped[time]
        before = at_risk
        if events:
            survival *= 1.0 - events / before
            if before > events:
                greenwood_sum += events / (before * (before - events))
        standard_error = survival * sqrt(greenwood_sum) if survival > 0 else 0.0
        lower = max(0.0, survival - 1.96 * standard_error)
        upper = min(1.0, survival + 1.96 * standard_error)
        curve.append({
            "time": time,
            "at_risk": before,
            "events": events,
            "censored": censored,
            "survival_probability": survival,
            "greenwood_standard_error": standard_error,
            "normal_95_ci": [lower, upper],
        })
        if median_time is None and survival <= 0.5:
            median_time = time
        at_risk -= events + censored
    return {
        "method": "kaplan_meier_product_limit",
        "observation_count": len(rows),
        "event_count": sum(event for _, event in rows),
        "censored_count": sum(not event for _, event in rows),
        "median_event_time": median_time,
        "median_not_reached": median_time is None,
        "curve": curve,
        "right_censoring_supported": True,
        "parametric_extrapolation_performed": False,
        "causal_or_field_reliability_claimed": False,
    }
