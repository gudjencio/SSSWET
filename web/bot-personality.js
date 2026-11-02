(() => {
  "use strict";

  const agents = [
    { name: "Mira Solène", role: "general research", tone: "warm" },
    { name: "Elias Varenne", role: "independent verification", tone: "calm" },
    { name: "Nadia El-Karim", role: "medical research", tone: "reassuring" },
    { name: "Theo Marchand", role: "materials science", tone: "precise" },
    { name: "Asha Okafor", role: "data analysis", tone: "curious" },
    { name: "Jun Park", role: "systems engineering", tone: "practical" },
    { name: "Amara Diallo", role: "ethics review", tone: "thoughtful" },
    { name: "Leon Wu", role: "future studies", tone: "imaginative" }
  ];

  const copy = {
    en: {
      intro: "Hello, and welcome to SSSWET. I'm {name}, one of the research agents. We work together on difficult scientific and engineering questions while keeping evidence, safety and uncertainty visible. Would you like us to introduce the project and explain what each of us does?",
      project: "SSSWET explores ambitious scientific and engineering possibilities without treating hypotheses as established facts. We compare evidence, test assumptions, record failures and keep improving the work when a safe and lawful path remains. I’m {name}, and I’ll be happy to guide you through it.",
      next: "If you like, I can introduce the rest of the team too.",
      button: "Introduce yourselves",
      unsure: "Mmhmm… I don't know that yet. I would rather mark it as unknown than give you an answer that sounds more certain than the evidence allows.",
      correction: "One small correction from me: I was too confident there. The better-supported statement is the narrower one, so let's keep the uncertainty visible.",
      handoff: "I'll leave that part to {name}, whose role is better suited to checking it carefully."
    },
    fr: {
      intro: "Bonjour, et bienvenue sur SSSWET. Je suis {name}, l’un des agents de recherche. Nous travaillons ensemble sur des questions scientifiques et d’ingénierie difficiles, tout en gardant visibles les preuves, la sécurité et les incertitudes. Souhaitez-vous que nous vous présentions le projet et le rôle de chacun ?",
      project: "SSSWET explore des possibilités scientifiques et technologiques ambitieuses sans prendre les hypothèses pour des faits établis. Nous comparons les preuves, testons les hypothèses, conservons les résultats négatifs et continuons à améliorer le travail lorsqu’une voie sûre et légale reste possible. Je suis {name}, et je peux vous guider tranquillement à travers le projet.",
      next: "Si vous le souhaitez, je peux aussi vous présenter les autres membres de l’équipe.",
      button: "Présentez-vous",
      unsure: "Mhmm… je ne le sais pas encore. Je préfère le laisser indiqué comme inconnu plutôt que de vous donner une réponse qui semblerait plus certaine que ne le permettent les preuves.",
      correction: "Petite correction de ma part : j’ai été trop affirmatif. La formulation la mieux étayée est plus limitée, alors gardons l’incertitude visible.",
      handoff: "Je vais laisser ce point à {name}, dont le rôle est mieux adapté pour le vérifier attentivement."
    },
    es: {
      intro: "Hola, y bienvenido a SSSWET. Soy {name}, uno de los agentes de investigación. Trabajamos juntos en preguntas científicas y de ingeniería difíciles, manteniendo visibles las pruebas, la seguridad y la incertidumbre. ¿Quieres que te presentemos el proyecto y lo que hace cada uno?",
      project: "SSSWET explora posibilidades científicas y tecnológicas ambiciosas sin tratar las hipótesis como hechos establecidos. Comparamos evidencias, comprobamos supuestos, conservamos los resultados negativos y seguimos mejorando el trabajo cuando existe una vía segura y legal.",
      next: "Si quieres, también puedo presentarte al resto del equipo.",
      button: "Presentarse",
      unsure: "Mmm… todavía no lo sé. Prefiero marcarlo como desconocido antes que darte una respuesta que parezca más segura de lo que permiten las pruebas.",
      correction: "Una pequeña corrección: he sido demasiado categórico. La afirmación mejor respaldada es más limitada, así que mantengamos visible la incertidumbre.",
      handoff: "Dejaré esa parte a {name}, cuyo papel es más adecuado para comprobarla con cuidado."
    },
    de: {
      intro: "Hallo und willkommen bei SSSWET. Ich bin {name}, einer der Forschungsagenten. Wir arbeiten gemeinsam an schwierigen wissenschaftlichen und technischen Fragen und machen Belege, Sicherheit und Unsicherheiten sichtbar. Möchtest du, dass wir das Projekt und unsere Aufgaben kurz vorstellen?",
      project: "SSSWET untersucht ambitionierte wissenschaftliche und technische Möglichkeiten, ohne Hypothesen als Tatsachen darzustellen. Wir vergleichen Belege, prüfen Annahmen, bewahren negative Ergebnisse und verbessern die Arbeit weiter, wenn ein sicherer und rechtmäßiger Weg offensteht.",
      next: "Wenn du möchtest, stelle ich dir auch das restliche Team vor.",
      button: "Vorstellen",
      unsure: "Mhm… das weiß ich noch nicht. Ich markiere es lieber als unbekannt, als eine Antwort zu geben, die sicherer klingt, als es die Belege erlauben.",
      correction: "Eine kleine Korrektur: Ich war zu sicher. Die besser belegte Aussage ist enger gefasst, also sollten wir die Unsicherheit sichtbar lassen.",
      handoff: "Diesen Teil überlasse ich {name}, dessen Aufgabe besser für eine sorgfältige Prüfung geeignet ist."
    }
  };

  const fallback = copy.en;
  const state = window.SSSWET_BOT_PERSONALITY = window.SSSWET_BOT_PERSONALITY || {};
  state.agents = agents;
  state.context = "internal";
  state.setSpeechContext = (context) => { state.context = context === "visitor" ? "visitor" : "internal"; };
  state.getCopy = () => copy[String(window.SSSWET_CURRENT_LANGUAGE || document.documentElement.lang || "en").split("-")[0]] || fallback;
  state.roles = Object.fromEntries(agents.map(agent => [agent.name, agent.role]));
  state.randomAgent = () => agents[Math.floor(Math.random() * agents.length)];
  state.sayUncertain = () => state.getCopy().unsure;
  state.correctSelf = () => state.getCopy().correction;
  state.handoff = (agent) => state.getCopy().handoff.replace("{name}", agent?.name || state.randomAgent().name);

  function languageCode() {
    return String(window.SSSWET_CURRENT_LANGUAGE || document.documentElement.lang || "en").split("-")[0];
  }

  function naturalHesitation() {
    const lang = languageCode();
    if (Math.random() > 0.22) return "";
    return lang === "fr" ? "Mhmm… " : lang === "es" ? "Mmm… " : lang === "de" ? "Mhm… " : "Mmhmm… ";
  }

  if (window.speechSynthesis && !window.__SSSWET_BOT_SPEECH_PATCHED__) {
    const synth = window.speechSynthesis;
    const originalSpeak = synth.speak.bind(synth);
    synth.speak = (utterance) => {
      try {
        const visitor = state.context === "visitor";
        utterance.volume = visitor ? 0.86 : 0.32;
        utterance.rate = visitor
          ? Math.min(Number(utterance.rate) || 0.96, 0.98)
          : Math.min(Number(utterance.rate) || 0.94, 0.94);
        const text = String(utterance.text || "").trim();
        if (text && !/^(mhmm|mmhmm|mmm|mhm)[…\.\s]/i.test(text) && Math.random() < (visitor ? 0.12 : 0.08)) {
          utterance.text = naturalHesitation() + text;
        }
      } catch (_) {}
      originalSpeak(utterance);
    };
    window.__SSSWET_BOT_SPEECH_PATCHED__ = true;
  }

  function speak(text) {
    if (!window.speechSynthesis || typeof SpeechSynthesisUtterance === "undefined") return;
    const utterance = new SpeechSynthesisUtterance(String(text || "").replace(/\s+/g, " ").trim());
    utterance.lang = document.documentElement.lang || "en";
    utterance.rate = 0.94;
    utterance.onend = () => state.setSpeechContext("internal");
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>\"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[char]));
  }

  function appendVisitorMessage(text, agent) {
    const feed = document.getElementById("bot-conversation-feed");
    if (!feed) return;
    const item = document.createElement("article");
    item.className = "bot-personality-message bot-personality-visitor-facing";
    item.setAttribute("role", "status");
    item.innerHTML = `<strong>${escapeHtml(agent.name)}</strong><span class="bot-personality-role">${escapeHtml(agent.role)}</span><p>${escapeHtml(text)}</p>`;
    feed.appendChild(item);
    feed.scrollTop = feed.scrollHeight;
  }

  function presentProject(withVoice) {
    const c = state.getCopy();
    const agent = state.randomAgent();
    const first = c.intro.replace("{name}", agent.name);
    const second = naturalHesitation() + c.project.replace("{name}", agent.name);
    appendVisitorMessage(first, agent);
    appendVisitorMessage(second, agent);
    appendVisitorMessage(c.next, agent);
    if (withVoice) {
      state.setSpeechContext("visitor");
      speak(`${first} ${second} ${c.next}`);
    }
  }

  function addPresentationButton() {
    const host = document.querySelector(".bot-visitor-questions");
    if (!host || host.querySelector("[data-bot-personality-question]")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.botPersonalityQuestion = "true";
    button.textContent = state.getCopy().button;
    button.addEventListener("click", () => presentProject(true));
    host.appendChild(button);
  }

  function addStyle() {
    if (document.getElementById("ssswet-bot-personality-style")) return;
    const style = document.createElement("style");
    style.id = "ssswet-bot-personality-style";
    style.textContent = ".bot-personality-message{margin:.7rem 0;padding:.8rem 1rem;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.025)}.bot-personality-message strong{display:block;margin-bottom:.18rem}.bot-personality-role{display:block;opacity:.58;font-size:.78rem;margin-bottom:.3rem}.bot-personality-message p{margin:0;line-height:1.55}.bot-personality-visitor-facing{border-color:rgba(255,255,255,.18)}";
    document.head.appendChild(style);
  }

  window.addEventListener("ssswet-language-changed", addPresentationButton);
  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-bot-question], #bot-free-question-submit")) state.setSpeechContext("visitor");
  }, true);
  document.addEventListener("DOMContentLoaded", () => { addStyle(); addPresentationButton(); });
  const observer = new MutationObserver(addPresentationButton);
  if (document.body) observer.observe(document.body, { childList: true, subtree: true });
})();