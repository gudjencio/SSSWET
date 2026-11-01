# Research Integrity & Ethics Framework

The integrity register records concerns linked to an assembled evidence dossier. It is a traceability and review aid, not an ethics committee, safety certification, legal opinion or institutional authorization system.

## Risk categories

- Data integrity and provenance
- Bias
- Conflicts of interest
- Reproducibility
- Safety
- Ethics
- Legal and regulatory constraints
- Security
- Other documented concerns

Each event records a severity (`low`, `medium`, `high`, `critical`), a workflow state, a description, a reviewer label, optional mitigation notes, an optional authorization reference and evidence-reference identifiers.

## Workflow states

`open`, `under_review`, `mitigated`, `accepted_with_controls`, `closed`, and `escalated`.

Events are append-only. A new event updates the displayed current state while preserving the complete prior history. Closing, mitigating or accepting a high/critical safety, ethics or legal/regulatory risk requires a documented mitigation and a qualified human authorization reference. The reference is recorded as supplied; the software does not verify its authenticity or sufficiency.

## API

- `GET /api/research-integrity` returns the latest state per risk and the retained event history.
- `GET /api/research-integrity?dossier_id=<id>` filters the register to one dossier.
- `POST /api/research-integrity/risks` records a new risk event.

Writes are accepted only from the local loopback interface. Reviewer labels and authorization references are self-declared text, not identity or credential verification.

## Hold recommendations and limits

An unresolved high or critical risk sets `campaign_hold_recommendation` to true. This is an advisory signal for a responsible human to assess and, where appropriate, pause the relevant work. The service does not automatically suspend campaigns, stop external processes, approve experiments or authorize research. It does not replace qualified safety, ethics, legal, regulatory or institutional review.

A record marked mitigated or closed is an administrative record of a human-submitted decision, not proof that the underlying risk has been eliminated.
