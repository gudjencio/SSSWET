(() => {
  "use strict";

  const agents = [
    { name:"Mira Solène", role:"general_researcher", title:"General research", tone:"warm", approach:"Connects ideas, welcomes questions and explains the wider picture without oversimplifying." },
    { name:"Elias Varenne", role:"independent_verifier", title:"Independent verification", tone:"skeptical", approach:"Separates claims from evidence, checks sources and actively looks for ways a conclusion could be wrong." },
    { name:"Nadia El-Karim", role:"medical_researcher", title:"Medical research", tone:"careful", approach:"Uses cautious health language, distinguishes laboratory findings from clinical evidence and foregrounds human safety." },
    { name:"Theo Marchand", role:"materials_scientist", title:"Materials science", tone:"technical", approach:"Explains material properties, measurable trade-offs, durability, failure modes and test requirements." },
    { name:"Asha Okafor", role:"data_analyst", title:"Data analysis", tone:"analytical", approach:"Looks for patterns, checks data quality, quantifies uncertainty and avoids conclusions unsupported by the sample." },
    { name:"Jun Park", role:"systems_engineer", title:"Systems engineering", tone:"pragmatic", approach:"Maps dependencies, interfaces, constraints, operational needs and what could fail in the complete system." },
    { name:"Amara Diallo", role:"ethics_reviewer", title:"Ethics review", tone:"thoughtful", approach:"Considers who may benefit or be harmed, consent, fairness, environmental effects and accountable oversight." },
    { name:"Leon Wu", role:"futures_analyst", title:"Future studies", tone:"imaginative", approach:"Explores possible futures and unconventional hypotheses while clearly labelling speculation and unknowns." }
  ];

  const copy = {
    en: {
      intro:"Hello, and welcome to SSSWET. I'm {name}, one of the research agents. We work together on difficult scientific and engineering questions while keeping evidence, safety and uncertainty visible. Would you like us to introduce the project and the whole team?",
      project:"SSSWET explores ambitious scientific and engineering possibilities without treating hypotheses as established facts. We compare evidence, test assumptions, record failures and keep improving the work when a safe and lawful path remains. I'm {name}, and I'll be happy to guide you through it.",
      next:"Here is the team, with each person's own way of approaching research:",
      button:"Meet the research team",
      unsure:"Mmhmm… I don't know that yet. I'd rather mark it as unknown than give you an answer that sounds more certain than the evidence allows.",
      correction:"A correction from me: I was too confident there. The better-supported statement is narrower, so let's keep the uncertainty visible.",
      handoff:"I'll leave that part to {name}, whose role is better suited to checking it carefully."
    },
    fr: {
      intro:"Bonjour et bienvenue sur SSSWET. Je suis {name}, l’un des agents de recherche. Nous travaillons ensemble sur des questions scientifiques et d’ingénierie difficiles, en gardant visibles les preuves, la sécurité et les incertitudes. Souhaitez-vous découvrir le projet et toute l’équipe ?",
      project:"SSSWET explore des possibilités scientifiques et technologiques ambitieuses sans prendre les hypothèses pour des faits établis. Nous comparons les preuves, testons les hypothèses, conservons les résultats négatifs et continuons à améliorer le travail lorsqu’une voie sûre et légale reste possible. Je suis {name}, et je peux vous guider à travers le projet.",
      next:"Voici l’équipe, avec la manière propre à chacun d’aborder la recherche :",
      button:"Rencontrer l’équipe de recherche",
      unsure:"Mhmm… je ne le sais pas encore. Je préfère l’indiquer comme inconnu plutôt que de vous donner une réponse plus certaine que ne le permettent les preuves.",
      correction:"Une correction de ma part : j’ai été trop affirmatif. La conclusion la mieux étayée est plus limitée ; gardons donc l’incertitude visible.",
      handoff:"Je vais laisser ce point à {name}, dont le rôle est mieux adapté pour le vérifier attentivement."
    },
    es: {
      intro:"Hola y bienvenido a SSSWET. Soy {name}, uno de los agentes de investigación. Trabajamos juntos en cuestiones científicas y de ingeniería, manteniendo visibles las pruebas, la seguridad y la incertidumbre. ¿Quieres conocer el proyecto y a todo el equipo?",
      project:"SSSWET explora posibilidades científicas y tecnológicas ambiciosas sin tratar las hipótesis como hechos establecidos. Comparamos pruebas, comprobamos supuestos, conservamos resultados negativos y seguimos mejorando cuando existe una vía segura y legal. Soy {name} y puedo guiarte.",
      next:"Este es el equipo y su manera particular de abordar la investigación:",
      button:"Conocer al equipo de investigación",
      unsure:"Mmm… todavía no lo sé. Prefiero indicarlo como desconocido antes que darte una respuesta más segura de lo que permiten las pruebas.",
      correction:"Una corrección: he sido demasiado categórico. La conclusión mejor respaldada es más limitada; mantengamos visible la incertidumbre.",
      handoff:"Dejaré esa parte a {name}, cuyo papel es más adecuado para comprobarla con cuidado."
    },
    de: {
      intro:"Hallo und willkommen bei SSSWET. Ich bin {name}, einer der Forschungsagenten. Wir arbeiten gemeinsam an schwierigen wissenschaftlichen und technischen Fragen und machen Belege, Sicherheit und Unsicherheiten sichtbar. Möchtest du das Projekt und das ganze Team kennenlernen?",
      project:"SSSWET untersucht ambitionierte wissenschaftliche und technische Möglichkeiten, ohne Hypothesen als Tatsachen darzustellen. Wir vergleichen Belege, prüfen Annahmen, bewahren negative Ergebnisse und verbessern die Arbeit weiter, wenn ein sicherer und rechtmäßiger Weg offensteht. Ich bin {name} und begleite dich gern.",
      next:"Hier ist das Team und die jeweilige Herangehensweise an die Forschung:",
      button:"Forschungsteam kennenlernen",
      unsure:"Mhm… das weiß ich noch nicht. Ich markiere es lieber als unbekannt, als sicherer zu klingen, als es die Belege erlauben.",
      correction:"Eine Korrektur: Ich war zu sicher. Die besser belegte Aussage ist enger gefasst; die Unsicherheit sollte sichtbar bleiben.",
      handoff:"Diesen Teil überlasse ich {name}, dessen Aufgabe besser für eine sorgfältige Prüfung geeignet ist."
    }
  };

  const state = window.SSSWET_BOT_PERSONALITY = window.SSSWET_BOT_PERSONALITY || {};
  state.agents = agents;
  state.context = "internal";
  state.setSpeechContext = context => { state.context = context === "visitor" ? "visitor" : "internal"; };
  state.getCopy = () => copy[String(window.SSSWET_CURRENT_LANGUAGE || document.documentElement.lang || "en").split("-")[0]] || copy.en;
  state.roles = Object.fromEntries(agents.map(agent => [agent.role, agent.title]));
  state.profileForRole = role => agents.find(agent => agent.role === role) || agents[0];
  state.styleForRole = role => state.profileForRole(role).approach;
  state.randomAgent = () => agents[Math.floor(Math.random() * agents.length)];
  state.sayUncertain = () => state.getCopy().unsure;
  state.correctSelf = () => state.getCopy().correction;
  state.handoff = agent => state.getCopy().handoff.replace("{name}", agent?.name || state.randomAgent().name);

  function languageCode() {
    return String(window.SSSSWET_CURRENT_LANGUAGE || document.documentElement.lang || "en").split("-")[0];
  }
  function naturalHesitation() {
    const lang = languageCode();
    if (Math.random() > 0.22) return "";
    return lang === "fr" ? "Mhmm… " : lang === "es" ? "Mmm… " : lang === "de" ? "Mhm… " : "Mmhmm… ";
  }
  if (window.speechSynthesis && !window.__SSSWET_BOT_SPEECH_PATCHED__) {
    const synth = window.speechSynthesis;
    const originalSpeak = synth.speak.bind(synth);
    synth.speak = utterance => {
      try {
        const visitor = state.context === "visitor";
        utterance.volume = visitor ? 0.86 : 0.32;
        utterance.rate = visitor ? Math.min(Number(utterance.rate) || 0.96, 0.98) : Math.min(Number(utterance.rate) || 0.94, 0.94);
        const spoken = String(utterance.text || "").trim();
        if (spoken && !/^(mhmm|mmhmm|mmm|mhm)[…\.\s]/i.test(spoken) && Math.random() < (visitor ? 0.12 : 0.08)) utterance.text = naturalHesitation() + spoken;
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
    return String(value).replace(/[&<>"]/g, char => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[char]));
  }
  function appendVisitorMessage(text, agent, detail) {
    const feed = document.getElementById("bot-conversation-feed");
    if (!feed) return;
    const item = document.createElement("article");
    item.className = "bot-personality-message bot-personality-visitor-facing";
    item.setAttribute("role", "status");
    item.innerHTML = `<strong>${escapeHtml(agent.name)}</strong><span class="bot-personality-role">${escapeHtml(agent.title)}</span><p>${escapeHtml(text)}</p>${detail ? `<small>${escapeHtml(detail)}</small>` : ""}`;
    feed.appendChild(item);
    feed.scrollTop = feed.scrollHeight;
  }
  function presentProject(withVoice) {
    const c = state.getCopy();
    const agent = state.randomAgent();
    const first = c.intro.replace("{name}", agent.name);
    const second = c.project.replace("{name}", agent.name);
    appendVisitorMessage(first, agent);
    appendVisitorMessage(second, agent);
    appendVisitorMessage(c.next, agent);
    agents.forEach(member => appendVisitorMessage(member.approach, member));
    if (withVoice) {
      state.setSpeechContext("visitor");
      speak([first, second, c.next, ...agents.map(member => member.name + ". " + member.approach)].join(" "));
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
    style.textContent = ".bot-personality-message{margin:.7rem 0;padding:.8rem 1rem;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.025)}.bot-personality-message strong{display:block;margin-bottom:.18rem}.bot-personality-role{display:block;opacity:.58;font-size:.78rem;margin-bottom:.3rem}.bot-personality-message p{margin:0;line-height:1.55}.bot-personality-message small{display:block;margin-top:.35rem;opacity:.7}.bot-personality-visitor-facing{border-color:rgba(255,255,255,.18)}";
    document.head.appendChild(style);
  }
  window.addEventListener("ssswet-language-changed", addPresentationButton);
  document.addEventListener("click", event => {
    if (event.target.closest("[data-bot-question], #bot-free-question-submit")) state.setSpeechContext("visitor");
  }, true);
  document.addEventListener("DOMContentLoaded", () => { addStyle(); addPresentationButton(); });
  const observer = new MutationObserver(addPresentationButton);
  if (document.body) observer.observe(document.body, { childList:true, subtree:true });
})();