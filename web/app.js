(() => {
  "use strict";

  const locales = window.SSSWET_LOCALES || {};
  const fallback = locales.en || {};
  const languageSelect = document.getElementById("language");
  const feed = document.getElementById("feed");
  const localApiBases = ["http://127.0.0.1:8765", "http://localhost:8765"];
  const remoteApiBase = String(window.SSSWET_REMOTE_API_BASE || "").replace(/\/+$/, "");
  const sameOriginBase = window.location.origin;
  const isLocalOrigin = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(sameOriginBase);
  let activeApiBase = isLocalOrigin ? sameOriginBase : null;
  let apiDiscoveryPromise = null;
  let lastApiFailure = "The hosted research service has not responded yet.";

  async function probeApi(base, timeoutMs) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(new URL("/api/status", base).toString(), {
        method: "GET", mode: "cors", headers: { Accept: "application/json" },
        cache: "no-store", signal: controller.signal
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const status = await response.json();
      if (status.service !== "SSSWET") throw new Error("Unexpected service response");
      return base;
    } finally { window.clearTimeout(timeout); }
  }

  async function discoverLocalApi(force = false) {
    if (activeApiBase && !force) return activeApiBase;
    if (apiDiscoveryPromise) return apiDiscoveryPromise;
    apiDiscoveryPromise = (async () => {
      const candidates = isLocalOrigin
        ? [...new Set([sameOriginBase, ...localApiBases])]
        : [...new Set([remoteApiBase, ...localApiBases].filter(Boolean))];
      let lastError = null;
      for (const base of candidates) {
        try {
          // Hosted services may need time to wake after an idle period.
          const timeoutMs = base === remoteApiBase ? 70000 : 1800;
          const winningBase = await probeApi(base, timeoutMs);
          activeApiBase = winningBase;
          window.SSSWET_API_BASE = winningBase;
          lastApiFailure = "";
          window.dispatchEvent(new CustomEvent("ssswet-engine-connection", {detail:{connected:true,base:winningBase,remote:winningBase===remoteApiBase}}));
          return winningBase;
        } catch (error) {
          lastError = error;
          lastApiFailure = error.name === "AbortError"
            ? "Research service did not respond within the connection timeout."
            : (error.message || "No research service responded.");
        }
      }
      activeApiBase = null;
      window.SSSWET_API_BASE = null;
      window.dispatchEvent(new CustomEvent("ssswet-engine-connection", {detail:{connected:false,error:lastApiFailure}}));
      throw new Error(lastError ? lastApiFailure : "No research API is configured.");
    })();
    try { return await apiDiscoveryPromise; }
    finally { apiDiscoveryPromise = null; }
  }

  window.ssswetApiFetch = async function(path, options = {}) {
    const base = await discoverLocalApi();
    try {
      const response = await fetch(new URL(path, base).toString(), {
        ...options,
        mode: "cors",
        cache: "no-store",
        headers: { Accept: "application/json", ...(options.headers || {}) }
      });
      if (!response.ok) {
        const httpError = new Error("HTTP " + response.status);
        httpError.status = response.status;
        throw httpError;
      }
      return response;
    } catch (error) {
      // An HTTP response proves that the local engine is reachable. Only
      // transport/CORS failures should change the connection state.
      if (!error.status) {
        activeApiBase = null;
        window.SSSWET_API_BASE = null;
        window.dispatchEvent(new CustomEvent("ssswet-engine-connection", {detail:{connected:false,error:error.message}}));
      }
      throw error;
    }
  };




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


  const brandNames = {
    en: ["SSSWET", "Super Soldier's Space Warping Engineering & Tech"],
    fr: ["ETDESS", "Équipements et technologies de distorsions spatiales pour super-soldats"],
    ja: ["SSSWET", "超兵士向け空間歪曲工学・技術"],
    es: ["SSSWET", "Ingeniería y tecnología de distorsión espacial para supersoldados"],
    de: ["SSSWET", "Weltraumkrümmungsingenieurwesen und -technologie für Supersoldaten"],
    it: ["SSSWET", "Ingegneria e tecnologia della distorsione spaziale per supersoldati"],
    pt: ["SSSWET", "Engenharia e tecnologia de distorção espacial para supersoldados"],
    nl: ["SSSWET", "Ruimtevervormingstechniek en -technologie voor supersoldaten"],
    ru: ["SSSWET", "Инженерия и технологии искривления пространства для суперсолдат"],
    uk: ["SSSWET", "Інженерія та технології викривлення простору для суперсолдатів"],
    ar: ["SSSWET", "هندسة وتقنيات تشويه الفضاء للجنود الخارقين"],
    he: ["SSSWET", "הנדסה וטכנולוגיית עיוות מרחב לחיילי־על"],
    ko: ["SSSWET", "슈퍼 솔저를 위한 공간 왜곡 공학 및 기술"],
    zh: ["SSSWET", "超级士兵空间扭曲工程与技术"],
    hi: ["SSSWET", "सुपर सैनिकों के लिए अंतरिक्ष विकृति अभियांत्रिकी और प्रौद्योगिकी"],
    id: ["SSSWET", "Rekayasa dan teknologi pelengkungan ruang untuk prajurit super"],
    tr: ["SSSWET", "Süper askerler için uzay bükme mühendisliği ve teknolojisi"],
    pl: ["SSSWET", "Inżynieria i technologia zakrzywiania przestrzeni dla superżołnierzy"],
    bn: ["SSSWET", "সুপার সৈনিকদের জন্য মহাকাশ বক্রায়ন প্রকৌশল ও প্রযুক্তি"],
    sw: ["SSSWET", "Uhandisi na teknolojia ya kupinda kwa anga kwa askari bora"],
    vi: ["SSSWET", "Kỹ thuật và công nghệ bẻ cong không gian dành cho siêu chiến binh"],
    fa: ["SSSWET", "مهندسی و فناوری خمیدگی فضا برای ابرسربازان"],
    ur: ["SSSWET", "سپر سپاہیوں کے لیے خلائی انحراف کی انجینئرنگ اور ٹیکنالوجی"],
    ta: ["SSSWET", "சூப்பர் வீரர்களுக்கான விண்வெளி வளைவு பொறியியல் மற்றும் தொழில்நுட்பம்"],
    te: ["SSSWET", "సూపర్ సైనికుల కోసం అంతరిక్ష వక్రీకరణ ఇంజినీరింగ్ మరియు సాంకేతికత"]
  };
  function applyProjectBranding(code) {
    const pair = brandNames[translationSource(code)] || brandNames.en;
    const mark = document.getElementById("brand-mark");
    const subtitle = document.getElementById("brand-subtitle");
    const heading = document.getElementById("title");
    if (mark) mark.textContent = pair[0];
    if (subtitle) subtitle.textContent = pair[1];
    if (heading) heading.textContent = pair[0];
    document.title = pair[0] + " — " + pair[1];
    document.querySelectorAll(".social-corner a").forEach(link => {
      link.title = link.dataset.social || link.title;
      link.setAttribute("aria-label", link.dataset.social || link.getAttribute("aria-label"));
    });
  }

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
  function translationSource(code) {
    if (code === "fr-CA") return "fr";
    if (code === "zh-CN" || code === "zh-TW") return "zh";
    return code;
  }
  function currentTranslations() { return { ...fallback, ...(locales[translationSource(currentLanguage())] || {}) }; }

  const voiceToggle = document.getElementById("voice-toggle");
  let voiceEnabled = Boolean(window.speechSynthesis && typeof SpeechSynthesisUtterance !== "undefined");
  let availableVoices = [];
  const speechSynthesisApi = window.speechSynthesis || null;
  function refreshVoices() {
    if (speechSynthesisApi) availableVoices = speechSynthesisApi.getVoices();
  }
  if (speechSynthesisApi) {
    refreshVoices();
    speechSynthesisApi.addEventListener?.("voiceschanged", refreshVoices);
  }
  function voiceLanguageMatches(voice, language) {
    const wanted = String(language || "en").toLowerCase();
    const actual = String(voice.lang || "").toLowerCase();
    return actual === wanted || actual.split("-")[0] === wanted.split("-")[0];
  }
  function chooseVoice(language, gender) {
    refreshVoices();
    if (!availableVoices.length) return null;
    const sameLanguage = availableVoices.filter(voice => voiceLanguageMatches(voice, language));
    if (!sameLanguage.length) return null;
    const candidates = sameLanguage;
    const feminine = /female|woman|zira|aria|jenny|samantha|susan|sara|ava|emma|olivia| victoria|natasha|google français|google français|amélie|audrey|marie|elsa/i;
    const masculine = /male|man|david|mark|guy|james|thomas|henri|paul|daniel|alex|george|fred|google uk english male/i;
    const genderPattern = gender === "female" ? feminine : masculine;
    const genderMatches = candidates.filter(voice =>
      (voice.gender && String(voice.gender).toLowerCase() === gender) || genderPattern.test(voice.name || "")
    );
    const pool = genderMatches.length ? genderMatches : candidates;
    const natural = /natural|neural|online|premium|enhanced|google|microsoft|siri/i;
    return pool.slice().sort((a, b) =>
      Number(natural.test(b.name || "")) - Number(natural.test(a.name || "")) ||
      Number(b.lang?.toLowerCase() === language.toLowerCase()) - Number(a.lang?.toLowerCase() === language.toLowerCase())
    )[0] || null;
  }
  function speakAsAgent(text, agentIndex = 0) {
    if (!voiceEnabled || !speechSynthesisApi || typeof SpeechSynthesisUtterance === "undefined") return;
    const spoken = String(text || "").replace(/\\s+/g, " ").trim().slice(0, 1800);
    if (!spoken) return;
    const utterance = new SpeechSynthesisUtterance(spoken);
    const requestedLanguage = currentLanguage();
    const copyLanguage = translationSource(requestedLanguage);
    const speechLanguage = (window.SSSWET_AGENT_COPY || {})[copyLanguage] ? requestedLanguage : "en";
    const gender = agentIndex === 1 ? "male" : "female";
    utterance.lang = speechLanguage;
    utterance.rate = 0.96;
    utterance.pitch = gender === "female" ? 1.04 : 0.94;
    utterance.volume = 1;
    const voice = chooseVoice(speechLanguage, gender);
    if (voice) utterance.voice = voice;
    speechSynthesisApi.speak(utterance);
  }
  function speakLongText(text, agentIndex = 0) {
    const normalized = String(text || "").replace(/\s+/g, " ").trim();
    if (!normalized) return;
    const sentences = normalized.match(/[^.!?。！？]+[.!?。！？]*/gu) || [normalized];
    let chunk = "";
    sentences.forEach(sentence => {
      if ((chunk + sentence).length > 1100 && chunk) { speakAsAgent(chunk, agentIndex); chunk = ""; }
      chunk += sentence;
    });
    if (chunk) speakAsAgent(chunk, agentIndex);
  }
  function readCurrentFeed() {
    const feed = document.getElementById("feed");
    if (!feed || !voiceEnabled) return;
    const clone = feed.cloneNode(true);
    clone.querySelectorAll("button").forEach(button => button.remove());
    speakLongText(clone.textContent || "", 0);
  }
  function speakWelcome(copy) {
    if (!voiceEnabled || !copy) return;
    speechSynthesisApi?.cancel();
    speakAsAgent(copy.welcome + " " + copy.summary, 0);
    copy.roles.forEach((role, index) => {
      const parts = Array.isArray(role) ? role : [role.name, role.description];
      speakAsAgent(parts.filter(Boolean).join(". "), index);
    });
  }
  function capitalizeInitial(value, language = currentLanguage()) {
    const characters = Array.from(String(value));
    const index = characters.findIndex(character => /\p{L}/u.test(character));
    if (index < 0) return String(value);
    characters[index] = characters[index].toLocaleUpperCase(language);
    return characters.join("");
  }
  function capitalizeInterfaceText(root = document.body) {
    if (!root || !document.createTreeWalker) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent || parent.closest('script,style,textarea,pre,code,svg,a[href^="mailto:"]')) continue;
      const updated = capitalizeInitial(node.nodeValue);
      if (updated !== node.nodeValue) node.nodeValue = updated;
    }
    if (root.querySelectorAll) {
      root.querySelectorAll("[placeholder],[aria-label]").forEach(element => {
        for (const attribute of ["placeholder", "aria-label"]) {
          if (element.hasAttribute(attribute)) {
            const value = element.getAttribute(attribute);
            const updated = capitalizeInitial(value);
            if (updated !== value) element.setAttribute(attribute, updated);
          }
        }
      });
    }
  }
  const capitalizationObserver = new MutationObserver(records => {
    records.forEach(record => {
      if (record.type === "characterData") capitalizeInterfaceText(record.target.parentElement);
      else record.addedNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
          const parent = node.parentElement;
          if (parent && !parent.closest('script,style,textarea,pre,code,svg,a[href^="mailto:"]')) {
            const updated = capitalizeInitial(node.nodeValue);
            if (updated !== node.nodeValue) node.nodeValue = updated;
          }
        } else if (node.nodeType === Node.ELEMENT_NODE) capitalizeInterfaceText(node);
      });
    });
  });
  capitalizationObserver.observe(document.body, { childList: true, subtree: true, characterData: true });

  function setLanguage(requested) {
    const selected = locales[requested] ? requested : "en";
    const t = { ...fallback, ...(locales[translationSource(selected)] || {}) };
    const direction = t.dir === "rtl" ? "rtl" : "ltr";
    applyProjectBranding(selected);
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
    if (voiceToggle) {
      voiceToggle.textContent = voiceEnabled ? (t.voiceDisable || "Disable voice") : (t.voiceEnable || "Enable voice");
      voiceToggle.setAttribute("aria-pressed", voiceEnabled ? "true" : "false");
    }
    capitalizeInterfaceText(document.body);
    safeSaveLanguage(selected);
    window.dispatchEvent(new CustomEvent("ssswet-language-changed", {detail:{language:selected}}));
    refreshStatus();
    if (lastView === "ready") showAgentWelcome();
    else if (lastView === "discoveries") showDiscoveries();
    else if (lastView === "activity") showActivity();
    else if (lastView === "verified") showVerified();
    else if (lastView === "dashboard") showDashboard();
  }

  function showMessage(message, agentIndex = 0, shouldSpeak = true) {
    dashboard.hidden = true;
    feed.hidden = false;
    const paragraph = document.createElement("p");
    paragraph.className = "feed-line";
    const marker = document.createElement("span");
    marker.textContent = "●";
    paragraph.append(marker, document.createTextNode(" " + message));
    feed.replaceChildren(paragraph);
    if (shouldSpeak) speakAsAgent(message, agentIndex);
  }

  function showAgentWelcome() {
    const copy = (window.SSSWET_AGENT_COPY || {})[translationSource(currentLanguage())]
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

    const teamTitle = document.createElement("p");
    teamTitle.className = "agent-section-title agent-team-title";
    teamTitle.textContent = currentLanguage() === "fr" ? "Équipe de recherche" : "Research team";
    fragment.append(teamTitle);

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
      heading.textContent = Array.isArray(role) ? role[0] : role.name;
      const description = document.createElement("p");
      description.textContent = Array.isArray(role) ? role[1] : role.description;
      identity.append(heading, description);
      const speakButton = document.createElement("button");
      speakButton.type = "button";
      speakButton.className = "agent-speak";
      speakButton.textContent = currentTranslations().voiceListen || "Listen";
      speakButton.setAttribute("aria-label", (currentTranslations().voiceListen || "Listen") + " — " + heading.textContent);
      speakButton.addEventListener("click", () => speakAsAgent(heading.textContent + ". " + description.textContent, index));
      article.append(avatar, identity, speakButton);
      roles.append(article);
    });
    fragment.append(roles);

    const questionsPanel = document.createElement("section");
    questionsPanel.className = "agent-questions-panel";
    const questionsTitle = document.createElement("p");
    questionsTitle.className = "agent-section-title";
    questionsTitle.textContent = copy.questionsTitle || (currentLanguage() === "fr" ? "Que souhaitez-vous demander aux bots ?" : "What would you like to ask the research bots?");
    questionsPanel.append(questionsTitle);
    const questions = document.createElement("div");
    questions.className = "agent-questions";
    const actions = [
      ["working", showActivity],
      ["evidence", showDiscoveries],
      ["review", showVerified]
    ];
    actions.forEach(([key, action], index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "agent-question";
      button.textContent = Array.isArray(copy.questions) ? copy.questions[index] : copy.questions[key];
      button.addEventListener("click", action);
      questions.append(button);
    });
    questionsPanel.append(questions);
    fragment.append(questionsPanel);

    const agentDetails = document.createElement("details");
    agentDetails.className = "agent-details";
    const agentSummary = document.createElement("summary");
    agentSummary.textContent = currentLanguage() === "fr" ? "Découvrir notre méthode de recherche" : "Explore our research workflow";
    agentDetails.append(agentSummary);

    const stepsTitle = document.createElement("p");
    stepsTitle.className = "agent-section-title";
    stepsTitle.textContent = copy.stepsTitle || (currentLanguage() === "fr" ? "Étapes de recherche" : "Research workflow");
    agentDetails.append(stepsTitle);
    const steps = document.createElement("ol");
    steps.className = "agent-steps";
    copy.steps.forEach((step) => {
      const item = document.createElement("li");
      item.textContent = step;
      steps.append(item);
    });
    agentDetails.append(steps);

    const note = document.createElement("p");
    note.className = "agent-disclaimer";
    note.textContent = copy.disclaimer;
    agentDetails.append(note);
    fragment.append(agentDetails);
    feed.replaceChildren(fragment);
    if (voiceEnabled) speakWelcome(copy);
  }

  async function apiGet(path) {
    const response = await window.ssswetApiFetch(path, { method: "GET" });
    if (!response.ok) throw new Error("HTTP " + response.status);
    return response.json();
  }
  async function apiPost(path, payload) {
    const response = await window.ssswetApiFetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || ("HTTP " + response.status));
    return result;
  }

  const priorityCriteria = [
    ["societal_benefit", "Societal benefit", 20],
    ["ecological_benefit", "Ecological and animal benefit", 20],
    ["evidence_maturity", "Evidence maturity", 15],
    ["technical_feasibility", "Technical feasibility", 15],
    ["resource_accessibility", "Resource accessibility", 10],
    ["safety_legal_readiness", "Safety and legal readiness", 20]
  ];
  let priorityAssessmentReport = null;

  function renderPriorityAssessments(report) {
    const fr = currentLanguage() === "fr";
    priorityAssessmentReport = report || null;
    const container = document.getElementById("priority-assessment-ranking");
    if (!container) return;
    container.replaceChildren();
    const ranked = Array.isArray(report && report.ranked) ? report.ranked : [];
    const incomplete = Array.isArray(report && report.incomplete) ? report.incomplete : [];
    const summary = document.createElement("p");
    summary.className = "priority-assessment-summary";
    summary.textContent = fr
      ? (report?.assessed_programmes ?? 0) + " programmes évalués · " + ranked.length + " classements complets · " + incomplete.length + " incomplets"
      : (report?.assessed_programmes ?? 0) + " programmes assessed · " + ranked.length + " complete rankings · " + incomplete.length + " incomplete";
    container.append(summary);
    if (!ranked.length && !incomplete.length) {
      const empty = document.createElement("p");
      empty.className = "visual-empty";
      empty.textContent = fr
        ? "Aucune évaluation de programme n’a encore été enregistrée. Les notes ne sont jamais déduites des descriptions du catalogue."
        : "No programme assessments have been recorded yet. Scores are never generated from catalogue descriptions.";
      container.append(empty);
    }
    ranked.forEach(item => {
      const article = document.createElement("article");
      article.className = "priority-ranking-item";
      const heading = document.createElement("div");
      heading.className = "priority-ranking-heading";
      const name = document.createElement("strong");
      name.textContent = "#" + item.rank + " · " + item.programme_id;
      const score = document.createElement("span");
      score.textContent = Number(item.score).toFixed(1) + " / 100";
      heading.append(name, score);
      const track = document.createElement("div");
      track.className = "priority-score-track";
      const fill = document.createElement("span");
      fill.style.width = Math.max(0, Math.min(100, Number(item.score))) + "%";
      track.append(fill);
      const meta = document.createElement("small");
      meta.textContent = (fr ? "Dernière évaluation · " : "Latest assessment · ") + (item.reviewer_label || (fr ? "Évaluateur non nommé" : "Reviewer not named"))
        + " · " + new Date(item.created_at).toLocaleDateString(fr ? "fr-FR" : "en-US");
      article.append(heading, track, meta);
      container.append(article);
    });
    if (incomplete.length) {
      const heading = document.createElement("h4");
      heading.className = "priority-incomplete-heading";
      heading.textContent = fr ? "Évaluations incomplètes — non classées" : "Incomplete assessments — not ranked";
      container.append(heading);
      incomplete.forEach(item => {
        const line = document.createElement("p");
        line.className = "priority-incomplete-item";
        line.textContent = item.programme_id + " · " + item.coverage_percent
          + (fr ? " % évalués · critères manquants : " : "% assessed · missing: ") + (item.missing_criteria || Object.keys(item.scores || {}).filter(key => item.scores[key] == null)).join(", ");
        container.append(line);
      });
    }
    const history = document.createElement("details");
    history.className = "priority-history";
    const summaryLine = document.createElement("summary");
    summaryLine.textContent = (fr ? "Historique des évaluations (" : "Assessment history (") + (report?.history_count ?? 0) + (fr ? " entrées)" : " entries)");
    history.append(summaryLine);
    (report?.history || []).slice(0, 40).forEach(item => {
      const row = document.createElement("p");
      row.textContent = item.programme_id + " · " + (item.score == null ? (fr ? "Incomplet" : "Incomplete") : Number(item.score).toFixed(1) + " / 100")
        + " · " + (item.reviewer_label || (fr ? "Évaluateur non nommé" : "Reviewer not named")) + " · " + new Date(item.created_at).toLocaleString(fr ? "fr-FR" : "en-US");
      history.append(row);
    });
    container.append(history);
    syncPriorityForm();
  }

  function syncPriorityForm() {
    const form = document.getElementById("priority-assessment-form");
    if (!form || !priorityAssessmentReport) return;
    const programme = form.elements.programme_id.value;
    const latest = [...(priorityAssessmentReport.ranked || []), ...(priorityAssessmentReport.incomplete || [])]
      .find(item => item.programme_id === programme);
    if (!latest) {
      priorityCriteria.forEach(([key]) => { if (form.elements[key]) form.elements[key].value = ""; });
      return;
    }
    priorityCriteria.forEach(([key]) => {
      const field = form.elements[key];
      if (field) field.value = latest.scores[key] == null ? "" : String(latest.scores[key]);
    });
  }

  async function loadPriorityAssessments() {
    const status = document.getElementById("priority-assessment-status");
    const container = document.getElementById("priority-assessment-ranking");
    if (!status || !container) return;
    const fr = currentLanguage() === "fr";
    status.textContent = fr ? "Chargement du registre local des évaluations…" : "Loading the local assessment register…";
    try {
      const [report, framework] = await Promise.all([
        apiGet("/api/research-priority-assessments"),
        apiGet("/api/research-priority-framework")
      ]);
      renderPriorityAssessments(report);
      status.textContent = fr
        ? "Registre local connecté · " + framework.criteria.length + " critères pondérés · pondération totale : " + framework.weight_total + " % · historique non modifiable"
        : "Local assessment register connected · " + framework.criteria.length + " weighted criteria · " + framework.weight_total + "% total weight · append-only history";
    } catch (error) {
      status.textContent = (fr ? "Registre local indisponible : " : "The local assessment register is unavailable: ") + String(error.message || error);
    }
  }

  const priorityForm = document.getElementById("priority-assessment-form");
  priorityForm?.elements.programme_id.addEventListener("change", syncPriorityForm);
  priorityForm?.addEventListener("submit", async event => {
    event.preventDefault();
    const button = priorityForm.querySelector('button[type="submit"]');
    const status = document.getElementById("priority-assessment-status");
    const formData = new FormData(priorityForm);
    const scores = {};
    priorityCriteria.forEach(([key]) => {
      const raw = formData.get(key);
      scores[key] = raw === "" ? null : Number(raw);
    });
    const evidenceRefs = String(formData.get("evidence_refs") || "").split("\\n")
      .map(value => value.trim()).filter(Boolean);
    button.disabled = true;
    status.textContent = currentLanguage() === "fr" ? "Enregistrement d’une nouvelle évaluation dans l’historique…" : "Saving a new append-only assessment…";
    try {
      await apiPost("/api/research-priority-assessments", {
        programme_id: formData.get("programme_id"),
        scores,
        reviewer_label: formData.get("reviewer_label"),
        rationale: formData.get("rationale"),
        evidence_refs: evidenceRefs
      });
      priorityForm.elements.rationale.value = "";
      priorityForm.elements.evidence_refs.value = "";
      await loadPriorityAssessments();
      status.textContent = currentLanguage() === "fr" ? "Évaluation enregistrée. La précédente reste conservée dans l’historique." : "Assessment saved. The previous assessment remains in the history.";
    } catch (error) {
      status.textContent = (currentLanguage() === "fr" ? "Évaluation non enregistrée : " : "Assessment not saved: ") + String(error.message || error);
    } finally {
      button.disabled = false;
    }
  });
  document.getElementById("priority-assessment-refresh")?.addEventListener("click", loadPriorityAssessments);

  async function refreshStatus() {
    const t = currentTranslations();
    try {
      const status = await apiGet("/api/status");
      agentCount.textContent = String(status.agents_total ?? 0).padStart(2, "0");
      systemStatus.textContent = t.statusOnline;
      systemStatus.dataset.connected = "true";
      const connectionPanel = document.getElementById("engine-connection");
      if (connectionPanel) connectionPanel.hidden = true;
    } catch (error) {
      agentCount.textContent = "—";
      systemStatus.textContent = t.statusOffline;
      systemStatus.dataset.connected = "false";
      const connectionPanel = document.getElementById("engine-connection");
      const connectionMessage = document.getElementById("engine-connection-message");
      const connectionDiagnostic = document.getElementById("engine-connection-diagnostic");
      if (connectionPanel) connectionPanel.hidden = false;
      if (connectionMessage) connectionMessage.textContent = document.documentElement.lang.toLowerCase().startsWith("fr")
        ? "Le moteur local n'est pas joignable. L'interface reste disponible en mode de consultation ; les données de recherche en direct apparaîtront dès que le moteur sera lancé et accessible."
        : "The local engine is not reachable. The interface remains available in fallback mode; live research data will appear when the engine is running and accessible.";
      if (connectionDiagnostic) {
        const detail = String(error && error.message || lastApiFailure || "").slice(0, 420);
        connectionDiagnostic.textContent = detail
          ? (document.documentElement.lang.toLowerCase().startsWith("fr") ? "Diagnostic de connexion : " : "Connection diagnostic: ") + detail
          : "";
        connectionDiagnostic.hidden = !detail;
      }
    }
  }

  function cleanDiscoverySummary(value) {
    let summary = String(value || "").trim();
    summary = summary.replace(/^\[UNVERIFIED\s*[·|]\s*[^\]]+\]\s*/i, "");
    const bibliographic = summary.match(/^Combined discovery returned (\d+) unique bibliographic lead\(s\) from Crossref and OpenAlex\.\s*Duplicate DOI records are collapsed\.\s*Metadata is not proof of quality or truth; review full texts, methods and independent evidence before drawing conclusions\.?$/i);
    if (bibliographic) {
      const count = bibliographic[1];
      return document.documentElement.lang.toLowerCase().startsWith("fr")
        ? "Découverte bibliographique : " + count + " références uniques trouvées dans Crossref et OpenAlex. Les DOI en double ont été regroupés ; la qualité scientifique des références reste à vérifier."
        : "Bibliographic discovery: " + count + " unique references found in Crossref and OpenAlex. Duplicate DOIs were merged; the scientific quality of these references remains unverified.";
    }
    return summary;
  }

