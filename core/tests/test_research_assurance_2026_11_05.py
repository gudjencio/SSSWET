from __future__ import annotations

import pytest

from ssswet_core.accessibility_audit import audit_html
from ssswet_core.agent_capability_registry import AgentCapabilityRegistry
from ssswet_core.evidence_freshness import assess, score
from ssswet_core.knowledge_graph import trace_paths
from ssswet_core.localization_quality import audit_translation_catalogue, resolve_translation
from ssswet_core.preregistration import amend, freeze, verify_snapshot
from ssswet_core.reproducibility_manifest import build_manifest, verify_manifest
from ssswet_core.source_independence import analyze_sources, group_sources
from ssswet_core.split_leakage import inspect
from ssswet_core.unit_normalization import convert, normalize_measurement


def test_unit_conversion_is_dimension_safe_and_finite():
    assert convert(100, "cm", "m") == pytest.approx(1.0)
    assert convert(2, "h", "min") == pytest.approx(120.0)
    assert normalize_measurement(500, "g", "kg")["dimension"] == "mass"
    with pytest.raises(ValueError, match="incompatible units"):
        convert(1, "m", "s")
    for invalid in (True, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="finite number"):
            convert(invalid, "m", "cm")


def test_source_independence_uses_strong_identity_not_publisher_alone():
    sources = [
        {"id": "a", "doi": "https://doi.org/10.1000/ABC", "publisher": "Journal", "title": "Same"},
        {"id": "b", "doi": "doi:10.1000/abc", "publisher": "Other", "title": "Republished"},
        {"id": "c", "publisher": "Journal", "title": "Different paper one", "domain": "journal.example"},
        {"id": "d", "publisher": "Journal", "title": "Different paper two", "domain": "journal.example"},
        {"id": "e", "publisher": "Journal", "title": "Same"},
    ]
    result = analyze_sources(sources)
    assert result["source_count"] == 5
    assert result["independent_group_count"] == 3
    assert result["duplicate_candidate_count"] == 2
    assert result["domain_or_publisher_alone_used_to_merge"] is False
    assert sorted(len(group) for group in result["group_map"].values()) == [1, 1, 3]
    assert group_sources([{"id": "b", "publisher": "X"}, {"id": "a", "publisher": "X"}])["x"] == ["a", "b"]


def test_source_independence_rejects_duplicate_source_identifiers():
    with pytest.raises(ValueError, match="duplicate source id"):
        analyze_sources([{"id": "same"}, {"id": "same"}])


def test_evidence_freshness_is_deterministic_and_never_auto_excludes():
    stale = assess(
        {"id": "guideline-1", "source_type": "guideline", "published_at": "2024-01-01"},
        as_of="2026-01-01",
    )
    assert stale["status"] == "stale"
    assert stale["freshness_score"] == pytest.approx(0.25, abs=0.002)
    assert stale["review_required"] is True
    assert stale["auto_excluded"] is False
    assert assess({"id": "unknown"}, as_of="2026-01-01")["status"] == "unknown_date"
    assert assess({"id": "future", "published_at": "2027-01-01"}, as_of="2026-01-01")["status"] == "future_dated"
    assert score(30, 30) == pytest.approx(0.5, abs=0.002)


def test_preregistration_amendment_is_auditable_and_tamper_evident():
    plan = {
        "research_question": "Does treatment A change outcome B?",
        "hypotheses": "A changes B",
        "primary_outcome": "B at day 30",
        "method": "Randomized controlled comparison",
        "analysis_plan": "Compare group means",
        "stopping_rule": "Complete planned sample",
    }
    previous = freeze(plan)
    revised = {**plan, "analysis_plan": "Compare adjusted group means"}
    amendment = amend(previous, revised, reason="Pre-specified covariate clarification", actor="reviewer-1",
                      evidence_refs=["protocol-note-1"])
    assert verify_snapshot(previous)["valid"]
    assert amendment["changed_paths"] == ["/analysis_plan"]
    assert amendment["previous_snapshot_preserved"] is True
    assert amendment["scientific_validity_established"] is False
    tampered = {**previous, "snapshot": {**previous["snapshot"], "analysis_plan": "Changed silently"}}
    assert verify_snapshot(tampered)["valid"] is False
    with pytest.raises(ValueError, match="integrity verification"):
        amend(tampered, revised, reason="Correction", actor="reviewer-1")


def test_reproducibility_manifest_is_order_independent_and_tamper_evident():
    kwargs = {
        "protocol_id": "protocol-A",
        "protocol_version": 2,
        "dataset_refs": [{"dataset_id": "D2", "version": 1}, {"dataset_id": "D1", "version": 3}],
        "software_version": "1.4.0",
        "parameters": {"seed": 42, "threshold": 0.8},
        "source_ids": ["s2", "s1", "s1"],
    }
    first = build_manifest(**kwargs)
    second = build_manifest(**{**kwargs, "dataset_refs": list(reversed(kwargs["dataset_refs"])),
                               "source_ids": ["s1", "s2"]})
    assert first["canonical_sha256"] == second["canonical_sha256"]
    assert verify_manifest(first)["valid"]
    tampered = {**first, "parameters": {"seed": 99, "threshold": 0.8}}
    assert verify_manifest(tampered)["valid"] is False
    with pytest.raises(ValueError, match="duplicate dataset reference"):
        build_manifest(**{**kwargs, "dataset_refs": [kwargs["dataset_refs"][0]] * 2})


