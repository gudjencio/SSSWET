from ssswet_core.providers import CorpusDocument, LocalCorpusProvider


def test_local_corpus_returns_traceable_sources_without_claiming_verification():
    provider = LocalCorpusProvider([
        CorpusDocument(
            "paper-physics-01",
            "Introductory physics",
            "A study of wave propagation and electromagnetic fields.",
            "https://example.org/physics",
        ),
        CorpusDocument(
            "paper-biology-02",
            "Cell biology",
            "A study of cell membranes and biological processes.",
        ),
    ])
    result = provider.investigate("wave propagation electromagnetic fields", "search")

    assert result.source_ids == ("paper-physics-01",)
    assert "paper-physics-01" in result.evidence[0]
    assert result.uncertainty == 1.0
    assert "not scientific validation" in result.summary


def test_local_corpus_returns_no_evidence_when_nothing_matches():
    provider = LocalCorpusProvider([
        CorpusDocument("doc-1", "Ocean currents", "Marine currents and tides.")
    ])
    result = provider.investigate("quantum computing compiler", "search")
    assert result.evidence == ()
    assert result.source_ids == ()
    assert result.uncertainty == 1.0
