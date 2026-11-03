# Research infrastructure upgrades

This release adds ten independently useful research-support features. They preserve the project's conservative evidence model: none of these utilities certifies scientific truth, replaces independent review, or enables unsafe operations.

## 1. Bounded fast coordination
`fast_coordination.py` provides deterministic priority-based assignment with an explicit latency budget. Acceptance: assignments are stable, only waiting agents are selected, and the measured scheduling pass reports whether its budget was met. Previous scheduling remains available through `ResearchOrchestrator.schedule()`.

## 2. Memory retrieval quality metrics
`memory_quality.py` adds validated-aware deduplication and retrieval-quality measurements. Acceptance: duplicate normalized statements collapse, validated evidence is preferred, and retrieval reports hit and validation rates. It does not infer truth from age or popularity.

## 3. Tamper-evident provenance chains
`provenance.py` adds SHA-256 content and chained provenance digests. Acceptance: intact chains validate and altered parent links are detected. This complements existing source references rather than replacing them.

## 4. Contradiction triage
`contradiction_triage.py` groups conflicts by subject/predicate and produces deterministic review priorities. Acceptance: related conflicts are clustered and all distinct values remain visible. It does not select a winning claim.

## 5. Evidence quality scoring
`evidence_quality.py` measures source quality, method transparency, reproducibility, independence and provenance completeness. Acceptance: complete maximum-quality evidence reaches 100%, while missing provenance forces review. Scores are advisory, not scientific certification.

## 6. Virtual Time Mapping
`virtual_time_mapping.py` provides an evidence-based temporal map with explicit uncertainty windows and source identifiers. Acceptance: observations can be filtered by uncertainty and missing provenance is rejected. The feature is a research mapping interface; it does not claim physical time travel.

## 7. Conservative rescue workflow planning
`rescue_workflow.py` provides an allowlist for remote sensing, communications relay, resource mapping, hazard assessment and evacuation support. Human approval remains mandatory where appropriate. Unknown or unsafe actions are rejected rather than silently executed.

## 8. Versioned research checkpoints
`research_checkpoint.py` preserves monotonic checkpoint versions with source references and unresolved questions. Acceptance: a task can resume from its latest checkpoint while retaining its complete local history.

## 9. Bounded retention and deduplication
`bounded_retention.py` provides configurable maximum storage and latest-per-key compaction. Acceptance: duplicate keys collapse and retained records never exceed the configured bound. This supports durable research continuity without unbounded memory growth.

## 10. Localization coverage auditing
`localization_quality.py` measures per-language translation coverage and reports missing keys. Acceptance: full catalogues report 100% coverage and incomplete catalogues expose exact missing keys. The audit deliberately does not claim that untranslated text has been successfully translated.

## Regression posture
The new tests cover normal operation, boundary conditions, provenance requirements, safety allowlists and storage bounds. Existing engine, verification, knowledge-graph, decision-lineage and catalogue capabilities are not removed. CI remains the final acceptance gate; a green local-looking change is not treated as a deployment guarantee.
