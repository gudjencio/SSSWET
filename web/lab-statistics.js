(() => {
  "use strict";
  const root = document.getElementById("lab-statistics-list");
  const status = document.getElementById("lab-statistics-status");
  const refresh = document.getElementById("lab-statistics-refresh");
  const note = document.getElementById("lab-statistics-note");
  if (!root || !status) return;

  const labels = () => document.documentElement.lang === "fr" ? {
    title:"Statistiques descriptives du laboratoire", refresh:"Actualiser",
    loading:"Chargement des sorties numériques enregistrées…",
    unavailable:"Les résumés statistiques sont momentanément indisponibles.",
    empty:"Aucune sortie numérique enregistrée ne peut encore être résumée.",
    samples:"observations", mean:"Moyenne", median:"Médiane", sd:"Écart-type expérimental",
    range:"Étendue", quartiles:"Quartiles", outliers:"Valeurs atypiques potentielles à examiner",
    single:"Observation unique", summary:"Résumé descriptif uniquement",
    note:"Les valeurs atypiques sont des alertes à examiner et ne sont jamais supprimées automatiquement."
  } : {
    title:"Descriptive laboratory statistics", refresh:"Refresh",
    loading:"Loading recorded numeric outputs…",
    unavailable:"Statistical summaries are temporarily unavailable.",
    empty:"No recorded numeric outputs are available to summarize yet.",
    samples:"observations", mean:"Mean", median:"Median", sd:"Sample standard deviation",
    range:"Range", quartiles:"Quartiles", outliers:"Potential outlier candidates to review",
    single:"Single observation", summary:"Descriptive summary only",
    note:"Potential outliers are review flags and are never removed automatically."
  };
  const el = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = String(value);
    return node;
  };
  const fmt = value => typeof value === "number" && Number.isFinite(value)
    ? new Intl.NumberFormat(document.documentElement.lang || "en", {maximumFractionDigits: 5}).format(value)
    : "—";
  function field(label, value) {
    const row = el("div", "lab-stat-field");
    row.append(el("span", "lab-stat-label", label), el("span", "lab-stat-value", value));
    return row;
  }
  async function load() {
    const t = labels();
    const heading = document.getElementById("lab-statistics-title");
    if (heading) heading.textContent = t.title;
    if (refresh) refresh.textContent = t.refresh;
    root.replaceChildren();
    status.textContent = t.loading;
    if (note) note.textContent = t.note;
    try {
      const response = await fetch("/api/lab-statistical-summaries?limit=200", {
        headers: {Accept:"application/json"}, cache:"no-store"
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const report = await response.json();
      const summaries = Array.isArray(report.summaries) ? report.summaries : [];
      status.textContent = String(report.runs_examined || 0) + " · " + String(summaries.length);
      if (!summaries.length) {
        root.append(el("p", "lab-stat-empty", t.empty));
        return;
      }
      summaries.forEach(summary => {
        const card = el("article", "lab-stat-card");
        const heading = el("div", "lab-stat-heading");
        heading.append(el("h4", "", summary.output_name));
        heading.append(el("span", "lab-stat-count", String(summary.sample_size) + " " + t.samples));
        card.append(heading);
        card.append(el("p", "lab-stat-protocol", summary.protocol_id + " · v" + summary.protocol_version));
        card.append(field(t.mean, fmt(summary.mean)));
        card.append(field(t.median, fmt(summary.median)));
        card.append(field(t.sd, fmt(summary.sample_standard_deviation)));
        card.append(field(t.range, fmt(summary.minimum) + " – " + fmt(summary.maximum)));
        card.append(field(t.quartiles, fmt(summary.q1) + " / " + fmt(summary.q3)));
        if (summary.outlier_candidates?.length) {
          const flags = el("div", "lab-stat-outliers");
          flags.append(el("strong", "", t.outliers));
          summary.outlier_candidates.forEach(item => flags.append(
            el("p", "", String(item.run_id || "run") + ": " + fmt(item.value))
          ));
          card.append(flags);
        }
        card.append(el("p", "lab-stat-disclaimer", summary.sample_size < 2 ? t.single : t.summary));
        root.append(card);
      });
    } catch (error) {
      status.textContent = t.unavailable + " " + error.message;
    }
  }
  refresh?.addEventListener("click", load);
  window.addEventListener("ssswet-language-changed", load);
  load();
})();
