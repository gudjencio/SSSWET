from ssswet_core.evidence_quality import score_evidence


def test_complete_high_quality_evidence_scores_high():
    result = score_evidence(source_quality=5, method_transparency=5, reproducibility=5, independence=5, provenance_complete=True)
    assert result["score"] == 1.0
    assert not result["review_required"]


def test_missing_provenance_forces_review():
    result = score_evidence(source_quality=5, method_transparency=5, reproducibility=5, independence=5, provenance_complete=False)
    assert result["review_required"]


def test_score_exposes_dimension_breakdown_and_weak_areas():
    result = score_evidence(
        source_quality=5, method_transparency=5, reproducibility=5,
        independence=2, provenance_complete=True,
    )
    assert result["dimension_scores"]["independence"] == 0.4
    assert result["weak_dimensions"] == ["independence"]
    assert result["review_required"] is True
    assert result["score_is_a_review_aid_not_scientific_validation"] is True


def test_score_rejects_nan_infinity_booleans_and_non_boolean_provenance():
    import math
    import pytest
    for value in (math.nan, math.inf, -math.inf, True, "5"):
        with pytest.raises(ValueError):
            score_evidence(
                source_quality=value, method_transparency=5, reproducibility=5,
                independence=5, provenance_complete=True,
            )
    with pytest.raises(ValueError, match="boolean"):
        score_evidence(
            source_quality=5, method_transparency=5, reproducibility=5,
            independence=5, provenance_complete=1,
        )
