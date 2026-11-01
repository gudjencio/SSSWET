from ssswet_core.providers import MultiSourceLiteratureProvider, ProviderResult


class FakeProvider:
    name = "fake"

    def __init__(self, result):
        self.result = result

    def investigate(self, objective, strategy):
        return self.result


def test_multi_source_provider_deduplicates_doi_and_preserves_provenance():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (
        FakeProvider(ProviderResult(
            "crossref", evidence=("Paper A | DOI: 10.1234/a", "Paper B | DOI: 10.1234/b"),
            source_ids=("10.1234/a", "10.1234/b"),
        )),
        FakeProvider(ProviderResult(
            "openalex", evidence=("Paper A duplicate", "Paper C"),
            source_ids=("https://doi.org/10.1234/a", "https://openalex.org/W3"),
        )),
    )

    result = provider.investigate("test objective", "literature")

    assert len(result.evidence) == 3
    assert len(result.source_ids) == 3
    assert result.evidence[0].startswith("[fake]")
    assert result.uncertainty == 1.0
    assert "unique bibliographic lead" in result.summary


def test_multi_source_provider_empty_results_remain_unverified():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (
        FakeProvider(ProviderResult("none")),
        FakeProvider(ProviderResult("none")),
    )
    result = provider.investigate("test objective", "literature")
    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
    assert "no usable records" in result.summary
