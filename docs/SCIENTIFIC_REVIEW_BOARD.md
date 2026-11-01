# Scientific Review Board

The Scientific Review Board records structured, independent assessments of assembled evidence dossiers. It preserves each review as a separate append-only event and reports the range of recorded positions without selecting a winner.

## Review fields

Every submission requires a reviewer label, a verdict (`supports`, `challenges`, `mixed` or `abstains`), an explicit conflict-of-interest declaration (`none_declared`, `potential` or `confirmed`), a substantive rationale, a methods assessment and limitations. Evidence-reference identifiers are optional.

Reviewer labels are self-declared. They are not proof of identity, expertise, independence or authorization. Conflict declarations are also self-reported.

## API

- `GET /api/scientific-review-board` returns recent reviews and per-dossier summaries.
- `GET /api/scientific-review-board?dossier_id=<id>` filters to one dossier.
- `POST /api/scientific-review-board/reviews` records a review. The local server accepts write requests only from the loopback interface.

Example request body:

```json
{
  "dossier_id": "dossier-001",
  "reviewer_id": "reviewer-alpha",
  "reviewer_campaign_id": "campaign-independent-review",
  "verdict": "challenges",
  "conflict_status": "potential",
  "rationale": "The uncertainty analysis does not yet support the stated interpretation.",
  "methods_assessment": "The computational method is described, but parameter sensitivity is not documented.",
  "limitations": "The dossier contains simulations rather than physical observations.",
  "evidence_refs": ["run-001", "source-004"]
}
```

## Interpretation safeguards

- Reviews are immutable and are never overwritten or deleted by the service.
- Opposing and mixed assessments remain visible; disagreement is a reported property, not an error to erase.
- The service does not calculate a majority-based scientific verdict, certify reviewer independence, resolve disputes, or establish scientific validity.
- A review board summary is not peer-review accreditation or institutional approval.
- The local-only write restriction is not a substitute for authentication, authorization, CSRF protection or an institutional audit policy in any networked deployment.
