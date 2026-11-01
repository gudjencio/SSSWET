# Research contributions and future technology availability

SSSWET invites voluntary contributions to support ongoing research and development across its technology priorities.

## Research contributions

The technology catalogue describes research ambitions, not products currently available for sale. Contributors can select a research theme and open the contribution dialog. The interface displays an indicative minimum equivalent to EUR 0.50, using the visitor's browser region and an exchange-rate estimate where available.

Research contributions are redirected to the project's PayPal.Me page:

https://www.paypal.com/paypalme/gudjencio

The visitor must enter and confirm the desired amount and an available currency on PayPal. The amount shown in the SSSWET interface is an estimate and is not transferred automatically to PayPal. PayPal's checkout is authoritative for accepted currencies, fees, conversion and payment confirmation.

Contributors may make multiple separate payments. Each payment is an independent transaction. A contribution supports research and development; it is not a purchase of an existing technology and does not guarantee that a research objective will succeed.

## Future technology purchases and delivery

Research support and product purchases are separate transactions. A research contribution does not reserve a product, create a purchase contract or guarantee delivery.

A technology may be offered for purchase only after it has actually been developed, assessed as technically realizable, tested to an appropriate standard, reviewed for safety and legal compliance, and made available under clear product terms. The project must be capable of manufacturing or procuring, quality-checking, supporting and lawfully delivering the specific product before accepting an order.

When a product is genuinely available, the buyer will receive a separate itemized offer identifying the technology, specification, total price, any legally applicable taxes, payment options, estimated lead time, delivery terms, warranty, support, limitations and refund/cancellation conditions. No product price, tax rate, delivery date or technical capability is promised before that offer exists.

### Instalments and the proposed one-time purchase contribution

The intended policy is to let an ordinary buyer pay the same base product price in several clearly disclosed instalments, with delivery only after the full agreed amount has been received and verified. A buyer who chooses to pay the entire amount at once may be charged an additional, technology-specific public-access contribution. Its amount would be calculated in relation to the price and documented cost/access characteristics of that particular product, and disclosed before payment.

This additional amount is **not described as a tax** unless a competent authority confirms that it is a tax legally due. A private project cannot create a statutory tax by naming it one. Until the applicable legal, consumer-protection, tax and payment-provider requirements have been reviewed, no surcharge is active and no surcharge rate is published. Any final pricing policy must be transparent, proportionate, lawful, and must not disguise interest, a credit charge or a compulsory donation.

A payment split must not increase the buyer's total base product price merely because the buyer needs more time. The exact instalment schedule, missed-payment handling, cancellation and refund rights must be included in the offer. No financing or credit arrangement will be offered without the required legal and regulatory review.

The project also intends to prevent early access from being determined solely by wealth. Before a product launch, the project must publish a fair allocation and release policy (for example, equal-access release windows or capped allocation rounds). A one-time surcharge alone cannot guarantee equal access or prevent a wealthy buyer from obtaining a product first.

### Delivery address and fulfilment

A delivery address is requested only after the specific product is genuinely available, the buyer has accepted the final offer, and the full purchase amount has been received and reconciled. Address details are private fulfilment information: they must never be placed in the public repository, public research journal, public contribution ledger or a public issue.

The address is used only for lawful fulfilment, shipping and necessary support. Access is restricted to authorized personnel and service providers who need it. Retention and deletion follow applicable legal, accounting, consumer and shipping obligations; personal data must not be deleted where the law requires it to be retained.

An address being supplied does not itself prove that payment has cleared or that a product has been delivered. Delivery is complete only after the carrier or other appropriate fulfilment evidence has been checked and the buyer's receipt has been confirmed or otherwise established under the published terms.

## Continuing ambition

One of the project's central goals is to make ambitious technologies possible. SSSWET intends to keep researching, testing, learning, revising failed approaches and trying again, continuously and responsibly. This ambition is not a claim that every technology can be achieved. Hypotheses, simulations, prototypes, independently reviewed results and deliverable products remain distinct.

## Public research portfolio and progress records

The technology cards display a public status for each research direction: current research stage, confirmed contributions attributed to that direction, a funding goal when formally set, whether a prototype has been publicly recorded, and whether a resulting technology is available.

The portfolio is configured in `web/donation-config.js`. Unknown amounts and unset targets remain `null` and are displayed as unpublished or not set. They must not be replaced with invented zeroes, estimates or targets. A funding progress percentage is displayed only when both a confirmed amount and a positive target are published.

### Updating the public ledger

PayPal.Me does not automatically send payment confirmations or transaction details to this static website. The project operator must update the public ledger manually after checking PayPal's transaction record and attributing the contribution to a technology. Update only aggregate totals; do not publish donor names, email addresses, transaction IDs or other personal payment details.

For each technology, update `confirmed_contributions_eur` with confirmed aggregate contributions attributed to that research theme, `funding_goal_eur` with an approved public target or `null`, `stage` with one of `planning`, `literature_review`, `feasibility`, `prototype`, `validation` or `available`, `prototype` with `true` only when a real prototype has been recorded, `availability` with `available` only when genuinely available under separately published terms, and `last_updated` with the latest review date in ISO format (`YYYY-MM-DD`) or `null`.

A prototype, simulation, research paper or concept does not by itself establish a working or deliverable product. Availability must be reviewed separately, including technical feasibility, safety, legal compliance and delivery capability.

## Research progress journal

SSSWET maintains an append-only research journal for dated programme updates. Entries identify the relevant technology, update type, status, evidence classification, references and author label. The journal is available through the local research engine at `GET /api/research-journal`; local operators can add entries through `POST /api/research-journal`. Writes are restricted to the local machine.

Each entry includes a SHA-256 digest linked to the preceding entry. The integrity report checks whether the recorded sequence has been altered. A valid hash chain demonstrates record integrity only; it does not authenticate the author, independently verify a source, establish scientific validity or prove that a reported prototype works. Do not place personal donor data, delivery addresses, credentials or private information in journal entries.

## Technology Feasibility Observatory

The local research engine exposes a read-only evidence-led overview through `GET /api/technology-feasibility`. It identifies recorded research maturity and missing review areas for all 29 technology themes. It does not calculate an unsupported feasibility score, establish product readiness or authorize delivery. See [the observatory documentation](TECHNOLOGY_FEASIBILITY_OBSERVATORY.md).

## Payment and privacy

Research contributions use the public PayPal.Me destination. PayPal.Me is not an order-management or instalment-reconciliation integration. Product purchases will require a separate itemized checkout or invoice mechanism that can identify the order, exact amount, currency and payment status. No order or delivery workflow is activated until that mechanism is configured and tested.

Never commit passwords, API secrets, private tokens, Gmail credentials, banking credentials, payment webhook signing keys, donor records or delivery addresses to this public repository. Gmail administration is provided as a separate, owner-restricted Google Apps Script project. It creates drafts but never sends messages automatically, and it only moves a labelled email to Gmail Trash after explicit confirmation that both payment and delivery have been verified.
