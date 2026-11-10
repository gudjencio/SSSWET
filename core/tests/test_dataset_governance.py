from copy import deepcopy

import pytest

from ssswet_core.dataset_governance import (
    assess_consent_scope,
    assess_license_use,
    audit_field_release_policy,
    audit_group_time_splits,
    audit_lineage_graph,
    build_release_manifest,
    build_release_readiness,
    compare_dataset_schemas,
    plan_retention_reviews,
    screen_aggregate_disclosure,
    verify_release_manifest,
)


def test_license_policy_requires_explicit_human_approval_and_requested_use():
    policy = {
        "license_id": "CC-BY-4.0",
        "review_status": "approved",
        "reviewer_ref": "review:42",
        "reviewed_at": "2026-11-10T08:00:00Z",
        "permitted_uses": ["internal_research", "public_release"],
        "prohibited_uses": ["commercial_reuse"],
    }
    assert assess_license_use(policy, "public_release")["policy_gate_passed"] is True
    blocked = assess_license_use(policy, "commercial_reuse")
    assert blocked["policy_gate_passed"] is False
    assert "requested_use_explicitly_prohibited" in blocked["reasons"]
    policy["review_status"] = "pending"
    assert assess_license_use(policy, "public_release")["policy_gate_passed"] is False
    policy["review_status"] = "approved"
    policy["reviewed_at"] = "2026-11-10T08:00:00"
    assert assess_license_use(policy, "public_release")["policy_gate_passed"] is False
    assert assess_license_use(policy, "public_release")["legal_interpretation_performed"] is False


def test_license_policy_rejects_duplicates_and_unbounded_values():
    policy = {"license_id": "LicenseRef-X", "review_status": "approved", "reviewer_ref": "r1",
              "reviewed_at": "2026-01-01T00:00:00Z", "permitted_uses": ["research", "research"]}
    with pytest.raises(ValueError, match="duplicates"):
        assess_license_use(policy, "research")
    clean_policy = {**policy, "permitted_uses": ["research"]}
    with pytest.raises(ValueError, match="requested_use"):
        assess_license_use(clean_policy, " ")


def test_consent_scope_blocks_withdrawn_pending_and_unapproved_sharing():
    base = {"status": "documented", "permitted_purposes": ["rescue_research"], "sharing_authorized": False,
            "consent_evidence_ref": "consent:record-12", "reviewer_ref": "review:consent-4"}
    assert assess_consent_scope(base, "rescue_research")["policy_gate_passed"] is True
    assert assess_consent_scope(base, "public_release")["policy_gate_passed"] is False
    assert assess_consent_scope(base, "rescue_research", sharing_requested=True)["policy_gate_passed"] is False
    for status in ("pending", "withdrawn", "not_recorded"):
        assert assess_consent_scope({**base, "status": status}, "rescue_research")["policy_gate_passed"] is False
    not_required = {"status": "not_required", "permitted_purposes": ["rescue_research"],
                    "not_required_reason_ref": "ethics:na-1", "reviewer_ref": "reviewer:2"}
    assert assess_consent_scope(not_required, "rescue_research")["policy_gate_passed"] is True
    not_required.pop("reviewer_ref")
    assert assess_consent_scope(not_required, "rescue_research")["policy_gate_passed"] is False


def test_field_release_audit_flags_sensitive_unknown_and_missing_transformation_review():
    report = audit_field_release_policy([
        {"name": "sample_code", "classification": "public", "release_action": "include"},
        {"name": "emailAddress", "classification": "personal_data", "release_action": "coarsen"},
        {"name": "precise_gps", "classification": "sensitive_data", "release_action": "exclude",
         "transformation_status": "completed", "transformation_ref": "transform:3"},
        {"name": "custom_metric", "classification": "unknown", "release_action": "include"},
    ])
    assert report["policy_gate_passed"] is False
    assert {item["field"] for item in report["release_blockers"]} == {"emailAddress", "custom_metric"}
    assert report["field_values_inspected"] is False
    corrected = audit_field_release_policy([
        {"name": "email_address", "classification": "personal_data", "release_action": "coarsen", "review_ref": "review:7",
         "transformation_status": "completed", "transformation_ref": "transform:7"},
        {"name": "sample_code", "classification": "public", "release_action": "include"},
    ])
    assert corrected["policy_gate_passed"] is True
    with pytest.raises(ValueError, match="duplicate"):
        audit_field_release_policy([{"name": "id", "classification": "public", "release_action": "include"},
                                    {"name": "ID", "classification": "public", "release_action": "include"}])


