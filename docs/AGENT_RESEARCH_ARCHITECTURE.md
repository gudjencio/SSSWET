# Auditable multi-agent research architecture

## Status and scope

This is the first, deliberately bounded foundation for SSSWET's auditable multi-agent research programme. It adds a browser-local, append-only research event ledger. It does **not** yet connect the ledger to autonomous agents, share memory between devices, or provide authenticated human identity.

The design borrows general engineering ideas—provenance, immutable event history, reproducible references, independent review and human approval—from auditable agent systems. It does not copy or depend on Inalpha source code, services, schemas or infrastructure. SSSWET remains MIT-licensed; no AGPL code is incorporated.

## Event model

The first schema supports four event types:

- `proposal`: an agent or person records a bounded research proposal.
- `result`: a research output is recorded with an explicit evidence classification.
- `review`: a reviewer records a review linked to an existing proposal.
- `approval`: a human actor records an explicit `approved` or `rejected` decision linked to an existing proposal.

Every event includes a sequence number, timestamp, actor type and non-identifying actor key, role, classification, short summary, source identifiers, previous-event hash and SHA-256 digest. The digest covers canonical JSON with sorted object keys.

Evidence classifications are deliberately explicit: `observation`, `derived`, `simulation`, and `hypothesis`. A simulation or hypothesis is never promoted to an observation by the ledger.

## Safety and privacy boundaries

- The browser implementation uses local storage only; it makes no network requests.
- The schema is an allowlist. Raw prompts, raw datasets, coordinates, media, credentials and arbitrary payload fields are rejected.
- Summaries are limited to 500 characters; source identifiers are limited to 20 entries of at most 300 characters each; the ledger is limited to 1,000 events.
- Agent actors cannot record approval decisions. An approval must refer to an existing proposal and must be explicitly recorded by an actor marked as human.
- Actor labels are **not authentication**. A local user or script can claim an actor type; this browser-only prototype is a workflow safeguard, not an access-control boundary.
- The hash chain is tamper-evident for accidental or unsophisticated modification, not tamper-proof. Anyone able to rewrite local storage and recompute hashes can rewrite the chain. Exported files should be preserved separately when stronger audit retention is required.
- Storage can be cleared by the user or browser. There is no cloud backup or cross-device synchronization.
- A full ledger refuses further appends; it never silently drops old events.

## Reproducibility contract

A result should reference stable identifiers for the method, source set, dataset version and test fixture. Do not put sensitive source material in the ledger. Store the actual research artefacts in their approved local or separately governed locations and record only stable references and hashes where appropriate.

A future experiment-run schema should add explicit software revision, dependency lock, parameters, random seed, dataset fingerprint, environment description and output fingerprint. Until that schema and its independent verification are implemented, the ledger must not label an experiment reproducible merely because it has a hash.

## Verification

Run:

```sh
node --check web/research-ledger.js
node web/test-research-ledger.cjs
```

The regression test checks deterministic hash-chain integrity, bounded/allowlisted fields, proposal linkage, human-only approval, tamper detection, invalid-storage handling and fail-closed behavior after integrity failure.

## Next integration stages

1. Connect actual research pipeline outputs to the ledger using stable run and agent identifiers; do not store private chain-of-thought or raw prompts.
2. Add run manifests containing code revision, dependencies, parameters, random seed and dataset fingerprints.
3. Add cross-agent memory as references to reviewed, versioned research records—not a shared unfiltered prompt transcript.
4. Add a server-side authenticated approval service only if multi-user collaboration is required. Keep approvals human-controlled and auditable.
5. Add independent replay tests and compare regenerated outputs against recorded fingerprints before claiming reproducibility.

The Virtual Time Travel Mapping programme can later use the same event vocabulary to reference capture sessions, observation batches, model versions and review decisions. The ledger itself does not improve spatial reconstruction accuracy.
