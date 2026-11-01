from ssswet_core.providers import (
    CorpusDocument,
    DocumentAnalysisProvider,
    ProviderResult,
)


class StubModelProvider:
    name = "stub-model"

    def __init__(self):
        self.objectives = []

    def investigate(self, objective, strategy):
        self.objectives.append(objective)
        return ProviderResult("MODEL DRAFT: methods appear to be described.", uncertainty=1.0)


def test_document_analysis_passes_retrieved_excerpts_to_model_and_keeps_provenance():
    model = StubModelProvider()
    document = CorpusDocument(
        source_id="pdf:paper.pdf:p0003",
        title="Experimental methods — page 3",
        text="The experiment used a randomized control group and measured temperature.",
    )
    provider = DocumentAnalysisProvider(model, [document])

    result = provider.investigate("Compare experimental methods", "initial")

    assert "randomized control group" in model.objectives[0]
    assert "Do not invent missing methods" in model.objectives[0]
    assert result.source_ids == ("pdf:paper.pdf:p0003",)
    assert "randomized control group" in result.evidence[0]
    assert "MODEL-GENERATED DOCUMENT ANALYSIS" in result.summary
    assert "MODEL DRAFT" in result.summary
    assert result.uncertainty == 1.0


def test_document_analysis_does_not_call_model_when_no_passage_matches():
    model = StubModelProvider()
    provider = DocumentAnalysisProvider(
        model,
        [CorpusDocument("pdf:paper.pdf:p0001", "Unrelated", "Astronomy and galaxies.")],
    )

    result = provider.investigate("Clinical trial randomization", "initial")

    assert model.objectives == []
    assert result.source_ids == ()
    assert "not run" in result.summary
    assert result.uncertainty == 1.0



def test_document_analysis_requests_structured_cross_source_comparison():
    model = StubModelProvider()
    docs = [
        CorpusDocument("paper-a:p1", "Experimental methods", "Experimental methods and control group design."),
        CorpusDocument("paper-b:p2", "Results and limitations", "Results and limitations of the measured experiment."),
    ]
    provider = DocumentAnalysisProvider(model, docs)
    provider.investigate("Compare experimental methods, results and limitations", "comparison")

    prompt = model.objectives[0]
    assert "HYPOTHESES AND OBJECTIVES" in prompt
    assert "METHODS AND EXPERIMENTAL DESIGN" in prompt
    assert "AGREEMENTS BETWEEN SOURCES" in prompt
    assert "DISAGREEMENTS OR CONTRADICTIONS" in prompt
    assert "For every statement, identify its source ID" in prompt
