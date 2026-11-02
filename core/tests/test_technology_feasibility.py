from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_journal import ResearchJournal
from ssswet_core.technology_feasibility import TechnologyFeasibilityObservatory


def test_observatory_reports_all_100_themes_and_never_claims_feasibility(tmp_path):
    store = SQLiteResearchStore(tmp_path / "feasibility.sqlite3")
    report = TechnologyFeasibilityObservatory(store).build()
    assert report["count"] == 100
    assert {item["technology"] for item in report["technologies"]} >= {"timetravel", "spacetime", "cleanenergy", "biodiversity", "animalHealth", "artificialGravity", "medicalNanotechnology", "atmosphericRestoration"}
    assert all(item["technical_feasibility"] == "not_assessed" for item in report["technologies"])
    assert all(item["delivery_readiness"] == "not_assessed" for item in report["technologies"])
    assert report["technical_feasibility_established"] is False
    assert report["delivery_authorized"] is False



def test_observatory_has_labels_for_every_catalogue_entry(tmp_path):
    from ssswet_core.research_journal import TECHNOLOGIES
    from ssswet_core.technology_feasibility import TECHNOLOGY_LABELS
    assert TECHNOLOGIES == set(TECHNOLOGY_LABELS)
    assert TECHNOLOGY_LABELS["blackHoleObservation"]
    assert TECHNOLOGY_LABELS["nuclearBlastResilience"]



def test_observatory_separates_literature_simulation_prototype_and_review(tmp_path):
    store = SQLiteResearchStore(tmp_path / "feasibility-records.sqlite3")
    journal = ResearchJournal(store)
    journal.append(technology="timetravel", event_type="literature_review", title="Published models", summary="Primary literature survey.", classification="literature", evidence_refs=["doi:10.example/2"])
    journal.append(technology="timetravel", event_type="simulation", title="Numerical model", summary="A simulation record.", classification="simulation")
    journal.append(technology="timetravel", event_type="prototype", title="Bench apparatus", summary="A prototype record; not a validated product.", classification="prototype")
    item = TechnologyFeasibilityObservatory(store).build("timetravel")["technologies"][0]
    assert item["classification_counts"] == {"literature": 1, "prototype": 1, "simulation": 1}
    assert item["recorded_maturity"] == "prototype_recorded_not_validated"
    assert item["technical_feasibility"] == "not_assessed"
    assert "test" in item["missing_review_areas"]
    assert "independent_review" in item["missing_review_areas"]


def test_observatory_rejects_unknown_theme(tmp_path):
    import pytest
    store = SQLiteResearchStore(tmp_path / "feasibility-invalid.sqlite3")
    with pytest.raises(ValueError, match="unknown technology"):
        TechnologyFeasibilityObservatory(store).build("unknown")
