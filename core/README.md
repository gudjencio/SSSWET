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
