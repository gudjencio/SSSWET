# Public-media evidence pipeline expansion — 14 November 2026

## Baseline inspected before implementation

- Current main: `6d8291c420ad23b946e6553707d7638d32ac9e24` (bounded multilingual public-media workbench).
- Immediately preceding main revision: `b8b600847e2871ea56300a30c7015a110e20986a` (independent VTT local-frame holdout validation).
- The one-commit comparison from the preceding revision to current main adds the public-media workbench, its tests, its benchmark and CI wiring. The prior revision did not contain that workbench.
- Existing APIs inspected: `public_media_ingestion.py`, `public_media_research_workbench.py`, `multilingual_research_triage.py`, `translation_fidelity.py`, `privacy_minimization.py`, `review_assignment.py`, `source_independence.py`, and the current CI workflow.
- Compatibility baseline: existing normalization, triage, translation review, review queue, snapshot comparison and audit-chain APIs remain unchanged. This batch will add a separate opt-in extension module.

## Proposed ten improvements and measurable acceptance criteria

1. **Safe public-feed import** — parse RSS 2.0, Atom 1.0 and JSON Feed 1.1 from caller-supplied bytes only; accept at most 2 MiB and 250 entries; reject DTD/entity declarations, malformed XML/JSON and non-HTTPS item links; preserve feed/entry identifiers and timestamps without fetching anything.
   - Acceptance: fixtures for all three formats; malformed, oversized, entity-bearing and missing-link inputs rejected; source order and entry count deterministic.
2. **Adapter schema-drift audit** — validate provider adapter declarations against the existing platform access-mode and field allowlists; report required/optional/missing/unexpected fields before normalization.
   - Acceptance: every existing platform has a deterministic contract; unexpected sensitive fields are flagged, not copied; unknown platforms and unapproved access modes fail closed.
3. **Privacy-bounded pagination checkpoints** — create resumable page checkpoints using sequence numbers, opaque-cursor hashes and prior-checkpoint hashes; never persist raw cursors or credentials; cap history at 500 pages.
   - Acceptance: valid monotonic chains verify; repeated cursor digests, sequence gaps, tampering, duplicate IDs and capacity overflow are detected; raw cursor/token strings are absent from exports.
4. **Language/script consistency audit** — compare an explicitly declared/provider-supplied language with Unicode script composition; distinguish script compatibility from actual language identification.
   - Acceptance: deterministic cases for Latin, Cyrillic, Arabic, Hebrew, Devanagari, Bengali, Thai, Hangul, Japanese kana and Han-only ambiguity; no language is auto-assigned when evidence is insufficient.
5. **Multilingual headline/context sensationalism audit** — combine existing configured language cues with transparent title/body contrast, typography and certainty-signal features.
   - Acceptance: controlled multilingual fixtures identify configured signals; neutral counterexamples avoid escalation; every output exposes reason codes and says that clickbait, intent and truth are not adjudicated.
6. **Time-coded transcript segmentation** — parse caller-supplied WebVTT and SRT text, validate timestamps and cue order, and preserve cue IDs and offsets.
   - Acceptance: valid VTT/SRT fixtures retain exact text and millisecond timing; malformed, overlapping, reversed, overlong and oversized cues are rejected or explicitly flagged; no transcript is fetched.
7. **Claim-to-source provenance binding** — bind existing sentence candidates to source snapshot hashes, transcript cue IDs, language and code-point offsets; preserve original and translated text references separately.
   - Acceptance: deterministic claim IDs; every claim resolves to an existing source and optional cue; offsets round-trip to the exact source substring; translation never replaces original evidence.
8. **Publisher correction/retraction event ledger** — record explicit publisher-declared correction, retraction, update, removal and restoration events as a bounded append-only hash chain.
   - Acceptance: event order and prior hashes verify; source versions remain visible; missing/withdrawn records are not silently deleted; no status is inferred from disappearance.
9. **Public-text privacy screening and redaction preview** — detect common direct identifiers, credentials, IP/coordinate patterns and contact details in supplied text; return offset-based findings and an optional redacted preview.
   - Acceptance: multilingual text fixtures retain code-point offsets; secrets and matched values are not echoed in findings; scanner never mutates input or stores a redacted replacement automatically; false-positive limitations are explicit.
10. **Deterministic human-review packet** — assemble bounded source snapshots, claim bindings, transcript cues, language/translation audits, correction events, privacy findings, omissions and a manifest digest into an exportable JSON packet.
    - Acceptance: byte-identical canonical output for identical inputs; all source and claim references resolve; contradictions/unknown states are retained; 500-record/5 MiB limits enforced; no media bytes or private credentials included.

## Cross-cutting acceptance and regression criteria

- New code uses only the Python standard library and existing SSSWET modules.
- No network requests, scraping, authentication, media downloads, platform-policy bypass, automated scientific adjudication or reviewer contact.
- Existing public-media APIs remain unchanged and are tested by the complete core suite.
- Every new feature receives direct positive, negative, boundary and tamper tests.
- A deterministic synthetic benchmark reports workload size, median and maximum latency, source/claim retention, packet byte growth and parser/claim reference integrity. The CI per-workload ceiling is 5 seconds; synthetic measurements are not production or intelligence claims.
- Public documentation describes use, prior behavior, limitations and privacy/safety boundaries.
- Any regression, missing CI result or unverified deployment is reported rather than described as complete.
