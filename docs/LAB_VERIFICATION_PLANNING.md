# Laboratory verification planning

The local read-only endpoint `GET /api/lab-verification-plans` builds a human-review checklist for each finding returned by the laboratory discrepancy screen.

Plans can identify missing run records, incompatible protocol conditions, environment or implementation differences, unverified independence, shared source or dataset provenance, incomplete comparison metadata, and follow-up checks relevant to a recorded output divergence.

These are bounded review suggestions derived from saved metadata. They do not create tasks, schedule or execute experiments, modify evidence, or determine which result is correct. Any repeat or measurement activity remains subject to applicable safety, ethics, legal, institutional and professional review. Simulation records remain distinct from real observations.

The endpoint reports no scientific validity as established. Reviewers must assess the underlying records and uncertainty before drawing conclusions.
