"""Transparent evidence rubric; scores support review and do not prove truth."""
from __future__ import annotations

from math import isfinite


DIMENSIONS = ("source_quality", "method_transparency", "reproducibility", "independence")
WEIGHTS = {name: 0.2 for name in DIMENSIONS}
PROVENANCE_WEIGHT = 0.2


def score_evidence(*, source_quality: float, method_transparency: float, reproducibility: float, independence: float, provenance_complete: bool) -> dict:
    raw = {
        "source_quality": source_quality,
        "method_transparency": method_transparency,
        "reproducibility": reproducibility,
        "independence": independence,
    }
    for name, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0 <= value <= 5:
            raise ValueError(f"{name} must be a finite number between 0 and 5")
    if not isinstance(provenance_complete, bool):
        raise ValueError("provenance_complete must be a boolean")
    normalized = {name: value / 5.0 for name, value in raw.items()}
    provenance_score = 1.0 if provenance_complete else 0.0
    score = sum(normalized[name] * WEIGHTS[name] for name in DIMENSIONS) + provenance_score * PROVENANCE_WEIGHT
    weak_dimensions = [name for name, value in normalized.items() if value < 0.6]
    return {
        "score": round(score, 4),
        "percent": round(score * 100, 1),
        "provenance_complete": provenance_complete,
        "dimension_scores": {name: round(value, 4) for name, value in normalized.items()},
        "dimension_weights": dict(WEIGHTS),
        "provenance_weight": PROVENANCE_WEIGHT,
        "weak_dimensions": weak_dimensions,
        "review_required": score < 0.7 or not provenance_complete or bool(weak_dimensions),
        "score_is_a_review_aid_not_scientific_validation": True,
    }
