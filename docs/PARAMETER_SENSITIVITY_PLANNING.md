# Parameter sensitivity planning

The local read-only endpoint `GET /api/parameter-sensitivity-plans` builds proposed sensitivity-study designs from metadata explicitly attached to published digital-laboratory protocol versions.

## Protocol metadata

A protocol may define a `parameter_sensitivity` object keyed by each required parameter. Each parameter entry must include:

- `unit`: exactly matching the protocol's declared unit for that parameter;
- `range.minimum` and `range.maximum`: finite numeric bounds, with minimum below maximum;
- `baseline`: a finite value inside the range;
- `levels`: 3–9 unique, explicit numeric values inside the range, including the baseline;
- `measurement_uncertainty`: a finite, non-negative value with the same unit;
- `replicates`: an integer from 2 to 100;
- `safety_constraints`: explicit operating boundaries and safeguards;
- `rationale`: why the parameter is being varied.

All required protocol parameters need complete metadata before a complete design is generated. Incomplete definitions are reported with field-specific reasons; they do not receive invented defaults.

## Design method

The planner creates a one-factor-at-a-time (OAT) scenario matrix. Each scenario retains the baseline values for other parameters, varies one parameter to one declared level, and receives a stable identifier. Each level is listed for the requested number of repetitions.

OAT is a screening design. It does not estimate interactions between parameters, nonlinear causal effects, or a global optimum. Interactions are explicitly marked `not_assessed`. Measurement uncertainty is recorded as supplied metadata; the planner does not propagate uncertainty or infer a confidence interval.

## Review and safety boundaries

The endpoint is read-only. It does not create tasks, change protocol versions, schedule or execute experiments, or authorize any physical activity. A plan classified `ready_for_human_review` is only structurally complete against the declared fields. Qualified reviewers must assess the design, measurement method, uncertainty model, environmental constraints, safety, ethics, legal requirements and feasibility before any study is considered.

A proposed scenario is not an observation. No trend, effect, causality or scientific validity is established by generating a plan. High-impact or safety-critical research requires the appropriate domain experts and formal approvals.
