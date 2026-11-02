from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.technology_dossier import TechnologyDossierRegistry
from ssswet_core.technology_catalogue import TECHNOLOGY_CATALOGUE, register_catalogue


def test_catalogue_contains_unique_stable_ids_and_expected_count():
    ids = [item["technology_id"] for item in TECHNOLOGY_CATALOGUE]
    assert len(ids) == 106
    assert len(ids) == len(set(ids))
    assert all(item["domain"] and item["subcategory"] for item in TECHNOLOGY_CATALOGUE)


def test_catalogue_registration_is_idempotent_and_does_not_claim_validation(tmp_path):
    registry = TechnologyDossierRegistry(SQLiteResearchStore(tmp_path / "catalogue.sqlite3"))
    first = register_catalogue(registry)
    second = register_catalogue(registry)
    assert first["created_count"] == 106
    assert second["created_count"] == 0
    assert second["already_registered_count"] == 106
    dossier = registry.get("spacetime")
    assert dossier["current_recorded_state"] == "concept"
    assert dossier["scientific_validity_established"] is False
    assert dossier["events"][-1]["payload"]["research_status"] == "not_assessed"


def test_engine_can_register_full_catalogue(tmp_path):
    from ssswet_core.engine import SSSWETEngine

    engine = SSSWETEngine(SQLiteResearchStore(tmp_path / "engine-catalogue.sqlite3"))
    result = engine.register_technology_catalogue(actor_id="catalogue-bot")
    assert result["catalogue_size"] == 510
    assert result["created_count"] == 510
    assert engine.get_technology_dossier("education")["domain"] == "society"


def test_extended_portfolio_contains_ten_curated_additions():
    from ssswet_core.technology_catalogue_500 import TECHNOLOGY_CATALOGUE as portfolio
    from ssswet_core.technology_catalogue_additions import ADDITIONAL_TECHNOLOGIES

    ids = [item["technology_id"] for item in portfolio]
    assert len(portfolio) == 510
    assert len(ids) == len(set(ids))
    assert len(ADDITIONAL_TECHNOLOGIES) == 10
    virtual_time = next(item for item in portfolio if item["technology_id"] == "virtualTimeTravelMap")
    assert "Unrecorded past events cannot be recovered as observations; retrospective outputs are hypotheses constrained by evidence." in virtual_time["scientific_limitations"]
    assert virtual_time["domain"] == "society"


def test_engine_registers_all_510_research_programmes(tmp_path):
    from ssswet_core.engine import SSSWETEngine

    engine = SSSWETEngine(SQLiteResearchStore(tmp_path / "engine-catalogue-510.sqlite3"))
    result = engine.register_technology_catalogue(actor_id="catalogue-bot")
    assert result["catalogue_size"] == 510
    assert result["created_count"] == 510
    assert engine.get_technology_dossier("virtualTimeTravelMap")["scientific_validity_established"] is False
