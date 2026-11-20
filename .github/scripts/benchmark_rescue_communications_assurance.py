"""Synthetic, offline benchmarks for civil-rescue communications assurance."""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.assurance_common import canonical_bytes
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


def measure(function, repeats: int = 5) -> dict:
    values = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter_ns()
        result = function()
        values.append((time.perf_counter_ns() - started) / 1_000_000)
    ordered = sorted(values)
    p95 = ordered[min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)]
    return {
        "median_ms": round(statistics.median(values), 4),
        "p95_ms": round(p95, 4),
        "samples": repeats,
    }, result


def synthetic_plan() -> dict:
    nodes = []
    gateways = []
    for index in range(4):
        node_id = f"gateway-{index:02d}"
        gateways.append(node_id)
        nodes.append({
            "node_id": node_id, "role": "gateway", "service_zones": [],
            "battery_wh": 500.0, "load_w": 20.0, "usable_fraction": 0.8,
        })
    for index in range(16):
        nodes.append({
            "node_id": f"relay-{index:02d}", "role": "relay",
            "service_zones": [], "battery_wh": 200.0, "load_w": 10.0,
            "usable_fraction": 0.75,
        })
    for index in range(80):
        nodes.append({
            "node_id": f"endpoint-{index:03d}", "role": "endpoint",
            "service_zones": [f"zone-{index % 20:02d}"],
        })

    links = []
    for index in range(16):
        links.append({
            "link_id": f"gateway-relay-{index:02d}",
            "from_node": gateways[index % 4],
            "to_node": f"relay-{index:02d}",
            "direction": "bidirectional", "status": "available",
            "capacity_kbps": 1000.0, "reserved_kbps": 100.0, "latency_ms": 5.0,
        })
    for index in range(80):
        links.append({
            "link_id": f"relay-endpoint-{index:03d}",
            "from_node": f"relay-{index % 16:02d}",
            "to_node": f"endpoint-{index:03d}",
            "direction": "directed", "status": "available",
            "capacity_kbps": 500.0, "reserved_kbps": 50.0, "latency_ms": 8.0,
        })
    for index in range(20):
        links.append({
            "link_id": f"relay-mesh-{index:02d}",
            "from_node": f"relay-{index % 16:02d}",
            "to_node": f"relay-{(index + 1) % 16:02d}" if index < 16 else f"relay-{(index + 5) % 16:02d}",
            "direction": "bidirectional", "status": "available",
            "capacity_kbps": 300.0, "reserved_kbps": 30.0, "latency_ms": 12.0,
        })
    zones = [
        {"zone_id": f"zone-{index:02d}", "demand_kbps": 200.0, "priority": 1 + index % 5}
        for index in range(20)
    ]
    return {
        "schema_version": 1, "plan_id": "synthetic-communications-benchmark",
        "nodes": nodes, "links": links, "zones": zones, "gateways": gateways,
    }


def main() -> None:
    plan = synthetic_plan()
    messages = [
        {
            "message_id": f"message-{index:03d}",
            "from_node": f"gateway-{index % 4:02d}",
            "to_zone": f"zone-{index % 20:02d}",
            "payload_kb": 2.0, "ttl_seconds": 5.0, "priority": 1 + index % 5,
        }
        for index in range(100)
    ]
    flows = [
        {
            "flow_id": f"flow-{index:03d}",
            "from_node": f"gateway-{index % 4:02d}",
            "to_zone": f"zone-{index % 20:02d}",
            "offered_kbps": 20.0, "priority": 1 + index % 5,
        }
        for index in range(100)
    ]
    scenarios = [
        {"scenario_id": f"relay-outage-{index:02d}",
         "failed_node_ids": [f"relay-{index:02d}"], "failed_link_ids": []}
        for index in range(16)
    ] + [
        {"scenario_id": f"link-outage-{index:02d}",
         "failed_node_ids": [], "failed_link_ids": [f"relay-endpoint-{index:03d}"]}
        for index in range(16)
    ]

    probes = {}
    results = {}
    workloads = {
        "plan_validation_100_nodes_116_links": lambda: validate_communications_plan(plan),
        "connectivity_20_zones": lambda: analyze_communications_connectivity(plan),
        "single_point_failures_100_nodes_116_links": lambda: identify_communications_single_points_of_failure(plan),
        "zone_coverage_20_zones": lambda: assess_communications_zone_coverage(plan),
        "bandwidth_max_flow_20_zones": lambda: assess_communications_bandwidth(plan),
        "power_autonomy_20_powered_nodes": lambda: estimate_relay_power_autonomy(plan, minimum_runtime_hours=8),
        "message_routes_100_messages": lambda: plan_communications_message_routes(plan, messages),
        "traffic_load_100_flows": lambda: assess_communications_traffic_load(plan, flows),
        "outage_scenarios_32_cases": lambda: compare_communications_outage_scenarios(plan, scenarios),
    }
    for name, function in workloads.items():
        metrics, result = measure(function)
        probes[name] = metrics
        results[name] = result

    assessments = {
        "connectivity": results["connectivity_20_zones"],
        "coverage": results["zone_coverage_20_zones"],
        "bandwidth": results["bandwidth_max_flow_20_zones"],
        "outages": results["outage_scenarios_32_cases"],
    }
    manifest_metrics, manifest = measure(
        lambda: build_communications_assurance_manifest(
            plan, assessments, evidence_refs=["fixture:communications-v1", "test:synthetic"]
        )
    )
    probes["manifest_build"] = manifest_metrics
    verify_metrics, verification = measure(
        lambda: verify_communications_assurance_manifest(manifest, plan=plan, assessments=assessments)
    )
    probes["manifest_verify"] = verify_metrics
    if not verification["valid"]:
        raise SystemExit("synthetic manifest verification failed")
    if len(results["connectivity_20_zones"]["reachable_zone_ids"]) != 20:
        raise SystemExit("synthetic connectivity acceptance check failed")
    if results["zone_coverage_20_zones"]["zone_coverage_ratio"] != 1.0:
        raise SystemExit("synthetic coverage acceptance check failed")
    if not all(item["status"] != "no_declared_route" for item in results["message_routes_100_messages"]["messages"]):
        raise SystemExit("synthetic message-route acceptance check failed")

    budget_ms = 2000.0
    if any(item["p95_ms"] > budget_ms for item in probes.values()):
        raise SystemExit("communications assurance benchmark exceeded the 2,000 ms p95 budget")
    print(json.dumps({
        "benchmark": "SSSWET civil-rescue communications assurance",
        "synthetic_only": True,
        "workload": {
            "nodes": len(plan["nodes"]), "links": len(plan["links"]),
            "zones": len(plan["zones"]), "messages": len(messages),
            "traffic_flows": len(flows), "outage_scenarios": len(scenarios),
        },
        "probes": probes,
        "manifest_bytes": len(canonical_bytes(manifest)),
        "p95_budget_ms": budget_ms,
        "live_network_access": False,
        "dispatch_or_safety_authorization": False,
        "field_performance_or_coverage_established": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
