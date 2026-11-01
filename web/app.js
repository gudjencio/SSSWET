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
  let selectedKnowledgeNodeId = null;
  let currentKnowledgeGraph = { nodes: [], edges: [] };
  let currentResearchOpportunities = { opportunities: [] };
  let currentCampaigns = [];
  let currentTimelinePayload = { events: [], total_events: 0, event_kinds: [] };

  const languageCatalog = window.SSSWET_LANGUAGE_CATALOG || Object.keys(locales).map(code => code + "|" + (locales[code].name || code));
  const languageCodes = languageCatalog.map(item => item.split("|")[0]);
  function languageLabel(code, selectedCode) {
    const native = (locales[code] && locales[code].name) || languageCatalog.find(item => item.startsWith(code + "|"))?.split("|")[1] || code;
    try {
      const display = new Intl.DisplayNames([selectedCode || "en"], { type: "language" }).of(code);
      if (display && display.toLowerCase() !== code.toLowerCase()) return display;
    } catch (_) {}
    return native;
  }
  const languageOptions = new Map();
  languageCodes.forEach(code => {
    const option = document.createElement("option");
    option.value = code;
    languageOptions.set(code, option);
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
    languageOptions.forEach((option, code) => { option.textContent = languageLabel(code, selected); });
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const value = t[element.dataset.i18n];
      if (typeof value === "string") element.textContent = value;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
      const value = t[element.dataset.i18nAria];
      if (typeof value === "string") element.setAttribute("aria-label", value);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const value = t[element.dataset.i18nPlaceholder];
      if (typeof value === "string") element.setAttribute("placeholder", value);
    });
    safeSaveLanguage(selected);
    refreshStatus();
    if (lastView === "ready") showAgentWelcome();
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

  function showAgentWelcome() {
    const copy = (window.SSSWET_AGENT_COPY || {})[currentLanguage()]
      || (window.SSSWET_AGENT_COPY || {}).en;
    if (!copy) { showMessage(currentTranslations().ready); return; }
    lastView = "ready";
    dashboard.hidden = true;
    feed.hidden = false;
    const fragment = document.createDocumentFragment();
    const intro = document.createElement("p");
    intro.className = "feed-line agent-intro";
    const marker = document.createElement("span");
    marker.textContent = "●";
    const lead = document.createElement("strong");
    lead.textContent = copy.welcome;
    intro.append(marker, lead, document.createTextNode(" " + copy.summary));
    fragment.append(intro);

    const roles = document.createElement("div");
    roles.className = "agent-role-list";
    copy.roles.forEach((role, index) => {
      const article = document.createElement("article");
      article.className = "agent-role";
      const avatar = document.createElement("span");
      avatar.className = "agent-avatar agent-avatar-" + (index + 1);
      avatar.setAttribute("aria-hidden", "true");
      avatar.innerHTML = '<span class="agent-robot-head"><i></i><i></i></span><span class="agent-robot-body"></span>';
      const identity = document.createElement("div");
      identity.className = "agent-role-copy";
      const heading = document.createElement("strong");
      heading.textContent = role.name;
      const description = document.createElement("p");
      description.textContent = role.description;
      identity.append(heading, description);
      article.append(avatar, identity);
      roles.append(article);
    });
    fragment.append(roles);

    const stepsTitle = document.createElement("p");
    stepsTitle.className = "agent-section-title";
    stepsTitle.textContent = copy.stepsTitle;
    fragment.append(stepsTitle);
    const steps = document.createElement("ol");
    steps.className = "agent-steps";
    copy.steps.forEach((step) => {
      const item = document.createElement("li");
      item.textContent = step;
      steps.append(item);
    });
    fragment.append(steps);

    const questionsTitle = document.createElement("p");
    questionsTitle.className = "agent-section-title";
    questionsTitle.textContent = copy.questionsTitle;
    fragment.append(questionsTitle);
    const questions = document.createElement("div");
    questions.className = "agent-questions";
    const actions = [
      ["working", showActivity],
      ["evidence", showDiscoveries],
      ["review", showVerified]
    ];
    actions.forEach(([key, action]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "agent-question";
      button.textContent = copy.questions[key];
      button.addEventListener("click", action);
      questions.append(button);
    });
    fragment.append(questions);

    const note = document.createElement("p");
    note.className = "agent-disclaimer";
    note.textContent = copy.disclaimer;
    fragment.append(note);
    feed.replaceChildren(fragment);
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


  function renderOpportunityList(payload) {
    currentResearchOpportunities = payload || { opportunities: [] };
    const container = document.getElementById("opportunity-list");
    container.replaceChildren();
    const t = currentTranslations();
    let items = Array.isArray(payload && payload.opportunities) ? payload.opportunities : [];
    if (selectedKnowledgeNodeId) {
      items = items.filter(item => (item.graph_node_ids || []).includes(selectedKnowledgeNodeId));
    }
    if (!items.length) {
      const empty = document.createElement("p");
      empty.className = "visual-empty";
      empty.textContent = selectedKnowledgeNodeId ? t.noNodeOpportunities : t.opportunityEmpty;
      container.append(empty);
      return;
    }
    items.slice(0, 12).forEach((item) => {
      const details = document.createElement("details");
      details.className = "opportunity-item";
      const summary = document.createElement("summary");
      const title = document.createElement("strong");
      title.textContent = item.title || item.opportunity_id;
      const meta = document.createElement("span");
      meta.className = "opportunity-meta";
      meta.textContent = (item.kind === "research_gap" ? t.gapSignal : t.linkSignal)
        + " · " + String(item.priority || "medium").toUpperCase();
      summary.append(title, meta);
      const body = document.createElement("div");
      body.className = "opportunity-body";
      const description = document.createElement("p");
      description.textContent = item.summary || "";
      const action = document.createElement("p");
      action.textContent = t.suggestedAction + ": " + (item.suggested_action || "");
      const refs = document.createElement("p");
      refs.className = "opportunity-references";
      refs.textContent = t.references + ": " + (item.graph_node_ids || []).join(", ")
        + ((item.campaign_ids || []).length ? " · " + t.campaignsShort + ": " + item.campaign_ids.join(", ") : "");
      body.append(description, action, refs);
      details.append(summary, body);
      container.append(details);
    });
    const notice = document.createElement("p");
    notice.className = "visual-disclaimer";
    notice.textContent = t.opportunityDisclaimer;
    container.append(notice);
  }

  function renderNodeInspector(nodeId) {
    const container = document.getElementById("node-inspector");
    container.replaceChildren();
    const t = currentTranslations();
    const node = currentKnowledgeGraph.nodes.find(item => item.node_id === nodeId);
    if (!node) {
      const empty = document.createElement("p");
      empty.className = "visual-empty";
      empty.textContent = t.inspectorEmpty;
      container.append(empty);
      return;
    }
    const heading = document.createElement("h4");
    heading.textContent = node.label || node.node_id;
    const type = document.createElement("p");
    type.className = "inspector-meta";
    type.textContent = [node.node_type || t.unknownType, node.verification_state || t.unverifiedState].join(" · ");
    const description = document.createElement("p");
    description.textContent = node.description || t.noDescription;
    const id = document.createElement("p");
    id.className = "inspector-id";
    id.textContent = t.nodeIdentifier + ": " + node.node_id;
    container.append(heading, type, description, id);

    const metadata = node.metadata && typeof node.metadata === "object" ? node.metadata : {};
    const campaignId = metadata.campaign_id || node.campaign_id;
    if (campaignId) {
      const campaign = document.createElement("p");
      campaign.className = "inspector-meta";
      campaign.textContent = t.campaignsShort + ": " + String(campaignId);
      container.append(campaign);
    }
    const related = currentKnowledgeGraph.edges.filter(edge =>
      edge.source_id === nodeId || edge.target_id === nodeId
    );
    const relationHeading = document.createElement("h5");
    relationHeading.textContent = t.recordedConnections + " (" + related.length + ")";
    container.append(relationHeading);
    if (!related.length) {
      const none = document.createElement("p");
      none.className = "visual-empty";
      none.textContent = t.noRecordedConnections;
      container.append(none);
    } else {
      const list = document.createElement("ul");
      list.className = "inspector-connections";
      related.slice(0, 30).forEach(edge => {
        const otherId = edge.source_id === nodeId ? edge.target_id : edge.source_id;
        const other = currentKnowledgeGraph.nodes.find(item => item.node_id === otherId);
        const li = document.createElement("li");
        const relation = document.createElement("strong");
        relation.textContent = edge.relation || t.recordedRelation;
        const target = document.createElement("button");
        target.type = "button";
        target.className = "text-link";
        target.textContent = other ? (other.label || other.node_id) : otherId;
        target.addEventListener("click", () => selectKnowledgeNode(otherId));
        const note = document.createElement("span");
        note.textContent = edge.note ? " — " + edge.note : "";
        li.append(relation, document.createTextNode(" · "), target, note);
        list.append(li);
      });
      container.append(list);
    }
    const disclaimer = document.createElement("p");
    disclaimer.className = "visual-disclaimer";
    disclaimer.textContent = t.nodeDisclaimer;
    container.append(disclaimer);
  }

  function selectKnowledgeNode(nodeId) {
    selectedKnowledgeNodeId = nodeId;
    renderNodeInspector(nodeId);
    renderOpportunityList(currentResearchOpportunities);
    document.querySelectorAll(".knowledge-node").forEach(group => {
      group.classList.toggle("is-selected", group.dataset.nodeId === nodeId);
      group.setAttribute("aria-pressed", group.dataset.nodeId === nodeId ? "true" : "false");
    });
  }

  function renderKnowledgeMap(payload) {
    currentKnowledgeGraph = payload || { nodes: [], edges: [] };
    const container = document.getElementById("knowledge-map");
    container.replaceChildren();
    const t = currentTranslations();
    const nodes = Array.isArray(payload && payload.nodes) ? payload.nodes.slice(0, 24) : [];
    const edges = Array.isArray(payload && payload.edges) ? payload.edges : [];
    if (!nodes.length) {
      const empty = document.createElement("p");
      empty.className = "visual-empty";
      empty.textContent = t.mapEmpty;
      container.append(empty);
      renderNodeInspector(null);
      return;
    }
    if (selectedKnowledgeNodeId && !nodes.some(node => node.node_id === selectedKnowledgeNodeId)) {
      selectedKnowledgeNodeId = null;
    }
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 720 320");
    svg.setAttribute("role", "group");
    svg.setAttribute("aria-label", t.mapAccessible);
    const positions = new Map();
    nodes.forEach((node, index) => {
      const angle = (Math.PI * 2 * index / nodes.length) - Math.PI / 2;
      positions.set(node.node_id, {x: 360 + Math.cos(angle) * (nodes.length > 2 ? 245 : 150), y: 160 + Math.sin(angle) * 112});
    });
    edges.forEach((edge) => {
      const a = positions.get(edge.source_id), b = positions.get(edge.target_id);
      if (!a || !b) return;
      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
      line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
      line.setAttribute("class", "knowledge-edge");
      const title = document.createElementNS(ns, "title");
      title.textContent = edge.relation || t.recordedRelation;
      line.append(title); svg.append(line);
    });
    nodes.forEach((node) => {
      const point = positions.get(node.node_id);
      const group = document.createElementNS(ns, "g");
      group.setAttribute("class", "knowledge-node" + (node.node_id === selectedKnowledgeNodeId ? " is-selected" : ""));
      group.setAttribute("tabindex", "0");
      group.setAttribute("role", "button");
      group.setAttribute("aria-label", t.selectNode + ": " + (node.label || node.node_id));
      group.setAttribute("aria-pressed", node.node_id === selectedKnowledgeNodeId ? "true" : "false");
      group.dataset.nodeId = node.node_id;
      const circle = document.createElementNS(ns, "circle");
      circle.setAttribute("cx", point.x); circle.setAttribute("cy", point.y); circle.setAttribute("r", "8");
      const label = document.createElementNS(ns, "text");
      label.setAttribute("x", point.x); label.setAttribute("y", point.y + 22);
      label.setAttribute("text-anchor", "middle");
      label.textContent = String(node.label || node.node_id).slice(0, 28);
      const title = document.createElementNS(ns, "title");
      title.textContent = (node.label || node.node_id) + " · " + (node.node_type || "record") + " · " + (node.verification_state || "unverified");
      group.append(circle, label, title);
      group.addEventListener("click", () => selectKnowledgeNode(node.node_id));
      group.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectKnowledgeNode(node.node_id);
        }
      });
      svg.append(group);
    });
    container.append(svg);
    const legend = document.createElement("p");
    legend.className = "map-legend";
    legend.textContent = nodes.length + " " + t.mapNodes + " · "
      + edges.filter(edge => positions.has(edge.source_id) && positions.has(edge.target_id)).length
      + " " + t.mapRelations + " · " + t.mapDisclaimer;
    container.append(legend);
    renderNodeInspector(selectedKnowledgeNodeId);
  }

  function renderLabReproducibility(matrixPayload, datasetPayload) {
    const t = currentTranslations();
    const summary = document.getElementById("lab-repro-summary");
    const matrix = document.getElementById("lab-repro-matrix");
    const datasets = document.getElementById("lab-dataset-audit");
    summary.replaceChildren(); matrix.replaceChildren(); datasets.replaceChildren();

    const metric = (label, value) => {
      const item = document.createElement("div");
      item.className = "lab-repro-metric";
      const number = document.createElement("strong");
      number.textContent = String(value);
      const caption = document.createElement("span");
      caption.textContent = label;
      item.append(number, caption);
      return item;
    };
    if (matrixPayload) {
      summary.append(
        metric(t.labProtocolGroups, matrixPayload.protocol_group_count || 0),
        metric(t.labRecordedRuns, matrixPayload.run_count || 0),
        metric(t.labPendingPairs, (matrixPayload.protocol_groups || []).reduce((n, group) => n + (group.pending_comparison_count || 0), 0))
      );
      const groups = Array.isArray(matrixPayload.protocol_groups) ? matrixPayload.protocol_groups : [];
      if (!groups.length) {
        const empty = document.createElement("p"); empty.className = "visual-empty";
        empty.textContent = t.labNoRuns; matrix.append(empty);
      }
      groups.slice(0, 12).forEach(group => {
        const article = document.createElement("article"); article.className = "lab-repro-item";
        const heading = document.createElement("h5"); heading.textContent = (group.protocol_title || group.protocol_id) + " · v" + group.protocol_version;
        const meta = document.createElement("p"); meta.textContent = (group.run_count || 0) + " " + t.labRecordedRuns + " · " + (group.distinct_campaign_count || 0) + " " + t.labCampaigns;
        const pending = document.createElement("p"); pending.className = "lab-repro-status";
        pending.textContent = (group.pending_comparison_count || 0) + " " + t.labPendingPairs;
        article.append(heading, meta, pending);
        (group.cross_campaign_pairs || []).slice(0, 8).forEach(pair => {
          const row = document.createElement("p"); row.className = "lab-repro-pair";
          row.textContent = pair.left_run_id + " ↔ " + pair.right_run_id + " · "
            + (pair.comparison_recorded ? t.labCompared : t.labComparisonPending);
          article.append(row);
        });
        matrix.append(article);
      });
    } else {
      const error = document.createElement("p"); error.className = "visual-empty";
      error.textContent = t.dashEndpointUnavailable; matrix.append(error);
    }

    if (datasetPayload) {
      const integrity = datasetPayload.integrity || {};
      const datasetsMetric = metric(t.labDatasetVersions, datasetPayload.version_count || 0);
      const integrityMetric = metric(t.labIntegrityChecks, integrity.versions_checked || 0);
      const state = document.createElement("span");
      state.className = "lab-integrity-state" + (integrity.all_intact ? " is-intact" : " is-warning");
      state.textContent = integrity.all_intact ? t.labFingerprintsIntact : t.labIntegrityWarning;
      datasets.append(datasetsMetric, integrityMetric, state);
      const shared = Array.isArray(datasetPayload.shared_content_candidates) ? datasetPayload.shared_content_candidates : [];
      const heading = document.createElement("h5"); heading.textContent = t.labSharedContentCandidates + " (" + shared.length + ")";
      datasets.append(heading);
      if (!shared.length) {
        const empty = document.createElement("p"); empty.className = "visual-empty";
        empty.textContent = t.labNoSharedContent; datasets.append(empty);
      }
      shared.slice(0, 8).forEach(candidate => {
        const item = document.createElement("p"); item.className = "lab-repro-pair";
        item.textContent = candidate.content_sha256.slice(0, 16) + "… · "
          + (candidate.records || []).length + " " + t.labDatasetVersions + " · "
          + (candidate.campaigns || []).join(", ");
        datasets.append(item);
      });
      const note = document.createElement("p"); note.className = "timeline-caption";
      note.textContent = t.labFilesNotStored; datasets.append(note);
    } else {
      const error = document.createElement("p"); error.className = "visual-empty";
      error.textContent = t.dashEndpointUnavailable; datasets.append(error);
    }
  }

  function renderResearchTimeline(payload) {
    currentTimelinePayload = payload || { events: [], total_events: 0, event_kinds: [] };
    const container = document.getElementById("research-timeline");
    container.replaceChildren();
    const t = currentTranslations();
    const allEvents = Array.isArray(currentTimelinePayload.events) ? currentTimelinePayload.events : [];
    const search = (document.getElementById("timeline-search").value || "").trim().toLocaleLowerCase();
    const selectedKind = document.getElementById("timeline-kind").value || "";
    const events = allEvents.filter(event => {
      if (selectedKind && event.kind !== selectedKind) return false;
      if (!search) return true;
      const refs = event.references && typeof event.references === "object" ? event.references : {};
      const searchable = [
        event.title, event.description, event.kind, event.campaign_id,
        event.event_id, JSON.stringify(refs)
      ].filter(Boolean).join(" ").toLocaleLowerCase();
      return searchable.includes(search);
    });
    if (!events.length) {
      const empty = document.createElement("p");
      empty.className = "visual-empty";
      empty.textContent = allEvents.length ? t.timelineNoMatches : t.timelineEmpty;
      container.append(empty);
      return;
    }
    const list = document.createElement("ol");
    list.className = "timeline-list";
    events.slice(0, 100).forEach(event => {
      const item = document.createElement("li");
      item.className = "timeline-event";
      const date = document.createElement("time");
      date.className = "timeline-date";
      const parsed = new Date(event.occurred_at);
      date.dateTime = event.occurred_at || "";
      date.textContent = Number.isNaN(parsed.getTime())
        ? event.occurred_at || t.dateUnavailable
        : new Intl.DateTimeFormat(currentLanguage(), { dateStyle: "medium", timeStyle: "short" }).format(parsed);
      const heading = document.createElement("h4");
      heading.textContent = event.title || event.kind || t.timelineEvent;
      const kind = document.createElement("span");
      kind.className = "timeline-kind";
      kind.textContent = String(event.kind || t.timelineEvent).replaceAll("_", " ");
      const description = document.createElement("p");
      description.textContent = event.description || t.noDescription;
      item.append(date, heading, kind, description);
      if (event.campaign_id) {
        const campaign = document.createElement("p");
        campaign.className = "timeline-reference";
        campaign.textContent = t.campaignsShort + ": " + event.campaign_id;
        item.append(campaign);
      }
      const refs = event.references && typeof event.references === "object" ? event.references : {};
      const referenceParts = [];
      for (const key of ["graph_node_ids", "experiment_ids", "source_ids", "run_ids"]) {
        if (Array.isArray(refs[key]) && refs[key].length) referenceParts.push(key.replaceAll("_", " ") + ": " + refs[key].join(", "));
      }
      for (const key of ["version_id", "dispute_case_id", "protocol_id", "comparison_id", "review_id", "watch_id"]) {
        if (refs[key]) referenceParts.push(key.replaceAll("_", " ") + ": " + refs[key]);
      }
      if (referenceParts.length) {
        const references = document.createElement("p");
        references.className = "timeline-reference";
        references.textContent = referenceParts.join(" · ");
        item.append(references);
      }
      if (event.scientific_validity_established !== true) {
        const status = document.createElement("span");
        status.className = "timeline-status";
        status.textContent = t.timelineNotValidation;
        item.append(status);
      }
      list.append(item);
    });
    container.append(list);
    const summary = document.createElement("p");
    summary.className = "timeline-summary";
    summary.textContent = events.length + " / " + (currentTimelinePayload.total_events ?? events.length) + " " + t.timelineShown
      + (currentTimelinePayload.undated_records_omitted ? " · " + t.timelineUndated : "");
    container.append(summary);
  }

  function populateTimelineKinds(kinds) {
    const select = document.getElementById("timeline-kind");
    const selected = select.value;
    select.replaceChildren();
    const all = document.createElement("option");
    all.value = "";
    all.textContent = currentTranslations().allEventTypes;
    select.append(all);
    (Array.isArray(kinds) ? kinds : []).forEach(kind => {
      const option = document.createElement("option");
      option.value = kind;
      option.textContent = String(kind).replaceAll("_", " ");
      select.append(option);
    });
    select.value = (kinds || []).includes(selected) ? selected : "";
  }

  async function loadResearchTimeline(campaignId = "") {
    const endpoint = "/api/research-timeline?limit=200"
      + (campaignId ? "&campaign_id=" + encodeURIComponent(campaignId) : "");
    const container = document.getElementById("research-timeline");
    container.setAttribute("aria-busy", "true");
    try {
      const payload = await apiGet(endpoint);
      populateTimelineKinds(payload.event_kinds);
      renderResearchTimeline(payload);
    } catch {
      container.replaceChildren();
      const error = document.createElement("p");
      error.className = "visual-empty";
      error.textContent = currentTranslations().timelineUnavailable;
      container.append(error);
    } finally {
      container.setAttribute("aria-busy", "false");
    }
  }

  function populateTimelineCampaigns(campaigns) {
    currentCampaigns = Array.isArray(campaigns) ? campaigns : [];
    const select = document.getElementById("timeline-campaign");
    const selected = select.value;
    select.replaceChildren();
    const all = document.createElement("option");
    all.value = "";
    all.textContent = currentTranslations().allCampaigns;
    select.append(all);
    currentCampaigns.forEach(campaign => {
      if (!campaign.campaign_id) return;
      const option = document.createElement("option");
      option.value = campaign.campaign_id;
      option.textContent = campaign.title || campaign.campaign_id;
      select.append(option);
    });
    select.value = currentCampaigns.some(campaign => campaign.campaign_id === selected) ? selected : "";
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
        key: "opportunities", path: "/api/research-opportunities", list: "opportunities",
        title: t.opportunityTitle,
        count: (a, p) => safeCount(p.total),
        detail: (a, p) => dashboardMetrics([
          [t.gapSignal, p.signal_counts && p.signal_counts.research_gaps || 0],
          [t.linkSignal, p.signal_counts && p.signal_counts.interdisciplinary_links || 0]
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
    const [reproductionMatrix, datasetAudit] = await Promise.all([
      apiGet("/api/digital-lab/reproduction-matrix").catch(() => null),
      apiGet("/api/digital-lab/datasets").catch(() => null)
    ]);
    if (requestId !== dashboardRequest) return;
    renderLabReproducibility(reproductionMatrix, datasetAudit);
    const graphResult = results.find(result => result.item.key === "graph");
    renderKnowledgeMap(graphResult && !graphResult.error ? graphResult.payload : {nodes: [], edges: []});
    const opportunityResult = results.find(result => result.item.key === "opportunities");
    renderOpportunityList(opportunityResult && !opportunityResult.error ? opportunityResult.payload : {opportunities: []});
    const campaignData = campaignResult && !campaignResult.error ? campaignResult.array : [];
    populateTimelineCampaigns(campaignData);
    await loadResearchTimeline(document.getElementById("timeline-campaign").value);
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
  document.getElementById("timeline-campaign").addEventListener("change", event => loadResearchTimeline(event.target.value));
  document.getElementById("timeline-search").addEventListener("input", () => renderResearchTimeline(currentTimelinePayload));
  document.getElementById("timeline-kind").addEventListener("change", () => renderResearchTimeline(currentTimelinePayload));
  languageSelect.addEventListener("change", () => setLanguage(languageSelect.value));
  setLanguage(safeReadLanguage() || preferredLanguage());
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
})();
