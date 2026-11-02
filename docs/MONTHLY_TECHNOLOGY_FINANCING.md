# Monthly technology financing and fulfilment policy

**Status: proposed design — not enabled for checkout.**

This policy describes a possible monthly financing flow for future, genuinely developed and deliverable SSSWET products. It does not make any research programme available for purchase, establish a current price, or create a promise of delivery.

## 1. Research support and product purchases are separate

- A voluntary contribution to research, infrastructure or platform operations is not a product purchase and does not reserve a technology.
- A product-financing agreement may only be offered for a specific item that exists, has passed appropriate technical, safety, quality and legal review, and can actually be supplied.
- The checkout must identify which of these two transaction types is being entered into before the customer pays. They must never be conflated.

## 2. Monthly subscription and technology selection

The proposed customer journey is:

1. The customer selects one or more eligible technologies.
2. The interface displays each technology's itemised price, the applicable tax treatment, the all-inclusive total, the monthly amount, the expected funding sequence and any delivery conditions before approval.
3. One PayPal monthly subscription button is used for the selected monthly plan. The customer must see and approve the exact recurring amount and frequency in PayPal before the subscription starts.
4. The financing queue processes **no more than one technology per monthly billing period**, even if several technologies have been selected.
5. If multiple technologies are selected, their totals are added to the customer's financing plan and the interface displays the sequence and expected number of billing periods. It must not silently charge the full combined total in one month unless the customer has expressly selected and approved that amount.
6. At each renewal, the customer is invited to keep the same technology, change the selection, add or remove a future priority, or cancel. A change must be confirmed before it changes a future charge.
7. If one technology's all-inclusive price is fully paid during the first billing period, the next renewal may finance another agreed unit or another technology. The interface must explicitly state which technology and amount the next renewal will fund; it must never imply that a completed price automatically authorises an undisclosed repeat charge.
8. The customer is reminded how to cancel before the next renewal. Cancellation stops future recurring charges; it does not erase rights attached to payments already collected.

The project owner's intended operating rule is one technology funded per monthly period, including when the customer initially selects only one technology. The actual payment schedule, allocation order and what happens when a technology is fully funded must be shown clearly in the order summary.

## 3. Monthly amount and technology price (USD 1 minimum to X maximum)

- The customer's monthly payment must be at least **USD 1** and may not exceed **X**, where X is the approved, all-inclusive price of the specific technology or the remaining balance due for that technology. The amount charged in any month must be displayed and expressly approved before the billing cycle begins.
- X is not a universal fixed ceiling. It is calculated separately for each genuinely deliverable technology from a documented estimate of the work and resources required: research and engineering hours, specialist review, materials, prototypes, testing, compute and infrastructure, safety and quality assurance, maintenance, fulfilment and other directly attributable costs.
- Research bots may prepare estimates, compare scenarios, identify missing cost inputs and explain uncertainty. Their estimates must be source-linked, reproducible where possible, independently checked and labelled with confidence and assumptions. Bots must not invent labour rates, supplier quotes, tax rates or completed work, and must not autonomously publish or charge a price. A responsible human review must approve the final X and its supporting calculation.
- The published customer price must show the applicable taxes and be **TTC / all-inclusive** for the destination and transaction. Tax is determined from the actual product or service classification, seller status, customer location, delivery destination and applicable law. There is no single worldwide tax rate that can safely be added to every technology.
- For EU consumer sales, destination-based VAT and the applicable scheme may apply to cross-border transactions. The correct treatment must be reviewed for the seller and each product/service category before launch.
- Any platform margin, operating charge or project contribution must be disclosed as a price component, not disguised as a statutory tax. The USD 1 minimum is a minimum monthly payment, not a guaranteed USD 1 net profit or margin.
- Repair, restoration or compensation amounts may be included in the maximum amount due only when a specific, documented event makes them applicable and they are legally recoverable. They must appear as separate, itemised line items, with their own applicable taxes shown separately. Repair or compensation costs are not themselves taxes and must never be labelled as such. No charge may be imposed for a repair covered by a statutory or express warranty; no duplicate recovery is allowed.
- Prices, tax rules, currency conversion, payment-provider fees, shipping, customs and import charges must be modelled separately. Where the final landed cost cannot be guaranteed, the offer must state that limitation before the order is placed.

