"""Bounded freshness weighting without changing source claims."""
from __future__ import annotations
from math import exp


def score(age_days: float, half_life_days: float = 30.0) -> float:
    if age_days < 0 or half_life_days <= 0:
        raise ValueError("age_days must be non-negative and half_life_days positive")
    return exp(-0.6931471805599453 * age_days / half_life_days)
