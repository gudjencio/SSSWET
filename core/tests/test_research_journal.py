import pytest

from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_journal import ResearchJournal


def test_journal_appends_hash_chained_entries_and_filters_by_technology(tmp_path):
    store = SQLiteResearchStore(tmp_path / "journal.sqlite3")
    journal = ResearchJournal(store)
    first = journal.append(
        technology="timetravel", event_type="research_question",
        title="Causality constraints", summary="Map established constraints before proposing models.",
        classification="hypothesis", evidence_refs=["doi:10.example/1"],
    )
    second = journal.append(
        technology="spacetime", event_type="literature_review",
        title="Metric models", summary="Review published mathematical frameworks.",
        classification="literature",
    )
    assert first["previous_hash"] == "0" * 64
    assert second["previous_hash"] == first["entry_hash"]
    assert journal.verify_chain()["chain_intact"] is True
    report = journal.overview(technology="timetravel")
    assert report["count"] == 1
    assert report["entries"][0]["entry_id"] == first["entry_id"]
    assert report["scientific_validity_established"] is False


def test_journal_rejects_unknown_technology_and_invalid_classification(tmp_path):
    journal = ResearchJournal(SQLiteResearchStore(tmp_path / "journal.sqlite3"))
    with pytest.raises(ValueError, match="unknown technology"):
        journal.append(technology="teleportation", event_type="simulation", title="x", summary="y")
    with pytest.raises(ValueError, match="unsupported evidence classification"):
        journal.append(technology="armor", event_type="simulation", title="x", summary="y", classification="proven")


def test_journal_is_append_only_and_rejects_bad_references(tmp_path):
    store = SQLiteResearchStore(tmp_path / "journal.sqlite3")
    journal = ResearchJournal(store)
    entry = journal.append(technology="armor", event_type="prototype", title="Shell concept", summary="CAD mock-up only.")
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("UPDATE research_journal SET title='changed' WHERE entry_id=?", (entry["entry_id"],))
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("DELETE FROM research_journal WHERE entry_id=?", (entry["entry_id"],))
    with pytest.raises(ValueError, match="evidence reference"):
        journal.append(technology="armor", event_type="test", title="Invalid", summary="Bad reference", evidence_refs=[""])


def test_journal_detects_modified_chain_payload(tmp_path):
    store = SQLiteResearchStore(tmp_path / "journal.sqlite3")
    journal = ResearchJournal(store)
    journal.append(technology="cellular", event_type="milestone", title="Record", summary="Initial note")
    with store._connect() as connection:
        connection.execute("DROP TRIGGER research_journal_no_update")
        connection.execute("UPDATE research_journal SET summary='tampered' WHERE sequence=1")
    result = journal.verify_chain()
    assert result["chain_intact"] is False
    assert result["invalid_entries"] == ["journal-00000001"]


def test_journal_validates_limit_and_technology(tmp_path):
    journal = ResearchJournal(SQLiteResearchStore(tmp_path / "journal.sqlite3"))
    with pytest.raises(ValueError, match="limit"):
        journal.overview(limit=0)
    with pytest.raises(ValueError, match="unknown technology"):
        journal.overview(technology="unknown")


def test_journal_accepts_the_eight_additional_research_areas(tmp_path):
    journal = ResearchJournal(SQLiteResearchStore(tmp_path / "expanded-journal.sqlite3"))
    technologies = ["neurointerfaces", "quantumNetworks", "fusionEnergy", "spaceLifeSupport", "autonomousLabs", "roboticsExoskeletons", "planetaryMonitoring", "advancedComputing"]
    for technology in technologies:
        entry = journal.append(
            technology=technology, event_type="research_question",
            title="Initial research question", summary="Define a bounded, evidence-led research question.",
        )
        assert entry["technology"] == technology
    assert journal.verify_chain()["chain_intact"] is True


def test_journal_supports_exactly_one_hundred_research_programmes(tmp_path):
    from ssswet_core.research_journal import TECHNOLOGIES
    assert len(TECHNOLOGIES) == 100
    required = {
        "blackHoleObservation", "blackHoleProbeSystems", "blackHoleResilientVehicles",
        "nuclearBlastResilience", "radiationProtection",
    }
    assert required <= TECHNOLOGIES
    journal = ResearchJournal(SQLiteResearchStore(tmp_path / "hundred-programmes.sqlite3"))
    for technology in sorted(required):
        record = journal.append(
            technology=technology, event_type="research_question",
            title="Initial safety and feasibility review",
            summary="Define evidence requirements, physical limits and qualified review boundaries.",
        )
        assert record["technology"] == technology
