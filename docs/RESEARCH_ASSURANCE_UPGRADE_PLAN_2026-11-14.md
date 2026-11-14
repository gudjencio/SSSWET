# SSSWET research assurance upgrade plan — 14 November 2026

## Baseline inspected before implementation

- Current public main: `6d8291c420ad23b946e6553707d7638d32ac9e24` — bounded multilingual public-media research workbench.
- Immediately preceding main revision: `b8b600847e2871ea56300a30c7015a110e20986a` — independent hold-out validation for VTT local-frame transforms.
- The current workbench already has platform-origin checks, exact-text candidate clustering, lexical retrieval, caption readiness, human translation records, bounded claim spans, review ordering, snapshot comparison, intake budgets and a verifiable event hash chain. Adjacent modules also provide immutable scientific-memory versions, basic scope/condition/unit claim comparison, peer-review records and publisher/domain source grouping. This run must extend those capabilities rather than reimplement or silently change them.
- Existing cross-agent memory, decision lineage, knowledge graph, source review, VTT temporal capture and rescue accessibility components remain authoritative and unchanged. The new snapshot, claim-context and reviewer-concordance utilities are complementary exports/audits, not replacements for those services.

## Ten feature candidates and measurable acceptance criteria

1. **Versioned agent handoff contract** — validate bounded, versioned task envelopes; require source fingerprints and explicit safety/review state; reject expired, malformed, oversized or unknown-schema handoffs; never grant execution authorization.
2. **Portable scientific-memory snapshots** — deterministic, versioned snapshots; preserve all memory IDs, source references, review states and conflicting stances; bounded lexical retrieval (maximum 50); exact-content deduplication only as a view, never deletion; stable manifest digest.
3. **Cross-platform source-lineage analysis** — preserve declared repost/translation/quotation relations; detect missing parents and cycles; distinguish identical text from independent evidence; retain every source record.
4. **Claim-context comparability audit** — compare explicit metric, unit, population, conditions, method and observation window; flag incomparable contexts; never infer contradiction or scientific truth from differing values.
5. **Translation integrity audit** — compare numeric values, declared units, language-specific negation signals and protected terms; flag discrepancies for human review; never claim translation accuracy.
6. **Reviewer concordance measurement** — compute raw agreement and pairwise Cohen's kappa only on matched items; enforce minimum sample size; expose prevalence caveats; never treat agreement as correctness.
7. **Temporal evidence-window audit** — require timezone-aware timestamps; classify stale, future-dated, missing and capture-order anomalies; preserve all records and never equate recency with reliability.
8. **Post-ingestion source coverage audit** — measure platform, primary-language, domain, region and topic distributions; report HHI concentration and normalized Shannon entropy; compare only caller-specified minimum quotas; cap source and quota counts; never infer source quality or authorize collection.
9. **VTT spatial uncertainty propagation** — transform 2D points and covariance through a validated rigid rotation; include registration covariance; report 95% confidence-ellipse axes; reject invalid/non-PSD covariance; make no geodetic or 3D claim.
10. **Civil-rescue route redundancy analysis** — compute bounded edge-disjoint path count and cut-edge bottlenecks on declared route graphs; only explicitly open segments count; unknown/blocked segments remain visible but unavailable; never dispatch or certify a route.

## Shared release gates

- Add at least 50 focused regression assertions across ten independently importable modules.
- Keep each feature deterministic, versioned, input-bounded and dependency-free.
- Add explicit malformed-input, capacity, Unicode, contradiction-preservation, provenance, temporal, coverage-quota, uncertainty and graph-boundary tests.
- Synthetic benchmark: 250 memory records, 250 source-lineage records, 200 claim comparisons, 100 translation audits, 100 reviewer pairs, 5,000 source-coverage records and 500 rescue segments; all measured operations under 5 seconds per sample on the CI runner.
- Report retrieval hit/recall on a deterministic labelled fixture, provenance retention, contradiction preservation, serialized snapshot size at two capacities, and median/max latency. Do not claim production performance or increased agent intelligence.
- Preserve the existing public-media workbench, VTT hold-out validation, GPS/local storage, locale fallback and rescue-screening behavior.
- Run the complete Python test suite on Python 3.11, 3.12 and 3.13 plus existing JavaScript, locale, accessibility and asset-budget checks.
- Do not merge if any regression is observed or any acceptance gate fails.

## Regression risks and mitigations

- **Memory snapshot growth:** hard caps, deterministic export, explicit overflow errors, no automatic pruning.
- **Agent handoff confusion:** envelopes describe work only; execution authorization is always false and safety/review states remain explicit.
- **Repost false positives:** only caller-declared parent edges establish lineage; exact text hashes are candidate matches, never proof of common origin.
- **Claim comparison false contradiction:** context mismatch blocks value comparison; even comparable differences are only review leads.
- **Translation false positives:** preserve originals; numerical/unit/negation signals are heuristics and require a human reviewer.
- **Reviewer kappa instability:** expose raw agreement, minimum sample and prevalence warnings; no individual ranking.
- **Temporal bias:** recency is metadata only; missing/future timestamps are retained with explicit flags.
- **Coverage quota bias:** target minima can encode a biased sampling policy; require caller-specified quotas, expose unknown metadata and concentration by dimension, and never treat suggested quota slots as unique records or collection authorization.
- **VTT covariance misuse:** explicit coordinate units and covariance assumptions; reject invalid matrices; no conversion to geographic coordinates.
- **Rescue graph overconfidence:** unknown segments are never treated as open; output is topology analysis only, not operational routing.

## Baseline behavior comparison

| Area | Immediately before this run | Planned additive behavior |
|---|---|---|
| Agent coordination | Existing agent capability matching and context packs, but no single portable handoff envelope in this public-media workflow | Versioned bounded handoff with source hashes and explicit non-authorization |
| Scientific memory | Immutable versioned records, lexical retrieval, graph and decision lineage | Portable deterministic snapshot manifests, bounded retrieval and retained contradictions |
| Media provenance | Publisher/domain source grouping, exact text clusters and snapshot diffs | Explicit declared repost/translation lineage graph with cycle and missing-parent diagnostics |
| Claims | Basic subject/predicate/scope/conditions/unit comparator and evidence coverage | Pairwise metric/unit/population/condition/method/observation-window compatibility statuses before human review |
| Translation | Protected-term checks and human decision record | Numeric/unit/negation integrity signals |
| Review quality | Human peer-review records and reviewer-selection safeguards | Matched-item pairwise Cohen's kappa and raw agreement with sample/prevalence caveats |
| Temporal evidence | Timestamped source records and VTT clock calibration | Explicit evidence-window and capture-order audit |
| Source coverage | Feed-level round-robin intake diversity and language/script checks | Post-ingestion platform, language, domain, region and topic concentration metrics plus caller-defined quota gaps |
| VTT | 2D rigid alignment and independent hold-out residual checks | Covariance propagation through a validated transform |
| Rescue | Per-segment accessibility screening | Network redundancy and single-edge bottleneck analysis |

No existing API is replaced. All new functionality is opt-in and additive.


## Candidate replacement after overlap review

The initial privacy-export candidate was removed before release after inspection of the simultaneously open public-media evidence pipeline PR #57, which already adds content-level privacy scanning and packet redaction. It is not counted in this batch. The replacement is the post-ingestion source coverage audit: it measures concentration and caller-defined sampling gaps across five dimensions, a separate capability from feed ingestion round-robin scheduling and language/script consistency checks.