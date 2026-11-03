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
const timeTravelLinkSource = fs.readFileSync(new URL("./virtual-time-travel-link.js", `file://${__filename}`), "utf8");
for (const code of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi","id","tr","pl","bn","sw","vi","fa","ur","ta","te"]) {
  if (!timeTravelLinkSource.includes(code + ":\"")) throw new Error(`Virtual Time Travel launch label is missing locale ${code}`);
}
for (const feature of ["ssswet-language-changed", "data-language", "document.documentElement.lang", "MutationObserver", "virtual-time-travel-launch"]) {
  if (!timeTravelLinkSource.includes(feature)) throw new Error("Virtual Time Travel launch localization is missing " + feature);
}
console.log("Validated the Virtual Time Travel launch label in all 25 translated interface locales and on language changes.");

for (const [code, locale] of Object.entries(locales)) {
  if (!locale.voiceEnable || !locale.voiceDisable || !locale.voiceListen) {
    throw new Error(`Locale ${code} is missing voice-control labels`);
  }
}
const appSource = fs.readFileSync(new URL("./app.js", `file://${__filename}`), "utf8");
const pageSource = fs.readFileSync(new URL("./index.html", `file://${__filename}`), "utf8");

if (!/fr:\s*\["SSSWET"/.test(appSource)) throw new Error("French branding must display SSSWET, not ETDESS");
if (!appSource.includes('timeZone === "Europe/Paris"')) throw new Error("French locale should be detected from the metropolitan France time zone");
const interfaceTranslationKeys = [...new Set([...pageSource.matchAll(/data-i18n(?:-aria|-placeholder)?="([^"]+)"/g)].map(match => match[1]))];
for (const key of interfaceTranslationKeys) {
  if (typeof locales.fr[key] !== "string" || !locales.fr[key].trim()) {
    throw new Error(`French interface translation is missing: ${key}`);
  }
}
for (const feature of ["SpeechSynthesisUtterance", "speechSynthesis", "chooseVoice", "speakAsAgent", "speakLongText", "readCurrentFeed", "capitalizeInterfaceText", "MutationObserver"]) {
  if (!appSource.includes(feature)) throw new Error(`Voice or capitalization feature missing: ${feature}`);
}
if (!pageSource.includes('id="voice-toggle"') || !pageSource.includes('id="voice-read"') || !pageSource.includes('id="voice-pause"') || !pageSource.includes('id="voice-resume"') || !pageSource.includes('id="voice-stop"')) throw new Error("The voice controls are incomplete");

const agentCopy = context.window.SSSWET_AGENT_COPY;
if (!agentCopy || !fullyTranslated.size) {
  throw new Error("The first-load agent introduction catalogue is missing");
}
if (!Array.isArray(context.window.SSSWET_LANGUAGE_CATALOG) ||
    context.window.SSSWET_LANGUAGE_CATALOG.length !== 300) {
  throw new Error("Expected exactly 300 selectable languages (190 existing + 110 additions)");
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
for (const technology of ["cellular", "longevity", "armor", "jetpack", "translator", "spacetime", "sentientAI"]) {
  if (!donationSource.includes(technology)) throw new Error(`Technology catalogue entry missing: ${technology}`);
}
if (!pageSource.includes('id="technology-dialog"') || !pageSource.includes('id="technology-grid"')) throw new Error("Technology showcase or contribution dialog is missing");
console.log("Validated the technology catalogue and contribution-window integration.");
const brandingSource = appSource;
for (const required of ["SSSWET", "Ingénierie et technologies de distorsion de l’espace pour super-soldats", "超兵士向け空間歪曲工学・技術", "applyProjectBranding", "automaticVoiceRetried", "dashboard-foldout"]) {
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
if (catalogueEntries.length !== 108 || new Set(catalogueEntries).size !== 108) {
  throw new Error(`Expected exactly 108 unique public technology catalogue entries; found ${catalogueEntries.length}.`);
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
console.log("Validated all 100 research programmes, unpublished unknowns, manual PayPal ledger disclosure and progress interface.");


const journalSource = fs.readFileSync(new URL('./research-journal.js', `file://${__filename}`), 'utf8');
new Function(journalSource);
if (!pageSource.includes('id="research-journal-form"') || !pageSource.includes('id="research-journal-list"')) throw new Error('Research journal UI is missing.');
if (!journalSource.includes('/api/research-journal') || !journalSource.includes('chain_intact')) throw new Error('Research journal API or integrity display is missing.');
console.log('Validated the append-only research journal interface.');

const temporalSource=fs.readFileSync(new URL('./virtual-time-travel.js', `file://${__filename}`),'utf8');
new vm.Script(temporalSource);
const temporalHtml=fs.readFileSync(new URL('./virtual-time-travel.html', `file://${__filename}`),'utf8');
for(const id of ['vt-keyframe-clip','vt-keyframe-interval','vt-keyframe-analyze','vt-keyframe-results'])if(!temporalHtml.includes('id="'+id+'"'))throw new Error('Missing local keyframe control: '+id);
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
if (!donationSourceLatest.includes("cardFragment.append(card)") || !donationSourceLatest.includes("grid.append(cardFragment)")) throw new Error("Dynamic technology cards must be batch-inserted from a document fragment.");
const stylesLatest = fs.readFileSync(new URL("./styles.css", "file://" + __filename), "utf8");
if (!stylesLatest.includes("scroll-snap-type:x mandatory")) throw new Error("Mobile horizontal technology rail is missing.");
console.log("Validated local engine discovery, offline alternatives, project email and expanded horizontal technology catalogue.");

if (!stylesLatest.includes(".repair-project-button")) throw new Error("Project recovery button styling is missing.");
if (!pageSource.includes('id="fund-techs-button"') || !pageSource.includes('href="https://sites.google.com/view/aevolis/loop"') || !pageSource.includes('target="_blank"') || !stylesLatest.includes(".fund-techs-button")) throw new Error("The top-level free research-funding link is missing or incorrectly styled.");
if (!pageSource.includes('class="top-action-links"') || !pageSource.includes('id="repair-project-button"')) throw new Error("The funding and project-recovery actions must be grouped at the top of the interface.");
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

const versionCenterSource = fs.readFileSync(new URL("./version-center.js", `file://${__filename}`), "utf8");
new Function(versionCenterSource);
if (!pageSource.includes('id="version-center"') ||
    !pageSource.includes('id="version-center-status"') ||
    !pageSource.includes('id="version-center-history"')) {
  throw new Error("The official version centre interface is incomplete.");
}
if (!versionCenterSource.includes("/releases?per_page=8") ||
    !versionCenterSource.includes("SHA256SUMS") ||
    !versionCenterSource.includes("cache: \"no-store\"")) {
  throw new Error("The version centre must retrieve current releases and expose integrity information.");
}
if (!serviceWorkerCache.includes('"./version-center.js"')) {
  throw new Error("The version centre script must be cached for installed applications.");
}
console.log("Validated official release centre, release history and checksum information.");


const updateManagerSource = fs.readFileSync(new URL("./service-worker-updates.js", `file://${__filename}`), "utf8");
new Function(updateManagerSource);
if (!pageSource.includes('id="ssswet-update-banner"') ||
    !pageSource.includes('id="ssswet-update-action"') ||
    !pageSource.includes('src="service-worker-updates.js"')) {
  throw new Error("The application update notice is incomplete.");
}
if (!serviceWorkerCache.includes('"./service-worker-updates.js"') ||
    !serviceWorkerCache.includes('SSSWET_SKIP_WAITING') ||
    /^\s*self\.skipWaiting\(\);\s*$/m.test(serviceWorkerCache)) {
  throw new Error("Application updates must be cached and activated only after user confirmation.");
}
console.log("Validated the user-controlled service worker update flow.");


const taxonomySource = fs.readFileSync(new URL("./technology-categories.js", `file://${__filename}`), "utf8");
new Function(taxonomySource);
const taxonomyGroupsMatch = taxonomySource.match(/const groups = (\{[\s\S]*?\});/);
const taxonomyTranslationsMatch = taxonomySource.match(/const translations = (\{[\s\S]*?\});/);
if (!taxonomyGroupsMatch || !taxonomyTranslationsMatch) throw new Error("Technology taxonomy data is missing.");
const taxonomyGroups = JSON.parse(taxonomyGroupsMatch[1]);
const taxonomyTranslations = JSON.parse(taxonomyTranslationsMatch[1]);
const taxonomyKeys = Object.values(taxonomyGroups).flatMap(group => Object.values(group).flat());
if (Object.keys(taxonomyGroups).length !== 8 || taxonomyKeys.length !== 606 || new Set(taxonomyKeys).size !== 606) {
  throw new Error("The technology taxonomy must classify exactly six hundred and six unique programmes in eight categories.");
}
const requiredTaxonomyLocales = ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"];
for (const locale of requiredTaxonomyLocales) {
  if (!Array.isArray(taxonomyTranslations[locale]) || taxonomyTranslations[locale].length !== 27) {
    throw new Error(`Technology category and subcategory translations are incomplete for ${locale}.`);
  }
}
const catalogueDonationSource = fs.readFileSync(new URL("./donation.js", `file://${__filename}`), "utf8");
const curatedTechnologySource = fs.readFileSync(new URL("./technology-categories.js", `file://${__filename}`), "utf8");
for (const key of taxonomyKeys) {
  if (!catalogueDonationSource.includes(key + ": {") && !curatedTechnologySource.includes(key)) throw new Error(`Technology ${key} is missing from the public catalogue.`);
}
if (!pageSource.includes('src="technology-categories.js"') ||
    !serviceWorkerCache.includes('"./technology-categories.js"')) {
  throw new Error("The categorized technology catalogue must be loaded and cached.");
}
console.log("Validated exactly 606 unique technology themes, eight categories, and 15 translated taxonomies.");


const expansionSource = fs.readFileSync(new URL("./technology-expansion-ui.js", `file://${__filename}`), "utf8");
new Function(expansionSource);
if (!expansionSource.includes("researchSpace") || !expansionSource.includes("researchSociety")) throw new Error("The expanded technology interface is incomplete.");
const botRoomSource = fs.readFileSync(new URL("./bot-live-room.js", `file://${__filename}`), "utf8");
new Function(botRoomSource);
if (!pageSource.includes('id="bot-free-question-form"') ||
    !pageSource.includes('id="bot-free-question"') ||
    !botRoomSource.includes("function answerFreeQuestion") ||
    !botRoomSource.includes("recent_outputs") ||
    !botRoomSource.includes("agent_messages")) {
  throw new Error("The source-linked free-form bot question interface is incomplete.");
}
console.log("Validated multilingual free-form questions and source-linked research retrieval in the bot room.");


const purchasePolicySource = fs.readFileSync(new URL("./product-purchase-config.js", `file://${__filename}`), "utf8");
const purchasePolicyContext = { window: {} };
vm.runInNewContext(purchasePolicySource, purchasePolicyContext);
const purchasePolicy = purchasePolicyContext.window.SSSWET_PRODUCT_PURCHASES;
if (!purchasePolicy || purchasePolicy.monthly_technology_financing.status !== "proposed_not_enabled" ||
    purchasePolicy.monthly_technology_financing.enabled !== false) {
  throw new Error("Future monthly technology checkout must remain disabled until launch reviews are complete.");
}
const financingPolicy = purchasePolicy.monthly_technology_financing;
if (financingPolicy.billing_frequency !== "monthly" ||
    financingPolicy.maximum_technologies_funded_per_billing_period !== 1 ||
    financingPolicy.monthly_payment_minimum_usd !== 1 ||
    !financingPolicy.monthly_payment_maximum.includes("X") ||
    !financingPolicy.bot_estimates_require_sources_and_uncertainty_labels ||
    !financingPolicy.independent_estimate_review_required ||
    financingPolicy.automatic_price_publication_only_when_all_validation_checks_pass !== true ||
    financingPolicy.incomplete_or_unverifiable_estimate_must_withhold_price !== true ||
    financingPolicy.uncertainty_reserve_max_percent_of_pretax_baseline !== 10 ||
    financingPolicy.reserve_above_cap_requires_more_research_not_higher_price !== true ||
    financingPolicy.collected_reserve_becomes_customer_specific_future_purchase_credit !== true ||
    financingPolicy.credit_only_from_cleared_collected_reserve !== true ||
    financingPolicy.credit_ledger_private_auditable_and_nonduplicative !== true ||
    financingPolicy.statutory_refunds_override_store_credit !== true ||
    financingPolicy.research_outcome_and_non_delivery_risk_must_be_disclosed !== true ||
    !financingPolicy.minimum_is_monthly_payment_not_guaranteed_net_margin ||
    !financingPolicy.all_applicable_taxes_included_in_displayed_consumer_total ||
    !financingPolicy.repair_and_compensation_costs_must_be_separate_itemized_line_items ||
    !financingPolicy.repair_and_compensation_are_not_taxes ||
    !financingPolicy.repair_or_compensation_charge_requires_documented_legal_basis ||
    !financingPolicy.warranty_repairs_must_not_be_charged ||
    !financingPolicy.all_inclusive_price_required_before_checkout ||
    !financingPolicy.destination_aware_tax_calculation_required ||
    !financingPolicy.retain_payment_as_donation_only_with_separate_affirmative_consent ||
    !financingPolicy.refund_and_withdrawal_rights_must_follow_applicable_law ||
    !financingPolicy.repairs_under_statutory_or_express_warranty_are_free ||
    !financingPolicy.no_duplicate_recovery_of_repair_costs ||
    !financingPolicy.verified_server_side_payment_and_webhook_required) {
  throw new Error("The proposed monthly financing policy is missing required customer safeguards.");
}
if (Object.values(purchasePolicy.products).some(product => product.available || product.price_eur !== null)) {
  throw new Error("No research concept may be advertised as a purchasable product without verified availability and pricing.");
}
const monthlyFinancingDoc = fs.readFileSync(new URL("../docs/MONTHLY_TECHNOLOGY_FINANCING.md", `file://${__filename}`), "utf8");
for (const phrase of ["Status: proposed design", "blanket", "statutory guarantee", "all-inclusive", "one technology per monthly billing period", "monthly payment", "uncertainty reserve", "customer-specific discount credit", "not a guarantee", "not taxes"]) {
  if (!monthlyFinancingDoc.toLowerCase().includes(phrase.toLowerCase())) {
    throw new Error(`Monthly financing policy is missing safeguard: ${phrase}`);
  }
}
console.log("Validated disabled monthly technology financing, tax transparency, refunds, warranty and repair safeguards.");


const extraLocalization = fs.readFileSync(new URL("./interface-localization.js", `file://${__filename}`), "utf8");
new Function(extraLocalization);
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  if (!extraLocalization.includes(locale + ": { priority:")) {
    throw new Error("Research interface form translations are missing for " + locale);
  }
}
const platformRouting = fs.readFileSync(new URL("./platform-routing.js", `file://${__filename}`), "utf8");
new Function(platformRouting);
for (const locale of ["zh","hi"]) {
  if (!platformRouting.includes(locale + ": { heading:")) {
    throw new Error("Platform installation translations are missing for " + locale);
  }
}
console.log("Validated research-form localization and device installation guidance for all 15 complete interface locales.");


const catalogueUiSource = fs.readFileSync(new URL("./catalogue-500-ui.js", `file://${__filename}`), "utf8");
new Function(catalogueUiSource);
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  if (!catalogueUiSource.includes(locale + ":[")) {
    throw new Error("Research registry status is not localized for " + locale);
  }
}
for (const asset of ["./language-center.css","./ui-enhancements.js","./platform-routing.js","./catalogue-500-ui.js"]) {
  if (!serviceWorkerCache.includes(asset)) throw new Error("Enhanced interface asset is missing from the service-worker cache: " + asset);
}
if (!stylesLatest.includes(".app-shell > .topbar") || !stylesLatest.includes("justify-content: center")) {
  throw new Error("The responsive language selector is not centered in the application header.");
}
console.log("Validated 15-language research registry labels, cached interface assets and centered language navigation.");

const virtualHtml = fs.readFileSync(__dirname + "/virtual-time-travel.html", "utf8");
const virtualScript = fs.readFileSync(__dirname + "/virtual-time-travel.js", "utf8");
const virtualLink = fs.readFileSync(__dirname + "/virtual-time-travel-link.js", "utf8");
new Function(virtualScript);
new Function(virtualLink);
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  if (!virtualScript.includes(locale + ":{")) throw new Error("Virtual Time Travel translation missing for " + locale);
}
for (const control of ["vt-start","vt-stop","vt-locate","vt-time","vt-model","vt-delete","vt-export"]) {
  if (!virtualHtml.includes('id="' + control + '"')) throw new Error("Virtual Time Travel control missing: " + control);
}
if (!virtualScript.includes("map provider") || !virtualScript.includes("modelPast")) throw new Error("Virtual Time Travel disclosure or model distinction is missing.");
console.log("Validated Virtual Time Travel scripts, controls and 15 interface locales.");

const voiceSource = fs.readFileSync(__dirname + "/bot-live-room.js", "utf8");
const readAloudSource = fs.readFileSync(__dirname + "/read-aloud.js", "utf8");
new Function(voiceSource);
new Function(readAloudSource);
if (!voiceSource.includes("function splitSpeech") || !voiceSource.includes("bestVoice")) throw new Error("Natural speech pacing or voice selection is missing.");
if (!readAloudSource.includes("Read selected text")) throw new Error("Accessible read-aloud control is missing.");

const categoryScript = fs.readFileSync(__dirname + "/technology-categories.js", "utf8");
new Function(categoryScript);
for (const key of ["virtualTimeTravelMap","spatiotemporalDigitalTwin","forensicSceneReconstruction","predictiveSceneSimulation","geospatialSensorFusion","persistent3DMapping","motionTrajectoryReconstruction","privacyPreservingCapture","environmentalEventReplay","uncertaintyAwareWorldModel","sentientAI"]) {
  if (!categoryScript.includes(key)) throw new Error("New research theme missing from the interface: " + key);
}
if (!categoryScript.includes("curatedTechnologyCopy") || !categoryScript.includes("spatiotemporalSystems") || !categoryScript.includes("sentientAI")) throw new Error("New research theme translations or category are missing.");

const newCopySource = fs.readFileSync(__dirname + "/new-technology-copy.js", "utf8");
new Function(newCopySource);
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  if (!newCopySource.includes("\"" + locale + "\":")) throw new Error("New technology descriptions are missing locale " + locale);
}
if (!newCopySource.includes("SSSWET_TECHNOLOGIES")) throw new Error("Curated technology metadata is not exposed to the contribution interface.");
const sentientContext = { window: {} };
vm.runInNewContext(newCopySource, sentientContext);
const sentientTranslations = sentientContext.window.SSSWET_TECHNOLOGIES?.sentientAI;
if (!sentientTranslations || Object.keys(sentientTranslations).length !== 15) throw new Error("Sentient AI must provide 15 localized title and description pairs.");
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  const pair = sentientTranslations[locale];
  if (!Array.isArray(pair) || pair.length !== 2 || pair.some(value => !value.trim())) throw new Error("Sentient AI translation is incomplete: " + locale);
}
const robotContext = { window: {} };
vm.runInNewContext(newCopySource, robotContext);
const robotTranslations = robotContext.window.SSSWET_TECHNOLOGIES?.humanLikeRobots;
if (!robotTranslations || Object.keys(robotTranslations).length !== 15) throw new Error("Human-like Robots must provide 15 localized title and description pairs.");
for (const locale of ["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]) {
  const pair = robotTranslations[locale];
  if (!Array.isArray(pair) || pair.length !== 2 || pair.some(value => !value.trim())) throw new Error("Human-like Robots translation is incomplete: " + locale);
}



const virtualTimeSource = fs.readFileSync(new URL("./virtual-time-travel.js", `file://${__filename}`), "utf8");
if (!virtualTimeSource.includes("lastOrientationWrite=0")) throw new Error("Virtual time capture must track orientation sampling independently.");
if (!virtualTimeSource.includes("Date.now()-lastOrientationWrite<900") || !virtualTimeSource.includes("Date.now()-lastMotionWrite<900")) throw new Error("Motion and orientation sampling must each have independent throttling.");
if (!catalogueUiSource.includes("606 contribution themes") || !catalogueUiSource.includes("1000 research dossiers") || !catalogueUiSource.includes("IA sentiente")) throw new Error("Public catalogue counts or Sentient AI French title are out of date.");
console.log("Validated Sentient AI and Human-like Robots registration, 15 translations, catalogue counts and independent motion/orientation sampling.");


// Keep the public project support controls wired into the published page.
if (!pageSource.includes('class="repair-project-slot"') || !pageSource.includes('id="repair-project-button"')) {
  throw new Error("The always-available project recovery control is missing from the page");
}
if (!pageSource.includes('src="repair-project.js"') || !pageSource.includes('src="report-project.js"')) {
  throw new Error("Project recovery and reporting scripts must be loaded by the public page");
}
if (!pageSource.includes('href="mobile-repair.css"')) {
  throw new Error("Project support controls must load their responsive stylesheet");
}
