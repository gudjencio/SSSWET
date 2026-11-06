"""Dimension-aware normalization for an explicit, conservative unit set."""
from __future__ import annotations

from math import isfinite


FACTORS = {
    "m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0,
    "s": 1.0, "ms": 0.001, "min": 60.0, "h": 3600.0,
    "kg": 1.0, "g": 0.001,
}
DIMENSIONS = {
    "m": "length", "cm": "length", "mm": "length", "km": "length",
    "s": "time", "ms": "time", "min": "time", "h": "time",
    "kg": "mass", "g": "mass",
}


def _finite_number(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert within one physical dimension; cross-dimension ratios are rejected."""
    number = _finite_number(value, "value")
    if from_unit not in FACTORS or to_unit not in FACTORS:
        raise ValueError("unsupported unit")
    if DIMENSIONS[from_unit] != DIMENSIONS[to_unit]:
        raise ValueError(
            f"incompatible units: {from_unit} ({DIMENSIONS[from_unit]}) and "
            f"{to_unit} ({DIMENSIONS[to_unit]})"
        )
    return number * FACTORS[from_unit] / FACTORS[to_unit]


def normalize_measurement(value: float, unit: str, canonical_unit: str) -> dict:
    normalized = convert(value, unit, canonical_unit)
    return {
        "value": normalized,
        "unit": canonical_unit,
        "dimension": DIMENSIONS[canonical_unit],
        "original": {"value": value, "unit": unit},
    }
