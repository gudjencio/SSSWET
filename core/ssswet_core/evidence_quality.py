def score_evidence(*, source_quality: float, method_transparency: float, reproducibility: float, independence: float, provenance_complete: bool) -> dict:
    values = [source_quality, method_transparency, reproducibility, independence]
    if any(v < 0 or v > 5 for v in values):
        raise ValueError("evidence dimensions must be between 0 and 5")
    completeness = 1.0 if provenance_complete else 0.0
    score = (sum(values) / 20.0) * 0.8 + completeness * 0.2
    return {
        "score": round(score, 4),
        "percent": round(score * 100, 1),
        "provenance_complete": provenance_complete,
        "review_required": score < 0.7 or not provenance_complete,
    }
