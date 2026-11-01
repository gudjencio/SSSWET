/* Official project contribution destination.
 * Visitors select a suggested amount in the interface and confirm the final
 * amount and available currency directly on PayPal.
 * No API keys, passwords, private tokens or webhook secrets belong here.
 */
window.SSSWET_DONATION_LINKS = {
  PAYPAL: "https://www.paypal.com/paypalme/gudjencio"
};

/*
 * Public research portfolio. Update only after a payment is confirmed and
 * reliably attributed. PayPal.Me does not sync payments to this static site.
 * Unknown amounts and targets remain null; never estimate or invent them.
 */
window.SSSWET_RESEARCH_PORTFOLIO = {
  cellular:   { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  longevity:  { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  armor:      { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  jetpack:    { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  translator: { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  spacetime:  { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null },
  timetravel: { funding_goal_eur: null, confirmed_contributions_eur: null, stage: "planning", prototype: false, availability: "not_available", last_updated: null }
};
