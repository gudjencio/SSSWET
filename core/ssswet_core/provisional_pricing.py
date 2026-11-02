"""Evidence-gated provisional technology cost estimates.

This module estimates research/product cost scenarios. It does not authorize
commercial offers, collect payments, calculate jurisdiction-specific tax rules,
or promise that a research programme will succeed.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")
MAX_UNCERTAINTY_RATE = Decimal("0.10")
MIN_PUBLICATION_CONFIDENCE = Decimal("0.80")

REQUIRED_COST_CATEGORIES = (
    "research_labour",
    "specialist_review",
    "materials",
    "prototypes",
    "testing",
    "compute_infrastructure",
    "safety_quality",
    "maintenance",
    "fulfilment",
)


def _decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field} must be a valid decimal number") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def estimate_provisional_technology_price(
    *,
    cost_items: list[dict[str, Any]],
    currency: str,
    uncertainty_rate: Decimal | str | int | float,
    tax_rate: Decimal | str | int | float | None,
    confidence: Decimal | str | int | float,
    independent_verifier_approved: bool,
) -> dict[str, Any]:
    """Build low/base/high estimates and withhold publication if evidence is weak.

    Every required cost category must be represented, including evidenced
    zero-cost entries. Each entry needs low/base/high amounts, a source
    reference, and a verified flag. Tax is deliberately mandatory for a
    publishable consumer-facing total; unknown tax is never guessed.
    """
    if not isinstance(cost_items, list) or not cost_items:
        raise ValueError("cost_items must be a non-empty list")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
        raise ValueError("currency must be a three-letter code")
    currency = currency.upper()

    reserve_rate = _decimal(uncertainty_rate, "uncertainty_rate")
    if reserve_rate < 0 or reserve_rate > MAX_UNCERTAINTY_RATE:
        raise ValueError("uncertainty_rate must be between 0 and 0.10")

    confidence_score = _decimal(confidence, "confidence")
    if confidence_score < 0 or confidence_score > 1:
        raise ValueError("confidence must be between 0 and 1")

    tax = None if tax_rate is None else _decimal(tax_rate, "tax_rate")
    if tax is not None and (tax < 0 or tax > 1):
        raise ValueError("tax_rate must be between 0 and 1")

    totals = {"low": Decimal("0"), "base": Decimal("0"), "high": Decimal("0")}
    seen: set[str] = set()
    evidence_complete = True
    source_refs: list[str] = []

    for item in cost_items:
        if not isinstance(item, dict):
            raise ValueError("each cost item must be an object")
        category = item.get("category")
        if category not in REQUIRED_COST_CATEGORIES:
            raise ValueError(f"unsupported cost category: {category}")
        if category in seen:
            raise ValueError(f"duplicate cost category: {category}")
        seen.add(category)

        source_ref = item.get("source_ref")
        verified = item.get("verified") is True
        if not isinstance(source_ref, str) or not source_ref.strip() or not verified:
            evidence_complete = False
        elif source_ref not in source_refs:
            source_refs.append(source_ref.strip())

        amounts = {
            key: _decimal(item.get(key), f"{category}.{key}")
            for key in ("low", "base", "high")
        }
        if any(amount < 0 for amount in amounts.values()):
            raise ValueError(f"{category} amounts cannot be negative")
        if not amounts["low"] <= amounts["base"] <= amounts["high"]:
            raise ValueError(f"{category} must satisfy low <= base <= high")
        for key, amount in amounts.items():
            totals[key] += amount

    missing_categories = sorted(set(REQUIRED_COST_CATEGORIES) - seen)
    reserve = {key: totals[key] * reserve_rate for key in totals}
    pretax = {key: totals[key] + reserve[key] for key in totals}
    tax_amounts = None if tax is None else {key: pretax[key] * tax for key in pretax}
    consumer_totals = None if tax_amounts is None else {
        key: pretax[key] + tax_amounts[key] for key in pretax
    }

    publishable = (
        not missing_categories
        and evidence_complete
        and tax is not None
        and confidence_score >= MIN_PUBLICATION_CONFIDENCE
        and independent_verifier_approved is True
    )

    def scenario(values: dict[str, Decimal] | None) -> dict[str, str] | None:
        if values is None:
            return None
        return {key: _money(value) for key, value in values.items()}

    return {
        "currency": currency,
        "status": "estimate_ready_for_review" if publishable else "withheld_pending_evidence_or_review",
        "publishable": publishable,
        "commercial_offer_authorized": False,
        "research_success_or_delivery_guaranteed": False,
        "confidence": str(confidence_score),
        "minimum_publication_confidence": str(MIN_PUBLICATION_CONFIDENCE),
        "independent_verifier_approved": independent_verifier_approved is True,
        "evidence_complete": evidence_complete and not missing_categories,
        "missing_categories": missing_categories,
        "source_refs": source_refs,
        "uncertainty_rate": str(reserve_rate),
        "uncertainty_reserve_cap": str(MAX_UNCERTAINTY_RATE),
        "cost_subtotals": scenario(totals),
        "uncertainty_reserve": scenario(reserve),
        "pretax_estimates": scenario(pretax),
        "tax_rate": None if tax is None else str(tax),
        "tax_estimates": scenario(tax_amounts),
        "consumer_total_estimates": scenario(consumer_totals),
        "tax_unknown_blocks_publication": tax is None,
        "pricing_is_a_research_estimate_not_a_product_offer": True,
    }
