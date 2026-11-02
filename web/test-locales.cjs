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
const catalogueBlock = donationSourceLatest.slice(donationSourceLatest.indexOf("const technologies = {"), donationSourceLatest.indexOf("window.SSSWET_TECHNOLOGIES"));
const catalogueEntries = [...catalogueBlock.matchAll(/^    ([A-Za-z_$][\w$]*): \{/gm)].map(match => match[1]);
if (catalogueEntries.length !== 40 || new Set(catalogueEntries).size !== 40) {
  throw new Error(`Expected exactly 40 unique public technology catalogue entries; found ${catalogueEntries.length}.`);
}
if (!donationSourceLatest.includes("grid.replaceChildren()") || !donationSourceLatest.includes("updateCatalogueCount()")) {
  throw new Error("The public catalogue must render the complete canonical list and count rendered cards.");
}
const reportSource = fs.readFileSync(new URL("./report-project.js", `file://${__filename}`), "utf8");
new Function(reportSource);
if ((reportSource.match(/button:"/g) || []).length !== 25 || (reportSource.match(/options:\[\[/g) || []).length !== 25) {
  throw new Error("The report button and its complete improvement menu must be translated in all 25 supported report languages.");
}
if (!reportSource.includes('window.ssswetApiFetch("/api/project-reports"') || !reportSource.includes('dialog.showModal()')) {
  throw new Error("The report form must open accessibly and submit to the hosted review endpoint.");
}
if (!reportSource.includes('view:"Voir mes améliorations"') || !reportSource.includes('close:"Fermer"') ||
    !reportSource.includes("localStorage") || !reportSource.includes("showHistory()")) {
  throw new Error("The report dialog must offer a localized submitted-improvements history and a close-only action.");
}
if (reportSource.includes('catch (_) { const result={key:"received",unavailable:true}; liveStatusCache.set(number,result);')) {
  throw new Error("Temporary report-status failures must not be cached permanently.");
}
if (!reportSource.includes("const cleanTitle=title.value.trim()") ||
    !reportSource.includes("const cleanDescription=detail.value.trim()") ||
    !reportSource.includes("if(!cleanTitle || !cleanDescription)")) {
  throw new Error("Report submission must reject whitespace-only titles and descriptions before sending.");
}
if (!reportSource.includes("getLiveReportStatus") || !reportSource.includes("reportStatusCopy") ||
    !reportSource.includes('"/pulls/"+Number(prMatch[1])') ||
    !reportSource.includes('key:"integrated"') || !reportSource.includes('key:"proposed"')) {
  throw new Error("The submitted-improvements dashboard must retrieve and distinguish live issue and pull-request states.");
}
for (const language of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi","id","tr","pl","bn","sw","vi","fa","ur","ta","te"]) {
  if (!reportSource.includes(language+":{received:")) throw new Error("Missing localized live report status for "+language);
}
if (!reportSource.includes('new MutationObserver') || !reportSource.includes('repair-project-slot')) {
  throw new Error("The report control must attach when the repair control is added dynamically.");
}
const serviceWorker = fs.readFileSync(new URL("./sw.js", `file://${__filename}`), "utf8");
if (!serviceWorker.includes('"./report-project.js"') || !serviceWorker.includes('"./donation.js"')) {
  throw new Error("The offline cache must include the report form and complete technology catalogue.");
}
for (const feature of ["timetravel", "Time travel research", "Voyage dans le temps", "PayPal", "PAYPAL_SUBSCRIPTION_PLAN_ID", "monthly contribution", "ongoing effort to make them possible"]) {
  if (!donationSourceLatest.includes(feature)) throw new Error(`Research funding feature missing: ${feature}`);
}
if (!paymentConfig.includes("PAYPAL_CLIENT_ID") || !paymentConfig.includes("PAYPAL_SUBSCRIPTION_PLAN_ID")) throw new Error("The official PayPal subscription plan is not configured.");
if (!pageSource.includes('data-tech="timetravel"')) throw new Error("Time travel is missing from the public technology catalogue.");
console.log("Validated the PayPal research-funding route, conditional future product delivery wording and time-travel technology.");

const portfolioConfig = fs.readFileSync(new URL("./donation-config.js", `file://${__filename}`), "utf8");
const portfolioKeys = portfolioConfig.match(/const ssswetTechnologyKeys = \[([\s\S]*?)\];/);
if (!portfolioKeys) throw new Error("Research portfolio technology catalogue is missing.");
for (const key of ["cellular", "longevity", "armor", "jetpack", "translator", "spacetime", "timetravel", "cleanenergy", "energyStorage", "water", "foodSystems", "climate", "biodiversity", "wildlife", "oceans", "reforestation", "agriculture", "circularEconomy", "airQuality", "mobility", "accessibility", "disasterResilience", "publicHealth", "sanitation", "education", "animalHealth", "materials", "carbonMonitoring", "pollinators", "artificialGravity", "medicalNanotechnology", "atmosphericRestoration", "neurointerfaces", "quantumNetworks", "fusionEnergy", "spaceLifeSupport", "autonomousLabs", "roboticsExoskeletons", "planetaryMonitoring", "advancedComputing"]) {
  if (!portfolioKeys[1].includes(`"${key}"`)) throw new Error(`Research portfolio is missing ${key}`);
}
for (const field of ["funding_goal_eur: null", "confirmed_contributions_eur: null", 'stage: "planning"', 'prototype: false', 'availability: "not_available"']) {
  if (!portfolioConfig.includes(field)) throw new Error(`Research portfolio transparency field missing: ${field}`);
}
if (!donationSourceLatest.includes("renderPortfolio")) throw new Error("Research progress display is missing.");
if (!pageSource.includes('id="portfolio-manual-note"') || !pageSource.includes('id="technology-dialog-progress"')) throw new Error("Research portfolio interface is missing.");
console.log("Validated all 40 research programmes, unpublished unknowns, manual PayPal ledger disclosure and progress interface.");


const journalSource = fs.readFileSync(new URL('./research-journal.js', `file://${__filename}`), 'utf8');
new Function(journalSource);
if (!pageSource.includes('id="research-journal-form"') || !pageSource.includes('id="research-journal-list"')) throw new Error('Research journal UI is missing.');
if (!journalSource.includes('/api/research-journal') || !journalSource.includes('chain_intact')) throw new Error('Research journal API or integrity display is missing.');
console.log('Validated the append-only research journal interface.');

const feasibilitySource=fs.readFileSync(new URL('./technology-feasibility.js', `file://${__filename}`),'utf8');
new Function(feasibilitySource);
if(!pageSource.includes('id="technology-feasibility-list"')||!feasibilitySource.includes('/api/technology-feasibility'))throw new Error('Technology feasibility observatory UI is missing.');
console.log('Validated the technology feasibility observatory interface.');

const purchaseConfig=fs.readFileSync(new URL('./product-purchase-config.js', `file://${__filename}`),'utf8');
new Function(purchaseConfig);
for(const key of ['cellular','longevity','armor','jetpack','translator','spacetime','timetravel','cleanenergy','energyStorage','water','foodSystems','climate','biodiversity','wildlife','oceans','reforestation','agriculture','circularEconomy','airQuality','mobility','accessibility','disasterResilience','publicHealth','sanitation','education','animalHealth','materials','carbonMonitoring','pollinators']) if(!purchaseConfig.includes(key+':')) throw new Error('Product purchase config missing '+key);
if(!purchaseConfig.includes('delivery_address_collection')||!purchaseConfig.includes('legal_review_required')) throw new Error('Product purchase safeguards missing.');
console.log('Validated future product purchase gates and delivery safeguards.');

const engineConnectionSource = appSource;
for (const feature of ["ssswetApiFetch", "http://127.0.0.1:8765", "ssswet-engine-connection", "refreshStatus"]) {
  if (!engineConnectionSource.includes(feature)) throw new Error("Local engine discovery feature missing: " + feature);
}
if (!pageSource.includes('id="engine-connection"') || !pageSource.includes('id="engine-connection-retry"')) throw new Error("Automatic engine fallback notice is missing.");
if (!pageSource.includes("ssswetindustries@gmail.com")) throw new Error("Project contact address is missing.");
for (const feature of ["cleanenergy", "biodiversity", "wildlife", "oceans", "animalHealth", "pollinators", "water", "accessibility", "disasterResilience"]) {
  if (!donationSourceLatest.includes(feature)) throw new Error("Expanded social-benefit technology missing: " + feature);
}
if (!donationSourceLatest.includes("grid.append(card)")) throw new Error("Dynamic technology cards are not generated.");
const stylesLatest = fs.readFileSync(new URL("./styles.css", "file://" + __filename), "utf8");
if (!stylesLatest.includes("scroll-snap-type:x mandatory")) throw new Error("Mobile horizontal technology rail is missing.");
console.log("Validated local engine discovery, offline alternatives, project email and expanded horizontal technology catalogue.");

if (!stylesLatest.includes(".repair-project-button")) throw new Error("Project recovery button styling is missing.");
for (const logText of ["function localizeResearchLog", "Task lifecycle state updated.", "Research group created with role-matched agents.", "Erreur technique à examiner"]) {
  if (!appSource.includes(logText)) throw new Error("Localized research log handling is missing: " + logText);
}
console.log("Validated the project recovery button and localized research logs.");

new Function(donationSourceLatest);
const reminderScript = fs.readFileSync(new URL("../integrations/google-apps-script/PaymentReminders.gs", `file://${__filename}`), "utf8");
new Function(reminderScript);
for (const feature of ["registerPaymentReminder_", "confirmPaymentReminder_", "sendDuePaymentReminders_", "installPaymentReminderTrigger_", "unsubscribePaymentReminder_"]) {
  if (!reminderScript.includes(feature)) throw new Error("Payment reminder service is missing: " + feature);
}
console.log("Validated payment UI syntax and the opt-in Apps Script reminder service.");

const monthlyPaypalMarkup = pageSource.includes('paypal-button-container-P-75A66386EX5825057NLTZHII');
if (!monthlyPaypalMarkup || !donationSourceLatest.includes("quantity: String(amount)") || !donationSourceLatest.includes("vault=true&intent=subscription")) {
  throw new Error("Monthly PayPal subscription integration is incomplete.");
}
if (!paymentConfig.includes("PAYPAL_CLIENT_ID") || !paymentConfig.includes("PAYPAL_SUBSCRIPTION_PLAN_ID")) {
  throw new Error("Monthly PayPal client or plan configuration is missing.");
}
if (!donationSourceLatest.includes('amount >= 1') || !donationSourceLatest.includes('amount <= 100000')) {
  throw new Error("Monthly subscription amount validation is missing.");
}
const mainStyles = fs.readFileSync(new URL("./styles.css", `file://${__filename}`), "utf8");
if (!mainStyles.includes(".app-shell > .social-corner") ||
    !mainStyles.includes("position: relative !important") ||
    !mainStyles.includes(".app-shell > .topbar")) {
  throw new Error("Mobile social navigation must remain in document flow above the header.");
}
const serviceWorkerCache = fs.readFileSync(new URL("./sw.js", `file://${__filename}`), "utf8");
if (!/const CACHE = "ssswet-web-v[0-9]+"/.test(serviceWorkerCache)) {
  throw new Error("The mobile layout must be delivered through a versioned service-worker cache.");
}
console.log("Validated the PayPal monthly subscription flow, variable quantity configuration and mobile social navigation.");

const platformSource = fs.readFileSync(new URL("./platform-downloads.js", `file://${__filename}`), "utf8");
new Function(platformSource);
const manifest = JSON.parse(fs.readFileSync(new URL("./manifest.json", `file://${__filename}`), "utf8"));
if (!manifest.icons?.some(icon => icon.src === "./icons/ssswet-icon.svg")) throw new Error("Installable application icon is missing.");
if (!pageSource.includes('id="platform-downloads"') || !pageSource.includes('id="ssswet-install-app"') || !pageSource.includes('id="ssswet-desktop-download"') || !pageSource.includes('id="ssswet-mobile-download"')) throw new Error("Mobile and desktop application download controls are incomplete.");
const desktopShell = fs.readFileSync(new URL("../desktop/main.cjs", `file://${__filename}`), "utf8");
new Function(desktopShell);
const packageConfig = JSON.parse(fs.readFileSync(new URL("../package.json", `file://${__filename}`), "utf8"));
if (!packageConfig.build?.win || !packageConfig.build?.mac || !packageConfig.build?.linux) throw new Error("Cross-platform desktop build targets are incomplete.");
console.log("Validated mobile installation, desktop download controls, PWA manifest and desktop package configuration.");
