import pytest

from ssswet_core.multilingual_research_triage import (
    normalize_for_matching, script_profile, tokenize, triage_title,
)
from ssswet_core.source_identity import canonicalize_url, cluster_sources
from ssswet_core.research_query_plan import build_query_plan
from ssswet_core.evidence_applicability import assess_record, assess_records
from ssswet_core.memory_retrieval_evaluation import evaluate_retrieval
from ssswet_core.agent_task_contracts import build_task_contract, validate_completion
from ssswet_core.agent_conflict_register import AgentConflictRegister
from ssswet_core.research_graph_snapshot import build_snapshot, verify_snapshot, diff_snapshots
from ssswet_core.temporal_clock_alignment import build_clock_model, align_events, verify_clock_model
from ssswet_core.rescue_design_assurance import build_assurance_case
from ssswet_core.evidence_freshness import assess as assess_freshness
from ssswet_core.virtual_time_mapping import VirtualTimeMap, TemporalObservation
from ssswet_core.rescue_resource_planner import plan_resources


def test_multilingual_triage_handles_cjk_scripts_and_keeps_original_text():
    title = "信じられない科学の発見"
    result = triage_title(title, "ja")
    assert result["original_text"] == title
    assert result["matched_cue_count"] == 1
    assert result["matched_cues"][0]["language"] == "ja"
    assert result["translation_performed"] is False
    assert result["truth_or_misleadingness_determined"] is False
    assert script_profile(title)["dominant_script"] == "cjk"
    assert "科学" in tokenize("科学研究")
    assert normalize_for_matching("Énergie") == "energie"


def test_multilingual_triage_checks_multiple_languages_without_claiming_language_id():
    result = triage_title("You won't believe this; vous n'allez pas y croire")
    assert {item["language"] for item in result["matched_cues"]} == {"en", "fr"}
    assert result["triage_level"] == "multiple_signals"
    assert result["script_profile"]["language_identification_performed"] is False
    with pytest.raises(ValueError):
        triage_title("hello", "xx")


def test_source_identity_removes_tracking_but_preserves_content_parameters():
    left = canonicalize_url("HTTPS://www.example.org/paper/?utm_source=feed&id=7#section")
    right = canonicalize_url("https://example.org/paper?id=7")
    assert left == right == "https://example.org/paper?id=7"
    result = cluster_sources([
        {"source_id": "a", "doi": "https://doi.org/10.1234/ABC"},
        {"source_id": "b", "doi": "doi:10.1234/abc"},
        {"source_id": "c", "title": "Same title only"},
    ])
    assert result["clusters"][0]["source_ids"] == ["a", "b"]
    assert result["unclustered_source_ids"] == ["c"]
    assert result["records_deleted_or_merged"] is False
    assert result["title_only_matches_used"] is False


def test_source_identity_accepts_arxiv_and_rejects_weak_or_unsafe_urls():
    result = cluster_sources([
        {"source_id": "a", "arxiv_id": "https://arxiv.org/abs/2401.01234v2"},
        {"source_id": "b", "arxiv_id": "2401.01234v2"},
    ])
    assert result["cluster_count"] == 1
    with pytest.raises(ValueError):
        canonicalize_url("javascript:alert(1)")
    with pytest.raises(ValueError):
        cluster_sources([{"source_id": "same"}, {"source_id": "same"}])


def test_query_plan_is_bounded_multilingual_and_permission_aware():
    plan = build_query_plan(
        objective="Review protective materials evidence",
        terms=[{"term": "impact attenuation", "language": "en"},
               {"term": "衝撃吸収材料", "language": "ja"}],
        source_channels=["youtube", "instagram", "scholarly_index"],
        inclusion_terms=["test protocol"], exclusion_terms=["advertisement"],
        date_from="2024-01-01", date_to="2026-12-31", max_queries=1,
    )
    assert plan["query_count"] == 1
    assert plan["truncated"] is True
    assert plan["source_channels"][0]["channel"] == "instagram"
    assert plan["source_channels"][0]["operator_configuration_required"] is True
    assert plan["private_data_accessed"] is False
    assert plan["execution_started"] is False
    assert len(plan["plan_sha256"]) == 64
    with pytest.raises(ValueError):
        build_query_plan(objective="x", terms=[{"term": "x", "language": "en"}],
                         source_channels=["unknown"])


