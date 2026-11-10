import pytest

from ssswet_core.claim_specification import (
    ClaimSpecification, comparable, validate_claim_history,
)
from ssswet_core.hypothesis_matrix import (
    Hypothesis, Observation, Prediction, evaluate_hypotheses,
)
from ssswet_core.source_lineage import analyze_source_lineage
from ssswet_core.evidence_coverage import build_evidence_coverage
from ssswet_core.blind_review_packet import build_blind_packet
from ssswet_core.reviewer_calibration import evaluate_reviewer_agreement
from ssswet_core.argument_map import validate_argument_map, trace_argument_paths
from ssswet_core.disagreement_analysis import analyze_disagreements
from ssswet_core.reassessment_triggers import compare_review_dependencies
from ssswet_core.deliberation_synthesis import build_deliberation_synthesis


def _claim(**overrides):
    values = dict(
        claim_id="claim-1", version=1,
        statement="Material A reduces measured heat transfer under laboratory conditions.",
        subject="Material A", predicate="heat transfer", value="reduced",
        scope="laboratory", conditions="23 C; 50% RH",
        population="sample coupons", comparator="Material B",
        unit="W/m2K", timeframe="2026-Q3", outcome="heat transfer",
        method="guarded hot plate", evidence_refs=("src-1",),
    )
    values.update(overrides)
    return ClaimSpecification(**values)


def test_claim_contract_comparability_and_gap_free_versioning():
    first = _claim()
    second = _claim(
        version=2, statement="Revised statement with additional limitations.",
        value="reduced with uncertainty", supersedes_version="claim-1@1",
    )
    assert comparable(first, second)
    assert not comparable(first, _claim(unit="W/mK"))
    assert first.fingerprint == _claim().fingerprint
    assert validate_claim_history([second, first])["valid"]
    assert not validate_claim_history([first, _claim(
        version=3, supersedes_version="claim-1@2"
    )])["valid"]
    with pytest.raises(ValueError):
        _claim(version=2)


def test_hypothesis_matrix_preserves_negative_and_untested_results():
    hypothesis = Hypothesis(
        "h1", "Material A reduces heat transfer",
        (
            Prediction("heat transfer", "reduced", "lab", "increased"),
            Prediction("mass loss", "low", "lab", "high"),
        ),
    )
    untouched = Hypothesis(
        "h2", "A competing explanation",
        (Prediction("corrosion", "none", "field"),),
    )
    result = evaluate_hypotheses(
        [hypothesis, untouched],
        [
            Observation("o1", "heat transfer", "reduced", "lab", ("s1",)),
            Observation("o2", "mass loss", "high", "lab", ("s2",)),
        ],
    )
    assert result["hypotheses"][0]["prediction_results"][0]["status"] == "consistent_with_prediction"
    assert result["hypotheses"][0]["prediction_results"][1]["status"] == "inconsistent_with_prediction"
    assert result["hypotheses"][0]["descriptive_outcome"] == "mixed"
    assert result["hypotheses"][1]["descriptive_outcome"] == "not_tested"
    assert result["negative_results_preserved"]
    with pytest.raises(ValueError):
        evaluate_hypotheses([hypothesis, hypothesis], [])


def test_source_lineage_uses_explicit_dependencies_not_publisher_similarity():
    sources = [
        {"source_id": "s1", "dataset_ids": ["d1"], "publisher": "same"},
        {"source_id": "s2", "dataset_ids": ["d1"], "publisher": "same"},
        {"source_id": "s3", "dataset_ids": ["d2"], "publisher": "same"},
        {"source_id": "s4", "parent_source_ids": ["s1"]},
    ]
    result = analyze_source_lineage(sources)
    mapping = result["source_to_cluster"]
    assert mapping["s1"] == mapping["s2"] == mapping["s4"]
    assert mapping["s3"] != mapping["s1"]
    assert result["publisher_similarity_used"] is False
    cyclic = analyze_source_lineage([
        {"source_id": "a", "parent_source_ids": ["b"]},
        {"source_id": "b", "parent_source_ids": ["a"]},
    ])
    assert not cyclic["valid"]
    assert cyclic["cycle_paths"]


def test_evidence_coverage_counts_lineage_groups_not_duplicate_citations():
    sources = [
        {"source_id": "s1", "dataset_ids": ["d-shared"]},
        {"source_id": "s2", "dataset_ids": ["d-shared"]},
        {"source_id": "s3", "dataset_ids": ["d-independent"]},
    ]
    evidence = [
        {"evidence_id": "e1", "claim_id": "c1", "stance": "supports", "source_ids": ["s1"]},
        {"evidence_id": "e2", "claim_id": "c1", "stance": "supports", "source_ids": ["s2"]},
        {"evidence_id": "e3", "claim_id": "c1", "stance": "challenges", "source_ids": ["s3"]},
        {"evidence_id": "e4", "claim_id": "c1", "stance": "inconclusive"},
    ]
    report = build_evidence_coverage([{"claim_id": "c1"}], evidence, sources)
    claim = report["claims"][0]
    assert claim["independent_supporting_group_count"] == 1
    assert claim["independent_challenging_group_count"] == 1
    assert claim["unresolved_provenance_evidence_count"] == 1
    assert "no_supporting_evidence_recorded" not in claim["coverage_gaps"]
    assert "some_evidence_has_unresolved_provenance" in claim["coverage_gaps"]


