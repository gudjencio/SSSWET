from ssswet_core.evidence_quality import score_evidence


def test_complete_high_quality_evidence_scores_high():
    result = score_evidence(source_quality=5, method_transparency=5, reproducibility=5, independence=5, provenance_complete=True)
    assert result["score"] == 1.0
    assert not result["review_required"]


def test_missing_provenance_forces_review():
    result = score_evidence(source_quality=5, method_transparency=5, reproducibility=5, independence=5, provenance_complete=False)
    assert result["review_required"]
