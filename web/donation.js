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
    },
    cleanenergy: {
      en: ["Clean energy systems", "Research into safe, scalable solar, wind, geothermal and other low-carbon energy systems."],
      fr: ["Systèmes d’énergie propre", "Recherche sur des systèmes énergétiques bas carbone sûrs et évolutifs : solaire, éolien, géothermie et autres filières."]
    },
    energyStorage: {
      en: ["Advanced energy storage", "Long-duration storage, safer batteries, grid balancing and responsible materials research."],
      fr: ["Stockage avancé de l’énergie", "Stockage de longue durée, batteries plus sûres, équilibre des réseaux et recherche responsable sur les matériaux."]
    },
    water: {
      en: ["Clean water and desalination", "Affordable water purification, contaminant detection, low-energy desalination and resilient access."],
      fr: ["Eau potable et dessalement", "Purification abordable, détection des contaminants, dessalement sobre en énergie et accès résilient à l’eau."]
    },
    foodSystems: {
      en: ["Sustainable food systems", "Resilient crops, food preservation, reduced waste and equitable access to nutritious food."],
      fr: ["Systèmes alimentaires durables", "Cultures résilientes, conservation des aliments, réduction du gaspillage et accès équitable à une alimentation nutritive."]
    },
    climate: {
      en: ["Climate adaptation", "Monitoring, forecasting, heat resilience, flood preparedness and evidence-led adaptation tools."],
      fr: ["Adaptation climatique", "Surveillance, prévisions, résilience face aux fortes chaleurs, préparation aux inondations et outils d’adaptation fondés sur les preuves."]
    },
    biodiversity: {
      en: ["Biodiversity protection", "Non-invasive monitoring, habitat connectivity and measurable conservation outcomes."],
      fr: ["Protection de la biodiversité", "Suivi non invasif, continuité des habitats et résultats de conservation mesurables."]
    },
    wildlife: {
      en: ["Wildlife protection", "Ethical tracking, rescue support, anti-poaching detection and safer coexistence with wildlife."],
      fr: ["Protection de la faune sauvage", "Suivi éthique, aide au sauvetage, détection du braconnage et coexistence plus sûre avec la faune."]
    },
    oceans: {
      en: ["Ocean and marine restoration", "Ocean observation, marine pollution reduction, reef monitoring and ecosystem recovery."],
      fr: ["Océans et restauration marine", "Observation des océans, réduction de la pollution marine, suivi des récifs et restauration des écosystèmes."]
    },
    reforestation: {
      en: ["Reforestation and habitat restoration", "Native-species restoration, soil recovery, ecological corridors and long-term survival monitoring."],
      fr: ["Reforestation et restauration des habitats", "Restauration d’espèces indigènes, régénération des sols, corridors écologiques et suivi de la survie à long terme."]
    },
    agriculture: {
      en: ["Regenerative agriculture", "Soil health, precision irrigation, biodiversity-friendly farming and lower-impact cultivation."],
      fr: ["Agriculture régénératrice", "Santé des sols, irrigation de précision, agriculture favorable à la biodiversité et cultures à moindre impact."]
    },
    circularEconomy: {
      en: ["Circular economy and recycling", "Repairable products, material recovery, safer recycling and reduced resource extraction."],
      fr: ["Économie circulaire et recyclage", "Produits réparables, récupération des matériaux, recyclage plus sûr et réduction de l’extraction des ressources."]
    },
    airQuality: {
      en: ["Clean air technologies", "Affordable air-quality sensing, filtration, emissions monitoring and exposure reduction."],
      fr: ["Qualité de l’air", "Capteurs abordables, filtration, surveillance des émissions et réduction de l’exposition à la pollution."]
    },
    mobility: {
      en: ["Sustainable mobility", "Accessible public transport, safer cycling, efficient logistics and low-emission mobility research."],
      fr: ["Mobilité durable", "Transports publics accessibles, vélo plus sûr, logistique efficace et mobilité à faibles émissions."]
    },
    accessibility: {
      en: ["Assistive and accessibility technology", "Affordable tools for communication, mobility, independent living and inclusive design."],
      fr: ["Technologies d’assistance et d’accessibilité", "Outils abordables pour la communication, la mobilité, l’autonomie et la conception inclusive."]
    },
    disasterResilience: {
      en: ["Disaster prevention and response", "Early warning, resilient infrastructure, emergency logistics and recovery coordination."],
      fr: ["Prévention et réponse aux catastrophes", "Alertes précoces, infrastructures résilientes, logistique d’urgence et coordination du rétablissement."]
    },
    publicHealth: {
      en: ["Public health and prevention", "Evidence-led prevention, accessible diagnostics, health information and community resilience."],
      fr: ["Santé publique et prévention", "Prévention fondée sur les preuves, diagnostics accessibles, information sanitaire et résilience communautaire."]
    },
    sanitation: {
      en: ["Sanitation and waste-water treatment", "Safe sanitation, decentralized treatment, water reuse and pollution prevention."],
      fr: ["Assainissement et traitement des eaux usées", "Assainissement sûr, traitement décentralisé, réutilisation de l’eau et prévention de la pollution."]
    },
    education: {
      en: ["Open science and education", "Free learning resources, scientific literacy, accessible laboratories and research collaboration."],
      fr: ["Science ouverte et éducation", "Ressources pédagogiques libres, culture scientifique, laboratoires accessibles et collaboration en recherche."]
    },
    animalHealth: {
      en: ["Animal health and welfare", "Non-invasive diagnostics, disease prevention, humane care and improved veterinary access."],
      fr: ["Santé et bien-être animal", "Diagnostics non invasifs, prévention des maladies, soins respectueux et meilleur accès vétérinaire."]
    },
    materials: {
      en: ["Sustainable and safer materials", "Durable, recyclable and non-toxic materials for construction, medicine and everyday products."],
      fr: ["Matériaux durables et plus sûrs", "Matériaux durables, recyclables et non toxiques pour la construction, la médecine et les produits courants."]
    },
    carbonMonitoring: {
      en: ["Carbon and ecosystem monitoring", "Transparent measurement of emissions, carbon storage and ecosystem health."],
      fr: ["Surveillance du carbone et des écosystèmes", "Mesure transparente des émissions, du stockage du carbone et de la santé des écosystèmes."]
    },
    pollinators: {
      en: ["Pollinator protection", "Habitat mapping, pesticide exposure reduction and monitoring of pollinator populations."],
      fr: ["Protection des pollinisateurs", "Cartographie des habitats, réduction de l’exposition aux pesticides et suivi des populations de pollinisateurs."]
    },
    artificialGravity: {
      en: ["Artificial gravity research", "Theoretical research into gravity-like environments, rotational habitats, inertial effects, human adaptation and measurable safety limits. No controllable artificial-gravity technology is currently claimed."],
      fr: ["Recherche sur la gravité artificielle", "Recherche théorique sur les environnements assimilables à la gravité, les habitats rotatifs, les effets inertiels, l’adaptation humaine et les limites de sécurité mesurables. Aucune technologie de gravité artificielle contrôlable n’est présentée comme acquise."]
    },
    medicalNanotechnology: {
      en: ["Medical nanotechnology", "Research into nanoscale diagnostics, targeted sensing, biocompatible materials, delivery constraints, toxicology and independently reviewed medical safety. No clinical capability is implied."],
      fr: ["Nanotechnologies médicales", "Recherche sur le diagnostic à l’échelle nanométrique, la détection ciblée, les matériaux biocompatibles, les contraintes d’administration, la toxicologie et la sécurité médicale évaluée indépendamment. Aucune capacité clinique n’est présumée."]
    },
    atmosphericRestoration: {
      en: ["Atmospheric restoration", "Research into atmospheric pollution monitoring, source reduction, carbon-cycle measurement, ecosystem recovery and validated interventions with transparent environmental safeguards."],
      fr: ["Restauration atmosphérique", "Recherche sur la surveillance de la pollution atmosphérique, la réduction des émissions à la source, la mesure du cycle du carbone, la restauration des écosystèmes et les interventions validées avec des garanties environnementales transparentes."]
    }
  };

  Object.assign(technologies, {
    neurointerfaces: {
      en: ["Interfaces cerveau-machine", "Research into non-invasive brain–computer interfaces, accessibility, signal quality and neural-data privacy."],
      fr: ["Interfaces cerveau-machine", "Recherche non invasive sur les interfaces cerveau-machine, l’accessibilité, la qualité du signal et la protection des données neuronales."]
    },
    quantumNetworks: {
      en: ["Réseaux de communication quantique", "Fundamental research into experimental quantum networks, quantum key distribution and their physical limits."],
      fr: ["Réseaux de communication quantique", "Recherche fondamentale sur les réseaux quantiques expérimentaux, la distribution quantique de clés et leurs limites physiques."]
    },
    fusionEnergy: {
      en: ["Énergie de fusion", "Research into materials, confinement, thermal management and fusion-related energy systems, without promising net energy production."],
      fr: ["Énergie de fusion", "Recherche sur les matériaux, le confinement, la gestion thermique et les systèmes associés à la fusion, sans promesse de production nette."]
    },
    spaceLifeSupport: {
      en: ["Écosystèmes spatiaux en boucle fermée", "Closed-loop life-support systems, water and air recycling, food production and resilient space habitats."],
      fr: ["Écosystèmes spatiaux en boucle fermée", "Systèmes de support-vie, recyclage de l’eau et de l’air, production alimentaire et résilience des habitats spatiaux."]
    },
    autonomousLabs: {
      en: ["Laboratoires scientifiques autonomes", "Automated measurements, experimental traceability, quality control and human validation of research protocols."],
      fr: ["Laboratoires scientifiques autonomes", "Automatisation des mesures, traçabilité expérimentale, contrôle qualité et validation humaine des protocoles."]
    },
    roboticsExoskeletons: {
      en: ["Robotique avancée et exosquelettes", "Assistive robotics, ergonomics, mobility, human–machine interaction and user safety."],
      fr: ["Robotique avancée et exosquelettes", "Robotique d’assistance, ergonomie, mobilité, interaction humain-machine et sécurité des utilisateurs."]
    },
    planetaryMonitoring: {
      en: ["Surveillance planétaire et risques astéroïdaux", "Astronomical detection, orbital tracking, uncertainty estimation and scientific risk assessment."],
      fr: ["Surveillance planétaire et risques astéroïdaux", "Détection astronomique, suivi orbital, estimation des incertitudes et évaluation scientifique des risques."]
    },
    advancedComputing: {
      en: ["Calcul avancé et intelligence artificielle scientifique", "Computational tools, interpretable scientific models, reproducibility and evaluation of AI-system limitations."],
      fr: ["Calcul avancé et intelligence artificielle scientifique", "Outils de calcul, modèles scientifiques interprétables, reproductibilité et évaluation des limites des systèmes d’IA."]
    }
  });

  window.SSSWET_TECHNOLOGIES = technologies;
  // Configure only official, verified payment links here. No payment credentials belong in this public file.
  const paymentLinks = window.SSSWET_DONATION_LINKS || {};
  const portfolio = window.SSSWET_RESEARCH_PORTFOLIO || {};
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
  Object.entries(technologies).forEach(([key, item], index) => {
    if (grid.querySelector('[data-tech="' + key + '"]')) return;
    const card = document.createElement("article");
    card.className = "technology-card";
    const number = document.createElement("span");
    number.className = "technology-number";
    number.textContent = String(index + 1).padStart(2, "0");
    const heading = document.createElement("h3");
    heading.textContent = item.en[0];
    const summary = document.createElement("p");
    summary.textContent = item.en[1];
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.tech = key;
    button.textContent = "Explore & contribute";
    card.append(number, heading, summary, button);
    grid.append(card);
  });

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
    en: { eyebrow:"FUTURE TECHNOLOGIES · RESEARCH PRIORITIES", title:"Choose a technology to support", intro:"Explore the research directions and open a contribution window for the technology you want to encourage.", disclaimer:"These are research themes, not claims that the technologies exist or are currently achievable. The project will keep exploring, testing and refining ideas in an ongoing effort to make them possible. Contributions fund research and development; they are not a purchase or a guarantee of results. If a technology becomes feasible and a product is actually developed, a future offer and delivery terms will be communicated separately.", explore:"Explore & contribute", dialogEyebrow:"FUND RESEARCH & DEVELOPMENT", amountLabel:"Monthly contribution amount (USD)", repeatLabel:"Number of separate contributions", perContribution:"Monthly contribution", totalLabel:"Annual equivalent", currencyNote:"Choose a monthly amount in USD. PayPal will display the subscription terms before approval.", paymentMissing:"The PayPal subscription is not configured.", paymentReady:"Choose your monthly amount, then approve the recurring subscription securely with PayPal.", checkout:"Continue to PayPal", copySummary:"Copy research contribution summary", paymentDisclaimer:"This is a recurring monthly contribution. The amount selected is billed monthly through PayPal until the subscriber cancels. Contributions support ongoing research and do not purchase an existing product or guarantee a result. Any future product offer and delivery terms will be communicated separately if a technology is developed and becomes available.", invalid:"Enter a monthly amount between USD 1 and USD 100,000.", copied:"Contribution summary copied.", copyError:"Unable to copy automatically. Please select and copy the summary." },
    fr: { eyebrow:"TECHNOLOGIES DU FUTUR · PRIORITÉS DE RECHERCHE", title:"Choisissez une technologie à soutenir", intro:"Découvrez les axes de recherche et ouvrez une fenêtre de contribution pour la technologie que vous souhaitez encourager.", disclaimer:"Ces axes ne signifient pas que les technologies existent ou soient réalisables aujourd'hui. Le projet poursuivra continuellement les recherches, les essais et les améliorations pour tenter de les rendre possibles. Les contributions financent la recherche et le développement ; elles ne constituent pas un achat et ne garantissent aucun résultat. Si une technologie devient réalisable et qu'un produit est effectivement développé, une offre et des conditions de livraison seront communiquées séparément.", explore:"Découvrir et contribuer", dialogEyebrow:"FINANCER LA RECHERCHE ET LE DÉVELOPPEMENT", amountLabel:"Montant mensuel en dollars américains · équivalent en euros", repeatLabel:"Nombre de contributions distinctes", perContribution:"Contribution mensuelle", totalLabel:"Équivalent annuel", currencyNote:"Le montant est facturé en dollars américains. Son équivalent en euros est affiché à titre indicatif selon le taux de change de référence le plus récent. PayPal affichera les conditions avant validation.", paymentMissing:"L’abonnement PayPal n’est pas configuré.", paymentReady:"Choisissez votre montant mensuel, puis approuvez l’abonnement récurrent en toute sécurité avec PayPal.", checkout:"Continuer vers PayPal", copySummary:"Copier le récapitulatif du financement", paymentDisclaimer:"Il s’agit d’une contribution mensuelle récurrente. Le montant choisi est facturé chaque mois par PayPal jusqu’à l’annulation de l’abonnement. Les contributions financent la recherche en cours et ne constituent pas l’achat d’un produit existant ni une garantie de résultat. Toute future offre de produit et de livraison sera communiquée séparément si une technologie est développée et devient disponible.", invalid:"Saisissez un montant mensuel compris entre 1 et 100 000 dollars américains.", copied:"Récapitulatif copié.", copyError:"Copie automatique impossible. Veuillez sélectionner et copier le récapitulatif." }
  };
  const copy = () => translations[(document.documentElement.lang || "en").startsWith("fr") ? "fr" : "en"];
  function applyPaymentLanguage() {
    const fr = copy() === translations.fr;
    const labels = {
      mode: fr ? "Modalité de paiement" : "Payment plan",
      single: fr ? "Paiement unique" : "One-time payment",
      installments: fr ? "Fractionner en échéances volontaires d’au moins 1 dollar américain" : "Split into voluntary instalments of at least USD 1",
      reminderTitle: fr ? "Rappels de paiement" : "Payment reminders",
      reminderDescription: fr ? "Après le premier paiement, vous pouvez demander des rappels volontaires par e-mail pour la prochaine échéance. Aucun prélèvement automatique ne sera effectué." : "After completing the first payment, you may request voluntary email reminders for the next instalment. No automatic charge will be made.",
      email: fr ? "Adresse e-mail" : "Email address",
      frequency: fr ? "Fréquence des rappels" : "Reminder frequency",
      weekly: fr ? "Une fois par semaine" : "Once a week",
      monthly: fr ? "Une fois par mois" : "Once a month",
      yearly: fr ? "Une fois par an" : "Once a year",
      confirmation: fr ? "Je confirme avoir effectué le premier paiement." : "I confirm that I have completed the first payment.",
      save: fr ? "Demander les rappels par e-mail" : "Request email reminders"
    };
    const set = (id, value) => { const element = document.getElementById(id); if (element) element.textContent = value; };
    set("donation-mode-label", labels.mode); set("donation-mode-single", labels.single); set("donation-mode-installments", labels.installments);
    set("payment-reminder-title", labels.reminderTitle); set("payment-reminder-description", labels.reminderDescription);
    set("payment-reminder-email-label", labels.email); set("payment-reminder-frequency-label", labels.frequency);
    set("payment-reminder-weekly", labels.weekly); set("payment-reminder-monthly", labels.monthly); set("payment-reminder-yearly", labels.yearly);
    set("payment-reminder-confirm-label", labels.confirmation); set("payment-reminder-save-label", labels.save);
  }
  let selectedTechnology = null;
  let currency = "EUR";
  let minimumLocal = 1;
  let usdToLocalRate = 1;
  let rateReady = false;
  const portfolioLabels = {
    en: { stage:"Research stage", goal:"Funding goal", confirmed:"Confirmed contributions", availability:"Availability", prototypeLabel:"Prototype status", unknown:"Not published", notSet:"Not set", planning:"Research planning", literature:"Literature review", feasibility:"Feasibility study", prototype:"Prototype development", validation:"Testing and validation", available:"Available for separate purchase", prototypeYes:"Prototype recorded", prototypeNo:"No prototype recorded", unavailable:"Not available", updated:"Last updated", progress:"Funding progress", manual:"Public figures are updated manually after payment confirmation. PayPal.Me does not synchronize payments with this website." },
    fr: { stage:"Étape de recherche", goal:"Objectif de financement", confirmed:"Contributions confirmées", availability:"Disponibilité", prototypeLabel:"Statut du prototype", unknown:"Non publié", notSet:"Non défini", planning:"Planification de la recherche", literature:"Revue de la littérature", feasibility:"Étude de faisabilité", prototype:"Développement d’un prototype", validation:"Essais et validation", available:"Disponible à l’achat séparément", prototypeYes:"Prototype déclaré", prototypeNo:"Aucun prototype déclaré", unavailable:"Non disponible", updated:"Dernière mise à jour", progress:"Progression du financement", manual:"Les chiffres publics sont actualisés manuellement après confirmation des paiements. PayPal.Me ne synchronise pas les paiements avec ce site." }
  };

  function localeRegion() {
    try { return new Intl.Locale(navigator.language || "en").region || ""; } catch (_) { return ""; }
  }
  function formatMoney(value) {
    try { return new Intl.NumberFormat(navigator.language || "en", { style:"currency", currency, minimumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2, maximumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2 }).format(value); }
    catch (_) { return value.toFixed(2) + " " + currency; }
  }
  let usdToEurRate = null;
  let exchangeRateDate = "";
  function formatUsd(value, french) {
    if (french) return new Intl.NumberFormat("fr-FR", {minimumFractionDigits:2,maximumFractionDigits:2}).format(value) + (Math.abs(value - 1) < 0.000001 ? " dollar américain" : " dollars américains");
    return new Intl.NumberFormat("en-US", {style:"currency",currency:"USD",minimumFractionDigits:2,maximumFractionDigits:2}).format(value);
  }
  function formatEur(value) {
    return new Intl.NumberFormat("fr-FR", {style:"currency",currency:"EUR",minimumFractionDigits:2,maximumFractionDigits:2}).format(value);
  }
  function updateAmounts() {
    const amount = Number(amountInput.value);
    const valid = Number.isFinite(amount) && amount >= 1 && amount <= 100000;
    const french = copy() === translations.fr;
    const monthlyEur = valid && Number.isFinite(usdToEurRate) ? " · ≈ " + formatEur(amount * usdToEurRate) : valid && french ? " · équivalent en euros indisponible" : "";
    const annualEur = valid && Number.isFinite(usdToEurRate) ? " · ≈ " + formatEur(amount * 12 * usdToEurRate) : valid && french ? " · équivalent en euros indisponible" : "";
    perOutput.textContent = valid ? formatUsd(amount,french) + (french ? " / mois" : " / month") + monthlyEur : "—";
    totalOutput.textContent = valid ? formatUsd(amount*12,french) + (french ? " / an" : " / year") + annualEur : "—";
    currencyLabel.textContent = french ? "Dollars américains / mois · équivalent en euros" : "USD / month";
    const configured = Boolean(paymentLinks.PAYPAL_CLIENT_ID && paymentLinks.PAYPAL_SUBSCRIPTION_PLAN_ID);
    paymentStatus.textContent = !valid ? copy().invalid : configured ? copy().paymentReady : copy().paymentMissing;
  }
  async function loadEuroExchangeRate() {
    try {
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), 12000);
      let response;
      try {
        response = await fetch("https://api.frankfurter.dev/v2/rate/usd/eur", {
          cache:"no-store", headers:{Accept:"application/json"}, signal:controller.signal
        });
      } finally {
        window.clearTimeout(timeout);
      }
      if (!response.ok) throw new Error("Exchange-rate service returned HTTP " + response.status);
      const data = await response.json();
      const rate = Number(data && data.rate);
      if (!Number.isFinite(rate) || rate <= 0 || data.base?.toUpperCase() !== "USD" || data.quote?.toUpperCase() !== "EUR") {
        throw new Error("Invalid USD/EUR exchange-rate response");
      }
      usdToEurRate = rate;
      exchangeRateDate = typeof data.date === "string" ? data.date : "";
    } catch (error) {
      usdToEurRate = null;
      exchangeRateDate = "";
      console.warn("[SSSWET] USD/EUR conversion unavailable:", error);
    }
    updateAmounts();
    updateCurrencyNote();
  }
  function updateCurrencyNote() {
    if (!currencyNote) return;
    const french = copy() === translations.fr;
    if (french) {
      currencyNote.textContent = copy().currencyNote
        + (usdToEurRate && exchangeRateDate
          ? " Taux de référence du " + new Intl.DateTimeFormat("fr-FR").format(new Date(exchangeRateDate + "T12:00:00Z")) + "."
          : usdToEurRate ? "" : " La conversion en euros est temporairement indisponible ; aucun taux n’est inventé.");
    } else {
      currencyNote.textContent = copy().currencyNote;
    }
  }

  function chooseCurrency() {
    amountInput.min = "1";
    amountInput.max = "100000";
    amountInput.step = "0.01";
    amountInput.value = String(Math.max(1, Math.round((Number(amountInput.value) || 1) * 100) / 100));
    currencyLabel.textContent = copy() === translations.fr ? "Dollars américains / mois · équivalent en euros" : "USD / month";
    updateCurrencyNote();
    updateAmounts();
  }

  let paypalButtonsRendered = false;
  let paypalSdkPromise = null;
  function loadPayPalSdk() {
    if (window.paypal && window.paypal.Buttons) return Promise.resolve(window.paypal);
    if (paypalSdkPromise) return paypalSdkPromise;
    paypalSdkPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-ssswet-paypal-sdk="true"]');
      if (existing) {
        existing.addEventListener("load", () => resolve(window.paypal), {once:true});
        existing.addEventListener("error", reject, {once:true});
        return;
      }
      const script = document.createElement("script");
      script.src = "https://www.paypal.com/sdk/js?client-id=" + encodeURIComponent(paymentLinks.PAYPAL_CLIENT_ID) + "&vault=true&intent=subscription";
      script.dataset.sdkIntegrationSource = "button-factory";
      script.dataset.ssswetPaypalSdk = "true";
      script.onload = () => window.paypal && window.paypal.Buttons ? resolve(window.paypal) : reject(new Error("PayPal SDK did not initialize."));
      script.onerror = () => reject(new Error("Unable to load PayPal SDK."));
      document.head.appendChild(script);
    });
    return paypalSdkPromise;
  }
  async function renderPayPalSubscriptionButton() {
    const container = document.getElementById("paypal-button-container-P-75A66386EX5825057NLTZHII");
    if (!container || paypalButtonsRendered) return;
    try {
      const paypal = await loadPayPalSdk();
      if (!paypal || !paypal.Buttons) throw new Error("PayPal Buttons are unavailable.");
      paypal.Buttons({
        style: {shape:"pill", color:"gold", layout:"vertical", label:"paypal"},
        createSubscription: function(data, actions) {
          const amount = Number(amountInput.value);
          if (!Number.isFinite(amount) || amount < 1 || amount > 100000) {
            paymentStatus.textContent = copy() === translations.fr ? "Saisissez un montant mensuel d’au moins 1 dollar américain." : "Enter a monthly amount of at least USD 1.";
            return Promise.reject(new Error("Invalid monthly contribution amount."));
          }
          return actions.subscription.create({
            plan_id: paymentLinks.PAYPAL_SUBSCRIPTION_PLAN_ID,
            quantity: String(amount)
          });
        },
        onApprove: function(data) {
          paymentStatus.textContent = copy() === translations.fr
            ? "Abonnement PayPal approuvé. Vous pouvez gérer ou annuler vos paiements récurrents depuis votre compte PayPal. Référence : " + data.subscriptionID
            : "PayPal subscription approved. You can manage or cancel recurring payments from your PayPal account. Reference: " + data.subscriptionID;
        },
        onCancel: function() {
          paymentStatus.textContent = copy() === translations.fr ? "Création de l’abonnement annulée." : "Subscription setup was cancelled.";
        },
        onError: function(error) {
          console.error("[SSSWET] PayPal subscription error:", error);
          paymentStatus.textContent = copy() === translations.fr
            ? "PayPal n’a pas pu créer l’abonnement. Vérifiez que le plan autorise les quantités personnalisées et réessayez."
            : "PayPal could not create the subscription. Check that the plan supports custom quantities, then try again.";
        }
      }).render("#paypal-button-container-P-75A66386EX5825057NLTZHII");
      paypalButtonsRendered = true;
    } catch (error) {
      console.error("[SSSWET] PayPal SDK error:", error);
      paymentStatus.textContent = copy() === translations.fr ? "Impossible de charger PayPal pour le moment. Actualisez la page et réessayez." : "PayPal could not be loaded right now. Refresh the page and try again.";
    }
  }

  function renderPortfolio() {
    const language = copy() === translations.fr ? "fr" : "en";
    const labels = portfolioLabels[language];
    document.querySelectorAll(".technology-card").forEach(card => {
      const button = card.querySelector("button[data-tech]");
      if (!button) return;
      const record = portfolio[button.dataset.tech] || {};
      let panel = card.querySelector(".technology-progress");
      if (!panel) { panel = document.createElement("div"); panel.className = "technology-progress"; card.insertBefore(panel, button); }
      const goalKnown = Number.isFinite(record.funding_goal_eur) && record.funding_goal_eur > 0;
      const totalKnown = Number.isFinite(record.confirmed_contributions_eur) && record.confirmed_contributions_eur >= 0;
      const money = value => new Intl.NumberFormat(language, { style:"currency", currency:"EUR" }).format(value);
      const amount = totalKnown ? money(record.confirmed_contributions_eur) : labels.unknown;
      const goal = goalKnown ? money(record.funding_goal_eur) : labels.notSet;
      const stages = { planning:labels.planning, literature_review:labels.literature, feasibility:labels.feasibility, prototype:labels.prototype, validation:labels.validation, available:labels.available };
      const stage = stages[record.stage] || labels.unknown;
      const percent = goalKnown && totalKnown ? Math.min(100, Math.round(record.confirmed_contributions_eur / record.funding_goal_eur * 100)) : null;
      panel.replaceChildren();
      const lines = [[labels.stage,stage],[labels.confirmed,amount],[labels.goal,goal],[labels.prototypeLabel,record.prototype === true ? labels.prototypeYes : labels.prototypeNo],[labels.availability,record.availability === "available" ? labels.available : labels.unavailable]];
      for (const pair of lines) { const line=document.createElement("div"); line.className="technology-progress-line"; const left=document.createElement("span"); left.textContent=pair[0]; const right=document.createElement("strong"); right.textContent=pair[1]; line.append(left,right); panel.append(line); }
      if (percent !== null) { const track=document.createElement("div"); track.className="technology-progress-track"; const fill=document.createElement("span"); fill.style.width=percent+"%"; track.append(fill); const caption=document.createElement("small"); caption.textContent=labels.progress+" · "+percent+"%"; panel.append(track,caption); }
      if (record.last_updated) { const updated=document.createElement("small"); updated.textContent=labels.updated+" · "+record.last_updated; panel.append(updated); }
    });
    const note=document.getElementById("portfolio-manual-note"); if(note) note.textContent=labels.manual;
  }
  function openTechnology(key) {
    const item = technologies[key];
    if (!item) return;
    selectedTechnology = key;
    const language = copy() === translations.fr ? "fr" : "en";
    title.textContent = item[language][0];
    description.textContent = item[language][1];
    const record = portfolio[key] || {};
    const detail = document.getElementById("technology-dialog-progress");
    if (detail) { const labels=portfolioLabels[language]; const stages={planning:labels.planning,literature_review:labels.literature,feasibility:labels.feasibility,prototype:labels.prototype,validation:labels.validation,available:labels.available}; const money=value=>new Intl.NumberFormat(language,{style:"currency",currency:"EUR"}).format(value); const goal=Number.isFinite(record.funding_goal_eur)&&record.funding_goal_eur>0?money(record.funding_goal_eur):labels.notSet; const total=Number.isFinite(record.confirmed_contributions_eur)&&record.confirmed_contributions_eur>=0?money(record.confirmed_contributions_eur):labels.unknown; detail.textContent=labels.stage+": "+(stages[record.stage]||labels.unknown)+" · "+labels.confirmed+": "+total+" · "+labels.goal+": "+goal; }
    amountInput.value = "1";
    updateAmounts();
    if (typeof modal.showModal === "function") modal.showModal();
    else modal.setAttribute("open", "");
    renderPayPalSubscriptionButton();
  }
  grid.addEventListener("click", event => {
    const button = event.target.closest("button[data-tech]");
    if (button) openTechnology(button.dataset.tech);
  });
  amountInput.addEventListener("input", updateAmounts);
  amountInput.addEventListener("change", updateAmounts);
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
  applyPaymentLanguage();
  renderPortfolio();
  chooseCurrency();
  loadEuroExchangeRate();
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
    updateCurrencyNote();
    renderPortfolio();
    updateAmounts();
  });
})();
