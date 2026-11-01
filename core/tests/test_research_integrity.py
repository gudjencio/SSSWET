import pytest

from ssswet_core.evidence_dossiers import EvidenceDossierService
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_integrity import ResearchIntegrityRegister


def _store_with_dossier(tmp_path):
    store = SQLiteResearchStore(tmp_path / "integrity.sqlite3")
    EvidenceDossierService(store).assemble("dossier-integrity", "Integrity review", "Recorded evidence summary.")
    return store


def test_high_severity_open_risk_recommends_campaign_hold_without_suspending(tmp_path):
    register = ResearchIntegrityRegister(_store_with_dossier(tmp_path))
    event = register.record(
        "dossier-integrity", "safety", "critical",
        "Potentially unsafe experimental procedure is described.",
        "reviewer-a",
    )
    report = register.report("dossier-integrity")
    assert event["hold_recommended"] is True
    assert report["campaign_hold_recommendation"] is True
    assert report["automatic_campaign_suspension"] is False
    assert report["automatic_research_authorization"] is False
    assert report["unresolved_high_or_critical"] == 1


def test_risk_state_updates_are_append_only_and_latest_state_is_reported(tmp_path):
    register = ResearchIntegrityRegister(_store_with_dossier(tmp_path))
    first = register.record(
        "dossier-integrity", "data_integrity", "high",
        "Source provenance is incomplete.", "reviewer-a", state="open",
    )
    second = register.record(
        "dossier-integrity", "data_integrity", "high",
        "Source provenance is incomplete.", "reviewer-b", state="under_review",
    )
    report = register.report("dossier-integrity")
    assert first["risk_id"] == second["risk_id"]
    assert len(report["events"]) == 2
    assert report["risks"][0]["state"] == "under_review"
    with pytest.raises(Exception):
        with register.store._connect() as connection:
            connection.execute(
                "DELETE FROM research_integrity_events WHERE event_id=?",
                (first["event_id"],),
            )


def test_high_risk_safety_closure_requires_human_authorization_reference(tmp_path):
    register = ResearchIntegrityRegister(_store_with_dossier(tmp_path))
    with pytest.raises(ValueError, match="authorization reference"):
        register.record(
            "dossier-integrity", "safety", "critical",
            "A high-risk activity needs review.", "reviewer-a",
            state="mitigated", mitigation="Controls have been proposed.",
        )
    event = register.record(
        "dossier-integrity", "safety", "critical",
        "A high-risk activity needs review.", "reviewer-a",
        state="mitigated", mitigation="Controls reviewed by competent authority.",
        authorization_reference="approval-record-2026-001",
    )
    assert event["hold_recommended"] is False
    assert event["research_authorized"] is False


def test_register_rejects_unknown_dossier_and_invalid_category(tmp_path):
    register = ResearchIntegrityRegister(_store_with_dossier(tmp_path))
    with pytest.raises(ValueError, match="Unknown evidence dossier"):
        register.record("missing", "safety", "high", "Concern", "reviewer")
    with pytest.raises(ValueError, match="category"):
        register.record("dossier-integrity", "unknown", "high", "Concern", "reviewer")
