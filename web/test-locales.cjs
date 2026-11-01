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
for (const [code, locale] of Object.entries(locales)) {
  for (const key of required) {
    if (typeof locale[key] !== "string" || !locale[key].trim()) {
      throw new Error(`Locale ${code} is missing a valid "${key}" translation`);
    }
  }
  if (!["ltr", "rtl"].includes(locale.dir)) {
    throw new Error(`Locale ${code} has an invalid text direction`);
  }
}
if (locales.ar.dir !== "rtl" || locales.he.dir !== "rtl") {
  throw new Error("Arabic and Hebrew must use right-to-left layout");
}
console.log(`Validated ${Object.keys(locales).length} locales and ${required.length} required interface strings.`);

const agentCopy = context.window.SSSWET_AGENT_COPY;
if (!agentCopy || Object.keys(agentCopy).length !== Object.keys(locales).length) {
  throw new Error("Every interface locale must have a localized first-load agent introduction");
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
  if (!Array.isArray(copy.questions) || copy.questions.length !== 3 ||
      copy.questions.some(question => typeof question !== "string" || !question.trim())) {
    throw new Error(`Agent introduction ${code} must define three guided questions`);
  }
}