function localizedDiscoveryRole(role, language) {
    const code = translationSource(language);
    const labels = {
      en: { independent_verifier: "independent verifier", general_researcher: "general researcher", medical_researcher: "medical researcher", materials_scientist: "materials scientist", research: "research agent", data_analyst: "data analyst", evidence_researcher: "evidence researcher", methodologist: "methodologist", safety_reviewer: "safety reviewer", ethics_reviewer: "ethics reviewer", literature_researcher: "literature researcher" },
      fr: { independent_verifier: "vérificateur indépendant", general_researcher: "chercheur généraliste", medical_researcher: "chercheur médical", materials_scientist: "spécialiste des matériaux", research: "agent de recherche", data_analyst: "analyste de données", evidence_researcher: "chercheur en preuves", methodologist: "méthodologiste", safety_reviewer: "réviseur sécurité", ethics_reviewer: "réviseur éthique", literature_researcher: "chercheur bibliographique" },
      es: { independent_verifier: "verificador independiente", general_researcher: "investigador general", medical_researcher: "investigador médico", materials_scientist: "científico de materiales", research: "agente de investigación", data_analyst: "analista de datos", evidence_researcher: "investigador de evidencias", methodologist: "metodólogo", safety_reviewer: "revisor de seguridad", ethics_reviewer: "revisor de ética", literature_researcher: "investigador bibliográfico" },
      de: { independent_verifier: "unabhängiger Prüfer", general_researcher: "allgemeiner Forscher", medical_researcher: "medizinischer Forscher", materials_scientist: "Materialwissenschaftler", research: "Forschungsagent", data_analyst: "Datenanalyst", evidence_researcher: "Evidenzforscher", methodologist: "Methodologe", safety_reviewer: "Sicherheitsprüfer", ethics_reviewer: "Ethikprüfer", literature_researcher: "Literaturforscher" },
      it: { independent_verifier: "verificatore indipendente", general_researcher: "ricercatore generale", medical_researcher: "ricercatore medico", materials_scientist: "scienziato dei materiali", research: "agente di ricerca", data_analyst: "analista dei dati", evidence_researcher: "ricercatore delle evidenze", methodologist: "metodologo", safety_reviewer: "revisore della sicurezza", ethics_reviewer: "revisore etico", literature_researcher: "ricercatore bibliografico" },
      pt: { independent_verifier: "verificador independente", general_researcher: "pesquisador geral", medical_researcher: "pesquisador médico", materials_scientist: "cientista de materiais", research: "agente de pesquisa", data_analyst: "analista de dados", evidence_researcher: "pesquisador de evidências", methodologist: "metodologista", safety_reviewer: "revisor de segurança", ethics_reviewer: "revisor de ética", literature_researcher: "pesquisador bibliográfico" },
      nl: { independent_verifier: "onafhankelijke verificateur", general_researcher: "algemeen onderzoeker", medical_researcher: "medisch onderzoeker", materials_scientist: "materiaalwetenschapper", research: "onderzoeksagent", data_analyst: "data-analist", evidence_researcher: "bewijsdeskundige", methodologist: "methodoloog", safety_reviewer: "veiligheidsbeoordelaar", ethics_reviewer: "ethiekbeoordelaar", literature_researcher: "literatuuronderzoeker" },
      ru: { independent_verifier: "независимый проверяющий", general_researcher: "общий исследователь", medical_researcher: "медицинский исследователь", materials_scientist: "специалист по материалам", research: "исследовательский агент", data_analyst: "аналитик данных", evidence_researcher: "исследователь доказательств", methodologist: "методолог", safety_reviewer: "эксперт по безопасности", ethics_reviewer: "эксперт по этике", literature_researcher: "библиографический исследователь" },
      uk: { independent_verifier: "незалежний перевіряльник", general_researcher: "загальний дослідник", medical_researcher: "медичний дослідник", materials_scientist: "фахівець із матеріалів", research: "дослідницький агент", data_analyst: "аналітик даних", evidence_researcher: "дослідник доказів", methodologist: "методолог", safety_reviewer: "експерт із безпеки", ethics_reviewer: "експерт з етики", literature_researcher: "бібліографічний дослідник" },
      ar: { independent_verifier: "مُحقّق مستقل", general_researcher: "باحث عام", medical_researcher: "باحث طبي", materials_scientist: "عالم مواد", research: "وكيل بحث", data_analyst: "محلل بيانات", evidence_researcher: "باحث أدلة", methodologist: "خبير منهجيات", safety_reviewer: "مراجع السلامة", ethics_reviewer: "مراجع الأخلاقيات", literature_researcher: "باحث مراجع علمية" },
      he: { independent_verifier: "מאמת עצמאי", general_researcher: "חוקר כללי", medical_researcher: "חוקר רפואי", materials_scientist: "מדען חומרים", research: "סוכן מחקר", data_analyst: "מנתח נתונים", evidence_researcher: "חוקר ראיות", methodologist: "מתודולוג", safety_reviewer: "בודק בטיחות", ethics_reviewer: "בודק אתיקה", literature_researcher: "חוקר ספרות מדעית" },
      ja: { independent_verifier: "独立検証担当", general_researcher: "総合研究担当", medical_researcher: "医学研究担当", materials_scientist: "材料科学者", research: "研究エージェント", data_analyst: "データ分析担当", evidence_researcher: "証拠研究担当", methodologist: "方法論専門家", safety_reviewer: "安全性審査担当", ethics_reviewer: "倫理審査担当", literature_researcher: "文献調査担当" },
      ko: { independent_verifier: "독립 검증 담당자", general_researcher: "일반 연구원", medical_researcher: "의학 연구원", materials_scientist: "재료 과학자", research: "연구 에이전트", data_analyst: "데이터 분석가", evidence_researcher: "증거 연구원", methodologist: "방법론 전문가", safety_reviewer: "안전성 검토자", ethics_reviewer: "윤리 검토자", literature_researcher: "문헌 연구원" },
      zh: { independent_verifier: "独立核验员", general_researcher: "综合研究员", medical_researcher: "医学研究员", materials_scientist: "材料科学家", research: "研究代理", data_analyst: "数据分析师", evidence_researcher: "证据研究员", methodologist: "方法学专家", safety_reviewer: "安全审查员", ethics_reviewer: "伦理审查员", literature_researcher: "文献研究员" },
      hi: { independent_verifier: "स्वतंत्र सत्यापक", general_researcher: "सामान्य शोधकर्ता", medical_researcher: "चिकित्सा शोधकर्ता", materials_scientist: "सामग्री वैज्ञानिक", research: "शोध एजेंट", data_analyst: "डेटा विश्लेषक", evidence_researcher: "साक्ष्य शोधकर्ता", methodologist: "कार्यप्रणाली विशेषज्ञ", safety_reviewer: "सुरक्षा समीक्षक", ethics_reviewer: "नैतिकता समीक्षक", literature_researcher: "साहित्य शोधकर्ता" }
    };
    const key = String(role || "research").trim().toLowerCase().replace(/[\s-]+/g, "_");
    return (labels[code] || labels.en)[key] || key.replace(/_/g, " ");
  }

  function localizedUnverifiedLabel(language) {
    const code = translationSource(language);
    const labels = {
      en: "Unverified", fr: "Non vérifié", es: "Sin verificar", de: "Nicht verifiziert",
      it: "Non verificato", pt: "Não verificado", nl: "Niet geverifieerd", ru: "Не проверено",
      uk: "Не перевірено", ar: "غير متحقق منه", he: "לא אומת", ja: "未検証",
      ko: "검증되지 않음", zh: "未经验证", hi: "असत्यापित"
    };
    return labels[code] || "Unverified";
  }

  function discoveryAgentCountLabel(language) {
    const code = translationSource(language);
    const labels = { fr: "agents", es: "agentes", de: "Agenten", it: "agenti", pt: "agentes", nl: "agenten", ru: "агентов", uk: "агентів", ar: "وكلاء", he: "סוכנים", ja: "エージェント", ko: "에이전트", zh: "个代理", hi: "एजेंट" };
    return labels[code] || "agents";
  }

