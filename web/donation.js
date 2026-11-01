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
  const countInput = document.getElementById("donation-count");
  const currencyLabel = document.getElementById("donation-currency");
  const perOutput = document.getElementById("donation-per");
  const totalOutput = document.getElementById("donation-total");
  const currencyNote = document.getElementById("donation-currency-note");
  const paymentStatus = document.getElementById("donation-payment-status");
  const checkout = document.getElementById("donation-checkout");
  const copyButton = document.getElementById("donation-copy");
  const translations = {
    en: { eyebrow:"FUTURE TECHNOLOGIES · RESEARCH PRIORITIES", title:"Choose a technology to support", intro:"Explore the research directions and open a contribution window for the technology you want to encourage.", disclaimer:"These are research themes, not claims that the technologies exist or are currently achievable. Contributions support the project and do not purchase a product or guarantee an outcome.", explore:"Explore & contribute", dialogEyebrow:"SUPPORT A RESEARCH DIRECTION", amountLabel:"Contribution amount", repeatLabel:"Number of separate contributions", perContribution:"Per contribution", totalLabel:"Planned total", currencyNote:"Currency is estimated from your browser's regional settings. The minimum is the equivalent of €0.50 per contribution.", paymentMissing:"Online payment is not activated for this currency yet. The secure payment link must be configured before contributions can be collected.", paymentReady:"A secure payment link is available for this currency.", checkout:"Continue to secure contribution", copySummary:"Copy contribution summary", paymentDisclaimer:"Online payment is activated only when an official payment link for this currency has been configured. You can contribute again as often as you wish; each separate contribution starts at the equivalent of €0.50.", invalid:"Enter at least the equivalent of €0.50 and one contribution.", copied:"Contribution summary copied.", copyError:"Unable to copy automatically. Please select and copy the summary." },
    fr: { eyebrow:"TECHNOLOGIES DU FUTUR · PRIORITÉS DE RECHERCHE", title:"Choisissez une technologie à soutenir", intro:"Découvrez les axes de recherche et ouvrez une fenêtre de contribution pour la technologie que vous souhaitez encourager.", disclaimer:"Ces thèmes de recherche ne signifient pas que ces technologies existent ou soient réalisables aujourd'hui. Les contributions soutiennent le projet : elles n'achètent aucun produit et ne garantissent aucun résultat.", explore:"Découvrir et contribuer", dialogEyebrow:"SOUTENIR UN AXE DE RECHERCHE", amountLabel:"Montant de chaque contribution", repeatLabel:"Nombre de contributions distinctes", perContribution:"Par contribution", totalLabel:"Total envisagé", currencyNote:"La devise est estimée à partir des paramètres régionaux du navigateur. Le minimum est l'équivalent de 0,50 € par contribution.", paymentMissing:"Le paiement en ligne n'est pas encore activé pour cette devise. Un lien de paiement sécurisé doit être configuré avant de pouvoir collecter les contributions.", paymentReady:"Un lien de paiement sécurisé est disponible pour cette devise.", checkout:"Continuer vers le paiement sécurisé", copySummary:"Copier le récapitulatif", paymentDisclaimer:"Le paiement en ligne sera activé uniquement après configuration d'un lien officiel pour cette devise. Vous pourrez contribuer autant de fois que vous le souhaitez ; chaque contribution distincte commence à l'équivalent de 0,50 €.", invalid:"Saisissez au moins l'équivalent de 0,50 € et une contribution.", copied:"Récapitulatif copié.", copyError:"Copie automatique impossible. Veuillez sélectionner et copier le récapitulatif." }
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
    const count = Math.max(1, Math.min(1000, Math.floor(Number(countInput.value) || 1)));
    const valid = Number.isFinite(amount) && amount >= minimumLocal && count >= 1;
    perOutput.textContent = Number.isFinite(amount) ? formatMoney(amount) : "—";
    totalOutput.textContent = valid ? formatMoney(amount * count) : "—";
    checkout.disabled = !valid || !paymentLinks[currency];
    paymentStatus.textContent = valid ? (paymentLinks[currency] ? copy().paymentReady : copy().paymentMissing) : copy().invalid;
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
        minimumLocal = Math.ceil((0.5 * rate) * 100) / 100;
        rateReady = true;
        currencyNote.textContent = copy().currencyNote + " " + (copy() === translations.fr ? "Taux indicatif actualisé ; le montant final dépend du prestataire de paiement." : "Indicative live exchange rate; the final amount depends on the payment provider.");
      } catch (_) {
        currency = "EUR";
        minimumLocal = 0.50;
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
    countInput.value = "1";
    updateAmounts();
    if (typeof modal.showModal === "function") modal.showModal();
    else modal.setAttribute("open", "");
  }
  grid.addEventListener("click", event => {
    const button = event.target.closest("button[data-tech]");
    if (button) openTechnology(button.dataset.tech);
  });
  amountInput.addEventListener("input", updateAmounts);
  countInput.addEventListener("input", updateAmounts);
  checkout.addEventListener("click", () => {
    const url = paymentLinks[currency];
    if (!url || !/^https:\/\//i.test(url)) return;
    const amount = Number(amountInput.value);
    const count = Math.max(1, Math.min(1000, Math.floor(Number(countInput.value) || 1)));
    const separator = url.includes("?") ? "&" : "?";
    window.open(url + separator + "client_reference_id=" + encodeURIComponent("ssswet-" + selectedTechnology + "-" + count) + "&prefilled_amount=" + encodeURIComponent(String(Math.round(amount * 100))), "_blank", "noopener,noreferrer");
  });
  copyButton.addEventListener("click", async () => {
    const item = technologies[selectedTechnology];
    const amount = Number(amountInput.value);
    const count = Math.max(1, Math.min(1000, Math.floor(Number(countInput.value) || 1)));
    const summary = [item ? item[copy() === translations.fr ? "fr" : "en"][0] : "SSSWET", count + " × " + formatMoney(amount), "Total: " + formatMoney(amount * count), "Minimum: equivalent of EUR 0.50 per contribution"].join("\n");
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
