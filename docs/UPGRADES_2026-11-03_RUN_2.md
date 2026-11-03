# Research infrastructure upgrades — run 2

This run adds ten independently useful, public research-support capabilities. They build on the preceding research-memory, provenance, contradiction, evidence-quality, Virtual Time Mapping, rescue-workflow and localization infrastructure. They are deliberately conservative: none establishes scientific truth, enables unsafe action, or replaces independent review.

## Acceptance criteria and regression comparison

1. **Uncertainty propagation** — adds independent-error quadrature and worst-case bounds. Previous behavior exposed numeric observations without a reusable uncertainty-combination primitive. Acceptance: non-negative inputs produce deterministic bounds; invalid uncertainty is rejected.
2. **Reproducibility manifests** — creates canonical, hashed run manifests and field-by-field comparisons. Previous behavior stored protocol/dataset records separately. Acceptance: identical manifests hash identically and changed fields remain visible.
3. **Repeatable benchmark registry** — stores benchmark observations with sample counts and baseline deltas. Previous behavior could measure individual operations but lacked a small reusable comparison registry. Acceptance: comparisons expose absolute/relative changes and explicitly avoid intelligence claims.
4. **Public accessibility audit** — detects selected high-value HTML accessibility omissions such as missing image alternatives and missing main landmarks around interactive content. Previous behavior relied on broader project checks. Acceptance: known violations are reported deterministically; the audit is explicitly not a complete WCAG review.
5. **Temporal snapshot diffing** — compares recorded Virtual Time Mapping observations across snapshots. Previous behavior could filter/export observations but did not provide a structured change report. Acceptance: additions, removals and changes are preserved; it never claims recovery of unrecorded history.
6. **Evidence-aware research queue** — prioritizes follow-up work using missing evidence, contradictions, review deadlines and safety gates. Previous scheduling handled work allocation but not this evidence-gap prioritization layer. Acceptance: higher-risk/review-sensitive items receive deterministic higher priority.
7. **Agent capability registry** — records explicit capabilities and reports missing coverage before routing work. Previous coordination selected waiting agents without a reusable capability matrix. Acceptance: only explicitly registered capabilities satisfy requirements; execution is not started by the registry.
8. **Rescue resource planner** — computes bounded allocations and shortages for a conservative civil-protection resource allowlist. Previous rescue planning identified safe action categories but did not quantify resource gaps. Acceptance: allocations never exceed declared stock and dispatch/medical decisions remain human-controlled.
9. **Bounded memory compaction** — deduplicates normalized statements while preferring validated records and enforcing a maximum retained count. Previous retention provided storage bounds; this adds statement-level consolidation. Acceptance: duplicate statements collapse, validated records win ties, and retained count never exceeds the bound.
10. **Evidence packet validator** — checks minimum public evidence-packet completeness and duplicate source references before review. Previous evidence tooling assembled and scored evidence; this adds a lightweight pre-review gate. Acceptance: missing required fields or duplicate source IDs block review readiness.

## Tests

`core/tests/test_upgrades_2026_11_03_later.py` provides deterministic regression coverage for all ten features. CI remains the authoritative acceptance gate; repository writes alone are not treated as proof that CI has passed.

## Limitations

These utilities improve traceability, reproducibility, prioritization and safety structure. They do not increase scientific intelligence by assertion, prove hypotheses, recover the unrecorded past, certify protective equipment, automate emergency decisions, or replace domain experts, ethics review, human-subject protections, privacy safeguards, cybersecurity controls or applicable law.
