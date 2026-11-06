from ssswet_core.accessibility_audit import audit_html
from ssswet_core.agent_capability_registry import AgentCapabilityRegistry
from ssswet_core.dataset_registry import governance_issues
from ssswet_core.evidence_quality_matrix import EvidenceQualityMatrix
from ssswet_core.localization_quality import audit_translation_catalogue
from ssswet_core.preregistration import compare_frozen, freeze, record_deviation, verify_frozen
from ssswet_core.provenance_graph import build as build_provenance_graph
from ssswet_core.reproducibility_manifest import build_manifest, compare_manifests, verify_manifest
from ssswet_core.rescue_resource_planner import plan_multiple_requests, plan_resources
from ssswet_core.virtual_time_mapping import TemporalObservation, VirtualTimeMap


def test_provenance_graph_preserves_legacy_keys_and_reports_deterministic_dag_order():
    report = build_provenance_graph([{"id": "c"}, {"id": "a"}, {"id": "b"}], [("a", "b"), ("b", "c")])
    assert report["roots"] == ["a"]
    assert report["edges"] == [("a", "b"), ("b", "c")]
    assert report["invalid_edge_count"] == 0
    assert report["topological_order"] == ["a", "b", "c"]
    assert report["leaves"] == ["c"]
    assert report["component_count"] == 1
    assert report["graph_integrity_complete"] is True


def test_provenance_graph_surfaces_cycles_duplicates_and_broken_links():
    report = build_provenance_graph(
        [{"id": "a"}, {"id": "b"}, {"id": "a"}, {}],
        [("a", "b"), ("b", "a"), ("missing", "a"), ("a", "a"), ("a", "b")],
    )
    assert report["cycle_node_ids"] == ["a", "b"]
    assert report["is_acyclic"] is False
    assert report["invalid_edge_count"] == 2
    assert report["duplicate_edge_count"] == 1
    assert report["duplicate_node_ids"] == ["a"]
    assert report["invalid_node_count"] == 1
    assert report["topological_order"] == []
    assert report["graph_integrity_complete"] is False


def test_provenance_graph_separates_cycle_members_from_downstream_blocked_nodes():
    report = build_provenance_graph([{"id": "a"}, {"id": "b"}, {"id": "c"}], [("a", "b"), ("b", "a"), ("b", "c")])
    assert report["cycle_node_ids"] == ["a", "b"]
    assert report["blocked_by_cycles"] == ["c"]


