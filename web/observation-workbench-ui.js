(() => {
  "use strict";
  const api = window.SSSWETObservationWorkbench;
  if (!api) return;
  const $ = id => document.getElementById(id);
  const copy = {
    en: {
      language: "Language", title: "Observation analysis workbench", intro: "Validate and review an observation index exported by Virtual Time Travel Mapping. All analysis runs in this browser; this page does not upload your file.",
      importTitle: "1. Import an observation index", importHelp: "Choose an ssswet-observation-index.json file exported from the mapping interface. Media files are not included.", fileLabel: "Observation index JSON", limits: "Limits: 20 MiB per file and 50,000 observations. Unsupported versions or invalid records are rejected without changing your original file.", statusWaiting: "Waiting for a local file.",
      observations: "Observations", sessions: "Sessions", gps: "GPS fixes", flags: "Quality flags", provenanceTitle: "2. Provenance and clock audit", sessionNote: "Capture sessions are isolated. Device wall-clock anchors from different sessions are not assumed comparable; the report never infers a global chronology.",
      qualityTitle: "3. GPS quality diagnostics", qualityRecords: "First 100 flagged records", qualityHelp: "Flags identify records or segments for review. They do not delete observations or establish that a location is wrong.", coverageTitle: "4. Temporal coverage and route metrics", coverageHelp: "Sampling gaps describe recorded cadence only; they do not prove that no event occurred during an interval.", duplicatesTitle: "5. Duplicate review candidates", duplicatesHelp: "Exact and near-duplicate candidates are suggestions for human review. Nothing is merged, hidden or deleted.",
      privacyTitle: "6. Privacy-adjusted export", privacyHelp: "Choose what to include in a new copy. The imported source remains unchanged. The default profile reduces location and time precision and removes free-text descriptions and detailed sensor values.", coordinatePrecision: "Coordinate decimals", timePrecision: "Time precision", includeDescriptions: "Include free-text descriptions", includeSensors: "Include detailed motion and orientation values", includeClock: "Include clock diagnostics", includeSessions: "Include capture-session identifiers", pseudonymize: "Replace record IDs with sequential local labels", exportJson: "Export adjusted JSON + integrity manifest", exportCsv: "Export CSV", exportGeojson: "Export GeoJSON", exportManifest: "Export integrity manifest only", integrityWaiting: "No integrity manifest checked.", back: "Back to Virtual Time Travel Mapping", footer: "SSSWET research prototype · Local analysis only · Not a scientific or safety certification.",
      loaded: "Index loaded and validated. Analysis completed locally.", invalid: "The index could not be accepted. No analysis or export was performed.", noFile: "Choose a JSON file first.", tooLarge: "The file exceeds the 20 MiB limit.", readFailed: "The file could not be read.", noManifest: "This input has no embedded integrity manifest. You can create one for an adjusted export.", manifestValid: "Integrity manifest matches the imported observations. This checks accidental changes, not authorship or authenticity.", manifestInvalid: "Integrity manifest does not match the imported observations.", exported: "Export created locally.", cryptoUnavailable: "Web Crypto is unavailable. Open this page over HTTPS or localhost to create SHA-256 manifests.",
      session: "Session", records: "Records", start: "Start (device time)", end: "End (device time)", duration: "Span", medianAccuracy: "Median GPS accuracy", kinds: "Kinds", clock: "Clock states", code: "Diagnostic", count: "Count", record: "Record ID", type: "Candidate type", details: "Details", gaps: "Gaps", medianInterval: "Median interval", longestGap: "Longest gap", distance: "Route distance", acceptedSegments: "Accepted segments", excludedSegments: "Excluded segments", excludedLowAccuracy: "low accuracy", averageSpeed: "Average speed", maxSpeed: "Maximum observed speed", noRows: "No rows to display.", noFlags: "No GPS quality flags found under the current screening thresholds.", noDuplicates: "No duplicate candidates found.", provenance: "Clock metadata retained: {kept}; missing: {missing}. Wall-clock divergence flags: {diverged}. Monotonic/order regressions: {regressions}.", duplicates: "{count} duplicate candidates; {comparisons} comparisons; truncated: {truncated}.", coverage: "Sampling gaps are descriptive and are not evidence of event absence. Sessions are summarized independently."
    },
    fr: {
      language: "Langue", title: "Atelier d’analyse des observations", intro: "Validez et examinez un index exporté depuis Virtual Time Travel Mapping. Toute l’analyse s’effectue dans ce navigateur ; aucun fichier n’est envoyé.",
      importTitle: "1. Importer un index d’observations", importHelp: "Choisissez un fichier ssswet-observation-index.json exporté depuis l’interface cartographique. Les médias ne sont pas inclus.", fileLabel: "Index d’observations JSON", limits: "Limites : 20 Mio par fichier et 50 000 observations. Les versions non prises en charge ou les enregistrements invalides sont refusés sans modifier le fichier original.", statusWaiting: "En attente d’un fichier local.",
      observations: "Observations", sessions: "Sessions", gps: "Positions GPS", flags: "Alertes qualité", provenanceTitle: "2. Audit de provenance et des horloges", sessionNote: "Les sessions restent séparées. Les horloges système de sessions différentes ne sont pas supposées comparables ; aucune chronologie globale n’est déduite.",
      qualityTitle: "3. Diagnostics de qualité GPS", qualityRecords: "100 premiers enregistrements signalés", qualityHelp: "Les alertes signalent des enregistrements ou segments à examiner. Elles ne suppriment rien et ne prouvent pas qu’une position est erronée.", coverageTitle: "4. Couverture temporelle et métriques d’itinéraire", coverageHelp: "Les intervalles décrivent uniquement la cadence enregistrée ; ils ne prouvent pas qu’aucun événement ne s’est produit pendant une période.", duplicatesTitle: "5. Candidats aux doublons", duplicatesHelp: "Les doublons exacts ou proches sont proposés à l’examen humain. Rien n’est fusionné, masqué ou supprimé.",
      privacyTitle: "6. Export avec réglages de confidentialité", privacyHelp: "Choisissez les informations à inclure dans une nouvelle copie. La source importée reste inchangée. Le profil par défaut réduit la précision géographique et temporelle et retire les descriptions libres et les valeurs détaillées des capteurs.", coordinatePrecision: "Décimales des coordonnées", timePrecision: "Précision temporelle", includeDescriptions: "Inclure les descriptions libres", includeSensors: "Inclure les valeurs détaillées de mouvement et d’orientation", includeClock: "Inclure les diagnostics d’horloge", includeSessions: "Inclure les identifiants de session", pseudonymize: "Remplacer les identifiants par des libellés locaux séquentiels", exportJson: "Exporter le JSON ajusté + manifeste d’intégrité", exportCsv: "Exporter en CSV", exportGeojson: "Exporter en GeoJSON", exportManifest: "Exporter uniquement le manifeste d’intégrité", integrityWaiting: "Aucun manifeste d’intégrité vérifié.", back: "Retour à Virtual Time Travel Mapping", footer: "Prototype de recherche SSSWET · Analyse locale uniquement · Aucune certification scientifique ou de sécurité.",
      loaded: "Index chargé et validé. Analyse effectuée localement.", invalid: "L’index n’a pas été accepté. Aucune analyse ni export n’a été effectué.", noFile: "Choisissez d’abord un fichier JSON.", tooLarge: "Le fichier dépasse la limite de 20 Mio.", readFailed: "Le fichier n’a pas pu être lu.", noManifest: "Ce fichier ne contient pas de manifeste d’intégrité. Vous pouvez en créer un pour un export ajusté.", manifestValid: "Le manifeste correspond aux observations importées. Il détecte les modifications accidentelles, pas l’auteur ni l’authenticité.", manifestInvalid: "Le manifeste d’intégrité ne correspond pas aux observations importées.", exported: "Export créé localement.", cryptoUnavailable: "Web Crypto est indisponible. Ouvrez cette page en HTTPS ou sur localhost pour créer des manifestes SHA-256.",
      session: "Session", records: "Enregistrements", start: "Début (heure appareil)", end: "Fin (heure appareil)", duration: "Étendue", medianAccuracy: "Précision GPS médiane", kinds: "Types", clock: "États d’horloge", code: "Diagnostic", count: "Nombre", record: "Identifiant", type: "Type de candidat", details: "Détails", gaps: "Intervalles", medianInterval: "Intervalle médian", longestGap: "Plus long intervalle", distance: "Distance de l’itinéraire", acceptedSegments: "Segments acceptés", excludedSegments: "Segments exclus", excludedLowAccuracy: "faible précision", averageSpeed: "Vitesse moyenne", maxSpeed: "Vitesse observée maximale", noRows: "Aucune ligne à afficher.", noFlags: "Aucune alerte GPS selon les seuils actuels.", noDuplicates: "Aucun candidat doublon détecté.", provenance: "Métadonnées d’horloge conservées : {kept} ; absentes : {missing}. Écarts d’horloge système : {diverged}. Régressions monotones/de séquence : {regressions}.", duplicates: "{count} candidats doublons ; {comparisons} comparaisons ; résultat tronqué : {truncated}.", coverage: "Les intervalles sont descriptifs et ne prouvent pas l’absence d’événement. Les sessions sont résumées séparément."
    }
  };
  let locale = "en";
  let sourcePayload = null;
  let report = null;

  function t(key) { return copy[locale][key] || copy.en[key] || key; }
  function applyLocale() {
    const browser = (navigator.language || "en").toLowerCase();
    locale = $("language").value || (browser.startsWith("fr") ? "fr" : "en");
    document.documentElement.lang = locale;
    document.documentElement.dir = "ltr";
    document.querySelectorAll("[data-i]").forEach(node => { node.textContent = t(node.dataset.i); });
  }
  function setStatus(message, bad) {
    const node = $("status");
    node.textContent = message;
    node.classList.toggle("bad", !!bad);
  }
  function formatDate(value) {
    if (!Number.isFinite(value)) return "—";
    try { return new Intl.DateTimeFormat(locale, { dateStyle: "short", timeStyle: "short", timeZone: "UTC" }).format(new Date(value)) + " UTC"; }
    catch (_) { return String(value); }
  }
  function formatDuration(ms) {
    if (!Number.isFinite(ms)) return "—";
    const seconds = Math.round(ms / 1000);
    if (seconds < 60) return seconds + " s";
    if (seconds < 3600) return Math.floor(seconds / 60) + " min";
    return (seconds / 3600).toFixed(2) + " h";
  }
  function makeTable(container, headers, rows, caption) {
    container.replaceChildren();
    const table = document.createElement("table");
    if (caption) { const cap = document.createElement("caption"); cap.textContent = caption; table.append(cap); }
    const thead = document.createElement("thead"), headRow = document.createElement("tr");
    headers.forEach(label => { const th = document.createElement("th"); th.scope = "col"; th.textContent = label; headRow.append(th); });
    thead.append(headRow); table.append(thead);
    const tbody = document.createElement("tbody");
    (rows.length ? rows : [[t("noRows")]]).forEach(row => {
      const tr = document.createElement("tr");
      row.forEach(value => { const td = document.createElement("td"); td.textContent = value === null || value === undefined ? "—" : String(value); tr.append(td); });
      if (!rows.length) { const td = tr.firstElementChild; td.colSpan = headers.length; }
      tbody.append(tr);
    });
    table.append(tbody); container.append(table);
  }
  function render() {
    const observations = sourcePayload.observations;
    $("report").hidden = false;
    $("metric-observations").textContent = String(observations.length);
    $("metric-sessions").textContent = String(report.provenance.sessionCount);
    $("metric-gps").textContent = String(observations.filter(e => e.kind === "gps").length);
    $("metric-flags").textContent = String(report.gpsQuality.flagCount);
    const p = report.provenance;
    $("provenance-summary").textContent = t("provenance").replace("{kept}", p.recordsWithClockMetadata).replace("{missing}", p.recordsMissingClockMetadata).replace("{diverged}", p.wallClockDivergedRecords).replace("{regressions}", p.orderingRegressions);
    makeTable($("sessions-table"), [t("session"), t("records"), t("gps"), t("start"), t("end"), t("duration"), t("medianAccuracy")], report.sessionSummaries.sessions.map(s => [s.sessionKey, s.recordCount, s.gpsFixCount, formatDate(s.startTimestamp), formatDate(s.endTimestamp), formatDuration(s.durationMs), s.medianGpsAccuracyM === null ? "—" : s.medianGpsAccuracyM.toFixed(1) + " m"]));
    const qualityRows = Object.entries(report.gpsQuality.counts).map(([code, count]) => [code, count]);
    makeTable($("quality-table"), [t("code"), t("count")], qualityRows);
    const flagRows = report.gpsQuality.flags.slice(0, 100).map(flag => [flag.id, flag.sessionKey, flag.code]);
    makeTable($("quality-records-table"), [t("record"), t("session"), t("code")], flagRows, t("qualityRecords"));
    makeTable($("coverage-table"), [t("session"), t("gps"), t("medianInterval"), t("gaps"), t("longestGap")], report.temporalCoverage.sessions.map(s => [s.sessionKey, s.gpsFixCount, formatDuration(s.medianIntervalMs), s.gapCount, formatDuration(s.longestGapMs)]));
    makeTable($("routes-table"), [t("session"), t("distance"), t("acceptedSegments"), t("excludedSegments") + " / " + t("excludedLowAccuracy"), t("averageSpeed"), t("maxSpeed")], report.routeMetrics.sessions.map(s => [s.sessionKey, s.distanceM.toFixed(1) + " m", s.acceptedSegments, s.excludedSegments + " / " + s.excludedLowAccuracySegments, s.averageSpeedMps === null ? "—" : s.averageSpeedMps.toFixed(2) + " m/s", s.maxObservedSpeedMps === null ? "—" : s.maxObservedSpeedMps.toFixed(2) + " m/s"]));
    const duplicateRows = report.duplicates.candidates.map(c => [c.type, (c.recordIds || []).join(", "), c.distanceM === undefined ? "—" : c.distanceM + " m"]);
    makeTable($("duplicates-table"), [t("type"), t("record"), t("details")], duplicateRows);
    if (!qualityRows.length) { $("quality-table").firstElementChild.querySelector("tbody td").textContent = t("noFlags"); $("quality-records-table").firstElementChild.querySelector("tbody td").textContent = t("noFlags"); }
    if (!duplicateRows.length) $("duplicates-table").firstElementChild.querySelector("tbody td").textContent = t("noDuplicates");
    const duplicateNote = document.createElement("p"); duplicateNote.className = "note"; duplicateNote.textContent = t("duplicates").replace("{count}", report.duplicates.candidates.length).replace("{comparisons}", report.duplicates.comparisonCount).replace("{truncated}", report.duplicates.truncated ? "yes" : "no"); $("duplicates-table").append(duplicateNote);
    ["export-json", "export-csv", "export-geojson", "export-manifest"].forEach(id => { $(id).disabled = false; });
    const embedded = sourcePayload.integrityManifest || sourcePayload.integrity_manifest;
    if (!embedded) $("integrity-status").textContent = t("noManifest");
    else api.verifyIntegrityManifest(sourcePayload, embedded).then(result => { $("integrity-status").textContent = result.valid ? t("manifestValid") : t("manifestInvalid"); }).catch(() => { $("integrity-status").textContent = t("cryptoUnavailable"); });
  }
  function exportOptions() {
    return {
      coordinateDecimals: Number($("coordinate-decimals").value),
      timePrecision: $("time-precision").value,
      includeDescriptions: $("include-descriptions").checked,
      includeSensorValues: $("include-sensors").checked,
      includeClockMetadata: $("include-clock").checked,
      includeSessionIds: $("include-sessions").checked,
      pseudonymizeIds: $("pseudonymize-ids").checked
    };
  }
  function adjustedPayload() { return api.privacyTransform(sourcePayload, exportOptions()); }
  function download(name, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url; link.download = name; link.hidden = true; document.body.append(link); link.click(); link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function exportJson() {
    try {
      const payload = adjustedPayload();
      payload.integrityManifest = await api.createIntegrityManifest(payload);
      download("ssswet-observations-adjusted.json", JSON.stringify(payload, null, 2), "application/json;charset=utf-8");
      $("integrity-status").textContent = t("exported");
    } catch (_) { $("integrity-status").textContent = t("cryptoUnavailable"); }
  }
  async function exportManifest() {
    try {
      const manifest = await api.createIntegrityManifest(adjustedPayload());
      download("ssswet-observations-integrity.json", JSON.stringify(manifest, null, 2), "application/json;charset=utf-8");
      $("integrity-status").textContent = t("exported");
    } catch (_) { $("integrity-status").textContent = t("cryptoUnavailable"); }
  }
  function resetReport() {
    sourcePayload = null;
    report = null;
    $("report").hidden = true;
    $("validation-errors").replaceChildren();
    ["export-json", "export-csv", "export-geojson", "export-manifest"].forEach(id => { $(id).disabled = true; });
  }
  function loadFile(file) {
    if (!file) { resetReport(); setStatus(t("noFile"), true); return; }
    resetReport();
    if (file.size > api.MAX_INPUT_BYTES) { setStatus(t("tooLarge"), true); return; }
    file.text().then(text => {
      const parsed = api.parseIndexText(text);
      $("validation-errors").replaceChildren();
      if (!parsed.ok) {
        parsed.errors.slice(0, 100).forEach(error => { const li = document.createElement("li"); li.textContent = error; $("validation-errors").append(li); });
        resetReport();
        setStatus(t("invalid"), true); return;
      }
      sourcePayload = parsed.payload;
      report = api.analyze(sourcePayload);
      render();
      setStatus(t("loaded"), false);
      parsed.warnings.slice(0, 100).forEach(warning => { const li = document.createElement("li"); li.textContent = warning; $("validation-errors").append(li); });
    }).catch(() => setStatus(t("readFailed"), true));
  }

  $("language").addEventListener("change", () => { applyLocale(); if (sourcePayload) render(); });
  const browser = (navigator.language || "en").toLowerCase();
  $("language").value = browser.startsWith("fr") ? "fr" : "en";
  applyLocale();
  $("index-file").addEventListener("change", event => loadFile(event.target.files && event.target.files[0]));
  $("export-json").addEventListener("click", () => exportJson());
  $("export-csv").addEventListener("click", () => { if (sourcePayload) { const adjusted = adjustedPayload(); download("ssswet-observations-adjusted.csv", api.toCSV(adjusted.observations), "text/csv;charset=utf-8"); setStatus(t("exported"), false); } });
  $("export-geojson").addEventListener("click", () => { if (sourcePayload) { const adjusted = adjustedPayload(); download("ssswet-observations-adjusted.geojson", JSON.stringify(api.toGeoJSON(adjusted.observations, { includeSessionIds: exportOptions().includeSessionIds, includeDescriptions: exportOptions().includeDescriptions }), null, 2), "application/geo+json;charset=utf-8"); setStatus(t("exported"), false); } });
  $("export-manifest").addEventListener("click", () => exportManifest());
})();