from __future__ import annotations

from copy import deepcopy

import pytest

from ssswet_core.rescue_communications_assurance import (
    validate_communications_plan,
    analyze_communications_connectivity,
    identify_communications_single_points_of_failure,
    assess_communications_zone_coverage,
    assess_communications_bandwidth,
    estimate_relay_power_autonomy,
    plan_communications_message_routes,
    assess_communications_traffic_load,
    compare_communications_outage_scenarios,
    build_communications_assurance_manifest,
    verify_communications_assurance_manifest,
)


def sample_plan():
    return {
        "schema_version": 1,
        "plan_id": "community-relay-plan-r1",
        "nodes": [
            {
                "node_id": "gateway-a", "role": "gateway", "service_zones": [],
                "battery_wh": 50, "load_w": 5, "usable_fraction": 0.8,
                "evidence_refs": ["power-test:a"],
            },
            {"node_id": "gateway-b", "role": "gateway", "service_zones": []},
            {"node_id": "relay-a", "role": "relay", "service_zones": []},
            {"node_id": "relay-b", "role": "relay", "service_zones": []},
            {"node_id": "endpoint-a", "role": "endpoint", "service_zones": ["zone-a"]},
            {"node_id": "endpoint-b", "role": "endpoint", "service_zones": ["zone-b"]},
        ],
        "links": [
            {
                "link_id": "a-gw-relay", "from_node": "gateway-a", "to_node": "relay-a",
                "direction": "bidirectional", "status": "available",
                "capacity_kbps": 100, "reserved_kbps": 10, "latency_ms": 50,
            },
            {
                "link_id": "a-relay-endpoint", "from_node": "relay-a", "to_node": "endpoint-a",
                "direction": "directed", "status": "available",
                "capacity_kbps": 80, "reserved_kbps": 10, "latency_ms": 40,
            },
            {
                "link_id": "b-gw-relay", "from_node": "gateway-b", "to_node": "relay-b",
                "direction": "bidirectional", "status": "available",
                "capacity_kbps": 80, "reserved_kbps": 20, "latency_ms": 20,
            },
            {
                "link_id": "b-relay-endpoint", "from_node": "relay-b", "to_node": "endpoint-a",
                "direction": "directed", "status": "available",
                "capacity_kbps": 60, "reserved_kbps": 10, "latency_ms": 30,
            },
            {
                "link_id": "a-relay-zone-b", "from_node": "relay-a", "to_node": "endpoint-b",
                "direction": "directed", "status": "available",
                "capacity_kbps": 40, "reserved_kbps": 10, "latency_ms": 25,
            },
            {
                "link_id": "unknown-direct", "from_node": "gateway-b", "to_node": "endpoint-b",
                "direction": "directed", "status": "unknown",
                "capacity_kbps": 100, "reserved_kbps": 0, "latency_ms": 1,
            },
        ],
        "zones": [
            {"zone_id": "zone-a", "demand_kbps": 130, "priority": 5},
            {"zone_id": "zone-b", "demand_kbps": 20, "priority": 4},
        ],
        "gateways": ["gateway-a", "gateway-b"],
    }


def test_plan_validation_normalizes_order_and_rejects_unknown_fields():
    plan = sample_plan()
    reversed_plan = deepcopy(plan)
    reversed_plan["nodes"].reverse()
    reversed_plan["links"].reverse()
    reversed_plan["zones"].reverse()
    assert validate_communications_plan(plan)["normalized_plan"] == validate_communications_plan(reversed_plan)["normalized_plan"]

    invalid = sample_plan()
    invalid["nodes"][0]["api_token"] = "must-not-be-accepted"
    with pytest.raises(ValueError, match="unsupported fields"):
        validate_communications_plan(invalid)


@pytest.mark.parametrize("mutation,match", [
    (lambda p: p.update(schema_version=True), "schema_version"),
    (lambda p: p.update(schema_version=1.0), "schema_version"),
    (lambda p: p["nodes"][0].update(role=[]), "node role"),
    (lambda p: p["links"][0].update(direction={}), "link direction"),
    (lambda p: p["links"].append(dict(p["links"][0])), "link_id"),
    (lambda p: p["links"][0].update(to_node="missing"), "unknown node"),
    (lambda p: p["links"][0].update(reserved_kbps=101), "reserved_kbps"),
    (lambda p: p["nodes"][0].update(usable_fraction=1.1), "usable_fraction"),
])
def test_plan_validation_rejects_invalid_boundaries(mutation, match):
    plan = sample_plan()
    mutation(plan)
    with pytest.raises(ValueError, match=match):
        validate_communications_plan(plan)


