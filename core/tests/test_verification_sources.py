from ssswet_core.models import Finding, VerificationState
from ssswet_core.verification import VerificationEngine


def test_two_evidence_strings_without_source_ids_are_not_independent():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(finding, "evidence one")
    result = engine.independent_check(result, "evidence two")
    assert result.verification == VerificationState.CANDIDATE
    assert result.metadata["independent_sources"] == []


def test_distinct_source_ids_are_required_for_independent_verification():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(finding, "evidence one", "paper-a")
    result = engine.independent_check(result, "evidence two", "paper-b")
    assert result.verification == VerificationState.INDEPENDENTLY_VERIFIED


def test_duplicate_source_does_not_count_twice():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(finding, "evidence one", "paper-a")
    result = engine.independent_check(result, "more from same paper", "paper-a")
    assert result.verification == VerificationState.CANDIDATE


def test_reproduction_requires_independent_sources_and_separate_run():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    blocked = engine.require_reproduction(finding, "run-1")
    assert blocked.verification == VerificationState.HYPOTHESIS

    verified = engine.independent_check(finding, "e1", "source-a")
    verified = engine.independent_check(verified, "e2", "source-b")
    reproduced = engine.require_reproduction(verified, "run-1")
    assert reproduced.verification == VerificationState.REPRODUCED
