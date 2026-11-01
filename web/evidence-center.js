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
      scientificBoard: fr ? "Comité de revue scientifique" : "Scientific Review Board", boardLoading: fr ? "Chargement des évaluations…" : "Loading assessments…", boardEmpty: fr ? "Aucune évaluation indépendante enregistrée." : "No independent assessments recorded.", reviewerId: fr ? "Identifiant du réviseur" : "Reviewer label", verdict: fr ? "Évaluation" : "Assessment", supports: fr ? "Soutient" : "Supports", challenges: fr ? "Conteste" : "Challenges", mixed: fr ? "Mitigé" : "Mixed", abstains: fr ? "S’abstient" : "Abstains", conflict: fr ? "Conflit d’intérêts" : "Conflict of interest", noneDeclared: fr ? "Aucun déclaré" : "None declared", potential: fr ? "Potentiel" : "Potential", confirmed: fr ? "Confirmé" : "Confirmed", rationale: fr ? "Justification" : "Rationale", methodsAssessment: fr ? "Évaluation des méthodes" : "Methods assessment", limitations: fr ? "Limites" : "Limitations", evidenceRefs: fr ? "Références (séparées par des virgules)" : "Evidence references (comma-separated)", submitAssessment: fr ? "Soumettre l’évaluation" : "Submit assessment", boardSaved: fr ? "Évaluation enregistrée dans l’historique." : "Assessment saved to the review history.", disagreement: fr ? "Des évaluations divergentes sont enregistrées." : "Divergent assessments are recorded.", noConsensus: fr ? "Aucun consensus automatique" : "No automatic consensus",integrityTitle: fr ? "Intégrité et éthique de la recherche" : "Research integrity & ethics", riskEmpty: fr ? "Aucun risque enregistré." : "No risks recorded.", riskLoading: fr ? "Chargement du registre…" : "Loading risk register…", riskCategory: fr ? "Catégorie du risque" : "Risk category", riskSeverity: fr ? "Gravité" : "Severity", riskDescription: fr ? "Description du problème" : "Risk description", riskReviewer: fr ? "Identifiant du réviseur" : "Reviewer label", riskSubmit: fr ? "Enregistrer le risque" : "Record risk", riskSaved: fr ? "Risque ajouté à l’historique." : "Risk added to history.", riskHold: fr ? "Une suspension de campagne est recommandée après examen humain." : "A campaign hold is recommended pending human review.", riskOpen: fr ? "Ouvert" : "Open", riskUnderReview: fr ? "En cours d’examen" : "Under review", riskEscalated: fr ? "Escaladé" : "Escalated", riskMitigated: fr ? "Atténué" : "Mitigated", riskAccepted: fr ? "Accepté avec contrôles" : "Accepted with controls", riskClosed: fr ? "Clôturé" : "Closed", riskMitigation: fr ? "Mesures d’atténuation / justification" : "Mitigation / closure rationale", riskAuthorization: fr ? "Référence d’autorisation humaine qualifiée" : "Qualified human authorization reference", riskNoAuto: fr ? "Aucune autorisation ni suspension automatique n’est effectuée." : "No automatic authorization or campaign suspension is performed.", riskState: fr ? "État du risque" : "Risk state", riskHistory: fr ? "Historique des événements" : "Event history", reproTitle: fr ? "Indice de reproductibilité" : "Reproducibility evidence index", reproLoading: fr ? "Analyse des enregistrements…" : "Analysing recorded evidence…", reproUnavailable: fr ? "L’indice est momentanément indisponible." : "The index is temporarily unavailable.", reproNoData: fr ? "Aucune comparaison enregistrée : aucun indice calculable." : "No recorded comparisons; no index can be calculated.", reproIndex: fr ? "Indice documentaire" : "Evidence index", reproStatus: fr ? "État des comparaisons" : "Comparison status", reproComponents: fr ? "Composantes (sur 20 points chacune)" : "Components (20 points each)", reproDisclaimer: fr ? "Cet indice mesure uniquement la complétude des éléments enregistrés. Il ne mesure ni la vérité, ni la qualité scientifique, ni la probabilité qu’un résultat soit correct." : "This index measures only the completeness of recorded evidence. It does not measure truth, scientific quality or the probability that a result is correct.", reproNoAssessment: fr ? "Non évalué" : "Not assessed", verification: fr ? "Plan de vérification ciblée" : "Targeted verification plan", checks: fr ? "Contrôles à examiner" : "Checks to review", reason: fr ? "Motif" : "Reason", noPlan: fr ? "Aucun plan associé aux comparaisons de ce dossier." : "No plan is associated with this dossier’s comparisons.", planUnavailable: fr ? "Les plans de vérification sont momentanément indisponibles." : "Verification plans are temporarily unavailable.", pending: fr ? "À examiner" : "Pending", inProgress: fr ? "En cours" : "In progress", completed: fr ? "Terminé" : "Completed", blocked: fr ? "Bloqué" : "Blocked", reviewerLabel: fr ? "Identifiant du réviseur" : "Reviewer label", reviewNote: fr ? "Note de revue obligatoire" : "Required review note", saveReview: fr ? "Enregistrer la revue" : "Save review", saved: fr ? "Événement ajouté à l’historique." : "Event added to history.", humanReview: fr ? "Revue humaine requise" : "Human review required", trace: fr ? "Chaîne de traçabilité" : "Traceability chain", traceText: fr ? "Question → sources → protocole → données → exécutions → reproductions → objections → revues → état des preuves" : "Question → sources → protocol → data → runs → reproductions → objections → reviews → evidence state"
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
    const graphSection = document.createElement("section"); graphSection.className = "evidence-section"; const graphHeading = document.createElement("h5"); graphHeading.textContent = document.documentElement.lang === "fr" ? "Graphe des preuves" : "Evidence graph"; const graphContainer = document.createElement("div"); graphContainer.className = "evidence-graph"; graphSection.append(graphHeading, graphContainer); panel.append(graphSection); if (typeof window.SSSWETRenderEvidenceGraph === "function") window.SSSWETRenderEvidenceGraph(graphContainer, dossier);
    const trace = document.createElement("div"); trace.className = "evidence-trace"; const traceTitle = document.createElement("strong"); traceTitle.textContent = labels.trace; const traceText = document.createElement("span"); traceText.textContent = labels.traceText; trace.append(traceTitle, traceText); panel.append(trace);
    const overview = document.createElement("section"); overview.className = "evidence-section evidence-overview"; const overviewHeading = document.createElement("h5"); overviewHeading.textContent = labels.question; overview.append(overviewHeading, field(labels.id, dossier.dossier_id), field(labels.state, dossier.verification_state), field(labels.assembledFrom, dossier.assembled_from_existing_records ? "Yes" : "No"), field(labels.validity, dossier.scientific_validity_established ? "Yes" : labels.no)); const summary = document.createElement("p"); summary.className = "evidence-result"; summary.textContent = text(dossier.result_summary); overview.append(summary); panel.append(overview);
    panel.append(collection(labels.sourcesTitle, dossier.sources, (item) => recordCard([[labels.id, item.source_id], ["Title", item.title], ["Type", item.source_type], ["Reference", item.reference]])));
    panel.append(collection(labels.protocols, dossier.protocols, (item) => recordCard([[labels.id, item.protocol_id], [labels.version, item.version], ["Fingerprint", item.fingerprint], [labels.state, item.status]])));
    panel.append(collection(labels.datasets, dossier.datasets, (item) => recordCard([[labels.id, item.dataset_id], [labels.version, item.version], ["SHA-256", item.content_sha256], ["Provenance", item.provenance]])));
    panel.append(collection(labels.runsTitle, dossier.runs, (item) => recordCard([[labels.id, item.run_id], ["Protocol", item.protocol_id], [labels.version, item.protocol_version], [labels.state, item.status], ["Started", item.started_at]])));
    panel.append(collection(labels.comparisonsTitle, dossier.comparisons, (item) => recordCard([
      [labels.id, item.comparison_id],
      ["Run A", item.left_run_id || item.reference_run_id],
      ["Run B", item.right_run_id || item.candidate_run_id],
      ["Comparable conditions", item.comparable],
      ["Outputs match within tolerance", item.outputs_match_within_tolerance],
      ["Tolerance", item.tolerance],
      ["Independent reproduction candidate", item.independent_reproduction_candidate],
      ["Independence independently verified", item.independence_independently_verified],
      ["Same environment", item.same_environment],
      ["Same code / model reference", item.same_code_or_model_reference],
      ["Differences", Array.isArray(item.differences) ? item.differences.length : "—"],
      ["Human review required", item.requires_human_review],
      [labels.validity, item.scientific_validity_established]
    ])));
    panel.append(collection(labels.objections, dossier.objections, (item) => recordCard([[labels.note, item]])));
    panel.append(collection(labels.disputes, dossier.disputes, (item) => recordCard([[labels.id, item.case_id], [labels.state, item.status], [labels.note, item.summary || item.description]])));
    const reviews = (dossier.events || []).filter((event) => event.kind === "review"); panel.append(collection(labels.review, reviews, (item) => recordCard([[labels.reviewer, item.reviewer_campaign_id], [labels.decision, item.decision], [labels.note, item.note], [labels.created, item.created_at]])));
    panel.append(collection(labels.eventsTitle, dossier.events, (item) => recordCard([[labels.id, item.event_id], ["Kind", item.kind], [labels.created, item.created_at], ["Dossier", item.dossier_id]])));
    const boardSection = document.createElement("section"); boardSection.className = "evidence-section evidence-review-board";
    const boardHeading = document.createElement("h5"); boardHeading.textContent = labels.scientificBoard; boardSection.append(boardHeading);
    const boardStatus = document.createElement("p"); boardStatus.className = "evidence-muted"; boardStatus.textContent = labels.boardLoading; boardSection.append(boardStatus);
    const boardList = document.createElement("div"); boardList.className = "evidence-record-list"; boardSection.append(boardList);
    const boardForm = document.createElement("form"); boardForm.className = "evidence-board-form";
    const boardReviewer = document.createElement("input"); boardReviewer.required = true; boardReviewer.maxLength = 200; boardReviewer.placeholder = labels.reviewerId; boardReviewer.setAttribute("aria-label", labels.reviewerId);
    const verdict = document.createElement("select"); verdict.setAttribute("aria-label", labels.verdict);
    [["supports", labels.supports], ["challenges", labels.challenges], ["mixed", labels.mixed], ["abstains", labels.abstains]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; verdict.append(option); });
    const conflict = document.createElement("select"); conflict.setAttribute("aria-label", labels.conflict);
    [["none_declared", labels.noneDeclared], ["potential", labels.potential], ["confirmed", labels.confirmed]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; conflict.append(option); });
    const rationale = document.createElement("textarea"); rationale.required = true; rationale.maxLength = 4000; rationale.placeholder = labels.rationale; rationale.setAttribute("aria-label", labels.rationale);
    const methods = document.createElement("textarea"); methods.required = true; methods.maxLength = 4000; methods.placeholder = labels.methodsAssessment; methods.setAttribute("aria-label", labels.methodsAssessment);
    const limitations = document.createElement("textarea"); limitations.required = true; limitations.maxLength = 4000; limitations.placeholder = labels.limitations; limitations.setAttribute("aria-label", labels.limitations);
    const refs = document.createElement("input"); refs.placeholder = labels.evidenceRefs; refs.maxLength = 3000; refs.setAttribute("aria-label", labels.evidenceRefs);
    const boardSubmit = document.createElement("button"); boardSubmit.type = "submit"; boardSubmit.textContent = labels.submitAssessment;
    const boardFeedback = document.createElement("span"); boardFeedback.className = "evidence-review-feedback"; boardFeedback.setAttribute("aria-live", "polite");
    boardForm.append(boardReviewer, verdict, conflict, rationale, methods, limitations, refs, boardSubmit, boardFeedback); boardSection.append(boardForm); panel.append(boardSection);
    const loadBoard = () => get("/api/scientific-review-board?dossier_id=" + encodeURIComponent(dossier.dossier_id)).then((report) => {
      boardList.replaceChildren(); const reviews = Array.isArray(report.reviews) ? report.reviews : [];
      const summary = (report.summaries || [])[0];
      boardStatus.textContent = reviews.length ? (summary?.disagreement_recorded ? labels.disagreement + " · " : "") + reviews.length + " " + labels.events + " · " + labels.noConsensus : labels.boardEmpty;
      reviews.forEach((review) => {
        const item = recordCard([[labels.reviewerId, review.reviewer_id], [labels.verdict, review.verdict], [labels.conflict, review.conflict_status], [labels.rationale, review.rationale], [labels.methodsAssessment, review.methods_assessment], [labels.limitations, review.limitations], [labels.evidenceRefs, (review.evidence_refs || []).join(", ")], [labels.created, review.created_at]]);
        item.classList.add("evidence-board-review"); boardList.append(item);
      });
    }).catch(() => { boardStatus.textContent = labels.planUnavailable; });
    loadBoard();
    boardForm.addEventListener("submit", async (event) => {
      event.preventDefault(); boardSubmit.disabled = true; boardFeedback.textContent = "…";
      try {
        const response = await fetch("/api/scientific-review-board/reviews", {method: "POST", headers: {"Content-Type": "application/json", "Accept": "application/json"}, body: JSON.stringify({
          dossier_id: dossier.dossier_id, reviewer_id: boardReviewer.value, verdict: verdict.value,
          conflict_status: conflict.value, rationale: rationale.value, methods_assessment: methods.value,
          limitations: limitations.value, evidence_refs: refs.value.split(",").map((item) => item.trim()).filter(Boolean)
        })});
        const payload = await response.json(); if (!response.ok) throw new Error(payload.error || "HTTP " + response.status);
        boardFeedback.textContent = labels.boardSaved; boardForm.reset(); await loadBoard();
      } catch (error) { boardFeedback.textContent = error.message; }
      finally { boardSubmit.disabled = false; }
    });
    const integritySection = document.createElement("section"); integritySection.className = "evidence-section evidence-integrity";
    const integrityHeading = document.createElement("h5"); integrityHeading.textContent = labels.integrityTitle; integritySection.append(integrityHeading);
    const integrityStatus = document.createElement("p"); integrityStatus.className = "evidence-muted"; integrityStatus.textContent = labels.riskLoading; integritySection.append(integrityStatus);
    const integrityList = document.createElement("div"); integrityList.className = "evidence-record-list"; integritySection.append(integrityList);
    const riskForm = document.createElement("form"); riskForm.className = "evidence-risk-form";
    const riskReviewer = document.createElement("input"); riskReviewer.required = true; riskReviewer.maxLength = 200; riskReviewer.placeholder = labels.riskReviewer; riskReviewer.setAttribute("aria-label", labels.riskReviewer);
    const category = document.createElement("select"); category.setAttribute("aria-label", labels.riskCategory);
    [["data_integrity", "Data integrity"], ["bias", "Bias"], ["conflict_of_interest", "Conflict of interest"], ["reproducibility", "Reproducibility"], ["safety", "Safety"], ["ethics", "Ethics"], ["legal_regulatory", "Legal / regulatory"], ["security", "Security"], ["other", "Other"]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; category.append(option); });
    const severity = document.createElement("select"); severity.setAttribute("aria-label", labels.riskSeverity);
    [["low", "Low"], ["medium", "Medium"], ["high", "High"], ["critical", "Critical"]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; severity.append(option); });
    const description = document.createElement("textarea"); description.required = true; description.maxLength = 4000; description.placeholder = labels.riskDescription; description.setAttribute("aria-label", labels.riskDescription);
    const riskState = document.createElement("select"); riskState.setAttribute("aria-label", labels.riskState);
    [["open", labels.riskOpen], ["under_review", labels.riskUnderReview], ["escalated", labels.riskEscalated], ["mitigated", labels.riskMitigated], ["accepted_with_controls", labels.riskAccepted], ["closed", labels.riskClosed]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; riskState.append(option); });
    const mitigation = document.createElement("textarea"); mitigation.maxLength = 4000; mitigation.placeholder = labels.riskMitigation; mitigation.setAttribute("aria-label", labels.riskMitigation);
    const authorization = document.createElement("input"); authorization.maxLength = 500; authorization.placeholder = labels.riskAuthorization; authorization.setAttribute("aria-label", labels.riskAuthorization);
    const riskSubmit = document.createElement("button"); riskSubmit.type = "submit"; riskSubmit.textContent = labels.riskSubmit;
    const riskFeedback = document.createElement("span"); riskFeedback.className = "evidence-review-feedback"; riskFeedback.setAttribute("aria-live", "polite");
    riskForm.append(riskReviewer, category, severity, description, riskState, mitigation, authorization, riskSubmit, riskFeedback); integritySection.append(riskForm);
    const integrityNotice = document.createElement("p"); integrityNotice.className = "evidence-muted"; integrityNotice.textContent = labels.riskNoAuto; integritySection.append(integrityNotice); panel.append(integritySection);
    const loadIntegrity = () => get("/api/research-integrity?dossier_id=" + encodeURIComponent(dossier.dossier_id)).then((report) => {
      integrityList.replaceChildren(); const risks = Array.isArray(report.risks) ? report.risks : [];
      integrityStatus.textContent = risks.length ? risks.length + " " + labels.events : labels.riskEmpty;
      integritySection.querySelectorAll(".evidence-integrity-warning").forEach((item) => item.remove());
      if (report.campaign_hold_recommendation) { const warning = document.createElement("p"); warning.className = "evidence-integrity-warning"; warning.textContent = labels.riskHold; integritySection.insertBefore(warning, integrityList); }
      risks.forEach((risk) => {
        const item = recordCard([[labels.id, risk.risk_id], [labels.riskCategory, risk.category], [labels.riskSeverity, risk.severity], [labels.state, risk.state], [labels.riskDescription, risk.description], [labels.riskReviewer, risk.reviewer_label], [labels.riskMitigation, risk.mitigation || "—"], [labels.riskAuthorization, risk.authorization_reference || "—"], [labels.created, risk.created_at]]);
        item.classList.add("evidence-integrity-risk"); integrityList.append(item);
      });
      const history = document.createElement("details"); const summary = document.createElement("summary"); summary.textContent = labels.riskHistory; history.append(summary);
      (report.events || []).forEach((entry) => { const line = document.createElement("p"); line.className = "evidence-review-history"; line.textContent = entry.created_at + " · " + entry.risk_id + " · " + entry.state + " · " + entry.reviewer_label + " — " + entry.description; history.append(line); });
      integrityList.append(history);
    }).catch(() => { integrityStatus.textContent = labels.planUnavailable; });
    loadIntegrity();
    riskForm.addEventListener("submit", async (event) => {
      event.preventDefault(); riskSubmit.disabled = true; riskFeedback.textContent = "…";
      try {
        const response = await fetch("/api/research-integrity/risks", {method: "POST", headers: {"Content-Type": "application/json", "Accept": "application/json"}, body: JSON.stringify({
          dossier_id: dossier.dossier_id, category: category.value, severity: severity.value,
          description: description.value, reviewer_label: riskReviewer.value, state: riskState.value, mitigation: mitigation.value, authorization_reference: authorization.value
        })});
        const payload = await response.json(); if (!response.ok) throw new Error(payload.error || "HTTP " + response.status);
        riskFeedback.textContent = labels.riskSaved; description.value = ""; await loadIntegrity();
      } catch (error) { riskFeedback.textContent = error.message; }
      finally { riskSubmit.disabled = false; }
    });
    const verificationSection = document.createElement("section"); verificationSection.className = "evidence-section evidence-verification";
    const verificationHeading = document.createElement("h5"); verificationHeading.textContent = labels.verification; verificationSection.append(verificationHeading);
    const verificationStatus = document.createElement("p"); verificationStatus.className = "evidence-muted"; verificationStatus.textContent = "…"; verificationSection.append(verificationStatus); panel.append(verificationSection);
    const dossierComparisonIds = new Set((dossier.comparisons || []).map((item) => item.comparison_id));
    if (dossierComparisonIds.size) {
      get("/api/lab-verification-plans").then((payload) => {
        verificationSection.querySelectorAll(".evidence-verification-plan").forEach((item) => item.remove());
        const plans = (Array.isArray(payload.plans) ? payload.plans : []).filter((plan) => dossierComparisonIds.has(plan.comparison_id));
        verificationStatus.textContent = plans.length ? labels.humanReview : labels.noPlan;
        plans.forEach((plan) => {
          const card = document.createElement("article"); card.className = "evidence-record evidence-verification-plan";
          card.append(field(labels.id, plan.plan_id), field(labels.state, plan.classification), field(labels.humanReview, plan.requires_human_review ? "Yes" : "No"));
          const list = document.createElement("ol"); list.className = "evidence-check-list";
          (plan.checks || []).forEach((check) => {
            const item = document.createElement("li"); const title = document.createElement("strong"); title.textContent = check.instruction; const reason = document.createElement("p"); reason.textContent = labels.reason + ": " + text(check.reason);
            const state = document.createElement("p"); state.className = "evidence-review-state"; const stateLabels = {pending: labels.pending, in_progress: labels.inProgress, completed: labels.completed, blocked: labels.blocked}; state.textContent = (stateLabels[check.review_state] || labels.pending) + " · " + (check.review_history || []).length + " " + labels.events;
            (check.review_history || []).forEach((entry) => { const history = document.createElement("p"); history.className = "evidence-review-history"; history.textContent = text(entry.created_at) + " · " + text(entry.reviewer) + " · " + (stateLabels[entry.state] || entry.state) + " — " + text(entry.note); item.append(history); });
            const form = document.createElement("form"); form.className = "evidence-review-form";
            const reviewer = document.createElement("input"); reviewer.type = "text"; reviewer.maxLength = 200; reviewer.required = true; reviewer.placeholder = labels.reviewerLabel; reviewer.setAttribute("aria-label", labels.reviewerLabel);
            const note = document.createElement("textarea"); note.maxLength = 4000; note.required = true; note.rows = 2; note.placeholder = labels.reviewNote; note.setAttribute("aria-label", labels.reviewNote);
            const select = document.createElement("select"); select.setAttribute("aria-label", labels.state);
            [["in_progress", labels.inProgress], ["completed", labels.completed], ["blocked", labels.blocked]].forEach(([value, label]) => { const option = document.createElement("option"); option.value = value; option.textContent = label; select.append(option); });
            const submit = document.createElement("button"); submit.type = "submit"; submit.textContent = labels.saveReview; if (check.review_state === "completed") { form.hidden = true; }
            const feedback = document.createElement("span"); feedback.className = "evidence-review-feedback"; feedback.setAttribute("aria-live", "polite");
            form.append(reviewer, select, note, submit, feedback);
            form.addEventListener("submit", async (event) => {
              event.preventDefault(); submit.disabled = true; feedback.textContent = "…";
              try {
                const response = await fetch("/api/lab-verification-events", {method: "POST", headers: {"Content-Type": "application/json", "Accept": "application/json"}, body: JSON.stringify({plan_id: plan.plan_id, check_code: check.code, state: select.value, note: note.value, reviewer: reviewer.value})});
                const payload = await response.json(); if (!response.ok) throw new Error(payload.error || "HTTP " + response.status);
                feedback.textContent = labels.saved; form.hidden = true; state.textContent = (stateLabels[payload.event.state] || payload.event.state) + " · " + ((check.review_history || []).length + 1) + " " + labels.events;
              } catch (error) { feedback.textContent = error.message; submit.disabled = false; }
            });
            item.append(title, reason, state, form); list.append(item);
          });
          card.append(list); card.append(field(labels.validity, plan.scientific_validity_established ? "Yes" : labels.no)); verificationSection.append(card);
        });
      }).catch(() => { verificationStatus.textContent = labels.planUnavailable; });
    } else { verificationStatus.textContent = labels.noPlan; }
    const reproducibilitySection = document.createElement("section"); reproducibilitySection.className = "evidence-section evidence-reproducibility";
    const reproducibilityHeading = document.createElement("h5"); reproducibilityHeading.textContent = labels.reproTitle; reproducibilitySection.append(reproducibilityHeading);
    const reproducibilityStatus = document.createElement("p"); reproducibilityStatus.className = "evidence-muted"; reproducibilityStatus.textContent = labels.reproLoading; reproducibilitySection.append(reproducibilityStatus);
    const reproducibilityList = document.createElement("div"); reproducibilityList.className = "evidence-record-list"; reproducibilitySection.append(reproducibilityList);
    const reproducibilityDisclaimer = document.createElement("p"); reproducibilityDisclaimer.className = "evidence-note"; reproducibilityDisclaimer.textContent = labels.reproDisclaimer; reproducibilitySection.append(reproducibilityDisclaimer); panel.append(reproducibilitySection);
    get("/api/reproducibility-intelligence").then((report) => {
      const comparisons = new Set((dossier.comparisons || []).map((item) => item.comparison_id));
      const protocols = (report.protocols || []).filter((item) => (item.comparisons || []).some((comparison) => comparisons.has(comparison.comparison_id)));
      reproducibilityList.replaceChildren();
      if (!protocols.length) { reproducibilityStatus.textContent = labels.reproNoData; return; }
      reproducibilityStatus.textContent = protocols.length + " " + labels.protocols.toLowerCase();
      protocols.forEach((protocol) => {
        const card = document.createElement("article"); card.className = "evidence-record evidence-reproducibility-card";
        const indexValue = protocol.reproducibility_evidence_index === null ? labels.reproNoAssessment : protocol.reproducibility_evidence_index + " / 100";
        card.append(field(labels.protocols, protocol.protocol_title || (protocol.protocol_id + " · v" + protocol.protocol_version)), field(labels.reproIndex, indexValue), field(labels.reproStatus, protocol.status), field(labels.runsTitle, protocol.run_count), field(labels.comparisonsTitle, protocol.comparison_count));
        const heading = document.createElement("strong"); heading.textContent = labels.reproComponents; card.append(heading);
        (protocol.comparisons || []).filter((comparison) => comparisons.has(comparison.comparison_id)).forEach((comparison) => {
          const pair = document.createElement("div"); pair.className = "evidence-repro-pair";
          pair.append(field(labels.id, comparison.comparison_id), field(labels.state, comparison.classification), field(labels.reproIndex, comparison.index + " / 100"));
          Object.entries(comparison.components || {}).forEach(([name, value]) => pair.append(field(name.replaceAll("_", " "), value + " / 20")));
          card.append(pair);
        });
        const sensitivity = document.createElement("p"); sensitivity.className = "evidence-muted"; sensitivity.textContent = labels.reproNoAssessment + " · " + ((protocol.parameter_sensitivity || {}).reason || ""); card.append(sensitivity);
        reproducibilityList.append(card);
      });
    }).catch(() => { reproducibilityStatus.textContent = labels.reproUnavailable; });
    const validity = document.createElement("p"); validity.className = "evidence-validity"; validity.textContent = labels.validity + ": " + labels.no; panel.append(validity); const note = document.createElement("p"); note.className = "evidence-note"; note.textContent = labels.separation; panel.append(note); body.append(panel);
  }

  async function load() { root.replaceChildren(); status.textContent = "…"; try { const payload = await get("/api/evidence-dossiers?limit=50"); const dossiers = Array.isArray(payload.dossiers) ? payload.dossiers : []; status.textContent = String(dossiers.length); if (!dossiers.length) { const empty = document.createElement("p"); empty.className = "visual-empty"; empty.textContent = t().empty; root.append(empty); return; } dossiers.forEach((dossier) => root.append(renderDossier(dossier))); } catch { status.textContent = "—"; const error = document.createElement("p"); error.className = "visual-empty"; error.textContent = t().unavailable; root.append(error); } }
  refreshButton?.addEventListener("click", load); window.addEventListener("ssswet-language-changed", load); load();
})();
