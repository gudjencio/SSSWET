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
  "noVerified", "language", "social", "contact"
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