def test_provenance_graph_does_not_mistake_cross_edges_for_cycles():
    report = build_provenance_graph(
        [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        [("a", "b"), ("a", "c"), ("b", "c")],
    )
    assert report["is_acyclic"] is True
    assert report["cycle_node_ids"] == []
    assert report["topological_order"] == ["a", "b", "c"]


def test_agent_capability_matching_is_ranked_versioned_and_non_executing():
    registry = AgentCapabilityRegistry()
    registry.register("agent-b", ["materials", "simulation"])
    registry.register("agent-a", ["materials", "simulation", "measurement"])
    registry.register("agent-a", ["materials", "measurement"])
    report = registry.recommend(["materials", "simulation", "measurement"], forbidden=["weapons"])
    assert report["matches"][0]["agent_id"] == "agent-a"
    assert report["matches"][0]["registry_version"] == 2
    assert report["matches"][0]["missing_capabilities"] == ["simulation"]
    assert report["execution_not_started"] is True
    assert [item["version"] for item in registry.history()] == [1, 1, 2]


def test_agent_capability_forbidden_scope_excludes_candidate():
    registry = AgentCapabilityRegistry()
    registry.register("agent-safe", ["rescue", "materials"])
    registry.register("agent-excluded", ["rescue", "weapons"])
    report = registry.recommend(["rescue"], forbidden=["weapons"])
    assert [item["agent_id"] for item in report["matches"]] == ["agent-safe"]
    assert report["excluded_agents"][0]["agent_id"] == "agent-excluded"


def test_dataset_governance_flags_missing_controls_and_accepts_declared_review_metadata():
    legacy = {"license": "CC-BY-4.0", "privacy_classification": "unspecified",
              "consent_status": "not_recorded", "retention_policy": "not_recorded", "access_scope": "restricted"}
    flags = governance_issues(legacy)
    assert "privacy_classification_not_recorded" in flags
    assert "consent_status_not_recorded" in flags
    assert "retention_policy_not_recorded" in flags
    reviewed = {"license": "CC-BY-4.0", "privacy_classification": "personal_data",
                "consent_status": "documented", "retention_policy": "Delete or review after 12 months",
                "access_scope": "restricted"}
    assert governance_issues(reviewed) == []


def test_dataset_governance_flags_public_personal_data_and_withdrawn_consent():
    flags = governance_issues({"license": "unknown", "privacy_classification": "sensitive_data",
                               "consent_status": "withdrawn", "retention_policy": "not_recorded",
                               "access_scope": "public"})
    assert "consent_withdrawn" in flags
    assert "public_access_for_personal_data" in flags
    assert "license_terms_not_recorded" in flags


def _plan():
    return {
        "research_question": "Does method A reduce measurement error?",
        "hypotheses": "Method A reduces error under the stated conditions.",
        "primary_outcome": "Absolute measurement error",
        "method": "Paired controlled comparison",
        "analysis_plan": "Compare paired differences with a declared interval.",
        "stopping_rule": "Stop after the preregistered sample size or safety hold.",
        "secondary_outcomes": ["duration"],
    }


def test_preregistration_detects_tampering_and_records_explicit_deviations():
    original = _plan()
    frozen = freeze(original)
    assert verify_frozen(frozen)["valid"] is True
    revised = dict(original, primary_outcome="Relative measurement error")
    comparison = compare_frozen(frozen, revised)
    assert comparison["changed_field_count"] == 1
    deviation = record_deviation(frozen, revised, reason="Instrument calibration changed before data collection.",
                                 reviewer_id="reviewer-1")
    assert deviation["state"] == "recorded_pending_review"
    assert deviation["approval_granted"] is False
    assert deviation["base_fingerprint"] == frozen["fingerprint"]
    assert frozen["snapshot"]["primary_outcome"] == original["primary_outcome"]
    tampered = dict(frozen, snapshot=dict(frozen["snapshot"], stopping_rule="changed silently"))
    assert verify_frozen(tampered)["valid"] is False


def test_reproducibility_manifest_verifies_environment_and_nested_differences():
    manifest = build_manifest(
        protocol_id="protocol-1", protocol_version=2,
        dataset_refs=[{"dataset_id": "dataset-1", "version": 3, "sha256": "a" * 64}],
        software_version="SSSWET 1.1", parameters={"temperature": 21.5},
        source_ids=["source-b", "source-a", "source-a"],
        environment={"python": "3.12", "platform": "linux"},
        random_seed=42, input_checksums={"raw.csv": "b" * 64},
    )
    assert verify_manifest(manifest)["valid"] is True
    changed = dict(manifest, parameters={"temperature": 22.0})
    assert verify_manifest(changed)["valid"] is False
    diff = compare_manifests(manifest, changed)
    assert any(item["path"] == "parameters.temperature" for item in diff["changed_paths"])
    assert manifest["source_ids"] == ["source-a", "source-b"]


def test_virtual_time_map_preserves_multiple_observations_and_groups_overlapping_uncertainty():
    mapping = VirtualTimeMap()
    mapping.add(TemporalObservation("2026-01-01T00:00:00Z", "first", "source-a", 10))
    mapping.add(TemporalObservation("2026-01-01T00:00:05+00:00", "second", "source-b", 10))
    mapping.add(TemporalObservation("2026-01-01T00:00:00Z", "another note", "source-a", 10))
    clusters = mapping.temporal_clusters()
    assert len(mapping.export()) == 3
    assert clusters["observation_count"] == 3
    assert len(clusters["clusters"]) == 1
    assert clusters["clusters"][0]["possible_temporal_overlap"] is True
    assert clusters["clusters"][0]["event_identity_established"] is False


def test_virtual_time_map_keeps_naive_and_timezone_aware_clocks_separate():
    mapping = VirtualTimeMap()
    mapping.add(TemporalObservation("2026-01-01T12:00:00", "naive", "source-a", 0))
    mapping.add(TemporalObservation("2026-01-01T12:00:00Z", "aware", "source-b", 0))
    report = mapping.temporal_clusters()
    assert {item["time_basis"] for item in report["clusters"]} == {"aware", "naive"}
    assert report["time_basis_groups_separated"] is True


def test_rescue_planner_prioritizes_urgent_requests_and_fairly_splits_equal_priority_stock():
    report = plan_multiple_requests(
        [{"request_id": "urgent", "priority": 5, "needs": {"water": 5}},
         {"request_id": "lower", "priority": 1, "needs": {"water": 5}}],
        {"water": 6},
    )
    results = {item["request_id"]: item for item in report["requests"]}
    assert results["urgent"]["allocations"]["water"] == 5
    assert results["lower"]["allocations"]["water"] == 1
    assert report["requires_human_dispatch"] is True
    assert report["medical_or_evacuation_decisions_not_automated"] is True
    fair = plan_multiple_requests(
        [{"request_id": "a", "priority": 3, "needs": {"blanket": 5}},
         {"request_id": "b", "priority": 3, "needs": {"blanket": 5}}],
        {"blanket": 5},
    )
    split = {item["request_id"]: item["allocations"]["blanket"] for item in fair["requests"]}
    assert split == {"a": 3, "b": 2}


def test_rescue_planner_rejects_ambiguous_inventory_quantities():
    try:
        plan_resources({"water": 1}, {"water": True})
    except ValueError as exc:
        assert "integers" in str(exc)
    else:
        raise AssertionError("boolean stock must not be treated as one unit")


def test_accessibility_audit_detects_structural_and_name_issues():
    html = ('<html lang="en"><body><main><h1>Title</h1><h3>Skipped level</h3>'
            '<img src="map.png"><button aria-hidden="true"></button>'
            '<input id="query"><input id="query" aria-labelledby="missing-label">'
            '</main></body></html>')
    report = audit_html(html)
    rules = {item["rule"] for item in report["issues"]}
    assert {"image-alt", "heading-order", "button-name", "aria-hidden-focusable",
            "duplicate-id", "form-control-name", "aria-labelledby-reference"} <= rules
    assert report["automated_audit_is_not_a_full_accessibility_review"] is True


def test_accessibility_audit_accepts_named_controls_and_decorative_images():
    html = ('<html lang="fr"><body><main><h1>Carte</h1>'
            '<label for="query">Recherche</label><input id="query">'
            '<button>Envoyer</button><a href="/help">Aide</a><img src="decorative.svg" alt="">'
            '</main></body></html>')
    report = audit_html(html)
    assert report["issue_count"] == 0


def test_accessibility_audit_flags_missing_language_only_for_full_documents():
    report = audit_html("<html><body><main></main></body></html>")
    assert "document-lang" in {item["rule"] for item in report["issues"]}
    fragment = audit_html("<main><img src='x'></main>")
    assert fragment["issue_count"] == 1
    assert fragment["document_fragment"] is True


def test_localization_audit_checks_coverage_placeholders_extras_and_rtl():
    source = {"hello": "Hello {name}", "count": "Count %s", "save": "Save"}
    translations = {
        "en": dict(source),
        "fr": {"hello": "Bonjour {user}", "count": "Nombre %d", "save": "Save", "extra": "En plus"},
        "ar": {"hello": "مرحبا {name}", "count": "العدد %s", "save": "حفظ"},
    }
    report = audit_translation_catalogue(source, translations)
    assert report["fr"]["placeholder_mismatches"]
    assert report["fr"]["extra_keys"] == ["extra"]
    assert report["fr"]["possibly_untranslated"] == ["save"]
    assert report["ar"]["direction"] == "rtl"
    assert report["en"]["coverage"] == 1.0
    assert report["_meta"]["translation_quality_human_review_required"] is True


def test_evidence_matrix_audits_declared_provenance_links_and_repeated_reviewer_ids():
    dossier = {
        "dossier_id": "dossier-1",
        "sources": [{"source_id": "s1", "title": "Paper", "url": "https://example.org/paper",
                     "source_type": "paper", "related_source_ids": ["missing-source"], "dataset_ids": ["d1"]}],
        "protocols": [{"protocol_id": "p1", "source_ids": ["s1"]}],
        "runs": [{"run_id": "r1", "protocol_id": "p1", "source_ids": ["s1"], "dataset_ids": ["d1"]}],
        "datasets": [{"dataset_id": "d1", "source_ids": ["s1"]}],
        "comparisons": [{"comparison_id": "c1", "left_run_id": "r1", "right_run_id": "missing-run"}],
    }
    reviews = [
        {"reviewer_id": "reviewer-a", "verdict": "supports", "conflict_status": "none_declared"},
        {"reviewer_id": "reviewer-a", "verdict": "challenges", "conflict_status": "potential"},
        {"reviewer_id": None, "verdict": "unknown"},
    ]
    report = EvidenceQualityMatrix().analyze(dossier, reviews)
    provenance = report["provenance_integrity"]
    assert provenance["declared_reference_count"] == 9
    assert provenance["unresolved_reference_count"] == 2
    assert provenance["provenance_completeness"] == 7 / 9
    assert report["review_coverage"]["repeated_reviewer_id_count"] == 1
    assert report["review_coverage"]["missing_reviewer_id_count"] == 1
    assert report["review_coverage"]["conflict_declarations_complete"] is False
    assert report["scientific_validity_established"] is False
