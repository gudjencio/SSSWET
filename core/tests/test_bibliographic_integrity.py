import pytest

from ssswet_core.bibliographic_integrity import (
    analyze_bibliographic_integrity,
    normalize_doi,
    normalize_title,
)


def test_normalizes_doi_and_title_without_semantic_guessing():
    assert normalize_doi("https://doi.org/10.1000/ABC.1.") == "10.1000/abc.1"
    assert normalize_doi("DOI: 10.1000/ABC.1") == "10.1000/abc.1"
    assert normalize_title("  A Study: OF Batteries! ") == "a study of batteries"


def test_detects_duplicate_doi_and_exact_title_year_as_review_candidates():
    result = analyze_bibliographic_integrity([
        {"source_id": "crossref:1", "doi": "10.1000/EXAMPLE", "title": "Battery Study", "year": 2025},
        {"source_id": "openalex:2", "doi": "https://doi.org/10.1000/example", "title": "Different display title", "year": 2025},
        {"source_id": "repository:3", "title": "Battery Study", "year": 2025},
    ])
    doi_group = next(group for group in result["duplicate_groups"] if group["basis"] == "doi")
    title_group = next(group for group in result["duplicate_groups"] if group["basis"] == "exact_title_and_year")
    assert doi_group["source_ids"] == ["crossref:1", "openalex:2"]
    assert title_group["source_ids"] == ["crossref:1", "repository:3"]
    assert result["automatic_deduplication"] is False
    assert result["scientific_validity_established"] is False


def test_flags_retractions_corrections_preprints_and_missing_metadata():
    result = analyze_bibliographic_integrity([
        {
            "source_id": "retracted", "title": "Withdrawn paper", "doi": "10.1000/r",
            "authors": ["A"], "publication_date": "2024-01-01", "venue": "Journal",
            "publication_status": "retracted", "peer_reviewed": True,
        },
        {
            "source_id": "corrected", "title": "Corrected paper", "doi": "10.1000/c",
            "authors": ["B"], "publication_date": "2023-01-01", "venue": "Journal",
            "type": "correction", "peer_reviewed": True,
        },
        {
            "source_id": "preprint", "title": "Preprint", "doi": "10.1000/p",
            "authors": ["C"], "year": 2026, "venue": "Repository",
            "is_preprint": True,
        },
        {"source_id": "sparse", "title": "Sparse metadata"},
    ])
    by_id = {row["source_id"]: set(row["flags"]) for row in result["records"]}
    assert "retraction_status_signal" in by_id["retracted"]
    assert "correction_or_erratum_signal" in by_id["corrected"]
    assert "preprint_or_posted_content" in by_id["preprint"]
    assert {"doi_missing", "author_metadata_missing", "publication_date_missing",
            "venue_metadata_missing", "peer_review_status_not_established"} <= by_id["sparse"]
    assert result["retraction_signal_count"] == 1
    assert result["correction_signal_count"] == 1
    assert result["preprint_signal_count"] == 1
    assert result["publication_status_verified"] is False


def test_rejects_unbounded_or_malformed_input():
    with pytest.raises(ValueError, match="records"):
        analyze_bibliographic_integrity([{}] * 2001)
    with pytest.raises(ValueError, match="dictionary"):
        analyze_bibliographic_integrity([None])
