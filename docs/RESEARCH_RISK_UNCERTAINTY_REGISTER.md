# Research Risk & Uncertainty Register

The Research Risk & Uncertainty Register provides a structured summary of risk and uncertainty records explicitly supplied by an authorized research workflow.

## Recorded fields

Each record requires an identifier, title and category. Optional fields include a description, declared status, likelihood and impact labels, owner, review date, evidence references, assumptions, invalidation conditions, mitigation actions and provenance.

Supported categories are scientific, technical, measurement, ethical, environmental, regulatory, safety, operational and other.

## Interpretation

- Missing likelihood and impact remain unknown.
- Missing ownership, review dates, evidence and mitigation details are reported as gaps.
- The register does not calculate a composite score or generate a risk ranking.
- A recorded mitigation is not proof that a risk has been controlled.
- A closed or accepted status is a recorded administrative state, not proof of safety.
- The register does not establish scientific validity, legal compliance, technical feasibility or authorization to proceed.

The component is a deterministic organizer, not a predictive risk model or safety certification. It must not be used as the sole basis for high-consequence decisions.

## Python usage

```python
from ssswet_core.risk_uncertainty_register import ResearchRiskUncertaintyRegister

report = ResearchRiskUncertaintyRegister().analyze([
    {
        "item_id": "risk-001",
        "title": "Measurement uncertainty",
        "category": "measurement",
        "status": "open",
        "evidence_refs": ["source-001"],
    }
])
```

This component accepts explicit records and does not create, update or delete persistent research records.
