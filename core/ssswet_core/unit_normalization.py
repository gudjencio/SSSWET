"""Deterministic normalization for a small, explicit set of scientific units."""
from __future__ import annotations

FACTORS = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "s": 1.0, "ms": 0.001, "min": 60.0, "h": 3600.0, "kg": 1.0, "g": 0.001}


def convert(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit not in FACTORS or to_unit not in FACTORS:
        raise ValueError("unsupported unit")
    return value * FACTORS[from_unit] / FACTORS[to_unit]


def normalize_measurement(value: float, unit: str, canonical_unit: str) -> dict:
    normalized = convert(value, unit, canonical_unit)
    return {"value": normalized, "unit": canonical_unit, "original": {"value": value, "unit": unit}}