def test_connectivity_uses_only_declared_available_links_and_direction():
    plan = sample_plan()
    result = analyze_communications_connectivity(plan)
    assert result["reachable_zone_ids"] == ["zone-a", "zone-b"]
    assert result["zone_gateway_ids"]["zone-a"] == ["gateway-a", "gateway-b"]
    assert result["zone_gateway_ids"]["zone-b"] == ["gateway-a"]
    assert result["unknown_links_treated_as_available"] is False

    reverse = analyze_communications_connectivity(plan, failed_node_ids=["relay-a"])
    assert reverse["reachable_zone_ids"] == ["zone-a"]
    assert "zone-b" in reverse["unreachable_zone_ids"]


def test_single_point_analysis_distinguishes_bridge_and_redundant_paths():
    result = identify_communications_single_points_of_failure(sample_plan())
    critical_nodes = {item["node_id"]: item["lost_zone_ids"] for item in result["critical_node_failures"]}
    critical_links = {item["link_id"]: item["lost_zone_ids"] for item in result["critical_link_failures"]}
    assert "zone-b" in critical_nodes["relay-a"]
    assert "zone-a" not in critical_nodes.get("relay-a", [])
    assert "zone-b" in critical_links["a-gw-relay"]
    assert "zone-a" not in critical_links.get("a-gw-relay", [])


def test_zone_coverage_reports_gateway_redundancy_without_geographic_claim():
    result = assess_communications_zone_coverage(sample_plan())
    rows = {item["zone_id"]: item for item in result["zones"]}
    assert rows["zone-a"]["coverage_status"] == "multi_gateway_path"
    assert rows["zone-a"]["reachable_gateway_count"] == 2
    assert rows["zone-b"]["coverage_status"] == "single_gateway_path"
    assert result["zone_coverage_ratio"] == 1.0
    assert result["demand_weighted_coverage_ratio"] == 1.0
    assert result["coverage_is_geographic_or_field_verified"] is False


def test_bandwidth_max_flow_and_min_cut_match_hand_calculation():
    result = assess_communications_bandwidth(sample_plan())
    rows = {item["zone_id"]: item for item in result["zones"]}
    assert rows["zone-a"]["maximum_flow_kbps"] == pytest.approx(120.0)
    assert rows["zone-a"]["shortage_kbps"] == pytest.approx(10.0)
    assert set(rows["zone-a"]["minimum_cut_link_ids"]) == {"a-relay-endpoint", "b-relay-endpoint"}
    assert rows["zone-a"]["capacity_status"] == "declared_capacity_shortfall"
    assert rows["zone-b"]["maximum_flow_kbps"] == pytest.approx(30.0)
    assert result["shared_bandwidth_jointly_allocated"] is False


def test_power_autonomy_requires_all_declared_inputs():
    result = estimate_relay_power_autonomy(sample_plan(), minimum_runtime_hours=6)
    rows = {item["node_id"]: item for item in result["nodes"]}
    assert rows["gateway-a"]["runtime_hours"] == pytest.approx(8.0)
    assert rows["gateway-a"]["status"] == "meets_declared_minimum"
    assert rows["gateway-b"]["status"] == "unknown_missing_declared_power_data"
    assert rows["gateway-b"]["runtime_hours"] is None


def test_message_paths_include_serialization_and_ttl_without_message_content():
    result = plan_communications_message_routes(sample_plan(), [
        {"message_id": "m1", "from_node": "gateway-a", "to_zone": "zone-a",
         "payload_kb": 1, "ttl_seconds": 0.25, "priority": 5},
        {"message_id": "m2", "from_node": "gateway-b", "to_zone": "zone-b",
         "payload_kb": 1, "ttl_seconds": 5, "priority": 2},
    ])
    rows = {item["message_id"]: item for item in result["messages"]}
    assert rows["m1"]["status"] == "estimated_ttl_exceeded"
    assert rows["m1"]["estimated_delivery_seconds"] == pytest.approx(
        (50 + 8 / 90 * 1000 + 40 + 8 / 70 * 1000) / 1000
    )
    assert rows["m2"]["status"] == "no_declared_route"
    assert result["message_bodies_collected"] is False
    with pytest.raises(ValueError, match="unsupported fields"):
        plan_communications_message_routes(sample_plan(), [
            {"message_id": "bad", "from_node": "gateway-a", "to_zone": "zone-a",
             "payload_kb": 1, "ttl_seconds": 1, "body": "private message"}
        ])


def test_traffic_load_reports_over_capacity_without_reserving_or_mutating_plan():
    plan = sample_plan()
    before = deepcopy(plan)
    result = assess_communications_traffic_load(plan, [
        {"flow_id": "f1", "from_node": "gateway-a", "to_zone": "zone-a", "offered_kbps": 60},
        {"flow_id": "f2", "from_node": "gateway-a", "to_zone": "zone-a", "offered_kbps": 60},
    ])
    assert result["over_capacity_link_ids"] == ["a-gw-relay", "a-relay-endpoint"]
    assert next(item for item in result["links"] if item["link_id"] == "a-gw-relay")["utilization_ratio"] == pytest.approx(1.3)
    assert plan == before
    assert result["traffic_reserved_or_shaped"] is False


