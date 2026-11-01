# Configuring voluntary contributions

The technology catalogue and contribution dialog are public-facing interface components. Payment collection is deliberately disabled until the project operator configures official hosted checkout links.

1. Create a hosted, variable-amount contribution page with a regulated payment provider.
2. Configure the provider to accept the relevant currency and a minimum amount no higher than the equivalent of EUR 0.50.
3. Add the verified HTTPS payment URL to `web/donation-config.js`, keyed by ISO 4217 currency code (for example, `EUR`, `USD`, `GBP` or `CAD`).
4. Verify the payment page, legal disclosures, refund policy, recipient identity and currency handling before publishing the link.

Example structure (replace the example URL with a real provider-issued link):

```js
window.SSSWET_DONATION_LINKS = {
  EUR: "https://buy.stripe.com/your_verified_eur_link",
  USD: "https://buy.stripe.com/your_verified_usd_link"
};
```

Do not add secret API keys, private tokens, bank credentials or webhook signing secrets to this public repository. The browser detects a likely currency from the visitor's regional browser setting and uses a public exchange-rate feed for an indicative EUR 0.50 minimum conversion. If conversion is unavailable, the interface falls back to EUR. The payment provider's checkout page remains authoritative for the final amount and accepted currency.

Each checkout opens one separate contribution. Visitors may return and make additional contributions; the interface does not claim to bundle multiple payments into one transaction.
