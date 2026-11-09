# Virtual Time Travel observation analysis workbench

The public Virtual Time Travel Mapping page exports a local JSON observation index. The companion [Observation Analysis Workbench](../web/observation-workbench.html) accepts that export and performs bounded analysis entirely in the browser. It does not upload the selected file, access the mapping page's IndexedDB, or include recorded media.

## Ten independently useful capabilities

1. **Versioned import validation.** Accepts \`ssswet-virtual-time-map-index-v1\`, checks record identifiers, kinds, timestamps, coordinates, session identifiers and numeric metadata, and enforces 20 MiB, 50,000-record, 64-level nesting and one-million-node structural limits. Unknown future event kinds and unknown fields are retained with a warning rather than silently discarded.
2. **Provenance and clock audit.** Counts clock metadata retention, wall-clock divergence and within-session timestamp/monotonic regressions. Legacy records remain in a separate legacy group. Cross-session chronology is never inferred.
3. **GPS quality screening.** Flags missing or weak accuracy, non-increasing timestamps, sampling gaps over 15 minutes, jumps over 5 km and implied speeds over 70 m/s. Flags are review leads; they never delete observations.
4. **Session-isolated route metrics.** Calculates geodesic distance, duration, average and maximum observed segment speed, and accepted/excluded segment counts separately for each capture session. Segments touching a fix with reported accuracy worse than 150 m or missing coordinates are excluded from route totals; the route is not bridged across an unusable fix. Missing accuracy remains visible and is not treated as zero.
5. **Temporal coverage diagnostics.** Reports per-session sample count, span, median and p95 GPS sampling intervals, gap count and longest gap. A gap is not evidence that no event occurred.
6. **Non-destructive duplicate candidates.** Groups exact payload matches (ignoring record ID) and screens same-session GPS fixes within 1 second and 5 metres. The scan is capped at 250,000 pair comparisons and 2,000 results by default; truncation is reported. Nothing is merged or removed.
7. **Session comparison summaries.** Compares record counts, event-kind counts, GPS counts, per-session time spans and median reported GPS accuracy without sorting or combining sessions into a global timeline.
8. **Privacy transformations.** Creates a separate copy with configurable coordinate rounding (0–6 decimals), time coarsening (exact/minute/hour/day), optional removal of the event description field, detailed sensor values and clock diagnostics, optional session-ID removal, and optional sequential record-ID pseudonyms. The imported object is never mutated.
9. **Interoperable exports.** Produces privacy-adjusted JSON, CSV and RFC 7946-style GeoJSON. GeoJSON coordinates use \`[longitude, latitude]\`; only GPS and geolocated annotation records become point features. CSV text cells are escaped and formula-prefixed strings are neutralized.
10. **Integrity manifests.** Creates and verifies a deterministic SHA-256 manifest over the export format identifier and ordered observation records using sorted-key JSON canonicalization. This detects payload changes; it is not a digital signature, author identity check or source authentication.

## Use

1. Open [Virtual Time Travel Mapping](../web/virtual-time-travel.html).
2. Export the observation index from the data and privacy panel.
3. Open the workbench and select the downloaded JSON file.
4. Review validation, provenance, GPS quality, route, temporal coverage and duplicate reports.
5. Choose privacy settings before exporting a shareable copy. The defaults round coordinates to three decimals, round timestamps to minutes, omit descriptions and detailed sensor values, omit clock diagnostics and session identifiers, and pseudonymize record IDs.
6. Keep the original export separately if you need exact source timestamps or coordinates.

The browser's Web Crypto API is required for SHA-256 manifests; use the GitHub Pages HTTPS site or localhost. The workbench supports English and French. Other browser languages currently use English fallback; this is not a claim of complete translation.

## Baseline and non-regression review

Inspected before implementation:

- \`main\` at \`2f4399caf3d8dc951fe3c124d5be5c841f2d1add\`.
- Its immediate predecessor at \`448d42088998aac95a992f5457e5b1c70b69daf9\`.
- The one-commit mainline difference only tightens the GPS scenario test around selected-session filtering and export-ordering assertions. The mapping application already provides local IndexedDB capture, session-isolated playback, GPS scenario estimates and a v1 observation-index export.
- The adjacent temporal-clock regression proposal was also inspected; its cache assertion was version-coupled to v193 while the service worker declared v194. The workbench branch includes the version-agnostic test correction and scheduled test coverage so the new work does not build on a known stale assertion.

Previous behaviour had no dedicated import/analysis workbench: users could export the v1 index but had no built-in validator, session quality report, duplicate triage, privacy-adjusted interchange formats or record integrity manifest. The existing capture and export format remains unchanged.

## Measurable acceptance criteria

- A valid v1 fixture passes; unsupported formats, duplicate IDs, invalid coordinates/timestamps, oversized files, more than 50,000 observations and over-deep/over-large structures are rejected with explicit errors.
- Unknown event kinds and unknown metadata remain present and produce warnings rather than destructive migration.
- Two overlapping sessions remain separate in provenance, route and coverage results; no cross-session distance or chronology is calculated.
- Known synthetic GPS gaps, poor-accuracy segments, jumps and speed outliers produce the expected flags; no record is removed.
- Duplicate candidate results are deterministic and remain within configured comparison/result caps; no destructive action is possible.
- Privacy transformation leaves the source object unchanged and rounds both epoch and clock metadata at the selected precision; session IDs can be retained independently from clock diagnostics.
- GeoJSON uses longitude/latitude order; CSV quoting and formula-injection safeguards are tested.
- Identical payloads produce the same manifest digest; any observation change invalidates it.
- The UI contains labelled file input, keyboard-visible focus, semantic tables and live status feedback. Static checks confirm no fetch/XHR/sendBeacon upload path.
- A five-trial Node.js benchmark analyzes 10,000 synthetic GPS observations across five sessions with p95 below a deliberately broad 5-second CI guard.

## Regression risks and safeguards

- The original mapping page's IndexedDB, capture permissions, timeline, map, media and export code are not changed.
- The v1 export format is read-only input. No schema migration or record rewrite occurs.
- Workbench file handling is local-only and size-bounded. It does not make network requests or upload records.
- Low-accuracy GPS segments are excluded from route totals but remain in the imported dataset and quality report.
- Duplicate detection is candidate-only, bounded and does not infer semantic equivalence.
- Privacy transformation preserves unknown custom metadata. Users must inspect unknown fields and \`exported_at\` before sharing; the tool cannot guarantee anonymity or remove every identifying detail.
- Coarsened coordinates and times are approximations. The reported coordinate decimal count is not a surveyed spatial error bound.
- Route distances and speeds are descriptive geodesic calculations, not survey-grade measurements or navigation instructions.
- SHA-256 manifests detect changes to the included format and observation payload, not malicious authorship or certificate authenticity.
- English/French UI coverage is partial; no full WCAG certification or professional translation is claimed.

## Local benchmark reference

A five-trial Node.js 22.16 synthetic run processed 10,000 GPS observations across five isolated sessions with a median of approximately 91 ms and p95 of approximately 107 ms in the local development container. CI records its own runner measurements; these figures are not browser field-performance guarantees.