import math

import pytest

from ssswet_core.memory_intelligence import (
    audit_memory_integrity,
    benchmark_memory_retrieval,
    build_agent_context_packet,
    build_memory_conflict_review,
    compare_retrieval_cases,
    create_memory_snapshot,
    evaluate_retrieval,
    find_duplicate_memory_candidates,
    search_scientific_memory,
    verify_memory_snapshot,
)


def record(version_id, key, topic, statement, **extra):
    return {
        "version_id": version_id,
        "memory_key": key,
        "version_number": extra.pop("version_number", 1),
        "topic": topic,
        "statement": statement,
        "created_at": extra.pop("created_at", "2026-01-01T00:00:00+00:00"),
        "status": extra.pop("status", "candidate"),
        "source_ids": extra.pop("source_ids", []),
        "experiment_ids": extra.pop("experiment_ids", []),
        "graph_node_ids": extra.pop("graph_node_ids", []),
        "is_current": extra.pop("is_current", True),
        **extra,
    }


def test_fielded_search_is_explainable_deterministic_and_keeps_contested_records():
    records = [
        record("wave-1", "wave", "Wave propagation", "Measured speed in water",
               contested_by_graph=True, contested_graph_node_ids=["claim-b"]),
        record("other-1", "other", "Thermal transfer", "Unrelated material research"),
        record("wave-0", "wave", "Wave propagation", "Old candidate",
               is_current=False, version_number=0),
    ]
    result = search_scientific_memory(records, "wave propagation")
    assert [item["version_id"] for item in result["results"]] == ["wave-1"]
    item = result["results"][0]
    assert item["retrieval_method"] == "weighted_fielded_lexical_v1"
    assert item["score_components"]["topic_matches"] == 2
    assert item["contested_by_graph"] is True
    assert item["scientific_validity_established"] is False
    assert result == search_scientific_memory(records, "wave propagation")


def test_search_can_include_history_without_promoting_newer_versions_as_truth():
    records = [
        record("v1", "key", "Wave model", "Initial statement", version_number=1, is_current=False),
        record("v2", "key", "Wave model", "Revised statement", version_number=2, is_current=True),
    ]
    current = search_scientific_memory(records, "wave", include_history=False)
    history = search_scientific_memory(records, "wave", include_history=True)
    assert [item["version_id"] for item in current["results"]] == ["v2"]
    assert {item["version_id"] for item in history["results"]} == {"v1", "v2"}
    assert all(item["scientific_validity_established"] is False for item in history["results"])


def test_search_bounds_records_query_and_result_count():
    with pytest.raises(ValueError, match="500-record"):
        search_scientific_memory([{}] * 501, "wave")
    with pytest.raises(ValueError, match="limit"):
        search_scientific_memory([], "wave", limit=101)
    with pytest.raises(ValueError, match="searchable term"):
        search_scientific_memory([], "!!!")


def test_retrieval_metrics_calculate_precision_recall_mrr_and_ndcg():
    metrics = evaluate_retrieval(["a", "noise", "b"], ["a", "b"], k=3)
    assert metrics["precision_at_k"] == pytest.approx(2 / 3)
    assert metrics["recall_at_k"] == 1.0
    assert metrics["f1_at_k"] == pytest.approx(0.8)
    assert metrics["mrr"] == 1.0
    assert 0.9 < metrics["ndcg_at_k"] < 1.0


def test_benchmark_comparison_detects_improvement_on_labelled_fixture():
    report = compare_retrieval_cases([{
        "candidate_ids": ["relevant-a", "relevant-b"],
        "baseline_ids": ["unrelated", "relevant-a"],
        "relevant_ids": ["relevant-a", "relevant-b"],
    }], k=2)
    assert report["delta"]["mrr"] > 0
    assert report["delta"]["recall_at_k"] > 0
    assert report["candidate"]["ndcg_at_k"] > report["baseline"]["ndcg_at_k"]
    assert report["scientific_validity_established"] is False