def test_blind_packet_is_deterministic_and_keeps_unblinding_key_separate():
    documents = [{
        "evidence_id": "e1", "text": "Measured result",
        "author_name": "Researcher A", "organization": "Institute X",
        "source_refs": ["doi:example"], "contact_email": "a@example.invalid",
    }]
    first = build_blind_packet("case-1", documents, salt="a-long-private-salt")
    second = build_blind_packet("case-1", documents, salt="a-long-private-salt")
    packet = first["packet"]["documents"][0]
    assert first["packet_sha256"] == second["packet_sha256"]
    assert packet["author_name"].startswith("masked-")
    assert packet["organization"].startswith("masked-")
    assert packet["evidence_id"] == "e1"
    assert first["unblinding_key_separate_from_packet"]
    assert first["warnings"][0]["unreviewed_identity_fields"] == ["contact_email"]
    assert "Researcher A" not in str(first["packet"])
    with pytest.raises(ValueError):
        build_blind_packet("case", documents, salt="short")


def test_reviewer_calibration_reports_agreement_and_abstentions_separately():
    cases = []
    for index in range(10):
        cases.append({
            "case_id": f"case-{index}", "reference_status": "human_adjudicated",
            "reference": "supports",
            "assessments": [
                {"reviewer_id": "r1", "outcome": "abstains" if index < 2 else "supports"},
                {"reviewer_id": "r2", "outcome": "challenges" if index == 0 else "supports"},
            ],
        })
    report = evaluate_reviewer_agreement(cases)
    first = next(item for item in report["reviewers"] if item["reviewer_id"] == "r1")
    assert first["scored_case_count"] == 8
    assert first["abstention_count"] == 2
    assert first["agreement_with_reference"] == 1.0
    assert first["agreement_wilson_95"] is not None
    assert first["small_sample_warning"] is True
    assert report["reviewer_ranking_produced"] is False
    cases[0]["reference_status"] = "candidate"
    with pytest.raises(ValueError):
        evaluate_reviewer_agreement(cases)


def test_argument_map_finds_evidence_paths_and_rejects_cycles():
    nodes = [
        {"node_id": "e1", "node_type": "evidence"},
        {"node_id": "a1", "node_type": "assumption"},
        {"node_id": "c1", "node_type": "claim"},
        {"node_id": "c2", "node_type": "claim"},
    ]
    edges = [
        {"source_id": "e1", "target_id": "a1", "relation": "derived_from"},
        {"source_id": "a1", "target_id": "c1", "relation": "supports"},
    ]
    report = validate_argument_map(nodes, edges)
    assert report["valid"]
    assert report["claim_nodes_without_evidence_path"] == ["c2"]
    paths = trace_argument_paths(nodes, edges, "e1", "c1")
    assert paths["paths"] == [["e1", "a1", "c1"]]
    cyclic = validate_argument_map(nodes, edges + [
        {"source_id": "c1", "target_id": "a1", "relation": "depends_on"}
    ])
    assert not cyclic["valid"]
    with pytest.raises(ValueError):
        trace_argument_paths(nodes, edges, "missing", "c1")


def test_disagreement_analysis_exposes_method_and_source_overlap():
    reviews = [
        {
            "case_id": "c1", "reviewer_id": "r1", "position": "supports",
            "scope": "lab", "method": "method A", "population": "small samples",
            "source_ids": ["s1", "s2"],
        },
        {
            "case_id": "c1", "reviewer_id": "r2", "position": "challenges",
            "scope": "lab", "method": "method B", "population": "large samples",
            "source_ids": ["s1", "s3"],
        },
    ]
    report = analyze_disagreements(reviews)["cases"][0]
    assert report["position_disagreement"]
    assert set(report["declared_methodological_differences"]) == {"method", "population"}
    assert report["shared_source_ids"] == {"s1": ["r1", "r2"]}
    assert report["automatic_resolution"] is False


def test_reassessment_triggers_detect_added_changed_and_missing_dependencies():
    previous = {
        "source_digests": {"s1": "sha-a"},
        "dataset_digests": {"d1": "sha-d1"},
        "method_versions": {"m1": "v1"},
        "safety_review_versions": {"safety": "v1"},
        "memory_version_ids": {"claim-1": "v1"},
    }
    current = {
        "source_digests": {"s1": "sha-b", "s2": "sha-c"},
        "dataset_digests": {},
        "method_versions": {"m1": "v1"},
        "safety_review_versions": {"safety": "v2"},
        "memory_version_ids": {"claim-1": "v1"},
    }
    report = compare_review_dependencies(previous, current)
    assert report["reassessment_recommended"]
    assert report["changes"]["source_digests"]["changed"] == ["s1"]
    assert report["changes"]["source_digests"]["added"] == ["s2"]
    assert report["changes"]["dataset_digests"]["missing_from_current"] == ["d1"]
    assert report["missing_means_deleted"] is False
    assert report["automatic_review_started"] is False


