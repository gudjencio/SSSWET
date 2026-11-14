# Research assurance upgrades — 14 November 2026

This release adds ten opt-in, independently importable Python capabilities. They are decision-support utilities: they do not establish scientific truth, increase agent intelligence, approve experiments, certify equipment, or authorize operational activity. They add no runtime dependencies and perform no network access.

## What changed

1. **Agent handoff contracts** (`agent_handoff_contract.py`) validate a versioned, expiring, size-bounded task envelope. Source references carry SHA-256 fingerprints, constraints and output expectations are explicit, and safety state is non-authorizing. `validate_handoff()` always returns `execution_authorized: false`.
2. **Scientific-memory snapshots** (`research_memory_snapshot.py`) produce deterministic, versioned exports with source hashes, review states and stances. Exact-text matches are grouped for inspection but never merged or deleted. Retrieval uses bounded, explainable lexical recall (maximum 50 results); supporting and contradicting notes remain visible.
3. **Cross-platform source lineage** (`media_source_lineage.py`) models only caller-declared repost, translation, quotation, adaptation and syndication edges. It reports missing parents and cycles. Identical text is a match candidate, not proof of shared origin or non-independence.
4. **Claim-context comparability** (`claim_context_audit.py`) checks metric, unit, population, conditions, method and observation window before comparing declared values. Incomplete or mismatched contexts are not compared. Even comparable numeric differences remain human-review leads, never automatic contradictions.
5. **Translation integrity** (`translation_integrity.py`) checks numeric tokens, adjacent measurement units, configured language-specific negation signals and caller-declared protected terms. It flags review needs but does not translate text or certify semantic accuracy.
6. **Reviewer concordance** (`reviewer_concordance.py`) reports raw agreement and pairwise Cohen's kappa on matched items, with a minimum sample and prevalence caveat. It does not rank reviewers or treat agreement as correctness.
7. **Temporal evidence windows** (`temporal_evidence_window.py`) require timezone-aware timestamps and distinguish in-window, stale, future-dated and unknown publication times. Capture-before-publication anomalies are visible; no record is discarded and recency is not treated as reliability.
8. **Privacy export preview** (`privacy_export_gate.py`) returns a redacted copy and category/offset-only findings for configured email, phone-like, IPv4, explicitly labelled coordinate and secret-like patterns. Matched values are not returned. Human review remains required and publication is never authorized by the scanner.
9. **VTT spatial uncertainty propagation** (`vtt_spatial_uncertainty.py`) propagates a 2D point covariance through a proper rigid rotation and adds registration covariance. It reports a 95% confidence-ellipse approximation and rejects invalid rotations or non-positive-semidefinite covariance. It does not convert geographic coordinates or reconstruct 3D scenes.
10. **Civil-rescue route redundancy** (`rescue_route_redundancy.py`) computes a bounded edge-disjoint path count and minimum-cut segment IDs for a declared graph. Only segments explicitly marked open are traversable; blocked and unknown segments remain visible but unavailable. It does not generate operational routes, dispatch responders or certify safety.

## Examples

```python
from ssswet_core.research_memory_snapshot import build_memory_snapshot, retrieve_memory

snapshot = build_memory_snapshot(memory_records)
results = retrieve_memory(snapshot, "alloy fatigue", limit=20)
# Inspect each result's review_state, stance, matched_tokens and source_refs.
```

```python
from ssswet_core.claim_context_audit import compare_claim_contexts

comparison = compare_claim_contexts([
    {
        "claim_id": "paper-a", "metric": "fatigue life", "value": 1200,
        "unit": "cycles", "population": "alloy A", "condition": "20 C dry",
        "method": "three point bend", "observation_window": "2025-Q1",
    },
    {
        "claim_id": "paper-b", "metric": "fatigue life", "value": 1500,
        "unit": "cycles", "population": "alloy A", "condition": "20 C dry",
        "method": "three point bend", "observation_window": "2025-Q1",
    },
])
# A comparable difference is a review lead, not an inferred contradiction.
```

```python
from ssswet_core.rescue_route_redundancy import analyze_route_redundancy

review = analyze_route_redundancy(
    route_segments, start_node="shelter", destination_node="assembly-point"
)
# Unknown and blocked segments are not treated as open.
```

## Baseline comparison

The inspected baseline was main commit `6d8291c420ad23b946e6553707d7638d32ac9e24`; its immediate predecessor was `b8b600847e2871ea56300a30c7015a110e20986a`.

