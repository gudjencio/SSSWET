from ssswet_core.research_checkpoint import CheckpointLedger


def test_checkpoint_versions_are_monotonic_and_recoverable():
    ledger = CheckpointLedger()
    ledger.save("t1", "hypothesis", source_refs=["s1"], unresolved_questions=["q"])
    latest = ledger.save("t1", "experiment", source_refs=["s2"])
    assert latest.version == 2
    assert ledger.latest("t1").state == "experiment"
    assert len(ledger.history("t1")) == 2
