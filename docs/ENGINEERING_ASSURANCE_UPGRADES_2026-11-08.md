# Engineering assurance and reproducibility upgrades — 8 November 2026

This additive release candidate introduces ten independently importable, bounded research utilities. They support measurement QA, protective-system engineering review, civil-rescue equipment research and reproducible spatial observation analysis. They do not make operational, medical, dispatch, certification or safety-approval decisions.

## Version comparison and scope

The implementation baseline is main at 98989f4332a86101771a6d5d0573d54b023d34d8. The immediately preceding commit is d09ab611037e2c85602f302a90f02a6f6baa4d70. The complete recursive file trees are identical; the only difference is a GPS scenario test-fixture adjustment from an exactly 70 m/s boundary to 69.999 m/s. No production file changed between those two revisions.

This proposal is additive: it creates ten new core modules, a focused regression suite, a synthetic benchmark and public documentation. It does not edit persistent research records, database schemas, existing API routes, catalogue data, payments, customer data, credentials or legal/commercial settings.

| Area | Previous behaviour in main | New capability |
|---|---|---|
| Virtual Time Travel sensor streams | Recorded timestamps can be replayed, but independent sensor-clock offset/drift is not reconciled by a dedicated core utility | Robust affine clock alignment with per-anchor residuals, explicit uncertainty and no extrapolation |
| Measurement uncertainty | Existing uncertainty propagation covers independent additive quadrature and worst-case sums | First-order covariance-aware uncertainty budgets with positive-semidefinite correlation validation |
| Metrology | Existing calibration metrics evaluate probabilistic prediction calibration (Brier/ECE), not physical instrument records | Calibration-record metadata audit with validity windows, certificate digest shape, traceability references and review state |
| Component reliability | No non-parametric right-censored reliability curve | Kaplan–Meier product-limit estimates with tied events, censor counts and Greenwood uncertainty |
| Measurement-system QA | No balanced between-group/repeatability decomposition | Balanced one-way variance-component estimate with explicit scope limits |
| Failure analysis | Existing risk registers record concerns and mitigations | Structured failure-mode review with separate severity/occurrence/detectability and closure evidence; no composite RPN |
| Engineering trade-offs | Existing prioritisation and sensitivity tools provide other views | Conservative interval Pareto dominance; overlapping uncertainty intervals remain incomparable |
| Design verification | Evidence dossiers and review workflows exist, but no compact requirement-to-verification matrix | Requirement traceability with broken links, orphan evidence, conflicts and reviewer/provenance gates |
| Environmental inventory | No factor-based, phase-separated inventory aggregator | Transparent aggregation using only supplied factors, exact declared units and source versions |
| Reproducibility hand-off | Canonical run manifests exist, but no deterministic archive packager | Uncompressed deterministic ZIP bundle with stable metadata, per-file digests, size caps and integrity verification |

## The ten improvements and acceptance criteria

1. **Sensor clock alignment** — sensor_clock_alignment.py fits an affine clock map using Theil–Sen pairwise medians, retains source IDs and residuals, and aligns only timestamps inside the anchor interval. Acceptance: deterministic offset/drift recovery on a synthetic outlier fixture; unique anchor IDs; invalid/non-forward clocks rejected; out-of-range observations are reported rather than extrapolated; 10,000-observation probe remains below the broad 5-second CI guard.
2. **Covariance-aware uncertainty budgets** — uncertainty_budget.py calculates first-order propagation for declared sensitivities, standard uncertainties and a correlation matrix. Acceptance: independent inputs reproduce quadrature; correlated inputs change the result correctly; asymmetric, out-of-range and non-PSD matrices are rejected; worst-case absolute bounds remain separately visible.
3. **Metrology calibration-record audit** — calibration_registry.py checks timezone-aware validity windows, digest format, declared traceability references, review state, reviewer and review timestamp. Acceptance: expired, pending, rejected, incomplete and malformed records are surfaced; completed review states require reviewer attribution and a timezone-aware review timestamp; duplicate instruments are rejected. The certificate content itself is not fetched or authenticated.
4. **Right-censored reliability analysis** — reliability_survival.py produces a Kaplan–Meier curve with tied events, right-censor counts, Greenwood standard errors and an unreached-median state. Acceptance: known hand-calculated fixtures match; invalid durations and duplicate IDs are rejected; no parametric extrapolation occurs; the implementation is O(n log n) after sorting.
5. **Measurement repeatability** — measurement_repeatability.py estimates within-group and between-group variance components for balanced repeated measurements. Acceptance: equal replicate counts are required; known synthetic variance fixtures are reproducible; zero-variance cases do not divide by zero. This is not a full crossed Gage R&R study or an accreditation assessment.
6. **Failure-mode review** — failure_mode_review.py validates separate ordinal ratings, controls, evidence and action closure. Acceptance: high-severity items without controls and modes without evidence remain flagged; closed actions require a named reviewer and closure evidence; no risk-priority number is calculated.
7. **Uncertainty-aware Pareto frontier** — robust_pareto.py compares explicit minimize/maximize objectives using absolute uncertainty intervals. Acceptance: only non-overlapping, conservatively dominated alternatives are removed; missing metrics and invalid uncertainties are rejected; no single winner is selected automatically.
8. **Requirements traceability** — requirements_traceability.py links requirements to reviewed evidence. Acceptance: only a passing item with both reviewer and provenance reference can count as reviewed pass evidence; fail/inconclusive evidence remains visible; broken references and orphan evidence are reported.
9. **Life-cycle inventory aggregation** — lifecycle_inventory.py groups supplied quantities and factors by phase and impact unit. Acceptance: exact unit-basis matching is required; duplicate flow IDs, non-finite values and negative quantities/factors are rejected; source IDs and factor versions are retained; uncertainty aggregation states its independence assumption. No emission factors are bundled with SSSWET.
10. **Deterministic research bundles** — reproducible_bundle.py builds and verifies sorted ZIP archives with fixed timestamps, stable file metadata and SHA-256 manifests. Acceptance: identical inputs yield byte-identical archives; altered payloads fail verification; traversal, symlinks, private-key paths/markers, duplicate entries and size-limit violations are rejected.