def test_evidence_applicability_uses_explicit_windows_not_implicit_expiry():
    as_of = "2026-11-11T12:00:00+00:00"
    due = assess_record({
        "source_id": "s1", "observed_at": "2026-10-01T00:00:00+00:00",
        "review_after_days": 30,
    }, as_of=as_of)
    outside = assess_record({
        "source_id": "s2", "observed_at": "2026-01-01",
        "valid_until": "2026-06-01",
    }, as_of=as_of)
    no_policy = assess_record({"source_id": "s3", "observed_at": "2026-11-01"}, as_of=as_of)
    assert due["status"] == "review_due"
    assert outside["status"] == "outside_declared_window"
    assert no_policy["status"] == "no_expiry_policy"
    assert no_policy["automatic_expiry"] is False
    assert assess_records([], as_of=as_of)["record_count"] == 0
    with pytest.raises(ValueError):
        assess_record({"source_id": "s4", "observed_at": "2026-11-01T00:00:00"}, as_of=as_of)


def test_memory_retrieval_benchmark_measures_relevance_provenance_latency_and_conflicts():
    result = evaluate_retrieval([{
        "query_id": "q1", "relevant_ids": ["a", "b"],
        "retrieved_ids": ["a", "c"], "contradictory_ids": ["b"],
        "latency_ms": 12.5,
    }], top_k=2, provenance_groups={"a": "g1", "b": "g2"}, storage_bytes=4096)
    report = result["per_query"][0]
    assert report["precision_at_k"] == 0.5
    assert report["recall_at_k"] == 0.5
    assert report["reciprocal_rank"] == 1.0
    assert report["provenance_group_recall_at_k"] == 0.5
    assert report["contradiction_retention_at_k"] == 0.0
    assert result["latency_ms"]["median"] == 12.5
    assert result["storage_bytes"] == 4096
    assert result["retrieval_quality_is_not_model_intelligence"] is True
    with pytest.raises(ValueError):
        evaluate_retrieval([{"relevant_ids": [], "retrieved_ids": ["a", "a"]}])


def test_agent_task_contract_enforces_capabilities_and_review_separation():
    contract = build_task_contract(
        task_id="task-1", objective="Compare published materials tests",
        creator_agent_id="agent-a", assigned_agent_id="agent-b",
        reviewer_agent_id="agent-c", required_capabilities=["materials", "statistics"],
        declared_capabilities=["materials", "statistics", "literature"],
        allowed_source_ids=["paper-1"], max_steps=50, max_runtime_seconds=600,
    )
    result = validate_completion(contract, {
        "output": {"summary": "Comparison", "limitations": ["Small sample"],
                   "evidence_refs": ["paper-1"]},
        "evidence_refs": ["paper-1"],
    })
    assert result["eligible_for_human_review"] is True
    assert result["completion_accepted"] is False
    blocked = validate_completion(contract, {
        "output": {"summary": "Comparison", "limitations": ["Limitations"],
                   "evidence_refs": ["unknown"]},
        "evidence_refs": ["unknown"],
    })
    assert blocked["unapproved_evidence_refs"] == ["unknown"]
    with pytest.raises(ValueError):
        build_task_contract(
            task_id="t", objective="x", creator_agent_id="a",
            assigned_agent_id="b", reviewer_agent_id="b",
            required_capabilities=["science"], declared_capabilities=["science"],
        )
    with pytest.raises(ValueError):
        build_task_contract(
            task_id="t", objective="x", creator_agent_id="a",
            assigned_agent_id="b", reviewer_agent_id="c",
            required_capabilities=["science"], declared_capabilities=["other"],
        )


def test_agent_conflict_register_is_append_only_and_requires_explicit_disclosure():
    register = AgentConflictRegister()
    register.declare(
        declaration_id="conflict-1", agent_id="agent-1", category="collaboration",
        description="Recent co-authorship with a source author",
        campaign_ids=["campaign-a"], source_ids=["paper-1"],
        recorded_at="2026-11-11T09:00:00+00:00",
    )
    declaration = register.history("conflict-1")[0]
    declaration["campaign_ids"].clear()
    assert register.eligibility("agent-1", campaign_id="campaign-a")["eligible_for_assignment"] is False
    history = register.history("conflict-1")
    history[0]["source_ids"].append("mutated")
    assert "mutated" not in register.history("conflict-1")[0]["source_ids"]
    with pytest.raises(ValueError):
        register.review("conflict-1", reviewer_id="agent-1", decision="cleared_after_review",
                        note="Self-review", evidence_refs=["review-1"])
    register.review(
        "conflict-1", reviewer_id="independent-reviewer",
        decision="cleared_after_review", note="Independent disclosure review",
        evidence_refs=["review-record-1"], recorded_at="2026-11-11T10:00:00+00:00",
    )
    result = register.eligibility("agent-1", campaign_id="campaign-a")
    assert result["eligible_for_assignment"] is True
    assert result["independence_certified"] is False
    assert len(register.history("conflict-1")) == 2
    assert register.eligibility("agent-2", campaign_id="campaign-a")["status"] == "no_applicable_declaration"


