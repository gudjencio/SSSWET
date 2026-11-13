"""Structured safety-case graph diagnostics for independent human review."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

MAX_NODES = 2_000
MAX_EDGES = 5_000
MAX_REVIEWERS = 500
_NODE_TYPES = {"claim", "argument", "evidence", "hazard", "control"}
_RELATIONS = {"supports", "rebuts", "addresses", "mitigates", "decomposes"}


def _identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 160:
        raise ValueError(f"{field} must contain 1 to 160 characters")
    return value.strip()


def audit_safety_case(
    *, owner_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]],
    top_level_claim_ids: list[str], reviewers: list[dict[str, Any]],
    owner_independence_group: str = "",
) -> dict[str, Any]:
    """Audit traceability and review gaps; this function never approves a safety case."""
    owner = _identifier(owner_id, "owner_id")
    owner_group = owner_independence_group.strip() if isinstance(owner_independence_group, str) else ""
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= MAX_NODES:
        raise ValueError(f"nodes must contain 1 to {MAX_NODES} records")
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        raise ValueError(f"edges must contain at most {MAX_EDGES} records")
    if not isinstance(top_level_claim_ids, list) or not top_level_claim_ids:
        raise ValueError("at least one top-level claim ID is required")
    if not isinstance(reviewers, list) or len(reviewers) > MAX_REVIEWERS:
        raise ValueError(f"reviewers must contain at most {MAX_REVIEWERS} records")

    node_map = {}
    for item in nodes:
        if not isinstance(item, dict):
            raise ValueError("every node must be an object")
        node_id = _identifier(item.get("node_id"), "node_id")
        node_type = item.get("node_type")
        if node_type not in _NODE_TYPES:
            raise ValueError("unsupported safety-case node_type")
        if node_id in node_map:
            raise ValueError("node IDs must be unique")
        state = item.get("state", "active")
        if state not in {"active", "under_review", "withdrawn", "superseded"}:
            raise ValueError("unsupported node state")
        node_map[node_id] = {"node_type": node_type, "state": state}

    top_ids = sorted({_identifier(item, "top_level_claim_id") for item in top_level_claim_ids})
    if len(top_ids) != len(top_level_claim_ids):
        raise ValueError("top-level claim IDs must be unique")
    invalid_top = [item for item in top_ids if item not in node_map or node_map[item]["node_type"] != "claim"]

    normalized_edges = []
    dangling = []
    adjacency = defaultdict(list)
    incoming_support = defaultdict(list)
    mitigated_hazards = set()
    rebutted_claims = set()
    for item in edges:
        if not isinstance(item, dict):
            raise ValueError("every edge must be an object")
        source = _identifier(item.get("source_id"), "edge.source_id")
        target = _identifier(item.get("target_id"), "edge.target_id")
        relation = item.get("relation")
        if relation not in _RELATIONS:
            raise ValueError("unsupported safety-case relation")
        if source not in node_map or target not in node_map:
            dangling.append({"source_id": source, "target_id": target, "relation": relation})
            continue
        normalized_edges.append((source, target, relation))
        if relation in {"supports", "decomposes"}:
            adjacency[source].append(target)
        if relation == "supports":
            incoming_support[target].append(source)
        if relation == "mitigates" and node_map[target]["node_type"] == "hazard":
            mitigated_hazards.add(target)
        if relation == "rebuts" and node_map[target]["node_type"] == "claim":
            rebutted_claims.add(target)

    # Iterative colour DFS avoids recursion-depth failures on long public graphs.
    colour = {key: 0 for key in node_map}
    cycles = []
    for start in sorted(node_map):
        if colour[start]:
            continue
        stack = [(start, 0)]
        colour[start] = 1
        while stack:
            current, index = stack[-1]
            neighbours = sorted(adjacency.get(current, []))
            if index >= len(neighbours):
                colour[current] = 2
                stack.pop()
                continue
            target = neighbours[index]
            stack[-1] = (current, index + 1)
            if colour[target] == 1:
                cycles.append({"from": current, "to": target})
            elif colour[target] == 0:
                colour[target] = 1
                stack.append((target, 0))

    unsupported_claims = [
        claim_id for claim_id in top_ids
        if claim_id in node_map and not any(
            node_map.get(source, {}).get("node_type") == "argument"
            for source in incoming_support.get(claim_id, [])
        )
    ]
    unsupported_arguments = [
        key for key, value in node_map.items()
        if value["node_type"] == "argument" and not any(
            node_map.get(source, {}).get("node_type") == "evidence"
            for source in incoming_support.get(key, [])
        )
    ]
    unmitigated_hazards = sorted(
        key for key, value in node_map.items()
        if value["node_type"] == "hazard" and key not in mitigated_hazards
    )

    reviewer_map = {}
    for item in reviewers:
        if not isinstance(item, dict):
            raise ValueError("every reviewer must be an object")
        reviewer_id = _identifier(item.get("reviewer_id"), "reviewer_id")
        if reviewer_id in reviewer_map:
            raise ValueError("reviewer IDs must be unique")
        group = _identifier(item.get("independence_group"), "independence_group")
        reviewed = item.get("reviewed_node_ids", [])
        if not isinstance(reviewed, list) or len(reviewed) > MAX_NODES:
            raise ValueError("reviewed_node_ids must be a bounded list")
        reviewed_ids = sorted({_identifier(value, "reviewed_node_id") for value in reviewed})
        reviewer_map[reviewer_id] = {"group": group, "reviewed": set(reviewed_ids)}

    required_review_nodes = set(top_ids) | {
        key for key, value in node_map.items() if value["node_type"] == "hazard"
    }
    review_gaps, conflicts = [], []
    for node_id in sorted(required_review_nodes):
        eligible = []
        for reviewer_id, reviewer in reviewer_map.items():
            if node_id not in reviewer["reviewed"]:
                continue
            if reviewer_id == owner or (owner_group and reviewer["group"] == owner_group):
                conflicts.append({"node_id": node_id, "reviewer_id": reviewer_id, "reason": "owner_or_shared_independence_group"})
                continue
            eligible.append(reviewer_id)
        if not eligible:
            review_gaps.append(node_id)

    return {
        "top_level_claim_ids": top_ids,
        "invalid_top_level_claim_ids": invalid_top,
        "dangling_edges": dangling,
        "cycle_edges": cycles,
        "unsupported_top_level_claim_ids": unsupported_claims,
        "unsupported_argument_ids": sorted(unsupported_arguments),
        "unmitigated_hazard_ids": unmitigated_hazards,
        "claims_with_rebuttals": sorted(rebutted_claims & set(top_ids)),
        "independent_review_gaps": review_gaps,
        "reviewer_conflicts": conflicts,
        "edge_count": len(normalized_edges),
        "status": "review_gaps_found" if (
            invalid_top or dangling or cycles or unsupported_claims
            or unsupported_arguments or unmitigated_hazards or review_gaps
        ) else "structured_for_independent_review",
        "safety_case_approved": False,
        "certification_granted": False,
        "real_world_use_authorized": False,
    }
