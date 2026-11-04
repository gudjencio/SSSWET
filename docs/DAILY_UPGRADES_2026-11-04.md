# Research-continuity upgrades — 4 November 2026

This release candidate adds ten independently testable capabilities to the SSSWET research core. The work is deliberately conservative: it improves record integrity, retrieval, hand-offs and planning without claiming scientific validation or authorising autonomous action.

## Baseline and review method

The implementation was based on the public main branch at commit dd2aed6a805ca9a74ede5dc9a99a7ce05acc7633 and compared with its immediate predecessor 14d138a2651599a3ffa11706f27a971f3adcda4c. The immediately preceding change focused on catalogue pagination and initial DOM workload; the memory, provenance, evidence, checkpoint, temporal and rescue modules below were unchanged by that commit. An open documentation/localisation pull request was inspected separately and left untouched.

The previous behaviour was captured in regression fixtures where practical. The new checks are deterministic and do not treat retrieval metrics, workflow labels or modelled scenarios as evidence that a scientific claim is true.

## Ten improvements and acceptance criteria

1. **Provenance-chain genesis and uniqueness checks**
   - Before: a first record with a non-null parent digest could pass the chain check; repeated source IDs were not reported.
   - Now: the genesis parent must be null, every later parent must match the preceding record digest, and duplicate source identifiers are reported with exact indices.
   - Acceptance: valid two-record chains pass; orphaned genesis links and repeated source IDs fail with machine-readable diagnostics.
   - Regression risk: existing chains that intentionally reuse source IDs or start from an externally anchored parent will now need an explicit anchor design rather than being treated as self-contained chains.

2. **Field-weighted research-memory retrieval**
   - Before: topic text, statement text, campaign identifiers and opaque source IDs shared one lexical overlap score.
   - Now: deterministic BM25-style scoring weights topic terms above statement terms; source and campaign identifiers are exact filters rather than free-text evidence.
   - Acceptance: the fixed regression fixture moves a campaign-metadata token collision below the relevant research statement; exact source and campaign filters still retrieve the intended record.
   - Regression risk: users who previously searched by typing a source identifier into the prose query must use the explicit source_id filter.

3. **Retrieval-quality evaluation**
   - Before: memory search had no standard ranking-quality report.
   - Now: MRR@k, precision@k, recall@k and nDCG@k are calculated from labelled query fixtures, with a before/after comparator. A repeatable helper also reports median and p95 search latency without imposing a machine-specific pass threshold.
   - Acceptance: the fixture reports an MRR@1 increase from 0.0 to 1.0 for the known metadata-token collision; recall non-regression is explicitly reported.
   - Limitation: synthetic labelled fixtures do not establish performance on an external scientific corpus. Real relevance labels are still needed for representative benchmarking.

4. **Evidence-packet completeness and reference resolution**
   - Before: validation mostly checked whether required fields were truthy and whether source IDs were duplicated.
   - Now: text types, source-list shape, empty identifiers, duplicate IDs, optional source resolution and declared independence groups are checked separately.
   - Acceptance: unresolved source references block review readiness; a structurally complete single-source packet remains eligible but carries a corroboration warning.
   - Limitation: a resolved source ID is not proof that the source is authentic, high quality or correctly interpreted.

5. **Context-mismatch audit for conflicting claims**
   - Before: same-context conflicts were returned, but claims in different units, scopes or conditions were simply absent from the result.
   - Now: the audit reports same-context conflicts and separately lists context groups that were intentionally not compared.
   - Acceptance: different units are not falsely compared; conflicting values within matching declared contexts remain visible.
   - Limitation: context metadata is supplied by callers and is not independently verified or automatically converted.

6. **Bounded agent hand-off packets**
   - Before: there was no single bounded packet that combined task intent, open questions, constraints and relevant collective memories.
   - Now: a deterministic hand-off envelope carries status, source IDs, provenance groups, review notes and matched terms under a configurable character budget.
   - Acceptance: source references and contested/rejected states are retained; the packet reports omissions and never authorises execution.
   - Regression risk: records that exceed the context budget are omitted rather than silently truncated; callers must inspect the omission count.

7. **Hash-linked research checkpoints and explicit diffs**
   - Before: checkpoints were versioned in memory but had no integrity digest or structured comparison.
   - Now: each checkpoint hashes its canonical content and previous digest; verification detects altered history, and diffs list state, source and unresolved-question changes.
   - Acceptance: two-step histories verify and produce deterministic added/removed source and question sets.
   - Limitation: the ledger remains in-memory in this module; durable cross-process storage is not claimed.

8. **Uncertainty-aware temporal map windows**
   - Before: observations could be filtered by a maximum uncertainty threshold but not queried by interval overlap; a repeated source ID silently replaced its earlier observation.
   - Now: ISO-8601/date/year timestamps are normalised to UTC, uncertainty-expanded interval queries are available, non-finite uncertainty is rejected, and conflicting duplicate source IDs are refused.
   - Acceptance: an observation whose uncertainty interval overlaps a requested time window is returned; the same query without uncertainty expansion is not; duplicate overwrite is blocked.
   - Limitation: the interval is a simple symmetric bound, not a calibrated probability distribution or recovered historical record. A year-only timestamp is represented by 1 January at 00:00 UTC, not by a full-year interval.

9. **Priority-tiered, proportional rescue-resource allocation**
   - Before: a single needs/stock comparison reported aggregate allocations without distributing scarce stock across multiple requests.
   - Now: higher explicit priority tiers are served first; tied requests share remaining integer stock proportionally using deterministic largest-remainder rounding.
   - Acceptance: a four-unit urgent request is fully allocated before two equal-priority requests share the remaining two units; human review and dispatch remain mandatory.
   - Safety boundary: this is a planning aid only. It does not make medical, evacuation, eligibility or dispatch decisions.

10. **Audited retention projections**
    - Before: the basic helper retained the latest record per key and truncated the result, without reporting omitted records or carrying forward older source references.
    - Now: a non-destructive projection protects candidate/contested/rejected/current records, aggregates source lineage across retained versions, and reports capacity overflow and provenance-retention ratio. The keep-latest option can be disabled when callers need individual version rows.
    - Acceptance: the latest version keeps source references from earlier versions of the same key; contested records are not silently dropped when protected records exceed the nominal cap.
    - Limitation: this function produces a projection only. It does not delete or compact the persistent database.

## Verification

The new regression suite is core/tests/test_daily_upgrades_2026_11_04.py. It covers all ten capabilities, including the retrieval before/after metric fixture, provenance retention, contradiction context separation, temporal interval overlap, fair allocation and protected-retention overflow.

The pull request must pass the repository's Python 3.11/3.12/3.13 CI matrix and web-interface checks before merge. GitHub Pages deployment and any hosted Render deployment are intentionally not triggered from this feature branch. No payment, tax, refund, customer-data, credential, legal-policy or commercial-promise settings were changed.
