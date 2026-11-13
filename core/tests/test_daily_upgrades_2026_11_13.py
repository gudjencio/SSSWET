from __future__ import annotations

import hashlib

import pytest

from ssswet_core.public_media_ingestion import normalize_public_record, normalize_public_batch
from ssswet_core.translation_fidelity import audit_translation
from ssswet_core.claim_evidence_matrix import build_claim_evidence_matrix
from ssswet_core.evidence_change_impact import analyze_change_impact
from ssswet_core.research_checkpoint_bundle import build_checkpoint_bundle, verify_checkpoint_bundle, assess_resume
from ssswet_core.agent_execution_receipts import build_execution_receipt, verify_execution_chain
from ssswet_core.spatiotemporal_uncertainty import compare_observations, analyze_segments
from ssswet_core.rescue_scenario_robustness import evaluate_rescue_scenario
from ssswet_core.protective_design_change_impact import analyze_design_change_impact
from ssswet_core.web_quality_gate import audit_web_root


def test_public_media_intake_is_platform_scoped_and_metadata_only():
    base = {
        "platform": "instagram", "visibility": "public_professional",
        "access_mode": "approved_meta_graph_api", "source_url": "https://www.instagram.com/p/example/",
        "captured_at": "2026-11-13T09:00:00+01:00", "provider_item_id": "media-1",
        "content_type": "post",
        "metadata": {
            "caption": "Public materials research post", "published_at": "2026-11-12T10:00:00Z",
            "like_count": 10, "email": "must-not-return@example.invalid", "private_profile_id": "secret",
            "unapproved_internal_field": "not retained",
        },
    }
    result = normalize_public_record(base)
    assert result["source_id"] == "instagram:media-1"
    assert result["metadata"]["caption"] == "Public materials research post"
    assert "email" not in result["metadata"]
    assert "private_profile_id" in result["sensitive_field_names_flagged"]
    assert "email" in result["discarded_field_names"]
    assert result["private_content_accessed"] is False
    assert result["scientific_evidence_established"] is False
    assert len(result["snapshot_sha256"]) == 64
    with pytest.raises(ValueError):
        normalize_public_record({**base, "visibility": "private"})
    with pytest.raises(ValueError):
        normalize_public_record({**base, "access_mode": "scrape_private_profile"})
    with pytest.raises(ValueError):
        normalize_public_record({**base, "source_url": "http://example.org/post"})


def test_public_media_batch_retains_duplicate_candidates_and_bounds_size():
    item = {
        "platform": "youtube", "visibility": "public", "access_mode": "official_api",
        "source_url": "https://www.youtube.com/watch?v=abc", "captured_at": "2026-11-13T09:00:00Z",
        "source_id": "youtube:abc", "content_type": "video",
        "metadata": {"title": "Public lecture", "duration_seconds": 60, "captions_available": True},
    }
    batch = normalize_public_batch([item, item])
    assert batch["record_count"] == 2
    assert batch["records_discarded"] == 0
    assert batch["duplicate_candidates"][0]["source_id"] == "youtube:abc"
    with pytest.raises(ValueError):
        normalize_public_batch([item] * 501)


def test_translation_fidelity_flags_quantity_unit_and_negation_drift():
    report = audit_translation(
        "The sample was not heated above 5 °C.",
        "L'échantillon a été chauffé au-dessus de 5 °F.",
        source_language="en", target_language="fr",
        term_pairs=[{"source": "sample", "translation": "échantillon"}],
    )
    assert report["review_required"] is True
    assert "quantity_missing_or_changed_in_translation" in report["mismatch_codes"]
    assert "negation_presence_differs" in report["mismatch_codes"]
    assert report["translation_performed"] is False
    clean = audit_translation("The load was 5 kg.", "La charge était de 5 kg.", source_language="en", target_language="fr")
    assert clean["quantities_missing_from_translation"] == []
    assert clean["quantities_added_in_translation"] == []