def test_dissent_preserving_synthesis_is_deterministic_and_never_votes():
    reviews = [
        {
            "review_id": "rev-2", "reviewer_id": "r2", "position": "challenges",
            "rationale": "The dataset is not representative.",
        },
        {
            "review_id": "rev-1", "reviewer_id": "r1", "position": "supports",
            "rationale": "The reported measurement is consistent with the hypothesis.",
        },
    ]
    coverage = {"claims": [{"claim_id": "c1", "coverage_gaps": ["no_challenging_evidence_recorded"]}]}
    disagreement = {"case_count": 1}
    reassessment = {"reassessment_recommended": True}
    first = build_deliberation_synthesis(
        "case-1", "c1", reviews, evidence_coverage=coverage,
        disagreement=disagreement, reassessment=reassessment,
    )
    second = build_deliberation_synthesis(
        "case-1", "c1", list(reversed(reviews)), evidence_coverage=coverage,
        disagreement=disagreement, reassessment=reassessment,
    )
    assert first["synthesis_sha256"] == second["synthesis_sha256"]
    assert first["position_pattern"] == "mixed_recorded_positions"
    assert len(first["reviewer_positions"]) == 2
    assert first["minority_positions_preserved"]
    assert first["majority_vote_used"] is False
    assert first["human_review_required"]
    assert first["scientific_validity_established"] is False


def test_claim_history_rejects_duplicate_versions_and_bad_lineage():
    first = _claim()
    duplicate = _claim()
    with pytest.raises(ValueError):
        validate_claim_history([first, duplicate])
    wrong_parent = _claim(version=2, supersedes_version="claim-9@1")
    assert not validate_claim_history([first, wrong_parent])["valid"]


def test_lineage_rejects_duplicate_ids_and_reports_missing_parent():
    with pytest.raises(ValueError):
        analyze_source_lineage([{"source_id": "s1"}, {"source_id": "s1"}])
    report = analyze_source_lineage([{"source_id": "s1", "parent_source_ids": ["missing"]}])
    assert report["valid"]
    assert report["warnings"] == [{"source_id": "s1", "missing_parent_source_id": "missing"}]


def test_coverage_rejects_unknown_claims_and_invalid_stances():
    with pytest.raises(ValueError):
        build_evidence_coverage(
            [{"claim_id": "c1"}],
            [{"evidence_id": "e1", "claim_id": "unknown", "stance": "supports"}],
        )
    with pytest.raises(ValueError):
        build_evidence_coverage(
            [{"claim_id": "c1"}],
            [{"evidence_id": "e1", "claim_id": "c1", "stance": "verified"}],
        )


def test_argument_map_rejects_missing_endpoints_and_self_edges():
    nodes = [{"node_id": "c1", "node_type": "claim"}]
    missing = validate_argument_map(nodes, [
        {"source_id": "e1", "target_id": "c1", "relation": "supports"}
    ])
    assert not missing["valid"]
    with pytest.raises(ValueError):
        validate_argument_map(nodes, [
            {"source_id": "c1", "target_id": "c1", "relation": "supports"}
        ])


def test_disagreement_rejects_duplicate_reviewer_within_case():
    review = {"case_id": "c1", "reviewer_id": "r1", "position": "mixed"}
    with pytest.raises(ValueError):
        analyze_disagreements([review, review])


def test_synthesis_rejects_duplicate_review_ids_and_bounds_text():
    review = {"review_id": "r1", "reviewer_id": "a", "position": "supports"}
    with pytest.raises(ValueError):
        build_deliberation_synthesis("c", "claim", [review, review])
    with pytest.raises(ValueError):
        build_deliberation_synthesis("c", "claim", [
            {**review, "rationale": "x" * 4001}
        ])


def test_coverage_rejects_duplicate_evidence_ids():
    item = {"evidence_id": "same", "claim_id": "c1", "stance": "supports"}
    with pytest.raises(ValueError):
        build_evidence_coverage([{"claim_id": "c1"}], [item, item])


def test_synthesis_rejects_duplicate_reviewer_identity():
    reviews = [
        {"review_id": "one", "reviewer_id": "r1", "position": "supports"},
        {"review_id": "two", "reviewer_id": "r1", "position": "challenges"},
    ]
    with pytest.raises(ValueError):
        build_deliberation_synthesis("case", "claim", reviews)


def test_observation_source_references_are_bounded_and_typed():
    with pytest.raises(ValueError):
        Observation("o", "x", "y", source_ids=["not-a-tuple"])
    with pytest.raises(ValueError):
        Observation("o", "x", "y", source_ids=tuple(f"s{i}" for i in range(101)))
