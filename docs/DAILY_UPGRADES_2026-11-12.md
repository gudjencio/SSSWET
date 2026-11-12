# Research continuity and evidence workflow upgrades — 12 November 2026

## Pre-implementation inspection

The implementation was planned against public main at 8c0bc15409af58453a5ecdcaef3f226a37f03c3e, with immediate predecessor 0a932a960ab49bfbd5281a728bad516bf0232a0b. The Git comparison showed one intervening commit: the public-read/browser-write origin separation and its HTTP regression tests. The preceding commit already contained temporal event-identity validation and scheduled temporal/GPS regression coverage.

The inspected baseline already had append-only scientific-memory versions, a knowledge graph with explicit supports and contradicts edges, source provenance records, Crossref/OpenAlex metadata discovery, literature-watch history, dataset governance metadata, and reproducibility manifests. The gaps addressed here were narrower and measurable:

- the legacy memory-lineage endpoint materialized a complete lineage instead of offering SQL-bounded pages;
- agents had no single bounded context pack that retained linked counterevidence and source IDs together;
- review signals existed in separate APIs but were not consolidated into a deterministic queue;
- graph retrieval was global rather than a bounded neighbourhood around selected claims;
- literature-watch runs were stored but had no explicit run-to-run change report;
- the existing broad provider covered Crossref and OpenAlex, but not arXiv and Europe PMC, and did not retain conflicting provider observations in a structured candidate;
- dataset governance flags were reportable but were not a gate when constructing a reproducibility manifest.

## Acceptance criteria defined before implementation

| # | Improvement | Measurable acceptance criteria |
|---|---|---|
| 1 | Temporal event identity and scheduled regression integrity | Duplicate IDs within the aligned session/source are rejected; reuse in another session/source remains representable; both scheduled regression workflows retain temporal/GPS checks. |
| 2 | Separate browser read and write origins | Google Sites can read public endpoints but cannot submit browser writes; only the dedicated GitHub Pages origin is accepted for public report submission; local CLI writes remain supported. |
| 3 | Reduced-motion support in Virtual Time Travel Mapping | CSS motion is reduced and every MapLibre camera transition used by selection, geolocation, live follow and trajectory bounds becomes non-animated when the browser preference is enabled. |
| 4 | Bounded agent research context packs | Default pack is capped at 16,000 characters; includes selected memory versions, source identifiers and linked contradiction edges; deterministic digest; no verification-state changes. |
| 5 | Consolidated human-review queue | At most 500 returned items; deterministic ordering and reason codes; contested memory and withdrawn/pending dataset governance signals are surfaced; no automatic task or status changes. |
| 6 | Bounded knowledge-graph neighbourhood retrieval | Depth at most 3, 200 nodes and 500 edges; contradiction edges are ordered first; missing seeds and truncation are explicit. |
| 7 | Paginated scientific-memory lineage | SQL query returns at most limit + 1 rows; public page limit at most 100; consecutive pages do not overlap; the existing full-lineage endpoint remains unchanged. |
| 8 | Literature-watch run comparison | At most 200 candidates per report; strong DOI/arXiv/URL identities; reports added, absent and metadata-changed candidates; absence is never labelled retraction. |
| 9 | Expanded scholarly discovery with provenance reconciliation | Four official metadata sources (Crossref, OpenAlex, arXiv and Europe PMC); each provider capped at 20 results and 30 seconds; arXiv and Europe PMC requests are restricted to fixed HTTPS host allowlists, redirects are followed only when they remain HTTPS on the exact provider host, responses are capped at 2 MB, and arXiv DTD/entity declarations are rejected; duplicate identities are grouped while every provider observation and detected title/year/DOI conflict is retained. |
| 10 | Dataset-governed reproducibility manifests | Public manifests require an explicit public privacy classification, a recorded consent basis, public access scope, known licence and dataset content digest; personal/sensitive datasets require a traceable consent-basis reference for non-public project manifests. Withdrawn consent, tampered dataset records and unapproved personal/sensitive data block manifest creation; valid manifests pass digest verification. |

## Regression risks identified and controls

- **Compatibility:** new context, queue, graph, diff, governance and paginated-lineage routes are additive. The existing lineage route and existing Crossref/OpenAlex MultiSourceLiteratureProvider remain available.
- **Retrieval truncation:** every new bounded API reports omitted or truncated records rather than silently implying completeness.
- **Contradiction loss:** context packs include graph contradiction links for selected memories; graph neighbourhood traversal sorts contradicts edges before other relations.
- **Source over-merging:** strong identifiers are used; title similarity is not used as proof of identity. Provider observations are retained rather than choosing a winning metadata record.
- **Network and resource exposure:** new providers use fixed HTTPS endpoints, capped result counts, bounded timeouts and response-size limits. They are opt-in; existing provider defaults are not expanded silently.
- **Privacy and ethics:** dataset governance gates do not grant consent or legal approval. Personal/sensitive data with missing or withdrawn consent cannot be included in a generated manifest for public use.
- **Scientific interpretation:** no new workflow automatically verifies a claim, adjudicates a contradiction, certifies an equipment design, or treats a metadata count as evidence quality.

