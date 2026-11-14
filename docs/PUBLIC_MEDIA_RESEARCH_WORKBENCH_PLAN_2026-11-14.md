# Public Media Research Workbench — acceptance plan (2026-11-14)

## Baseline inspected before implementation

- Main baseline: `b8b600847e2871ea56300a30c7015a110e20986a`.
- Immediate predecessor: `e32900aa8876d8d026c89bd5950cf6c9d1dd07a2`.
- The baseline already contains `public_media_ingestion.py`, `source_identity.py` and `multilingual_research_triage.py`. They normalize permitted public metadata, cluster strong source identifiers and surface multilingual lexical sensationalism cues. They do not constitute an end-to-end review workflow.
- The baseline contains separate provenance, evidence-packet, review-queue, memory and research-context components. This change must compose with, not replace, those components.
- Existing `normalize_public_record`, `normalize_public_batch`, `source_identity`, `cluster_sources` and `triage_title` contracts must remain unchanged.
- PR #55 is open against the inspected main baseline and is not part of this feature branch; its public wording/accessibility/scheduled-test changes are intentionally left untouched.

## Ten feature acceptance criteria

1. **Platform-origin binding** — require exact approved HTTPS host matching for supported social/video platforms; require explicit exact host allowlists for generic forums; reject credentials, IP literals, suffix spoofing and unknown hosts. Do not change the legacy normalizer.
2. **Cross-platform exact-content clustering** — normalize Unicode and whitespace, fingerprint public title/caption/text/description, cluster exact matches across platforms, preserve every original record, and never call a match a confirmed duplicate or independent-source finding.
3. **Explainable topic relevance** — use deterministic token overlap with the existing multilingual tokenizer; return matched terms and a transparent normalized score; never infer truth, expertise or scientific quality. Repeated runs must be byte-for-byte stable.
4. **Caption/transcript readiness** — assess only caller-supplied public metadata/transcript text; report explicit missing fields and bounded coverage indicators; do not fetch, download or infer absent captions.
5. **Human translation review** — retain original and supplied translation separately, fingerprint both, check caller-declared protected terms, and distinguish unreviewed/accepted/needs-revision; never generate or silently overwrite translations.
6. **Claim-candidate extraction** — return bounded sentence spans with exact character offsets and heuristic review reasons; every item remains a candidate requiring human verification; no automatic evidence or truth labels.
7. **Deterministic review queue** — rank review needs by disclosed reason codes (privacy flags, source mismatch, translation gaps, cue signals, missing transcript, candidate claims); retain ties deterministically; no automated adjudication.
8. **Snapshot revision comparison** — compare normalized snapshots by source ID and field; report added/removed/changed records; absence is not retraction and metadata changes are not corrections.
9. **Fair bounded intake planning** — apply record, text and serialized-size budgets using deterministic round-robin platform allocation; never truncate an individual record silently; report excluded records and exact reasons.
10. **Tamper-evident audit chain** — create a bounded SHA-256-linked event chain with deterministic canonicalization, verification and explicit capacity stop; do not silently prune or rewrite earlier events.

## Shared measurable gates

- Add at least 30 focused regression tests across the ten features.
- Test invalid inputs, hard caps, Unicode/Japanese text, exact duplicates versus near-duplicates, deterministic ordering, provenance retention and tamper detection.
- Synthetic 250-record workbench benchmark: all outputs deterministic; no network calls; no more than 5 seconds per measured operation in CI; report medians, not intelligence claims.
- No runtime dependencies added.
- Existing legacy public-media normalization and multilingual triage tests remain green.
- All outputs explicitly state that discovery metadata and lexical cues do not establish scientific evidence or truth.
- Run the complete core test suite and CI matrix before merge; do not merge if any regression is observed.

## Regression risks and mitigations

- **Host allowlist false rejection:** strict origin binding is a new opt-in stage; existing normalizer behavior is unchanged. Forum hosts must be supplied explicitly.
- **False duplicate clusters:** only exact normalized text hashes cluster; records are never deleted or merged and near-matches remain separate.
- **Lexical relevance bias:** the score is a transparent retrieval aid only; matched tokens are exposed and no truth/trust score is produced.
- **Clickbait false positives:** existing cues remain review prompts, not verdicts.
- **Translation false alarms:** protected terms are supplied by the reviewer; no machine translation or correctness claim is made.
- **Claim extraction misses/false positives:** preserve offsets and original text; all candidates require review.
- **Queue ordering bias:** return reason codes and deterministic tie-breaks; never suppress lower-priority records.
- **Snapshot absence ambiguity:** explicitly label absence as not observed in the newer snapshot, not retraction/deletion.
- **Budget exclusion:** exclude whole records only, with explicit counts/reasons; no silent truncation.
- **Audit capacity:** fail closed at the configured maximum and require an exported, verified archive before a new chain is started.

## Scope exclusions

No scraping, browser automation, authentication, private-content access, media download, platform terms bypass, automated translation, scientific adjudication, user profiling, personal-data enrichment, safety certification or real-world dispatch is introduced.
