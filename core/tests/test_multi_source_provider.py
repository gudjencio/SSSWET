from ssswet_core.providers import MultiSourceLiteratureProvider, ProviderResult


class HealthyIndex:
    name = "healthy-index"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            "One bibliographic lead was returned.",
            evidence=("A research paper",),
            uncertainty=1.0,
            source_ids=("https://doi.org/10.example/123",),
            bibliographic_records=({"source_id": "https://doi.org/10.example/123", "title": "A research paper", "doi": "10.example/123", "publication_year": 2025, "authors": ["A. Researcher"], "venue": "Example Journal", "type": "journal-article"},),
        )


class UnstableIndex:
    name = "unstable-index"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        raise RuntimeError("simulated upstream failure")


def test_multi_source_search_keeps_results_when_one_index_fails():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (UnstableIndex(), HealthyIndex())

    result = provider.investigate("A harmless research question", "initial")

    assert isinstance(result.summary, str)
    assert result.evidence == ("[healthy-index] A research paper",)
    assert "unstable-index: RuntimeError" in result.summary
    assert result.uncertainty == 1.0
    assert len(result.bibliographic_records) == 1
    assert result.bibliographic_records[0]["title"] == "A research paper"


def test_multi_source_search_reports_when_both_indexes_fail():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (UnstableIndex(), UnstableIndex())

    result = provider.investigate("A harmless research question", "initial")

    assert isinstance(result.summary, str)
    assert result.evidence == ()
    assert "Source failures:" in result.summary
    assert result.uncertainty == 1.0


class SecondHealthyIndex:
    name = "second-healthy-index"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            "The same DOI was independently indexed.",
            evidence=("A research paper from the second index",),
            uncertainty=1.0,
            source_ids=("https://doi.org/10.example/123",),
            bibliographic_records=({
                "source_id": "https://doi.org/10.example/123",
                "title": "A research paper", "doi": "https://doi.org/10.example/123",
                "publication_date": "2025-02-03", "metadata_provider": "second-healthy-index",
            },),
        )


def test_multi_source_duplicate_doi_retains_both_index_provenances():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (HealthyIndex(), SecondHealthyIndex())

    result = provider.investigate("A harmless research question", "initial")

    assert len(result.evidence) == 1
    assert len(result.bibliographic_records) == 1
    record = result.bibliographic_records[0]
    assert record["metadata_providers"] == ["healthy-index", "second-healthy-index"]
    assert record["provider_source_ids"] == ["https://doi.org/10.example/123"]
    assert record["publication_date"] == "2025-02-03"