## Completed implementation

1. Temporal event IDs are normalized and unique within the exact session/source being aligned. Scheduled 30-minute and hourly workflows now exercise temporal and GPS checks.
2. Public read origins and browser write origins are separate. Shared Google Sites origins remain read-only by default; dedicated GitHub Pages report submission and local CLI compatibility are tested.
3. Virtual Time Travel Mapping now honours prefers-reduced-motion for CSS and all four MapLibre camera paths.
4. research_context_pack.py builds a deterministic, character-bounded agent context with memory versions, linked contradictions, source identifiers, missing-link flags and a SHA-256 digest.
5. research_review_queue.py consolidates contested memory, missing links, literature candidates/provider conflicts and dataset-governance flags into a deterministic human-review queue.
6. knowledge_graph_neighborhood.py provides bounded breadth-first graph retrieval with contradiction-first edge ordering.
7. ScientificMemoryService.lineage_page() and SQLiteResearchStore.scientific_memory_history_page_for_key() provide SQL-bounded predecessor pages without changing the legacy endpoint.
8. literature_watch_diff.py compares saved watch reports and explicitly distinguishes disappearance from retraction and metadata change from correction.
9. ArxivProvider, EuropePMCProvider and opt-in BroadScholarlyLiteratureProvider extend scholarly discovery. The new endpoints enforce fixed HTTPS host allowlists, bounded query lengths, 2 MB response caps, and DTD/entity rejection for arXiv. ProviderResult and literature-watch candidates retain per-provider observations and metadata conflict fields.
10. governed_reproducibility.py blocks manifest creation when recorded dataset governance is insufficient for the requested scope and keeps governance-gate metadata inside the manifest digest.

## Local administrator API additions

- GET /api/research-context?q=...&limit=20&max_chars=16000
- GET /api/research-review-queue?limit=100
- GET /api/knowledge-graph/neighborhood?node_ids=id1,id2&depth=2&max_nodes=100&max_edges=200
- GET /api/scientific-memory/lineage-page?version_id=...&limit=50&before_version_number=...
- GET /api/literature-watch/diff?older_watch_id=...&newer_watch_id=...
- GET /api/dataset-governance-gate?dataset_id=...&version=1&scope=public

These six research endpoints are restricted to loopback requests with the configured local administrator token. They are not unauthenticated public website APIs. The governance-gate endpoint returns eligibility and issue codes only; it does not expose raw dataset contents or create a stored experiment.

## Validation and limitations

The regression suite is in core/tests/test_research_continuity_features.py. It covers deterministic hashes, character and graph limits, contradiction retention, review priorities, watch diffs, governance blocks, provider parsing/size safeguards, metadata conflicts, paginated lineage and HTTP endpoint behaviour.

Synthetic provider fixtures validate parsing and reconciliation logic; they do not establish current upstream API availability. Provider discovery returns bibliographic metadata only, not full-text access or claim verification. The four-index provider is opt-in: instantiate BroadScholarlyLiteratureProvider and pass it to LiteratureWatchService rather than changing the existing two-index default. For example:

```python
provider = BroadScholarlyLiteratureProvider(max_results=5)
watch = LiteratureWatchService(provider, store)
report = watch.run("wave propagation")
```

The context pack's character budget is a deterministic size bound, not a model-token guarantee. A synthetic one-query retrieval evaluation checks recall, provenance-group recall, contradiction retention, measured latency and SQLite file size; it is a regression fixture, not a representative production benchmark. Review priorities are workflow cues, not scientific truth rankings. The legacy full-lineage endpoint remains for compatibility; consumers handling long histories should use the new paginated endpoint.

No payment, tax, refund, customer-data, credential, legal-policy or commercial-promise settings are changed.

## Post-validation hardening

A follow-up review identified that validating a response URL after urllib returns is not sufficient to prevent urllib from first following a redirect. The arXiv and Europe PMC adapters now validate each proposed redirect target before following it and allow only HTTPS redirects to the exact provider host, validate the fixed HTTPS request host before opening it, and still validate the returned response URL. Regression tests cover off-host, insecure same-host and permitted HTTPS same-host redirects. All six extended research-read routes now require the existing loopback-only local administrator check and token; unauthenticated requests return HTTP 401 before accessing the research store. The dataset-governed manifest gate now rejects malformed content-digest strings unless they are exactly 64 hexadecimal characters; this is a format and registry-integrity gate only and cannot recompute the digest without the dataset bytes. Literature-watch comparison also normalizes arXiv version suffixes so v1 and v3 observations are compared as revisions of the same preprint rather than unrelated additions and disappearances.