# Research quality upgrades — 11 November 2026

This release proposal adds ten independent, additive research-support capabilities. Existing storage schemas, public routes, payment settings, customer data, credentials, legal policies and deployment settings are untouched.

## Baseline inspection

The implementation was based on the current main tree at 18452711042712cbd41175bc710526532f6bf4f7 and its immediate predecessor 96a1bd80881f017ccdf5ee8ba2b5642ee2608c9d. The direct comparison showed that the only intervening change removed an accidentally committed, incomplete test fixture; no application code changed in that one-commit interval. The new work is additive to the inspected current tree.

The current baseline already included scientific-memory versioning, bounded memory compaction, evidence freshness weighting, source-quality assessment, research knowledge graphs, task decomposition, reviewer proposals, Virtual Time Mapping, rescue resource allocation and reproducibility manifests. The ten additions below deliberately complement those facilities instead of replacing their existing interfaces.

## Ten independently usable improvements

### 1. Multilingual research-text triage

**New module:** multilingual_research_triage.py

- Adds Unicode compatibility normalization, diacritic-insensitive matching without transliteration, broad script profiling and CJK/Thai character-bigram tokenization.
- Adds conservative sensationalism cue lexicons for 21 languages: Arabic, Bengali, German, English, Spanish, French, Hebrew, Hindi, Indonesian, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Russian, Thai, Turkish, Ukrainian, Vietnamese and Chinese.
- Returns matched phrases and script observations, not a probability, truth verdict or automatic evidence downgrade.

**Acceptance criteria:** fixtures cover Latin, Arabic, Devanagari, Cyrillic, Hangul, Japanese and Chinese text; Japanese and French/English cue matches are reproducible; original text is preserved; unsupported language codes fail closed.

**Previous behaviour:** no shared multilingual clickbait-cue or script-aware retrieval utility existed in the current core package. The addition is opt-in and does not change provider ingestion.

**Regression risks and controls:** lexical false positives and missed idioms are possible. Every result explicitly says that translation, language identification, truth assessment and evidence-status changes were not performed.

### 2. Provenance-preserving source identity and deduplication

**New module:** source_identity.py

- Canonicalizes safe HTTP(S) URLs, removes common tracking parameters, preserves content-bearing query parameters, and normalizes DOI and arXiv identifiers.
- Groups only exact strong identifiers: DOI, arXiv ID, canonical URL or supplied SHA-256 content digest.
- Retains every original source record and reports clusters as duplicate candidates; it never infers scientific independence or deletes records.

**Acceptance criteria:** tracking-only URL variants normalize identically; DOI and arXiv variants cluster; title-only matches remain separate; duplicate source IDs and unsafe URL schemes are rejected.

**Previous behaviour:** source independence was assessed from declared provenance, but there was no single reusable strong-identifier clustering utility.

**Regression risks and controls:** canonical URL rules can occasionally collapse mirrors or preserve different aliases. The output exposes the exact identity keys and keeps original records untouched so a reviewer can reverse a mistaken grouping.

### 3. Permission-aware multilingual research query plans

**New module:** research_query_plan.py

- Produces bounded, deterministic search plans from explicitly supplied translated terms, language tags, inclusion/exclusion terms and date ranges.
- Describes access requirements for scholarly indexes, preprint servers, standards catalogues, institutional repositories, YouTube, X, Instagram, Facebook, Threads, Bluesky, Reddit, Snapchat, MeWe, Weibo, Bilibili, Niconico, Qiita and public forums.
- Marks permission-sensitive channels for operator configuration and explicitly forbids private-content access or terms-of-service bypass.

**Acceptance criteria:** query generation is bounded to 100 entries; invalid dates, language tags and channels are rejected; plan fingerprints are stable for identical inputs; platform-specific permission requirements remain visible.

**Previous behaviour:** providers could be configured individually, but the core had no common, reproducible, permission-aware query-plan object.

**Regression risks and controls:** a query plan is not proof that a platform exposes a search API or grants access. The module only prepares a plan; it does not execute requests, log in, scrape private material or bypass platform controls.

