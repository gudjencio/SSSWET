from decimal import Decimal
import pytest

from ssswet_core.order_registry import PrivateOrderRegistry


def test_order_requires_full_verified_balance_before_fulfilment(tmp_path):
    registry = PrivateOrderRegistry(tmp_path / "orders.sqlite3")
    order = registry.create_order("time-travel", "EUR", "120.00", "12.00")
    assert order["balance_minor"] == 13200
    with pytest.raises(ValueError, match="Full payment"):
        registry.update_fulfilment(order["order_id"], "preparing", "operator")

    registry.record_verified_payment(
        order["order_id"], "60.00", "EUR", "PayPal",
        "provider-tx-1", "operator",
    )
    assert registry.get_order(order["order_id"])["state"] == "partially_paid"
    registry.record_verified_payment(
        order["order_id"], "72.00", "EUR", "PayPal",
        "provider-tx-2", "operator",
    )
    paid = registry.get_order(order["order_id"])
    assert paid["state"] == "paid"
    assert paid["balance_minor"] == 0
    assert paid["delivery_address_stored"] is False
    registry.update_fulfilment(order["order_id"], "preparing", "operator")
    registry.update_fulfilment(order["order_id"], "shipped", "operator", "carrier-ref")
    received = registry.update_fulfilment(
        order["order_id"], "received", "operator", "receipt-ref"
    )
    assert received["state"] == "received"


def test_duplicate_payment_reference_is_rejected(tmp_path):
    registry = PrivateOrderRegistry(tmp_path / "orders.sqlite3")
    order = registry.create_order("armor", "EUR", "100")
    args = (order["order_id"], "50", "EUR", "PayPal", "same-ref", "operator")
    registry.record_verified_payment(*args)
    with pytest.raises(Exception):
        registry.record_verified_payment(*args)


def test_currency_mismatch_and_overpayment_are_rejected(tmp_path):
    registry = PrivateOrderRegistry(tmp_path / "orders.sqlite3")
    order = registry.create_order("jetpacks", "EUR", "100")
    with pytest.raises(ValueError, match="currency"):
        registry.record_verified_payment(order["order_id"], "10", "USD", "PayPal", "usd-1", "operator")
    with pytest.raises(ValueError, match="exceeds"):
        registry.record_verified_payment(order["order_id"], "101", "EUR", "PayPal", "eur-1", "operator")


def test_delivery_events_are_append_only_and_do_not_store_address(tmp_path):
    registry = PrivateOrderRegistry(tmp_path / "orders.sqlite3")
    order = registry.create_order("longevity", "EUR", "10")
    registry.record_verified_payment(order["order_id"], "10", "EUR", "PayPal", "tx-1", "operator")
    registry.update_fulfilment(order["order_id"], "preparing", "operator")
    with registry._connect() as db:
        with pytest.raises(Exception):
            db.execute("UPDATE order_events SET event_type='tampered'")
    result = registry.get_order(order["order_id"])
    assert "address" not in str(result).lower() or result["delivery_address_stored"] is False
