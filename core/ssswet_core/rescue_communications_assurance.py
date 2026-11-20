"""Bounded, offline assurance for civil-rescue communications planning.

This module analyzes caller-declared network plans. It never scans, connects to,
configures, transmits over, or dispatches a real communications network.
Unknown links are never treated as available.
"""
from __future__ import annotations

from collections import deque
import heapq
from math import isfinite
from typing import Any

from .assurance_common import canonical_bytes, digest, finite_number, identifier

SCHEMA_VERSION = 1
MAX_NODES = 250
MAX_LINKS = 1000
MAX_ZONES = 250
MAX_MESSAGES = 500
MAX_TRAFFIC_FLOWS = 500
MAX_SCENARIOS = 100
MAX_BANDWIDTH_ZONES = 50
MAX_PLAN_BYTES = 1_048_576
MAX_EVIDENCE_REFS = 500
ROLES = {"gateway", "relay", "endpoint"}
LINK_DIRECTIONS = {"directed", "bidirectional"}
LINK_STATES = {"available", "blocked", "unknown"}


def _records(value: Any, field: str, maximum: int) -> list[dict]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"{field} must be a list of at most {maximum} records")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"every {field} record must be an object")
    return value


def _refs(value: Any, field: str, maximum: int = 20) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)) or len(value) > maximum:
        raise ValueError(f"{field} must contain at most {maximum} references")
    result = [identifier(item, field, 200) for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return sorted(result)


def _number(value: Any, field: str, *, minimum: float = 0.0,
            maximum: float = 1_000_000_000.0) -> float:
    result = finite_number(value, field)
    if result < minimum or result > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return result


def _optional_number(item: dict, field: str, *, minimum: float = 0.0,
                     maximum: float = 1_000_000_000.0) -> float | None:
    value = item.get(field)
    return None if value is None else _number(value, field, minimum=minimum, maximum=maximum)


def _unique_ids(records: list[dict], field: str) -> set[str]:
    result = set()
    for item in records:
        value = identifier(item.get(field), field, 160)
        if value in result:
            raise ValueError(f"{field} values must be unique")
        result.add(value)
    return result


def _normalize_plan(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("plan must be an object")
    allowed = {"schema_version", "plan_id", "nodes", "links", "zones", "gateways"}
    if set(plan) - allowed:
        raise ValueError("plan contains unsupported fields")
    version = plan.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be integer {SCHEMA_VERSION}")
    plan_id = identifier(plan.get("plan_id"), "plan_id", 160)
    nodes = _records(plan.get("nodes"), "nodes", MAX_NODES)
    links = _records(plan.get("links"), "links", MAX_LINKS)
    zones = _records(plan.get("zones"), "zones", MAX_ZONES)
    if not nodes:
        raise ValueError("at least one node is required")
    if not zones:
        raise ValueError("at least one service zone is required")

    node_ids = _unique_ids(nodes, "node_id")
    zone_ids = _unique_ids(zones, "zone_id")
    normalized_zones = []
    for item in zones:
        if set(item) - {"zone_id", "demand_kbps", "priority", "evidence_refs"}:
            raise ValueError("zone contains unsupported fields")
        demand = _optional_number(item, "demand_kbps")
        priority = item.get("priority")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("zone priority must be an integer from 1 to 5")
        normalized_zones.append({
            "zone_id": identifier(item.get("zone_id"), "zone_id", 160),
            "demand_kbps": demand,
            "priority": priority,
            "evidence_refs": _refs(item.get("evidence_refs"), "zone evidence_refs"),
        })

    normalized_nodes = []
    for item in nodes:
        if set(item) - {
            "node_id", "role", "service_zones", "battery_wh", "load_w",
            "usable_fraction", "evidence_refs",
        }:
            raise ValueError("node contains unsupported fields")
        node_id = identifier(item.get("node_id"), "node_id", 160)
        role = item.get("role")
        if not isinstance(role, str) or role not in ROLES:
            raise ValueError("node role must be gateway, relay or endpoint")
        service_zones = item.get("service_zones", [])
        if not isinstance(service_zones, list) or len(service_zones) > MAX_ZONES:
            raise ValueError("service_zones must be a bounded list")
        service_zones = [identifier(value, "service_zone", 160) for value in service_zones]
        if len(service_zones) != len(set(service_zones)):
            raise ValueError("service_zones must not contain duplicates")
        if set(service_zones) - zone_ids:
            raise ValueError("node references an unknown service zone")
        battery = _optional_number(item, "battery_wh")
        load = _optional_number(item, "load_w")
        usable = _optional_number(item, "usable_fraction", minimum=0.000000001, maximum=1.0)
        normalized_nodes.append({
            "node_id": node_id,
            "role": role,
            "service_zones": sorted(service_zones),
            "battery_wh": battery,
            "load_w": load,
            "usable_fraction": usable,
            "evidence_refs": _refs(item.get("evidence_refs"), "node evidence_refs"),
        })

    normalized_links = []
    for item in links:
        if set(item) - {
            "link_id", "from_node", "to_node", "direction", "status",
            "capacity_kbps", "reserved_kbps", "latency_ms", "evidence_refs",
        }:
            raise ValueError("link contains unsupported fields")
        link_id = identifier(item.get("link_id"), "link_id", 160)
        source = identifier(item.get("from_node"), "from_node", 160)
        target = identifier(item.get("to_node"), "to_node", 160)
        if source == target:
            raise ValueError("link endpoints must differ")
        if source not in node_ids or target not in node_ids:
            raise ValueError("link references an unknown node")
        direction = item.get("direction")
        status = item.get("status")
        if not isinstance(direction, str) or direction not in LINK_DIRECTIONS:
            raise ValueError("link direction must be directed or bidirectional")
        if not isinstance(status, str) or status not in LINK_STATES:
            raise ValueError("link status must be available, blocked or unknown")
        capacity = _optional_number(item, "capacity_kbps")
        reserved = _optional_number(item, "reserved_kbps")
        latency = _optional_number(item, "latency_ms")
        if capacity is not None and reserved is not None and reserved > capacity:
            raise ValueError("reserved_kbps must not exceed capacity_kbps")
        normalized_links.append({
            "link_id": link_id,
            "from_node": source,
            "to_node": target,
            "direction": direction,
            "status": status,
            "capacity_kbps": capacity,
            "reserved_kbps": reserved,
            "latency_ms": latency,
            "evidence_refs": _refs(item.get("evidence_refs"), "link evidence_refs"),
        })
    _unique_ids(links, "link_id")

    gateways = plan.get("gateways")
    if not isinstance(gateways, list) or not gateways:
        raise ValueError("gateways must be a non-empty list")
    gateway_ids = [identifier(value, "gateway", 160) for value in gateways]
    if len(gateway_ids) != len(set(gateway_ids)):
        raise ValueError("gateways must not contain duplicates")
    node_by_id = {item["node_id"]: item for item in normalized_nodes}
    if set(gateway_ids) - node_ids:
        raise ValueError("gateways reference an unknown node")
    if any(node_by_id[value]["role"] != "gateway" for value in gateway_ids):
        raise ValueError("every declared gateway must have role gateway")

    normalized = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "nodes": sorted(normalized_nodes, key=lambda item: item["node_id"]),
        "links": sorted(normalized_links, key=lambda item: item["link_id"]),
        "zones": sorted(normalized_zones, key=lambda item: item["zone_id"]),
        "gateways": sorted(gateway_ids),
    }
    if len(canonical_bytes(normalized)) > MAX_PLAN_BYTES:
        raise ValueError(f"normalized plan exceeds {MAX_PLAN_BYTES} bytes")
    return normalized


def validate_communications_plan(plan: dict) -> dict:
    """Validate and canonicalize an offline civil-rescue communications plan."""
    normalized = _normalize_plan(plan)
    return {
        "schema_version": SCHEMA_VERSION,
        "normalized_plan": normalized,
        "node_count": len(normalized["nodes"]),
        "link_count": len(normalized["links"]),
        "zone_count": len(normalized["zones"]),
        "gateway_count": len(normalized["gateways"]),
        "unknown_links_are_traversable": False,
        "live_network_access_performed": False,
        "message_content_collected": False,
        "dispatch_authorized": False,
        "safety_certified": False,
    }


def _validate_failures(plan: dict, failed_nodes=(), failed_links=()) -> tuple[set[str], set[str]]:
    node_ids = {item["node_id"] for item in plan["nodes"]}
    link_ids = {item["link_id"] for item in plan["links"]}
    if not isinstance(failed_nodes, (list, tuple, set)) or len(failed_nodes) > MAX_NODES:
        raise ValueError("failed_node_ids must be a bounded collection")
    if not isinstance(failed_links, (list, tuple, set)) or len(failed_links) > MAX_LINKS:
        raise ValueError("failed_link_ids must be a bounded collection")
    nodes = {identifier(value, "failed_node_id", 160) for value in failed_nodes}
    links = {identifier(value, "failed_link_id", 160) for value in failed_links}
    if nodes - node_ids or links - link_ids:
        raise ValueError("failure set references an unknown node or link")
    return nodes, links


def _adjacency(plan: dict, failed_nodes: set[str] | None = None,
               failed_links: set[str] | None = None, *, require_capacity=False,
               require_latency=False) -> dict[str, list[tuple[str, dict, float | None]]]:
    failed_nodes = failed_nodes or set()
    failed_links = failed_links or set()
    active = {item["node_id"] for item in plan["nodes"]} - failed_nodes
    graph = {node_id: [] for node_id in active}
    for link in plan["links"]:
        if link["status"] != "available" or link["link_id"] in failed_links:
            continue
        source, target = link["from_node"], link["to_node"]
        if source not in active or target not in active:
            continue
        capacity = link["capacity_kbps"]
        reserved = link["reserved_kbps"]
        if require_capacity and (capacity is None or reserved is None or capacity <= reserved):
            continue
        if require_latency and link["latency_ms"] is None:
            continue
        residual = None if capacity is None or reserved is None else capacity - reserved
        graph[source].append((target, link, residual))
        if link["direction"] == "bidirectional":
            graph[target].append((source, link, residual))
    for values in graph.values():
        values.sort(key=lambda row: (row[0], row[1]["link_id"]))
    return graph


def _reachable(graph: dict[str, list], start: str) -> set[str]:
    if start not in graph:
        return set()
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for target, _link, _capacity in graph.get(current, []):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _connectivity(plan: dict, failed_nodes=None, failed_links=None) -> dict:
    failed_nodes, failed_links = _validate_failures(plan, failed_nodes or (), failed_links or ())
    graph = _adjacency(plan, failed_nodes, failed_links)
    gateways = [value for value in plan["gateways"] if value in graph]
    per_gateway = {gateway: _reachable(graph, gateway) for gateway in gateways}
    reachable = set().union(*per_gateway.values()) if per_gateway else set()
    zone_nodes = {
        zone["zone_id"]: sorted(
            node["node_id"] for node in plan["nodes"]
            if zone["zone_id"] in node["service_zones"]
        )
        for zone in plan["zones"]
    }
    zone_gateways = {}
    reachable_zones = []
    for zone_id, service_nodes in zone_nodes.items():
        providers = sorted(
            gateway for gateway, nodes in per_gateway.items()
            if any(node_id in nodes for node_id in service_nodes)
        )
        zone_gateways[zone_id] = providers
        if providers:
            reachable_zones.append(zone_id)
    return {
        "graph": graph,
        "reachable_node_ids": sorted(reachable),
        "reachable_zone_ids": sorted(reachable_zones),
        "unreachable_zone_ids": sorted(set(zone_nodes) - set(reachable_zones)),
        "zone_gateway_ids": zone_gateways,
    }


def analyze_communications_connectivity(plan: dict, *, failed_node_ids=(),
                                         failed_link_ids=()) -> dict:
    """Report directed reachability from declared gateways using available links."""
    normalized = _normalize_plan(plan)
    result = _connectivity(normalized, failed_node_ids, failed_link_ids)
    return {
        "plan_id": normalized["plan_id"],
        "reachable_node_ids": result["reachable_node_ids"],
        "reachable_zone_ids": result["reachable_zone_ids"],
        "unreachable_zone_ids": result["unreachable_zone_ids"],
        "zone_gateway_ids": result["zone_gateway_ids"],
        "unknown_links_treated_as_available": False,
        "blocked_links_treated_as_available": False,
        "live_network_test_performed": False,
    }


def identify_communications_single_points_of_failure(plan: dict) -> dict:
    """Find individual node/link removals that disconnect currently served zones."""
    normalized = _normalize_plan(plan)
    baseline = _connectivity(normalized)
    baseline_zones = set(baseline["reachable_zone_ids"])
    node_failures = []
    link_failures = []
    for node in normalized["nodes"]:
        node_id = node["node_id"]
        after = _connectivity(normalized, [node_id], [])
        lost = sorted(baseline_zones - set(after["reachable_zone_ids"]))
        if lost:
            node_failures.append({"node_id": node_id, "lost_zone_ids": lost})
    for link in normalized["links"]:
        link_id = link["link_id"]
        after = _connectivity(normalized, [], [link_id])
        lost = sorted(baseline_zones - set(after["reachable_zone_ids"]))
        if lost:
            link_failures.append({"link_id": link_id, "lost_zone_ids": lost})
    return {
        "plan_id": normalized["plan_id"],
        "critical_node_failures": node_failures,
        "critical_link_failures": link_failures,
        "tested_node_failures": len(normalized["nodes"]),
        "tested_link_failures": len(normalized["links"]),
        "baseline_reachable_zone_ids": sorted(baseline_zones),
        "unknown_links_counted_as_redundancy": False,
        "operational_failover_performed": False,
    }


def assess_communications_zone_coverage(plan: dict) -> dict:
    """Measure declared service-zone coverage and distinct reachable gateways."""
    normalized = _normalize_plan(plan)
    connectivity = _connectivity(normalized)
    rows = []
    zones = {item["zone_id"]: item for item in normalized["zones"]}
    nodes = {item["node_id"]: item for item in normalized["nodes"]}
    for zone_id in sorted(zones):
        service_nodes = sorted(
            node_id for node_id, node in nodes.items()
            if zone_id in node["service_zones"]
        )
        reachable_nodes = set(connectivity["reachable_node_ids"])
        providers = [node_id for node_id in service_nodes if node_id in reachable_nodes]
        gateway_ids = connectivity["zone_gateway_ids"][zone_id]
        rows.append({
            "zone_id": zone_id,
            "service_node_ids": service_nodes,
            "reachable_service_node_ids": providers,
            "reachable_gateway_ids": gateway_ids,
            "reachable_gateway_count": len(gateway_ids),
            "coverage_status": (
                "no_declared_path" if not gateway_ids else
                "multi_gateway_path" if len(gateway_ids) >= 2 else
                "single_gateway_path"
            ),
            "demand_kbps": zones[zone_id]["demand_kbps"],
        })
    covered = sum(bool(item["reachable_gateway_ids"]) for item in rows)
    known_demands = [item for item in rows if item["demand_kbps"] is not None]
    total_demand = sum(item["demand_kbps"] for item in known_demands)
    weighted = None
    if len(known_demands) == len(rows) and total_demand > 0:
        weighted = sum(
            item["demand_kbps"] for item in rows if item["reachable_gateway_ids"]
        ) / total_demand
    return {
        "plan_id": normalized["plan_id"],
        "zones": rows,
        "covered_zone_count": covered,
        "zone_coverage_ratio": covered / len(rows) if rows else 0.0,
        "demand_weighted_coverage_ratio": weighted,
        "demand_weighted_coverage_available": weighted is not None,
        "coverage_is_geographic_or_field_verified": False,
    }


def _max_flow_for_zone(plan: dict, zone_id: str, failed_nodes=None,
                       failed_links=None) -> dict:
    failed_nodes, failed_links = _validate_failures(plan, failed_nodes or (), failed_links or ())
    active = {item["node_id"] for item in plan["nodes"]} - failed_nodes
    source, sink = "__ssswet_source__", "__ssswet_sink__"
    graph: dict[str, list[list]] = {}
    original_edges = []

    def add_edge(start: str, end: str, capacity: float, link_id: str | None = None):
        left = graph.setdefault(start, [])
        right = graph.setdefault(end, [])
        forward = [end, capacity, len(right), link_id, capacity]
        reverse = [start, 0.0, len(left), None, 0.0]
        left.append(forward)
        right.append(reverse)
        if link_id is not None:
            original_edges.append((start, len(left) - 1, link_id, capacity))

    capacities = []
    for link in plan["links"]:
        if link["status"] != "available" or link["link_id"] in failed_links:
            continue
        if link["from_node"] not in active or link["to_node"] not in active:
            continue
        capacity, reserved = link["capacity_kbps"], link["reserved_kbps"]
        if capacity is None or reserved is None:
            continue
        residual = capacity - reserved
        if residual <= 0:
            continue
        capacities.append(residual)
    infinity = sum(capacities) + 1.0
    if infinity <= 1.0:
        infinity = 1.0
    for gateway in plan["gateways"]:
        if gateway in active:
            add_edge(source, "node:" + gateway, infinity)
    service_nodes = sorted(
        node["node_id"] for node in plan["nodes"]
        if node["node_id"] in active and zone_id in node["service_zones"]
    )
    for node_id in service_nodes:
        add_edge("node:" + node_id, sink, infinity)
    for link in plan["links"]:
        if link["status"] != "available" or link["link_id"] in failed_links:
            continue
        u, v = link["from_node"], link["to_node"]
        if u not in active or v not in active:
            continue
        capacity, reserved = link["capacity_kbps"], link["reserved_kbps"]
        if capacity is None or reserved is None or capacity <= reserved:
            continue
        residual = capacity - reserved
        add_edge("node:" + u, "node:" + v, residual, link["link_id"])
        if link["direction"] == "bidirectional":
            add_edge("node:" + v, "node:" + u, residual, link["link_id"])

    flow = 0.0
    while True:
        parent: dict[str, tuple[str, int] | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            current = queue.popleft()
            for index, edge in enumerate(graph.get(current, [])):
                target, capacity = edge[0], edge[1]
                if capacity > 1e-12 and target not in parent:
                    parent[target] = (current, index)
                    queue.append(target)
        if sink not in parent:
            break
        amount = float("inf")
        current = sink
        while parent[current] is not None:
            previous, index = parent[current]
            amount = min(amount, graph[previous][index][1])
            current = previous
        current = sink
        while parent[current] is not None:
            previous, index = parent[current]
            edge = graph[previous][index]
            edge[1] -= amount
            graph[current][edge[2]][1] += amount
            current = previous
        flow += amount

    reachable = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for edge in graph.get(current, []):
            if edge[1] > 1e-12 and edge[0] not in reachable:
                reachable.add(edge[0])
                queue.append(edge[0])
    cut = sorted({
        link_id for start, index, link_id, capacity in original_edges
        if capacity > 0 and start in reachable and graph[start][index][0] not in reachable
    })
    return {
        "maximum_flow_kbps": flow,
        "minimum_cut_link_ids": cut,
        "service_node_ids": service_nodes,
        "capacity_known_link_count": len(capacities),
    }


def assess_communications_bandwidth(plan: dict, *, zone_ids=None) -> dict:
    """Compute independent max-flow upper bounds for up to 50 selected service zones."""
    normalized = _normalize_plan(plan)
    all_zone_ids = {item["zone_id"] for item in normalized["zones"]}
    if zone_ids is None:
        selected = sorted(all_zone_ids)
    else:
        if not isinstance(zone_ids, (list, tuple)) or len(zone_ids) > MAX_BANDWIDTH_ZONES:
            raise ValueError(f"zone_ids must contain at most {MAX_BANDWIDTH_ZONES} zones")
        selected = [identifier(value, "zone_id", 160) for value in zone_ids]
        if len(selected) != len(set(selected)):
            raise ValueError("zone_ids must not contain duplicates")
        if set(selected) - all_zone_ids:
            raise ValueError("zone_ids references an unknown service zone")
        selected = sorted(selected)
    if len(selected) > MAX_BANDWIDTH_ZONES:
        raise ValueError(f"bandwidth analysis is limited to {MAX_BANDWIDTH_ZONES} zones per call; use zone_ids batches")
    rows = []
    zone_by_id = {item["zone_id"]: item for item in normalized["zones"]}
    for zone_id in selected:
        zone = zone_by_id[zone_id]
        result = _max_flow_for_zone(normalized, zone_id)
        demand = zone["demand_kbps"]
        shortage = None if demand is None else max(0.0, demand - result["maximum_flow_kbps"])
        rows.append({
            "zone_id": zone_id,
            "demand_kbps": demand,
            "maximum_flow_kbps": result["maximum_flow_kbps"],
            "shortage_kbps": shortage,
            "capacity_status": (
                "demand_unknown" if demand is None else
                "no_declared_capacity_path" if result["maximum_flow_kbps"] <= 0 else
                "declared_capacity_shortfall" if shortage > 1e-9 else
                "declared_capacity_covers_demand"
            ),
            "minimum_cut_link_ids": result["minimum_cut_link_ids"],
            "service_node_ids": result["service_node_ids"],
            "capacity_known_link_count": result["capacity_known_link_count"],
        })
    return {
        "plan_id": normalized["plan_id"],
        "zones": rows,
        "analyzed_zone_ids": selected,
        "unassessed_zone_ids": sorted(all_zone_ids - set(selected)),
        "max_zones_per_call": MAX_BANDWIDTH_ZONES,
        "independent_per_zone_upper_bounds": True,
        "shared_bandwidth_jointly_allocated": False,
        "measured_throughput_established": False,
    }


def estimate_relay_power_autonomy(plan: dict, *, minimum_runtime_hours: float) -> dict:
    """Estimate declared relay runtime; missing energy/load/fraction remains unknown."""
    normalized = _normalize_plan(plan)
    threshold = _number(minimum_runtime_hours, "minimum_runtime_hours")
    rows = []
    for node in normalized["nodes"]:
        battery, load, usable = node["battery_wh"], node["load_w"], node["usable_fraction"]
        if battery is None or load is None or usable is None:
            rows.append({
                "node_id": node["node_id"],
                "status": "unknown_missing_declared_power_data",
                "runtime_hours": None,
                "reserve_margin_hours": None,
            })
            continue
        if load <= 0:
            rows.append({
                "node_id": node["node_id"],
                "status": "invalid_zero_load",
                "runtime_hours": None,
                "reserve_margin_hours": None,
            })
            continue
        runtime = battery * usable / load
        rows.append({
            "node_id": node["node_id"],
            "status": "below_declared_minimum" if runtime < threshold else "meets_declared_minimum",
            "usable_energy_wh": battery * usable,
            "declared_load_w": load,
            "runtime_hours": runtime,
            "reserve_margin_hours": runtime - threshold,
        })
    return {
        "plan_id": normalized["plan_id"],
        "minimum_runtime_hours": threshold,
        "nodes": rows,
        "battery_health_or_field_runtime_verified": False,
    }


def _shortest_route(plan: dict, source: str, zone_id: str, *, payload_kb: float = 0.0):
    graph = _adjacency(plan, require_capacity=True, require_latency=True)
    targets = {
        node["node_id"] for node in plan["nodes"]
        if zone_id in node["service_zones"]
    }
    if source not in graph or not targets:
        return None
    initial = (0.0, (source,), (), source)
    heap = [initial]
    best = {source: (0.0, (source,), ())}
    while heap:
        cost, path, link_path, current = heapq.heappop(heap)
        if best.get(current) != (cost, path, link_path):
            continue
        if current in targets:
            return {"nodes": list(path), "links": list(link_path), "delay_ms": cost}
        for target, link, residual in graph.get(current, []):
            if residual is None or residual <= 0 or link["latency_ms"] is None:
                continue
            serialization_ms = payload_kb * 8.0 / residual * 1000.0
            candidate = (
                cost + link["latency_ms"] + serialization_ms,
                path + (target,),
                link_path + (link["link_id"],),
            )
            previous = best.get(target)
            if previous is None or candidate < previous:
                best[target] = candidate
                heapq.heappush(heap, (*candidate, target))
    return None


def plan_communications_message_routes(plan: dict, messages: list[dict]) -> dict:
    """Estimate paths from message metadata only; message bodies are not accepted."""
    normalized = _normalize_plan(plan)
    messages = _records(messages, "messages", MAX_MESSAGES)
    seen = set()
    rows = []
    zone_ids = {item["zone_id"] for item in normalized["zones"]}
    node_ids = {item["node_id"] for item in normalized["nodes"]}
    for item in messages:
        if set(item) - {"message_id", "from_node", "to_zone", "payload_kb", "ttl_seconds", "priority"}:
            raise ValueError("message metadata contains unsupported fields")
        message_id = identifier(item.get("message_id"), "message_id", 160)
        if message_id in seen:
            raise ValueError("message_id values must be unique")
        seen.add(message_id)
        source = identifier(item.get("from_node"), "from_node", 160)
        zone = identifier(item.get("to_zone"), "to_zone", 160)
        if source not in node_ids or zone not in zone_ids:
            raise ValueError("message references an unknown node or zone")
        payload = _number(item.get("payload_kb"), "payload_kb")
        ttl = _number(item.get("ttl_seconds"), "ttl_seconds", minimum=0.000000001)
        priority = item.get("priority", 1)
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("message priority must be an integer from 1 to 5")
        route = _shortest_route(normalized, source, zone, payload_kb=payload)
        if route is None:
            rows.append({
                "message_id": message_id, "status": "no_declared_route",
                "path_node_ids": [], "path_link_ids": [],
                "estimated_delivery_seconds": None,
            })
            continue
        seconds = route["delay_ms"] / 1000.0
        rows.append({
            "message_id": message_id,
            "status": "estimated_within_ttl" if seconds <= ttl else "estimated_ttl_exceeded",
            "path_node_ids": route["nodes"],
            "path_link_ids": route["links"],
            "estimated_delivery_seconds": seconds,
            "ttl_seconds": ttl,
            "priority": priority,
        })
    return {
        "plan_id": normalized["plan_id"],
        "messages": rows,
        "message_bodies_collected": False,
        "queueing_retransmission_interference_and_radio_conditions_modelled": False,
        "delivery_established": False,
    }


def assess_communications_traffic_load(plan: dict, traffic_flows: list[dict], *,
                                       warning_utilization: float = 0.8) -> dict:
    """Screen aggregate offered load along deterministic lowest-latency paths."""
    normalized = _normalize_plan(plan)
    flows = _records(traffic_flows, "traffic_flows", MAX_TRAFFIC_FLOWS)
    warning = _number(warning_utilization, "warning_utilization", minimum=0.000000001, maximum=1.0)
    seen = set()
    link_loads = {}
    flow_rows = []
    node_ids = {item["node_id"] for item in normalized["nodes"]}
    zone_ids = {item["zone_id"] for item in normalized["zones"]}
    link_by_id = {item["link_id"]: item for item in normalized["links"]}
    for item in flows:
        if set(item) - {"flow_id", "from_node", "to_zone", "offered_kbps", "priority"}:
            raise ValueError("traffic flow contains unsupported fields")
        flow_id = identifier(item.get("flow_id"), "flow_id", 160)
        if flow_id in seen:
            raise ValueError("flow_id values must be unique")
        seen.add(flow_id)
        source = identifier(item.get("from_node"), "from_node", 160)
        zone = identifier(item.get("to_zone"), "to_zone", 160)
        if source not in node_ids or zone not in zone_ids:
            raise ValueError("traffic flow references an unknown node or zone")
        offered = _number(item.get("offered_kbps"), "offered_kbps")
        priority = item.get("priority", 1)
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
            raise ValueError("traffic priority must be an integer from 1 to 5")
        route = _shortest_route(normalized, source, zone)
        if route is None:
            flow_rows.append({"flow_id": flow_id, "status": "no_declared_route", "path_link_ids": []})
            continue
        for link_id in route["links"]:
            link_loads[link_id] = link_loads.get(link_id, 0.0) + offered
        flow_rows.append({
            "flow_id": flow_id, "status": "path_estimated",
            "path_node_ids": route["nodes"], "path_link_ids": route["links"],
            "offered_kbps": offered, "priority": priority,
        })
    link_rows = []
    for link_id, offered in sorted(link_loads.items()):
        link = link_by_id[link_id]
        capacity, reserved = link["capacity_kbps"], link["reserved_kbps"]
        if capacity is None or reserved is None or capacity <= 0:
            utilization = None
            status = "capacity_unknown"
        else:
            utilization = (reserved + offered) / capacity
            status = (
                "over_capacity" if utilization > 1.0 else
                "near_capacity" if utilization >= warning else
                "within_declared_capacity"
            )
        link_rows.append({
            "link_id": link_id, "offered_kbps": offered,
            "reserved_kbps": reserved, "capacity_kbps": capacity,
            "utilization_ratio": utilization, "status": status,
        })
    return {
        "plan_id": normalized["plan_id"],
        "flows": flow_rows,
        "links": link_rows,
        "over_capacity_link_ids": sorted(item["link_id"] for item in link_rows if item["status"] == "over_capacity"),
        "traffic_reserved_or_shaped": False,
        "packet_delivery_established": False,
    }


def compare_communications_outage_scenarios(plan: dict, scenarios: list[dict]) -> dict:
    """Compare up to 100 declared outages with the unchanged baseline plan."""
    normalized = _normalize_plan(plan)
    scenarios = _records(scenarios, "scenarios", MAX_SCENARIOS)
    baseline = _connectivity(normalized)
    baseline_zones = set(baseline["reachable_zone_ids"])
    seen = set()
    rows = []
    for item in scenarios:
        if set(item) - {"scenario_id", "failed_node_ids", "failed_link_ids"}:
            raise ValueError("scenario contains unsupported fields")
        scenario_id = identifier(item.get("scenario_id"), "scenario_id", 160)
        if scenario_id in seen:
            raise ValueError("scenario_id values must be unique")
        seen.add(scenario_id)
        failed_nodes, failed_links = _validate_failures(
            normalized, item.get("failed_node_ids", []), item.get("failed_link_ids", [])
        )
        after = _connectivity(normalized, failed_nodes, failed_links)
        reachable = set(after["reachable_zone_ids"])
        rows.append({
            "scenario_id": scenario_id,
            "failed_node_ids": sorted(failed_nodes),
            "failed_link_ids": sorted(failed_links),
            "reachable_zone_ids": sorted(reachable),
            "lost_zone_ids": sorted(baseline_zones - reachable),
            "newly_unreachable_zone_ids": sorted(baseline_zones - reachable),
            "reachable_zone_count": len(reachable),
            "baseline_reachable_zone_count": len(baseline_zones),
        })
    return {
        "plan_id": normalized["plan_id"],
        "baseline_reachable_zone_ids": sorted(baseline_zones),
        "scenarios": rows,
        "scenario_count": len(rows),
        "plan_mutated": False,
        "live_outage_performed": False,
        "automatic_failover_performed": False,
    }


def _assessment_digests(assessments: dict) -> dict[str, str]:
    if not isinstance(assessments, dict) or len(assessments) > 10:
        raise ValueError("assessments must be an object with at most 10 named results")
    if any(not isinstance(name, str) for name in assessments):
        raise ValueError("assessment names must be strings")
    result = {}
    for name in sorted(assessments):
        key = identifier(name, "assessment_name", 80)
        if key in result:
            raise ValueError("assessment names must remain unique after normalization")
        encoded = canonical_bytes(assessments[name])
        if len(encoded) > 100_000:
            raise ValueError("each assessment must not exceed 100000 canonical bytes")
        result[key] = digest(assessments[name])
    return result


def build_communications_assurance_manifest(plan: dict, assessments: dict, *,
                                             evidence_refs=()) -> dict:
    """Build a deterministic metadata-only integrity manifest for reviewed outputs."""
    normalized = _normalize_plan(plan)
    assessment_hashes = _assessment_digests(assessments)
    refs = _refs(evidence_refs, "evidence_refs", MAX_EVIDENCE_REFS)
    body = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": normalized["plan_id"],
        "plan_sha256": digest(normalized),
        "assessment_sha256": assessment_hashes,
        "evidence_refs": refs,
        "limits": {
            "max_nodes": MAX_NODES, "max_links": MAX_LINKS,
            "max_zones": MAX_ZONES, "max_messages": MAX_MESSAGES,
            "max_traffic_flows": MAX_TRAFFIC_FLOWS,
            "max_scenarios": MAX_SCENARIOS,
            "max_bandwidth_zones_per_call": MAX_BANDWIDTH_ZONES,
        },
        "unknown_links_are_traversable": False,
        "message_content_included": False,
        "live_network_activity_performed": False,
        "dispatch_authorized": False,
        "safety_certified": False,
        "interpretation": "Integrity metadata for caller-declared planning inputs; not operational telemetry, certification or authorization.",
    }
    return {**body, "manifest_sha256": digest(body)}


def verify_communications_assurance_manifest(manifest: dict, *, plan: dict | None = None,
                                             assessments: dict | None = None) -> dict:
    """Verify manifest integrity and, when supplied, the referenced input digests."""
    if not isinstance(manifest, dict):
        return {"valid": False, "reasons": ["manifest_not_object"], "authorship_authenticated": False}
    required = {
        "schema_version", "plan_id", "plan_sha256", "assessment_sha256",
        "evidence_refs", "limits", "unknown_links_are_traversable",
        "message_content_included", "live_network_activity_performed",
        "dispatch_authorized", "safety_certified", "interpretation",
        "manifest_sha256",
    }
    if set(manifest) != required:
        return {"valid": False, "reasons": ["manifest_schema_invalid"], "authorship_authenticated": False}
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    reasons = []
    try:
        expected = digest(body)
    except ValueError:
        return {"valid": False, "reasons": ["manifest_not_canonical"], "authorship_authenticated": False}
    version = manifest.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        reasons.append("manifest_schema_version_invalid")
    try:
        identifier(manifest.get("plan_id"), "plan_id", 160)
    except ValueError:
        reasons.append("manifest_plan_id_invalid")
    plan_hash = manifest.get("plan_sha256")
    if not isinstance(plan_hash, str) or len(plan_hash) != 64 or any(ch not in "0123456789abcdef" for ch in plan_hash):
        reasons.append("manifest_plan_digest_invalid")
    assessment_hashes = manifest.get("assessment_sha256")
    if not isinstance(assessment_hashes, dict) or len(assessment_hashes) > 10:
        reasons.append("manifest_assessment_digests_invalid")
    else:
        seen_assessment_names = set()
        for key, value in assessment_hashes.items():
            try:
                normalized_name = identifier(key, "assessment_name", 80)
            except ValueError:
                reasons.append("manifest_assessment_digests_invalid")
                break
            if normalized_name != key or normalized_name in seen_assessment_names:
                reasons.append("manifest_assessment_digests_invalid")
                break
            seen_assessment_names.add(normalized_name)
            if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                reasons.append("manifest_assessment_digests_invalid")
                break
    try:
        if not isinstance(manifest.get("evidence_refs"), list):
            raise ValueError("manifest evidence_refs must be a list")
        _refs(manifest.get("evidence_refs"), "evidence_refs", MAX_EVIDENCE_REFS)
    except ValueError:
        reasons.append("manifest_evidence_refs_invalid")
    expected_limits = {
        "max_nodes": MAX_NODES, "max_links": MAX_LINKS,
        "max_zones": MAX_ZONES, "max_messages": MAX_MESSAGES,
        "max_traffic_flows": MAX_TRAFFIC_FLOWS,
        "max_scenarios": MAX_SCENARIOS,
        "max_bandwidth_zones_per_call": MAX_BANDWIDTH_ZONES,
    }
    if manifest.get("limits") != expected_limits:
        reasons.append("manifest_limits_invalid")
    if any(manifest.get(name) is not False for name in (
        "unknown_links_are_traversable", "message_content_included",
        "live_network_activity_performed", "dispatch_authorized", "safety_certified",
    )):
        reasons.append("manifest_safety_flags_invalid")
    if not isinstance(manifest.get("interpretation"), str):
        reasons.append("manifest_interpretation_invalid")
    if manifest.get("manifest_sha256") != expected:
        reasons.append("manifest_digest_mismatch")
    if plan is not None:
        try:
            if manifest.get("plan_sha256") != digest(_normalize_plan(plan)):
                reasons.append("plan_digest_mismatch")
        except ValueError:
            reasons.append("plan_invalid")
    if assessments is not None:
        try:
            if manifest.get("assessment_sha256") != _assessment_digests(assessments):
                reasons.append("assessment_digest_mismatch")
        except (ValueError, TypeError):
            reasons.append("assessments_invalid")
    return {
        "valid": not reasons,
        "reasons": reasons,
        "authorship_authenticated": False,
        "deployment_authorized": False,
    }
