(() => {
  "use strict";

  const get = (path) => fetch(path, { headers: { Accept: "application/json" }, cache: "no-store" }).then((r) => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  });

  const t = () => {
    const fr = document.documentElement.lang === "fr";
    return {
      empty: fr ? "Aucun dossier de preuves n’est encore disponible." : "No evidence dossiers are available yet.",
      unavailable: fr ? "Le registre des preuves est momentanément indisponible." : "The evidence registry is temporarily unavailable.",
      assembled: fr ? "assemblé" : "assembled", sources: fr ? "sources" : "sources", runs: fr ? "exécutions" : "runs",
      comparisons: fr ? "comparaisons" : "comparisons", events: fr ? "événements" : "events", unverified: fr ? "NON VÉRIFIÉ" : "UNVERIFIED",
      details: fr ? "Ouvrir la fiche scientifique" : "Open scientific sheet", hash: fr ? "Empreinte" : "Fingerprint",
      validity: fr ? "Validité scientifique établie" : "Scientific validity established", no: fr ? "Non" : "No",
      question: fr ? "Question / résultat" : "Question / result", sourcesTitle: fr ? "Sources et provenance" : "Sources and provenance",
      protocols: fr ? "Protocoles et versions" : "Protocols and versions", datasets: fr ? "Jeux de données et versions" : "Datasets and versions",
      runsTitle: fr ? "Expériences / exécutions" : "Experiments / runs", comparisonsTitle: fr ? "Reproductions et comparaisons" : "Reproductions and comparisons",
      objections: fr ? "Objections et limites" : "Objections and limitations", review: fr ? "Revues et décisions" : "Reviews and decisions",
      disputes: fr ? "Litiges" : "Disputes", eventsTitle: fr ? "Chronologie du dossier" : "Dossier chronology", none: fr ? "Aucun élément enregistré." : "No recorded items.",
      id: fr ? "Identifiant" : "Identifier", version: fr ? "Version" : "Version", state: fr ? "État" : "State", decision: fr ? "Décision" : "Decision",
      reviewer: fr ? "Campagne de revue" : "Review campaign", note: fr ? "Note" : "Note", created: fr ? "Créé" : "Created",
      assembledFrom: fr ? "Assemblé à partir des enregistrements existants" : "Assembled from existing records",
      separation: fr ? "Une revue du dossier ne constitue pas une validation scientifique. Les simulations, métadonnées et comparaisons restent des éléments à examiner, pas des preuves automatiquement établies." : "Reviewing a dossier does not establish scientific validity. Simulations, metadata and comparisons remain items for examination, not automatically established evidence.",
      trace: fr ? "Chaîne de traçabilité" : "Traceability chain", traceText: fr ? "Question → sources → protocole → données → exécutions → reproductions → objections → revues → état des preuves" : "Question → sources → protocol → data → runs → reproductions → objections → reviews → evidence state"
    };
  };

  const root = document.getElementById("evidence-center-list");
  const status = document.getElementById("evidence-center-status");
  const refreshButton = document.getElementById("evidence-center-refresh");
  if (!root || !status) return;
  const text = (value) => value === undefined || value === null || value === "" ? "—" : String(value);

  function field(label, value) { const item = document.createElement("div"); item.className = "evidence-field"; const key = document.createElement("span"); key.className = "evidence-field-label"; key.textContent = label; const val = document.createElement("span"); val.className = "evidence-field-value"; val.textContent = text(value); item.append(key, val); return item; }
  function collection(title, value, formatter) { const section = document.createElement("section"); section.className = "evidence-section"; const heading = document.createElement("h5"); heading.textContent = title; section.append(heading); if (!Array.isArray(value) || !value.length) { const empty = document.createElement("p"); empty.className = "evidence-muted"; empty.textContent = t().none; section.append(empty); return section; } const list = document.createElement("div"); list.className = "evidence-record-list"; value.forEach((item) => list.append(formatter(item))); section.append(list); return section; }
  function recordCard(fields) { const card = document.createElement("article"); card.className = "evidence-record"; fields.forEach(([label, value]) => card.append(field(label, value))); return card; }

  function renderDossier(dossier) {
    const labels = t(); const details = document.createElement("details"); details.className = "evidence-dossier";
    const summary = document.createElement("summary"); const title = document.createElement("strong"); title.textContent = text(dossier.title || dossier.dossier_id); const badge = document.createElement("span"); badge.className = "evidence-badge"; badge.textContent = labels.unverified; summary.append(title, badge);
    const body = document.createElement("div"); body.className = "evidence-body"; const description = document.createElement("p"); description.textContent = text(dossier.result_summary); body.append(description);
    const metrics = document.createElement("div"); metrics.className = "evidence-metrics"; [[labels.sources, dossier.source_count], [labels.runs, dossier.run_count], [labels.comparisons, dossier.comparison_count], [labels.events, dossier.event_count]].forEach(([label, value]) => { const item = document.createElement("span"); item.textContent = text(value) + " " + label; metrics.append(item); }); body.append(metrics);
    const meta = document.createElement("p"); meta.className = "evidence-meta"; meta.textContent = labels.assembled + ": " + text(dossier.assembled_at) + " · " + labels.hash + ": " + text(dossier.content_hash).slice(0, 20) + "…"; body.append(meta);
    const open = document.createElement("button"); open.type = "button"; open.className = "evidence-open"; open.textContent = labels.details;
    open.addEventListener("click", async () => { open.disabled = true; try { const full = await get("/api/evidence-dossiers/" + encodeURIComponent(dossier.dossier_id)); renderDetail(body, full); window.dispatchEvent(new CustomEvent("ssswet-evidence-dossier", { detail: full })); } catch { const error = document.createElement("p"); error.className = "evidence-error"; error.textContent = labels.unavailable; body.append(error); } finally { open.disabled = false; } });
    body.append(open); details.append(summary, body); return details;
  }

  function renderDetail(body, dossier) {
    const labels = t(); const previous = body.querySelector(".evidence-detail"); if (previous) previous.remove(); const panel = document.createElement("div"); panel.className = "evidence-detail";
    const trace = document.createElement("div"); trace.className = "evidence-trace"; const traceTitle = document.createElement("strong"); traceTitle.textContent = labels.trace; const traceText = document.createElement("span"); traceText.textContent = labels.traceText; trace.append(traceTitle, traceText); panel.append(trace);
    const overview = document.createElement("section"); overview.className = "evidence-section evidence-overview"; const overviewHeading = document.createElement("h5"); overviewHeading.textContent = labels.question; overview.append(overviewHeading, field(labels.id, dossier.dossier_id), field(labels.state, dossier.verification_state), field(labels.assembledFrom, dossier.assembled_from_existing_records ? "Yes" : "No"), field(labels.validity, dossier.scientific_validity_established ? "Yes" : labels.no)); const summary = document.createElement("p"); summary.className = "evidence-result"; summary.textContent = text(dossier.result_summary); overview.append(summary); panel.append(overview);
    panel.append(collection(labels.sourcesTitle, dossier.sources, (item) => recordCard([[labels.id, item.source_id], ["Title", item.title], ["Type", item.source_type], ["Reference", item.reference]])));
    panel.append(collection(labels.protocols, dossier.protocols, (item) => recordCard([[labels.id, item.protocol_id], [labels.version, item.version], ["Fingerprint", item.fingerprint], [labels.state, item.status]])));
    panel.append(collection(labels.datasets, dossier.datasets, (item) => recordCard([[labels.id, item.dataset_id], [labels.version, item.version], ["SHA-256", item.content_sha256], ["Provenance", item.provenance]])));
    panel.append(collection(labels.runsTitle, dossier.runs, (item) => recordCard([[labels.id, item.run_id], ["Protocol", item.protocol_id], [labels.version, item.protocol_version], [labels.state, item.status], ["Started", item.started_at]])));
    panel.append(collection(labels.comparisonsTitle, dossier.comparisons, (item) => recordCard([[labels.id, item.comparison_id], ["Reference run", item.reference_run_id], ["Candidate run", item.candidate_run_id], [labels.state, item.status]])));
    panel.append(collection(labels.objections, dossier.objections, (item) => recordCard([[labels.note, item]])));
    panel.append(collection(labels.disputes, dossier.disputes, (item) => recordCard([[labels.id, item.case_id], [labels.state, item.status], [labels.note, item.summary || item.description]])));
    const reviews = (dossier.events || []).filter((event) => event.kind === "review"); panel.append(collection(labels.review, reviews, (item) => recordCard([[labels.reviewer, item.reviewer_campaign_id], [labels.decision, item.decision], [labels.note, item.note], [labels.created, item.created_at]])));
    panel.append(collection(labels.eventsTitle, dossier.events, (item) => recordCard([[labels.id, item.event_id], ["Kind", item.kind], [labels.created, item.created_at], ["Dossier", item.dossier_id]])));
    const validity = document.createElement("p"); validity.className = "evidence-validity"; validity.textContent = labels.validity + ": " + labels.no; panel.append(validity); const note = document.createElement("p"); note.className = "evidence-note"; note.textContent = labels.separation; panel.append(note); body.append(panel);
  }

  async function load() { root.replaceChildren(); status.textContent = "…"; try { const payload = await get("/api/evidence-dossiers?limit=50"); const dossiers = Array.isArray(payload.dossiers) ? payload.dossiers : []; status.textContent = String(dossiers.length); if (!dossiers.length) { const empty = document.createElement("p"); empty.className = "visual-empty"; empty.textContent = t().empty; root.append(empty); return; } dossiers.forEach((dossier) => root.append(renderDossier(dossier))); } catch { status.textContent = "—"; const error = document.createElement("p"); error.className = "visual-empty"; error.textContent = t().unavailable; root.append(error); } }
  refreshButton?.addEventListener("click", load); window.addEventListener("ssswet-language-changed", load); load();
})();