## Public use

Run from the repository root after installing the core package or adding core/ to PYTHONPATH. For example:

    from ssswet_core.sensor_clock_alignment import fit_clock_map, align_observations
    from ssswet_core.uncertainty_budget import propagate_linear
    from ssswet_core.reliability_survival import kaplan_meier
    from ssswet_core.robust_pareto import analyze_frontier
    from ssswet_core.reproducible_bundle import build_bundle, verify_bundle

    clock = fit_clock_map(sync_anchors)
    aligned = align_observations(sensor_observations, clock)
    budget = propagate_linear(measurement_components, correlation_matrix)
    reliability = kaplan_meier(component_life_test_records)
    frontier = analyze_frontier(engineering_alternatives, objectives)
    archive = build_bundle(explicitly_selected_artifacts)
    archive_check = verify_bundle(archive)

The remaining public APIs are documented in their module docstrings and covered by core/tests/test_engineering_assurance_2026_11_08.py.

## Regression and safety safeguards

- All ten features are new modules; existing APIs and database schemas remain untouched.
- Sensor alignment preserves original timestamps, labels aligned times as derived, and refuses extrapolation. The affine model cannot represent changing drift within a stream.
- Covariance propagation is first-order and only as defensible as the user-supplied sensitivities and correlation matrix. It does not establish measurement validity.
- Calibration review validates metadata shape and declared traceability; a 64-character digest is not proof that a certificate is genuine or current.
- Kaplan–Meier summaries describe the supplied test cohort; they do not infer causes, field performance or future life beyond observed follow-up.
- Repeatability results assume a balanced one-way design; nested/crossed operator, device and site effects need a suitable study design.
- Failure-mode review preserves separate ratings and evidence; human safety review remains mandatory.
- Pareto dominance is conservative interval arithmetic, not a probability model or an automatic design decision.
- Requirements traceability is not product certification, regulatory compliance or ethics approval.
- Life-cycle results use only user-supplied factors; unit strings must match exactly and uncertainty is combined under an explicit independence assumption.
- Bundle path and private-key checks are defensive filters, not comprehensive secret scanning. Only explicitly selected, reviewed public artifacts should be packaged. A digest provides integrity checking, not a digital signature or identity proof.

## Local validation and performance probe

The focused suite passed **21 tests** on Python **3.13.5**. The synthetic benchmark uses three timed repetitions per workload; p95 is the maximum of those three samples and is a diagnostic, not a stable statistical tail estimate.

| Synthetic workload | Median | p95 |
|---|---:|---:|
| 10,000 sensor observations aligned from 200 anchors | 11.8205 ms | 50.3533 ms |
| 30-component covariance budget | 0.8524 ms | 0.8695 ms |
| 500 calibration records | 5.2568 ms | 7.4236 ms |
| 10,000 Kaplan–Meier observations | 19.4709 ms | 21.9284 ms |
| 100 repeatability groups | 0.3639 ms | 1.2328 ms |
| 500 failure modes | 1.6574 ms | 2.0739 ms |
| 200 alternatives × 8 objectives | 11.9297 ms | 12.5515 ms |
| 1,000 requirement/evidence links | 2.8295 ms | 2.9836 ms |
| 5,000 life-cycle inventory flows | 18.1825 ms | 19.0580 ms |
| 20-file reproducible bundle (~1 MB uncompressed) | 5.0039 ms | 5.6711 ms |

Measurements were produced in the local Python 3.13.5 container. CI repeats the same deterministic workloads on its Python 3.12 runner and retains a deliberately broad 5-second p95 guard. These numbers are not device-wide guarantees and do not establish scientific validity, agent intelligence, safety or certification.
