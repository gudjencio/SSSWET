# Social and video research discovery

## Purpose

SSSWET can use public videos and social posts as discovery and context leads alongside scholarly indexes. The first adapter set uses official platform APIs only. A platform result is not a scientific source-quality verdict and never changes a claim's verification state.

## Supported platform access

| Platform | Adapter | Coverage and limits |
|---|---|---|
| YouTube | YouTube Data API v3 search | Public video metadata, title, description, channel and publication date. No video downloading, transcript scraping or caption-permission bypass. |
| X | X API v2 recent search | Public recent posts and available author/post metadata. Availability depends on the account's current API entitlement and rate limits. |
| Instagram | Instagram Graph API Business Discovery | Only explicitly configured public professional accounts. Instagram does not provide unrestricted public-post search through this API; no scraping fallback is used. |

## Configuration

Set credentials in the local process environment or secret manager. Never commit credentials, put them in public workflow logs, or expose them to browser JavaScript.

- SSSWET_YOUTUBE_API_KEY
- SSSWET_X_BEARER_TOKEN
- SSSWET_INSTAGRAM_ACCESS_TOKEN
- SSSWET_INSTAGRAM_USER_ID (the connected professional Instagram account ID)
- SSSWET_INSTAGRAM_BUSINESS_ACCOUNTS (comma-separated allowlist of public professional usernames)

Use only credentials issued to an application you control and only within the platform's current terms, scopes, quotas and retention rules. Missing credentials disable that adapter without breaking scholarly search.

## CLI

Run from core/:

    python -m ssswet_core.research_cli --provider combined --objective "battery thermal management experimental results"

The continuous research daemon now combines scholarly discovery with social discovery whenever the corresponding official API credentials are configured. Missing social credentials leave the existing scholarly search active. For a one-off social-only pass, use --provider social. The provider can also be constructed programmatically:

    from ssswet_core.social_research import SocialResearchProvider
    provider = SocialResearchProvider.from_environment()
    result = provider.investigate("battery thermal management", "initial")

When configured, available platform adapters are queried concurrently with a maximum of three workers. Results are deduplicated by stable platform source ID and capped at ten. Request timeouts and response-size limits are enforced.

## Misinformation and clickbait handling

Automated triage only flags observable review signals, including sensational wording, extraordinary absolute claims, unsupported certainty language, missing source references, promotional context, reposts and missing author/language metadata.

It does not label a post as true, false, fake news or misinformation. It does not infer expertise from follower counts, popularity or verification badges. A high engagement count never increases scientific credibility.

The claim-review packet links a manually supplied claim to relevant posts and identifies whether similar material appears on more than one platform. Cross-platform recurrence is not independent corroboration: posts can copy one another or share the same original source.

A human reviewer should locate primary research, inspect methods and limitations, check dates, seek independent replication and contradictory evidence, and record the outcome through SSSWET's existing review workflows. Automated triage never promotes a claim to verified.

## Evidence and privacy boundaries

- Search results are public metadata only; private accounts, private messages and restricted content are not accessed.
- No browser automation, credential harvesting, scraping, paywall bypass or transcript circumvention is used.
- Video transcripts are not fetched. YouTube search metadata is not a substitute for viewing the experiment or reading its paper.
- The provider does not persist raw posts or media. The existing research pipeline may retain bounded evidence summaries and source IDs according to its configured store; review retention obligations before enabling persistence.
- API credentials remain in environment variables and are not serialized into evidence records.
- API errors and unavailable entitlements are reported; no fabricated fallback results are generated.

## Acceptance criteria and regression comparison

The previous default CLI offered demo, scholarly metadata and local-corpus providers; it had no first-party social/video adapters. This change adds an opt-in social provider without changing the default demo provider or existing scholarly choices.

Acceptance criteria:
1. Official API adapters preserve stable URLs, platform IDs, timestamps and author/channel provenance.
2. YouTube and X searches are bounded to at most ten returned records per provider.
3. Instagram access is restricted to an explicit allowlist of public professional accounts.
4. All social results remain not_verified; engagement metrics never promote them.
5. Clickbait and source-absence heuristics create review flags, never truth labels.
6. Similar claims across platforms are explicitly not treated as confirmation.
7. Missing credentials and one-platform failures do not crash other configured providers.
8. No runtime dependency, database migration, scraping fallback or default provider change is introduced.

Regression risks include API quota exhaustion, schema drift, rate limits, stale content, platform policy changes and false positives/negatives in text heuristics. These are surfaced as provider errors or review flags, not silently hidden. API access and real-world classification quality require separate live integration evaluation; deterministic unit tests do not establish misinformation-detection accuracy.