def test_aggregate_disclosure_uses_primary_and_complementary_suppression():
    report = screen_aggregate_disclosure([
        {"cell_id": "a", "group_id": "g1", "count": 2},
        {"cell_id": "b", "group_id": "g1", "count": 20},
        {"cell_id": "c", "group_id": "g1", "count": 35},
        {"cell_id": "d", "group_id": "g2", "count": 10},
        {"cell_id": "e", "group_id": "g2", "count": 12},
    ], minimum_group_size=5)
    by_id = {cell["cell_id"]: cell for cell in report["cells"]}
    assert by_id["a"]["suppressed"] is True and by_id["a"]["count"] is None
    assert by_id["b"]["suppressed"] is True
    assert by_id["c"]["suppressed"] is False
    assert report["suppressed_cell_count"] == 2
    assert report["disclosure_risk_eliminated"] is False
    with pytest.raises(ValueError, match="unique"):
        screen_aggregate_disclosure([{"cell_id": "x", "group_id": "g", "count": 5},
                                     {"cell_id": "x", "group_id": "g", "count": 6}])


def test_schema_diff_distinguishes_additive_and_breaking_changes():
    old = {"id": {"type": "string", "nullable": False, "required": True},
           "value": {"type": "number", "nullable": True, "required": False}}
    additive = compare_dataset_schemas(old, {**old, "notes": {"type": "string", "nullable": True, "required": False}})
    assert additive["schema_compatible"] is True
    assert additive["compatible_additive_change"] is True
    breaking = compare_dataset_schemas(old, {
        "id": {"type": "integer", "nullable": False, "required": True},
        "value": {"type": "number", "nullable": False, "required": True},
        "notes": {"type": "string", "nullable": True, "required": False},
    })
    assert breaking["schema_compatible"] is False
    assert breaking["breaking_change_count"] == 2
    assert "type_changed" in breaking["breaking_field_changes"][0]["reasons"]


def test_lineage_graph_detects_missing_edges_cycles_and_duplicate_edges():
    nodes = [{"id": name} for name in ("raw", "clean", "analysis", "orphan")]
    valid = audit_lineage_graph(nodes, [{"from": "raw", "to": "clean"}, {"from": "clean", "to": "analysis"}])
    assert valid["valid"] is True
    assert valid["topological_order"][:3] == ["orphan", "raw", "clean"] or set(valid["topological_order"]) == {"raw", "clean", "analysis", "orphan"}
    missing = audit_lineage_graph(nodes, [{"from": "raw", "to": "missing"}])
    assert missing["graph_is_complete"] is False and missing["policy_gate_passed"] is False
    cycle = audit_lineage_graph(nodes, [{"from": "raw", "to": "clean"}, {"from": "clean", "to": "raw"}])
    assert cycle["nodes_not_topologically_resolved"] == ["clean", "raw"]
    with pytest.raises(ValueError, match="duplicate"):
        audit_lineage_graph(nodes, [{"from": "raw", "to": "clean"}, {"from": "raw", "to": "clean"}])


