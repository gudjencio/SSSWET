import math

from ssswet_core.review_protocol import build_review_synthesis


def test_empty_review_set_is_not_mistaken_for_a_completed_review():
    synthesis = build_review_synthesis([])

    assert synthesis.review_count == 0
    assert synthesis.outcome == "no_review_records"


def test_evidence_without_traceable_sources_remains_provisional():
    synthesis = build_review_synthesis([
        {
            "reviewer_role": "independent_verifier",
            "evidence": ["A non-empty evidence note"],
            "source_ids": [],
            "uncertainty": 0.4,
        }
    ])

    assert synthesis.evidence_lead_count == 1
    assert synthesis.outcome == "evidence_leads_without_traceable_sources"
    assert any("source identifiers" in question for question in synthesis.unresolved_questions)


def test_unstructured_placeholders_do_not_inflate_evidence_or_source_counts():
    synthesis = build_review_synthesis([
        {
            "reviewer_role": " " + ("reviewer" * 30),
            "evidence": ["   ", {"claim": "not a source passage"}, None],
            "source_ids": [123, None, "   "],
            "uncertainty": math.nan,
        }
    ])

    assert synthesis.evidence_lead_count == 0
    assert synthesis.source_ids == ()
    assert synthesis.reviewers[0] == ("reviewer" * 30)[:100]
    assert synthesis.uncertainty_levels == ()
    assert synthesis.outcome == "insufficient_evidence_leads"


def test_traceable_review_is_recorded_but_never_called_scientifically_validated():
    synthesis = build_review_synthesis([
        {
            "reviewer_role": "independent_verifier",
            "evidence": ["The source reports a measured result."],
            "source_ids": ["doi:10.1234/example", "doi:10.1234/example"],
            "uncertainty": 0.2,
        }
    ])

    assert synthesis.outcome == "provisional_review_recorded"
    assert synthesis.source_ids == ("doi:10.1234/example",)
    public_text = synthesis.to_public_text().lower()
    assert "does not establish" in public_text
    assert "clinically validated" in public_text