def test_research_graph_snapshot_is_deterministic_verifiable_and_diffable():
    first = build_snapshot({
        "nodes": [{"node_id": "b", "label": "B"}, {"node_id": "a", "label": "A"}],
        "edges": [{"edge_id": "e1", "source_id": "a", "target_id": "b", "relation": "supports"}],
    })
    reordered = build_snapshot({
        "nodes": [{"node_id": "a", "label": "A"}, {"node_id": "b", "label": "B"}],
        "edges": [{"edge_id": "e1", "source_id": "a", "target_id": "b", "relation": "supports"}],
    })
    assert first["snapshot_sha256"] == reordered["snapshot_sha256"]
    assert verify_snapshot(first)["valid"] is True
    second = build_snapshot({
        "nodes": [{"node_id": "a", "label": "A"}, {"node_id": "c", "label": "C"}],
        "edges": [],
    })
    diff = diff_snapshots(first, second)
    assert diff["nodes"]["added"][0]["node_id"] == "c"
    assert diff["nodes"]["removed"][0]["node_id"] == "b"
    assert diff["edges"]["removed"][0]["edge_id"] == "e1"
    tampered = dict(first)
    tampered["nodes"] = []
    assert verify_snapshot(tampered)["valid"] is False
    with pytest.raises(ValueError):
        diff_snapshots(tampered, second)


def test_temporal_clock_alignment_interpolates_only_inside_session_anchors():
    model = build_clock_model([
        {"session_id": "session-1", "source_id": "camera-a",
         "source_timestamp": "2026-11-11T10:00:00+00:00",
         "reference_timestamp": "2026-11-11T10:01:00+00:00",
         "uncertainty_seconds": 1.0},
        {"session_id": "session-1", "source_id": "camera-a",
         "source_timestamp": "2026-11-11T10:10:00+00:00",
         "reference_timestamp": "2026-11-11T10:11:00+00:00",
         "uncertainty_seconds": 2.0},
    ])
    result = align_events(model, [
        {"event_id": "inside", "session_id": "session-1", "source_id": "camera-a",
         "timestamp": "2026-11-11T10:05:00+00:00", "uncertainty_seconds": 0.0},
        {"event_id": "other-session", "session_id": "session-2", "source_id": "camera-a",
         "timestamp": "2026-11-11T10:05:00+00:00"},
        {"event_id": "outside", "session_id": "session-1", "source_id": "camera-a",
         "timestamp": "2026-11-11T10:20:00+00:00"},
    ])
    assert result["events"][0]["aligned_at"] == "2026-11-11T10:06:00+00:00"
    assert result["events"][0]["uncertainty_seconds"] == 1.5
    assert result["events"][1]["status"] == "different_session_or_source"
    assert result["events"][2]["status"] == "outside_anchor_range"
    assert result["unrecorded_history_recovered"] is False
    assert verify_clock_model(model)["valid"] is True
    tampered = dict(model)
    tampered["anchors"] = list(model["anchors"])
    tampered["anchors"][0] = dict(tampered["anchors"][0], uncertainty_seconds=99)
    assert verify_clock_model(tampered)["valid"] is False
    with pytest.raises(ValueError):
        align_events(tampered, [])
    with pytest.raises(ValueError):
        build_clock_model([
            {"session_id": "s", "source_id": "x", "source_timestamp": "2026-11-11T10:00:00",
             "reference_timestamp": "2026-11-11T10:01:00+00:00"},
            {"session_id": "s", "source_id": "x", "source_timestamp": "2026-11-11T10:10:00+00:00",
             "reference_timestamp": "2026-11-11T10:11:00+00:00"},
        ])


