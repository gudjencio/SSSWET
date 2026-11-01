# Laboratory verification planning

The local read-only endpoint `GET /api/lab-verification-plans` builds a human-review checklist for each finding returned by the laboratory discrepancy screen.

Plans can identify missing run records, incompatible protocol conditions, environment or implementation differences, unverified independence, shared source or dataset provenance, incomplete comparison metadata, and follow-up checks relevant to a recorded output divergence.

These are bounded review suggestions derived from saved metadata. They do not create tasks, schedule or execute experiments, modify evidence, or determine which result is correct. Any repeat or measurement activity remains subject to applicable safety, ethics, legal, institutional and professional review. Simulation records remain distinct from real observations.

The endpoint reports no scientific validity as established. Reviewers must assess the underlying records and uncertainty before drawing conclusions.


## Review lifecycle

Each verification check has a stable plan/check identifier and an append-only review history. A reviewer can record `in_progress`, `completed` or `blocked` with a required note and reviewer label. A completed check is closed; its event history remains available and cannot be overwritten or deleted.

The local interface exposes `GET /api/lab-verification-events` and a loopback-only `POST /api/lab-verification-events`. The write endpoint accepts only local-machine requests. This is a local review log, not an identity or authorization system: reviewer labels are self-declared. Deployments beyond a trusted local machine require authentication, authorization, CSRF protection and an audit policy before enabling writes.

A review event records an administrative check state only. It does not validate data, certify independence, resolve a scientific dispute or establish scientific validity.
