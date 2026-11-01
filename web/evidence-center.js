(() => {
  "use strict";

  const get = (path) => fetch(path, { headers: { Accept: "application/json" }, cache: "no-store" }).then((r) => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  });

  const t = () => ({
    title: document.documentElement.lang === "fr" ? "Centre des preuves" : "Evidence Center",
    caption: document.documentElement.lang === "fr" ? "Dossiers traçables, revues et limites explicites" : "Traceable dossiers, reviews and explicit limitations",
    refresh: document.documentElement.lang === "fr" ? "Actualiser" : "Refresh",
    empty: document.documentElement.lang === "fr" ? "Aucun dossier de preuves n’est encore disponible." : "No evidence dossiers are available yet.",
    unavailable: document.documentElement.lang === "fr" ? "Le registre des preuves est momentanément indisponible." : "The evidence registry is temporarily unavailable.",
    assembled: document.documentElement.lang === "fr" ? "assemblé" : "assembled",
    sources: document.documentElement.lang === "fr" ? "sources" : "sources",
    runs: document.documentElement.lang === "fr" ? "exécutions" : "runs",
    comparisons: document.documentElement.lang === "fr" ? "comparaisons" : "comparisons",
    events: document.documentElement.lang === "fr" ? "événements" : "events",
    unverified: document.documentElement.lang === "fr" ? "NON VÉRIFIÉ" : "UNVERIFIED",
    details: document.documentElement.lang === "fr" ? "Ouvrir le dossier" : "Open dossier",
    hash: document.documentElement.lang === "fr" ? "Empreinte" : "Fingerprint",
    validity: document.documentElement.lang === "fr" ? "Validité scientifique établie" : "Scientific validity established",
    no: document.documentElement.lang === "fr" ? "Non" : "No",
    review: document.documentElement.lang === "fr" ? "Décisions de revue" : "Review decisions",
    objections: document.documentElement.lang === "fr" ? "Objections" : "Objections",
    protocols: document.documentElement.lang === "fr" ? "Protocoles" : "Protocols",
    datasets: document.documentElement.lang === "fr" ? "Jeux de données" : "Datasets",
    disputes: document.documentElement.lang === "fr" ? "Litiges" : "Disputes",
    separation: document.documentElement.lang === "fr" ? "Une revue du dossier ne constitue pas une validation scientifique." : "Reviewing a dossier does not establish scientific validity."
  });

  const root = document.getElementById("evidence-center-list");
  const status = document.getElementById("evidence-center-status");
  const refreshButton = document.getElementById("evidence-center-refresh");
  if (!root || !status) return;

  function text(value) {
    return value === undefined || value === null || value === "" ? "—" : String(value);
  }

  function renderDossier(dossier) {
    const labels = t();
    const details = document.createElement("details");
    details.className = "evidence-dossier";
    const summary = document.createElement("summary");
    const title = document.createElement("strong");
    title.textContent = text(dossier.title || dossier.dossier_id);
    const badge = document.createElement("span");
    badge.className = "evidence-badge";
    badge.textContent = labels.unverified;
    summary.append(title, badge);

    const body = document.createElement("div");
    body.className = "evidence-body";
    const description = document.createElement("p");
    description.textContent = text(dossier.result_summary);
    body.append(description);

    const metrics = document.createElement("div");
    metrics.className = "evidence-metrics";
    [[labels.sources, dossier.source_count], [labels.runs, dossier.run_count], [labels.comparisons, dossier.comparison_count], [labels.events, dossier.event_count]].forEach(([label, value]) => {
      const item = document.createElement("span");
      item.textContent = text(value) + " " + label;
      metrics.append(item);
    });
    body.append(metrics);

    const meta = document.createElement("p");
    meta.className = "evidence-meta";
    meta.textContent = labels.assembled + ": " + text(dossier.assembled_at) + " · " + labels.hash + ": " + text(dossier.content_hash).slice(0, 20) + "…";
    body.append(meta);

    const open = document.createElement("button");
    open.type = "button";
    open.className = "evidence-open";
    open.textContent = labels.details;
    open.addEventListener("click", async () => {
      open.disabled = true;
      try {
        const full = await get("/api/evidence-dossiers/" + encodeURIComponent(dossier.dossier_id));
        renderDetail(body, full);
      } catch {
        const error = document.createElement("p");
        error.className = "evidence-error";
        error.textContent = labels.unavailable;
        body.append(error);
      } finally { open.disabled = false; }
    });
    body.append(open);
    details.append(summary, body);
    return details;
  }

  function renderDetail(body, dossier) {
    const labels = t();
    const previous = body.querySelector(".evidence-detail");
    if (previous) previous.remove();
    const panel = document.createElement("div");
    panel.className = "evidence-detail";
    const sections = [
      [labels.protocols, dossier.protocols],
      [labels.datasets, dossier.datasets],
      [labels.disputes, dossier.disputes],
      [labels.objections, dossier.objections],
      [labels.review, (dossier.events || []).filter((event) => event.kind === "review")]
    ];
    sections.forEach(([headingText, value]) => {
      const heading = document.createElement("h5");
      heading.textContent = headingText;
      panel.append(heading);
      const pre = document.createElement("pre");
      pre.textContent = JSON.stringify(value || [], null, 2);
      panel.append(pre);
    });
    const validity = document.createElement("p");
    validity.className = "evidence-validity";
    validity.textContent = labels.validity + ": " + labels.no;
    panel.append(validity);
    const note = document.createElement("p");
    note.className = "evidence-note";
    note.textContent = labels.separation;
    panel.append(note);
    body.append(panel);
  }

  async function load() {
    root.replaceChildren();
    status.textContent = "…";
    try {
      const payload = await get("/api/evidence-dossiers?limit=50");
      const dossiers = Array.isArray(payload.dossiers) ? payload.dossiers : [];
      status.textContent = String(dossiers.length);
      if (!dossiers.length) {
        const empty = document.createElement("p");
        empty.className = "visual-empty";
        empty.textContent = t().empty;
        root.append(empty);
        return;
      }
      dossiers.forEach((dossier) => root.append(renderDossier(dossier)));
    } catch {
      status.textContent = "—";
      const error = document.createElement("p");
      error.className = "visual-empty";
      error.textContent = t().unavailable;
      root.append(error);
    }
  }

  refreshButton?.addEventListener("click", load);
  window.addEventListener("ssswet-language-changed", load);
  load();
})();