def test_group_and_time_split_audit_detects_group_overlap_and_temporal_reversal():
    good = {
        "train": [{"person_group": "g1", "captured_at": "2026-01-01T00:00:00Z"}],
        "validation": [{"person_group": "g2", "captured_at": "2026-02-01T00:00:00+00:00"}],
        "test": [{"person_group": "g3", "captured_at": "2026-03-01T00:00:00Z"}],
    }
    result = audit_group_time_splits(good, group_field="person_group", time_field="captured_at",
                                     split_order=["train", "validation", "test"])
    assert result["policy_gate_passed"] is True
    bad = deepcopy(good)
    bad["test"].append({"person_group": "g1", "captured_at": "2025-12-31T00:00:00Z"})
    bad["train"].append({"person_group": "g4", "captured_at": "2026-01-02T00:00:00Z"})
    bad["test"].append({"person_group": "g4", "captured_at": "2026-03-02T00:00:00Z"})
    result = audit_group_time_splits(bad, group_field="person_group", time_field="captured_at",
                                     split_order=["train", "validation", "test"])
    assert result["group_leakage_detected"] is True
    assert result["group_overlap_count"] == 2
    assert result["group_overlap_pattern_count"] == 1
    assert result["group_overlaps"][0]["group_count"] == 2
    assert "group" not in result["group_overlaps"][0]
    assert result["temporal_leakage_detected"] is True
    with pytest.raises(ValueError, match="timezone"):
        audit_group_time_splits({"a": [{"g": "1", "t": "2026-01-01T00:00:00"}],
                                 "b": [{"g": "2", "t": "2026-02-01T00:00:00Z"}]}, group_field="g", time_field="t")


def test_retention_planner_marks_due_and_holds_without_deleting():
    result = plan_retention_reviews([
        {"dataset_id": "d1", "retention_start": "2025-01-01", "retention_days": 30,
         "legal_or_policy_hold": False, "policy_ref": "policy:1"},
        {"dataset_id": "d2", "retention_start": "2026-11-01", "retention_days": 365,
         "legal_or_policy_hold": True, "policy_ref": "policy:2"},
    ], as_of="2026-11-10")
    states = {item["dataset_id"]: item["state"] for item in result["records"]}
    assert states == {"d1": "review_due", "d2": "on_hold"}
    assert result["data_deleted"] is False
    assert result["policy_gate_passed"] is False
    with pytest.raises(ValueError, match="unique"):
        plan_retention_reviews([
            {"dataset_id": "d1", "retention_start": "2025-01-01", "retention_days": 30, "policy_ref": "p"},
            {"dataset_id": "d1", "retention_start": "2025-01-01", "retention_days": 30, "policy_ref": "p"},
        ], as_of="2026-11-10")


def test_release_readiness_requires_all_eight_explicit_gates_and_never_authorizes():
    passing = {name: {"policy_gate_passed": True} for name in (
        "license", "consent", "field_privacy", "disclosure", "schema", "lineage", "split_integrity", "retention")}
    ready = build_release_readiness(passing)
    assert ready["ready_for_human_release_review"] is True
    assert ready["release_authorized"] is False
    failing = dict(passing)
    failing["consent"] = {"policy_gate_passed": False}
    assert build_release_readiness(failing)["ready_for_human_release_review"] is False
    assert build_release_readiness({})["missing_checks"] == list(passing)


def test_release_manifest_is_deterministic_and_detects_tampering():
    readiness = {"ready_for_human_release_review": True, "release_authorized": False}
    args = dict(dataset_id="field-study", dataset_version=3, schema_digest="a" * 64,
                artifact_digests={"summary.json": "b" * 64}, source_refs=["doi:10.1234/example"],
                review_refs=["review:9"], readiness_report=readiness, software_version="0.2.0")
    first = build_release_manifest(**args)
    second = build_release_manifest(**args)
    assert first == second
    assert verify_release_manifest(first)["valid"] is True
    changed = dict(first)
    changed["dataset_version"] = 4
    assert verify_release_manifest(changed)["valid"] is False
    assert first["raw_dataset_content_included"] is False
    assert first["release_authorized"] is False


