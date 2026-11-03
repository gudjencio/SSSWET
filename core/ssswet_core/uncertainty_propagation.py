"""Conservative uncertainty propagation for arithmetic research estimates."""
from __future__ import annotations
from math import sqrt


def combine_independent_additive(values: list[tuple[float, float]]) -> dict:
    """Combine value/1-sigma pairs for a sum; assumptions remain explicit."""
    if not values:
        raise ValueError("at least one value is required")
    if any(error < 0 for _, error in values):
        raise ValueError("uncertainties must be non-negative")
    value = sum(item[0] for item in values)
    uncertainty = sqrt(sum(error * error for _, error in values))
    return {"value": value, "uncertainty": uncertainty, "method": "independent_quadrature", "assumption": "independent errors"}


def combine_worst_case(values: list[tuple[float, float]]) -> dict:
    """Combine value/absolute-error pairs without assuming independence."""
    if not values:
        raise ValueError("at least one value is required")
    if any(error < 0 for _, error in values):
        raise ValueError("uncertainties must be non-negative")
    return {"value": sum(v for v, _ in values), "uncertainty": sum(e for _, e in values), "method": "worst_case_absolute", "assumption": "no cancellation assumed"}