def test_latency_benchmark_reports_bounded_500_record_measurements():
    records = [
        record(f"v-{index}", f"key-{index}", f"Wave topic {index}", f"Wave speed measurement {index}")
        for index in range(500)
    ]
    report = benchmark_memory_retrieval(records, ["wave speed"], repeats=2, limit=10)
    assert report["record_count"] == 500
    assert report["sample_count"] == 2
    assert math.isfinite(report["median_latency_ms"])
    assert report["p95_latency_ms"] >= report["median_latency_ms"]


def test_agent_context_packet_keeps_provenance_and_respects_token_budget():
    records = [
        record("v1", "wave", "Wave propagation", "Measured wave speed",
               source_ids=["paper-a"], experiment_ids=["exp-a"],
               graph_node_ids=["claim-a"], provenance_group="lab-a",
               contested_by_graph=True, missing_links={"source_ids": []}),
        record("v2", "thermal", "Thermal transfer", "Heat transfer model"),
    ]
    packet = build_agent_context_packet(records, "wave speed", token_budget=1000)
    assert packet["record_count"] == 1
    assert packet["estimated_tokens"] <= packet["token_budget"]
    assert packet["provenance_retained"] is True
    assert packet["records"][0]["source_ids"] == ["paper-a"]
    assert packet["records"][0]["experiment_ids"] == ["exp-a"]
    assert packet["records"][0]["graph_node_ids"] == ["claim-a"]
    assert packet["records"][0]["contested_by_graph"] is True
    tiny = build_agent_context_packet(records, "wave speed", token_budget=1)
    assert tiny["record_count"] == 0
    assert tiny["omitted_count"] == 1


def test_integrity_audit_reports_missing_links_and_declared_provenance_only():
    records = [record(
        "v1", "key", "Topic", "Statement",
        source_ids=["source-a", "source-missing"],
        experiment_ids=["experiment-missing"],
        graph_node_ids=["node-a", "node-missing"],
    )]
    report = audit_memory_integrity(
        records,
        [{"source_id": "source-a", "provenance_group": "group-a"}],
        [],
        {"nodes": [{"node_id": "node-a"}], "edges": []},
    )
    item = report["records"][0]
    assert item["missing_links"] == {
        "source_ids": ["source-missing"],
        "experiment_ids": ["experiment-missing"],
        "graph_node_ids": ["node-missing"],
    }
    assert item["declared_provenance_group_count"] == 1
    assert report["independence_established"] is False
    assert report["scientific_validity_established"] is False


def test_duplicate_review_finds_candidates_without_merging_versions():
    records = [
        record("a1", "alpha", "Materials", "High strength polymer matrix.", source_ids=["s1"]),
        record("b1", "beta", "Materials", "High strength polymer matrix", source_ids=["s2"]),
        record("a0", "alpha", "Materials", "High strength polymer matrix.", is_current=False),
        record("c1", "gamma", "Materials", "Completely different acoustic method"),
    ]
    report = find_duplicate_memory_candidates(records, threshold=0.8)
    assert report["candidate_count"] == 1
    candidate = report["candidates"][0]
    assert candidate["exact_normalized_match"] is True
    assert candidate["different_source_sets"] is True
    assert candidate["automatic_merge"] is False
    assert candidate["automatic_deletion"] is False


def test_duplicate_review_finds_near_matches_without_calling_them_exact():
    records = [
        record("near-a", "near-a", "Topic", "alpha beta gamma delta epsilon"),
        record("near-b", "near-b", "Topic", "alpha beta gamma delta zeta"),
    ]
    report = find_duplicate_memory_candidates(records, threshold=0.6)
    assert report["candidate_count"] == 1
    assert report["candidates"][0]["exact_normalized_match"] is False
    assert report["candidates"][0]["similarity"] == pytest.approx(4 / 6)


