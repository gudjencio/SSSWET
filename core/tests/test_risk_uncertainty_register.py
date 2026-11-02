import pytest

from ssswet_core.risk_uncertainty_register import ResearchRiskUncertaintyRegister


def test_register_preserves_unknown_assessments_and_avoids_composite_score():
    result = ResearchRiskUncertaintyRegister().analyze([
        {"item_id": "r-1", "title": "Unresolved measurement uncertainty", "category": "measurement"},
        {
            "item_id": "r-2", "title": "Review of regulatory requirements",
            "category": "regulatory", "status": "monitoring",
            "likelihood": "medium", "impact": "high",
            "evidence_refs": ["source-1"], "assumptions": ["Applicable rules may change"],
        },
    ])
    assert result["record_count"] == 2
    assert result["unassessed_count"] == 1
    assert result["records"][0]["likelihood"] is None
    assert result["records"][0]["impact"] is None
    assert result["records"][0]["assessment_complete"] is False
    assert result["composite_risk_score"] is None
    assert result["risk_ranking_generated"] is False
    assert result["work_authorized"] is False


def test_register_reports_categories_and_statuses_without_prioritizing():
    result = ResearchRiskUncertaintyRegister().analyze([
        {"item_id": "a", "title": "A", "category": "safety", "status": "open"},
        {"item_id": "b", "title": "B", "category": "safety", "status": "closed"},
        {"item_id": "c", "title": "C", "category": "ethical"},
    ])
    assert result["category_counts"] == {"ethical": 1, "safety": 2}
    assert result["status_counts"] == {"closed": 1, "open": 1, "unknown": 1}


def test_register_rejects_duplicate_ids_and_unknown_categories():
    register = ResearchRiskUncertaintyRegister()
    with pytest.raises(ValueError, match="duplicate"):
        register.analyze([
            {"item_id": "x", "title": "X", "category": "technical"},
            {"item_id": "x", "title": "X2", "category": "technical"},
        ])
    with pytest.raises(ValueError, match="unsupported category"):
        register.analyze([{"item_id": "x", "title": "X", "category": "classified"}])


def test_register_validates_assessment_and_list_fields():
    register = ResearchRiskUncertaintyRegister()
    with pytest.raises(ValueError, match="likelihood"):
        register.analyze([{
            "item_id": "x", "title": "X", "category": "technical", "likelihood": "certain"
        }])
    with pytest.raises(ValueError, match="evidence_refs"):
        register.analyze([{
            "item_id": "x", "title": "X", "category": "technical", "evidence_refs": "source-1"
        }])


def test_register_rejects_non_object_collections():
    with pytest.raises(ValueError, match="iterable"):
        ResearchRiskUncertaintyRegister().analyze("not a register")
    with pytest.raises(ValueError, match="object"):
        ResearchRiskUncertaintyRegister().analyze([None])
