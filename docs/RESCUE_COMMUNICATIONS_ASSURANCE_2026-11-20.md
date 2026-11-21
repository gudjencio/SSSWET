# Civil-rescue communications assurance

**Status:** opt-in, offline planning utilities  
**Schema:** version 1  
**Runtime dependencies:** Python standard library only

## Purpose

SSSWET already provides civil-rescue action allowlists, physical-route redundancy, resource allocation, scenario robustness and safety-case preparation. Those modules do not model a declared communications network as a directed/bidirectional graph with service zones, link capacity, reserved bandwidth, latency and relay power.

This module adds that missing planning layer. It accepts only caller-supplied metadata and performs deterministic analysis locally. It does not connect to radios, inspect networks, transmit messages, change configurations, dispatch responders or make evacuation decisions.

## Ten capabilities

| # | Public function | Capability |
|---:|---|---|
| 1 | \`validate_communications_plan\` | Strict allowlisted schema, reference validation, deterministic normalization and bounded input |
| 2 | \`analyze_communications_connectivity\` | Directed/bidirectional reachability from declared gateways; unknown/blocked links are unavailable |
| 3 | \`identify_communications_single_points_of_failure\` | Individual node/link removal tests and affected service-zone reporting |
| 4 | \`assess_communications_zone_coverage\` | Declared service-zone coverage and distinct reachable-gateway counts |
| 5 | \`assess_communications_bandwidth\` | Per-zone maximum-flow/minimum-cut upper bounds after reserved bandwidth |
| 6 | \`estimate_relay_power_autonomy\` | Declared Wh/W runtime estimate with explicit usable-energy fraction |
| 7 | \`plan_communications_message_routes\` | Lowest-estimated-delay path and TTL screening using metadata only |
| 8 | \`assess_communications_traffic_load\` | Aggregate offered-load utilization and overloaded-link candidates |
| 9 | \`compare_communications_outage_scenarios\` | Bounded baseline-versus-outage comparison without changing the plan |
| 10 | \`build_communications_assurance_manifest\` / \`verify_communications_assurance_manifest\` | Deterministic plan/assessment hashes, evidence references and tamper detection |

## Input contract

A plan has exactly these top-level fields:

- \`schema_version\`: integer \`1\` (boolean values are rejected).
- \`plan_id\`: non-empty identifier.
- \`nodes\`: unique \`node_id\`, role (\`gateway\`, \`relay\`, \`endpoint\`), declared \`service_zones\`, and optional power fields.
- \`links\`: unique \`link_id\`, existing endpoints, \`direction\` (\`directed\` or \`bidirectional\`), \`status\` (\`available\`, \`blocked\`, \`unknown\`), and optional capacity/reservation/latency values.
- \`zones\`: unique \`zone_id\`, priority 1–5 and optional declared demand in kbps.
- \`gateways\`: non-empty list of node IDs whose role is \`gateway\`.

Unrecognized fields are rejected. This prevents credentials, URLs, message bodies, personal data and device-specific secrets from being accidentally accepted as plan metadata. Evidence references are short caller-supplied identifiers, not credentials or raw source content.

### Limits

| Input | Maximum |
|---|---:|
| Nodes | 250 |
| Links | 1,000 |
| Service zones | 250 |
| Messages per route-planning call | 500 |
| Traffic flows per load assessment | 500 |
| Outage scenarios | 100 |
| Canonical normalized plan | 1 MiB |
| Evidence references in a manifest | 500 |
| Assessment outputs in a manifest | 10 |
| Canonical size per assessment | 100,000 bytes |
| Bandwidth zones per call | 50 |

For a plan with more than 50 zones, call \`assess_communications_bandwidth(plan, zone_ids=[...])\` in explicit batches. The result identifies unassessed zones; it never implies that omitted zones passed. The `independent_per_zone_upper_bounds` flag describes only analyzed rows and is false for an empty batch. `declared_capacity_assessment_complete` is true only when every plan zone was selected and all required capacity inputs are known; partial and empty batches keep it false.

Unknown links are never traversable, never count as redundancy, and never contribute capacity. A link with unknown capacity/reservation or latency can still be used for topological reachability when its status is explicitly \`available\`, but it is excluded from calculations that require the missing quantity.

## Example

\`\`\`python
from ssswet_core.rescue_communications_assurance import (
    validate_communications_plan,
    analyze_communications_connectivity,
    assess_communications_zone_coverage,
    assess_communications_bandwidth,
    estimate_relay_power_autonomy,
    build_communications_assurance_manifest,
    verify_communications_assurance_manifest,
)

plan = {
    "schema_version": 1,
    "plan_id": "community-relay-r1",
    "nodes": [
        {"node_id": "gateway-1", "role": "gateway", "service_zones": [],
         "battery_wh": 120, "load_w": 10, "usable_fraction": 0.8},
        {"node_id": "relay-1", "role": "relay", "service_zones": ["shelter-a"],
         "service_capacity_kbps": 256, "service_reserved_kbps": 32},
    ],
    "links": [
        {"link_id": "link-1", "from_node": "gateway-1", "to_node": "relay-1",
         "direction": "bidirectional", "status": "available",
         "capacity_kbps": 256, "reserved_kbps": 32, "latency_ms": 40},
    ],
    "zones": [{"zone_id": "shelter-a", "demand_kbps": 100, "priority": 5}],
    "gateways": ["gateway-1"],
}

validation = validate_communications_plan(plan)
connectivity = analyze_communications_connectivity(plan)
coverage = assess_communications_zone_coverage(plan)
bandwidth = assess_communications_bandwidth(plan)
power = estimate_relay_power_autonomy(plan, minimum_runtime_hours=6)

assessments = {
    "connectivity": connectivity,
    "coverage": coverage,
    "bandwidth": bandwidth,
    "power": power,
}
manifest = build_communications_assurance_manifest(
    plan, assessments, evidence_refs=["field-study:example", "protocol:relay-r1"]
)
verification = verify_communications_assurance_manifest(
    manifest, plan=plan, assessments=assessments
)
assert verification["valid"]
\`\`\`

The example is illustrative metadata, not a recommended radio configuration or a validated field design.

## Interpretation rules

### Connectivity and coverage

Only explicitly available links count. A directed link can be traversed only from \`from_node\` to \`to_node\`; a bidirectional link can be traversed in either direction. A service zone is topologically reachable if at least one node declares it and at least one declared gateway has a path to that node.

Coverage is not geographic radio coverage, signal-strength measurement, building penetration, interoperability, public availability or a field survey. Distinct gateways indicate graph-path redundancy only.

### Single points of failure

Each declared node and link is removed individually from a copy of the in-memory graph. The report lists baseline-reachable zones that become unreachable and sums their declared demand; zones with unknown demand are listed separately and make the demand total incomplete. It does not test correlated failures, common power sources, shared spectrum, shared physical ducts, weather, cyber incidents or simultaneous failures unless those are represented by a caller-supplied outage scenario.

### Bandwidth

For each selected zone, a maximum-flow calculation uses \`capacity_kbps - reserved_kbps\` on explicitly available links. The minimum cut identifies declared links that bound the modeled flow.

Each zone is analyzed independently. Capacity is not jointly allocated across zones; summing per-zone upper bounds can overstate what one shared network can deliver. These are declared-capacity upper bounds, not measured throughput or guaranteed service.

### Power autonomy

The estimate is:

\`runtime_hours = battery_wh × usable_fraction / load_w\`

All three values must be supplied. Missing values remain unknown. This does not model battery aging, temperature, conversion loss beyond the declared usable fraction, intermittent loads, generator behavior or real-world runtime. The caller's minimum-runtime threshold is a review threshold, not a safety recommendation.

### Message paths

Only message identifiers, source node, target zone, payload size, TTL and priority are accepted; message text/content is rejected. Estimated path delay is the sum of declared link latency and serialization time:

\`serialization_ms = payload_kb × 8 / residual_capacity_kbps × 1000\`

Queueing, contention, retransmission, interference, radio modulation, routing-protocol convergence and actual delivery are not modeled. A route estimate is not permission to transmit or evidence that a message arrived.

### Traffic load

Flows are routed independently on deterministic lowest-latency paths. The tool adds declared offered load to each selected link and compares it with declared reserved and total capacity. It does not reserve bandwidth, shape traffic, schedule messages or optimize all flows jointly. Over-capacity findings are planning warnings.

### Outage scenarios

Each scenario names failed nodes and links. The baseline is retained and compared with each scenario, including lost declared demand and any zones whose demand is unknown. The plan is never mutated and no live outage is performed. The result does not trigger automatic failover.

### Assurance manifests

Manifests contain canonical SHA-256 digests for the normalized plan and named assessment outputs, plus caller-supplied evidence identifiers. Verification detects accidental or deliberate content changes relative to the recorded digest. A plain hash does not authenticate the author, prove source authenticity, establish scientific validity or provide non-repudiation.

## Comparison with previous behaviour

Before this addition, SSSWET had:
- physical civil-rescue route redundancy over undirected route segments;
- resource allocation and demand/supply scenario ranges;
- a conservative rescue-action allowlist containing \`communications_relay\`;
- general safety-case and protective-design assurance.

There was no dedicated offline communications-network model for directed links, gateway-to-zone reachability, relay power estimates, per-zone bandwidth upper bounds, message TTL estimates, aggregate traffic utilization and repeatable outage comparison. The new module is additive; the existing physical-route, resource-planning, safety-case and workflow APIs are unchanged.

## Regression and safety boundaries

- No network scanning, socket access, packet capture, API calls or radio configuration.
- No message bodies, personal data, credentials, IP addresses, phone numbers or exact shelter coordinates.
- No unknown-link optimism or automatic imputation of missing capacity, latency, battery energy or load.
- No dispatch, evacuation, medical, eligibility or operational decision.
- No safety certification, legal authorization, coverage guarantee or deployment approval.
- No runtime dependency or persistent database change.

## Reproducible validation

Focused tests cover schema limits, directed reachability, unknown-link rejection, single-point detection, gateway redundancy, hand-calculated max-flow/min-cut, Wh/W autonomy, message serialization and TTL, overload detection, outage comparison, deterministic manifests and tamper detection.

The synthetic benchmark uses 100 nodes, 116 links, 20 service zones, 100 message metadata records, 100 traffic flows and 32 outage scenarios. The CI p95 budget is 2,000 ms per probe. Results are runner-specific software measurements, not field performance.

Acceptance criteria and regression risks were recorded before implementation in [Run 8 pre-implementation plan](UPGRADE_PLAN_2026-11-20_RUN_8.md).
