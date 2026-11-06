# Research assurance upgrades — 5 November 2026

This change set adds ten independently useful, test-backed improvements to SSSWET's scientific assurance and public research infrastructure. It is based on main at commit 940576d77f5fdf28323880fbce19ed66c85cde2e; the immediately preceding commit 1ec1633c98fa11892e41c0ca7c5972c03efbccd9 differs only in the Virtual Time Travel service-worker cache version. The earlier open research-continuity PR (#3) and cross-origin write-guard PR (#4) were inspected and left untouched; this change avoids their modified files.

## Acceptance criteria and delivered behaviour

1. **Dimension-safe units** — preserve all previously supported within-dimension conversions; reject cross-dimension conversions, booleans, NaN and infinity. The prior implementation silently returned a numeric ratio for incompatible dimensions such as metres-to-seconds.
2. **Conservative source independence** — the new analyze_sources audit merges records only on DOI, canonical URL, explicit canonical/syndication identity, or exact publisher/title pairs. Publisher or domain alone never collapses distinct papers. Duplicate source IDs are rejected. The legacy group_sources helper retains its prior publisher/DOI/domain metadata buckets for compatibility and must not be used as an independence count.
3. **Evidence freshness assessment** — produce deterministic fresh, aging, stale, unknown_date and future_dated states from a supplied reference date and source-type half-life. Unknown/future records require review; no record is automatically excluded.
4. **Prospective preregistration amendments** — verify snapshot fingerprints, record changed JSON-pointer paths, actor, reason and evidence references, and preserve the original snapshot. Identical or tampered prior snapshots cannot be amended.
5. **Reproducibility manifest verification** — canonicalize dataset references, parameters and source identifiers; reject duplicate dataset references and non-finite JSON values; detect payload tampering by recomputing SHA-256.
6. **Expanded dataset leakage audit** — retain identifier overlap checks and optionally add declared group overlap, normalized exact-text duplicate overlap and chronological split-order checks. It explicitly does not claim semantic or near-duplicate detection.
7. **Translation placeholder parity and fallback** — identify mismatched {name} / {{name}} placeholders and resolve exact locale, base language, then configured fallback. Existing coverage and missing-key fields remain.
8. **Expanded static accessibility audit** — detect missing image alt attributes, unnamed buttons/links, unlabeled form controls, duplicate IDs, unresolved aria-labelledby references, skipped heading levels and main-landmark problems. This remains a heuristic, not a WCAG certification.
9. **Bounded knowledge-graph path tracing** — add cycle-safe breadth-first evidence-path queries with relation/direction filters and hard depth/path caps. Results expose visited-node count and truncation; graph edges remain declarations, not proof.
10. **Explainable agent capability routing** — rank agents only when all required capabilities are present and capacity/status allow; expose partial matches, exclusions, preference matches and utilization. Routing proposes candidates only; it does not assign work or authorize autonomous execution.

## Regression risks and controls

- Cross-dimension unit conversion now raises ValueError; callers that relied on the previous meaningless ratio must correct their units.
- Source independence is more conservative through analyze_sources. The compatibility helper group_sources preserves its historic publisher-first grouping and is not a valid corroboration metric.
- Freshness classifications depend on the selected half-life and supplied timestamp. They are review cues, not evidence-quality scores.
- Preregistration amendments are returned as immutable-by-convention snapshots; durable persistence is the caller's responsibility.
- Manifest ordering is canonicalized, so the digest is stable for equivalent lists of dataset references and source IDs. It is not a digital signature.
- Group/content/time leakage checks are opt-in. Exact normalized text is not semantic deduplication.
- HTML accessibility findings are static heuristics; keyboard and screen-reader testing remains necessary.
- Graph traversal is bounded and in-memory over supplied records; no graph data is modified.
- Agent rankings are deterministic proposals and do not certify competence or independence.

## Verification

core/tests/test_research_assurance_2026_11_05.py covers all ten improvements, including compatibility paths and negative cases. Public-reader documentation is in this file. CI is required before merge. No payment, tax, refund, customer-data, credential, legal-policy or commercial-promise settings are changed.