| Capability | Before this release | Added behavior |
|---|---|---|
| Agent handoff | Agent capability matching and context packs existed, but no portable, expiring envelope joined task constraints to hashed source references | Versioned handoff contract with strict schema, bounded budgets and non-authorizing safety states |
| Memory continuity | Cross-agent memory, graph and decision-lineage tools existed | Deterministic portable snapshots, explicit exact-text groups, bounded retrieval and digest verification |
| Media provenance | Exact-content clusters and source snapshot comparison existed | Declared lineage graph, missing-parent and cycle checks; exact text never proves origin |
| Claim comparison | Candidate extraction and evidence coverage existed | Explicit context compatibility gate before value comparison |
| Translation QA | Protected-term presence and reviewer state existed | Number, unit and negation discrepancy prompts |
| Review calibration | Human review and reviewer selection safeguards existed | Matched-item inter-reviewer concordance statistics with prevalence caveats |
| Temporal review | Timestamped media and local clock calibration existed | Explicit age-window and capture-order classifications |
| Public privacy | Sensitive metadata field names could be flagged | Content-level redaction preview that does not return matched values |
| VTT | Local 2D alignment and independent hold-out residual validation existed | Covariance propagation through a validated local rigid transform |
| Rescue planning | Segment accessibility screening existed | Edge-disjoint-path and bottleneck analysis over declared segment graphs |

No existing public-media, VTT, locale, GPS, memory, safety-case or rescue API is replaced. All ten additions are opt-in and additive. Existing behavior remains the compatibility baseline.

## Validation and synthetic measurements

Run from the repository root:

```bash
python -m py_compile core/ssswet_core/assurance_common.py core/ssswet_core/agent_handoff_contract.py core/ssswet_core/research_memory_snapshot.py core/ssswet_core/media_source_lineage.py core/ssswet_core/claim_context_audit.py core/ssswet_core/translation_integrity.py core/ssswet_core/reviewer_concordance.py core/ssswet_core/temporal_evidence_window.py core/ssswet_core/privacy_export_gate.py core/ssswet_core/vtt_spatial_uncertainty.py core/ssswet_core/rescue_route_redundancy.py
cd core && python -m pytest -q tests/test_research_assurance_upgrades.py
cd ..
python .github/scripts/benchmark_research_assurance.py
```

The focused regression suite contains 10 grouped test cases and 72 explicit assertions covering valid, malformed, bounded, Unicode, tampering, contradiction preservation, missing provenance, translation discrepancy, reviewer agreement, timestamp anomalies, privacy redaction, covariance and graph bottlenecks.

A local synthetic run on Python 3.13.5 used three repeats per workload. Median batch latencies were: memory snapshot 3.618 ms (250 notes); memory retrieval 2.051 ms (250 notes); source lineage 1.616 ms (250 sources); claim context 22.837 ms (200 claims); translation integrity 1.204 ms (100 checks); reviewer concordance 0.355 ms (100 matched items); temporal window 1.528 ms (250 sources); privacy scan 0.940 ms (100 excerpts); VTT uncertainty 1.177 ms (100 transforms); rescue redundancy 3.529 ms (500 segments); and handoff validation 0.126 ms. Every maximum sample remained below the 5,000 ms CI budget in that local run.

The labelled synthetic memory fixture retrieved 50/50 known relevant notes at precision@50 = 1.0 and recall@50 = 1.0. This measures deterministic lexical retrieval on a deliberately separable fixture, not semantic or real-world relevance. All 250 memory IDs and 250 source references were retained, including 50 notes carrying supporting or contradicting stances. Canonical snapshot export measured 45,606 bytes at 125 notes and 91,095 bytes at 250 notes (1.9974× growth); this is serialized JSON size, not heap or database storage. No live sources or media were accessed.

CI is the release gate for the complete Python 3.11/3.12/3.13 matrix and existing JavaScript, locale, accessibility and asset-budget checks. The local measurements above do not substitute for the remote CI result.

## Limitations and safety

- These utilities do not establish scientific validity, causation, truth, source trustworthiness or increased AI intelligence.
- Exact text matches and reviewer agreement do not establish source independence or correctness.
- Translation cues are incomplete heuristics; native-speaker and domain review remain necessary.
- The privacy scanner is not a guarantee against disclosure. It is an opt-in redaction preview; inspect the original and redacted text before publication.
- VTT covariance assumes the caller's declared local Cartesian coordinate frame and covariance model. It is not geodesy, a 3D model or a physical accuracy certificate.
- Rescue redundancy is a graph-topology diagnostic over supplied segment states. Real conditions, accessibility, weather, capacity, emergency command and responder judgment are outside its scope.
- No private-content access, scraping, media downloading, authentication, terms-of-service bypass, payment changes, customer-data changes, credential changes, or legal-policy changes are introduced.
