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


def test_source_independence_detects_shared_dataset_without_claiming_independence():
    from ssswet_core.sources import analyze_source_independence

    result = analyze_source_independence([
        {"source_id": "paper-a", "dataset_ids": ["dataset-1"], "authors": ["A"]},
        {"source_id": "paper-b", "dataset_ids": ["dataset-1"], "authors": ["B"]},
        {"source_id": "paper-c", "dataset_ids": ["dataset-2"], "authors": ["C"]},
    ])
    assert result["source_count"] == 3
    assert result["pair_count"] == 3
    first = result["pairs"][0]
    assert first["dependency_signals"] == ["shared_dataset"]
    assert first["independence_status"] == "possible_dependency_requires_review"
    assert result["independent_source_count"] is None
    assert result["independence_established"] is False


def test_shared_authors_are_context_not_proof_of_shared_provenance():
    from ssswet_core.sources import analyze_source_independence

    result = analyze_source_independence([
        {"source_id": "paper-a", "authors": ["Researcher A"], "institutions": ["Institute X"]},
        {"source_id": "paper-b", "authors": ["Researcher A"], "institutions": ["Institute X"]},
    ])
    pair = result["pairs"][0]
    assert pair["dependency_signals"] == []
    assert pair["contextual_overlaps"] == ["shared_author", "shared_institution"]
    assert pair["independence_status"] == "not_established"


def test_source_independence_deduplicates_ids_and_normalizes_doi_urls():
    from ssswet_core.sources import analyze_source_independence

    result = analyze_source_independence([
        {"source_id": "paper-a", "doi": "10.1000/example"},
        {"source_id": "paper-b", "doi": "https://doi.org/10.1000/example"},
        {"source_id": "paper-a", "doi": "different"},
    ])
    assert result["source_count"] == 2
    assert result["pairs"][0]["dependency_signals"] == ["same_doi"]