def test_rescue_design_assurance_requires_traceability_and_independent_review():
    base = {
        "design_id": "rescue-vest-1", "design_class": "protective_equipment",
        "design_owner_id": "engineer-1",
        "requirements": [{"requirement_id": "r1", "statement": "Maintain visibility"}],
        "hazards": [{"hazard_id": "h1", "description": "Low visibility",
                     "severity": 4, "likelihood": 2}],
        "controls": [{"control_id": "c1", "hazard_id": "h1",
                      "description": "Reflective panels", "owner_id": "engineer-2"}],
        "verifications": [{"verification_id": "v1", "requirement_id": "r1",
                           "outcome": "pass", "evidence_refs": ["test-report-1"]}],
    }
    blocked = build_assurance_case(**base)
    assert blocked["status"] == "independent_review_required"
    ready = build_assurance_case(**base, independent_reviews=[{
        "review_id": "review-1", "hazard_id": "h1",
        "reviewer_id": "reviewer-1", "evidence_refs": ["review-record-1"],
    }])
    assert ready["status"] == "evidence_ready_for_human_safety_review"
    assert ready["design_approved"] is False
    assert ready["safe_for_use_established"] is False
    failed = dict(base)
    failed["verifications"] = [{"verification_id": "v1", "requirement_id": "r1",
                                "outcome": "fail", "evidence_refs": ["test-report-1"]}]
    assert build_assurance_case(**failed)["status"] == "verification_failures_recorded"
    inconclusive = dict(base)
    inconclusive["verifications"] = [{"verification_id": "v1", "requirement_id": "r1",
                                      "outcome": "inconclusive", "evidence_refs": ["test-report-1"]}]
    assert build_assurance_case(**inconclusive)["status"] == "verification_inconclusive_review_required"
    invalid = dict(base)
    invalid["design_class"] = "weapon"
    with pytest.raises(ValueError):
        build_assurance_case(**invalid)


def test_legacy_freshness_virtual_time_and_rescue_planning_remain_unchanged():
    freshness = assess_freshness(30, 30)
    assert freshness["freshness_band"] == "aging"
    assert freshness["source_claim_modified"] is False

    mapping = VirtualTimeMap()
    mapping.add(TemporalObservation(
        timestamp="2026-11-11T09:00:00+00:00",
        label="Recorded observation", source_id="camera-1",
        uncertainty_seconds=1.0,
    ))
    assert len(mapping.window()) == 1
    assert mapping.export()[0]["source_id"] == "camera-1"

    allocation = plan_resources({"water": 5}, {"water": 3})
    assert allocation["allocations"]["water"] == 3
    assert allocation["shortages"]["water"] == 2
    assert allocation["requires_human_dispatch"] is True



def test_multilingual_triage_profiles_and_tokenizes_japanese_kana_without_kanji():
    assert script_profile("これはすごい")["dominant_script"] == "cjk"
    assert "れは" in tokenize("これはすごい")


def test_source_identity_preserves_order_sensitive_queries_and_ipv6_hosts():
    assert canonicalize_url("https://[2001:db8::1]:443/a") == "https://[2001:db8::1]/a"
    assert canonicalize_url("https://example.org/search?tag=a&tag=b") != canonicalize_url(
        "https://example.org/search?tag=b&tag=a"
    )


def test_evidence_review_interval_is_due_at_exact_boundary_and_empty_batch_validates_time():
    due = assess_record({
        "source_id": "boundary", "observed_at": "2026-10-01T00:00:00+00:00",
        "review_after_days": 30,
    }, as_of="2026-10-31T00:00:00+00:00")
    assert due["status"] == "review_due"
    with pytest.raises(ValueError):
        assess_records([], as_of="2026-11-11T12:00:00")


def test_retrieval_latency_uses_statistical_median_and_nearest_rank_p95():
    result = evaluate_retrieval([
        {"relevant_ids": ["a"], "retrieved_ids": ["a"], "latency_ms": 1},
        {"relevant_ids": ["a"], "retrieved_ids": ["a"], "latency_ms": 2},
        {"relevant_ids": ["a"], "retrieved_ids": ["a"], "latency_ms": 3},
        {"relevant_ids": ["a"], "retrieved_ids": ["a"], "latency_ms": 4},
    ])
    assert result["latency_ms"]["median"] == 2.5
    assert result["latency_ms"]["p95"] == 4.0
    assert result["latency_ms"]["percentile_method"] == "nearest_rank"