function classifyDiscovery(group) {
    const text = (group.summary + " " + Array.from(group.roles.keys()).join(" ")).toLowerCase();
    if (/\b(error|exception|traceback|failed|failure|unavailable|timeout|connection refused|http 5\d\d)\b/.test(text)) return "technical";
    if (/\b(crossref|openalex|doi|bibliographic|bibliography|publication|journal article|citation|references found)\b/.test(text)) return "bibliographic";
    if (/\b(experiment|experimental|measurement|measured|observed|observation|laboratory result|dataset|simulation result|test result)\b/.test(text)) return "experimental";
    if (/\b(hypothesis|hypotheses|hypothesize|hypothesised|hypothesized|proposed mechanism|conjecture|research question)\b/.test(text)) return "hypothesis";
    if (/\b(verify|verifier|verification|verified|validation|validated|reproducib|independent review|peer review|reviewer|evidence check)\b/.test(text)) return "verification";
    return "other";
  }

  async function showDiscoveries() {
    lastView = "discoveries";
    const t = currentTranslations();
    const isFrench = document.documentElement.lang.toLowerCase().startsWith("fr");
    const categoryLabels = isFrench
      ? { all: "Toutes les catégories", bibliographic: "Découvertes bibliographiques", hypothesis: "Hypothèses", experimental: "Résultats expérimentaux", verification: "Vérifications", technical: "Alertes techniques", other: "Autres informations" }
      : { all: "All categories", bibliographic: "Bibliographic discoveries", hypothesis: "Hypotheses", experimental: "Experimental results", verification: "Verification", technical: "Technical alerts", other: "Other information" };
    const categoryOrder = ["bibliographic", "hypothesis", "experimental", "verification", "technical", "other"];
    try {
      const items = await apiGet("/api/discoveries");
      const groups = new Map();
      items.forEach((item) => {
        const summary = cleanDiscoverySummary(item.summary || item.statement || "");
        if (!summary) return;
        const key = summary.replace(/\s+/g, " ").toLocaleLowerCase();
        if (!groups.has(key)) groups.set(key, { summary, roles: new Map(), count: 0 });
        const group = groups.get(key);
        const role = String(item.role || "research").replace(/_/g, " ");
        group.roles.set(role, (group.roles.get(role) || 0) + 1);
        group.count += 1;
      });
      const entries = Array.from(groups.values()).map(group => ({ ...group, category: classifyDiscovery(group) }));
      dashboard.hidden = true;
      feed.hidden = false;
      feed.replaceChildren();
      if (!entries.length) {
        const empty = document.createElement("p");
        empty.className = "feed-line";
        empty.textContent = t.noDiscoveries;
        feed.append(empty);
        return;
      }

      const heading = document.createElement("p");
      heading.className = "feed-line discovery-heading";
      heading.textContent = isFrench
        ? items.length + " étapes examinées · " + entries.length + " messages distincts"
        : items.length + " steps reviewed · " + entries.length + " distinct messages";
      feed.append(heading);

      const toolbar = document.createElement("div");
      toolbar.className = "discovery-toolbar";
      const filterLabel = document.createElement("label");
      filterLabel.className = "discovery-filter-label";
      filterLabel.textContent = isFrench ? "Filtrer les résultats" : "Filter results";
      const filter = document.createElement("select");
      filter.className = "discovery-filter";
      filter.setAttribute("aria-label", filterLabel.textContent);
      [["all", categoryLabels.all], ...categoryOrder.map(key => [key, categoryLabels[key]])].forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label + (value === "all" ? "" : " (" + entries.filter(entry => entry.category === value).length + ")");
        filter.append(option);
      });
      toolbar.append(filterLabel, filter);
      feed.append(toolbar);

      const list = document.createElement("div");
      list.className = "discovery-list";
      feed.append(list);
      const renderEntries = () => {
        list.replaceChildren();
        const visible = filter.value === "all" ? entries : entries.filter(entry => entry.category === filter.value);
        if (!visible.length) {
          const empty = document.createElement("p");
          empty.className = "feed-line";
          empty.textContent = isFrench ? "Aucun résultat dans cette catégorie." : "No results in this category.";
          list.append(empty);
          return;
        }
        visible.forEach(group => {
          const paragraph = document.createElement("article");
          paragraph.className = "feed-line discovery-item category-" + group.category;
          const top = document.createElement("div");
          top.className = "discovery-item-top";
          const category = document.createElement("span");
          category.className = "discovery-category category-" + group.category;
          category.textContent = categoryLabels[group.category];
          const status = document.createElement("span");
          status.className = "discovery-status";
          const labels = currentTranslations();
          status.textContent = localizedUnverifiedLabel(currentLanguage());
          top.append(category, status);
          const metadata = document.createElement("p");
          metadata.className = "discovery-meta";
          metadata.textContent = Array.from(group.roles.entries())
            .map(([role, count]) => {
              const localized = localizedDiscoveryRole(role, currentLanguage());
              return count > 1 ? localized + " ×" + count : localized;
            })
            .join(", ") + (group.count > 1 ? " · " + group.count + " " + discoveryAgentCountLabel(currentLanguage()) : "");
          const summaryText = document.createElement("p");
          summaryText.className = "discovery-summary";
          summaryText.textContent = group.summary;
          paragraph.append(top, metadata, summaryText);
          list.append(paragraph);
        });
      };
      filter.addEventListener("change", renderEntries);
      renderEntries();

      if (voiceEnabled) entries.slice(0, 5).forEach(group => {
        const role = Array.from(group.roles.keys()).join(" ").toLowerCase();
        const agentIndex = /evidence|method|data|protocol|source/.test(role) ? 1
          : /integrity|review|ethic|safety|risk/.test(role) ? 2 : 0;
        speakAsAgent(group.summary, agentIndex);
      });
    } catch { showMessage(t.offline); }
  }
  function localizeResearchLog(message) {
    const raw = String(message || "").trim();
    const language = translationSource(currentLanguage());
    const dictionaries = {
      fr: {
        "Task lifecycle state updated.":"État du cycle de vie de la tâche mis à jour.",
        "independent_verifier completed a research pass; evidence remains subject to verification.":"Le vérificateur indépendant a terminé un cycle de recherche ; les éléments recueillis restent à vérifier.",
        "general_researcher completed a research pass; evidence remains subject to verification.":"Le chercheur généraliste a terminé un cycle de recherche ; les éléments recueillis restent à vérifier.",
        "Research group created with role-matched agents.":"Groupe de recherche créé avec des agents affectés selon leurs rôles.",
        "Specialist team allocated: 2 agents.":"Équipe de spécialistes affectée : 2 agents.",
        "Specialist team allocated: 1 agent.":"Équipe de spécialistes affectée : 1 agent."
      },
      en: {
        "Task lifecycle state updated.":"Task lifecycle state updated.",
        "independent_verifier completed a research pass; evidence remains subject to verification.":"The independent verifier completed a research pass; evidence remains subject to verification.",
        "general_researcher completed a research pass; evidence remains subject to verification.":"The general researcher completed a research pass; evidence remains subject to verification.",
        "Research group created with role-matched agents.":"Research group created with role-matched agents.",
        "Specialist team allocated: 2 agents.":"Specialist team allocated: 2 agents.",
        "Specialist team allocated: 1 agent.":"Specialist team allocated: 1 agent."
      }
    };
    const known = dictionaries[language] || dictionaries.en;
    if (known[raw]) return (language === "fr" ? "Information · " : "Info · ") + known[raw];
    const errorLike = /\b(error|failed|failure|exception|traceback|timeout|refused|unavailable)\b/i.test(raw);
    if (!errorLike) return raw;
    const details = raw
      .replace(/\bConnection refused\b/gi, language === "fr" ? "Connexion refusée" : "Connection refused")
      .replace(/\bPermission denied\b/gi, language === "fr" ? "Autorisation refusée" : "Permission denied")
      .replace(/\bTimeout\b/gi, language === "fr" ? "Délai d’attente dépassé" : "Timeout")
      .replace(/\bService unavailable\b/gi, language === "fr" ? "Service indisponible" : "Service unavailable")
      .replace(/\bHTTP (\d{3})\b/gi, language === "fr" ? "Réponse HTTP $1" : "HTTP $1");
    return language === "fr"
      ? "Erreur technique à examiner : " + details
      : "Technical error requiring review: " + details;
  }

  async function showActivity() {
    lastView = "activity";
    const t = currentTranslations();
    try {
      let events;
      try { events = await apiGet("/api/events"); }
      catch (firstError) {
        if (!/timeout|HTTP 5\d{2}|temporar|connection reset/i.test(String(firstError && firstError.message || firstError))) throw firstError;
        await new Promise(resolve => window.setTimeout(resolve, 650));
        events = await apiGet("/api/events");
      }
      const recent = events.slice(0, 50).map((event) => localizeResearchLog(event.message)).filter(Boolean);
      const unique = new Map();
      recent.forEach((message) => {
        const key = message.replace(/\s+/g, " ").trim().toLocaleLowerCase();
        if (!unique.has(key)) unique.set(key, { message: message.trim(), count: 0 });
        unique.get(key).count += 1;
      });
      dashboard.hidden = true;
      feed.hidden = false;
      feed.replaceChildren();
      if (!unique.size) {
        const empty = document.createElement("p");
        empty.className = "feed-line";
        empty.textContent = t.noActivity;
        feed.append(empty);
      } else {
        unique.forEach((entry) => {
          const paragraph = document.createElement("p");
          paragraph.className = "feed-line";
          const marker = document.createElement("span");
          marker.textContent = "●";
          const suffix = entry.count > 1
            ? (document.documentElement.lang.toLowerCase().startsWith("fr")
              ? ` · répété ${entry.count} fois` : ` · repeated ${entry.count} times`)
            : "";
          paragraph.append(marker, document.createTextNode(` ${entry.message}${suffix}`));
          feed.append(paragraph);
        });
      }
    } catch { showMessage(t.offline); }
  }
  async function showVerified() {
    lastView = "verified";
    const t = currentTranslations();
    try {
      const items = await apiGet("/api/verified");
      const lines = items.map((item) => item.statement).filter(Boolean);
      showMessage(lines.length ? lines.join(" • ") : t.noVerified, 2);
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
    await loadPriorityAssessments();
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
  const voiceReadButton = document.getElementById("voice-read");
  const voicePauseButton = document.getElementById("voice-pause");
  const voiceResumeButton = document.getElementById("voice-resume");
  const voiceStopButton = document.getElementById("voice-stop");
  const voiceStatus = document.getElementById("voice-status");
  function updateVoiceControls() {
    const speaking = Boolean(speechSynthesisApi?.speaking);
    const paused = Boolean(speechSynthesisApi?.paused);
    if (voiceReadButton) voiceReadButton.disabled = !voiceEnabled;
    if (voicePauseButton) voicePauseButton.disabled = !voiceEnabled || !speaking || paused;
    if (voiceResumeButton) voiceResumeButton.disabled = !voiceEnabled || !paused;
    if (voiceStopButton) voiceStopButton.disabled = !voiceEnabled || (!speaking && !paused);
    if (voiceStatus) voiceStatus.textContent = !voiceEnabled ? currentTranslations().voiceReady || "Voice is off" : paused ? currentTranslations().voicePaused || "Voice paused" : speaking ? currentTranslations().voiceSpeaking || "Speaking" : currentTranslations().voiceReady || "Voice ready";
  }
  voiceReadButton?.addEventListener("click", readCurrentFeed);
  voicePauseButton?.addEventListener("click", () => { speechSynthesisApi?.pause(); updateVoiceControls(); });
  voiceResumeButton?.addEventListener("click", () => { speechSynthesisApi?.resume(); updateVoiceControls(); });
  voiceStopButton?.addEventListener("click", () => { speechSynthesisApi?.cancel(); updateVoiceControls(); });
  window.setInterval(updateVoiceControls, 500);
  voiceToggle?.addEventListener("click", () => {
    voiceEnabled = !voiceEnabled;
    voiceToggle.setAttribute("aria-pressed", voiceEnabled ? "true" : "false");
    voiceToggle.textContent = voiceEnabled
      ? currentTranslations().voiceDisable || "Disable voice"
      : currentTranslations().voiceEnable || "Enable voice";
    if (voiceEnabled) {
      const copy = (window.SSSWET_AGENT_COPY || {})[translationSource(currentLanguage())]
        || (window.SSSWET_AGENT_COPY || {}).en;
      speakWelcome(copy);
    } else {
      speechSynthesisApi?.cancel();
    }
    updateVoiceControls();
  });
  if (speechSynthesisApi) {
    speechSynthesisApi.addEventListener?.("voiceschanged", refreshVoices);
    window.addEventListener("pagehide", () => speechSynthesisApi.cancel());
    speechSynthesisApi.addEventListener?.("start", updateVoiceControls);
    speechSynthesisApi.addEventListener?.("end", updateVoiceControls);
    speechSynthesisApi.addEventListener?.("pause", updateVoiceControls);
    speechSynthesisApi.addEventListener?.("resume", updateVoiceControls);
  }
  setLanguage(safeReadLanguage() || preferredLanguage());
  // Browsers may permit speech synthesis on page load; if blocked, retry once after the first user interaction.
  let automaticVoiceRetried = false;
  if (voiceEnabled) {
    window.addEventListener("pointerdown", () => {
      if (automaticVoiceRetried || speechSynthesisApi?.speaking) return;
      automaticVoiceRetried = true;
      const copy = (window.SSSWET_AGENT_COPY || {})[translationSource(currentLanguage())] || (window.SSSWET_AGENT_COPY || {}).en;
      if (copy) speakWelcome(copy);
    }, { once: true, passive: true });
  }
  document.querySelectorAll("#dashboard > section").forEach(section => {
    const heading = section.querySelector("h3, h2");
    if (!heading || section.parentElement.tagName === "DETAILS") return;
    const foldout = document.createElement("details");
    foldout.className = "dashboard-foldout";
    const summary = document.createElement("summary");
    summary.textContent = heading.textContent.trim();
    section.parentNode.insertBefore(foldout, section);
    foldout.append(summary, section);
  });
  document.getElementById("engine-connection-retry")?.addEventListener("click", refreshStatus);
  window.setInterval(refreshStatus, 3000);
  refreshStatus();
  capitalizeInterfaceText(document.body);
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
})();
