from ssswet_core.contradiction import ContradictionDetector, ResearchClaim


def test_detects_conflicting_values_from_distinct_sources():
    claims = [
        ResearchClaim("water", "boiling_point_c", "100", "source-a"),
        ResearchClaim("water", "boiling_point_c", "98", "source-b"),
    ]
    conflicts = ContradictionDetector().compare(claims)
    assert len(conflicts) == 1
    assert set(conflicts[0].values) == {"100", "98"}
    assert ContradictionDetector().requires_third_review(claims)


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
