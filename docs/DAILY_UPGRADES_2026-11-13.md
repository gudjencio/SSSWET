# SSSWET daily upgrade plan — 13 November 2026

## Baseline inspected before implementation

- Current `main`: `bd906b86bae2379b36f4d5ac48f743c161f1003d` (12 November 2026).
- Immediate predecessor: `09f118132ac8c0c17f3b708ad2612dab3016166d`.
- The direct comparison confirms the latest change adds deterministic, privacy-bounded observation-snapshot fingerprints to the local clock-calibration workspace, regression tests, documentation and service-worker cache version `v199`.
- The predecessor comparison confirms the local clock-calibration workspace was added immediately before that, with a 5,000-event workspace bound, 15 locale dictionaries, explicit clock-basis semantics and model/snapshot verification.
- The preceding mainline commits repaired the public interface and added bounded research context/review/graph/lineage/literature/dataset-governance workflows.
- Latest recorded core CI run for the inspected baseline: run 43288598711, completed successfully on 12 November 2026.

The existing tree already contains versioned scientific memory, contradiction links, provenance and source-independence utilities, multilingual title triage in 21 languages, permission-aware query planning for public social/video channels, bounded research context packs, evidence packet validation, reproducibility manifests, temporal calibration, GPS accuracy footprints, rescue resource allocation, protective-design assurance, a static accessibility audit and service-worker regression tests. The additions below are deliberately complementary: they add missing operational bridges rather than duplicate those existing facilities.

## Ten acceptance criteria defined before implementation

| # | Candidate improvement | Acceptance criteria |
|---|---|---|
| 1 | Permission-aware public media intake | Normalize at least 14 public channels; require public visibility and an allowed access mode; enforce a 500-record batch bound; discard unapproved fields; flag sensitive-field presence without returning values; stable fingerprints; never fetch or persist private content. |
| 2 | Multilingual translation-fidelity audit | Compare original/translated numeric quantities, signs, units, configured term pairs and negation cues across at least 20 language families; preserve both texts; report mismatches; never translate or certify correctness. |
| 3 | Claim/evidence corroboration matrix | Bound claims, sources and links; resolve every link; count unique provenance groups rather than duplicate publishers; retain support and contradiction separately; separate withdrawn evidence; emit no truth score. |
| 4 | Evidence-change impact propagation | Traverse a bounded dependency graph from changed source/artifact IDs; return direct and downstream review targets, shortest paths, missing references and cycle diagnostics; never delete or automatically retract records. |
| 5 | Integrity-checked research checkpoint bundles | Canonical SHA-256 digest and 64 KiB cap; tampering must fail verification; resume assessment must block when query/context/memory/source fingerprints changed or review blockers remain. |
| 6 | Agent execution provenance receipts | Bind task/contract, agent, model label, tool versions, input digests, output digest, budgets and parent receipts; verify hashes and parent chains; reject secret-bearing fields; never claim correctness or intelligence. |
| 7 | Spatiotemporal uncertainty envelopes | Propagate declared timestamp and GPS uncertainty into distance/speed bounds; handle antimeridian and overlapping time intervals; do not infer event identity or extrapolate missing observations. |
| 8 | Civil-rescue demand stress testing | Evaluate min/expected/max supply and demand for allowlisted civil resources; report best/worst shortages and criticality; no dispatch, triage or medical/evacuation decision. |
| 9 | Protective/rescue design change-impact review | Map changed requirements, hazards, controls and evidence to stale verifications and required independent reviews; preserve unrelated checks; never approve a design or certify safety. |
| 10 | Web accessibility/performance quality gate | Audit the deployed HTML entry points with the existing static accessibility rules; enforce explicit JS/CSS/HTML size budgets and local asset existence; run in CI and report measured byte counts/issues. |

## Regression risks and controls

- **Platform terms and privacy:** social/video intake is a metadata normalizer for official APIs or permitted public feeds only. It does not log in, scrape restricted pages, download media, or bypass rate limits. Unknown fields are excluded.
- **Translation false positives:** lexical negation and unit matching are review prompts, not semantic translation verification. Original and translated text remain available to the reviewer.
- **Evidence overcounting:** repeated publishers/provenance groups must not inflate independent corroboration. Conflicting evidence remains visible.
- **Invalidation blast radius:** dependency traversal is advisory and bounded. It reports impacted artifacts without changing stored verification states.
- **Checkpoint compatibility:** bundles are additive and schema-versioned; old checkpoint APIs remain unchanged.
- **Agent trace confidentiality:** receipts contain hashes and bounded metadata only, never raw prompts, private messages, credentials or secret values.
- **Temporal/spatial overclaiming:** uncertainty envelopes use declared bounds only. If the time interval crosses zero, speed is withheld rather than made artificially precise.
- **Rescue/design safety:** outputs are planning and review aids, not operational authorization, engineering certification or clinical guidance.
- **Web gate compatibility:** budgets are set above the inspected current asset sizes; any accessibility fixes must preserve all existing interactions and translations.
- No payments, taxes, refunds, customer data, credentials, legal policies or commercial promises are in scope.

Implementation will be accepted only if each feature has deterministic regression tests, public-facing usage/limitations documentation, and the full existing CI suite remains green.