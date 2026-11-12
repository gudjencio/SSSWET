import pytest

from ssswet_core.evidence_quality_matrix import EvidenceQualityMatrix


def test_reports_source_metadata_and_review_coverage_without_truth_score():
    dossier = {
        "dossier_id": "d-1",
        "sources": [{
            "source_id": "s-1", "title": "Primary paper", "url": "https://example.org/paper",
            "doi": "10.1000/example", "source_type": "paper", "authors": ["A"],
            "institutions": ["Institute"], "dataset_ids": ["data-1"],
            "related_source_ids": [], "provenance_group": "group-a",
            "metadata": {"peer_reviewed": True, "primary_source": True,
                         "methods_available": True, "publication_date_known": True,
                         "limitations": ["small sample"]},
        }],
        "protocols": [{"protocol_id": "p1"}], "runs": [{"run_id": "r1"}],
        "datasets": [{"dataset_id": "data-1"}], "comparisons": [],
        "peer_reviews": [],
    }
    reviews = [
        {"reviewer_id": "reviewer-a", "verdict": "supports", "conflict_status": "none_declared"},
        {"reviewer_id": "reviewer-b", "verdict": "challenges", "conflict_status": "potential"},
    ]
    result = EvidenceQualityMatrix().analyze(dossier, reviews)
    assert result["source_assessments"][0]["tier"] == "high"
    assert result["review_coverage"]["multiple_positions_recorded"] is True
    assert result["review_coverage"]["independent_review_established"] is False
    assert result["evidence_quality_score"] is None
    assert result["bibliographic_integrity"]["record_count"] == 1
    assert "peer_review_status_not_established" in result["bibliographic_integrity"]["records"][0]["flags"]
    assert result["scientific_validity_established"] is False


def test_missing_source_fields_are_not_filled_in():
    result = EvidenceQualityMatrix().analyze(
        {"dossier_id": "d-2", "sources": [{"source_id": "s-2"}]}, []
    )
    assert result["source_assessments"][0]["assessment"] == "incomplete_source_metadata"
    assert "protocols" in result["missing_areas"]
    assert result["record_counts"]["sources"] == 1


def test_rejects_malformed_input():
    matrix = EvidenceQualityMatrix()
    with pytest.raises(ValueError, match="dossier"):
        matrix.analyze([], [])
    with pytest.raises(ValueError, match="reviews"):
        matrix.analyze({"sources": []}, [None])
