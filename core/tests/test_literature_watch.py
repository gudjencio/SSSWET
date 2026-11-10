from ssswet_core.literature_watch import LiteratureWatchService
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.providers import ProviderResult
from ssswet_core.collective_memory import CollectiveMemoryRecord


class FakeProvider:
    name = "fixture-provider"
    def investigate(self, objective, strategy):
        return ProviderResult(
            "Fixture metadata only",
            evidence=(
                "Known paper | Author A | 2024 | Journal | DOI: 10.1234/known | URL: https://example.org/known",
                "A new study of orbital dynamics | Author B | 2025 | Journal | DOI: 10.1234/new | URL: https://example.org/new",
            ),
            source_ids=("10.1234/known", "10.1234/new"),
            bibliographic_records=(
                {"source_id": "10.1234/known", "title": "Known paper", "doi": "10.1234/known", "authors": ["Author A"], "publication_year": 2024, "publication_date": "2024-01-01", "venue": "Journal", "type": "retraction"},
                {"source_id": "10.1234/new", "title": "A new study of orbital dynamics", "doi": "10.1234/new", "authors": ["Author B"], "publication_year": 2025, "publication_date": "2025-02-01", "venue": "Journal", "type": "journal-article"},
            ),
        )


def test_watch_flags_exact_doi_and_new_candidate_without_promoting(tmp_path):
    store = SQLiteResearchStore(tmp_path / "watch.sqlite3")
    store.save_collective_memory(CollectiveMemoryRecord.create(
        "memory-orbit", "orbital dynamics", "Review orbital dynamics models"
    ))
    # Register a known source using a tiny compatible record object.
    class Source:
        source_id = "existing-known"
        doi = "10.1234/known"
        title = "Known paper"
        url = "https://example.org/known"
        source_type = "journal"
        authors = institutions = dataset_ids = related_source_ids = limitations = ()
        provenance_group = retrieved_at = ""
        peer_reviewed = primary_source = methods_available = publication_date_known = False
    store.register_source(Source())

    report = LiteratureWatchService(FakeProvider(), store).run("orbital dynamics")
    assert report.scientific_validity_established is False
    assert report.memory_changed is False
    assert report.campaign_changed is False
    assert report.candidates[0].classification == "possible_duplicate"
    assert report.candidates[0].duplicate_source_ids == ("existing-known",)
    assert report.candidates[1].classification == "candidate_for_review"
    assert report.candidates[1].related_memory_ids == ("memory-orbit",)
    assert report.bibliographic_integrity["record_count"] == 2
    assert report.bibliographic_integrity["retraction_signal_count"] == 1
    assert report.bibliographic_integrity["scientific_validity_established"] is False
    assert store.literature_watch_history()[0]["watch_id"] == report.watch_id


def test_watch_rejects_empty_query(tmp_path):
    import pytest
    store = SQLiteResearchStore(tmp_path / "empty.sqlite3")
    with pytest.raises(ValueError, match="non-empty"):
        LiteratureWatchService(FakeProvider(), store).run("  ")