def test_duplicate_review_bounds_retained_candidates_even_for_all_matching_pairs():
    records = [
        record(f"v-{index}", f"key-{index}", "Same topic", "alpha beta gamma delta epsilon")
        for index in range(500)
    ]
    report = find_duplicate_memory_candidates(records, threshold=0.8, limit=5)
    assert report["candidate_count"] == 500 * 499 // 2
    assert len(report["candidates"]) == 5
    assert report["current_record_count"] == 500


def test_duplicate_review_validates_threshold_and_pairwise_bound():
    with pytest.raises(ValueError, match="threshold"):
        find_duplicate_memory_candidates([], threshold=0.2)
    with pytest.raises(ValueError, match="500-record"):
        find_duplicate_memory_candidates([{}] * 501)


def test_conflict_review_includes_current_linked_memory_and_preserves_status():
    records = [
        record("v1", "key", "Claim", "Older statement", is_current=False),
        record("v2", "key", "Claim", "Current statement", graph_node_ids=["claim-a"],
               status="contested"),
    ]
    graph = {
        "nodes": [
            {"node_id": "claim-a", "label": "Original claim"},
            {"node_id": "claim-b", "label": "Conflicting observation"},
        ],
        "edges": [{
            "source_id": "claim-a", "target_id": "claim-b",
            "relation": "contradicts", "note": "Different measured result",
            "confidence": 0.7, "created_at": "2026-02-01T00:00:00+00:00",
        }],
    }
    report = build_memory_conflict_review(records, graph)
    assert report["case_count"] == 1
    case = report["cases"][0]
    assert case["version_id"] == "v2"
    assert case["contradicting_node_label"] == "Conflicting observation"
    assert len(case["review_checklist"]) == 4
    assert case["automatic_status_change"] is False
    assert case["memory_status"] == "contested"


def test_conflict_review_bounds_retained_cases_and_counts_all_reviews():
    records = [
        record(
            f"v-{index}", f"key-{index}", "Claim", f"Statement {index}",
            graph_node_ids=["claim-a"],
            created_at=f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}+00:00",
        )
        for index in range(500)
    ]
    graph = {
        "nodes": [{"node_id": "claim-a", "label": "Claim A"}, {"node_id": "claim-b", "label": "Claim B"}],
        "edges": [{"source_id": "claim-a", "target_id": "claim-b", "relation": "contradicts"}],
    }
    report = build_memory_conflict_review(records, graph, limit=10)
    assert report["case_count"] == 500
    assert len(report["cases"]) == 10
    assert report["cases"][0]["version_id"] == "v-499"


def test_snapshot_is_order_independent_and_detects_record_tampering():
    records = [
        record("v2", "b", "Topic B", "Statement B", version_number=2),
        record("v1", "a", "Topic A", "Statement A"),
    ]
    first = create_memory_snapshot(records)
    second = create_memory_snapshot(list(reversed(records)))
    assert first["digest"] == second["digest"]
    assert verify_memory_snapshot(first)["valid"] is True
    tampered = dict(first)
    tampered["records"] = [dict(item) for item in first["records"]]
    tampered["records"][0]["statement"] = "Changed after export"
    assert verify_memory_snapshot(tampered)["valid"] is False


def test_snapshot_marks_truncation_and_rejects_unsupported_formats():
    snapshot = create_memory_snapshot([], complete=False)
    assert snapshot["truncated_possible"] is True
    assert verify_memory_snapshot(snapshot)["valid"] is True
    invalid = dict(snapshot, schema_version=99)
    with pytest.raises(ValueError, match="unsupported"):
        verify_memory_snapshot(invalid)


def test_snapshot_digest_covers_interpretation_flags():
    snapshot = create_memory_snapshot([])
    tampered = dict(snapshot, scientific_validity_established=True)
    assert verify_memory_snapshot(tampered)["valid"] is False
