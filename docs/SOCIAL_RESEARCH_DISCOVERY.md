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

Automated triage currently flags a limited set of observable English- and French-language review signals, including sensational wording, extraordinary absolute claims, unsupported certainty language, missing source references, promotional context, reposts and missing author/language metadata. It is a keyword heuristic, not a multilingual misinformation classifier.

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


## Expanded global discovery

The provider registry now includes additional sources, always retaining the platform-specific scope and access limits:

| Source | Access mode | Important limits |
|---|---|---|
| Bluesky | Public AT Protocol AppView search | Public posts only; results remain discovery leads |
| Public web / forums | Optional Brave Search API | Searches indexed public pages across community sites and forums; snippets are discovery leads, not source text verification |
| Reddit | OAuth API search | Requires an approved Reddit API app/token and a descriptive user agent; respect rate limits and Reddit terms |
| Threads | Official Meta Threads keyword-search endpoint | Requires `threads_keyword_search`; public search may be restricted until Meta grants advanced access |
| Facebook | Official Graph API posts for explicitly configured Page IDs | Public Page fields only; Page Public Content Access/app review or other Meta permissions may be required |
| Instagram | Existing Graph API Business Discovery adapter | Configured public professional accounts only; not unrestricted Instagram search |
| Qiita | Official Qiita API v2 | Japanese technical articles; public rate limits apply; optional access token |
| Community/forum feeds | Operator-configured HTTPS RSS/Atom URLs | Public feeds only; HTTPS required, private-network destinations and redirects rejected, response size bounded |
| Regional/community feeds | Same RSS/Atom adapter, with platform provenance inferred for configured domains | Can include public feeds from Bilibili, Niconico, Zenn, note, Weibo, Zhihu, MeWe, Snapchat and independent forums when a lawful public RSS/Atom feed is available |

The RSS adapter is a generic open-web connector for publicly published feeds; it does not imply that every named service itself offers an official RSS endpoint. MeWe and Snapchat do not currently have a generally available unrestricted public research-search API in this integration. Their content is included only if an operator supplies an accessible public feed or a future officially approved API connector. The same rule applies to Chinese and Japanese services without a stable, documented public API. Qiita and Bluesky have direct adapters; other regional services can be added as official access becomes available.

### Additional environment settings

- `SSSWET_BRAVE_SEARCH_API_KEY` (optional; broad public-web/forum discovery)
- `SSSWET_REDDIT_ACCESS_TOKEN`
- `SSSWET_REDDIT_USER_AGENT` (required when Reddit is enabled)
- `SSSWET_THREADS_ACCESS_TOKEN` (must carry the approved `threads_keyword_search` scope for public search)
- `SSSWET_FACEBOOK_ACCESS_TOKEN`
- `SSSWET_FACEBOOK_PAGE_IDS` (comma-separated numeric public Page IDs; only these Pages are queried)
- `SSSWET_QIITA_ACCESS_TOKEN` (optional)
- `SSSWET_PUBLIC_FEEDS` (one operator-approved public HTTPS RSS/Atom URL per line)
- `SSSWET_DEEPL_AUTH_KEY` (optional; translation disabled if absent)
- `SSSWET_TRANSLATION_TARGET_LANG` (defaults to EN)
- `SSSWET_DEEPL_API_URL` (must be the official free or paid DeepL API endpoint)

Bluesky public search and Qiita public search are available without an access token. The optional Brave Search adapter can discover indexed public pages across additional community sites and forums; it does not see private or unindexed content. The configured source list is bounded, queried concurrently with a maximum of eight workers, and globally deduplicated. The ten-record research-pass cap is selected by round-robin across platforms so a high-volume source cannot monopolize the entire result set. Individual platform errors do not suppress successful sources.

### Multilingual clickbait and translation

The heuristic phrase library currently covers English, French, Spanish, Portuguese, German, Italian, Dutch, Russian, Arabic, Hindi, Turkish, Indonesian, Japanese, Simplified/Traditional Chinese phrase forms, and Korean. These are language-specific review signals, not a calibrated multilingual classifier. Script detection is only a hint; platform-provided language metadata is preferred. Short posts, slang, sarcasm, dialects, code-switching, memes, and adversarially altered text can evade detection or trigger false positives. An unflagged post is not considered trustworthy.

Optional DeepL translation stores the translation beside the untouched original title/text, records detected source and target language, and marks translation as not fact verification. Translation is attempted only when an API key is configured; failures preserve the original content. Reviewers should compare important technical terms, units, numbers, negations, names, and quoted passages against the original-language source before relying on a translation. Translation never changes the verification status.

### Additional regression and acceptance criteria

1. Public adapters return stable source IDs and canonical HTTPS links with author, timestamp and language metadata where the source exposes them.
2. Reddit, Threads and Facebook require explicit credentials; Meta page search is restricted to configured Page IDs.
3. Bluesky and Qiita are added without making existing scholarly providers or platform adapters mandatory.
4. Public RSS/Atom feeds are HTTPS-only, size-bounded, redirect-disabled and rejected when DNS resolves to non-public IP addresses.
5. Social source retrieval uses no more than eight concurrent workers and remains bounded by the existing ten-record research-pass cap.
6. The original language text remains unchanged when a translation is attached; translation failure cannot discard the source.
7. At least 15 language/script families have deterministic clickbait review fixtures; all triage outputs remain `not_verified`.
8. No automated language heuristic or translation is allowed to mark a claim true, false, confirmed or disproven.
9. Missing credentials, unavailable platform APIs and unsupported platforms do not trigger scraping, login automation or fabricated results.
10. Existing YouTube, X, Instagram, Crossref, OpenAlex, daemon and CLI behaviours remain available.

Live platform quotas, Meta app-review status, Reddit approval, DeepL billing/limits and regional feed availability must be validated with the operator's own credentials. The unit suite uses mocked responses and does not establish live platform availability or real-world misinformation-classification accuracy.

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

## GitHub Actions live smoke checks

The repository includes `.github/workflows/social-live-smoke.yml`. It runs on:
- pushes to the social-discovery feature branch;
- pull requests (read-only public API calls only);
- a daily schedule;
- manual `workflow_dispatch`.

The workflow tests four fixed research queries (English, French, Japanese and Chinese) against public Bluesky search and the official Qiita API. It does not require API secrets, does not write to the repository, and does not access private accounts. It uploads a seven-day artifact named `social-live-smoke-report` containing bounded public metadata, URLs, counts, language hints and request status; it does not retain full post/article bodies.

A zero-result query is valid and is not treated as an outage. Individual provider errors are recorded in the report; the workflow fails only if every request fails. A successful response confirms endpoint reachability and response parsing only, not scientific accuracy, completeness, or the quality of a claim. GitHub Actions is a suitable lightweight validation runner, but it is not a continuously running SSSWET research daemon or a permanent database.

To run it manually: open **Actions → Social research live smoke test → Run workflow**, select the feature branch, and start the run. Download the `social-live-smoke-report` artifact from the completed run.

Credentials for optional Brave, Reddit, Threads, Facebook and DeepL integrations must be added separately as repository Actions secrets only after the corresponding provider account/app has been approved. Do not place credentials in workflow YAML, source files, issues, logs or artifacts. The current smoke workflow deliberately does not print or consume those secrets.