def test_split_leakage_audit_detects_group_content_and_temporal_overlap():
    result = inspect(
        {
            "train": [
                {"id": "t1", "subject": "p1", "text": "Hello   World", "when": "2024-01-01"},
                {"id": "t2", "subject": "p2", "text": "train only", "when": "2024-01-03"},
            ],
            "test": [
                {"id": "v1", "subject": "p1", "text": " hello world ", "when": "2024-01-02"},
                {"id": "v2", "subject": "p3", "text": "unique", "when": "2024-01-05"},
            ],
        },
        group_field="subject",
        timestamp_field="when",
        temporal_order=["train", "test"],
        content_field="text",
    )
    assert result["identifier_overlap_count"] == 0
    assert result["group_overlap_count"] == 1
    assert result["exact_content_overlap_count"] == 1
    assert result["temporal_order_violation_count"] == 1
    assert result["leakage_detected"] is True
    assert "semantic or near-duplicate" in result["scope"]


def test_split_leakage_legacy_identifier_only_mode_remains_available():
    result = inspect({"train": [{"id": "a"}], "test": [{"id": "b"}]})
    assert result["overlap_count"] == 0
    assert result["leakage_detected"] is False


def test_localization_audit_checks_placeholder_parity_and_fallback_chain():
    source = {"welcome": "Hello {name}", "count": "{count} items"}
    translations = {
        "en": {"welcome": "Hello {name}", "count": "{count} items"},
        "fr": {"welcome": "Bonjour", "count": "{count} éléments"},
    }
    report = audit_translation_catalogue(source, translations)
    assert report["fr"]["placeholder_mismatch_count"] == 1
    assert report["fr"]["placeholder_mismatches"][0]["key"] == "welcome"
    resolved = resolve_translation("count", translations, "fr-CA")
    assert resolved["value"] == "{count} éléments"
    assert resolved["source_language"] == "fr"
    assert resolved["fallback_used"] is True
    assert resolve_translation("missing", translations, "fr-CA")["missing"] is True


def test_accessibility_audit_detects_names_labels_ids_and_heading_order():
    html = """
    <main>
      <h1>Project</h1><h3>Skipped heading</h3>
      <button></button><a href="/help"></a>
      <input id="unlabelled">
      <label for="named">Name</label><input id="named">
      <img src="diagram.png">
      <span id="duplicate"></span><span id="duplicate"></span>
      <p aria-labelledby="not-present">Text</p>
    </main>
    """
    report = audit_html(html)
    rules = {item["rule"] for item in report["issues"]}
    assert {"heading-order", "interactive-name", "form-control-name", "image-alt",
            "duplicate-id", "aria-labelledby-reference"}.issubset(rules)
    assert report["buttons_checked"] == 1
    assert report["automated_audit_is_not_a_full_accessibility_review"] is True


def test_knowledge_graph_path_tracing_is_bounded_and_cycle_safe():
    nodes = [{"node_id": key, "label": key.upper()} for key in ("a", "b", "c", "d")]
    edges = [
        {"source_id": "a", "target_id": "b", "relation": "supports", "confidence": 0.7},
        {"source_id": "b", "target_id": "c", "relation": "derived_from", "confidence": 0.5},
        {"source_id": "a", "target_id": "c", "relation": "related_to", "confidence": 0.2},
        {"source_id": "c", "target_id": "a", "relation": "related_to", "confidence": 0.2},
        {"source_id": "c", "target_id": "d", "relation": "tests", "confidence": 0.8},
    ]
    result = trace_paths(nodes, edges, "a", "c", max_paths=1, direction="outgoing")
    assert result["path_count"] == 1
    assert result["paths"][0]["node_ids"] == ["a", "c"]
    assert result["truncated"] is True
    incoming = trace_paths(nodes, edges, "c", "a", direction="incoming")
    assert incoming["path_count"] >= 1
    filtered = trace_paths(nodes, edges, "a", "c", allowed_relations={"supports"}, max_depth=1)
    assert filtered["path_count"] == 0
    assert filtered["scientific_validity_established"] is False


def test_agent_routing_ranks_full_coverage_and_explains_capacity_exclusions():
    registry = AgentCapabilityRegistry()
    registry.register("agent-a", ["math", "materials"])
    registry.register("agent-b", ["math", "materials"], active_tasks=1, max_concurrent_tasks=2)
    registry.register("agent-c", ["math"])
    registry.register("agent-d", ["math", "materials"], status="busy")
    registry.register("agent-e", ["math", "materials"], active_tasks=1, max_concurrent_tasks=1)
    result = registry.rank_for_task(["math", "materials"], preferred=["materials"])
    assert [item["agent_id"] for item in result["candidates"]] == ["agent-a", "agent-b"]
    assert result["partial_matches"][0]["agent_id"] == "agent-c"
    assert {item["reason"] for item in result["excluded_agents"]} == {"agent_not_available", "capacity_exhausted"}
    assert result["assignment_executed"] is False
    assert "agent-d" in registry.eligible("math")


def test_agent_routing_rejects_empty_or_invalid_requirements():
    registry = AgentCapabilityRegistry()
    registry.register("agent-a", ["math"])
    with pytest.raises(ValueError, match="at least one required capability"):
        registry.rank_for_task([])
    with pytest.raises(ValueError, match="non-empty strings"):
        registry.register("agent-b", [""])