def test_agent_completion_cannot_hide_unapproved_output_references():
    contract = build_task_contract(
        task_id="task-refs", objective="Check source references",
        creator_agent_id="creator", assigned_agent_id="worker", reviewer_agent_id="reviewer",
        required_capabilities=["review"], declared_capabilities=["review"],
        allowed_source_ids=["approved-paper"],
    )
    result = validate_completion(contract, {
        "output": {"summary": "Review", "limitations": ["Scope"],
                   "evidence_refs": ["unapproved-paper"]},
        "evidence_refs": ["approved-paper"],
    })
    assert result["unapproved_evidence_refs"] == ["unapproved-paper"]
    assert "evidence_reference_fields_disagree" in result["blockers"]
    assert result["eligible_for_human_review"] is False


def test_conflict_register_return_values_are_isolated_and_timestamps_are_aware():
    register = AgentConflictRegister()
    register.declare(
        declaration_id="conflict-copy", agent_id="agent-x", category="collaboration",
        description="Co-authorship", campaign_ids=["campaign-x"],
        recorded_at="2026-11-11T09:00:00+00:00",
    )
    reviewed = register.review(
        "conflict-copy", reviewer_id="reviewer-x", decision="cleared_after_review",
        note="Independent review", evidence_refs=["review-evidence"],
        recorded_at="2026-11-11T10:00:00+00:00",
    )
    reviewed["campaign_ids"].clear()
    assert register.history("conflict-copy")[1]["campaign_ids"] == ["campaign-x"]
    with pytest.raises(ValueError):
        register.declare(
            declaration_id="bad-time", agent_id="agent-y", category="other",
            description="Disclosure", campaign_ids=["campaign-y"],
            recorded_at="2026-11-11T10:00:00",
        )


def test_graph_snapshot_verifier_rejects_malformed_structure_even_with_a_digest():
    malformed = {"schema_version": 1, "nodes": "not-a-list", "edges": [],
                 "node_count": 0, "edge_count": 0, "source_graph_mutated": False,
                 "snapshot_sha256": "0" * 64}
    assert verify_snapshot(malformed)["valid"] is False


def test_clock_model_verifier_rejects_incomplete_anchor_payload():
    malformed = {"schema_version": 1, "session_id": "s", "source_id": "camera",
                 "anchors": [], "anchor_count": 0, "max_absolute_drift_ppm": 0.0,
                 "drift_is_diagnostic_only": True, "extrapolation_permitted": False,
                 "model_sha256": "0" * 64}
    assert verify_clock_model(malformed)["valid"] is False


def test_rescue_assurance_rejects_control_owner_as_independent_reviewer_and_handles_missing_refs():
    base = {
        "design_id": "rescue-vest-2", "design_class": "protective_equipment",
        "design_owner_id": "engineer-1",
        "requirements": [{"requirement_id": "r1", "statement": "Maintain visibility"}],
        "hazards": [{"hazard_id": "h1", "description": "Low visibility",
                     "severity": 4, "likelihood": 2}],
        "controls": [{"control_id": "c1", "hazard_id": "h1",
                      "description": "Reflective panels", "owner_id": "engineer-2"}],
        "verifications": [{"verification_id": "v1", "requirement_id": "r1",
                           "outcome": "pass", "evidence_refs": ["test-report-1"]}],
    }
    result = build_assurance_case(**base, independent_reviews=[{
        "review_id": "review-1", "hazard_id": "h1",
        "reviewer_id": "engineer-2", "evidence_refs": ["review-record-1"],
    }])
    assert result["status"] == "blocked_invalid_independent_review"
    assert result["critical_hazards_without_independent_review"] == ["h1"]
    assert result["invalid_review_refs"] == ["review-1"]
    malformed = dict(base, verifications=[{"verification_id": "v2", "outcome": "pass",
                                           "evidence_refs": ["report"]}])
    assert build_assurance_case(**malformed)["invalid_verification_refs"] == ["v2"]


def test_query_plan_rejects_oversized_channel_lists_before_normalization():
    with pytest.raises(ValueError):
        build_query_plan(
            objective="Check bounded channel handling",
            terms=[{"term": "materials testing", "language": "en"}],
            source_channels=["youtube"] * 101,
        )
