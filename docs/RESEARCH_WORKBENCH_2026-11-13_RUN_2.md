# Research workbench — 13 November 2026 (run 2)

This release adds ten opt-in, deterministic research utilities to the Python core. They complement the existing scientific-memory, preregistration, evidence-dossier, dataset-governance, protective-design, rescue-planning and Virtual Time Mapping systems. They do not replace those services or change their stored records.

The pre-implementation baseline and measurable acceptance criteria are recorded in [the upgrade plan](UPGRADE_PLAN_2026-11-13_RUN_2.md). The implementation is standard-library-only and each capability has regression coverage in `core/tests/test_daily_upgrades_2026_11_13_run2.py`.

## Capabilities

### 1. Hypothesis operationalisation

Module: `ssswet_core.hypothesis_testability`

`assess_hypothesis(specification)` checks for a research question, bounded system scope, comparator, time horizon, measurement context, defined independent variables and outcomes, falsification conditions, alternative explanations and safety constraints. Variable records must name units and operational measurement definitions. The result identifies missing fields and whether the specification is complete enough to enter protocol review.

A complete result is not evidence that a hypothesis is true, feasible, ethically acceptable or safe. It does not replace a preregistration, power analysis, institutional review or independent protocol review.

### 2. Append-only replication registry

Module: `ssswet_core.replication_registry`

`ReplicationRegistry.record_attempt(...)` stores run identifiers and SHA-256 fingerprints for the protocol, datasets, environment and analysis. It preserves positive, negative, inconclusive, failed and not-run outcomes. `compare(left_run_id, right_run_id)` lists the exact declared inputs that differ.

The registry is bounded to 2,000 attempts and 100 dataset fingerprints per attempt. It is an in-memory utility; the caller must choose and govern any durable storage. A matching fingerprint means only that the declared identifiers match. It does not prove that an experiment was executed correctly or independently replicated.

### 3. Claim-level evidence coverage

Module: `ssswet_core.evidence_coverage`

`audit_claim_coverage(claims, evidence, links)` checks explicit claim/evidence links and distinguishes support, contradiction, neutral material, under-review evidence, withdrawn records and dangling references. Independent support is counted by declared provenance group, not by the number of repeated URLs or records.

This is a coverage and counterevidence audit, not a truth score. Provenance groups must be maintained accurately by researchers; the tool cannot establish that two publishers are genuinely independent.

### 4. Source-audit calibration summaries

Module: `ssswet_core.source_audit_calibration`

`summarize_source_audits(records, minimum_sample=5)` summarizes explicit human audit outcomes for a source, domain and metadata field. It reports the number of audited records, observed agreement and a Wilson 95% interval only after the minimum sample is reached.

This is descriptive agreement with recorded human audits, not a general source-reliability rating. The tool produces no composite trust score, does not infer correctness from popularity and cannot remove reviewer bias.

### 5. Aggregate dataset-shift diagnostics

Module: `ssswet_core.dataset_shift`

`compare_dataset_summaries(reference, candidate)` compares aggregate-only feature summaries. It identifies added and removed fields, type and unit changes, missingness deltas, numeric standardized mean differences and categorical total-variation distance. Thresholds are explicit arguments.

Only counts and summary statistics are accepted; row-level observations are not accepted or retained. The numeric standardized difference is a descriptive comparison of supplied summaries, not a causal explanation. A detected shift requires domain review and may reflect sampling, instrumentation, preprocessing or genuine change.

### 6. Dependency readiness and critical path

Module: `ssswet_core.dependency_readiness`

`analyze_dependencies(tasks)` evaluates a bounded task graph with declared durations, dependencies and gate states. It returns a deterministic topological order where possible, missing references, exact cycle members, downstream tasks affected by cycles, blocked tasks and a critical path when the dependency graph is complete and acyclic.

This is a planning aid only. It does not dispatch agents, execute experiments, approve gates or imply that an estimated duration is guaranteed.

### 7. Multi-objective design frontier

Module: `ssswet_core.pareto_design_frontier`

`compare_designs(candidates, objectives, safety_floors=[...])` identifies non-dominated candidates across explicitly directed minimize/maximize objectives. Separate minimum/maximum screening floors can exclude candidates before frontier analysis. Missing metrics are reported rather than imputed.

No weighted composite score is generated. A Pareto frontier is not a safety certification, proof of feasibility or recommendation to deploy a design. The declared floors and metric directions require domain-owner review.

### 8. Structured safety-case graph audit

Module: `ssswet_core.safety_case_graph`

`audit_safety_case(...)` checks a bounded claim/argument/evidence/hazard/control graph for dangling links, cycles, unsupported top-level claims, unsupported arguments, rebuttals, unmitigated hazards and independent-review gaps. Reviewer IDs and declared independence groups are checked against the design owner.

The result can prepare a case for independent review; it cannot approve the case, certify a product, replace a competent safety engineer or authorize real-world use. Evidence states and reviewer independence remain subject to human governance.

### 9. Virtual Time Mapping local-frame alignment

Module: `ssswet_core.vtt_local_frame_alignment`

