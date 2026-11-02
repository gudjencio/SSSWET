# Research Reproducibility Monitor

The monitor checks the completeness and consistency of supplied research-run metadata. It is a diagnostic aid for record review, not an experiment runner or scientific certification service.

## Checks

- Required run identifiers, versioned protocol and dataset references, parameters, environment metadata and result fingerprints.
- Duplicate run identifiers in the supplied batch.
- Different result fingerprints among runs with matching recorded protocol, dataset, parameter and environment fields.

## Python usage

```python
from ssswet_core.reproducibility_monitor import ResearchReproducibilityMonitor

report = ResearchReproducibilityMonitor().analyze(run_records)
```

## Interpretation

A metadata match is not proof that physical or computational conditions were identical. A matching fingerprint is not proof of independent reproduction. Different fingerprints are a prompt to inspect original logs, seeds, software and hardware versions, hidden state and measurement uncertainty.

The monitor does not execute experiments, alter verification states, infer missing values, or establish scientific validity. All findings require human review and source-record inspection.
