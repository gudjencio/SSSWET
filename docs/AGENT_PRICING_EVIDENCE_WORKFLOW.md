# Agent-sourced technology pricing evidence

## Workflow

The pricing evidence adapter accepts structured cost submissions from registered SSSWET agent roles and passes only aggregated, explicitly sourced records to the deterministic provisional pricing calculator.

It does not autonomously query external sources or infer prices from an agent's narrative. A submission is data requiring evidence, not proof by virtue of being authored by an agent.

## Submission requirements

Each submission includes:
- a unique submission ID;
- the submitting agent ID and registered role;
- one supported cost category;
- low, base and high non-negative estimates;
- a source reference;
- an explicit source-verification flag.

Multiple submissions in the same category are summed scenario by scenario. Missing categories remain missing; the adapter never fills them with invented zero-cost assumptions. Duplicate submission IDs, unknown roles, unsupported categories and invalid ranges are rejected.

## Independent review

A separate reviewer with the `independent_verifier` role must approve the exact estimate ID and provide a review reference. The reviewer cannot be one of the agents who submitted costs for that estimate. A review of a different estimate, missing review reference, or unapproved review blocks publication.

The adapter records the reviewer ID and review status. It does not interpret a review as scientific proof or commercial authorization.

## Boundaries

The adapter is a deterministic validation layer, not an autonomous AI-agent execution system. It does not retrieve sources, verify source contents, decide tax jurisdiction, authorize sales or guarantee research success. Those capabilities require separate connected workflows and controls.

Implementation: `core/ssswet_core/pricing_evidence.py`.
Tests: `core/tests/test_pricing_evidence.py`.
