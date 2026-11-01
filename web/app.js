(() => {
  "use strict";

  const locales = window.SSSWET_LOCALES || {};
  const fallback = locales.en || {};
  const languageSelect = document.getElementById("language");
  const feed = document.getElementById("feed");
  const agentCount = document.getElementById("agent-count");
  const systemStatus = document.getElementById("system-status");
  const dashboard = document.getElementById("dashboard");
  const dashboardGrid = document.getElementById("dashboard-grid");
  let lastView = "ready";
  let dashboardRequest = 0;

  const languageNames = Object.keys(locales).sort((a, b) => {
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
    try { return localStorage.getItem("ssswet-language"); } catch { return null; }
  }
  function safeSaveLanguage(code) {
    try { localStorage.setItem("ssswet-language", code); } catch { /* Session-only preference. */ }
  }
  function preferredLanguage() {
    const candidates = Array.isArray(navigator.languages) && navigator.languages.length
      ? navigator.languages : [navigator.language || "en"];
    for (const candidate of candidates) {
      const code = String(candidate).toLowerCase().replace("_", "-").split("-")[0];
      if (locales[code]) return code;
    }
    return "en";
  }
  function currentLanguage() { return languageSelect.value || "en"; }
  function currentTranslations() { return { ...fallback, ...(locales[currentLanguage()] || {}) }; }

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
      const value = t[element.dataset.i18n];
      if (typeof value === "string") element.textContent = value;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
      const value = t[element.dataset.i18nAria];
      if (typeof value === "string") element.setAttribute("aria-label", value);
    });
    safeSaveLanguage(selected);
    refreshStatus();
    if (lastView === "ready") showMessage(t.ready);
    else if (lastView === "discoveries") showDiscoveries();
    else if (lastView === "activity") showActivity();
    else if (lastView === "verified") showVerified();
    else if (lastView === "dashboard") showDashboard();
  }

  function showMessage(message) {
    dashboard.hidden = true;
    feed.hidden = false;
    const paragraph = document.createElement("p");
    paragraph.className = "feed-line";
    const marker = document.createElement("span");
    marker.textContent = "●";
    paragraph.append(marker, document.createTextNode(" " + message));
    feed.replaceChildren(paragraph);
  }

  async function apiGet(path) {
    const response = await fetch(path, {
      method: "GET", headers: { "Accept": "application/json" }, cache: "no-store"
    });
    if (!response.ok) throw new Error("HTTP " + response.status);
    return response.json();
  }

  async function refreshStatus() {
    const t = currentTranslations();
    try {
      const status = await apiGet("/api/status");
      agentCount.textContent = String(status.agents_total ?? 0).padStart(2, "0");
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
      const lines = items.map((item) => `[UNVERIFIED · ${item.role || "research"}] ${item.summary || ""}`).filter(Boolean);
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

  function safeCount(value) {
    return Array.isArray(value) ? value.length : Number.isFinite(value) ? value : 0;
  }
  function makeDashboardCard(title, value, detail, state) {
    const article = document.createElement("article");
    article.className = "dashboard-card";
    const heading = document.createElement("h3");
    heading.textContent = title;
    const metric = document.createElement("strong");
    metric.className = "dashboard-metric";
    metric.textContent = String(value);
    const description = document.createElement("p");
    description.textContent = detail;
    const status = document.createElement("span");
    status.className = "dashboard-state" + (state === "error" ? " is-error" : "");
    status.textContent = state === "error" ? "UNAVAILABLE" : state === "empty" ? "NO RECORDS" : "LIVE DATA";
    article.append(heading, metric, description, status);
    return article;
  }
  function pickArray(payload, key) {
    if (Array.isArray(payload)) return payload;
    return payload && Array.isArray(payload[key]) ? payload[key] : [];
  }

  async function showDashboard() {
    lastView = "dashboard";
    feed.hidden = true;
    dashboard.hidden = false;
    dashboardGrid.replaceChildren();
    const requestId = ++dashboardRequest;
    const t = currentTranslations();
    const definitions = [
      { key: "campaigns", path: "/api/campaigns", list: "campaigns", title: "Research campaigns", detail: (a) => a.length ? a.slice(0, 3).map(x => x.title || x.campaign_id).join(" · ") : "No campaign has been recorded." },
      { key: "resources", path: "/api/resources", list: "snapshots", title: "Resource management", detail: (a) => a.length ? "Latest resource snapshots are available." : "No resource snapshot has been recorded." },
      { key: "transfers", path: "/api/collaboration/transfers", list: "transfers", title: "Shared knowledge", detail: (a) => a.length ? a.filter(x => x.state === "pending").length + " transfer(s) awaiting a decision." : "No knowledge transfer has been recorded." },
      { key: "experiments", path: "/api/experiments", list: "experiments", title: "Experiments", detail: (a) => a.length ? "Plans and records are tracked separately from verified findings." : "No experiment plan or record has been stored." },
      { key: "optimization", path: "/api/optimization", list: "cycles", title: "Adaptive optimization", detail: (a) => a.length ? "Proposals require human approval before execution." : "No adaptive cycle has been recorded." },
      { key: "gaps", path: "/api/research-gaps", list: "gaps", title: "Research gaps", detail: (a) => a.length ? "High priority: " + a.filter(x => x.priority === "high").length + " · Medium: " + a.filter(x => x.priority === "medium").length : "No graph-level gap is currently reported." },
      { key: "graph", path: "/api/knowledge-graph", list: "nodes", title: "Knowledge graph", detail: (a, p) => "Explicit relationships: " + safeCount(p.edges) + ". Links are not proof of truth." },
      { key: "events", path: "/api/events", list: null, title: "Recent activity", detail: (a) => a.length ? a.slice(0, 3).map(x => x.message || x.kind).filter(Boolean).join(" · ") : "No activity has been recorded." }
    ];
    const results = await Promise.all(definitions.map(async (item) => {
      try {
        const payload = await apiGet(item.path);
        const array = item.list ? pickArray(payload, item.list) : pickArray(payload, "");
        return { item, payload, array, error: false };
      } catch { return { item, payload: null, array: [], error: true }; }
    }));
    if (requestId !== dashboardRequest) return;
    results.forEach(({ item, payload, array, error }) => {
      const count = item.key === "gaps" ? safeCount(payload && payload.total) : array.length;
      const detail = error
        ? "The local research engine is not connected to this endpoint."
        : item.detail(array, payload || {});
      dashboardGrid.append(makeDashboardCard(item.title, error ? "—" : count, detail, error ? "error" : count ? "live" : "empty"));
    });
    if (results.every(result => result.error)) {
      const note = document.createElement("p");
      note.className = "dashboard-offline";
      note.textContent = t.offline;
      dashboardGrid.prepend(note);
    }
  }

  document.querySelectorAll("button[data-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const actions = { dashboard: showDashboard, discover: showDiscoveries, working: showActivity, verified: showVerified };
      if (actions[button.dataset.action]) actions[button.dataset.action]();
    });
  });
  languageSelect.addEventListener("change", () => setLanguage(languageSelect.value));
  setLanguage(safeReadLanguage() || preferredLanguage());
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
})();
