from ssswet_core.providers import MultiSourceLiteratureProvider, ProviderResult


class HealthyIndex:
    name = "healthy-index"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            "One bibliographic lead was returned.",
            evidence=("A research paper",),
            uncertainty=1.0,
            source_ids=("https://doi.org/10.example/123",),
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


def test_multi_source_search_reports_when_both_indexes_fail():
    provider = MultiSourceLiteratureProvider()
    provider.providers = (UnstableIndex(), UnstableIndex())

    result = provider.investigate("A harmless research question", "initial")

    assert isinstance(result.summary, str)
    assert result.evidence == ()
    assert "Source failures:" in result.summary
    assert result.uncertainty == 1.0
