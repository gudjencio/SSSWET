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

## 3. Bot-calculated provisional price and later official price

- The bots calculate and publish a **provisional monthly technology price** between USD 1 per monthly payment and a technology-specific maximum X. This is a research-financing estimate, not a guarantee that the technology will be completed, work as hoped or be delivered.
- X is calculated independently for each programme from traceable inputs: engineering and research hours, specialist review, materials, prototypes, testing, compute and infrastructure, safety and quality assurance, maintenance, fulfilment and other directly attributable costs. Missing inputs must be marked unknown rather than invented.
- The pricing agents must produce a costed baseline estimate, a low/base/high scenario, confidence level, assumptions, source references, estimate date and a breakdown of taxes and fees. The independent verifier checks arithmetic, source quality, duplicated costs and uncertainty. The agents may determine the price automatically only when these checks pass and all mandatory inputs exist; otherwise the system must withhold X and show that the estimate is incomplete.
- To keep the provisional amount only slightly above the best current estimate of the eventual official price, the bots may add a separate **uncertainty reserve**. It must be calculated from documented forecast uncertainty, not chosen arbitrarily, and capped at 10% of the pre-tax baseline. If uncertainty would require a larger reserve, the bots must not silently increase the price: they must mark the estimate as too uncertain and request more research. The reserve and its amount must be visible before payment.
- The **official price** is announced only when a specific technology has reached a real, validated and legally saleable product state, with verified specifications, safety/quality evidence, fulfilment capability and a final destination-aware tax calculation. A provisional research price must never be described as an official product price.
- When the official price is announced, the system calculates the uncertainty reserve actually collected from each customer's cleared payments for that technology. That amount becomes a customer-specific discount credit for future SSSWET technology purchases. Example: if the provisional pre-tax amount included USD 12 of reserve and the official price is later established, USD 12 is credited against the customer's next eligible technology purchase. The credit is never calculated from unpaid instalments, taxes, refunds or amounts not actually collected.
- Credits must be held in a private, auditable account ledger, shown to the customer, applied automatically to eligible new technology purchases, and never applied twice. If the balance exceeds the next purchase, the remainder carries forward. Refunds, chargebacks, cancellations, legal restrictions and tax corrections must adjust the ledger. Any mandatory cash refund or other statutory consumer remedy takes precedence over a store credit.
- Monthly payment amounts must be at least USD 1 and must not exceed the remaining agreed provisional funding amount for the selected technology. The customer must see and approve the exact amount, allocation and monthly schedule before each billing cycle. No automatic charge may exceed the amount expressly authorised.
- The published customer total must include all applicable taxes for the customer's destination. Taxes, payment fees, shipping, customs, project margin and the uncertainty reserve must be separately itemised. The USD 1 minimum is a minimum monthly payment, not a guaranteed USD 1 net profit.
- Repair or compensation costs may be charged only for a documented event where legally recoverable and expressly accepted. They are separate service/compensation line items, not taxes. Warranty repairs must remain free where required, and duplicate recovery is prohibited.

## 3A. Research outcome and delivery uncertainty

- Customers must be told prominently, before payment, that the funded work is experimental and may fail, be delayed, change scope or never produce a deliverable technology. A bot-generated feasibility score or estimate is not a promise, warranty or guarantee of success.
- The checkout must clearly state what the payment legally represents (for example, a research contribution or a separately reviewed crowdfunding/reward arrangement). It must not disguise a speculative contribution as an ordinary purchase of a product that does not yet exist.
- Each programme must publish milestones, progress evidence, material changes, spending allocation and a clear cancellation/refund route. Funds must not be represented as escrow or protected customer deposits unless the legal and payment arrangements genuinely provide that protection.
- A failure to achieve the research objective must trigger the published project-specific outcome process and applicable legal rights. No automatic forfeiture or blanket no-refund rule may override mandatory consumer law.

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
- A source-backed bot-generated price model, independent automated verification, disclosed uncertainty reserve and destination-aware tax calculation; estimates that fail checks must be withheld.
- Clear provisional/official price distinction, disclosed uncertainty and failure risk, itemised all-inclusive totals, exact recurring amount and private customer credit ledger.
- A separate PayPal plan or supported billing configuration for each valid price model.
- A secure backend, verified webhooks, refund reconciliation and private order management.
- Clear cancellation, withdrawal, warranty, repair and complaint procedures.
- A customer-facing statement of what is funded each month and how multiple selections are sequenced.
- Legal/accounting review for the seller's status, territory and product category.

Until every item is satisfied, the existing research contribution flow remains separate and all product availability flags stay disabled.
