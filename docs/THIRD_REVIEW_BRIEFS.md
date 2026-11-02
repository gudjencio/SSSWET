# Independent third-review briefs

The third-review brief endpoint prepares a structured handoff from an existing
evidence dossier and its recorded scientific-review-board assessments.

## Endpoint

`GET /api/third-review-brief?dossier_id=<URL-encoded dossier ID>`

The endpoint is read-only. It does not assign an agent, create a research task,
send data to an external provider, or change the dossier or its reviews.

## Readiness

- `not_ready_fewer_than_two_prior_reviews`: fewer than two prior assessments exist.
- `recommended_due_to_disagreement`: at least two assessments exist and their verdicts differ.
- `optional_independent_check`: at least two assessments exist without differing verdicts.

The brief lists prior reviewer IDs and campaign IDs to exclude from the third
reviewer selection, highlights evidence references shared by prior reviewers,
and provides a neutral assessment protocol and requested response structure.

A shared reference is an overlap signal, not proof that reviewers coordinated
or lacked independence. Reviewer declarations are not independently verified.

## Scientific safeguards

The third review is an additional assessment, not an adjudication. The system
does not use majority voting, automatically assign a reviewer, rewrite claims,
or establish scientific validity. The dossier and prior assessments remain
unchanged.
