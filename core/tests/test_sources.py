from ssswet_core.sources import SourceQualityAssessor, SourceRecord


def test_source_rubric_is_transparent_and_bounded():
    source = SourceRecord(
        source_id="paper-1",
        title="Example research paper",
        url="https://example.org/paper",
        peer_reviewed=True,
        primary_source=True,
        methods_available=True,
        publication_date_known=True,
    )
    assessment = SourceQualityAssessor().assess(source)
    assert assessment.score == 0.9
    assert assessment.tier == "high"
    assert "peer_reviewed" in assessment.factors
    assert "not proof" in assessment.warning


def test_source_limitations_reduce_quality_score_without_rejecting_source():
    source = SourceRecord(
        source_id="report-1",
        title="Incomplete report",
        limitations=("small sample", "methods missing"),
    )
    assessment = SourceQualityAssessor().assess(source)
    assert assessment.score == 0.0
    assert assessment.tier == "limited"
