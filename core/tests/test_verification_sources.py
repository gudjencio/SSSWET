import pytest

from ssswet_core.models import Finding, VerificationState
from ssswet_core.verification import VerificationEngine


def assessed_pair(engine, finding):
    result = engine.independent_check(
        finding, "evidence one", "paper-a",
        independence_group="research-team-a", independence_confirmed=True,
    )
    return engine.independent_check(
        result, "evidence two", "paper-b",
        independence_group="research-team-b", independence_confirmed=True,
    )


def test_two_evidence_strings_without_source_ids_are_not_independent():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(finding, "evidence one")
    result = engine.independent_check(result, "evidence two")
    assert result.verification == VerificationState.CANDIDATE
    assert result.metadata["independent_sources"] == []


def test_distinct_source_ids_need_explicit_independence_assessment():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(finding, "evidence one", "paper-a")
    result = engine.independent_check(result, "evidence two", "paper-b")
    assert result.verification == VerificationState.CANDIDATE
    assert "independence has not been explicitly assessed" in " ".join(result.limitations)


def test_same_provenance_group_does_not_count_twice():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="candidate")
    result = engine.independent_check(
        finding, "evidence one", "paper-a",
        independence_group="same-lab", independence_confirmed=True,
    )
    result = engine.independent_check(
        result, "evidence two", "paper-b",
        independence_group="same-lab", independence_confirmed=True,
    )
    assert result.verification == VerificationState.CANDIDATE


def test_two_assessed_independent_groups_are_required():
    engine = VerificationEngine()
    result = assessed_pair(engine, Finding(task_id="t1", summary="candidate"))
    assert result.verification == VerificationState.INDEPENDENTLY_VERIFIED


def test_reproduction_requires_explicit_confirmation_and_separate_run():
    engine = VerificationEngine()
    verified = assessed_pair(engine, Finding(task_id="t1", summary="candidate"))

    blocked = engine.require_reproduction(verified, "run-1")
    assert blocked.verification == VerificationState.INDEPENDENTLY_VERIFIED

    reproduced = engine.require_reproduction(
        verified, "run-1", reproduction_confirmed=True,
    )
    assert reproduced.verification == VerificationState.REPRODUCED

    same_id = engine.require_reproduction(
        verified, "paper-a", reproduction_confirmed=True,
    )
    assert same_id.verification == VerificationState.INDEPENDENTLY_VERIFIED


def test_real_world_validation_remains_separate():
    engine = VerificationEngine()
    finding = Finding(task_id="t1", summary="simulation result")
    result = engine.mark_real_world_validation_required(finding)
    assert result.verification == VerificationState.REQUIRES_REAL_WORLD_VALIDATION


def test_verification_does_not_mutate_original_finding():
    engine = VerificationEngine()
    original = Finding(task_id="t1", summary="candidate")
    engine.independent_check(
        original, "evidence", "paper-a",
        independence_group="group-a", independence_confirmed=True,
    )
    assert original.evidence == []
    assert original.metadata == {}
