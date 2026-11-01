# Pairwise parameter interaction planning

The local read-only endpoint `GET /api/parameter-interaction-plans` prepares bounded two-factor factorial study proposals from explicitly nominated parameter pairs in a published digital-laboratory protocol.

## Declaring candidate interactions

Inside a protocol's `parameter_sensitivity` metadata, define `interaction_candidates` as a list of objects. Each object contains:

- `parameters`: exactly two distinct names from the protocol's required parameters;
- `replicates`: an integer from 2 to 100 for each factor-level combination;
- `rationale`: a concise, documented reason to investigate this pair.

Both factors must also have complete, valid sensitivity metadata, and every other required parameter must have a declared baseline so it can be held constant: matching units, explicit numeric ranges, baseline values, 3–9 unique levels including the baseline, measurement uncertainty, replicate metadata, safety constraints and rationale. No interaction pair or range is inferred from recorded runs.

## Design construction

For each nominated pair, the planner constructs a balanced two-factor full-factorial grid from the declared levels. Other required parameters remain at their declared baseline values. Each combination is repeated the requested number of times and receives a stable scenario identifier.

The planner permits at most 500 generated scenarios per protocol across all candidate pairs. A pair that would exceed the limit is marked as limited and receives no partial scenario grid. Invalid or incomplete pairs are reported without fabricated defaults.

## Interpretation and review

A factorial grid is a proposed design, not an analysis. The planner does not estimate interaction effects, fit response models, calculate statistical power, propagate uncertainty, establish causality, or identify an optimum. Run order is not assigned: randomization, blocking, measurement procedures, power analysis, model assumptions and outcome analysis must be designed and reviewed by qualified people.

The endpoint is read-only. It does not create tasks, schedule studies, execute simulations or physical experiments, or authorize activity. Human review and all applicable safety, ethics, legal and regulatory approvals remain required.
