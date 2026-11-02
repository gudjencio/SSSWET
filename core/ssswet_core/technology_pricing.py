"""Transparent pricing rules for future SSSWET product sales.

This module is intentionally separate from research contributions and subscriptions.
A solidarity surcharge is only calculated when a technology has an explicitly
approved rate. Instalments carry no surcharge, so payment timing does not raise
the product price.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

PaymentMode = Literal["one_time", "installments"]
CENT = Decimal("0.01")


def build_technology_quote(
    *, base_price: Decimal | str | int | float,
    payment_mode: PaymentMode,
    solidarity_rate: Decimal | str | int | float,
    installments: int = 1,
) -> dict[str, str | int | bool]:
    """Build a quote using a technology-specific approved solidarity rate.

    The surcharge is applied only to a one-time payment. Instalments are
    interest-free and surcharge-free; their sum equals the base price.
    """
    try:
        price = Decimal(str(base_price))
        rate = Decimal(str(solidarity_rate))
    except Exception as exc:
        raise ValueError("price and solidarity rate must be valid numbers") from exc
    if not price.is_finite() or price <= 0:
        raise ValueError("base price must be a positive finite amount")
    if not rate.is_finite() or rate < 0 or rate > 1:
        raise ValueError("solidarity rate must be between 0 and 1")
    if payment_mode not in ("one_time", "installments"):
        raise ValueError("unsupported payment mode")
    if not isinstance(installments, int) or isinstance(installments, bool) or installments < 1 or installments > 120:
        raise ValueError("installments must be between 1 and 120")
    if payment_mode == "one_time":
        surcharge = (price * rate).quantize(CENT, rounding=ROUND_HALF_UP)
        total = price + surcharge
        count = 1
    else:
        surcharge = Decimal("0.00")
        total = price
        count = installments
    per_payment = (total / count).quantize(CENT, rounding=ROUND_HALF_UP)
    final_payment = total - per_payment * (count - 1)
    return {
        "currency": "EUR",
        "base_price": str(price.quantize(CENT, rounding=ROUND_HALF_UP)),
        "solidarity_rate": str(rate),
        "solidarity_surcharge": str(surcharge),
        "total_price": str(total.quantize(CENT, rounding=ROUND_HALF_UP)),
        "payment_mode": payment_mode,
        "installment_count": count,
        "regular_installment": str(per_payment),
        "final_installment": str(final_payment.quantize(CENT, rounding=ROUND_HALF_UP)),
        "interest_free": True,
        "installment_surcharge_free": payment_mode == "installments",
        "commercial_offer_authorized": False,
    }
