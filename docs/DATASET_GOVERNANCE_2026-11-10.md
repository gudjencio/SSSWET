# Dataset governance and release assurance — 10 November 2026

This change adds ten callable, bounded dataset-governance capabilities to the SSSWET Python core. It complements the existing metadata-only dataset registry, field-name privacy checks, record-ID split check and run reproducibility manifest. It does not replace those APIs, migrate SQLite, store datasets or change existing records.

## Baseline inspected

- Current main: 628c732839f1a916ceedea6d16efb7b35628118d.
- Immediate predecessor: f570158bdcbd6145bca4753f109088fc2c714c0c.
- The one-commit comparison contains only a one-line wording change in the Virtual Time Travel documentation; application code is unchanged between those revisions.
- Adjacent modules inspected: dataset_registry, data_quality, data_quality_profile, missingness_analysis, split_leakage, schema_versioning, bounded_retention, privacy_minimization, reproducibility_manifest, sources and evidence_packet_validator. The dataset registry, split check, privacy helper and run manifest have identical blob hashes in both baseline revisions.
- Pending PRs #18, #19, #22, #23 and #24 were reviewed to avoid duplicating the bounded research toolkit, engineering assurance, Virtual Time Travel workbench, regression coverage and structured agent-deliberation proposals.

## Ten functional improvements

| # | Capability | Previous behaviour | New behaviour and acceptance criteria |
|---|---|---|---|
| 1 | Explicit licence-use policy gate | Dataset metadata stored a licence label but did not check a requested use against an attributable review decision. | Requires approved review status, reviewer reference, timezone-aware review timestamp and explicit permitted/prohibited use lists. Case-insensitive duplicates are rejected. A use passes only when explicitly permitted and not prohibited. No legal interpretation is attempted. |
| 2 | Consent and purpose-scope gate | Dataset metadata represented consent status but did not check purpose and sharing scope together. | Documented consent requires evidence and reviewer references; a not-required decision requires a reason and reviewer. Pending, unrecorded and withdrawn states block. Requested purpose and sharing authorization are checked without collecting participant identifiers. |
| 3 | Field-level release disposition audit | Existing privacy screening flagged some identifier-like field names but did not check whether minimization actions were completed and evidenced. | Checks up to 5,000 field declarations, classification, release action, completion status and transformation/review references. Sensitive fields cannot pass as included or merely planned. Field values are never inspected or redacted automatically. |
| 4 | Small-cell and complementary disclosure suppression | No aggregate-output helper suppressed low-count cells and a second cell when a group would otherwise contain exactly one suppression. | Checks up to 20,000 aggregate cells, suppresses counts below a configurable minimum (2–1,000), and applies deterministic complementary suppression. Suppressed counts are null. This reduces a narrow differencing risk but does not guarantee anonymity. |
| 5 | Dataset schema compatibility diff | A schema-version guard checked a record's declared version and required keys, but did not compare two field contracts. | Compares up to 5,000 fields, reports optional additions separately, and flags removed, type-changed, newly required or newly non-nullable fields as potentially breaking. No migration is applied. |
| 6 | Dataset/transformation lineage DAG audit | Existing registries recorded versions and transformations, but there was no standalone bounded graph audit for missing endpoints, self-links, cycles and deterministic topological order. | Audits up to 10,000 nodes and 50,000 edges; rejects duplicate nodes/edges, reports missing endpoints and unresolved nodes, and produces deterministic topological ordering using a heap-based traversal. |
| 7 | Group-aware and chronological split leakage audit | The existing split check detected repeated record IDs only. | Checks up to 200,000 rows for group overlap and chronological ordering across named splits. Requires timezone-aware ISO-8601 timestamps, normalizes to UTC, and reports overlap patterns/counts without returning group identifiers. Semantic and near-duplicate leakage remain out of scope. |
| 8 | Non-destructive retention review planner | Dataset records could describe a retention policy, but no date-based helper identified when review was due. | Plans review dates for up to 10,000 records, recognizes policy/legal holds, sorts due reviews first and reports overdue counts. It never deletes, archives or changes data or policy. |
| 9 | Integrated dataset release-readiness gate | Governance checks were separate, so callers could omit a category without one consolidated report identifying missing checks. | Requires eight explicit boolean gates: licence, consent, field privacy, disclosure, schema, lineage, split integrity and retention. Missing, malformed or failed gates block readiness for human review. It never authorizes release or grants scientific, legal or ethics approval. |
| 10 | Deterministic release manifest and verifier | Existing reproducibility manifests covered protocol/run inputs, but not a bounded dataset-release package binding artifact digests to the governance report. | Produces a metadata-only canonical manifest with schema/artifact SHA-256 values, source/review references and a digest of the readiness report. Identical inputs produce identical manifests; tampering is detected. SHA-256 is integrity evidence, not author authentication or a digital signature. |

## Local API

