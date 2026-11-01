/* Future product acquisition policy.
 * No technology is currently offered for purchase through this configuration.
 * Configure a product only after development, safety/legal review and fulfilment readiness.
 * Do not publish buyer addresses or payment credentials in this file.
 */
window.SSSWET_PRODUCT_PURCHASES = Object.freeze({
  currency: "EUR",
  checkout_provider: null,
  research_contributions_are_product_payments: false,
  delivery_address_collection: "only_after_full_payment_cleared_and_order_accepted",
  delivery_confirmation_required_before_gmail_archiving: true,
  installment_plan: Object.freeze({
    enabled: false,
    base_price_unchanged: true,
    delivery_after_full_payment: true,
    schedule_requires_individual_written_offer: true
  }),
  one_time_public_access_contribution: Object.freeze({
    enabled: false,
    legal_review_required: true,
    not_a_statutory_tax: true,
    calculation: "product_specific_percentage_of_base_price",
    technology_rates: Object.freeze({
      cellular: null,
      longevity: null,
      armor: null,
      jetpack: null,
      translator: null,
      spacetime: null,
      timetravel: null
    })
  }),
  fair_access_policy: Object.freeze({
    required_before_product_launch: true,
    status: "not_defined",
    purpose: "Prevent allocation from being determined solely by ability to pay quickly."
  }),
  products: Object.freeze({
    cellular: Object.freeze({available:false,price_eur:null}),
    longevity: Object.freeze({available:false,price_eur:null}),
    armor: Object.freeze({available:false,price_eur:null}),
    jetpack: Object.freeze({available:false,price_eur:null}),
    translator: Object.freeze({available:false,price_eur:null}),
    spacetime: Object.freeze({available:false,price_eur:null}),
    timetravel: Object.freeze({available:false,price_eur:null})
  })
});
