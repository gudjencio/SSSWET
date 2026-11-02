from decimal import Decimal

import pytest

from ssswet_core.technology_pricing import build_technology_quote
from ssswet_core.provisional_pricing import (
    REQUIRED_COST_CATEGORIES,
    estimate_provisional_technology_price,
)


def _complete_cost_items():
    return [
        {
            "category": category,
            "low": "0" if category == "materials" else "10",
            "base": "0" if category == "materials" else "20",
            "high": "0" if category == "materials" else "30",
            "source_ref": f"evidence:{category}",
            "verified": True,
        }
        for category in REQUIRED_COST_CATEGORIES
    ]


def _estimate(**overrides):
    args = {
        "cost_items": _complete_cost_items(),
        "currency": "USD",
        "uncertainty_rate": "0.05",
        "tax_rate": "0.20",
        "confidence": "0.90",
        "independent_verifier_approved": True,
    }
    args.update(overrides)
    return estimate_provisional_technology_price(**args)


def test_complete_verified_estimate_is_calculated_but_not_a_commercial_offer():
    result = _estimate()
    assert result["publishable"] is True
    assert result["commercial_offer_authorized"] is False
    assert result["research_success_or_delivery_guaranteed"] is False
    assert result["cost_subtotals"] == {"low": "80.00", "base": "160.00", "high": "240.00"}
    assert result["uncertainty_reserve"]["base"] == "8.00"
    assert result["pretax_estimates"]["base"] == "168.00"
    assert result["tax_estimates"]["base"] == "33.60"
    assert result["consumer_total_estimates"]["base"] == "201.60"


def test_missing_tax_withholds_publication_and_never_guesses_tax():
    result = _estimate(tax_rate=None)
    assert result["publishable"] is False
    assert result["tax_unknown_blocks_publication"] is True
    assert result["consumer_total_estimates"] is None


def test_missing_cost_category_withholds_publication():
    items = _complete_cost_items()[:-1]
    result = _estimate(cost_items=items)
    assert result["publishable"] is False
    assert "fulfilment" in result["missing_categories"]


def test_unverified_cost_evidence_withholds_publication():
    items = _complete_cost_items()
    items[0]["verified"] = False
    result = _estimate(cost_items=items)
    assert result["publishable"] is False
    assert result["evidence_complete"] is False


def test_independent_verifier_is_required():
    result = _estimate(independent_verifier_approved=False)
    assert result["publishable"] is False


def test_low_confidence_withholds_publication():
    result = _estimate(confidence="0.79")
    assert result["publishable"] is False


@pytest.mark.parametrize("rate", ["-0.01", "0.1001", "NaN"])
def test_uncertainty_rate_outside_guardrail_is_rejected(rate):
    with pytest.raises(ValueError, match="uncertainty_rate"):
        _estimate(uncertainty_rate=rate)


def test_cost_ranges_must_be_ordered():
    items = _complete_cost_items()
    items[0]["low"] = "25"
    items[0]["base"] = "20"
    with pytest.raises(ValueError, match="low <= base <= high"):
        _estimate(cost_items=items)


def test_duplicate_cost_categories_are_rejected():
    items = _complete_cost_items()
    items.append(dict(items[0]))
    with pytest.raises(ValueError, match="duplicate"):
        _estimate(cost_items=items)


def test_zero_cost_must_still_have_verifiable_evidence():
    items = _complete_cost_items()
    zero_item = next(item for item in items if item["category"] == "materials")
    zero_item["source_ref"] = ""
    result = _estimate(cost_items=items)
    assert result["publishable"] is False
    assert result["evidence_complete"] is False


def test_existing_commercial_quote_calculator_remains_separate():
    quote = build_technology_quote(
        base_price="100", payment_mode="installments",
        solidarity_rate="0.10", installments=3
    )
    assert Decimal(quote["regular_installment"]) * 2 + Decimal(quote["final_installment"]) == Decimal("100.00")
