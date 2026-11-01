const translations = {
  en: {
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "RESEARCH SYSTEM ONLINE",
    mission: "Research ideas. Test them. Verify them. Never confuse a hypothesis with reality.",
    agents: "Research agents",
    verification: "verification-first",
    discover: "What did you discover?",
    working: "What are you working on?",
    verified: "Latest verified results",
    ready: "The research system is ready.",
    footer: "ETDESS is the French translation of SSSWET. Public results remain subject to verification.",
    discoveryMessage: "No public discovery has been published yet. The system is researching and verifying before publication.",
    workingMessage: "Research tasks are being decomposed, assigned, checked, and recovered when blocked.",
    verifiedMessage: "No independently verified public result is available yet. This is intentional: verification comes before publication."
  },
  fr: {
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "SYSTÈME DE RECHERCHE EN LIGNE",
    mission: "Rechercher des idées. Les tester. Les vérifier. Ne jamais confondre une hypothèse avec la réalité.",
    agents: "Agents de recherche",
    verification: "vérification prioritaire",
    discover: "Qu'avez-vous découvert ?",
    working: "Sur quoi travaillez-vous ?",
    verified: "Derniers résultats vérifiés",
    ready: "Le système de recherche est prêt.",
    footer: "ETDESS est la traduction française de SSSWET. Les résultats publics restent soumis à vérification.",
    discoveryMessage: "Aucune découverte publique n'a encore été publiée. Le système recherche et vérifie avant toute publication.",
    workingMessage: "Les tâches sont décomposées, distribuées, vérifiées et reprises lorsqu'elles sont bloquées.",
    verifiedMessage: "Aucun résultat public vérifié indépendamment n'est encore disponible. C'est volontaire : la vérification précède la publication."
  }
};

const languageSelect = document.getElementById("language");
const feed = document.getElementById("feed");

function preferredLanguage() {
  const lang = (navigator.language || "en").toLowerCase();
  return lang.startsWith("fr") ? "fr" : "en";
}

function setLanguage(lang) {
  const t = translations[lang] || translations.en;
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (t[key]) element.textContent = t[key];
  });
  languageSelect.value = lang;
  localStorage.setItem("ssswet-language", lang);
}

function message(key) {
  const lang = languageSelect.value;
  feed.innerHTML = `<p class="feed-line"><span>●</span> ${translations[lang][key]}</p>`;
}

document.querySelectorAll("button[data-action]").forEach((button) => {
  button.addEventListener("click", () => message({
    discover: "discoveryMessage",
    working: "workingMessage",
    verified: "verifiedMessage"
  }[button.dataset.action]));
});

languageSelect.addEventListener("change", () => setLanguage(languageSelect.value));

setLanguage(localStorage.getItem("ssswet-language") || preferredLanguage());
