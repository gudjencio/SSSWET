from ssswet_core.technology_progression import evaluate_progression, persistence_status


def verified(value):
    return {"value": value, "evidence_status": "verified", "source_refs": ["source:test"]}


def test_candidate_cannot_regress_verified_capability():
    decision = evaluate_progression(
        {"usefulness": verified(4), "performance": verified(4)},
        {"usefulness": verified(3), "performance": verified(5)},
        candidate_safety_gate=True,
        candidate_legality_gate=True,
    )
    assert not decision.accepted
    assert decision.regressions == ("usefulness: 3 < previous 4",)


def test_missing_candidate_capability_blocks_progression():
    decision = evaluate_progression(
        {"durability": verified(4)},
        {},
        candidate_safety_gate=True,
        candidate_legality_gate=True,
    )
    assert not decision.accepted
    assert "durability: candidate value is missing" in decision.regressions


def test_verified_improvements_are_accepted_when_gates_pass():
    decision = evaluate_progression(
        {"usefulness": verified(3), "efficiency": verified(3)},
        {"usefulness": verified(4), "efficiency": verified(4)},
        candidate_safety_gate=True,
        candidate_legality_gate=True,
    )
    assert decision.accepted
    assert decision.improvements == ("usefulness", "efficiency")


def test_unverified_claim_cannot_count_as_improvement():
    decision = evaluate_progression(
        {"performance": verified(3)},
        {"performance": {"value": 4, "evidence_status": "target"}},
        candidate_safety_gate=True,
        candidate_legality_gate=True,
    )
    assert not decision.accepted
    assert "claimed improvements require observed or verified evidence" in decision.reasons


def test_persistence_never_overrides_governance():
    state = persistence_status("Evidence is currently insufficient.")
    assert state["continue_research"] is True
    assert "record_negative_result" in state["allowed_next_steps"]
    assert "safety" in state["constraint"]
