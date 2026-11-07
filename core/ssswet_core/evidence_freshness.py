"""Bounded freshness weighting that never changes source claims."""
from __future__ import annotations

from math import exp, isfinite


def score(age_days: float, half_life_days: float = 30.0) -> float:
    """Return exponential recency weight; this is not an evidence-truth score."""
    if (
        isinstance(age_days, bool) or isinstance(half_life_days, bool)
        or not isinstance(age_days, (int, float))
        or not isinstance(half_life_days, (int, float))
        or not isfinite(age_days) or not isfinite(half_life_days)
        or age_days < 0 or half_life_days <= 0
    ):
        raise ValueError("age_days must be finite and non-negative; half_life_days must be finite and positive")
    return exp(-0.6931471805599453 * age_days / half_life_days)


def assess(age_days: float, half_life_days: float = 30.0) -> dict:
    """Explain recency weighting with bounded labels and explicit non-adjudication."""
    value = score(age_days, half_life_days)
    if value >= 0.8:
        band = "recent"
    elif value >= 0.5:
        band = "aging"
    elif value >= 0.2:
        band = "stale"
    else:
        band = "very_stale"
    return {
        "age_days": float(age_days),
        "half_life_days": float(half_life_days),
        "freshness_weight": round(value, 6),
        "freshness_band": band,
        "review_suggested": band in {"stale", "very_stale"},
        "source_claim_modified": False,
        "scientific_validity_established": False,
    }
