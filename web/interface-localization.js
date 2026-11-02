/* Completes French labels for controls and forms that are not part of the data-driven translation catalogue. */
(() => {
  const fr = {
    retry: "Réessayer la connexion",
    researchProgram: "Programme de recherche",
    societal: "Bénéfice sociétal",
    ecological: "Bénéfice écologique et animal",
    maturity: "Maturité des preuves",
    feasibility: "Faisabilité technique",
    resources: "Accessibilité des ressources",
    safety: "Préparation en matière de sécurité et de légalité",
    notAssessed: "Non évalué",
    veryLow: "Très faible", low: "Faible", limited: "Limité", moderate: "Modéré", strong: "Élevé", veryStrong: "Très élevé",
    reviewer: "Évaluateur ou équipe",
    rationale: "Justification de l’évaluation",
    evidenceRefs: "Références des preuves",
    saveAssessment: "Enregistrer l’évaluation dans l’historique local",
    assessmentNote: "Chaque envoi crée une entrée permanente dans l’historique. La dernière évaluation sert à la comparaison actuelle. Les critères sans note restent non évalués. Cet outil n’autorise ni financement, ni expérience, ni produit.",
    technology: "Technologie",
    allTechnologies: "Toutes les technologies",
    entryType: "Type d’entrée",
    title: "Titre",
    summary: "Résumé",
    classification: "Classification des éléments",
    state: "État d’avancement",
    author: "Nom de l’auteur",
    addEntry: "Ajouter une entrée immuable au journal",
    journalNote: "La saisie est limitée à la machine locale. Les entrées ne peuvent être ni modifiées ni supprimées. Une chaîne de hachage détecte les modifications ultérieures, sans établir la validité scientifique.",
    planned: "Planifié", inProgress: "En cours", completed: "Terminé", blocked: "Bloqué", superseded: "Remplacé",
    hypothesis: "Hypothèse", literature: "Littérature scientifique", simulation: "Simulation", prototype: "Prototype", observation: "Observation", independentReview: "Examen indépendant", projectUpdate: "Mise à jour du projet",
    question: "Question de recherche", literatureReview: "Revue de littérature", feasibilityAssessment: "Évaluation de faisabilité", test: "Test", milestone: "Jalon", limitation: "Limitation",
    placeholderReviewer: "ex. : équipe de recherche SSSWET",
    placeholderRationale: "Expliquez le jugement et signalez les incertitudes.",
    placeholderRefs: "Une URL ou une référence par ligne (facultatif)",
    placeholderDoi: "DOI, URL ou identifiant d’un enregistrement existant",
    placeholderTitle: "Saisir un titre",
    placeholderSummary: "Résumer la mise à jour du projet",
    placeholderSearch: "Rechercher des titres, descriptions ou références",
    prioritySummary: "Enregistrer ou actualiser une évaluation", journalHeading: "Enregistrer une mise à jour du projet",
    priorityStatus: "Connectez le moteur de recherche local pour consulter et enregistrer les évaluations des programmes.",
    feasibilityStatus: "Examen fondé sur les preuves des sept programmes technologiques. Connectez le moteur local pour consulter les données enregistrées.",
    feasibilityNote: "Cet observatoire résume les entrées enregistrées dans le projet. Il ne démontre ni la faisabilité, ni la sécurité, ni la validité scientifique, ni la disponibilité d’un produit. L’absence d’un enregistrement ne prouve pas qu’aucun travail n’existe ailleurs.",
    journalStatus: "Connectez le moteur de recherche local pour consulter les mises à jour enregistrées du projet.",
    weight: "Pondération : "
  };
  const optionLabels = {
    "Not assessed":fr.notAssessed,"0 — Very low":"0 — Très faible","1 — Low":"1 — Faible","2 — Limited":"2 — Limité","3 — Moderate":"3 — Modéré","4 — Strong":"4 — Élevé","5 — Very strong":"5 — Très élevé",
    "Cellular improvement":"Amélioration cellulaire","Longevity":"Longévité","Advanced protective materials and armor":"Matériaux de protection avancés et armures","Personal flight systems":"Systèmes de vol personnel","Human–alien communication research":"Communication humain–extraterrestre","Spacetime physics":"Physique de l’espace-temps","Time-travel research":"Recherche sur le voyage temporel","Clean energy":"Énergie propre","Advanced energy storage":"Stockage avancé de l’énergie","Water":"Eau propre et dessalement","Sustainable food systems":"Systèmes alimentaires durables","Climate adaptation":"Adaptation climatique","Biodiversity protection":"Protection de la biodiversité","Wildlife protection":"Protection de la faune","Marine restoration":"Restauration des milieux marins","Reforestation and habitat restoration":"Reboisement et restauration des habitats","Regenerative agriculture":"Agriculture régénératrice","Circular economy and recycling":"Économie circulaire et recyclage","Clean air":"Air pur","Sustainable mobility":"Mobilité durable","Assistive and accessibility technology":"Technologies d’assistance et d’accessibilité","Disaster prevention and response":"Prévention et réponse aux catastrophes","Public health and prevention":"Santé publique et prévention","Sanitation and wastewater":"Assainissement et eaux usées","Open science and education":"Science ouverte et éducation","Animal health and welfare":"Santé et bien-être animal","Sustainable and safer materials":"Matériaux durables et plus sûrs","Carbon and ecosystem monitoring":"Surveillance du carbone et des écosystèmes","Pollinator protection":"Protection des pollinisateurs",
    "Research question":"Question de recherche","Literature review":"Revue de littérature","Feasibility assessment":"Évaluation de faisabilité","Test":"Test","Independent review":"Examen indépendant","Milestone":"Jalon","Limitation":"Limitation","Project update":"Mise à jour du projet",
    "Planned":"Planifié","In progress":"En cours","Completed":"Terminé","Blocked":"Bloqué","Superseded":"Remplacé",
    "Hypothesis":"Hypothèse","Literature":"Littérature scientifique","Observation":"Observation"
  };
  function setFirstText(el, value) {
    if (!el) return;
    const node = [...el.childNodes].find(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
    if (node) node.textContent = " " + value + " ";
    else el.insertBefore(document.createTextNode(value + " "), el.firstChild);
  }
  function apply() {
    const lang = document.documentElement.dataset.language || document.documentElement.lang || "en";
    if (!lang.toLowerCase().startsWith("fr")) return;
    const retry = document.getElementById("engine-connection-retry");
    if (retry) retry.textContent = fr.retry;
    const priority = document.getElementById("priority-assessment-form");
    if (priority) {
      const labels = {
        programme_id:fr.researchProgram, societal_benefit:fr.societal, ecological_benefit:fr.ecological,
        evidence_maturity:fr.maturity, technical_feasibility:fr.feasibility, resource_accessibility:fr.resources,
        safety_legal_readiness:fr.safety, reviewer_label:fr.reviewer, rationale:fr.rationale, evidence_refs:fr.evidenceRefs
      };
      Object.entries(labels).forEach(([name,value]) => setFirstText(priority.querySelector('[name="'+name+'"]')?.closest("label"), value));
      const submit = priority.querySelector('button[type="submit"]'); if (submit) submit.textContent = fr.saveAssessment;
      const note = priority.querySelector(".priority-assessment-note"); if (note) note.textContent = fr.assessmentNote;
      priority.querySelectorAll("option").forEach(o => { if (optionLabels[o.textContent.trim()]) o.textContent = optionLabels[o.textContent.trim()]; });
      const reviewer = priority.querySelector('[name="reviewer_label"]'); if (reviewer) reviewer.placeholder = fr.placeholderReviewer;
      const rationale = priority.querySelector('[name="rationale"]'); if (rationale) rationale.placeholder = fr.placeholderRationale;
      const refs = priority.querySelector('[name="evidence_refs"]'); if (refs) refs.placeholder = fr.placeholderRefs;
    }
    const journal = document.getElementById("research-journal-form");
    if (journal) {
      const labels = {technology:fr.technology,event_type:fr.entryType,title:fr.title,summary:fr.summary,classification:fr.classification,state:fr.state,evidence_refs:fr.evidenceRefs,author_label:fr.author};
      Object.entries(labels).forEach(([name,value]) => setFirstText(journal.querySelector('[name="'+name+'"]')?.closest("label"), value));
      const submit = journal.querySelector('button[type="submit"]'); if (submit) submit.textContent = fr.addEntry;
      const note = journal.querySelector(".research-journal-note"); if (note) note.textContent = fr.journalNote;
      journal.querySelectorAll("option").forEach(o => { if (optionLabels[o.textContent.trim()]) o.textContent = optionLabels[o.textContent.trim()]; });
      const title = journal.querySelector('[name="title"]'); if (title) title.placeholder = fr.placeholderTitle;
      const summary = journal.querySelector('[name="summary"]'); if (summary) summary.placeholder = fr.placeholderSummary;
      const refs = journal.querySelector('[name="evidence_refs"]'); if (refs) refs.placeholder = fr.placeholderDoi;
    }
    const filter = document.getElementById("research-journal-filter");
    if (filter) filter.querySelectorAll("option").forEach(o => { if (optionLabels[o.textContent.trim()]) o.textContent = optionLabels[o.textContent.trim()]; });
    const search = document.getElementById("timeline-search"); if (search) search.placeholder = fr.placeholderSearch;
    const summary = document.querySelector(".priority-assessment-editor > summary"); if (summary) summary.textContent = fr.prioritySummary;
    const journalHeading = document.querySelector("#research-journal-form h4"); if (journalHeading) journalHeading.textContent = fr.journalHeading;
    const priorityStatus = document.getElementById("priority-assessment-status"); if (priorityStatus && priorityStatus.textContent.includes("Connect the local research engine")) priorityStatus.textContent = fr.priorityStatus;
    const feasibilityStatus = document.getElementById("technology-feasibility-status"); if (feasibilityStatus && feasibilityStatus.textContent.includes("Evidence-led review")) feasibilityStatus.textContent = fr.feasibilityStatus;
    const feasibilityNote = document.querySelector(".technology-feasibility-note"); if (feasibilityNote) feasibilityNote.textContent = fr.feasibilityNote;
    const journalStatus = document.getElementById("research-journal-status"); if (journalStatus && journalStatus.textContent.includes("Connect the local research engine")) journalStatus.textContent = fr.journalStatus;
    document.querySelectorAll(".priority-score-grid small").forEach(el => { el.textContent = el.textContent.replace(" weight", " de pondération").replace("% de pondération", " % de pondération"); });
    const journalToolsLabel = document.querySelector(".research-journal-tools label"); if (journalToolsLabel) setFirstText(journalToolsLabel, fr.technology);
    const aria = [["#priority-assessment-form","Formulaire d’évaluation des priorités"],["#research-journal-form","Formulaire du journal de recherche"],["#technology-grid","Programmes technologiques à soutenir"]];
    aria.forEach(([selector,label]) => document.querySelector(selector)?.setAttribute("aria-label",label));
  }
  document.addEventListener("DOMContentLoaded", apply, {once:true});
  window.addEventListener("ssswet-language-changed", apply);
  apply();
})();

/* Load the optional public bot personality after the main interface has initialized. */
(() => {
  if (window.__SSSWET_BOT_PERSONALITY_LOADER__) return;
  window.__SSSWET_BOT_PERSONALITY_LOADER__ = true;
  const load = () => {
    if (document.querySelector('script[data-ssswet-bot-personality]')) return;
    const script = document.createElement("script");
    script.src = "bot-personality.js";
    script.async = false;
    script.dataset.ssswetBotPersonality = "true";
    document.body.appendChild(script);
  };
  if (document.body) load(); else document.addEventListener("DOMContentLoaded", load, {once:true});
})();