# Public Media Evidence Pipeline

**Status:** opt-in, bounded Python research utilities for permitted public scientific-media discovery. This is not a scraper, automatic fact-checker or scientific review substitute.

This extension builds on the public-media workbench introduced in the 14 November 2026 mainline. It adds import, continuity, transcript, provenance, correction-history, privacy and export controls without changing the existing normalization or triage APIs.

## Ten independently usable improvements

1. **RSS 2.0, Atom 1.0 and JSON Feed 1.1 import** — parse_public_feed accepts caller-supplied UTF-8 text/bytes, normalizes approved public feed entries and records rejected links. It enforces a 2 MiB payload limit, 250-entry limit, exact HTTPS host allowlists and DTD/entity rejection. It performs no network requests.
2. **Provider adapter schema-drift audit** — audit_adapter_contract exposes the existing platform access-mode and metadata allowlists and reports missing, unexpected and sensitive field names before adapter output reaches normalization.
3. **Privacy-bounded pagination checkpoints** — build_pagination_checkpoint_chain and verify_pagination_checkpoint_chain retain sequence, page IDs, item IDs, opaque cursor hashes and external secure-store references. Raw cursors and credentials are never serialized. A caller must retain cursor values separately in an appropriately protected store if it needs to resume a provider session.
4. **Language/script consistency** — assess_language_script_consistency compares declared language metadata with Unicode script composition, including Japanese kana and Han-only ambiguity. It does not perform language identification.
5. **Headline/context review signals** — audit_headline_context combines the existing multilingual sensationalism cue set with title/body cue differences, uppercase ratio, repeated punctuation, certainty/qualification tension and lexical overlap. It produces reason codes and a review priority, never a clickbait or truth verdict.
6. **Time-coded transcript parsing** — parse_caption_transcript parses supplied WebVTT and SRT cues, validates time spans, retains cue identifiers and Unicode code-point offsets, and flags overlaps. It does not retrieve captions or download media.
7. **Claim-to-source provenance binding** — bind_claim_candidates_to_source binds existing sentence spans to a source snapshot SHA-256, exact offsets, optional transcript cue IDs and a separate translation reference. Original text remains authoritative for offsets; translations never replace it.
8. **Publisher correction/retraction ledger** — build_publisher_status_ledger and verify_publisher_status_ledger preserve explicit publisher-declared corrected, updated, retracted, removed and restored events in a bounded hash chain. Disappearance is not treated as retraction and prior source versions are not deleted.
9. **Public-text privacy screening** — scan_public_text_privacy detects common email, credential, IPv4, coordinate and phone-like patterns, returns code-point offsets and match hashes, and can produce a redacted preview without echoing matched values or mutating input.
10. **Deterministic human-review packet** — build_human_review_packet assembles bounded normalized source snapshots, claim bindings, transcript cues, translation and language review, publisher events and a reason-coded review queue. It strips tracking query strings, omits author display names, screens text before export, retains source hashes and enforces a 5 MiB maximum.

## Example: import a permitted feed

    from ssswet_core.public_media_evidence_pipeline import parse_public_feed

    result = parse_public_feed(
        feed_bytes,  # bytes already obtained through a permitted feed mechanism
        captured_at="2026-11-14T08:00:00+00:00",
        approved_hosts=["research-community.example"],
    )
    print(result["accepted_count"], result["rejected_entries"])

The approved host list is exact. A lookalike subdomain, HTTP URL, IP literal, embedded credential or non-standard port is not accepted. The parser does not resolve redirects or follow links.

## Example: preserve transcript and claim provenance

    from ssswet_core.public_media_evidence_pipeline import (
        parse_caption_transcript,
        bind_claim_candidates_to_source,
    )

    transcript = parse_caption_transcript(
        supplied_vtt_text,
        format_hint="vtt",
        language="ja",
    )
    binding = bind_claim_candidates_to_source(
        normalized_source_record,
        supplied_transcript_text,
        transcript_cues=transcript["cues"],
        language="ja",
    )

The cue offsets must address the exact same supplied text passed to the binder. Each claim remains an unverified candidate. A transcript hash and a claim hash identify the supplied text; neither proves authenticity, completeness or accuracy.

## Example: create a human-review packet

    from ssswet_core.public_media_evidence_pipeline import build_human_review_packet

    packet = build_human_review_packet(
        normalized_records,
        claim_bindings=claim_rows,
        transcript_cues=cue_rows,
        translation_reviews=translation_rows,
        language_audits=language_rows,
        publisher_status_ledger=publisher_ledger,
        review_queue=review_queue,
    )