def test_translation_fidelity_handles_japanese_negation_and_cjk_terms():
    report = audit_translation(
        "The system was not activated.",
        "システムは作動した。",
        source_language="en", target_language="ja",
    )
    assert report["review_required"] is True
    assert report["original_negation_detected"] is True
    assert report["translated_negation_detected"] is False
    with pytest.raises(ValueError):
        audit_translation("not", "no", source_language="xx", target_language="en")


def test_claim_matrix_counts_provenance_groups_and_keeps_counterevidence():
    result = build_claim_evidence_matrix(
        claims=[{"claim_id": "c1", "statement": "Material resists impact"}],
        sources=[
            {"source_id": "s1", "provenance_group": "publisher-a"},
            {"source_id": "s2", "provenance_group": "publisher-a"},
            {"source_id": "s3", "provenance_group": "publisher-b"},
            {"source_id": "s4", "provenance_group": "publisher-c"},
        ],
        links=[
            {"claim_id": "c1", "source_id": "s1", "relation": "supports", "evidence_ref": "e1"},
            {"claim_id": "c1", "source_id": "s2", "relation": "supports", "evidence_ref": "e2"},
            {"claim_id": "c1", "source_id": "s3", "relation": "contradicts", "evidence_ref": "e3"},
            {"claim_id": "c1", "source_id": "s4", "relation": "supports", "state": "withdrawn", "evidence_ref": "e4"},
        ],
    )
    claim = result["claims"][0]
    assert claim["support_independent_group_count"] == 1
    assert claim["contradiction_independent_group_count"] == 1
    assert claim["mixed_support_and_contradiction"] is True
    assert claim["withdrawn_evidence_refs"] == ["e4"]
    assert claim["scientific_truth_score"] is None
    assert result["duplicate_publishers_counted_as_one_group"] is True


def test_claim_matrix_surfaces_unresolved_links_and_rejects_duplicate_link_ids():
    result = build_claim_evidence_matrix(
        [{"claim_id": "c"}], [], [{"claim_id": "c", "source_id": "missing", "relation": "supports", "evidence_ref": "e"}]
    )
    assert result["unresolved_link_count"] == 1
    with pytest.raises(ValueError):
        build_claim_evidence_matrix(
            [{"claim_id": "c"}], [{"source_id": "s"}],
            [{"claim_id": "c", "source_id": "s", "relation": "supports", "evidence_ref": "e"},
             {"claim_id": "c", "source_id": "s", "relation": "supports", "evidence_ref": "e"}],
        )


def test_evidence_change_impact_follows_dependents_and_reports_cycles():
    report = analyze_change_impact([
        {"artifact_id": "paper", "depends_on": []},
        {"artifact_id": "claim", "depends_on": ["paper"]},
        {"artifact_id": "memory", "depends_on": ["claim"]},
        {"artifact_id": "report", "depends_on": ["memory"]},
        {"artifact_id": "cycle-a", "depends_on": ["cycle-b"]},
        {"artifact_id": "cycle-b", "depends_on": ["cycle-a"]},
    ], ["paper"])
    assert [item["artifact_id"] for item in report["downstream_review_required"]] == ["claim", "memory", "report"]
    assert report["dependency_cycle_detected"] is True
    assert report["automatic_retraction"] is False
    assert report["downstream_review_required"][1]["shortest_dependency_path"] == ["paper", "claim", "memory"]


