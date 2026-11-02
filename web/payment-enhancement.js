(() => {
  "use strict";

  const MIN_CONTRIBUTION = 1;
  const links = window.SSSWET_DONATION_LINKS || {};

  const install = () => {
    const amount = document.getElementById("donation-amount");
    const checkout = document.getElementById("donation-checkout");
    const status = document.getElementById("donation-payment-status");
    if (!amount || !checkout || !status) return;

    amount.min = String(MIN_CONTRIBUTION);
    amount.value = String(Math.max(MIN_CONTRIBUTION, Number(amount.value) || 0));

    const minimumNote = document.getElementById("donation-minimum-note") || (() => {
      const note = document.createElement("p");
      note.id = "donation-minimum-note";
      note.className = "donation-note";
      amount.closest(".donation-fields")?.append(note);
      return note;
    })();
    minimumNote.textContent = document.documentElement.lang?.startsWith("fr")
      ? "Contribution minimale : 1 dollar américain ou l’équivalent affiché."
      : "Minimum contribution: USD 1 or the displayed equivalent.";

    if (checkout.dataset.dynamicPaymentInstalled === "true") return;
    checkout.dataset.dynamicPaymentInstalled = "true";

    checkout.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      const value = Number(amount.value);
      if (!Number.isFinite(value) || value < MIN_CONTRIBUTION) {
        status.textContent = document.documentElement.lang?.startsWith("fr")
          ? "Le montant minimum est de 1 dollar américain ou son équivalent affiché."
          : "The minimum contribution is USD 1 or the displayed equivalent.";
        return;
      }

      const rounded = Math.round(value * 100) / 100;
      const custom = links.PAYPAL_ME;
      if (typeof custom === "string" && /^https:\/\/www\.paypal\.com\/paypalme\/gudjencio\/?$/i.test(custom)) {
        const currency = (document.getElementById("donation-currency")?.textContent || "USD").trim().toUpperCase();
        const suffix = currency === "USD" ? String(rounded) : String(rounded) + currency;
        const url = custom.replace(/\/$/, "") + "/" + encodeURIComponent(suffix);
        window.open(url, "_blank", "noopener,noreferrer");
        status.textContent = document.documentElement.lang?.startsWith("fr")
          ? "Ouverture de PayPal avec le montant choisi."
          : "Opening PayPal with the amount you selected.";
        return;
      }

      status.textContent = document.documentElement.lang?.startsWith("fr")
        ? "Aucun moyen de paiement PayPal configuré pour ce montant."
        : "No PayPal payment method is configured for this amount.";
    }, true);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", install, { once: true });
  else install();
})();
