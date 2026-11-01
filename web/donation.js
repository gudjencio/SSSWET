(() => {
  "use strict";

  const technologies = {
    cellular: {
      en: ["Cellular enhancement", "Research into cell repair, regenerative biology, resilience and safe measurement. This theme is exploratory and does not imply that human enhancement is currently possible."],
      fr: ["Améliorations cellulaires", "Recherche sur la réparation cellulaire, la biologie régénérative, la résilience et leur mesure sûre. Ce thème reste exploratoire et ne signifie pas qu'une amélioration humaine soit actuellement possible."]
    },
    longevity: {
      en: ["Healthy longevity", "Evidence-led research into healthy ageing, prevention, cellular maintenance and quality of life."],
      fr: ["Longévité en bonne santé", "Recherche fondée sur les preuves concernant le vieillissement en bonne santé, la prévention, le maintien cellulaire et la qualité de vie."]
    },
    armor: {
      en: ["Advanced protective suits", "Research into protective materials, ergonomics, mobility, thermal comfort and human safety."],
      fr: ["Armures et équipements de protection", "Recherche sur les matériaux protecteurs, l'ergonomie, la mobilité, le confort thermique et la sécurité humaine."]
    },
    jetpack: {
      en: ["Personal propulsion", "High-level study of propulsion concepts, energy efficiency, control systems and operational safety."],
      fr: ["Jetpacks et propulsion individuelle", "Étude générale des concepts de propulsion, de l'efficacité énergétique, du contrôle et de la sécurité opérationnelle."]
    },
    translator: {
      en: ["Human–alien translation", "Long-term research into bidirectional communication, unknown languages, signal interpretation and uncertainty-aware translation."],
      fr: ["Traducteurs humains–extraterrestres", "Recherche à long terme sur la communication bidirectionnelle, les langues inconnues, l'interprétation des signaux et la traduction tenant compte de l'incertitude."]
    },
    spacetime: {
      en: ["Space-warping physics", "Theoretical and mathematical exploration of spacetime models, with no claim of practical propulsion or controllable warping."],
      fr: ["Physique de la déformation de l'espace-temps", "Exploration théorique et mathématique de modèles d'espace-temps, sans prétendre disposer d'une propulsion pratique ni d'une déformation contrôlable."]
    },
    timetravel: {
      en: ["Time travel research", "Exploratory study of time, causality, relativity, spacetime geometry and the mathematical limits of proposed temporal models. This is a long-term research ambition, not an available capability."],
      fr: ["Voyage dans le temps", "Étude exploratoire du temps, de la causalité, de la relativité, de la géométrie de l'espace-temps et des limites mathématiques des modèles temporels proposés. Il s'agit d'une ambition de recherche à long terme, pas d'une capacité disponible."]
    }
  };

  window.SSSWET_TECHNOLOGIES = technologies;
  // Configure only official, verified payment links here. No payment credentials belong in this public file.
  const paymentLinks = window.SSSWET_DONATION_LINKS || {};
  const currencyByRegion = {
    US:"USD", CA:"CAD", GB:"GBP", CH:"CHF", JP:"JPY", CN:"CNY", IN:"INR", AU:"AUD", NZ:"NZD",
    BR:"BRL", MX:"MXN", SG:"SGD", HK:"HKD", KR:"KRW", ZA:"ZAR", NG:"NGN", KE:"KES",
    SE:"SEK", NO:"NOK", DK:"DKK", PL:"PLN", CZ:"CZK", HU:"HUF", RO:"RON", BG:"BGN",
    TR:"TRY", IL:"ILS", AE:"AED", SA:"SAR", TH:"THB", ID:"IDR", MY:"MYR", PH:"PHP",
    VN:"VND", UA:"UAH", IS:"ISK", FR:"EUR", DE:"EUR", ES:"EUR", IT:"EUR", PT:"EUR",
    NL:"EUR", BE:"EUR", IE:"EUR", AT:"EUR", FI:"EUR", GR:"EUR", LU:"EUR", EE:"EUR",
    LV:"EUR", LT:"EUR", SK:"EUR", SI:"EUR", CY:"EUR", MT:"EUR"
  };
  const rates = { EUR: 1 };
  const modal = document.getElementById("technology-dialog");
  const grid = document.getElementById("technology-grid");
  if (!modal || !grid) return;
  const title = document.getElementById("technology-dialog-title");
  const description = document.getElementById("technology-dialog-description");
  const amountInput = document.getElementById("donation-amount");
  const currencyLabel = document.getElementById("donation-currency");
  const perOutput = document.getElementById("donation-per");
  const totalOutput = document.getElementById("donation-total");
  const currencyNote = document.getElementById("donation-currency-note");
  const paymentStatus = document.getElementById("donation-payment-status");
  const checkout = document.getElementById("donation-checkout");
  const copyButton = document.getElementById("donation-copy");
  const translations = {
    en: { eyebrow:"FUTURE TECHNOLOGIES · RESEARCH PRIORITIES", title:"Choose a technology to support", intro:"Explore the research directions and open a contribution window for the technology you want to encourage.", disclaimer:"These are research themes, not claims that the technologies exist or are currently achievable. The project will keep exploring, testing and refining ideas in an ongoing effort to make them possible. Contributions fund research and development; they are not a purchase or a guarantee of results. If a technology becomes feasible and a product is actually developed, a future offer and delivery terms will be communicated separately.", explore:"Explore & contribute", dialogEyebrow:"FUND RESEARCH & DEVELOPMENT", amountLabel:"Suggested contribution amount", repeatLabel:"Number of separate contributions", perContribution:"Contribution amount", totalLabel:"Summary", currencyNote:"Currency is estimated from your browser's regional settings. The suggested minimum is the equivalent of €0.50.", paymentMissing:"The PayPal contribution link is unavailable.", paymentReady:"Continue to the project PayPal page. Confirm the amount and currency there.", checkout:"Continue to PayPal", copySummary:"Copy research contribution summary", paymentDisclaimer:"Your contribution supports ongoing research, not an existing product purchase. You may contribute again as often as you wish; each payment is separate. PayPal opens the project account page: enter and confirm your chosen amount and available currency there. If a technology is eventually developed and made available, any future purchase and delivery offer will be announced separately with its own terms.", invalid:"Enter at least the equivalent of €0.50.", copied:"Contribution summary copied.", copyError:"Unable to copy automatically. Please select and copy the summary." },
    fr: { eyebrow:"TECHNOLOGIES DU FUTUR · PRIORITÉS DE RECHERCHE", title:"Choisissez une technologie à soutenir", intro:"Découvrez les axes de recherche et ouvrez une fenêtre de contribution pour la technologie que vous souhaitez encourager.", disclaimer:"Ces axes ne signifient pas que les technologies existent ou soient réalisables aujourd'hui. Le projet poursuivra continuellement les recherches, les essais et les améliorations pour tenter de les rendre possibles. Les contributions financent la recherche et le développement ; elles ne constituent pas un achat et ne garantissent aucun résultat. Si une technologie devient réalisable et qu'un produit est effectivement développé, une offre et des conditions de livraison seront communiquées séparément.", explore:"Découvrir et contribuer", dialogEyebrow:"FINANCER LA RECHERCHE ET LE DÉVELOPPEMENT", amountLabel:"Montant indicatif de la contribution", repeatLabel:"Nombre de contributions distinctes", perContribution:"Montant de la contribution", totalLabel:"Récapitulatif", currencyNote:"La devise est estimée à partir des paramètres régionaux du navigateur. Le minimum indicatif est l'équivalent de 0,50 €.", paymentMissing:"Le lien de contribution PayPal est indisponible.", paymentReady:"Vous allez accéder à la page PayPal du projet. Confirmez-y le montant et la devise.", checkout:"Continuer vers PayPal", copySummary:"Copier le récapitulatif du financement", paymentDisclaimer:"Votre contribution finance les recherches en cours, et non l'achat d'un produit existant. Vous pouvez contribuer autant de fois que vous le souhaitez ; chaque paiement est distinct. PayPal ouvre la page du compte du projet : saisissez et confirmez le montant choisi et une devise acceptée. Si une technologie est un jour développée et disponible, une éventuelle offre d'achat et de livraison sera annoncée séparément, avec ses propres conditions.", invalid:"Saisissez au moins l'équivalent de 0,50 €.", copied:"Récapitulatif copié.", copyError:"Copie automatique impossible. Veuillez sélectionner et copier le récapitulatif." }
  };
  const copy = () => translations[(document.documentElement.lang || "en").startsWith("fr") ? "fr" : "en"];
  let selectedTechnology = null;
  let currency = "EUR";
  let minimumLocal = 0.50;
  let rateReady = false;

  function localeRegion() {
    try { return new Intl.Locale(navigator.language || "en").region || ""; } catch (_) { return ""; }
  }
  function formatMoney(value) {
    try { return new Intl.NumberFormat(navigator.language || "en", { style:"currency", currency, minimumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2, maximumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2 }).format(value); }
    catch (_) { return value.toFixed(2) + " " + currency; }
  }
  function updateAmounts() {
    const amount = Number(amountInput.value);
    const valid = Number.isFinite(amount) && amount >= minimumLocal;
    perOutput.textContent = Number.isFinite(amount) ? formatMoney(amount) : "—";
    totalOutput.textContent = valid ? formatMoney(amount) : "—";
    const paymentConfigured = typeof paymentLinks.PAYPAL === "string" && /^https:\/\/www\.paypal\.com\/paypalme\/gudjencio\/?$/i.test(paymentLinks.PAYPAL);
    checkout.disabled = !valid || !paymentConfigured;
    paymentStatus.textContent = valid ? (paymentConfigured ? copy().paymentReady : copy().paymentMissing) : copy().invalid;
  }
  async function chooseCurrency() {
    const region = localeRegion();
    currency = currencyByRegion[region] || "EUR";
    currencyLabel.textContent = currency;
    if (currency !== "EUR") {
      try {
        const response = await fetch("https://open.er-api.com/v6/latest/EUR", { cache:"no-store" });
        if (!response.ok) throw new Error("Exchange-rate service unavailable");
        const data = await response.json();
        const rate = Number(data.rates && data.rates[currency]);
        if (!Number.isFinite(rate) || rate <= 0) throw new Error("Exchange rate unavailable");
        rates[currency] = rate;
        const fractionDigits = ["JPY", "KRW"].includes(currency) ? 0 : 2;
        minimumLocal = Math.ceil((0.5 * rate) * Math.pow(10, fractionDigits)) / Math.pow(10, fractionDigits);
        amountInput.min = String(minimumLocal);
        amountInput.step = fractionDigits === 0 ? "1" : "0.01";
        rateReady = true;
        currencyNote.textContent = copy().currencyNote + " " + (copy() === translations.fr ? "Taux indicatif actualisé ; le montant final dépend du prestataire de paiement." : "Indicative live exchange rate; the final amount depends on the payment provider.");
      } catch (_) {
        currency = "EUR";
        minimumLocal = 0.50;
        amountInput.min = "0.50";
        amountInput.step = "0.01";
        currencyLabel.textContent = currency;
        currencyNote.textContent = copy().currencyNote + " " + (copy() === translations.fr ? "Conversion indisponible : affichage en euros." : "Conversion unavailable: showing euros.");
      }
    }
    updateAmounts();
  }
  function openTechnology(key) {
    const item = technologies[key];
    if (!item) return;
    selectedTechnology = key;
    const language = copy() === translations.fr ? "fr" : "en";
    title.textContent = item[language][0];
    description.textContent = item[language][1];
    amountInput.value = minimumLocal.toFixed(2);
    updateAmounts();
    if (typeof modal.showModal === "function") modal.showModal();
    else modal.setAttribute("open", "");
  }
  grid.addEventListener("click", event => {
    const button = event.target.closest("button[data-tech]");
    if (button) openTechnology(button.dataset.tech);
  });
  amountInput.addEventListener("input", updateAmounts);
  checkout.addEventListener("click", () => {
    const url = paymentLinks.PAYPAL;
    const amount = Number(amountInput.value);
    if (!url || !/^https:\/\/www\.paypal\.com\/paypalme\/gudjencio\/?$/i.test(url) || !Number.isFinite(amount) || amount < minimumLocal) return;
    window.open(url, "_blank", "noopener,noreferrer");
  });
  copyButton.addEventListener("click", async () => {
    const item = technologies[selectedTechnology];
    const amount = Number(amountInput.value);
    const summary = [item ? item[copy() === translations.fr ? "fr" : "en"][0] : "SSSWET", "Research contribution: " + formatMoney(amount), "Payment destination: PayPal", "Enter the amount manually on the PayPal page. Future product delivery is conditional on actual development, feasibility and separate terms."].join("\n");
    try { await navigator.clipboard.writeText(summary); paymentStatus.textContent = copy().copied; }
    catch (_) { paymentStatus.textContent = copy().copyError; }
  });
  document.querySelectorAll("[data-tech-copy]").forEach(element => {
    const key = element.dataset.techCopy;
    if (key === "eyebrow") element.textContent = copy().eyebrow;
    if (key === "title") element.textContent = copy().title;
    if (key === "intro") element.textContent = copy().intro;
    if (key === "disclaimer") element.textContent = copy().disclaimer;
    if (key === "dialogEyebrow") element.textContent = copy().dialogEyebrow;
    if (key === "amountLabel") element.textContent = copy().amountLabel;
    if (key === "repeatLabel") element.textContent = copy().repeatLabel;
    if (key === "perContribution") element.textContent = copy().perContribution;
    if (key === "totalLabel") element.textContent = copy().totalLabel;
    if (key === "checkout") element.textContent = copy().checkout;
    if (key === "copySummary") element.textContent = copy().copySummary;
    if (key === "paymentDisclaimer") element.textContent = copy().paymentDisclaimer;
  });
  document.querySelectorAll(".technology-card").forEach((card, index) => {
    const keys = Object.keys(technologies);
    const button = card.querySelector("button[data-tech]");
    if (button) button.textContent = copy().explore;
    const names = Object.values(technologies);
    if (names[index]) {
      card.querySelector("h3").textContent = names[index][copy() === translations.fr ? "fr" : "en"][0];
      card.querySelector("p").textContent = names[index][copy() === translations.fr ? "fr" : "en"][1];
    }
  });
  currencyNote.textContent = copy().currencyNote;
  chooseCurrency();
  window.addEventListener("languagechange", () => window.location.reload());
  document.getElementById("language")?.addEventListener("change", () => {
    const language = copy() === translations.fr ? "fr" : "en";
    document.querySelectorAll("[data-tech-copy]").forEach(element => {
      const key = element.dataset.techCopy;
      const value = copy()[key === "dialogEyebrow" ? "dialogEyebrow" : key];
      if (value) element.textContent = value;
    });
    document.querySelectorAll(".technology-card").forEach((card, index) => {
      const item = Object.values(technologies)[index];
      if (item) { card.querySelector("h3").textContent = item[language][0]; card.querySelector("p").textContent = item[language][1]; }
      const button = card.querySelector("button"); if (button) button.textContent = copy().explore;
    });
    if (selectedTechnology) {
      const item = technologies[selectedTechnology];
      title.textContent = item[language][0]; description.textContent = item[language][1];
    }
    currencyNote.textContent = copy().currencyNote;
    updateAmounts();
  });
})();
