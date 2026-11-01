const translations = {
  en: {
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "RESEARCH INTERFACE",
    statusOnline: "LOCAL RESEARCH ENGINE CONNECTED",
    statusOffline: "LOCAL RESEARCH ENGINE NOT CONNECTED",
    mission: "Research ideas. Test them. Verify them. Never confuse a hypothesis with reality.",
    agents: "Research agents", verification: "verification-first",
    discover: "What did you discover?", working: "What are you working on?", verified: "Latest verified results",
    ready: "The interface is ready. Connect the local engine to display live research data.",
    footer: "ETDESS is the French translation of SSSWET. Public results remain subject to verification.",
    offline: "The local research engine is not connected. On GitHub Pages, this is a static preview; run the local application to access live status.",
    noDiscoveries: "No research outputs are stored yet.",
    noActivity: "No research activity has been recorded yet.",
    noVerified: "No independently verified knowledge is available yet."
  },
  fr: {
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "INTERFACE DE RECHERCHE",
    statusOnline: "MOTEUR DE RECHERCHE LOCAL CONNECTÉ",
    statusOffline: "MOTEUR DE RECHERCHE LOCAL NON CONNECTÉ",
    mission: "Rechercher des idées. Les tester. Les vérifier. Ne jamais confondre une hypothèse avec la réalité.",
    agents: "Agents de recherche", verification: "vérification prioritaire",
    discover: "Qu'avez-vous découvert ?", working: "Sur quoi travaillez-vous ?", verified: "Derniers résultats vérifiés",
    ready: "L'interface est prête. Connectez le moteur local pour afficher les données de recherche en direct.",
    footer: "ETDESS est la traduction française de SSSWET. Les résultats publics restent soumis à vérification.",
    offline: "Le moteur de recherche local n'est pas connecté. Sur GitHub Pages, il s'agit d'un aperçu statique ; lancez l'application locale pour accéder aux données en direct.",
    noDiscoveries: "Aucun résultat de recherche n'est encore enregistré.",
    noActivity: "Aucune activité de recherche n'a encore été enregistrée.",
    noVerified: "Aucune connaissance vérifiée indépendamment n'est encore disponible."
  }
};

const languageSelect = document.getElementById("language");
const feed = document.getElementById("feed");
const agentCount = document.getElementById("agent-count");
const systemStatus = document.getElementById("system-status");

function preferredLanguage() {
  return (navigator.language || "en").toLowerCase().startsWith("fr") ? "fr" : "en";
}
function currentTranslations() {
  return translations[languageSelect.value] || translations.en;
}
function setLanguage(lang) {
  const selected = translations[lang] ? lang : "en";
  const t = translations[selected];
  document.documentElement.lang = selected;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (t[key]) element.textContent = t[key];
  });
  languageSelect.value = selected;
  localStorage.setItem("ssswet-language", selected);
}
function showMessage(message) {
  const paragraph = document.createElement("p");
  paragraph.className = "feed-line";
  const marker = document.createElement("span");
  marker.textContent = "●";
  paragraph.append(marker, document.createTextNode(" " + message));
  feed.replaceChildren(paragraph);
}
async function apiGet(path) {
  const response = await fetch(path, {
    method: "GET",
    headers: { "Accept": "application/json" },
    cache: "no-store"
  });
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}
async function refreshStatus() {
  const t = currentTranslations();
  try {
    const status = await apiGet("/api/status");
    agentCount.textContent = String(status.agents_total).padStart(2, "0");
    systemStatus.textContent = t.statusOnline;
    systemStatus.dataset.connected = "true";
  } catch {
    agentCount.textContent = "—";
    systemStatus.textContent = t.statusOffline;
    systemStatus.dataset.connected = "false";
  }
}
async function showDiscoveries() {
  const t = currentTranslations();
  try {
    const items = await apiGet("/api/discoveries");
    const lines = items.map((item) => `[UNVERIFIED · ${item.role}] ${item.summary}`).filter(Boolean);
    showMessage(lines.length ? lines.join(" • ") : t.noDiscoveries);
  } catch { showMessage(t.offline); }
}
async function showActivity() {
  const t = currentTranslations();
  try {
    const events = await apiGet("/api/events");
    const lines = events.slice(0, 5).map((event) => event.message).filter(Boolean);
    showMessage(lines.length ? lines.join(" • ") : t.noActivity);
  } catch { showMessage(t.offline); }
}
async function showVerified() {
  const t = currentTranslations();
  try {
    const items = await apiGet("/api/verified");
    const lines = items.map((item) => item.statement).filter(Boolean);
    showMessage(lines.length ? lines.join(" • ") : t.noVerified);
  } catch { showMessage(t.offline); }
}
document.querySelectorAll("button[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    const actions = { discover: showDiscoveries, working: showActivity, verified: showVerified };
    if (actions[button.dataset.action]) actions[button.dataset.action]();
  });
});
languageSelect.addEventListener("change", () => {
  setLanguage(languageSelect.value);
  refreshStatus();
});
setLanguage(localStorage.getItem("ssswet-language") || preferredLanguage());
showMessage(currentTranslations().ready);
refreshStatus();
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
