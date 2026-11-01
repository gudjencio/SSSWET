const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync(new URL("./locales.js", `file://${__filename}`), "utf8");
const context = { window: {} };
vm.runInNewContext(source, context);
const locales = context.window.SSSWET_LOCALES;
if (!locales || Object.keys(locales).length < 14) {
  throw new Error("Expected at least 14 available interface locales");
}
const required = [
  "name", "dir", "tagline", "status", "statusOnline", "statusOffline",
  "mission", "agents", "verification", "discover", "working", "verified",
  "ready", "footer", "offline", "noDiscoveries", "noActivity",
  "noVerified", "language", "social", "contact",
  "dashboard", "dashboardNote", "refresh",
  "dashCampaigns", "dashResources", "dashTransfers", "dashExperiments",
  "dashOptimization", "dashGaps", "dashGraph", "dashActivity", "dashConflicts",
  "dashUnavailable", "dashNoRecords", "dashLive", "dashActive", "dashBlocked",
  "dashQueued", "dashCompleted", "dashPending", "dashAccepted", "dashRejected",
  "dashPlans", "dashRecords", "dashNodes", "dashRelations", "dashHigh",
  "dashMedium", "dashLow", "dashCycles", "dashRecent",
  "dashEndpointUnavailable", "dashNoData"
];
const fullyTranslated = new Set(["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]);
const additionalTranslated = new Set(["id", "tr", "pl", "bn", "sw", "vi", "fa", "ur", "ta", "te"]);
const additionalRequired = ["tagline", "status", "statusOnline", "statusOffline", "mission", "agents", "verification", "discover", "working", "verified", "ready", "footer", "offline", "noDiscoveries", "noActivity", "noVerified", "language", "social", "contact", "dashboard", "dashboardNote", "refresh", "timelineTitle", "timelineFilter", "allCampaigns", "timelineSearchLabel", "timelineSearchPlaceholder", "timelineTypeFilter", "allEventTypes", "timelineNoMatches", "timelineCaption", "timelineEmpty"];
for (const [code, locale] of Object.entries(locales)) {
  if (!locale.name || !["ltr", "rtl"].includes(locale.dir)) {
    throw new Error(`Locale ${code} must define a name and text direction`);
  }
  if (additionalTranslated.has(code)) {
    for (const key of additionalRequired) {
      if (typeof locale[key] !== "string" || !locale[key].trim() || locale[key] === locales.en[key]) {
        throw new Error(`Locale ${code} is missing a localized "${key}" translation`);
      }
    }
  }
  if (!fullyTranslated.has(code)) continue;
  for (const key of required) {
    if (typeof locale[key] !== "string" || !locale[key].trim()) {
      throw new Error(`Locale ${code} is missing a valid "${key}" translation`);
    }
  }
  if (!["ltr", "rtl"].includes(locale.dir)) {
    throw new Error(`Locale ${code} has an invalid text direction`);
  }
}
if (locales.ar.dir !== "rtl" || locales.he.dir !== "rtl" || locales.fa.dir !== "rtl" || locales.ur.dir !== "rtl") {
  throw new Error("Arabic and Hebrew must use right-to-left layout");
}
console.log(`Validated ${Object.keys(locales).length} selectable locales, ${context.window.SSSWET_LANGUAGE_CATALOG.length} language options, and ${fullyTranslated.size} complete translations.`);

for (const [code, locale] of Object.entries(locales)) {
  if (!locale.voiceEnable || !locale.voiceDisable || !locale.voiceListen) {
    throw new Error(`Locale ${code} is missing voice-control labels`);
  }
}
const appSource = fs.readFileSync(new URL("./app.js", `file://${__filename}`), "utf8");
const pageSource = fs.readFileSync(new URL("./index.html", `file://${__filename}`), "utf8");
for (const feature of ["SpeechSynthesisUtterance", "speechSynthesis", "chooseVoice", "speakAsAgent", "speakLongText", "readCurrentFeed", "capitalizeInterfaceText", "MutationObserver"]) {
  if (!appSource.includes(feature)) throw new Error(`Voice or capitalization feature missing: ${feature}`);
}
if (!pageSource.includes('id="voice-toggle"') || !pageSource.includes('id="voice-read"') || !pageSource.includes('id="voice-pause"') || !pageSource.includes('id="voice-resume"') || !pageSource.includes('id="voice-stop"')) throw new Error("The voice controls are incomplete");

const agentCopy = context.window.SSSWET_AGENT_COPY;
if (!agentCopy || !fullyTranslated.size) {
  throw new Error("The first-load agent introduction catalogue is missing");
}
if (!Array.isArray(context.window.SSSWET_LANGUAGE_CATALOG) ||
    context.window.SSSWET_LANGUAGE_CATALOG.length < 180) {
  throw new Error("The complete selectable language catalogue is missing");
}
const languageCodes = context.window.SSSWET_LANGUAGE_CATALOG.map(item => item.split("|")[0]);
if (new Set(languageCodes).size !== languageCodes.length) {
  throw new Error("The language catalogue contains duplicate language codes");
}
for (const [code, copy] of Object.entries(agentCopy)) {
  if (!locales[code]) throw new Error(`Agent introduction has no matching locale: ${code}`);
  for (const key of ["welcome", "summary", "disclaimer"]) {
    if (typeof copy[key] !== "string" || !copy[key].trim()) {
      throw new Error(`Agent introduction ${code} is missing ${key}`);
    }
  }
  if (!Array.isArray(copy.roles) || copy.roles.length !== 3 ||
      copy.roles.some(role => !Array.isArray(role) || role.length !== 2 || role.some(value => !value.trim()))) {
    throw new Error(`Agent introduction ${code} must define three named roles`);
  }
  if (!Array.isArray(copy.steps) || copy.steps.length < 5 ||
      copy.steps.some(step => typeof step !== "string" || !step.trim())) {
    throw new Error(`Agent introduction ${code} must define the research workflow`);
  }
  const questionsValid = Array.isArray(copy.questions)
    ? copy.questions.length === 3 && copy.questions.every(question => typeof question === "string" && question.trim().length > 0)
    : !!copy.questions && ["working", "evidence", "review"].every(key => String(copy.questions[key] || "").trim().length > 0);
  if (!questionsValid) {
    throw new Error(`Agent introduction ${code} must define three guided questions`);
  }
}

const donationSource = fs.readFileSync(new URL("./donation.js", `file://${__filename}`), "utf8");
for (const feature of ["SSSWET_TECHNOLOGIES", "minimumLocal", "Intl.NumberFormat", "donation-checkout", "SSSWET_DONATION_LINKS"]) {
  if (!donationSource.includes(feature)) throw new Error(`Donation feature missing: ${feature}`);
}
for (const technology of ["cellular", "longevity", "armor", "jetpack", "translator", "spacetime"]) {
  if (!donationSource.includes(technology)) throw new Error(`Technology catalogue entry missing: ${technology}`);
}
if (!pageSource.includes('id="technology-dialog"') || !pageSource.includes('id="technology-grid"')) throw new Error("Technology showcase or contribution dialog is missing");
console.log("Validated the technology catalogue and contribution-window integration.");
const brandingSource = appSource;
for (const required of ["ETDESS", "Équipements et technologies de distorsions spatiales pour super-soldats", "超兵士向け空間歪曲工学・技術", "applyProjectBranding", "automaticVoiceRetried", "dashboard-foldout"]) {
  if (!brandingSource.includes(required)) throw new Error(`Branding, startup or compact layout feature missing: ${required}`);
}
for (const social of ["data-social=\"Instagram\"", "data-social=\"YouTube\"", "mailto:ssswetindustries@gmail.com", "<svg"]) {
  if (!pageSource.includes(social)) throw new Error(`Social link feature missing: ${social}`);
}
console.log("Validated localized project branding, automatic voice attempt, compact panels and social icons.");

const donationSourceLatest = fs.readFileSync(new URL("./donation.js", `file://${__filename}`), "utf8");
const paymentConfig = fs.readFileSync(new URL("./donation-config.js", `file://${__filename}`), "utf8");
new Function(donationSourceLatest);
for (const feature of ["timetravel", "Time travel research", "Voyage dans le temps", "PayPal", "paymentLinks.PAYPAL", "future purchase and delivery", "ongoing effort to make them possible"]) {
  if (!donationSourceLatest.includes(feature)) throw new Error(`Research funding feature missing: ${feature}`);
}
if (!paymentConfig.includes("https://www.paypal.com/paypalme/gudjencio")) throw new Error("The official PayPal destination is not configured.");
if (!pageSource.includes('data-tech="timetravel"')) throw new Error("Time travel is missing from the public technology catalogue.");
console.log("Validated the PayPal research-funding route, conditional future product delivery wording and time-travel technology.");

const portfolioConfig = fs.readFileSync(new URL("./donation-config.js", `file://${__filename}`), "utf8");
for (const key of ["cellular", "longevity", "armor", "jetpack", "translator", "spacetime", "timetravel"]) {
  if (!portfolioConfig.includes(key + ":")) throw new Error(`Research portfolio is missing ${key}`);
}
for (const field of ["funding_goal_eur: null", "confirmed_contributions_eur: null", 'stage: "planning"', 'prototype: false', 'availability: "not_available"']) {
  if (!portfolioConfig.includes(field)) throw new Error(`Research portfolio transparency field missing: ${field}`);
}
if (!donationSourceLatest.includes("renderPortfolio") || !donationSourceLatest.includes("PayPal.Me does not synchronize")) throw new Error("Research progress display or manual-ledger disclosure is missing.");
if (!pageSource.includes('id="portfolio-manual-note"') || !pageSource.includes('id="technology-dialog-progress"')) throw new Error("Research portfolio interface is missing.");
console.log("Validated the seven-theme research portfolio, unpublished unknowns, manual PayPal ledger disclosure and progress interface.");


const journalSource = fs.readFileSync(new URL('./research-journal.js', `file://${__filename}`), 'utf8');
new Function(journalSource);
if (!pageSource.includes('id="research-journal-form"') || !pageSource.includes('id="research-journal-list"')) throw new Error('Research journal UI is missing.');
if (!journalSource.includes('/api/research-journal') || !journalSource.includes('chain_intact')) throw new Error('Research journal API or integrity display is missing.');
console.log('Validated the append-only research journal interface.');
