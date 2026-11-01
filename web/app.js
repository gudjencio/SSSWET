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
    const t = currentTranslations();
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
    status.textContent = state === "error" ? t.dashUnavailable : state === "empty" ? t.dashNoRecords : t.dashLive;
    article.append(heading, metric, description, status);
    return article;
  }

  function pickArray(payload, key) {
    if (Array.isArray(payload)) return payload;
    return payload && Array.isArray(payload[key]) ? payload[key] : [];
  }

  function dashboardMetrics(entries) {
    return entries.filter(([, count]) => Number(count) > 0)
      .map(([label, count]) => String(count) + " " + label).join(" · ") || currentTranslations().dashNoData;
  }

  async function showDashboard() {
    lastView = "dashboard";
    feed.hidden = true;
    dashboard.hidden = false;
    dashboardGrid.replaceChildren();
    const requestId = ++dashboardRequest;
    const t = currentTranslations();
    const definitions = [
      {
        key: "campaigns", path: "/api/campaigns", list: "campaigns",
        title: t.dashCampaigns,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([
          [t.dashActive, a.filter(x => x.state === "active").length],
          [t.dashBlocked, a.filter(x => x.state === "blocked").length],
          [t.dashCompleted, a.filter(x => x.state === "completed").length]
        ])
      },
      {
        key: "resources", path: "/api/resources", list: "snapshots",
        title: t.dashResources,
        count: (a) => {
          const s = a[0] && a[0].snapshot || {};
          return safeCount(s.active) + safeCount(s.queued) + safeCount(s.completed_task_ids) + safeCount(s.failed_task_ids);
        },
        detail: (a) => {
          const s = a[0] && a[0].snapshot || {};
          return dashboardMetrics([
            [t.dashActive, safeCount(s.active)],
            [t.dashQueued, safeCount(s.queued)],
            [t.dashCompleted, safeCount(s.completed_task_ids)]
          ]);
        }
      },
      {
        key: "transfers", path: "/api/collaboration/transfers", list: "transfers",
        title: t.dashTransfers,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([
          [t.dashPending, a.filter(x => x.state === "pending").length],
          [t.dashAccepted, a.filter(x => x.state === "accepted").length],
          [t.dashRejected, a.filter(x => x.state === "rejected").length]
        ])
      },
      {
        key: "digitalLab", path: "/api/digital-lab", list: null,
        title: t.dashDigitalLab,
        count: (a, p) => safeCount(p.protocol_count) + safeCount(p.run_count) + safeCount(p.comparison_count),
        detail: (a, p) => dashboardMetrics([
          [t.dashLabProtocols, safeCount(p.protocol_count)],
          [t.dashLabRuns, safeCount(p.run_count)],
          [t.dashLabComparisons, safeCount(p.comparison_count)],
          [t.dashLabPublished, (p.protocols || []).filter(x => x.state === "published").length]
        ])
      },
      {
        key: "experiments", path: "/api/experiments", list: "experiments",
        title: t.dashExperiments,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([
          [t.dashPlans, a.length],
          [t.dashRecords, a.reduce((sum, item) => sum + safeCount(item.records), 0)]
        ])
      },
      {
        key: "optimization", path: "/api/optimization", list: "cycles",
        title: t.dashOptimization,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([[t.dashCycles, a.length]])
      },
      {
        key: "gaps", path: "/api/research-gaps", list: "gaps",
        title: t.dashGaps,
        count: (a, p) => safeCount(p.total),
        detail: (a, p) => dashboardMetrics([
          [t.dashHigh, p.priority_counts && p.priority_counts.high || 0],
          [t.dashMedium, p.priority_counts && p.priority_counts.medium || 0],
          [t.dashLow, p.priority_counts && p.priority_counts.low || 0]
        ])
      },
      {
        key: "graph", path: "/api/knowledge-graph", list: "nodes",
        title: t.dashGraph,
        count: (a) => a.length,
        detail: (a, p) => dashboardMetrics([
          [t.dashNodes, a.length],
          [t.dashRelations, safeCount(p.edges)]
        ])
      },
      {
        key: "scientificMemory", path: "/api/scientific-memory", list: "versions",
        title: t.dashScientificMemory,
        count: (a, p) => safeCount(p.current_versions),
        detail: (a, p) => dashboardMetrics([
          [t.dashMemoryVersions, safeCount(p.total_versions)],
          [t.dashCurrentMemory, safeCount(p.current_versions)],
          [t.dashContestedMemory, safeCount(p.contested_versions)]
        ])
      },
      {
        key: "literature", path: "/api/literature-watch", list: "reports",
        title: t.dashLiteratureWatch,
        count: (a) => a.reduce((sum, report) => sum + safeCount(report.candidates), 0),
        detail: (a) => {
          const candidates = a.flatMap(report => Array.isArray(report.candidates) ? report.candidates : []);
          return dashboardMetrics([
            [t.dashCandidates, candidates.length],
            [t.dashDuplicates, candidates.filter(x => x.classification === "possible_duplicate").length],
            [t.dashTitleMatches, candidates.filter(x => x.classification === "possible_title_match").length]
          ]);
        }
      },
      {
        key: "disputes", path: "/api/disputes", list: null,
        title: t.dashDisputes,
        count: (a, p) => (p.detected_contradictions || []).length,
        detail: (a, p) => dashboardMetrics([
          [t.dashDetectedContradictions, (p.detected_contradictions || []).length],
          [t.dashOpenReviews, (p.review_cases || []).filter(x => x.state === "open" || x.state === "reviewing").length],
          [t.dashClosedReviews, (p.review_cases || []).filter(x => ["resolved", "unresolved", "insufficient_evidence"].includes(x.state)).length]
        ])
      },
      {
        key: "peerReviews", path: "/api/collaboration/peer-reviews", list: "reviews",
        title: t.dashPeerReviews,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([
          [t.dashReviewOpen, a.filter(x => x.status === "open").length],
          [t.dashReviewCompleted, a.filter(x => x.status === "completed").length],
          [t.dashReviewSubmissions, a.reduce((sum, x) => sum + safeCount(x.submission_count), 0)]
        ])
      },
      {
        key: "collaboration", path: "/api/collaboration/recommendations", list: "recommendations",
        title: t.dashCollaboration,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([
          [t.dashRecommendations, a.length],
          [t.dashTargets, new Set(a.map(x => x.target_campaign_id)).size],
          [t.dashUnverified, a.filter(x => x.verification_state === "unverified").length]
        ])
      },
      {
        key: "campaignWatch", path: "/api/literature-watch/campaigns", list: null,
        title: t.dashCampaignWatch,
        count: (a, p) => (p.subscriptions || []).filter(x => x.enabled).length,
        detail: (a, p) => dashboardMetrics([
          [t.dashSubscriptions, (p.subscriptions || []).filter(x => x.enabled).length],
          [t.dashNewLeads, (p.runs || []).reduce((sum, x) => sum + safeCount(x.new_candidate_ids), 0)],
          [t.dashWatchRuns, (p.runs || []).length]
        ])
      },
      {
        key: "timeline", path: "/api/research-timeline", list: "events",
        title: t.dashTimeline,
        count: (a, p) => safeCount(p.total_events),
        detail: (a) => dashboardMetrics([
          [t.dashTimelineEvents, a.length],
          [t.dashTimelineCampaigns, new Set(a.map(x => x.campaign_id).filter(Boolean)).size],
          [t.dashTimelineKinds, new Set(a.map(x => x.kind)).size]
        ])
      },
      {
        key: "events", path: "/api/events", list: null,
        title: t.dashActivity,
        count: (a) => a.length,
        detail: (a) => dashboardMetrics([[t.dashRecent, a.length]])
      }
    ];
    const results = await Promise.all(definitions.map(async (item) => {
      try {
        const payload = await apiGet(item.path);
        const array = pickArray(payload, item.list || "");
        return { item, payload, array, error: false };
      } catch { return { item, payload: null, array: [], error: true }; }
    }));
    if (requestId !== dashboardRequest) return;
    results.forEach(({ item, payload, array, error }) => {
      const count = error ? 0 : item.count(array, payload || {});
      const detail = error ? t.dashEndpointUnavailable : item.detail(array, payload || {});
      dashboardGrid.append(makeDashboardCard(
        item.title, error ? "—" : count, detail,
        error ? "error" : count ? "live" : "empty"
      ));
    });

    const campaignResult = results.find(result => result.item.key === "campaigns");
    if (campaignResult && !campaignResult.error) {
      const campaigns = campaignResult.array.slice(0, 25);
      const conflictReports = await Promise.all(campaigns.map(async campaign => {
        const id = campaign.campaign_id;
        if (!id) return 0;
        try {
          const report = await apiGet("/api/collaboration/campaign/" + encodeURIComponent(id) + "/conflicts");
          return safeCount(report.contradictions);
        } catch { return 0; }
      }));
      if (requestId !== dashboardRequest) return;
      const totalConflicts = conflictReports.reduce((sum, value) => sum + value, 0);
      dashboardGrid.append(makeDashboardCard(
        t.dashConflicts, totalConflicts,
        totalConflicts ? t.dashPending + ": " + totalConflicts : t.dashNoData,
        totalConflicts ? "live" : "empty"
      ));
    }
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
