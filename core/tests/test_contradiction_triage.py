from ssswet_core.contradiction import ClaimConflict
from ssswet_core.contradiction_triage import triage_conflicts


def test_triage_groups_same_subject_and_predicate():
    conflicts = [ClaimConflict("x", "mass", ("1", "2")), ClaimConflict("x", "mass", ("2", "3"))]
    result = triage_conflicts(conflicts)
    assert result[0]["values"] == ["1", "2", "3"]
    assert result[0]["conflict_count"] == 2
