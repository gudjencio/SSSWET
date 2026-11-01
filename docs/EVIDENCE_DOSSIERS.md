# Evidence dossiers

SSSWET evidence dossiers provide a reproducible, reviewable package around a research result. They assemble references to records that already exist in the local research store and preserve the state available at the time of assembly.

## What a dossier contains

A dossier can reference:

- published protocol versions;
- recorded laboratory runs and their provenance;
- registered dataset versions and content fingerprints;
- recorded cross-campaign comparisons;
- literature/source records;
- peer-review cases;
- dispute cases and explicit objections.

The assembled snapshot is content-hashed and immutable. Review actions are append-only events.

## Review boundary

A dossier is **not** a scientific certification. Its state remains `unverified`, and the service explicitly reports `scientific_validity_established: false`.

Reviewer decisions only describe the dossier's readiness for further review:

- `accepted_for_review`
- `needs_revision`
- `rejected_for_review`

A review decision never changes a protocol, run, dataset, source, knowledge node, or verification state.

## API

The local read-only interface exposes:

- `GET /api/evidence-dossiers`
- `GET /api/evidence-dossiers/<dossier_id>`

Dossier assembly and review are local service operations rather than public HTTP mutations. The public HTTP interface remains read-only.

## Traceability principle

A dossier records provenance and review context; it does not replace the underlying records. Scientific conclusions should remain traceable to the original protocol, run, dataset, comparison and source records.

For simulations, model outputs and computational reproductions, the dossier preserves the distinction between a reproducible computation and a real-world observation.
