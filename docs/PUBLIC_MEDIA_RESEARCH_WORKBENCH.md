# Public Media Research Workbench

**Status:** bounded research-discovery and human-review utilities. This is not an automated fact-checker.

The workbench connects the existing public metadata normalizer, source identity controls and multilingual discovery cues into a repeatable intake workflow. It accepts records already obtained through an official API or a permitted public feed. It does not crawl websites, authenticate, download videos, access private material, follow redirects or bypass platform terms.

## Ten independently usable capabilities

1. **Platform-origin binding** — `validate_platform_origin` checks exact HTTPS hostnames for supported platforms. Generic forums require an explicit exact-host allowlist. It rejects embedded credentials, IP-literal hosts, non-standard ports and suffix lookalikes. It does not follow redirects.
2. **Exact cross-platform text clustering** — `content_fingerprint` and `cluster_exact_content` use NFKC, case-folding and whitespace normalization. Exact matches are review candidates only. Original records remain intact; no semantic similarity or scientific independence is inferred.
3. **Explainable topic retrieval** — `score_topic_relevance` uses the existing multilingual tokenizer and reports matched/missing tokens. Its unique-token recall score is a lexical retrieval aid, not a truth, source-quality or expertise score.
4. **Caption readiness** — `assess_caption_readiness` distinguishes provider-reported caption availability from a transcript actually supplied to the workbench. It reports token/character counts and language mismatches but does not establish completeness or transcript accuracy.
5. **Translation review** — `build_translation_review` preserves original and supplied translation text separately, fingerprints both, checks reviewer-declared protected terms and records a human decision. It never performs machine translation.
6. **Claim candidates** — `extract_claim_candidates` returns sentence spans with Unicode code-point offsets and transparent lexical signals. Every span remains unverified and has no evidence link by default.
7. **Human review queue** — `prioritize_review_queue` produces deterministic priorities and reason codes for origin, privacy, translation, sensationalism, transcript and candidate-claim review. It never adjudicates claims.
8. **Snapshot comparison** — `compare_record_snapshots` reports additions, absence and field-level changes. Absence is not a retraction; changed metadata is not a correction.
9. **Fair intake budgeting** — `plan_intake_budget` uses deterministic round-robin platform selection and whole-record budgets. Exclusions include explicit reasons; individual records are never silently truncated.
10. **Tamper-evident audit chain** — `build_audit_chain` and `verify_audit_chain` provide a bounded SHA-256 chain over event metadata and payload digests. The chain stops at 1,000 events rather than pruning history. Store payloads separately under an appropriate retention policy.

## End-to-end use

`prepare_public_media_batch(records, query, approved_forum_hosts=..., transcripts=..., translations=...)` composes origin validation, legacy normalization, multilingual cue triage, lexical relevance, caption readiness, candidate sentence extraction, exact-content clustering and review prioritization. The output includes a deterministic manifest fingerprint.

A record rejected by the strict origin check is retained in the `rejected` report and the review queue with a reason; it is not silently dropped. Existing `normalize_public_record` and `normalize_public_batch` APIs are unchanged. The new strict origin gate is opt-in through this workbench.

## Reproducibility and limits

- All input sizes and outputs are bounded; no network calls or new runtime dependencies are required.
- Text hashes and audit hashes are integrity identifiers, not proof that content is authentic or true. A hash chain without an independently retained trusted head hash is not a digital signature or non-repudiation mechanism.
- Exact duplicate candidates may be syndicated copies, quotations or coincidentally identical short text. They are not merged.
- Lexical matching can miss synonyms, slang, negation, sarcasm and domain-specific phrasing. No cue is not a reliability signal.
- Japanese and other CJK text use the existing script-aware tokenizer for retrieval and sentence punctuation for span extraction. This is not a full Japanese parser or translation engine.
- Translation protected-term checks are exact normalized string checks and can produce false alarms. A reviewer decision is a recorded attestation, not proof of translation correctness.
- Candidate extraction is deliberately overinclusive; a sentence is not necessarily a scientific claim.
- The queue score is a disclosed workflow ordering aid, not a source-trust score.
- No public media item becomes scientific evidence merely by entering this workbench. Evidence packets, source provenance, domain expertise, independent review and reproducibility requirements remain separate.
- Do not place private messages, credentials, personal data or sensitive location data in events, transcripts or public records. Follow applicable law, consent, platform terms and institutional review requirements.

## Benchmark and tests

Run from the repository root:

```bash
python -m py_compile core/ssswet_core/public_media_research_workbench.py
cd core
python -m pytest -q tests/test_public_media_research_workbench.py
cd ..
python .github/scripts/benchmark_public_media_workbench.py
```

The CI benchmark uses 250 synthetic metadata records, three measured repeats and a five-second per-workload ceiling. It reports median and maximum wall-clock time. Results are environment-specific and are not intelligence or scientific-quality evaluations.


## Baseline comparison

| Capability | Immediately before this workbench | New behavior |
|---|---|---|
| Platform identity | Public metadata normalization accepted HTTPS URLs without a platform-host binding stage | New opt-in exact-host validation rejects mismatched origins and requires exact forum allowlists; legacy normalization remains compatible |
| Cross-platform text duplicates | Strong identifiers and exact source hashes were available, but there was no normalized public-text candidate clustering across social/video records | New NFKC/case-folded text fingerprints expose exact-match candidates without merging or deleting sources |
| Topic retrieval | Multilingual script-aware tokenization existed, but no record/query overlap report was produced by the public-media intake path | New deterministic matched/missing token report and normalized lexical recall score |
| Captions | Provider metadata could say whether captions were available | New readiness output distinguishes provider-reported availability from a transcript actually supplied for review |
| Translation | Script-aware triage could inspect configured sensationalism cues; it did not maintain a bilingual reviewer record | New original/translation hashes, protected-term checks and explicit human decision state |
| Claim spans | Public metadata was normalized as discovery material, without stable sentence offsets | New bounded sentence candidates with Unicode code-point offsets and an unverified status |
| Review ordering | Existing general review queues operated on registered research records | New deterministic media-specific queue exposes origin, privacy, translation, cue and transcript reason codes |
| Revisions | Source identity and literature-watch comparisons existed for bibliographic candidates | New field-level comparison for normalized social/video snapshots; absence is explicitly not retraction |
| Intake budgets | Batch normalization had a record cap but no multi-platform text/serialized-byte budget planner | New whole-record, round-robin selection with per-record exclusion reasons |
| Audit history | Existing provenance and research ledgers served other research entities | New self-contained, bounded SHA-256 event chain for public-media intake events |

The new workbench is opt-in and additive. It does not replace the existing literature watch, research memory, evidence dossier, or provenance graph. It is a Python core capability; this change does not add a new browser screen or claim that every live bot automatically invokes it.