def test_checkpoint_bundle_detects_tampering_and_stale_resume_inputs():
    bundle = build_checkpoint_bundle(
        task_id="task-1", objective="Review public materials studies",
        query_plan_sha256="a" * 64, context_sha256="b" * 64,
        memory_versions={"memory-1": 3}, source_fingerprints={"source-1": "c" * 64},
        decision_ids=["decision-1"], unresolved_questions=["Check sample size"],
        review_blockers=[], budgets={"max_steps": 100, "max_runtime_seconds": 600},
        created_at="2026-11-13T09:00:00Z",
    )
    assert verify_checkpoint_bundle(bundle)["valid"] is True
    current = {
        "query_plan_sha256": "a" * 64, "context_sha256": "b" * 64,
        "memory_versions": {"memory-1": 3}, "source_fingerprints": {"source-1": "c" * 64},
        "review_blockers": [],
    }
    assert assess_resume(bundle, current)["safe_to_resume"] is True
    changed = {**current, "source_fingerprints": {"source-1": "d" * 64}}
    assert assess_resume(bundle, changed)["safe_to_resume"] is False
    tampered = dict(bundle, objective="Altered objective")
    assert verify_checkpoint_bundle(tampered)["valid"] is False


def test_agent_execution_receipts_verify_hashes_and_parent_lineage():
    parent = build_execution_receipt(
        receipt_id="r1", task_id="t1", contract_id="c1", agent_id="a1", role="researcher",
        provider="local", model_label="model-v1", input_refs=[{"ref_id": "source-1", "sha256": "a" * 64}],
        output_sha256="b" * 64, toolchain=[{"name": "python", "version": "3.12"}],
        parent_receipt_ids=[], step_count=2, elapsed_ms=100, max_steps=10, max_runtime_ms=1000,
        execution_status="completed",
    )
    child = build_execution_receipt(
        receipt_id="r2", task_id="t1", contract_id="c1", agent_id="a2", role="reviewer",
        provider="local", model_label="model-v1", input_refs=[{"ref_id": "r1", "sha256": parent["receipt_sha256"]}],
        output_sha256="c" * 64, toolchain=[{"name": "python", "version": "3.12"}],
        parent_receipt_ids=["r1"], step_count=1, elapsed_ms=50, max_steps=10, max_runtime_ms=1000,
        execution_status="completed", risk_flags=["safety"],
    )
    chain = verify_execution_chain([parent, child])
    assert chain["valid"] is True
    assert child["human_review_required"] is True
    assert chain["agent_intelligence_increased"] is False
    altered = dict(child, output_sha256="d" * 64)
    assert verify_execution_chain([parent, altered])["valid"] is False
    with pytest.raises(ValueError):
        build_execution_receipt(
            receipt_id="r3", task_id="t1", contract_id="c1", agent_id="a3", role="worker",
            provider="local", model_label="model-v1", input_refs=[{"ref_id": "s", "sha256": "a" * 64, "api_key": "secret"}],
            output_sha256="a" * 64, toolchain=[], parent_receipt_ids=[], step_count=1, elapsed_ms=1,
            max_steps=2, max_runtime_ms=10, execution_status="completed",
        )


def test_spatiotemporal_uncertainty_propagates_gps_and_clock_bounds():
    first = {
        "event_id": "e1", "session_id": "session-1", "source_id": "gps-a",
        "timestamp": "2026-11-13T10:00:00Z", "time_uncertainty_seconds": 1,
        "latitude": 0, "longitude": 179.999, "location_accuracy_m": 10,
    }
    second = {
        "event_id": "e2", "session_id": "session-1", "source_id": "gps-b",
        "timestamp": "2026-11-13T10:00:10Z", "time_uncertainty_seconds": 1,
        "latitude": 0, "longitude": -179.999, "location_accuracy_m": 20,
    }
    result = compare_observations(first, second)
    assert result["status"] == "bounded"
    assert result["distance_interval_m"]["lower"] <= result["center_distance_m"] <= result["distance_interval_m"]["upper"]
    assert result["speed_interval_mps"]["upper"] is not None
    assert result["event_identity_established"] is False
    overlapping = compare_observations(first, {**second, "timestamp": "2026-11-13T10:00:01Z", "time_uncertainty_seconds": 1})
    assert overlapping["status"] == "time_intervals_overlap"
    assert overlapping["speed_interval_mps"]["upper"] is None
    assert analyze_segments([first, second])["segment_count"] == 1
    with pytest.raises(ValueError):
        compare_observations(first, {**second, "latitude": 91})


