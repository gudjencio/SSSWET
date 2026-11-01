(() => {
  "use strict";
  const root = document.getElementById("lab-discrepancy-list");
  const status = document.getElementById("lab-discrepancy-status");
  const refresh = document.getElementById("lab-discrepancy-refresh");
  if (!root || !status) return;
  const fr = () => document.documentElement.lang === "fr";
  const labels = () => fr() ? {
    loading: "Analyse des comparaisons enregistrées…",
    empty: "Aucune divergence ou donnée de comparaison incomplète à examiner.",
    error: "Le registre des divergences est indisponible.",
    divergence: "Divergence de résultats enregistrée",
    incompatible: "Conditions incompatibles",
    incomplete: "Comparaison incomplète",
    review: "Examen humain requis",
    noConclusion: "Aucune contradiction scientifique n’est établie.",
    protocol: "Protocole", campaigns: "Campagnes", runs: "Exécutions", tolerance: "Tolérance",
    count: "éléments à examiner"
  } : {
    loading: "Screening recorded comparisons…",
    empty: "No divergences or incomplete comparison records require review.",
    error: "The discrepancy registry is unavailable.",
    divergence: "Recorded result divergence",
    incompatible: "Incompatible conditions",
    incomplete: "Incomplete comparison",
    review: "Human review required",
    noConclusion: "No scientific contradiction has been established.",
    protocol: "Protocol", campaigns: "Campaigns", runs: "Runs", tolerance: "Tolerance",
    count: "items for review"
  };
  const add = (parent, tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = value == null || value === "" ? "—" : String(value);
    parent.append(node);
    return node;
  };
  async function load() {
    const l = labels();
    status.textContent = l.loading;
    root.replaceChildren();
    try {
      const response = await fetch("/api/lab-discrepancies", {headers:{Accept:"application/json"},cache:"no-store"});
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      status.textContent = data.count + " " + l.count;
      if (!data.findings || !data.findings.length) {
        add(root, "p", "lab-discrepancy-empty", l.empty);
        return;
      }
      data.findings.forEach((finding) => {
        const card = document.createElement("article");
        card.className = "lab-discrepancy-card";
        const title = finding.classification === "recorded_result_divergence" ? l.divergence :
          finding.classification === "incompatible_conditions" ? l.incompatible : l.incomplete;
        add(card, "h4", "lab-discrepancy-title", title);
        add(card, "p", "lab-discrepancy-reason", finding.reason);
        const meta = document.createElement("div");
        meta.className = "lab-discrepancy-meta";
        add(meta, "span", "", l.protocol + ": " + (finding.protocol_id || "—") + (finding.protocol_version ? " v" + finding.protocol_version : ""));
        add(meta, "span", "", l.campaigns + ": " + (finding.left_campaign_id || "—") + " / " + (finding.right_campaign_id || "—"));
        add(meta, "span", "", l.runs + ": " + (finding.left_run_id || "—") + " / " + (finding.right_run_id || "—"));
        add(meta, "span", "", l.tolerance + ": " + (finding.tolerance == null ? "—" : finding.tolerance));
        card.append(meta);
        add(card, "p", "lab-discrepancy-warning", l.review + " · " + l.noConclusion);
        root.append(card);
      });
    } catch (_) {
      status.textContent = l.error;
      add(root, "p", "lab-discrepancy-empty", l.error);
    }
  }
  if (refresh) refresh.addEventListener("click", load);
  document.addEventListener("ssswet-language-changed", load);
  load();
})();