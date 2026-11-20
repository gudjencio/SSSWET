# Run 8 pre-implementation plan — civil-rescue communications assurance

## Baseline inspected before implementation

- Current `main`: `47042caf0ab6349ecc557cecaead7aca7e5fa0f0` (merged PR #78).
- Immediate predecessor: `110f7c665822b66d2af3485911670ebb5c1808c7`.
- The one-commit comparison contains only the UTF-16-safe XML DTD preflight, two feed-parser regression cases plus valid UTF-16 Atom acceptance, and the corresponding public security note.
- Existing rescue modules inspected: `rescue_workflow.py`, `rescue_design_assurance.py`, `rescue_route_redundancy.py`, `rescue_resource_planner.py`, `rescue_scenario_robustness.py`, and `rescue_readiness.py`.
- Existing route redundancy covers undirected physical-route segments; the proposed module is a separate, directed/bidirectional communications-network planning utility with explicit link capacity, latency, service zones, and node power.
- Existing public rescue action allowlist already includes `communications_relay`, but no dedicated communications topology/capacity/power assurance module exists on current `main`.
- Open PRs #18, #19, #22, #24, #25, #26 and #27 were reviewed for overlap. This proposal does not modify their memory, agent deliberation, VTT, engineering-assurance, dataset-governance, energy-storage or local ledger paths.

## Proposed ten independently usable improvements

1. **Strict bounded plan contract** — validate node/link/zone/gateway schemas, unique IDs, references, status/direction enums, finite physical quantities, allowlisted fields and input limits.
2. **Directed reachability and gateway failover** — determine which nodes and service zones are reachable from declared gateways; unknown/blocked links never count as traversable.
3. **Single-point-of-failure analysis** — remove each declared node/link in turn and report the service zones and demand affected by that failure.
4. **Zone coverage and gateway redundancy** — distinguish no-path, single-gateway and multi-gateway service; report both zone-count and demand-weighted coverage when demand is known.
5. **Per-zone bandwidth upper bounds** — use bounded max-flow/min-cut analysis on declared available capacities after reserved bandwidth; keep zones independent and disclose that shared capacity is not jointly allocated.
6. **Relay power-autonomy screening** — estimate runtime only when battery energy, load and usable-energy fraction are all declared; otherwise preserve an unknown state.
7. **Message-path and TTL estimation** — select deterministic lowest-delay paths using declared latency and serialization time, while retaining payload size only (never message content).
8. **Traffic-load and bottleneck screening** — route declared aggregate flows, calculate link utilization and expose overload/near-capacity candidates without reserving or shaping traffic.
9. **Bounded outage-scenario comparison** — compare baseline and up to 100 caller-declared node/link failure scenarios, preserving unknown links as unavailable.
10. **Deterministic assurance manifest** — hash the normalized plan and named assessment outputs, retain evidence references, and verify tampering without authorizing deployment.

## Measurable acceptance criteria

- Plan limits: at most 250 nodes, 1,000 links, 250 zones, 500 messages/traffic flows and 100 outage scenarios; canonical plan <= 1 MiB. Per-zone max-flow is limited to 50 selected zones per call; larger plans must use explicit batches and report unassessed zones.
- Reject duplicate IDs, dangling node/zone/gateway references, unknown object fields, booleans used as numbers, non-finite values, negative capacities/loads, invalid fractions and invalid enums.
- A synthetic directed fixture must reach only zones connected by `available` links; `unknown` and `blocked` links must never create reachability.
- Failure analysis must identify a known bridge relay and bridge link, while leaving a parallel-path fixture non-critical.
- Coverage must report a zone served through two distinct gateways as multi-gateway and must not infer coverage from unknown links.
- A two-path capacity fixture must produce the exact max-flow value and identify a minimum-cut link set; unknown capacity must not be treated as zero-capacity evidence or infinite capacity.
- Power autonomy must match hand-calculated Wh/W results and report unknown when any required quantity is absent.
- Message route estimates must match hand-calculated hop latency plus serialization, and separately report no-path and TTL-exceeded states.
- Traffic-load screening must report utilization above 1.0 as overload without mutating the plan or claiming packet delivery.
- Scenario output must be deterministic and preserve the baseline; unknown links remain unavailable in every scenario.
- Equivalent normalized plans/assessment maps must produce identical SHA-256 manifests; any altered plan/assessment digest must fail verification.
- All outputs must explicitly state that they are planning estimates, not live telemetry, operational dispatch, safety certification or legal authorization.

## Regression risks and mitigations

- **Confusion with physical-route analysis:** use a distinct module and explicit directed/bidirectional communication links; do not change `rescue_route_redundancy.py`.
- **False connectivity:** unknown/blocked links are never traversable; only explicitly available links count.
- **Capacity double-counting:** compute a separate upper bound per service zone and state that cross-zone bandwidth is not jointly allocated.
- **Optimistic latency:** include only propagation/declared link latency and serialization; explicitly omit queueing, retransmission, interference and real radio conditions.
- **Power overclaim:** require all three declared inputs; no manufacturer, battery-health or field-performance assumptions.
- **Privacy/security:** accept identifiers and aggregate metadata only; reject unrecognized fields; never accept endpoints, credentials, message bodies, personal data or device secrets.
- **Operational misuse:** no network scanning, packet transmission, configuration writes, dispatch, evacuation decisions or automatic failover.
- **Performance:** bounded graph sizes and deterministic algorithms; per-zone max-flow is separately capped at 50 zones per call; CI benchmark p95 budget <= 2,000 ms for the documented synthetic workload.
- **Compatibility:** new opt-in module only; no existing APIs, data stores, workflows, credentials, payment settings or public web assets are changed.

## Verification plan

- Add focused tests for all ten capabilities, boundary conditions, unknown data, tampering and deterministic results.
- Add a synthetic benchmark for validation, connectivity, single-point failures, coverage, max-flow, power, message routing, traffic load, outage scenarios and manifest verification.
- Run the existing full pytest suite and Python 3.11/3.12/3.13 CI matrix through GitHub Actions before merge.
- Confirm the pull request head is the tested head before merge; verify post-merge CI. No Pages deployment is expected because no `web/**` asset changes are planned.
