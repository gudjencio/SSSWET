# Private order register

The order register is a local operator tool for a future product offer. It is separate from public research contributions and from the public research journal.

## Data boundary

The SQLite register stores order identifiers, technology identifiers, currency, agreed price components, manually verified payment references, operator labels and fulfilment milestones. It deliberately does **not** store customer names, email addresses, delivery addresses, payment credentials or identity documents.

The register is not published by GitHub Pages and must never be copied into the public repository. Its default database path is `.ssswet/orders.sqlite3`; keep this directory private and protected by operating-system account permissions and encrypted device storage.

## Payment reconciliation

Only an operator-confirmed payment can be recorded. A screenshot, customer statement, payment initiation or return URL is not proof of settlement. The operator must independently verify the transaction in the payment provider's authoritative account records and enter its unique transaction reference. Duplicate provider references, currency mismatches and overpayments are rejected.

No provider webhook or automatic PayPal reconciliation is implemented. Do not automate order fulfilment until a payment provider integration can authenticate notifications, verify signatures, reconcile amounts/currency/order references and handle refunds and chargebacks.

## Order lifecycle

`awaiting_payment → partially_paid → paid → preparing → shipped → received`

Fulfilment cannot begin before the full accepted balance is verified. Shipment and receipt transitions require evidence references. These references are audit pointers, not independent proof by themselves.

## Delivery address

No address field or address endpoint exists in this module. Collect a delivery address only after a real product offer is lawful, available, accepted and fully paid. Use a separate access-controlled fulfilment provider or encrypted private workflow. Never add addresses to GitHub, this SQLite register, public APIs, research records or public contribution reports. Apply data minimisation, retention limits and applicable privacy/consumer laws.

## Local API

The local server exposes the registry only to loopback clients:
- `GET /api/private/orders`
- `GET /api/private/orders/<order_id>`
- `POST /api/private/orders`
- `POST /api/private/orders/<order_id>/payments`
- `POST /api/private/orders/<order_id>/fulfilment`

The local HTTP server is not an authentication system. Keep it bound to `127.0.0.1`; do not expose it to a LAN, reverse proxy or public internet. Add authenticated operator access and CSRF protection before any remote administration.

This is an operational ledger prototype, not a payment processor, legal compliance certification or production order-management system. Product sales remain disabled until payment, allocation, safety, consumer, privacy, tax and fulfilment requirements are reviewed.
