import math
import pytest

from ssswet_core.evidence_freshness import assess, score


def test_freshness_assessment_explains_recency_without_adjudicating_truth():
    recent = assess(0, 30)
    stale = assess(120, 30)
    assert recent["freshness_weight"] == 1.0
    assert recent["freshness_band"] == "recent"
    assert stale["freshness_band"] == "very_stale"
    assert stale["review_suggested"] is True
    assert stale["source_claim_modified"] is False
    assert stale["scientific_validity_established"] is False


def test_freshness_score_preserves_half_life_math():
    assert score(30, 30) == pytest.approx(0.5)
    assert score(60, 30) == pytest.approx(0.25)


@pytest.mark.parametrize("age,half_life", [
    (-1, 30), (0, 0), (math.nan, 30), (math.inf, 30),
    (30, math.inf), (True, 30), (30, False), ("1", 30),
])
def test_freshness_rejects_invalid_or_non_finite_inputs(age, half_life):
    with pytest.raises(ValueError):
        score(age, half_life)
