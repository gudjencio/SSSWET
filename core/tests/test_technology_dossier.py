import sqlite3

import pytest

from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.technology_dossier import TechnologyDossierRegistry


@pytest.fixture
def registry(tmp_path):
    return TechnologyDossierRegistry(SQLiteResearchStore(tmp_path / "research.sqlite3"))


def test_create_dossier_and_append_evidence_timeline(registry):
    created = registry.create(
        technology_id="warp-drive-001", title="Field propulsion concept",
        domain="advanced propulsion", actor_id="mira",
    )
    assert created["current_recorded_state"] == "concept"
    event = registry.append_event(
        technology_id="warp-drive-001", event_type="evidence_added",
        payload={"claim": "A theoretical model was reviewed", "classification": "hypothesis"},
        source_refs=["doi:10.example/123"], actor_id="mira",
    )
    dossier = registry.get("warp-drive-001")
    assert dossier["event_count"] == 2
    assert dossier["events"][1]["event_id"] == event["event_id"]
    assert dossier["scientific_validity_established"] is False


def test_status_transition_requires_sources_for_verified_states(registry):
    registry.create(technology_id="t-1", title="Test technology", domain="physics", actor_id="mira")
    with pytest.raises(ValueError, match="source references"):
        registry.append_event(
            technology_id="t-1", event_type="status_changed",
            payload={"state": "validated"}, actor_id="elias",
        )
    registry.append_event(
        technology_id="t-1", event_type="status_changed",
        payload={"state": "independently_verified"}, source_refs=["report:independent-1"],
        actor_id="elias",
    )
    assert registry.get("t-1")["current_recorded_state"] == "independently_verified"


def test_negative_results_are_first_class_and_require_provenance(registry):
    registry.create(technology_id="t-2", title="Prototype test", domain="materials", actor_id="theo")
    with pytest.raises(ValueError, match="source reference"):
        registry.append_event(
            technology_id="t-2", event_type="negative_result",
            payload={"result": "Test did not reproduce"}, actor_id="theo",
        )
    registry.append_event(
        technology_id="t-2", event_type="negative_result",
        payload={"result": "Test did not reproduce", "conditions": ["ambient temperature"]},
        source_refs=["lab-run:run-19"], actor_id="theo",
    )
    assert registry.get("t-2")["events"][-1]["event_type"] == "negative_result"


def test_duplicate_dossier_and_unknown_event_are_rejected(registry):
    registry.create(technology_id="t-3", title="Test", domain="engineering", actor_id="jun")
    with pytest.raises(sqlite3.IntegrityError):
        registry.create(technology_id="t-3", title="Duplicate", domain="engineering", actor_id="jun")
    with pytest.raises(ValueError, match="unsupported dossier event"):
        registry.append_event(
            technology_id="t-3", event_type="invented_event",
            payload={"note": "x"}, actor_id="jun",
        )


def test_dossier_events_are_append_only(registry):
    registry.create(technology_id="t-4", title="Test", domain="science", actor_id="mira")
    event = registry.append_event(
        technology_id="t-4", event_type="research_note",
        payload={"note": "A preliminary idea"}, actor_id="mira",
    )
    with registry.store._connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM technology_dossier_events WHERE event_id=?", (event["event_id"],)
            )


def test_invalid_payload_and_identifiers_are_rejected(registry):
    registry.create(technology_id="t-5", title="Test", domain="science", actor_id="mira")
    with pytest.raises(ValueError, match="JSON-compatible"):
        registry.append_event(
            technology_id="t-5", event_type="research_note",
            payload={"invalid": object()}, actor_id="mira",
        )
    with pytest.raises(ValueError, match="identifier"):
        registry.get("../secret")


def test_engine_exposes_persistent_dossier_workflow(tmp_path):
    from ssswet_core.engine import SSSWETEngine

    engine = SSSWETEngine(SQLiteResearchStore(tmp_path / "engine.sqlite3"))
    engine.create_technology_dossier(
        technology_id="engine-tech-1", title="Test propulsion concept",
        domain="propulsion", actor_id="mira",
    )
    engine.record_technology_event(
        technology_id="engine-tech-1", event_type="negative_result",
        payload={"finding": "Initial model did not converge"},
        source_refs=["simulation:run-001"], actor_id="jun",
    )
    dossier = engine.get_technology_dossier("engine-tech-1")
    assert dossier["event_count"] == 2
    assert dossier["events"][-1]["event_type"] == "negative_result"


def test_engine_requires_persistent_store_for_dossiers():
    from ssswet_core.engine import SSSWETEngine

    with pytest.raises(RuntimeError, match="persistent research store"):
        SSSWETEngine().create_technology_dossier(
            technology_id="t", title="T", domain="science", actor_id="mira"
        )
