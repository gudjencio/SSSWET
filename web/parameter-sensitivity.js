(() => {
  "use strict";
  const root = document.getElementById("parameter-sensitivity-list");
  const status = document.getElementById("parameter-sensitivity-status");
  const refresh = document.getElementById("parameter-sensitivity-refresh");
  if (!root || !status) return;

  const isFrench = () => document.documentElement.lang.toLowerCase().startsWith("fr");
  const labels = () => {
    const fr = isFrench();
    return {
      title: fr ? "Études de sensibilité des paramètres" : "Parameter sensitivity studies",
      caption: fr ? "Plans de variation contrôlée · plages documentées · incertitudes · revue humaine" : "Controlled variation plans · documented ranges · uncertainty · human review",
      refresh: fr ? "Actualiser" : "Refresh",
      loading: fr ? "Préparation des plans…" : "Preparing study plans…",
      unavailable: fr ? "Les plans de sensibilité sont momentanément indisponibles." : "Sensitivity plans are temporarily unavailable.",
      empty: fr ? "Aucun protocole publié ne contient encore de définition complète de sensibilité." : "No published protocol contains sensitivity definitions yet.",
      ready: fr ? "Prêt pour revue humaine" : "Ready for human review",
      incomplete: fr ? "Définition incomplète" : "Incomplete design",
      protocol: fr ? "Protocole" : "Protocol",
      parameters: fr ? "Paramètres" : "Parameters",
      scenarios: fr ? "Scénarios proposés" : "Proposed scenarios",
      baseline: fr ? "Valeur de référence" : "Baseline",
      range: fr ? "Plage" : "Range",
      levels: fr ? "Niveaux" : "Levels",
      uncertainty: fr ? "Incertitude de mesure" : "Measurement uncertainty",
      repeats: fr ? "Répétitions par niveau" : "Replicates per level",
      constraints: fr ? "Contraintes de sécurité" : "Safety constraints",
      rationale: fr ? "Justification" : "Rationale",
      missing: fr ? "Éléments manquants ou invalides" : "Missing or invalid definitions",
      interactions: fr ? "Interactions entre paramètres : non évaluées" : "Parameter interactions: not assessed",
      disclaimer: fr ? "Ces scénarios sont des propositions, pas des expériences ni des observations. Une revue humaine qualifiée et les autorisations applicables sont nécessaires avant toute étude." : "These scenarios are proposals, not experiments or observations. Qualified human review and applicable approvals are required before any study.",
      noExecution: fr ? "Aucune tâche ni expérience n'est créée ou exécutée automatiquement." : "No task or experiment is created or executed automatically.",
      interactionTitle: fr ? "Interactions entre paramètres" : "Pairwise parameter interactions",
      interactionCaption: fr ? "Propositions factorielles à deux facteurs · paires explicites · revue humaine" : "Two-factor factorial proposals · explicit candidate pairs · human review",
      interactionLoading: fr ? "Préparation des plans factoriels…" : "Preparing factorial plans…",
      interactionUnavailable: fr ? "Les plans d’interaction sont momentanément indisponibles." : "Interaction plans are temporarily unavailable.",
      interactionEmpty: fr ? "Aucune paire de paramètres n’a été explicitement proposée dans les protocoles publiés." : "No parameter pairs have been explicitly nominated in published protocols.",
      pair: fr ? "Paire étudiée" : "Candidate pair",
      grid: fr ? "Plan factoriel" : "Factorial design",
      combination: fr ? "Combinaisons proposées" : "Proposed combinations",
      pairReplicates: fr ? "Répétitions par combinaison" : "Replicates per combination",
      held: fr ? "Autres paramètres maintenus à la référence" : "Other parameters held at baseline",
      randomization: fr ? "Ordre d’exécution non attribué : randomisation et blocs à définir en revue." : "Run order not assigned: randomization and blocking require review.",
      noEffect: fr ? "Aucun effet d’interaction n’a été estimé." : "No interaction effect has been estimated."
    };
  };
  const element = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = String(value);
    return node;
  };
  const row = (label, value) => {
    const item = element("div", "sensitivity-field");
    item.append(element("span", "sensitivity-label", label), element("span", "sensitivity-value", value));
    return item;
  };

  async function load() {
    const l = labels();
    const title = document.getElementById("parameter-sensitivity-title");
    const caption = document.getElementById("parameter-sensitivity-caption");
    if (title) title.textContent = l.title;
    if (caption) caption.textContent = l.caption;
    if (refresh) refresh.textContent = l.refresh;
    root.replaceChildren();
    status.textContent = l.loading;
    try {
      const response = await fetch("/api/parameter-sensitivity-plans?limit=200", {
        headers: {Accept: "application/json"}, cache: "no-store"
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const report = await response.json();
      const plans = Array.isArray(report.plans) ? report.plans : [];
      status.textContent = String(plans.length) + " · " + String(report.ready_for_human_review || 0) + " " + l.ready.toLowerCase();
      if (!plans.length) {
        root.append(element("p", "sensitivity-empty", l.empty));
      }
      plans.forEach((plan) => {
        const card = element("article", "sensitivity-card");
        const heading = element("div", "sensitivity-card-heading");
        heading.append(element("h4", "", plan.protocol_title || plan.protocol_id));
        const badge = element("span", "sensitivity-badge", plan.classification === "ready_for_human_review" ? l.ready : l.incomplete);
        badge.dataset.state = plan.classification;
        heading.append(badge);
        card.append(heading);
        card.append(row(l.protocol, plan.protocol_id + " · v" + plan.protocol_version));
        card.append(row(l.parameters, plan.configured_parameter_count + " / " + plan.required_parameter_count));
        card.append(row(l.scenarios, plan.scenario_count));
        (plan.parameter_designs || []).forEach((design) => {
          const detail = element("section", "sensitivity-parameter");
          detail.append(element("h5", "", design.parameter));
          detail.append(row(l.range, design.range.minimum + "–" + design.range.maximum + " " + design.unit));
          detail.append(row(l.baseline, design.baseline + " " + design.unit));
          detail.append(row(l.levels, design.levels.join(", ") + " " + design.unit));
          detail.append(row(l.uncertainty, design.measurement_uncertainty.value + " " + design.measurement_uncertainty.unit));
          detail.append(row(l.repeats, design.replicates));
          detail.append(row(l.constraints, design.safety_constraints));
          detail.append(row(l.rationale, design.rationale));
          card.append(detail);
        });
        const missing = Object.entries(plan.missing_or_invalid_designs || {});
        if (missing.length) {
          const section = element("section", "sensitivity-issues");
          section.append(element("h5", "", l.missing));
          missing.forEach(([parameter, errors]) => {
            section.append(element("strong", "", parameter));
            (errors || []).forEach((error) => section.append(element("p", "", error)));
          });
          card.append(section);
        }
        card.append(element("p", "sensitivity-interactions", l.interactions));
        card.append(element("p", "sensitivity-disclaimer", l.disclaimer));
        card.append(element("p", "sensitivity-disclaimer", l.noExecution));
        root.append(card);
      });
    } catch (error) {
      status.textContent = l.unavailable + " " + error.message;
    }
  }
  async function loadInteractions() {
    const l = labels();
    const interactionRoot = document.getElementById("parameter-interaction-list");
    const interactionStatus = document.getElementById("parameter-interaction-status");
    const title = document.getElementById("parameter-interaction-title");
    const caption = document.getElementById("parameter-interaction-caption");
    if (!interactionRoot || !interactionStatus) return;
    if (title) title.textContent = l.interactionTitle;
    if (caption) caption.textContent = l.interactionCaption;
    interactionRoot.replaceChildren();
    interactionStatus.textContent = l.interactionLoading;
    try {
      const response = await fetch("/api/parameter-interaction-plans?limit=200", {
        headers: {Accept: "application/json"}, cache: "no-store"
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const report = await response.json();
      const plans = Array.isArray(report.plans) ? report.plans : [];
      interactionStatus.textContent = String(plans.length) + " · " + String(report.ready_for_human_review || 0) + " " + l.ready.toLowerCase();
      if (!plans.length) interactionRoot.append(element("p", "sensitivity-empty", l.interactionEmpty));
      plans.forEach((plan) => {
        const card = element("article", "sensitivity-card");
        const heading = element("div", "sensitivity-card-heading");
        heading.append(element("h4", "", plan.protocol_title || plan.protocol_id));
        const badge = element("span", "sensitivity-badge", plan.classification === "ready_for_human_review" ? l.ready : l.incomplete);
        badge.dataset.state = plan.classification === "ready_for_human_review" ? "ready_for_human_review" : "incomplete_design";
        heading.append(badge);
        card.append(heading);
        card.append(row(l.protocol, plan.protocol_id + " · v" + plan.protocol_version));
        card.append(row(l.pair, plan.ready_pair_count + " / " + plan.candidate_pair_count));
        card.append(row(l.scenarios, plan.scenario_count));
        (plan.pair_plans || []).forEach((pair) => {
          const detail = element("section", "sensitivity-parameter");
          detail.append(element("h5", "", (pair.parameters || []).join(" × ")));
          detail.append(row(l.grid, pair.design_type || pair.classification));
          detail.append(row(l.combination, pair.scenario_count || 0));
          if (pair.replicates_per_combination) detail.append(row(l.pairReplicates, pair.replicates_per_combination));
          if (pair.other_parameters_held_at_baseline?.length) detail.append(row(l.held, pair.other_parameters_held_at_baseline.join(", ")));
          if (pair.rationale) detail.append(row(l.rationale, pair.rationale));
          if (Array.isArray(pair.errors)) pair.errors.forEach((issue) => detail.append(element("p", "sensitivity-issues", issue)));
          else if (pair.errors && typeof pair.errors === "object") {
            Object.entries(pair.errors).forEach(([name, messages]) => {
              detail.append(element("strong", "", name));
              (messages || []).forEach((message) => detail.append(element("p", "sensitivity-issues", message)));
            });
          }
          card.append(detail);
        });
        (plan.errors || []).forEach((error) => card.append(element("p", "sensitivity-issues", error)));
        card.append(element("p", "sensitivity-interactions", l.randomization));
        card.append(element("p", "sensitivity-disclaimer", l.noEffect));
        card.append(element("p", "sensitivity-disclaimer", l.disclaimer));
        interactionRoot.append(card);
      });
    } catch (error) {
      interactionStatus.textContent = l.interactionUnavailable + " " + error.message;
    }
  }
  refresh?.addEventListener("click", () => { load(); loadInteractions(); });
  window.addEventListener("ssswet-language-changed", () => { load(); loadInteractions(); });
  load();
  loadInteractions();
})();