def test_release_manifest_rejects_bad_digest_and_oversized_metadata():
    with pytest.raises(ValueError, match="SHA-256"):
        build_release_manifest(dataset_id="d", dataset_version=1, schema_digest="bad", artifact_digests={},
                               source_refs=[], review_refs=[], readiness_report={"ready_for_human_release_review": False},
                               software_version="1")
    with pytest.raises(ValueError, match="unique"):
        build_release_manifest(dataset_id="d", dataset_version=1, schema_digest="a" * 64, artifact_digests={},
                               source_refs=["s", "s"], review_refs=[], readiness_report={"ready_for_human_release_review": False},
                               software_version="1")
    with pytest.raises(ValueError, match="artifact names"):
        build_release_manifest(dataset_id="d", dataset_version=1, schema_digest="a" * 64,
                               artifact_digests={" a": "b" * 64, "a": "c" * 64},
                               source_refs=[], review_refs=[], readiness_report={"ready_for_human_release_review": False},
                               software_version="1")


def test_documented_consent_without_evidence_reference_is_not_a_pass():
    report = assess_consent_scope(
        {"status": "documented", "permitted_purposes": ["research"], "sharing_authorized": True,
         "reviewer_ref": "review:1"},
        "research",
    )
    assert report["policy_gate_passed"] is False
    assert "documented_consent_needs_evidence_and_reviewer_refs" in report["reasons"]
    assert report["participant_identifiers_collected"] is False


def test_internal_and_confidential_fields_are_not_silently_released():
    report = audit_field_release_policy([
        {"name": "internal_notes", "classification": "internal", "release_action": "include"},
        {"name": "aggregate_score", "classification": "public", "release_action": "include"},
    ])
    assert report["policy_gate_passed"] is False
    assert report["release_blockers"][0]["field"] == "internal_notes"


def test_schema_addition_of_required_field_is_explicitly_breaking():
    report = compare_dataset_schemas(
        {"id": {"type": "string", "nullable": False, "required": True}},
        {"id": {"type": "string", "nullable": False, "required": True},
         "new_key": {"type": "string", "nullable": False, "required": True}},
    )
    assert report["schema_compatible"] is False
    assert report["breaking_field_changes"][0]["reasons"] == ["new_required_field", "new_non_nullable_field"]


def test_lineage_topological_order_is_deterministic_for_wide_graph():
    nodes = [{"id": f"n{i:04d}"} for i in range(250)]
    edges = [{"from": "n0000", "to": f"n{i:04d}"} for i in range(1, 250)]
    first = audit_lineage_graph(nodes, edges)
    second = audit_lineage_graph(nodes, edges)
    assert first["topological_order"] == second["topological_order"]
    assert first["valid"] is True
    assert len(first["topological_order"]) == 250


def test_time_split_order_is_timezone_normalized_and_requires_unique_names():
    splits = {
        "train": [{"group": "g1", "when": "2026-01-01T02:00:00+02:00"}],
        "test": [{"group": "g2", "when": "2026-01-01T00:00:00Z"}],
    }
    report = audit_group_time_splits(splits, group_field="group", time_field="when",
                                     split_order=["train", "test"])
    assert report["temporal_leakage_detected"] is True
    with pytest.raises(ValueError, match="exactly once"):
        audit_group_time_splits(splits, group_field="group", time_field="when",
                                split_order=["train", "train"])
    with pytest.raises(ValueError, match="whitespace"):
        audit_group_time_splits({" train": splits["train"], "test": splits["test"]},
                                group_field="group", time_field="when")


def test_limits_and_untrusted_types_fail_closed():
    with pytest.raises(ValueError, match="minimum_group_size"):
        screen_aggregate_disclosure([], minimum_group_size=True)
    with pytest.raises(ValueError, match="at most"):
        audit_field_release_policy([{"name": f"f{i}", "classification": "public", "release_action": "include"}
                                    for i in range(5001)])
    with pytest.raises(ValueError, match="status"):
        assess_license_use({"license_id": "x", "review_status": [], "permitted_uses": []}, "research")
    with pytest.raises(ValueError, match="status"):
        assess_consent_scope({"status": [], "permitted_purposes": []}, "research")


def test_release_readiness_does_not_accept_truthy_non_boolean_gate_values():
    reports = {name: {"policy_gate_passed": 1} for name in (
        "license", "consent", "field_privacy", "disclosure", "schema", "lineage", "split_integrity", "retention")}
    result = build_release_readiness(reports)
    assert result["ready_for_human_release_review"] is False
    assert len(result["blockers"]) == 8
