# Research workbench upgrade plan — 13 November 2026, run 2

## Inspected baseline

- Mainline baseline: `78fbb348430e8673eaddcc706b67564dd08f5178`.
- Immediately preceding version: `1d9d8c6e6b3fa8eb58d50a920a02f43b9b6e2e03`.
- The one-commit comparison confirms that the preceding release added ten evidence-led capabilities: public-media normalization, multilingual translation-fidelity checks, claim/evidence matrices, evidence-change propagation, integrity-checked checkpoints, agent execution receipts, spatiotemporal uncertainty envelopes, rescue stress testing, protective-design change impact and a web-quality gate.
- The current tree already contains versioned scientific memory, preregistration/deviation records, evidence dossiers, source metadata assessment, dataset governance, technology dependency graphs, protective-design assurance, rescue allocation and Virtual Time Travel Mapping. The new work therefore adds complementary tools instead of replacing these APIs.
- Baseline CI status lookup for the inspected head returned no combined status records and no PR-triggered workflow runs. This is recorded as unavailable evidence, not as a passing run.

## Ten proposed feature improvements and measurable acceptance criteria

1. **Hypothesis operationalisation audit** — assess whether a research question declares scope, variables, units, measurements, comparator, time horizon, falsification conditions, alternatives and safety constraints. Acceptance: deterministic output; missing/underspecified fields are named; malformed and oversized inputs are rejected; a complete form is described only as ready for protocol review, never as scientifically valid.
2. **Append-only replication registry** — preserve immutable run fingerprints and compare protocol, dataset, environment and analysis identity between attempts. Acceptance: duplicate run IDs and invalid digests are rejected; comparisons identify exact mismatches; negative and inconclusive outcomes remain first-class; no result is labelled a successful replication automatically.
3. **Claim-level evidence coverage audit** — connect claims to supporting, contradicting, neutral and unclear evidence while deduplicating by provenance group. Acceptance: dangling references, unsupported claims, unresolved counterevidence and single-group concentration are separately reported; repeated sources from one group never inflate independent-group counts.
4. **Source-audit calibration report** — summarize only explicit human audit outcomes by source, domain and metadata field. Acceptance: report sample counts and Wilson 95% intervals; suppress any accuracy estimate below the configured minimum sample; never produce a composite trust score or infer correctness from popularity.
5. **Aggregate dataset-shift monitor** — compare schema, units, missingness, numeric summaries and categorical proportions without loading row-level data. Acceptance: detect added/removed fields, unit changes, missingness shifts, numeric standardized mean differences and categorical total-variation distance; preserve unknowns and reject non-finite or malformed summaries.
6. **Dependency readiness and critical-path planner** — evaluate a bounded research-task DAG with explicit gates and dependencies. Acceptance: deterministic topological order, missing-reference and cycle diagnostics, blocked-descendant propagation and critical-path duration; no task execution or automatic gate approval.
7. **Multi-objective design frontier** — compare candidate designs against explicit metric directions and non-negotiable safety floors. Acceptance: return a Pareto frontier without a weighted composite score; exclude candidates with missing metrics or violated safety floors from the eligible frontier; explain dominance pairs.
8. **Structured safety-case graph audit** — validate claim/argument/evidence/hazard/control links and independent review coverage. Acceptance: report dangling edges, cycles, unsupported top-level claims, rebuttals, unmitigated hazards and reviewer conflicts; output is never an approval or certification.
9. **Virtual Time Mapping local-frame alignment** — fit a bounded 2D similarity transform from paired, consented landmarks with declared coordinate units and uncertainty. Acceptance: deterministic transform, per-landmark residuals, RMS/max residual and uncertainty-bound flags; reject degenerate inputs; do not convert geographic CRS, infer missing locations or claim historical recovery.
10. **Civil-rescue route accessibility review** — assess ordered route segments against declared clear-width, slope, surface and obstruction criteria. Acceptance: verify segment continuity, distinguish measured failures from unknown measurements, report segment-level reasons and avoid route generation, dispatch or operational safety claims.

## Cross-cutting acceptance and regression controls

- Each feature is a separate standard-library-only Python module with bounded input sizes and deterministic outputs.
- Each feature receives positive, negative, boundary and safety-semantics tests in the new regression suite.
- The full existing Python suite and existing web checks must remain unchanged and pass in CI.
- Existing files and public interfaces are not to be rewritten; the additions are opt-in utilities.
- No raw dataset rows, private social content, credentials, personal data or prompts are stored by these utilities.
- Algorithms must preserve unknown values and counterevidence. No automatic scientific approval, medical decision, rescue dispatch, design certification or claim of model intelligence is permitted.
- Potential regressions to monitor: extra import/runtime overhead, unbounded graph or dataset processing, misleading trust/quality scores, unsafe interpretation of map transforms, hidden unit mismatches, and accidental promotion of review readiness to scientific validity.
- If a feature fails its acceptance tests or introduces a regression, it must be removed or replaced before release; the target count does not justify a downgrade.

## Implementation sequencing

This plan is committed before feature implementation. The feature modules, regression suite, public usage notes and README links will be committed separately so that the implementation can be compared with this recorded baseline.
