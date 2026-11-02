from ssswet_core.evidence_gap_analysis import EvidenceGapAnalyzer


def sample_dossier():
    return {
        "dossier_id": "dossier-gap",
        "sources": [{"source_id": "source-1"}],
        "runs": [{"run_id": "run-1"}],
        "datasets": [{"dataset_id": "dataset-1"}],
        "protocols": [{"protocol_id": "protocol-1", "version": 1}],
        "comparisons": [{"comparison_id": "comparison-1"}],
    }


def test_reports_missing_record_categories_without_claiming_evidence_absence():
    dossier = sample_dossier()
    dossier["sources"] = []
    dossier["runs"] = []
    report = EvidenceGapAnalyzer().analyze(dossier)
    categories = {item["category"] for item in report["gaps"]}
    assert {"no_sources_in_dossier", "no_run_records"} <= categories
    assert report["scientific_validity_established"] is False
    assert "do not prove" in report["notice"]


def test_identifies_competing_positions_and_unmatched_review_references():
    reviews = [
        {"verdict": "supports", "evidence_refs": ["source-1"]},
        {"verdict": "challenges", "evidence_refs": ["external-record-9"]},
    ]
    report = EvidenceGapAnalyzer().analyze(sample_dossier(), reviews)
    categories = {item["category"] for item in report["gaps"]}
    assert "competing_review_positions" in categories
    assert "unmatched_review_references" in categories
    assert report["unmatched_review_reference_ids"] == ["external-record-9"]
    assert report["automatic_adjudication"] is False


def test_matching_review_references_are_not_flagged():
    reviews = [{"verdict": "supports", "evidence_refs": ["source-1", "run-1"]}]
    report = EvidenceGapAnalyzer().analyze(sample_dossier(), reviews)
    assert "unmatched_review_references" not in {
        item["category"] for item in report["gaps"]
    }


def test_rejects_malformed_inputs():
    import pytest
    analyzer = EvidenceGapAnalyzer()
    with pytest.raises(ValueError, match="dossier"):
        analyzer.analyze([])
    with pytest.raises(ValueError, match="reviews"):
        analyzer.analyze(sample_dossier(), {})
