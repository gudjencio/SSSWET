# SSSWET daily upgrades — 13 November 2026

## Baseline and pre-implementation controls

The work was based on main at `bd906b86bae2379b36f4d5ac48f743c161f1003d`, with immediate predecessor `09f118132ac8c0c17f3b708ad2612dab3016166d`. The direct comparison showed that the current head adds deterministic, privacy-bounded observation-snapshot fingerprints to the local clock-calibration workspace, verification tests, documentation and service-worker cache version v199. The predecessor adds the local clock-calibration workspace. The previous two mainline commits repaired the public interface and added bounded research context, human-review queues, graph-neighbour retrieval, paginated memory lineage, literature-watch diffs, broader official scholarly metadata discovery and dataset-governed reproducibility manifests. The inspected baseline CI run 43288598711 passed.

The existing modules already cover versioned scientific memory, contradiction links, provenance, 21-language clickbait cue triage, permission-aware search planning for social/video channels, reproducibility, rescue allocation, protective-design assurance, Virtual Time Travel Mapping and a static accessibility audit. The ten changes below add missing bridges around those facilities; none replaces their existing APIs.

## Ten implemented improvements

1. **Permission-aware public media intake** — `public_media_ingestion.py` normalizes public metadata for YouTube, X, Instagram, Facebook, Threads, Bluesky, Reddit, Snapchat, MeWe, Weibo, Bilibili, Niconico, Qiita and public forums. It enforces per-platform access modes, public visibility, HTTPS links and bounded metadata fields; it flags sensitive field names without returning their values and retains duplicate candidates rather than discarding records.
2. **Multilingual translation-fidelity audit** — `translation_fidelity.py` compares supplied original/translated text for quantities, recognized units, configured critical term pairs and negation cues across 27 language families. It never translates or certifies meaning.
3. **Claim/evidence corroboration matrix** — `claim_evidence_matrix.py` separates support, contradiction, neutral, withdrawn and under-review links; counts distinct provenance groups rather than repeated sources from the same group; exposes unresolved links and emits no truth score.
4. **Evidence-change impact propagation** — `evidence_change_impact.py` traverses bounded dependency graphs from changed source/artifact IDs, returns shortest downstream paths, missing references and cycle diagnostics, and leaves stored records untouched.
5. **Integrity-checked research checkpoint bundles** — `research_checkpoint_bundle.py` creates canonical SHA-256 bundles capped at 65,536 bytes and blocks safe-resume assessment when the query plan, context digest, memory versions, source fingerprints or review blockers differ.
6. **Agent execution provenance receipts** — `agent_execution_receipts.py` hashes bounded execution metadata, toolchain versions, input references, output digests, budgets and parent receipt IDs; it verifies receipt chains and rejects arbitrary/secret-bearing fields. Receipts do not store prompts or raw outputs.
7. **Spatiotemporal uncertainty envelopes** — `spatiotemporal_uncertainty.py` propagates declared clock and GPS uncertainty into distance/speed intervals, including antimeridian-safe distance calculation. It withholds an upper speed bound when time intervals overlap.
8. **Civil-rescue demand stress testing** — `rescue_scenario_robustness.py` compares best/expected/worst supply and demand ranges for the existing civil-rescue resource allowlist; it does not allocate supplies or dispatch responders.
9. **Protective/rescue design change-impact review** — `protective_design_change_impact.py` maps changed requirements, hazards, controls and evidence to stale verification records and critical hazards requiring renewed independent review. It never approves a design.
10. **Public web accessibility/performance quality gate** — `web_quality_gate.py` runs the existing static accessibility audit against the main and Virtual Time Travel HTML entry points, checks local assets and measures JavaScript/CSS/HTML bytes against explicit budgets. CI invokes `.github/scripts/check_web_quality.py`.

## Acceptance checks

The shared regression suite is `core/tests/test_daily_upgrades_2026_11_13.py`. It checks the 14-channel public metadata allowlist, sensitive-field exclusion, batch bounds, quantity/unit/negation drift, provenance-group deduplication, retained counterevidence, dependency propagation/cycles, checkpoint tampering and stale resume inputs, agent receipt hash chains, antimeridian and overlapping-time uncertainty, rescue worst-case shortages, design-change impact and web accessibility/asset budgets.

### Previous behaviour versus this release

- Social/video channels previously had permission-aware query-plan descriptions but no common normalized public-record envelope. The new intake layer provides one while deliberately leaving actual API credentials and network access to separately authorized providers.
- Translation checks previously had title clickbait cues but no cross-language quantity/unit/negation drift report.
- Contradictions and provenance existed in separate structures; the new matrix reports claim-level support and counterevidence without collapsing them into a score.
- Existing snapshots and ledgers preserved history, but downstream derived artifacts did not have a reusable dependency-impact report when an upstream source changed.
- Existing task checkpoints were in-memory state snapshots; the new bundle is digest-verifiable and compares exact resume dependencies.
- Agent task contracts and decision ledgers existed, but there was no hash-linked per-execution receipt chain binding input/output digests and tool versions.
- Virtual Time Travel already stored GPS accuracy and clock uncertainty separately; the new segment utility propagates both into bounded distance/speed intervals.
- Existing rescue planning allocated fixed quantities; the new scenario utility stress-tests uncertain ranges without performing allocation.
- Existing protective-design assurance evaluated a design snapshot; the new utility identifies verification and review records affected by design changes.
- Existing accessibility checks were reusable but not enforced as a public-web CI gate with explicit asset budgets.

## Safety, privacy and limitations

- Public media intake is a normalizer for records already returned by official APIs or permitted public feeds. It does not scrape restricted pages, authenticate, download media, access private accounts or bypass platform terms. Instagram/Facebook/Threads records require their approved API access modes.
- Translation matching is lexical and may miss idioms, scope, modality, sarcasm or equivalent wording. A clean report is not a translation certificate.
- A provenance group is only as accurate as its source metadata. The matrix does not infer publisher independence from titles.
- Change-impact output is advisory. It does not automatically retract, delete, invalidate or modify stored research.
- Checkpoint and receipt hashes detect payload changes; they are not digital signatures and do not prove source authenticity or execution correctness.
- Spatiotemporal results use declared bounds only; no missing history is recovered and no future trajectory is predicted.
- Rescue/design outputs are non-operational review aids. They do not authorize dispatch, medical decisions, evacuation, deployment or safe use.
- The web gate is a static automated check, not a complete WCAG audit. Contrast and real keyboard/screen-reader behaviour still require manual review.
- No payment, tax, refund, customer-data, credential, legal-policy or commercial-promise settings were changed.

## Validation status

Implementation tests and CI are being run against the updated mainline. Final measured results and any remaining limitations will be recorded after the workflows complete.