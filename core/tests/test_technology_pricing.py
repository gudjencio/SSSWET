from decimal import Decimal

import pytest

from ssswet_core.technology_pricing import build_technology_quote


def test_one_time_purchase_includes_technology_specific_solidarity_surcharge():
    quote = build_technology_quote(
        base_price="1200.00", payment_mode="one_time", solidarity_rate="0.075"
    )
    assert quote["solidarity_surcharge"] == "90.00"
    assert quote["total_price"] == "1290.00"
    assert quote["installment_count"] == 1
    assert quote["commercial_offer_authorized"] is False


def test_installments_keep_the_same_base_price_without_surcharge():
    quote = build_technology_quote(
        base_price="1000", payment_mode="installments",
        solidarity_rate="0.20", installments=4
    )
    assert quote["solidarity_surcharge"] == "0.00"
    assert quote["total_price"] == "1000.00"
    assert quote["regular_installment"] == "250.00"
    assert quote["final_installment"] == "250.00"
    assert quote["interest_free"] is True


def test_installment_rounding_preserves_exact_total():
    quote = build_technology_quote(
        base_price="100", payment_mode="installments",
        solidarity_rate="0.10", installments=3
    )
    assert Decimal(quote["regular_installment"]) * 2 + Decimal(quote["final_installment"]) == Decimal("100.00")


@pytest.mark.parametrize("price,rate", [("0", "0.1"), ("-1", "0.1"), ("100", "-0.1"), ("100", "1.1"), ("NaN", "0.1")])
def test_invalid_price_or_rate_is_rejected(price, rate):
    with pytest.raises(ValueError):
        build_technology_quote(base_price=price, payment_mode="one_time", solidarity_rate=rate)


def test_invalid_installment_count_is_rejected():
    with pytest.raises(ValueError, match="installments"):
        build_technology_quote(base_price=100, payment_mode="installments", solidarity_rate=0.1, installments=0)
