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


## Reference integrity

The overview checks whether linked source, experiment, and knowledge-graph identifiers resolve in the current research store. Each version exposes `missing_links` and `has_missing_links`; the overview provides aggregate counts.

A missing link indicates an incomplete or unavailable local record, not that the underlying source or experiment is invalid. The check is bounded by the overview's graph and experiment limits and does not modify memory records or scientific status.


## Evolution alerts

The `GET /api/scientific-memory/suggestions` response includes `potentially_outdated_memory`. An alert is emitted when a current memory version links to a graph node that has a recorded `contradicts` edge to another node whose recorded creation time is later than the memory version.

Alerts identify records for human re-examination; they do not establish that a hypothesis is false, do not rank evidence quality, and never revise or archive memory automatically. The response includes the later node, edge note and recorded confidence when available.


## Source independence comparison

Use `GET /api/source-independence?source_ids=source-a,source-b` to compare up to 100 registered sources. The report distinguishes explicit dependency signals (shared DOI, dataset, provenance group, or declared source relationship) from contextual overlaps (shared authors or institutions).

A dependency signal triggers review; it does not prove that two reports are dependent. Contextual overlaps are not treated as dependency proof. Most importantly, no recorded overlap does not prove independence, so the API never calculates an independent-source count or upgrades verification status.
