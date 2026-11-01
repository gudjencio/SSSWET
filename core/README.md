# SSSWET Core

The core will coordinate research agents without exposing the agent-generation mechanism to the agents themselves.

## Agent lifecycle

1. Define a precise task.
2. Assign the smallest useful number of specialist agents.
3. Let agents research or calculate independently.
4. Exchange relevant findings.
5. Run independent verification.
6. Run simulations/tests where applicable.
7. Classify the result and its uncertainty.
8. Publish only sufficiently supported conclusions.
9. Checkpoint the safe state.
10. Reassign, pause, replace, or retire agents according to workload.

## Recovery

A blocked agent must preserve the problem statement, then retry using a materially different strategy. Repeated loops are detected and interrupted. New agents can inherit the relevant validated knowledge without inheriting an unverified conclusion as fact.

## Scaling

The orchestrator should create additional agents when workload requires it, split work into groups when several tasks can run concurrently, and reduce idle agents when resource pressure becomes significant.

## Verification states

- `hypothesis`
- `candidate`
- `simulated`
- `independently_verified`
- `reproduced`
- `requires_real_world_validation`
- `rejected`

An agent consensus is not, by itself, scientific proof.

## Evidence independence and disagreement review

Evidence is retained with its source identity. Two evidence entries from the
same source do not count as independent verification. A finding can only enter
the independently verified state after at least two distinct source IDs have
been recorded. Reproduction also requires a separate reproduction-run ID.

Structured claims can be compared by subject, predicate and asserted value.
When distinct sources assert incompatible values, the engine records a
`disagreement_detected` event and queues one independent review task for that
conflict signature. The review is not automatically considered resolved:
the reviewer must inspect source quality, methods, context and uncertainty.
Free-form text is not silently interpreted as structured scientific claims.

Repeated detection of the same conflict does not create an unlimited queue of
duplicate review tasks. Unresolved claims remain unresolved until reviewed.

## Source quality rubric

Source assessments record visible factors: peer review, primary-source status,
availability of methods, known publication date, HTTPS URL and declared
limitations. The resulting score is a prioritization aid, not a probability
of truth and not a substitute for claim-level verification. A high source
score never automatically upgrades a finding's verification state.