`fit_local_frame_alignment(landmarks, ...)` fits a 2D rigid rotation and translation between two distinct local planar frames from paired landmarks. It returns the transform matrix, per-landmark residuals, RMS and maximum residuals, and whether each residual is within the sum of its declared uncertainty bounds.

Both frames must use the same declared coordinate unit. The method does not perform geographic coordinate-reference-system conversion, scale correction, 3D reconstruction, map extrapolation or inference of missing locations. It does not recover unrecorded history or predict future positions. Landmark consent, identity and measurement provenance must be established before use.

### 10. Civil-rescue route accessibility screening

Module: `ssswet_core.rescue_route_accessibility`

`review_route_accessibility(segments, ...)` screens an already-described sequence of route segments against declared clear-width, slope, surface and obstruction criteria. It checks segment continuity and distinguishes measured failures from missing measurements.

This utility does not generate a route, inspect live conditions, assess all accessibility requirements, dispatch responders or certify operational safety. Actual rescue decisions require current local information, trained personnel and applicable authority.

## Shared design guarantees

- Inputs are bounded and validated; non-finite values, duplicate identifiers and malformed records are rejected.
- Outputs are deterministic for the same inputs and do not mutate caller-owned records.
- Existing APIs are not replaced. These tools are imported explicitly from their modules.
- The modules add no third-party runtime dependency.
- Unknown values, counterevidence and negative outcomes remain visible.
- No private platform content, credentials, prompts or raw dataset rows are collected.
- Review readiness is never converted into scientific validity, safety approval or operational authorization.

## Example

```python
from ssswet_core.hypothesis_testability import assess_hypothesis
from ssswet_core.evidence_coverage import audit_claim_coverage

review = assess_hypothesis({
    "research_question": "Does intervention A change outcome B?",
    "system_scope": "A defined laboratory system",
    "comparator": "Matched baseline",
    "time_horizon": "A predeclared observation period",
    "measurement_context": "A calibrated method",
    "independent_variables": [
        {"name": "intervention A", "unit": "mg/L",
         "operational_definition": "Measured concentration"}
    ],
    "outcomes": [
        {"name": "outcome B", "unit": "mmol/L",
         "measurement_method": "A validated assay"}
    ],
    "falsification_conditions": ["The predeclared effect is not observed"],
    "alternative_explanations": ["Instrument drift"],
    "safety_constraints": ["No human or animal subjects"],
})

print(review["status"])  # ready_for_protocol_review; not scientific approval

coverage = audit_claim_coverage(
    claims=[{"claim_id": "claim-1", "text": "Example claim"}],
    evidence=[{
        "evidence_id": "evidence-1", "source_id": "source-1",
        "provenance_group": "publisher-family-a",
    }],
    links=[{
        "claim_id": "claim-1", "evidence_id": "evidence-1",
        "stance": "supports",
    }],
)
print(coverage["claims"][0]["supporting_independent_group_count"])
```

## Synthetic performance and bounded-storage measurements

The CI benchmark is available at `.github/scripts/benchmark_research_workbench.py`. On 13 November 2026 it ran three samples per workload on a GitHub Actions Python 3.12 runner. Every workload remained below the 5,000 ms maximum-per-sample guard:

| Workload | Median per batch | Bounded output checked |
|---|---:|---|
| 100 hypothesis assessments | 1.861 ms | Protocol-review readiness only |
| 500 replication attempts | 29.852 ms | 500 records; 538 serialized JSON bytes/record |
| 500 claims / 1,000 evidence links | 4.138 ms | 500 supporting groups, 500 contradicting groups, 500 contested claims, 0 dangling links |
| 5,000 source audits | 8.614 ms | 1,000 source/domain/field groups, all meeting the five-audit minimum |
| 300 dataset features | 2.434 ms | 300 flagged feature summaries; no row-level data |
| 500 dependency tasks | 4.123 ms | 500-hour declared critical path |
| 100 designs / 5 objectives | 4.961 ms | 70 Pareto-frontier candidates |
| 500 safety-case nodes / 300 edges | 1.548 ms | Structured for independent review, not approved |
| 200 VTT landmarks | 0.989 ms | RMS residual 0 in the synthetic rigid-transform fixture |
| 500 rescue-route segments | 1.530 ms | Within the declared synthetic screening limits |

The replication registry's canonical JSON export was 134,501 bytes for 250 attempts and 269,001 bytes for 500 attempts. This demonstrates approximately linear serialized-export growth for that fixture; it is **not** a measurement of Python heap use, database storage, long-term retention cost or production traffic.

These are synthetic microbenchmarks on one ephemeral runner, not service-latency guarantees or a comparison against a previous implementation. The figures must not be generalized to larger datasets, different hardware, live sources, physical systems or real rescue operations.

## Validation

The new regression suite covers normal, incomplete, malformed, boundary, contradiction, missing-reference, cycle, degenerate-geometry, unit, safety-floor and route-continuity cases. The full existing test suite and the CI workflow are the release gate. No claim of improved scientific intelligence or scientific validity is made.
