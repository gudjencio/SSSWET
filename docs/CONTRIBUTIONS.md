# Research contributions and future technology availability

SSSWET invites voluntary contributions to support ongoing research and development across its technology priorities.

## Current contributions

The technology catalogue describes research ambitions, not products currently available for sale. Contributors can select a research theme and open the contribution dialog. The interface displays an indicative minimum equivalent to EUR 0.50, using the visitor's browser region and an exchange-rate estimate where available.

Payments are redirected to the project's PayPal.Me page:

https://www.paypal.com/paypalme/gudjencio

The visitor must enter and confirm the desired amount and an available currency on PayPal. The amount shown in the SSSWET interface is an estimate and is not transferred automatically to PayPal. PayPal's checkout is authoritative for accepted currencies, fees, conversion and payment confirmation.

Contributors may make multiple separate payments. Each payment is an independent transaction. A contribution supports research and development; it is not a purchase of an existing technology and does not guarantee that a research objective will succeed.

## Future products and delivery

If a research direction eventually results in a technology that is scientifically, technically, legally and safely feasible, and a product is actually developed and made available, SSSWET may announce a separate acquisition and delivery offer for interested contributors.

Any such offer must specify availability, eligibility, price (if applicable), delivery conditions, timelines, limitations, warranties and refund terms before a contributor accepts it. A contribution alone does not create an automatic entitlement to a future device, product, service or delivery. No delivery date or technical capability is promised in advance.

## Continuing ambition

The project's purpose is to keep investigating, testing, learning and improving in a sustained effort to make ambitious technologies possible. Research hypotheses, simulations, prototypes and independently verified capabilities must remain clearly distinguished.

## Payment and privacy

The public repository contains only the public PayPal.Me destination. It must never contain passwords, API secrets, private tokens, banking credentials or webhook signing keys. Donors should complete payments only on the official PayPal domain and retain their transaction confirmation.


## Public research portfolio and progress records

The technology cards display a public status for each research direction: current research stage, confirmed contributions attributed to that direction, a funding goal when formally set, whether a prototype has been publicly recorded, and whether a resulting technology is available.

The portfolio is configured in `web/donation-config.js`. Unknown amounts and unset targets remain `null` and are displayed as unpublished or not set. They must not be replaced with invented zeroes, estimates or targets. A funding progress percentage is displayed only when both a confirmed amount and a positive target are published.

### Updating the public ledger

PayPal.Me is a simple account redirection and does not automatically send payment confirmations or transaction details to this static website. The portfolio therefore does not claim real-time payment synchronization. The project operator must update the public ledger manually after checking PayPal's transaction record and attributing the contribution to a technology. Update only aggregate totals; do not publish donor names, email addresses, transaction IDs or other personal payment details.

For each technology, update `confirmed_contributions_eur` with confirmed aggregate contributions attributed to that research theme, `funding_goal_eur` with an approved public target or `null`, `stage` with one of `planning`, `literature_review`, `feasibility`, `prototype`, `validation` or `available`, `prototype` with `true` only when a real prototype has been recorded, `availability` with `available` only when genuinely available under separately published terms, and `last_updated` with the latest review date in ISO format (`YYYY-MM-DD`) or `null`.

A prototype, simulation, research paper or concept does not by itself establish a working or deliverable product. Availability must be reviewed separately, including technical feasibility, safety, legal compliance and delivery capability.
