import pytest

from ssswet_core.research_observatory import ResearchKnowledgeObservatory


def test_summarizes_existing_records_without_claiming_scientific_validity():
    result = ResearchKnowledgeObservatory.summarize(
        {"nodes": [{"node_id": "h1"}, {"node_id": "s1"}], "edges": [{"relation": "supports"}]},
        {"count": 2, "technologies": [
            {"technology": "alpha", "recorded_maturity": "literature_recorded"},
            {"technology": "beta", "recorded_maturity": "no_project_records"},
        ]},
        {"protocol_count": 3, "run_count": 4, "comparison_count": 1,
         "integrity": {"all_intact": True}},
        {"count": 1, "dossiers": [
            {"dossier_id": "d1", "title": "Dossier", "source_count": 2,
             "run_count": 1, "comparison_count": 1, "event_count": 3,
             "verification_state": "pending"}
        ]},
    )
    assert result["overview"] == {
        "technology_programmes": 2, "knowledge_nodes": 2,
        "recorded_knowledge_relationships": 1, "protocol_versions": 3,
        "research_runs": 4, "recorded_comparisons": 1, "evidence_dossiers": 1,
    }
    assert result["technologies_without_project_records"] == ["beta"]
    assert result["evidence_dossiers"][0]["verification_state"] == "pending"
    assert result["scientific_validity_established"] is False
    assert result["automatic_experiment_execution"] is False


def test_empty_registry_is_reported_as_zero_not_as_failure():
    result = ResearchKnowledgeObservatory.summarize(
        {"nodes": [], "edges": []}, {"count": 0, "technologies": []},
        {"protocol_count": 0, "run_count": 0, "comparison_count": 0, "integrity": {}},
        {"count": 0, "dossiers": []},
    )
    assert all(value == 0 for value in result["overview"].values())
    assert result["technology_record_maturity"] == {}


def test_rejects_invalid_limits():
    class Store:
        pass
    with pytest.raises(ValueError, match="limit"):
        ResearchKnowledgeObservatory().build(Store(), limit=0)
