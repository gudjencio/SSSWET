import pytest
from ssswet_core.contradiction import ResearchClaim
from ssswet_core.context_aware_claim_comparison import ClaimContext, ContextAwareClaimComparator

def test_same_context_conflict_is_reported_for_review():
    items = [
        ClaimContext(ResearchClaim("coating", "thickness", "120", "paper-a"), scope="sample", unit="um"),
        ClaimContext(ResearchClaim("coating", "thickness", "105", "paper-b"), scope="sample", unit="um"),
    ]
    result = ContextAwareClaimComparator().compare(items)
    assert len(result) == 1
    assert result[0].classification == "potential_conflict"
    assert result[0].source_ids == ("paper-a", "paper-b")

def test_different_scope_conditions_and_units_are_not_compared():
    items = [
        ClaimContext(ResearchClaim("battery", "capacity", "100", "a"), scope="cell", unit="Wh"),
        ClaimContext(ResearchClaim("battery", "capacity", "80", "b"), scope="pack", unit="Wh"),
        ClaimContext(ResearchClaim("battery", "capacity", "70", "c"), scope="cell", conditions="cold", unit="Wh"),
        ClaimContext(ResearchClaim("battery", "capacity", "60", "d"), scope="cell", unit="mAh"),
    ]
    assert ContextAwareClaimComparator().compare(items) == []

def test_different_observation_dates_are_temporal_review_leads():
    items = [
        ClaimContext(ResearchClaim("material", "strength", "500", "a"), unit="MPa", observed_at="2024-01-01"),
        ClaimContext(ResearchClaim("material", "strength", "470", "b"), unit="MPa", observed_at="2025-01-01"),
    ]
    result = ContextAwareClaimComparator().compare(items)
    assert len(result) == 1
    assert result[0].classification == "temporal_difference_needs_review"
    assert result[0].observed_at_values == ("2024-01-01", "2025-01-01")

def test_same_source_disagreement_is_not_independent_support():
    items = [
        ClaimContext(ResearchClaim("sensor", "error", "1", "same"), unit="percent"),
        ClaimContext(ResearchClaim("sensor", "error", "2", "same"), unit="percent"),
    ]
    assert ContextAwareClaimComparator().compare(items) == []

def test_context_type_is_required():
    with pytest.raises(AttributeError):
        ContextAwareClaimComparator().compare([None])
