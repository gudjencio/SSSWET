# Technology pricing and access policy

SSSWET research contributions and future product sales are separate financial activities. Contributions currently support research; they do not purchase a technology, create ownership rights, or guarantee delivery.

## Equal-access payment principle

If a technology is eventually developed, independently assessed, legally marketable and offered for sale, its published base price will be the same regardless of payment schedule.

- **One-time payment:** a technology-specific solidarity surcharge may be added to the base price. The rate must be explicitly approved and published for that technology before checkout.
- **Instalments:** interest-free instalments carry no solidarity surcharge. The sum of instalments equals the published base price; no hidden finance charge is added.
- The final instalment absorbs any rounding remainder so the displayed schedule adds up exactly.
- Every quote must show the base price, surcharge (if any), total price, number of instalments and each payment amount before the buyer confirms.
- The surcharge is intended to fund broader access, shared research infrastructure and affordability measures. It is not represented as a government tax or statutory levy.
- No rate, product price, payment schedule or product availability is presumed. A missing approved rate means no commercial quote should be issued.

## Current implementation boundary

The pricing calculator is a policy and calculation component only. It does not activate product sales, charge a payment method, determine tax obligations, or change the existing research-contribution flow. Commercial activation requires a real product, an approved technology-specific rate, jurisdictional legal and tax review, consumer terms, and a verified checkout integration.

## Calculation rules

For a one-time purchase:

`total = base price + (base price × approved technology rate)`

For instalments:

`total = base price`

`surcharge = 0`

The calculator uses decimal arithmetic and rounds to cents. Any remainder is assigned to the final instalment.