def test_outage_scenarios_compare_against_unchanged_baseline():
    result = compare_communications_outage_scenarios(sample_plan(), [
        {"scenario_id": "relay-a-down", "failed_node_ids": ["relay-a"], "failed_link_ids": []},
        {"scenario_id": "link-b-down", "failed_node_ids": [], "failed_link_ids": ["b-relay-endpoint"]},
    ])
    rows = {item["scenario_id"]: item for item in result["scenarios"]}
    assert rows["relay-a-down"]["lost_zone_ids"] == ["zone-b"]
    assert rows["link-b-down"]["lost_zone_ids"] == []
    assert result["plan_mutated"] is False
    with pytest.raises(ValueError, match="unknown node or link"):
        compare_communications_outage_scenarios(sample_plan(), [
            {"scenario_id": "bad", "failed_node_ids": ["private-device"], "failed_link_ids": []}
        ])


def test_manifest_is_deterministic_and_detects_plan_or_assessment_tampering():
    plan = sample_plan()
    assessments = {
        "coverage": assess_communications_zone_coverage(plan),
        "capacity": assess_communications_bandwidth(plan),
    }
    first = build_communications_assurance_manifest(plan, assessments, evidence_refs=["study:1", "test:2"])
    second = build_communications_assurance_manifest(plan, assessments, evidence_refs=["test:2", "study:1"])
    assert first == second
    assert verify_communications_assurance_manifest(first, plan=plan, assessments=assessments)["valid"] is True

    changed = deepcopy(assessments)
    changed["coverage"]["covered_zone_count"] = 0
    assert "assessment_digest_mismatch" in verify_communications_assurance_manifest(
        first, plan=plan, assessments=changed
    )["reasons"]

    altered = dict(first)
    altered["plan_sha256"] = "0" * 64
    assert verify_communications_assurance_manifest(altered)["valid"] is False


def test_manifest_rejects_duplicate_normalized_assessment_names():
    with pytest.raises(ValueError, match="unique after normalization"):
        build_communications_assurance_manifest(
            sample_plan(), {"coverage": {"ok": True}, " coverage ": {"ok": True}}
        )


def test_bounded_message_and_scenario_collections():
    with pytest.raises(ValueError, match="at most 500"):
        plan_communications_message_routes(sample_plan(), [{}] * 501)
    with pytest.raises(ValueError, match="at most 100"):
        compare_communications_outage_scenarios(sample_plan(), [{}] * 101)



def test_bandwidth_analysis_requires_explicit_batches_above_fifty_zones():
    plan = sample_plan()
    plan["zones"] = [
        {"zone_id": f"zone-{index:02d}", "demand_kbps": 1, "priority": 1}
        for index in range(51)
    ]
    for node in plan["nodes"]:
        node["service_zones"] = []
    plan["nodes"][0]["service_zones"] = ["zone-00"]
    with pytest.raises(ValueError, match="50 zones per call"):
        assess_communications_bandwidth(plan)
    batch = assess_communications_bandwidth(plan, zone_ids=["zone-00", "zone-01"])
    assert batch["analyzed_zone_ids"] == ["zone-00", "zone-01"]
    assert len(batch["unassessed_zone_ids"]) == 49


def test_manifest_rejects_authorization_flags_even_with_recomputed_hash():
    from ssswet_core.assurance_common import digest

    plan = sample_plan()
    manifest = build_communications_assurance_manifest(plan, {"coverage": {"ok": True}})
    altered = dict(manifest)
    altered["dispatch_authorized"] = True
    body = {key: value for key, value in altered.items() if key != "manifest_sha256"}
    altered["manifest_sha256"] = digest(body)
    result = verify_communications_assurance_manifest(altered)
    assert result["valid"] is False
    assert "manifest_safety_flags_invalid" in result["reasons"]


def test_manifest_rejects_boolean_schema_version_even_with_recomputed_hash():
    from ssswet_core.assurance_common import digest

    manifest = build_communications_assurance_manifest(sample_plan(), {})
    altered = dict(manifest)
    altered["schema_version"] = True
    body = {key: value for key, value in altered.items() if key != "manifest_sha256"}
    altered["manifest_sha256"] = digest(body)
    result = verify_communications_assurance_manifest(altered)
    assert result["valid"] is False
    assert "manifest_schema_version_invalid" in result["reasons"]



def test_manifest_rejects_float_schema_version_even_with_recomputed_hash():
    from ssswet_core.assurance_common import digest

    manifest = build_communications_assurance_manifest(sample_plan(), {})
    altered = dict(manifest)
    altered["schema_version"] = 1.0
    body = {key: value for key, value in altered.items() if key != "manifest_sha256"}
    altered["manifest_sha256"] = digest(body)
    result = verify_communications_assurance_manifest(altered)
    assert result["valid"] is False
    assert "manifest_schema_version_invalid" in result["reasons"]
