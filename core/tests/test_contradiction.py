import pytest

from ssswet_core.contradiction import ContradictionDetector, ResearchClaim


def test_detects_conflicting_values_from_distinct_sources():
    claims = [
        ResearchClaim("water", "boiling_point_c", "100", "source-a"),
        ResearchClaim("water", "boiling_point_c", "98", "source-b"),
    ]
    conflicts = ContradictionDetector().compare(claims)
    assert len(conflicts) == 1
    assert set(conflicts[0].values) == {"100", "98"}
    assert conflicts[0].source_ids == ("source-a", "source-b")
    assert "Check units" in conflicts[0].explanation
    assert ContradictionDetector().requires_third_review(claims)


def test_normalizes_whitespace_and_case_for_subject_predicate_and_value():
    claims = [
        ResearchClaim("  Water  ", "Boiling   Point", "  100   C ", "source-a"),
        ResearchClaim("water", "boiling point", "100 c", "source-b"),
    ]
    assert ContradictionDetector().compare(claims) == []


def test_detects_conflict_after_normalizing_whitespace_and_case():
    claims = [
        ResearchClaim("  Water  ", "Boiling   Point", "  100   C ", "source-a"),
        ResearchClaim("water", "boiling point", " 98 C ", "source-b"),
    ]
    conflicts = ContradictionDetector().compare(claims)
    assert len(conflicts) == 1
    assert conflicts[0].subject == "water"
    assert conflicts[0].predicate == "boiling point"
    assert set(conflicts[0].values) == {"100   C", "98 C"}


def test_does_not_flag_matching_claims_or_same_source_variants():
    detector = ContradictionDetector()
    matching = [
        ResearchClaim("water", "state", "liquid", "source-a"),
        ResearchClaim("water", "state", "liquid", "source-b"),
    ]
    same_source = [
        ResearchClaim("water", "state", "liquid", "source-a"),
        ResearchClaim("water", "state", "solid", "source-a"),
    ]
    assert detector.compare(matching) == []
    assert detector.compare(same_source) == []


def test_rejects_missing_or_non_string_claim_fields():
    with pytest.raises(ValueError, match="subject"):
        ResearchClaim("", "state", "liquid", "source-a")
    with pytest.raises(ValueError, match="value"):
        ResearchClaim("water", "state", " ", "source-a")
    with pytest.raises(ValueError, match="source_id"):
        ResearchClaim("water", "state", "liquid", "")
    with pytest.raises(ValueError, match="predicate"):
        ResearchClaim("water", None, "liquid", "source-a")
