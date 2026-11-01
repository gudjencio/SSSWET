(() => {
  "use strict";

  const locales = window.SSSWET_LOCALES || {};
  const fallback = locales.en || {};
  const languageSelect = document.getElementById("language");
  const feed = document.getElementById("feed");
  const agentCount = document.getElementById("agent-count");
  const systemStatus = document.getElementById("system-status");
  let lastView = "ready";

  const languageNames = Object.keys(locales);
  languageNames.sort((a, b) => {
    if (a === "en") return -1;
    if (b === "en") return 1;
    if (a === "fr") return -1;
    if (b === "fr") return 1;
    return (locales[a].name || a).localeCompare(locales[b].name || b);
  });

  languageNames.forEach((code) => {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = locales[code].name || code;
    languageSelect.append(option);
  });

  function safeReadLanguage() {
    try { return localStorage.getItem("ssswet-language"); }
    catch { return null; }
  }

  function safeSaveLanguage(code) {
    try { localStorage.setItem("ssswet-language", code); }
    catch { /* Private browsing or storage restrictions: language still works for this session. */ }
  }

  function preferredLanguage() {
    const candidates = Array.isArray(navigator.languages) && navigator.languages.length
      ? navigator.languages
      : [navigator.language || "en"];
    for (const candidate of candidates) {
      const normalized = String(candidate).toLowerCase().replace("_", "-");
      const exact = normalized.split("-")[0];
      if (locales[exact]) return exact;
    }
    return "en";
  }

  function currentLanguage() {
    return languageSelect.value || "en";
  }

  function currentTranslations() {
    return { ...fallback, ...(locales[currentLanguage()] || {}) };
  }

  function setLanguage(requested) {
    const selected = locales[requested] ? requested : "en";
    const t = { ...fallback, ...locales[selected] };
    const direction = t.dir === "rtl" ? "rtl" : "ltr";
    document.documentElement.lang = selected;
    document.documentElement.dir = direction;
    document.body.dir = direction;
    document.documentElement.dataset.language = selected;
    languageSelect.value = selected;

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.dataset.i18n;
      if (typeof t[key] === "string") element.textContent = t[key];
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
      const key = element.dataset.i18nAria;
      if (typeof t[key] === "string") element.setAttribute("aria-label", t[key]);
    });
    safeSaveLanguage(selected);
    refreshStatus();
    if (lastView === "ready") showMessage(t.ready);
    else if (lastView === "discoveries") showDiscoveries();
    else if (lastView === "activity") showActivity();
    else if (lastView === "verified") showVerified();
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
    lastView = "discoveries";
    const t = currentTranslations();
    try {
      const items = await apiGet("/api/discoveries");
      const lines = items.map((item) => `[UNVERIFIED · ${item.role}] ${item.summary}`).filter(Boolean);
      showMessage(lines.length ? lines.join(" • ") : t.noDiscoveries);
    } catch { showMessage(t.offline); }
  }

  async function showActivity() {
    lastView = "activity";
    const t = currentTranslations();
    try {
      const events = await apiGet("/api/events");
      const lines = events.slice(0, 5).map((event) => event.message).filter(Boolean);
      showMessage(lines.length ? lines.join(" • ") : t.noActivity);
    } catch { showMessage(t.offline); }
  }

  async function showVerified() {
    lastView = "verified";
    const t = currentTranslations();
    try {
      const items = await apiGet("/api/verified");
      const lines = items.map((item) => item.statement).filter(Boolean);
      showMessage(lines.length ? lines.join(" • ") : t.noVerified);
    } catch { showMessage(t.offline); }
  }

  document.querySelectorAll("button[data-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const actions = {
        discover: showDiscoveries,
        working: showActivity,
        verified: showVerified
      };
      if (actions[button.dataset.action]) actions[button.dataset.action]();
    });
  });

  languageSelect.addEventListener("change", () => setLanguage(languageSelect.value));

  setLanguage(safeReadLanguage() || preferredLanguage());
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("sw.js").catch(() => {});
    });
  }
})();
