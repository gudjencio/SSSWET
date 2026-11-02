# Scientific Memory

SSSWET maintains an append-only, versioned record of research statements. Each revision preserves its predecessor and records its own sources, experiments, graph links, provenance, review note, and workflow status.

## Revision history

The read-only endpoint below returns the complete revision chain for a selected version:

`GET /api/scientific-memory/lineage?version_id=<version-id>`

The response separates:

- `predecessors`: earlier versions in chronological order;
- `selected_version`: the requested record;
- `successors`: later revisions;
- `current_version_id`: the latest recorded version for the same memory key.

The endpoint returns HTTP 400 when `version_id` is missing and HTTP 404 when the version does not exist.

## Interpretation safeguards

- Historical versions are preserved; revisions do not overwrite earlier statements.
- A newer version is not automatically more accurate than an older one.
- Workflow labels such as `candidate`, `reviewed`, `contested`, and `archived` do not establish scientific validity.
- A complete revision chain describes record history, not proof.
- No automatic adjudication or promotion to verified fact occurs.

## Existing overview

Use `GET /api/scientific-memory` to retrieve the memory overview. Add `q` for lexical retrieval and `limit` to bound the response. The overview identifies current and superseded versions and flags links to graph contradictions for human review.
