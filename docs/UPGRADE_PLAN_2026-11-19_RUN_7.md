# Upgrade plan — 19 November 2026, run 7

## Baseline inspected before implementation

- Current `main`: `7a506a0342c50d39c1cea209ac3ab822b192cac6`.
- Immediate predecessor: `9ca993d4865efc9334e8ac46583c1ec2ef992e9f`.
- Current commit changes the application release workflow to pinned Node 24 actions, limits workflow-level permissions to read, and scopes release write permission to tag publishing.
- Immediate predecessor expands the static accessibility gate to include `admin.html` and adds page-coverage tests.
- Existing mainline had Crossref/OpenAlex/arXiv/Europe PMC scholarly providers, a demo-default local CLI, and a scholarly-only continuous daemon. No social provider modules or social CLI mode were present.
- Existing research evidence, memory, provenance, public-media and accessibility systems were retained.
- Existing PR #29 contained a social-discovery proposal but was 83 commits ahead / 38 behind main and reported non-mergeable. It was inspected as a source of implementation material; its stale branch was not merged.

## Exactly ten acceptance-scoped improvements

1. Official YouTube Data API v3 public-video metadata discovery; no video downloads or transcript-permission bypass.
2. X API v2 recent public-post discovery; entitlement/rate-limit errors remain visible.
3. Instagram Graph API Business Discovery limited to explicitly configured public professional accounts.
4. Bluesky public AT Protocol search with stable post URI provenance.
5. Reddit OAuth search with explicit token and descriptive user-agent requirements.
6. Threads keyword search through the official endpoint, with approved scope requirement documented.
7. Facebook public Page posts restricted to explicitly configured numeric Page IDs.
8. Regional and public-web discovery through Qiita, optional Brave Search and operator-configured public RSS/Atom feeds; MeWe/Snapchat are feed-only when a lawful public feed exists.
9. Multilingual review triage across 15 language/script families, CJK-aware lexical relevance, bounded provider concurrency/deduplication/diversity, and optional translation that preserves originals.
10. Bibliographic integrity review in the evidence-quality matrix: DOI and exact-title/year duplicate candidates, correction/retraction/preprint metadata signals, missing-field warnings, and no automatic deduplication or truth verdict.

## Measurable acceptance criteria

- Provider registry remains capped at 20; at most 8 concurrent workers; result cap remains 10; duplicate source IDs are removed; round-robin keeps one platform from monopolizing results.
- Existing scholarly providers and demo-default CLI remain unchanged unless a user selects `social`/`combined` or sets `SSSWET_ENABLE_SOCIAL_DISCOVERY=1`.
- No social item is promoted beyond `not_verified`; engagement/popularity never affects scientific validity.
- Credentialed adapters require environment configuration; credentials are never serialized into records or smoke artifacts.
- RSS/Atom is HTTPS-only, port 443, redirects disabled, environment proxies disabled, DNS answers all globally routable, validated IPs pinned to the TLS-verified hostname, response capped at 2 MiB, and no more than 20 configured feeds.
- DeepL is restricted to official endpoints, uses pinned public IPs with TLS hostname verification, disables redirects/proxies, caps response size and preserves the original item on failure.
- Bibliographic audit accepts at most 2,000 source records, detects DOI/exact-title-year candidates, flags status/missing metadata, never deletes sources and never asserts scientific validity.
- Public multilingual smoke checks treat zero results as a valid response but fail on provider request errors; artifacts retain only bounded metadata for seven days.
- All new modules compile and all tests pass on Python 3.11, 3.12 and 3.13.

## Regression risks and controls

- Provider schema drift / API quotas: adapter-level error isolation, fixed endpoints, timeouts, byte caps and separate live smoke workflow.
- SSRF / DNS rebinding: exact HTTPS restrictions, no redirects or proxies, global-IP validation and IP pinning for operator-configured feeds and DeepL.
- Credential leakage: environment-only credentials, authorization headers, no raw token serialization, no secrets in scheduled smoke.
- False positives/negatives in multilingual heuristics: outputs are review flags only; no truth labels or calibrated accuracy claims.
- Platform access limits: Instagram, Reddit, Threads, Facebook and X remain entitlement-dependent; missing access never triggers scraping.
- CLI/daemon regression: default provider remains demo for CLI and scholarly-only for daemon; social daemon use is explicitly opt-in.
- Evidence regression: social posts remain contextual discovery leads; original language text is preserved; bibliographic duplicates are review candidates only.
- Storage/performance: result, feed, response and report bounds are explicit; synthetic benchmarks and live smoke are separate from production claims.

## Verification plan

Run the full existing Python matrix, core tests, web/accessibility/localization checks and all existing research benchmarks. Add focused adapter, security, provenance, integration and bibliographic tests. Run the separate read-only live smoke workflow without credentials and inspect its bounded artifact. No payment, tax, refund, customer-data, credential, legal-policy or commercial-promise settings are in scope.


## Benchmark acceptance budgets

The deterministic synthetic benchmark enforces p95 ceilings of 500 ms for 250-item query relevance, 500 ms for 250-item multilingual triage and 1,000 ms for a 500-record bibliographic audit. These budgets are CI guardrails, not production service-level objectives.
