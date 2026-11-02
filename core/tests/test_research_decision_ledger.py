import sqlite3
import pytest

from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_decision_ledger import ResearchDecisionLedger


@pytest.fixture
def ledger(tmp_path):
    return ResearchDecisionLedger(SQLiteResearchStore(tmp_path / "decisions.sqlite3"))


def test_decisions_preserve_rationale_evidence_and_status_history(ledger):
    item = ledger.record(
        subject_id="claim-1", rationale="Initial interpretation is provisional.",
        actor_id="mira", evidence_refs=["doi:10.example/a"], reviewer_ids=["elias"],
    )
    ledger.transition(
        item["decision_id"], status="challenged",
        rationale="A second dataset has a different result.",
        actor_id="elias", evidence_refs=["dataset:second"],
    )
    result = ledger.get(item["decision_id"])
    assert result["current_recorded_status"] == "challenged"
    assert result["events"][0]["evidence_refs"] == ["doi:10.example/a"]
    assert result["events"][1]["rationale"].startswith("A second dataset")
    assert result["scientific_truth_established"] is False


def test_correction_creates_new_decision_and_links_previous(ledger):
    old = ledger.record(subject_id="claim-2", rationale="First estimate.", actor_id="mira")
    new = ledger.record(
        subject_id="claim-2", rationale="Corrected estimate after recalculation.",
        actor_id="asha", evidence_refs=["calculation:revision-2"],
        supersedes_decision_id=old["decision_id"],
    )
    assert new["supersedes_decision_id"] == old["decision_id"]
    assert ledger.get(old["decision_id"])["current_recorded_status"] == "superseded"
    assert ledger.get(new["decision_id"])["current_recorded_status"] == "proposed"
    assert len(ledger.history("claim-2")) == 3


def test_supersession_requires_existing_same_subject_and_evidence(ledger):
    with pytest.raises(ValueError, match="does not exist"):
        ledger.record(subject_id="claim-a", rationale="x", actor_id="mira",
                      evidence_refs=["ref"], supersedes_decision_id="missing")
    old = ledger.record(subject_id="claim-a", rationale="x", actor_id="mira")
    with pytest.raises(ValueError, match="same subject"):
        ledger.record(subject_id="claim-b", rationale="y", actor_id="mira",
                      evidence_refs=["ref"], supersedes_decision_id=old["decision_id"])
    with pytest.raises(ValueError, match="evidence references"):
        ledger.record(subject_id="claim-a", rationale="y", actor_id="mira",
                      supersedes_decision_id=old["decision_id"])


def test_status_transitions_and_terminal_states_are_enforced(ledger):
    item = ledger.record(subject_id="claim-3", rationale="Proposal.", actor_id="mira")
    with pytest.raises(ValueError, match="unsupported"):
        ledger.transition(item["decision_id"], status="validated,
                          rationale="Not an allowed state.", actor_id="elias")
    ledger.transition(item["decision_id"], status="rejected",
                      rationale="Evidence did not support it.", actor_id="elias")
    with pytest.raises(ValueError, match="invalid"):
        ledger.transition(item["decision_id"], status="supported",
                          rationale="Attempt to revive.", actor_id="mira")


def test_event_log_is_append_only(ledger):
    item = ledger.record(subject_id="claim-4", rationale="Proposal.", actor_id="mira")
    with ledger.store._connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM research_decision_events WHERE event_id=?",
                               (item["event_id"],))


def test_history_is_bounded_and_validates_subject(ledger):
    ledger.record(subject_id="claim-5", rationale="Proposal.", actor_id="mira")
    with pytest.raises(ValueError, match="limit"):
        ledger.history("claim-5", limit=0)