## 4. Changes of mind, cancellation and refunds

- Customers may request cancellation of future subscription renewals at any time through a clear, accessible route. The project should also provide a direct cancellation contact and confirmation.
- Before fulfilment, a customer may ask to cancel an order and request a refund, or may expressly choose to leave the amount as a voluntary contribution to the platform, servers and research. Retaining money as a contribution requires a separate, affirmative and recorded choice; it must never be the default substitute for a refund.
- Applicable statutory withdrawal, refund, conformity, warranty and consumer-protection rights always prevail over this voluntary policy. A blanket "no refunds after delivery" rule must not be published or implemented.
- For distance sales to consumers in France, a statutory withdrawal period generally applies to goods and services, subject to specific legal exceptions and conditions. The customer must be given the required pre-contract information and withdrawal process.
- If the customer has already received a product, any withdrawal, return, refund or deduction must be assessed under the rules applicable to that specific product and transaction. A product being delivered does not automatically remove all statutory rights.
- Refunds must be processed through the original payment method where required, with an auditable payment-provider reference and a customer notification.

## 5. Repairs and repeat purchases

- Defects covered by a statutory guarantee or an express project warranty must be remedied without charging the customer for the covered repair. A later purchase must not be used to recover costs that the project is legally or contractually required to bear.
- For damage or repair work outside those guarantees, the customer must receive a diagnosis and an itemised quote before authorising any paid repair.
- Any optional repair-cost contribution must reflect documented, reasonable repair costs. It is a service charge, **not a tax**.
- A proposed minimum charge of USD 1 may only be used if lawful, proportionate, clearly disclosed in advance and accepted by the customer. It must not be stacked repeatedly or used to recover the same repair cost twice.
- If the same customer later buys the same technology again, any unpaid, previously disclosed repair charge may only be collected if it is still legally recoverable, itemised and expressly accepted. The checkout must show whether the repair amount is being paid in one instalment or several; the total must be identical whichever permitted payment schedule is chosen, except for separately disclosed lawful costs.
- Repairs covered by warranty remain free regardless of a repeat purchase.

## 6. Payment provider and technical safeguards

- PayPal subscriptions are recurring authorisations, not a generic instalment ledger. The exact plan price, billing frequency, quantity support, cancellation behaviour, payment failures and customer consent must be verified against the live PayPal plan and API before enabling checkout.
- The existing public plan ID is configured for the current research-contribution flow. It must not be repurposed for product sales or variable technology prices without a separate verified PayPal product/plan configuration.
- A browser-only interface cannot securely establish authoritative payment status, refunds, customer identity, tax calculations, subscription changes or delivery eligibility. These operations require a protected server-side integration, verified PayPal webhooks, idempotent event handling and a private order ledger.
- Never collect, store or commit payment credentials, customer addresses, identity documents or private order records in the public repository.
- Never dispatch or mark a product as paid from a browser success callback alone. Verify provider-side capture and settlement first.
- Checkout remains disabled until the product, tax, consumer terms, PayPal plan, server-side webhook handling, refund workflow, customer support process and fulfilment capability have all passed review.

## 7. Launch checklist

Before any product checkout is activated, the project must have:

- A real product, specification, safety evidence and fulfilment process.
- A reviewed, bot-assisted and independently checked cost estimate for each technology, human approval of X, and a country-aware calculation of all applicable taxes.
- Clear all-inclusive prices and the exact recurring amount shown before approval.
- A separate PayPal plan or supported billing configuration for each valid price model.
- A secure backend, verified webhooks, refund reconciliation and private order management.
- Clear cancellation, withdrawal, warranty, repair and complaint procedures.
- A customer-facing statement of what is funded each month and how multiple selections are sequenced.
- Legal/accounting review for the seller's status, territory and product category.

Until every item is satisfied, the existing research contribution flow remains separate and all product availability flags stay disabled.