def test_spatiotemporal_uncertainty_keeps_sessions_separate():
    first = {
        "session_id": "one", "timestamp": "2026-11-13T10:00:00Z",
        "latitude": 1, "longitude": 1,
    }
    second = {
        "session_id": "two", "timestamp": "2026-11-13T10:00:10Z",
        "latitude": 1, "longitude": 1,
    }
    assert compare_observations(first, second)["status"] == "different_recording_session"


def test_rescue_scenario_stress_test_reports_best_and_worst_case_shortages():
    report = evaluate_rescue_scenario(
        demand_ranges={
            "water": {"min": 100, "expected": 150, "max": 200, "criticality": "essential"},
            "blanket": {"min": 10, "expected": 20, "max": 30, "criticality": "standard"},
        },
        supply_ranges={
            "water": {"min": 80, "expected": 120, "max": 180},
            "blanket": {"min": 25, "expected": 25, "max": 30},
        },
    )
    water = next(item for item in report["resources"] if item["resource"] == "water")
    assert water["best_case_shortage"] == 0
    assert water["expected_shortage"] == 30
    assert water["worst_case_shortage"] == 120
    assert water["critical_shortage_possible"] is True
    assert report["dispatch_performed"] is False
    with pytest.raises(ValueError):
        evaluate_rescue_scenario({"weapon": {"min": 0, "expected": 0, "max": 0}}, {})


def test_protective_design_change_marks_only_dependent_verifications_stale():
    design = {
        "requirements": [{"requirement_id": "r1"}, {"requirement_id": "r2"}],
        "hazards": [
            {"hazard_id": "h1", "severity": 5, "likelihood": 2},
            {"hazard_id": "h2", "severity": 2, "likelihood": 2},
        ],
        "controls": [
            {"control_id": "c1", "hazard_id": "h1"},
            {"control_id": "c2", "hazard_id": "h2"},
        ],
        "verifications": [
            {"verification_id": "v1", "requirement_id": "r1", "control_ids": ["c1"], "evidence_refs": ["e1"]},
            {"verification_id": "v2", "requirement_id": "r2", "control_ids": ["c2"], "evidence_refs": ["e2"]},
        ],
        "independent_reviews": [{"review_id": "review-1", "hazard_id": "h1"}],
    }
    result = analyze_design_change_impact(design, {"changed_hazard_ids": ["h1"]})
    assert result["stale_verification_ids"] == ["v1"]
    assert result["unaffected_verification_ids"] == ["v2"]
    assert result["independent_review_required_for_hazard_ids"] == ["h1"]
    assert result["design_approved"] is False
    assert result["automatic_verification_invalidation"] is False


def test_web_quality_gate_checks_accessibility_assets_and_budgets(tmp_path):
    (tmp_path / "index.html").write_text(
        '<!doctype html><html lang="en"><main><h1>Home</h1><button type="button">Run</button>'
        '<label for="q">Query</label><input id="q"></main><script src="app.js"></script>'
        '<link rel="stylesheet" href="app.css"></html>', encoding="utf-8"
    )
    (tmp_path / "virtual-time-travel.html").write_text(
        '<!doctype html><html lang="en"><main><h1>Map</h1></main></html>', encoding="utf-8"
    )
    (tmp_path / "app.js").write_text("void 0;", encoding="utf-8")
    (tmp_path / "app.css").write_text("body{margin:0}", encoding="utf-8")
    report = audit_web_root(tmp_path)
    assert report["passed"] is True
    assert report["measurements"]["total_javascript_bytes"] == 7
    missing = audit_web_root(tmp_path, pages=("index.html", "virtual-time-travel.html"), budgets={"total_javascript_bytes": 1})
    assert missing["passed"] is False
    (tmp_path / "app.js").unlink()
    broken = audit_web_root(tmp_path)
    assert broken["missing_assets"]
    assert broken["passed"] is False
