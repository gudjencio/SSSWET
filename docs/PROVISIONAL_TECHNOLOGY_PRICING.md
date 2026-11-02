# Evidence-based provisional technology pricing

## Purpose and boundary

SSSWET may calculate a provisional research-cost estimate for a technology programme. The estimate is not a product offer, presale, guarantee of technical success, delivery promise, or authorization to collect payment. Research contributions remain separate from future product sales.

The calculator reports low, base and high scenarios. It uses only cost entries supported by evidence references and explicitly marked as verified. It does not invent missing costs, exchange rates, tax rates, or source material.

## Required cost categories

Every estimate must account for each category below. A genuine zero-cost category must still have an evidence reference explaining why its cost is zero.

- Research labour
- Specialist review
- Materials
- Prototypes
- Testing
- Compute and infrastructure
- Safety and quality assurance
- Maintenance
- Fulfilment

Each category records low, base and high estimates, a source reference, and verification status. Duplicate categories, unsupported categories, negative amounts, and inverted scenario ranges are rejected.

## Uncertainty reserve

The provisional uncertainty reserve is calculated as a percentage of the evidenced pre-tax cost subtotal. The current software guardrail is 10% maximum. If a realistic uncertainty allowance would exceed this cap, the estimate must be withheld and the underlying research or cost model improved; the system must not silently truncate the risk or publish an artificially low figure.

The reserve is not profit, tax, a statutory fee, or a guarantee. It represents a documented allowance for forecast uncertainty. Its rate and supporting rationale must be retained with the estimate.

## Taxes and publication gate

Tax is not guessed. A tax rate must be supplied for the relevant customer jurisdiction before a consumer-facing total can be marked ready for review. The software does not decide which tax regime applies or replace professional tax advice.

An estimate is marked ready for review only when:
1. All required cost categories are present.
2. Every cost item has a source reference and is marked verified.
3. The confidence score is at least 0.80.
4. A destination-relevant tax rate is supplied.
5. An independent verifier has approved the estimate.

The 0.80 confidence threshold is a provisional internal quality gate, not a scientific standard. A result that passes is still not a commercial offer: `commercial_offer_authorized` remains false. Separate legal, product-safety, fulfilment, consumer-rights and payment approvals are still required.

## Outputs and audit trail

Each estimate preserves currency, source references, cost subtotals, uncertainty reserve, pre-tax scenarios, tax scenarios, consumer-total scenarios, confidence, missing categories and publication-gate status. Estimates should be stored with a timestamp, technology identifier, model/version, estimator identity and independent review record in the project's audit system.

## Implementation

The deterministic calculator is implemented in `core/ssswet_core/provisional_pricing.py`. Its tests are in `core/tests/test_provisional_pricing.py`. It is deliberately separate from `technology_pricing.py`, which calculates future approved commercial quotes and instalments.