The packet contains a deterministic manifest hash and byte count. Text detected by the privacy scanner is redacted in the export only; the caller's source records are not changed. Source snapshot hashes continue to identify the original normalized records. Packet-specific event hashes identify the privacy-redacted event representation, while the original ledger event and chain hashes remain separately visible.

## Baseline comparison

Baseline inspected before implementation: main 6d8291c420ad23b946e6553707d7638d32ac9e24; immediately preceding revision b8b600847e2871ea56300a30c7015a110e20986a.

| Area | Immediately before this extension | Added behavior |
|---|---|---|
| Feed intake | Normalized records could be supplied by an approved provider, but there was no parser for common public feed formats | RSS, Atom and JSON Feed are parsed locally into the existing normalized record shape |
| Provider contracts | Platform allowlists were enforced during normalization but not exposed as a preflight adapter report | Explicit schema-drift and sensitive-field report |
| Pagination | Intake budgeting existed, but there was no cursor continuity ledger | Hash-only cursor chain with page ordering, loop detection and external secure-store references |
| Language | Script profiling and multilingual cue matching existed; provider language could be wrong without a dedicated compatibility report | Declared-language/script consistency and Han-only Japanese/Chinese ambiguity |
| Headline review | Sensationalism cues were inspected without title/body context comparison | Additional transparent context and typography reason codes |
| Captions | Caption availability and supplied transcript readiness could be recorded, but no VTT/SRT parser supplied cue offsets | Timestamped cue records, code-point offsets and overlap flags |
| Claims | Candidate sentence spans existed without a stable binding to a normalized source snapshot and transcript cue set | Deterministic claim IDs tied to source snapshot hashes, offsets and cue references |
| Publisher status | Snapshot comparison reported field changes and absence; it did not maintain explicit publisher correction/retraction events | Append-only publisher-declared event history with hash-chain verification |
| Text privacy | Field-name screening flagged likely sensitive schema fields, but public free text was not scanned | Value-pattern screening with offsets and packet-only redaction preview |
| Human export | The workbench returned a batch manifest, records and review queue | Bounded, privacy-screened multi-artifact review packet with deterministic manifest and byte accounting |

## Reproducibility and limits

- All work is local and caller-driven. No platform API, browser, network, scraping, login, media download or private-content access is performed.
- Platform policy still governs how records are obtained. Use only official APIs, authorized public interfaces or feeds that are permitted for the intended use.
- The feed parser intentionally supports common RSS/Atom/JSON Feed structures, not every extension namespace, media enclosure, authenticated feed or malformed publisher dialect.
- Cursor hashes support audit and continuity checks but cannot resume a provider session without a separately secured cursor store. Do not put tokens in page IDs, references or item IDs.
- Script compatibility is not language identification. Japanese and Chinese share Han characters; Han-only text remains ambiguous for Japanese.
- Lexical and typography signals can misclassify neutral headlines. They are review prompts, not evidence of deception or scientific unreliability.
- VTT/SRT timing and text are only as trustworthy as the caller-supplied transcript. Overlap is retained as a warning rather than silently resolved.
- Claim offsets are Unicode code-point offsets into the exact supplied text. Editing, normalization or translation after extraction invalidates offsets and requires a new binding.
- Publisher status events require an explicit publisher declaration and reference URL. The ledger records an assertion; it does not independently verify the publisher or decide whether a paper's scientific conclusions are invalid.
- Privacy scanning is incomplete and can produce false positives. A clean scan is not proof that data are anonymous. Review exports omit author display names and strip URL query strings, but human review is still required before sharing.
- SHA-256 hashes provide deterministic integrity identifiers, not signatures, authenticity or non-repudiation. Retain trusted ledger heads separately if tamper evidence must survive repository or storage compromise.
- No utility establishes scientific validity, source independence, clinical or engineering safety, human-subject compliance, or operational rescue readiness.

## Tests and benchmark

From the repository root:

    python -m py_compile core/ssswet_core/public_media_evidence_pipeline.py
    cd core
    python -m pytest -q tests/test_public_media_evidence_pipeline.py
    cd ..
    python .github/scripts/benchmark_public_media_evidence_pipeline.py

The CI benchmark runs three samples per workload, reports median and maximum latency, and enforces a five-second maximum per workload. It also reports feed acceptance, cursor-chain validity, claim/source coverage, publisher-ledger validity, privacy findings and serialized packet growth at 125 versus 250 records. These are synthetic fixture measurements, not production latency, real-world retrieval accuracy or model-intelligence evaluations.
