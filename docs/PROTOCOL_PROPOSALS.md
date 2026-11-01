# Protocol improvement proposals

SSSWET supports a review workflow for proposed changes to published digital-lab
protocols.

A proposal is submitted against an exact protocol ID and version by a different
active research campaign. It contains a restricted set of editable protocol
fields and a written rationale. The campaign that owns the protocol must review
the proposal and provide a written note when accepting or rejecting it.

Acceptance creates the next immutable protocol version. The prior version and
all run records remain unchanged. If the protocol has advanced since the
proposal was submitted, the proposal cannot be accepted; a new proposal must
target the latest version. Rejection records the decision without changing the
protocol.

The local read-only review queue is available at
`GET /api/digital-lab/proposals`. The Python service is available as
`ProtocolProposalService` in `ssswet_core.protocol_proposals`.

Proposal decisions govern protocol maintenance only. They do not establish
scientific validity, replace independent review, or authorize physical
experiments. The proposal event history retains submission and decision notes.