Import the helpers from ssswet_core.dataset_governance. The public functions are:

- assess_license_use
- assess_consent_scope
- audit_field_release_policy
- screen_aggregate_disclosure
- compare_dataset_schemas
- audit_lineage_graph
- audit_group_time_splits
- plan_retention_reviews
- build_release_readiness
- build_release_manifest
- verify_release_manifest

Example policy check:

    from ssswet_core.dataset_governance import assess_license_use

    report = assess_license_use(
        {
            "license_id": "CC-BY-4.0",
            "review_status": "approved",
            "reviewer_ref": "review:12",
            "reviewed_at": "2026-11-10T08:00:00Z",
            "permitted_uses": ["internal_research"],
        },
        "internal_research",
    )

All ten capabilities are pure in-memory helpers. They do not persist raw data, create database tables, call external services or modify existing research records. The caller is responsible for truthful policy and provenance declarations.

## Acceptance and regression controls

- 19 focused regression tests cover approved/pending/rejected licence states, consent withdrawal and scope, field-name privacy screening, transformation evidence, primary/complementary suppression, additive/breaking schema changes, lineage cycles and missing endpoints, group/time leakage, timezone normalization, retention holds, missing/malformed release gates, deterministic manifests, tampering and input limits.
- No new runtime dependency is introduced.
- No SQLite schema, existing API route, catalogue, PWA asset, payment setting, credential, customer record, legal policy or existing research record is changed.
- The existing CI matrix remains the compatibility gate for Python 3.11, 3.12 and 3.13. Its Python 3.12 benchmark step now includes ten synthetic dataset-governance workloads, each with a broad 5-second p95 ceiling.
- The lineage traversal was optimized after the first local benchmark exposed an avoidable quadratic isolated-node scan: a 5,000-node/4,999-edge synthetic graph improved from roughly 478 ms median to roughly 12 ms median in this environment.

## Synthetic benchmark snapshot

Five repetitions per workload in the development container; p95 is the maximum of the five samples. These are local regression baselines, not production guarantees.

| Workload | Input size | Median | p95 |
|---|---:|---:|---:|
| Licence policy | 1 | 0.006 ms | 0.050 ms |
| Consent scope | 1 | 0.003 ms | 0.009 ms |
| Field privacy audit | 1,000 fields | 4.619 ms | 5.182 ms |
| Aggregate disclosure screen | 10,000 cells | 14.066 ms | 14.857 ms |
| Schema diff | 1,000 fields | 1.286 ms | 1.433 ms |
| Lineage DAG audit | 5,000 nodes / 4,999 edges | 11.744 ms | 12.502 ms |
| Group/time split audit | 30,000 rows | 33.388 ms | 78.141 ms |
| Retention review plan | 5,000 records | 12.830 ms | 13.454 ms |
| Release readiness | 8 gates | 0.002 ms | 0.008 ms |
| Manifest build | 100 artifact digests | 0.222 ms | 0.463 ms |

A 10,000-cell disclosure run peaked at approximately 4.7 MiB of traced Python allocations. A 100-artifact manifest serialized to approximately 9.2 KiB. The functions are stateless; persistent storage growth is zero unless a caller chooses to save returned metadata. The CI benchmark uses a broad 5-second p95 guard to catch pathological regressions, not to claim a speedup over nonexistent prior operations.

## Regression risks and mitigations

- **Licence/consent declarations could be mistaken for legal or ethics approval.** Reports explicitly deny legal interpretation and approval; only attributed policy references pass the narrow declared gate.
- **Field-name screening can miss identifiers in free text or values.** It never claims full de-identification; sensitive-field release actions require completed transformation evidence.
- **Small-cell suppression can be defeated by auxiliary data or repeated releases.** Complementary suppression is included, but reports state that disclosure risk is not eliminated.
- **Schema additions could be mislabeled safe.** Newly required/non-nullable fields are treated as breaking; no migration is attempted.
- **Lineage traversal can leave downstream nodes unresolved when a cycle exists.** The output says nodes not topologically resolved, not that every such node is itself a cycle member.
- **Group/time split checks could leak group identifiers.** Reports aggregate overlap patterns and counts and do not return group values.
- **Timezone-naive timestamps could create false ordering.** They are rejected; valid times are normalized to UTC.
- **Retention planning could trigger destructive cleanup.** The module is read-only and returns no deletion command or action.
- **A readiness report could be mistaken for authorization.** The release gate and manifest hard-code release_authorized as false.
- **A matching SHA-256 could be mistaken for authenticity.** Verification reports author_authenticated as false; no signing key is handled.

## Limitations

These are policy-declaration validators and metadata-only checks. They cannot verify whether consent was validly obtained, interpret a licence, inspect raw data for hidden identifiers, guarantee anonymity, prove data quality, certify scientific independence, determine legal retention obligations or authorize a public release. Human, scientific, privacy, ethics, safety and legal review remain necessary.