### 4. Explicit evidence applicability windows

**New module:** evidence_applicability.py

- Evaluates supplied observation/publication dates, validity windows and reviewer-declared review intervals.
- Distinguishes undated, future-dated, not-yet-valid, outside-window, review-due and no-expiry-policy records.
- Requires timezone-aware timestamps and accepts date-only values as UTC dates.

**Acceptance criteria:** deterministic results for a supplied assessment time; invalid naive timestamps and reversed validity windows fail; no-expiry records are never silently marked current or automatically deleted.

**Previous behaviour:** the core had exponential freshness weighting but no policy-aware validity-window assessment.

**Regression risks and controls:** scientific evidence does not have one universal expiry period. No half-life or domain policy is invented; the module reports only the policy supplied by the caller and never modifies source claims.

### 5. Measurable memory retrieval evaluation

**New module:** memory_retrieval_evaluation.py

- Calculates precision@k, recall@k, reciprocal rank, provenance-group recall and contradiction retention on labelled query fixtures.
- Aggregates supplied retrieval latency using median and p95, and can record the measured storage footprint.
- Enforces bounded query/result counts and rejects duplicate retrieval IDs.

**Acceptance criteria:** deterministic metric values for identical labelled inputs; contradiction and provenance coverage are reported separately; latency is measured only when supplied; storage size is explicit.

**Previous behaviour:** memory helpers exposed lexical overlap and validated-hit summaries, but no reusable multi-query benchmark measured relevance, provenance continuity and contradiction retention together.

**Regression risks and controls:** benchmark scores depend on the quality and representativeness of labels. Results are explicitly not a measure of model intelligence, scientific truth or generalization beyond the supplied fixtures.

### 6. Machine-checkable agent task contracts

**New module:** agent_task_contracts.py

- Captures task identity, objective, creator, assignee, independent reviewer, required and forbidden capabilities, input references, source allowlist, required output fields and hard execution budgets.
- Rejects missing capabilities, prohibited capabilities and reviewer/assignee/creator identity collisions.
- Validates proposed completions without executing or accepting them.

**Acceptance criteria:** capability gaps and forbidden capabilities block contract creation; reviewer separation is enforced; output completeness and source allowlists are checked; step and runtime limits are bounded.

**Previous behaviour:** task decomposition and capability matching existed, but a single task object did not bind those decisions to explicit inputs, outputs, budgets and review separation.

**Regression risks and controls:** a valid contract cannot guarantee that an agent follows it. Contracts are advisory enforcement data; execution, review and scientific approval remain separate.

### 7. Append-only agent conflict and recusal register

**New module:** agent_conflict_register.py

- Records scoped conflict declarations for campaigns, sources or global work.
- Adds independent, evidence-linked review events for recusal or clearance without overwriting the original declaration.
- Treats missing declarations as unknown, not as proof of independence.

**Acceptance criteria:** an agent cannot review its own declaration; conflict review requires evidence references; each review supersedes the prior event; unresolved or recused conflicts block assignment in the matching scope.

**Previous behaviour:** reviewer selection already screened supplied conflict statuses, but there was no reusable versioned register to preserve declarations and later decisions.

**Regression risks and controls:** disclosure completeness and reviewer identity are not independently verified by this in-memory utility. Clearance never certifies independence; the complete event history remains available for audit.

### 8. Deterministic research-graph snapshots and diffs

**New module:** research_graph_snapshot.py

- Produces canonical, size-bounded snapshots of graph nodes and edges with stable SHA-256 fingerprints.
- Verifies snapshot integrity and reports added, removed and changed nodes/edges between two verified snapshots.
- Preserves node/edge payloads and leaves the source graph unchanged.

**Acceptance criteria:** record ordering does not change the fingerprint; a one-field mutation invalidates the prior digest; diff output is deterministic; snapshots are limited to 10,000 nodes, 20,000 edges and 5 MB.

**Previous behaviour:** the knowledge graph supported append-only relationships and bounded impact traversal, but there was no standalone deterministic snapshot/diff interface.

