"""Private, local-only order and payment register.

Stores order metadata and verified payment ledger entries only. Never store
customer names, email addresses, delivery addresses, card data or credentials.
"""
from __future__ import annotations

import json
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ORDER_STATES = {"awaiting_payment", "partially_paid", "paid", "preparing", "shipped", "received", "cancelled", "refunded"}
TECHNOLOGIES = {
    "cellular-enhancement", "longevity", "armor", "jetpacks",
    "human-alien-translator", "spacetime-physics", "time-travel",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _amount(value: object) -> int:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Amount must be a valid decimal number") from None
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be positive and use at most two decimal places")
    return int(amount * 100)


class PrivateOrderRegistry:
    """SQLite ledger intended for a single trusted local operator."""

    def __init__(self, database: str | Path = ".ssswet/orders.sqlite3") -> None:
        self.path = Path(database).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    technology TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    base_price_minor INTEGER NOT NULL,
                    access_contribution_minor INTEGER NOT NULL DEFAULT 0,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS order_payments (
                    payment_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL REFERENCES orders(order_id),
                    amount_minor INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    provider_reference TEXT NOT NULL,
                    verified_by TEXT NOT NULL,
                    verified_at TEXT NOT NULL,
                    UNIQUE(provider, provider_reference)
                );
                CREATE TABLE IF NOT EXISTS order_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL REFERENCES orders(order_id),
                    event_type TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_orders_state ON orders(state, created_at);
                CREATE INDEX IF NOT EXISTS idx_order_payments_order ON order_payments(order_id);
                CREATE TRIGGER IF NOT EXISTS order_events_no_update
                    BEFORE UPDATE ON order_events
                    BEGIN SELECT RAISE(ABORT, 'order events are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS order_events_no_delete
                    BEFORE DELETE ON order_events
                    BEGIN SELECT RAISE(ABORT, 'order events are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS order_payments_no_update
                    BEFORE UPDATE ON order_payments
                    BEGIN SELECT RAISE(ABORT, 'verified payment records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS order_payments_no_delete
                    BEFORE DELETE ON order_payments
                    BEGIN SELECT RAISE(ABORT, 'verified payment records are immutable'); END;
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=10000")
        return db

    @staticmethod
    def _event(db: sqlite3.Connection, order_id: str, kind: str, details: dict) -> None:
        db.execute(
            "INSERT INTO order_events(order_id,event_type,details_json,created_at) VALUES(?,?,?,?)",
            (order_id, kind, json.dumps(details, sort_keys=True), _now()),
        )

    def create_order(self, technology: str, currency: str, base_price: object,
                     access_contribution: object = "0") -> dict:
        if technology not in TECHNOLOGIES:
            raise ValueError("Unknown technology identifier")
        currency = str(currency).upper()
        if not re.fullmatch(r"[A-Z]{3}", currency):
            raise ValueError("Currency must be a three-letter ISO code")
        base = _amount(base_price)
        extra = 0 if str(access_contribution) in {"0", "0.0", "0.00", ""} else _amount(access_contribution)
        order_id = "SSW-" + secrets.token_hex(6).upper()
        now = _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",
                (order_id, technology, currency, base, extra, "awaiting_payment", now, now),
            )
            self._event(db, order_id, "order_created", {
                "technology": technology, "currency": currency,
                "base_price_minor": base, "access_contribution_minor": extra,
            })
        return self.get_order(order_id)

    def record_verified_payment(self, order_id: str, amount: object, currency: str,
                                provider: str, provider_reference: str,
                                verified_by: str) -> dict:
        minor = _amount(amount)
        currency = str(currency).upper()
        provider = str(provider).strip()
        reference = str(provider_reference).strip()
        reviewer = str(verified_by).strip()
        if not all((provider, reference, reviewer)) or len(reference) > 200 or len(reviewer) > 120:
            raise ValueError("Provider reference and verifier are required")
        with self._connect() as db:
            order = db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
            if not order:
                raise ValueError("Order not found")
            if order["state"] in {"cancelled", "refunded", "received"}:
                raise ValueError("This order no longer accepts payments")
            if currency != order["currency"]:
                raise ValueError("Payment currency does not match the order")
            due = order["base_price_minor"] + order["access_contribution_minor"]
            paid = db.execute(
                "SELECT COALESCE(SUM(amount_minor),0) FROM order_payments WHERE order_id=?",
                (order_id,),
            ).fetchone()[0]
            if paid + minor > due:
                raise ValueError("Payment exceeds the outstanding order balance")
            payment_id = "PAY-" + secrets.token_hex(6).upper()
            now = _now()
            db.execute(
                "INSERT INTO order_payments VALUES(?,?,?,?,?,?,?,?)",
                (payment_id, order_id, minor, currency, provider, reference, reviewer, now),
            )
            new_paid = paid + minor
            state = "paid" if new_paid == due else "partially_paid"
            db.execute("UPDATE orders SET state=?,updated_at=? WHERE order_id=?", (state, now, order_id))
            self._event(db, order_id, "payment_verified", {
                "payment_id": payment_id, "amount_minor": minor, "currency": currency,
                "provider": provider, "verified_by": reviewer, "paid_total_minor": new_paid,
                "balance_minor": due - new_paid,
            })
        return self.get_order(order_id)

    def update_fulfilment(self, order_id: str, state: str, operator: str,
                          evidence_reference: str = "") -> dict:
        allowed = {"preparing", "shipped", "received", "cancelled", "refunded"}
        if state not in allowed:
            raise ValueError("Unsupported fulfilment state")
        operator = str(operator).strip()
        evidence = str(evidence_reference).strip()
        if not operator:
            raise ValueError("Operator identity is required")
        with self._connect() as db:
            order = db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
            if not order:
                raise ValueError("Order not found")
            if state in {"preparing", "shipped", "received"} and order["state"] not in {
                "paid", "preparing", "shipped"
            }:
                raise ValueError("Full payment must be verified before fulfilment")
            if state == "shipped" and not evidence:
                raise ValueError("A carrier or shipment reference is required")
            if state == "received" and not evidence:
                raise ValueError("Receipt confirmation reference is required")
            now = _now()
            db.execute("UPDATE orders SET state=?,updated_at=? WHERE order_id=?", (state, now, order_id))
            self._event(db, order_id, "fulfilment_" + state, {
                "operator": operator, "evidence_reference": evidence,
            })
        return self.get_order(order_id)

    def get_order(self, order_id: str) -> dict:
        with self._connect() as db:
            row = db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
            if not row:
                raise ValueError("Order not found")
            payments = db.execute(
                "SELECT payment_id,amount_minor,currency,provider,provider_reference,verified_by,verified_at "
                "FROM order_payments WHERE order_id=? ORDER BY verified_at",
                (order_id,),
            ).fetchall()
            events = db.execute(
                "SELECT event_type,details_json,created_at FROM order_events WHERE order_id=? ORDER BY event_id",
                (order_id,),
            ).fetchall()
        item = dict(row)
        paid = sum(p["amount_minor"] for p in payments)
        due = item["base_price_minor"] + item["access_contribution_minor"]
        item.update({
            "paid_minor": paid, "balance_minor": due - paid,
            "payments": [dict(p) for p in payments],
            "events": [{**dict(e), "details": json.loads(e.pop("details_json"))} for e in events],
            "delivery_address_stored": False,
            "payment_provider_webhook_integrated": False,
        })
        item.pop("base_price_minor")
        item.pop("access_contribution_minor")
        return item

    def list_orders(self, limit: int = 100) -> dict:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self._connect() as db:
            ids = [r[0] for r in db.execute(
                "SELECT order_id FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
            )]
        return {"orders": [self.get_order(order_id) for order_id in ids],
                "personal_data_stored": False, "automatic_payment_confirmation": False}