**Regression risks and controls:** a hash detects accidental changes but is not a signature or proof of origin. Snapshots do not certify the truth of graph contents.

### 9. Anchor-bounded Virtual Time clock alignment

**New module:** temporal_clock_alignment.py

- Builds per-session, per-source clock models from at least two explicitly paired source/reference timestamps.
- Interpolates only between monotonic anchors, propagates declared anchor uncertainty and reports observed drift in parts per million.
- Refuses cross-session alignment and refuses extrapolation outside the anchor interval.

**Acceptance criteria:** deterministic interpolation for a synthetic two-anchor fixture; non-monotonic or timezone-naive anchors fail; events outside the anchor interval remain unaligned; session boundaries are preserved.

**Previous behaviour:** Virtual Time Mapping already represented recorded observations and uncertainty clusters, but had no separate tool for aligning two declared clocks.

**Regression risks and controls:** incorrect anchors can produce misleading aligned timestamps. The model reports anchor provenance, uncertainty and drift; it does not infer missing history, event identity or future events.

### 10. Civil protective/rescue design assurance case

**New module:** rescue_design_assurance.py

- Links requirements to verification records and hazards to documented controls.
- Requires independent review evidence for high-severity or high-likelihood hazards.
- Distinguishes missing traceability, recorded test failures, missing independent review and evidence ready for human safety review.
- Accepts only civil protective/rescue design classes.

**Acceptance criteria:** missing controls and requirement verification are surfaced; critical hazards without independent review remain blocked; failed verifications remain visible; weapon-class requests are rejected; no result marks a design safe, approved or deployment-ready.

**Previous behaviour:** rescue resource planning and protective-system scoring existed, but there was no unified requirement–hazard–control–verification traceability case.

**Regression risks and controls:** a complete record is not proof of safety. Qualified human review, legal compliance, field validation and deployment authorization remain mandatory and outside this module.

## Validation and non-regression plan

- Python compatibility: Python 3.11+ and standard-library-only implementation.
- Automated coverage: dedicated tests exercise all ten new modules, their failure paths, bounded inputs, provenance retention, contradiction retention, session isolation and safety gates. Additional hardening tests cover Japanese kana, order-sensitive URL queries, IPv6 URLs, exact review-interval boundaries, true median/p95 latency, conflicting evidence-reference fields, defensive copies, malformed snapshot/clock structures, control-owner recusal and oversized channel lists.
- Existing behaviour: legacy evidence freshness, Virtual Time Mapping and rescue resource-planning APIs remain unchanged and are covered by the repository's existing suite.
- Performance controls: all new bulk interfaces impose explicit record/query/byte caps; graph snapshots and query plans are deterministic; no unbounded background work or storage writes are introduced.
- Security and privacy: no credentials, private platform content, customer data, payment/tax/refund logic, legal policy or deployment secrets are read or modified.
- Scientific limits: no module autonomously adjudicates evidence, approves a design, authorizes an experiment, or claims that agent intelligence has increased.

The release is acceptable only if the complete core test suite and existing web checks pass on the pull-request commit. Any CI failure must be treated as a blocker, not as a successful release.


### Follow-up: provenance-preserving clock alignment

The anchor-bounded clock utility now emits schema version 2 with stable anchor identifiers, optional bounded reference-evidence references, per-interval drift diagnostics, and explicit uncertainty semantics. Aligned events retain their bracketing anchor IDs, interpolation fraction, interval drift, and available evidence references. Anchor and event uncertainty are treated as user-declared absolute bounds and combined linearly; if any required bound is undeclared, the model withholds the numeric total instead of silently assuming zero. Version-1 models remain verifiable, but their uncertainty/provenance completeness is not overstated. Regression coverage includes deterministic ordering/digests, exact-anchor provenance, missing uncertainty, semantic-flag tampering with a recomputed digest, bounded identifiers/references, and legacy compatibility.

**Scope note:** this remains a Python core research utility. It does not yet rewrite or automatically align browser IndexedDB records, and no new browser sensor, network, or service-worker behavior was introduced.
