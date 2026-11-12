/* Local-only, anchor-bounded clock alignment workspace for Virtual Time Travel Mapping. */
(function () {
  "use strict";

  const MAX_ANCHORS = 500;
  const UI_MAX_ANCHORS = 20;
  const MAX_EVENTS = 5000;
  const MAX_ID_LENGTH = 160;
  const MAX_EVIDENCE_REF_LENGTH = 500;
  const ALIGNMENT_METHOD = "piecewise_linear_interpolation";
  const CLOCK_MAPPING_ASSUMPTION = "piecewise_linear_between_declared_anchors";
  const UNCERTAINTY_METHOD = "linear_sum_of_declared_absolute_bounds_under_piecewise_linear_model";
  const UNCERTAINTY_INTERPRETATION = "conditional_envelope_under_piecewise_linear_clock_mapping";
  const UNCERTAINTY_SEMANTICS = "Declared values are conservative absolute bounds in seconds; they are not standard deviations or confidence intervals.";
  const FLOAT_KEYS = new Set(["uncertainty_seconds", "source_interval_seconds", "reference_interval_seconds", "drift_ppm", "max_absolute_drift_ppm"]);
  const SOURCE_ID = "browser-session-clock";
  const DB_NAME = "ssswet-virtual-time-map";

  function fail(message) {
    throw new Error(message);
  }

  function identifier(value, field) {
    if (typeof value !== "string" || !value.trim() || value.trim().length > MAX_ID_LENGTH) {
      fail(field + " must contain 1 to " + MAX_ID_LENGTH + " characters");
    }
    return value.trim();
  }

  function nonnegative(value, field) {
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
      fail(field + " must be finite and non-negative");
    }
    return value;
  }

  function evidenceRef(value) {
    if (value === null || value === undefined) return null;
    if (typeof value !== "string" || value.trim().length > MAX_EVIDENCE_REF_LENGTH) {
      fail("reference_evidence_ref must contain at most " + MAX_EVIDENCE_REF_LENGTH + " characters");
    }
    return value.trim() || null;
  }

  function pythonIsoFromEpochMs(epochMs) {
    if (!Number.isFinite(epochMs)) fail("timestamp must be finite");
    const date = new Date(Math.round(epochMs));
    if (!Number.isFinite(date.getTime())) fail("timestamp is outside the supported date range");
    const iso = date.toISOString();
    const whole = iso.slice(0, 19);
    const fraction = iso.slice(20, 23);
    return fraction === "000" ? whole + "+00:00" : whole + "." + fraction + "000+00:00";
  }

  function parseZonedTimestamp(value, field) {
    if (typeof value !== "string" || !value.trim()) fail((field || "timestamp") + " must be an ISO timestamp with an explicit timezone");
    const text = value.trim();
    const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?(Z|[+-]\d{2}:\d{2})$/i.exec(text);
    if (!match) fail((field || "timestamp") + " must include Z or an explicit ±HH:MM offset and use millisecond precision or less");
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const hour = Number(match[4]);
    const minute = Number(match[5]);
    const second = Number(match[6]);
    const millisecond = Number((match[7] || "").padEnd(3, "0") || 0);
    if (year < 1 || month < 1 || month > 12 || day < 1 || hour > 23 || minute > 59 || second > 59) {
      fail((field || "timestamp") + " contains an invalid calendar or time value");
    }
    const local = new Date(0);
    local.setUTCFullYear(year, month - 1, day);
    local.setUTCHours(hour, minute, second, millisecond);
    if (local.getUTCFullYear() !== year || local.getUTCMonth() !== month - 1 || local.getUTCDate() !== day ||
        local.getUTCHours() !== hour || local.getUTCMinutes() !== minute || local.getUTCSeconds() !== second ||
        local.getUTCMilliseconds() !== millisecond) {
      fail((field || "timestamp") + " contains an invalid calendar date");
    }
    if (match[8].toUpperCase() !== "Z") {
      const offsetHours = Number(match[8].slice(1, 3));
      const offsetMinutes = Number(match[8].slice(4, 6));
      if (offsetHours > 23 || offsetMinutes > 59) fail((field || "timestamp") + " contains an invalid timezone offset");
    }
    const epochMs = Date.parse(text);
    if (!Number.isFinite(epochMs)) fail((field || "timestamp") + " is not a supported timestamp");
    return { epochMs: epochMs, iso: pythonIsoFromEpochMs(epochMs) };
  }

  function pythonFloat(value) {
    if (!Number.isFinite(value)) fail("canonical JSON cannot contain non-finite numbers");
    if (Object.is(value, -0)) return "-0.0";
    if (value === 0) return "0.0";
    const absolute = Math.abs(value);
    let raw = value.toString();
    if (absolute < 1e-4 || absolute >= 1e16) {
      const sign = raw.charAt(0) === "-" ? "-" : "";
      raw = raw.replace(/^-/, "").toLowerCase();
      let mantissa;
      let exponent;
      if (raw.includes("e")) {
        const pieces = raw.split("e");
        mantissa = pieces[0];
        exponent = Number(pieces[1]);
      } else {
        const pieces = raw.split(".");
        const digits = pieces.join("");
        const first = digits.search(/[1-9]/);
        exponent = pieces[0].length - first - 1;
        const significant = digits.slice(first).replace(/0+$/, "");
        mantissa = significant.charAt(0) + (significant.length > 1 ? "." + significant.slice(1) : "");
      }
      mantissa = mantissa.replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1");
      return sign + mantissa + "e" + (exponent >= 0 ? "+" : "-") + String(Math.abs(exponent)).padStart(2, "0");
    }
    if (!raw.includes(".") && !raw.includes("e")) return raw + ".0";
    return raw;
  }

  function canonicalJson(value, parentKey) {
    if (value === null) return "null";
    if (typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
    if (typeof value === "number") {
      if (FLOAT_KEYS.has(parentKey)) return pythonFloat(value);
      if (!Number.isFinite(value)) fail("canonical JSON cannot contain non-finite numbers");
      return String(value);
    }
    if (Array.isArray(value)) return "[" + value.map(item => canonicalJson(item, null)).join(",") + "]";
    if (typeof value === "object") {
      return "{" + Object.keys(value).sort().map(key => JSON.stringify(key) + ":" + canonicalJson(value[key], key)).join(",") + "}";
    }
    fail("unsupported value in canonical JSON");
  }

  async function sha256Hex(value) {
    const bytes = new TextEncoder().encode(value);
    if (globalThis.crypto && globalThis.crypto.subtle) {
      const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
      return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
    }
    if (typeof require === "function") {
      return require("node:crypto").createHash("sha256").update(bytes).digest("hex");
    }
    fail("SHA-256 is unavailable; use a secure browser context");
  }

  function drift(previousSource, currentSource, previousReference, currentReference) {
    const sourceSeconds = (currentSource - previousSource) / 1000;
    const referenceSeconds = (currentReference - previousReference) / 1000;
    if (sourceSeconds <= 0 || referenceSeconds <= 0) {
      fail("source and reference anchor timestamps must be strictly increasing");
    }
    return {
      sourceSeconds: sourceSeconds,
      referenceSeconds: referenceSeconds,
      driftPpm: (referenceSeconds / sourceSeconds - 1) * 1000000
    };
  }

  async function buildClockModel(anchors) {
    if (!Array.isArray(anchors) || anchors.length < 2 || anchors.length > MAX_ANCHORS) {
      fail("anchors must contain 2 to " + MAX_ANCHORS + " records");
    }
    let sessionId = null;
    let sourceId = null;
    const normalized = anchors.map(item => {
      if (!item || typeof item !== "object" || Array.isArray(item)) fail("every anchor must be an object");
      const session = identifier(item.session_id, "session_id");
      const source = identifier(item.source_id, "source_id");
      if (sessionId === null) {
        sessionId = session;
        sourceId = source;
      }
      if (session !== sessionId || source !== sourceId) fail("one clock model may contain only one session and source");
      const sourceTime = parseZonedTimestamp(item.source_timestamp, "source_timestamp");
      const referenceTime = parseZonedTimestamp(item.reference_timestamp, "reference_timestamp");
      const declared = item.uncertainty_seconds !== null && item.uncertainty_seconds !== undefined;
      const uncertainty = declared ? nonnegative(item.uncertainty_seconds, "uncertainty_seconds") : 0;
      const rawId = item.anchor_id;
      const anchorId = rawId === null || rawId === undefined ? null : identifier(rawId, "anchor_id");
      return {
        anchor_id: anchorId,
        source_ms: sourceTime.epochMs,
        reference_ms: referenceTime.epochMs,
        source_timestamp: sourceTime.iso,
        reference_timestamp: referenceTime.iso,
        uncertainty_seconds: uncertainty,
        uncertainty_declared: declared,
        reference_evidence_ref: evidenceRef(item.reference_evidence_ref)
      };
    });
    normalized.sort((a, b) => a.source_ms - b.source_ms);
    for (let index = 1; index < normalized.length; index++) {
      drift(normalized[index - 1].source_ms, normalized[index].source_ms,
        normalized[index - 1].reference_ms, normalized[index].reference_ms);
    }
    normalized.forEach((item, index) => {
      if (item.anchor_id === null) item.anchor_id = "anchor-" + String(index + 1).padStart(4, "0");
    });
    const ids = normalized.map(item => item.anchor_id);
    if (new Set(ids).size !== ids.length) fail("anchor_id values must be unique");

    const serializedAnchors = normalized.map(item => ({
      anchor_id: item.anchor_id,
      source_timestamp: item.source_timestamp,
      reference_timestamp: item.reference_timestamp,
      uncertainty_seconds: item.uncertainty_seconds,
      uncertainty_declared: item.uncertainty_declared,
      reference_evidence_ref: item.reference_evidence_ref
    }));
    const driftIntervals = [];
    for (let index = 1; index < normalized.length; index++) {
      const previous = normalized[index - 1];
      const current = normalized[index];
      const interval = drift(previous.source_ms, current.source_ms, previous.reference_ms, current.reference_ms);
      driftIntervals.push({
        from_anchor_id: previous.anchor_id,
        to_anchor_id: current.anchor_id,
        source_interval_seconds: interval.sourceSeconds,
        reference_interval_seconds: interval.referenceSeconds,
        drift_ppm: interval.driftPpm
      });
    }
    const payload = {
      schema_version: 2,
      session_id: sessionId,
      source_id: sourceId,
      anchors: serializedAnchors,
      anchor_count: serializedAnchors.length,
      anchor_evidence_ref_count: serializedAnchors.filter(item => item.reference_evidence_ref !== null).length,
      all_anchor_uncertainties_declared: serializedAnchors.every(item => item.uncertainty_declared),
      alignment_method: ALIGNMENT_METHOD,
      clock_mapping_assumption: CLOCK_MAPPING_ASSUMPTION,
      drift_intervals: driftIntervals,
      max_absolute_drift_ppm: Math.max.apply(null, driftIntervals.map(item => Math.abs(item.drift_ppm))),
      drift_is_diagnostic_only: true,
      extrapolation_permitted: false,
      uncertainty_method: UNCERTAINTY_METHOD,
      uncertainty_semantics: UNCERTAINTY_SEMANTICS,
      uncertainty_interpretation: UNCERTAINTY_INTERPRETATION,
      uncertainty_is_confidence_interval: false
    };
    return Object.assign({}, payload, { model_sha256: await sha256Hex(canonicalJson(payload, null)) });
  }

  async function verifyClockModel(model) {
    try {
      if (!model || typeof model !== "object" || model.schema_version !== 2 || !Array.isArray(model.anchors)) {
        return { valid: false, tampered_or_incomplete: true, expected_sha256: null, recorded_sha256: model && model.model_sha256 || null };
      }
      const anchors = model.anchors.map(item => ({
        anchor_id: item.anchor_id,
        session_id: model.session_id,
        source_id: model.source_id,
        source_timestamp: item.source_timestamp,
        reference_timestamp: item.reference_timestamp,
        uncertainty_seconds: item.uncertainty_declared ? item.uncertainty_seconds : null,
        reference_evidence_ref: item.reference_evidence_ref
      }));
      const rebuilt = await buildClockModel(anchors);
      const expected = rebuilt.model_sha256;
      const payload = Object.assign({}, model);
      delete payload.model_sha256;
      const expectedPayload = Object.assign({}, rebuilt);
      delete expectedPayload.model_sha256;
      const valid = model.model_sha256 === expected && canonicalJson(payload, null) === canonicalJson(expectedPayload, null);
      return { valid: valid, tampered_or_incomplete: !valid, expected_sha256: expected, recorded_sha256: model.model_sha256 || null };
    } catch (_) {
      return { valid: false, tampered_or_incomplete: true, expected_sha256: null, recorded_sha256: model && model.model_sha256 || null };
    }
  }

  function alignEvents(model, events) {
    if (!Array.isArray(events) || events.length > MAX_EVENTS) fail("events must be a list of at most " + MAX_EVENTS + " records");
    const anchors = model.anchors.map(item => ({
      anchor_id: item.anchor_id,
      source_ms: parseZonedTimestamp(item.source_timestamp, "source_timestamp").epochMs,
      reference_ms: parseZonedTimestamp(item.reference_timestamp, "reference_timestamp").epochMs,
      uncertainty: item.uncertainty_seconds,
      uncertainty_declared: item.uncertainty_declared,
      reference_evidence_ref: item.reference_evidence_ref
    }));
    const reports = [];
    const seen = new Set();
    events.forEach((event, index) => {
      if (!event || typeof event !== "object" || Array.isArray(event)) fail("each event must be an object");
      const eventId = identifier(event.event_id === undefined ? String(index) : event.event_id, "event_id");
      const matches = event.session_id === model.session_id && event.source_id === model.source_id;
      if (!matches) {
        reports.push({ event_id: eventId, status: "different_session_or_source", aligned_at: null, extrapolation_used: false });
        return;
      }
      if (seen.has(eventId)) fail("event_id values must be unique within a session and source");
      seen.add(eventId);
      const instant = parseZonedTimestamp(event.timestamp, "event timestamp").epochMs;
      const eventDeclared = event.uncertainty_seconds !== null && event.uncertainty_seconds !== undefined;
      const eventUncertainty = eventDeclared ? nonnegative(event.uncertainty_seconds, "event uncertainty_seconds") : 0;
      if (instant < anchors[0].source_ms || instant > anchors[anchors.length - 1].source_ms) {
        reports.push({ event_id: eventId, status: "outside_anchor_range", aligned_at: null, extrapolation_used: false });
        return;
      }
      let rightIndex = anchors.findIndex(anchor => anchor.source_ms >= instant);
      if (rightIndex < 0) rightIndex = anchors.length - 1;
      let left = anchors[rightIndex];
      let right = anchors[rightIndex];
      let fraction = 0;
      let intervalSeconds = 0;
      let intervalDrift = null;
      let alignedMs = right.reference_ms;
      let anchorDeclared = right.uncertainty_declared;
      let anchorUncertainty = anchorDeclared ? right.uncertainty : null;
      if (right.source_ms !== instant) {
        left = anchors[rightIndex - 1];
        intervalSeconds = (right.source_ms - left.source_ms) / 1000;
        fraction = (instant - left.source_ms) / (right.source_ms - left.source_ms);
        alignedMs = left.reference_ms + (right.reference_ms - left.reference_ms) * fraction;
        anchorDeclared = left.uncertainty_declared && right.uncertainty_declared;
        anchorUncertainty = anchorDeclared ? left.uncertainty * (1 - fraction) + right.uncertainty * fraction : null;
        intervalDrift = model.drift_intervals[rightIndex - 1].drift_ppm;
      }
      const bracket = left === right ? [left] : [left, right];
      const refs = bracket.map(item => item.reference_evidence_ref).filter(value => value !== null);
      const requiredRefs = left === right ? 1 : 2;
      const uncertaintyComplete = anchorDeclared && eventDeclared;
      reports.push({
        event_id: eventId,
        status: "aligned_within_anchors",
        source_timestamp: pythonIsoFromEpochMs(instant),
        aligned_at: pythonIsoFromEpochMs(Math.round(alignedMs)),
        left_anchor_id: left.anchor_id,
        right_anchor_id: right.anchor_id,
        interpolation_fraction: fraction,
        interpolation_fraction_not_a_probability: true,
        anchor_interval_seconds: intervalSeconds,
        interval_drift_ppm: intervalDrift,
        anchor_reference_evidence_refs: refs,
        anchor_provenance_complete: refs.length === requiredRefs,
        anchor_uncertainty_seconds: anchorUncertainty,
        anchor_uncertainty_declared: anchorDeclared,
        event_uncertainty_seconds: eventDeclared ? eventUncertainty : null,
        event_uncertainty_declared: eventDeclared,
        declared_uncertainty_envelope_seconds: uncertaintyComplete ? anchorUncertainty + eventUncertainty : null,
        declared_uncertainty_inputs_complete: uncertaintyComplete,
        uncertainty_method: UNCERTAINTY_METHOD,
        uncertainty_interpretation: UNCERTAINTY_INTERPRETATION,
        clock_mapping_assumption: CLOCK_MAPPING_ASSUMPTION,
        uncertainty_is_confidence_interval: false,
        extrapolation_used: false
      });
    });
    const aligned = reports.filter(item => item.status === "aligned_within_anchors");
    return {
      events: reports,
      event_count: reports.length,
      aligned_count: aligned.length,
      complete_declared_uncertainty_input_count: aligned.filter(item => item.declared_uncertainty_inputs_complete).length,
      complete_anchor_provenance_count: aligned.filter(item => item.anchor_provenance_complete).length,
      clock_model_sha256: model.model_sha256,
      alignment_method: ALIGNMENT_METHOD,
      clock_mapping_assumption: CLOCK_MAPPING_ASSUMPTION,
      drift_is_diagnostic_only: true,
      extrapolation_permitted: false,
      session_isolation_preserved: true,
      unrecorded_history_recovered: false,
      event_identity_established: false,
      future_prediction_performed: false
    };
  }

  const COPY = {
    en: {
      drift: "Maximum absolute interval drift: {value} ppm (diagnostic only).",
      previewLimit: "The table previews at most 100 rows; the JSON export contains every processed observation.",
      title: "Local clock calibration",
      intro: "Create a derived timeline for one selected recording session by pairing recorded observations with independently known reference times. The original observations are never changed.",
      anchor: "Anchor",
      observation: "Recorded observation",
      reference: "Reference timestamp (ISO 8601 with Z or ±HH:MM)",
      uncertainty: "Anchor absolute uncertainty bound (seconds, optional)",
      evidence: "Reference evidence ID (optional)",
      evidenceHelp: "This is a user-supplied identifier, not evidence verification.",
      add: "Add anchor",
      remove: "Remove anchor",
      eventBound: "Event timestamp absolute bound in seconds (optional; applied uniformly to this session)",
      eventBoundHelp: "Leave blank when unknown. A declared value is an absolute bound, not a standard deviation or confidence interval.",
      build: "Build aligned preview",
      export: "Export derived JSON",
      refresh: "Refresh observations",
      noSession: "Select one recording session in the timeline above.",
      legacy: "This legacy group has no stable capture-session clock identifier. Alignment is disabled to avoid combining unrelated recordings.",
      loading: "Reading local observations…",
      noEvents: "No observations are available in this session.",
      tooMany: "This session exceeds the 5,000-observation processing limit. No data was truncated or modified.",
      ready: "Session loaded. Choose at least two distinct observations and enter timezone-aware reference timestamps.",
      needsTwo: "At least two anchors are required.",
      invalid: "Check the anchor selections, ISO timestamps, uncertainty bounds and evidence references.",
      resultEmpty: "No derived alignment has been generated.",
      resultSummary: "Aligned {aligned} of {total} observations; {outside} are outside the anchor range and were not extrapolated.",
      aligned: "Aligned within anchors",
      outside: "Outside anchor range",
      other: "Different session or source",
      tableObservation: "Observation",
      tableSource: "Source time",
      tableAligned: "Derived reference time",
      tableStatus: "Status",
      hash: "Model SHA-256",
      provenance: "Complete anchor evidence references: {count}",
      uncertaintyComplete: "Observations with complete declared uncertainty inputs: {count}",
      uncertaintyMissing: "Numerical uncertainty envelopes are withheld where any required bound is undeclared.",
      limitation: "Piecewise-linear interpolation is an explicit modelling assumption. Drift is diagnostic only. The browser rounds derived timestamps to 1 ms; this is not a clock-accuracy guarantee.",
      localNote: "Local-only preview. The workspace reads IndexedDB in read-only mode, includes no media, makes no network request for alignment, and never writes to the original observations.",
      exported: "Derived alignment JSON exported.",
      stale: "Inputs changed. Build a new preview before exporting.",
      maxAnchors: "The interface supports at most 20 anchors per preview.",
      noCrypto: "SHA-256 requires a secure browser context.",
      anchorHelp: "Choose distinct observations in increasing source-time order. Reference times must also increase strictly.",
      unsupported: "This browser cannot open the local observation database."
    },
    fr: {
      drift: "Dérive absolue maximale entre intervalles : {value} ppm (diagnostic uniquement).",
      previewLimit: "Le tableau affiche au maximum 100 lignes ; l’export JSON contient toutes les observations traitées.",
      title: "Calibration locale des horloges",
      intro: "Créez une chronologie dérivée pour une seule session en associant des observations enregistrées à des heures de référence connues indépendamment. Les observations originales ne sont jamais modifiées.",
      anchor: "Ancre",
      observation: "Observation enregistrée",
      reference: "Horodatage de référence (ISO 8601 avec Z ou ±HH:MM)",
      uncertainty: "Borne absolue d’incertitude de l’ancre (secondes, facultatif)",
      evidence: "Identifiant de la preuve de référence (facultatif)",
      evidenceHelp: "Il s’agit d’un identifiant fourni par l’utilisateur, pas d’une vérification de la preuve.",
      add: "Ajouter une ancre",
      remove: "Supprimer l’ancre",
      eventBound: "Borne absolue d’incertitude des événements (secondes, facultatif ; appliquée uniformément à la session)",
      eventBoundHelp: "Laissez vide si elle est inconnue. Une valeur déclarée est une borne absolue, pas un écart-type ni un intervalle de confiance.",
      build: "Calculer l’aperçu aligné",
      export: "Exporter le JSON dérivé",
      refresh: "Actualiser les observations",
      noSession: "Sélectionnez une session d’enregistrement dans la chronologie ci-dessus.",
      legacy: "Ce groupe historique ne possède pas d’identifiant stable d’horloge de session. L’alignement est désactivé pour éviter de mélanger des enregistrements distincts.",
      loading: "Lecture des observations locales…",
      noEvents: "Aucune observation n’est disponible dans cette session.",
      tooMany: "Cette session dépasse la limite de 5 000 observations. Aucune donnée n’a été tronquée ni modifiée.",
      ready: "Session chargée. Choisissez au moins deux observations distinctes et saisissez des heures de référence avec fuseau.",
      needsTwo: "Au moins deux ancres sont nécessaires.",
      invalid: "Vérifiez les observations choisies, les dates ISO, les bornes d’incertitude et les références de preuve.",
      resultEmpty: "Aucun alignement dérivé n’a été calculé.",
      resultSummary: "{aligned} observations alignées sur {total} ; {outside} sont hors de la plage des ancres et ne sont pas extrapolées.",
      aligned: "Aligné entre les ancres",
      outside: "Hors de la plage des ancres",
      other: "Session ou source différente",
      tableObservation: "Observation",
      tableSource: "Heure source",
      tableAligned: "Heure de référence dérivée",
      tableStatus: "Statut",
      hash: "SHA-256 du modèle",
      provenance: "Références de preuve d’ancrage complètes : {count}",
      uncertaintyComplete: "Observations avec toutes les bornes d’incertitude déclarées : {count}",
      uncertaintyMissing: "Les enveloppes numériques d’incertitude sont omises lorsqu’une borne requise n’est pas déclarée.",
      limitation: "L’interpolation linéaire par morceaux est une hypothèse explicite. La dérive est uniquement diagnostique. Le navigateur arrondit les heures dérivées à 1 ms ; cela ne garantit pas l’exactitude d’une horloge.",
      localNote: "Aperçu local uniquement. Le module lit IndexedDB en lecture seule, n’inclut aucun média, n’effectue aucune requête réseau pour l’alignement et n’écrit jamais dans les observations originales.",
      exported: "Fichier JSON d’alignement dérivé exporté.",
      stale: "Les paramètres ont changé. Recalculez l’aperçu avant l’exportation.",
      maxAnchors: "L’interface accepte au maximum 20 ancres par aperçu.",
      noCrypto: "SHA-256 nécessite un contexte de navigateur sécurisé.",
      anchorHelp: "Choisissez des observations distinctes dans l’ordre croissant de l’heure source. Les heures de référence doivent aussi être strictement croissantes.",
      unsupported: "Ce navigateur ne peut pas ouvrir la base d’observations locales."
    },
    es: {
      drift: "Deriva absoluta máxima entre intervalos: {value} ppm (solo diagnóstico).",
      previewLimit: "La tabla muestra como máximo 100 filas; el JSON exportado contiene todas las observaciones procesadas.",
      title: "Calibración local de relojes",
      intro: "Cree una cronología derivada para una sola sesión emparejando observaciones grabadas con horas de referencia conocidas de forma independiente. Las observaciones originales nunca se modifican.",
      anchor: "Ancla",
      observation: "Observación grabada",
      reference: "Marca de tiempo de referencia (ISO 8601 con Z o ±HH:MM)",
      uncertainty: "Límite absoluto de incertidumbre del ancla (segundos, opcional)",
      evidence: "ID de evidencia de referencia (opcional)",
      evidenceHelp: "Es un identificador proporcionado por el usuario, no una verificación de evidencia.",
      add: "Añadir ancla",
      remove: "Eliminar ancla",
      eventBound: "Límite absoluto de incertidumbre del evento en segundos (opcional; se aplica a toda la sesión)",
      eventBoundHelp: "Déjelo vacío si se desconoce. Es un límite absoluto, no una desviación estándar ni un intervalo de confianza.",
      build: "Crear vista previa alineada",
      export: "Exportar JSON derivado",
      refresh: "Actualizar observaciones",
      noSession: "Seleccione una sesión de grabación en la cronología superior.",
      legacy: "Este grupo antiguo no tiene un identificador estable de reloj de sesión. La alineación está desactivada para evitar mezclar grabaciones distintas.",
      loading: "Leyendo observaciones locales…",
      noEvents: "No hay observaciones disponibles en esta sesión.",
      tooMany: "La sesión supera el límite de 5.000 observaciones. No se truncó ni modificó ningún dato.",
      ready: "Sesión cargada. Elija al menos dos observaciones distintas e introduzca horas de referencia con zona horaria.",
      needsTwo: "Se necesitan al menos dos anclas.",
      invalid: "Compruebe las observaciones, las fechas ISO, los límites de incertidumbre y las referencias.",
      resultEmpty: "No se ha generado ninguna alineación derivada.",
      resultSummary: "{aligned} de {total} observaciones alineadas; {outside} quedan fuera del intervalo de anclas y no se extrapolan.",
      aligned: "Alineada dentro de las anclas",
      outside: "Fuera del intervalo de anclas",
      other: "Sesión o fuente diferente",
      tableObservation: "Observación",
      tableSource: "Hora de origen",
      tableAligned: "Hora de referencia derivada",
      tableStatus: "Estado",
      hash: "SHA-256 del modelo",
      provenance: "Referencias de evidencia completas: {count}",
      uncertaintyComplete: "Observaciones con límites de incertidumbre declarados completos: {count}",
      uncertaintyMissing: "Se omiten las envolventes numéricas cuando falta algún límite requerido.",
      limitation: "La interpolación lineal por tramos es una hipótesis explícita. La deriva es solo diagnóstica. El navegador redondea las horas derivadas a 1 ms; esto no garantiza la exactitud del reloj.",
      localNote: "Vista previa solo local. IndexedDB se lee en modo de solo lectura; no se incluyen medios, no hay solicitudes de red para alinear y las observaciones originales nunca se escriben.",
      exported: "JSON de alineación derivada exportado.",
      stale: "Los parámetros han cambiado. Genere una nueva vista previa antes de exportar.",
      maxAnchors: "La interfaz admite un máximo de 20 anclas por vista previa.",
      noCrypto: "SHA-256 requiere un contexto de navegador seguro.",
      anchorHelp: "Elija observaciones distintas en orden creciente de hora de origen. Las horas de referencia también deben aumentar estrictamente.",
      unsupported: "Este navegador no puede abrir la base de observaciones locales."
    },
    de: {
      drift: "Maximale absolute Intervallabweichung: {value} ppm (nur Diagnose).",
      previewLimit: "Die Tabelle zeigt höchstens 100 Zeilen; der JSON-Export enthält alle verarbeiteten Beobachtungen.",
      title: "Lokale Uhrkalibrierung",
      intro: "Erstellen Sie eine abgeleitete Zeitachse für eine Aufnahmesitzung, indem Sie aufgezeichnete Beobachtungen mit unabhängig bekannten Referenzzeiten verknüpfen. Originalbeobachtungen werden nie geändert.",
      anchor: "Anker",
      observation: "Aufgezeichnete Beobachtung",
      reference: "Referenzzeitstempel (ISO 8601 mit Z oder ±HH:MM)",
      uncertainty: "Absolute Unsicherheitsgrenze des Ankers (Sekunden, optional)",
      evidence: "Referenznachweis-ID (optional)",
      evidenceHelp: "Dies ist eine vom Nutzer angegebene Kennung, keine Prüfung des Nachweises.",
      add: "Anker hinzufügen",
      remove: "Anker entfernen",
      eventBound: "Absolute Unsicherheitsgrenze des Ereigniszeitstempels in Sekunden (optional; einheitlich für diese Sitzung)",
      eventBoundHelp: "Leer lassen, wenn unbekannt. Ein deklarierter Wert ist eine absolute Grenze, keine Standardabweichung oder kein Konfidenzintervall.",
      build: "Abgeleitete Vorschau erstellen",
      export: "Abgeleitetes JSON exportieren",
      refresh: "Beobachtungen aktualisieren",
      noSession: "Wählen Sie oben in der Zeitachse eine Aufnahmesitzung aus.",
      legacy: "Diese ältere Gruppe besitzt keine stabile Sitzungsuhrkennung. Die Ausrichtung ist deaktiviert, damit getrennte Aufnahmen nicht vermischt werden.",
      loading: "Lokale Beobachtungen werden gelesen…",
      noEvents: "In dieser Sitzung sind keine Beobachtungen verfügbar.",
      tooMany: "Diese Sitzung überschreitet das Limit von 5.000 Beobachtungen. Es wurden keine Daten gekürzt oder geändert.",
      ready: "Sitzung geladen. Wählen Sie mindestens zwei verschiedene Beobachtungen und geben Sie Referenzzeiten mit Zeitzone ein.",
      needsTwo: "Mindestens zwei Anker sind erforderlich.",
      invalid: "Prüfen Sie Beobachtungsauswahl, ISO-Zeitstempel, Unsicherheitsgrenzen und Nachweisreferenzen.",
      resultEmpty: "Es wurde keine abgeleitete Ausrichtung erstellt.",
      resultSummary: "{aligned} von {total} Beobachtungen ausgerichtet; {outside} liegen außerhalb des Ankerbereichs und werden nicht extrapoliert.",
      aligned: "Innerhalb der Anker ausgerichtet",
      outside: "Außerhalb des Ankerbereichs",
      other: "Andere Sitzung oder Quelle",
      tableObservation: "Beobachtung",
      tableSource: "Quellzeit",
      tableAligned: "Abgeleitete Referenzzeit",
      tableStatus: "Status",
      hash: "Modell-SHA-256",
      provenance: "Vollständige Ankernachweise: {count}",
      uncertaintyComplete: "Beobachtungen mit vollständig deklarierten Unsicherheitsgrenzen: {count}",
      uncertaintyMissing: "Numerische Unsicherheitshüllen werden ausgelassen, wenn eine erforderliche Grenze fehlt.",
      limitation: "Stückweise lineare Interpolation ist eine ausdrückliche Modellannahme. Drift dient nur der Diagnose. Der Browser rundet abgeleitete Zeitstempel auf 1 ms; dies garantiert keine Uhrgenauigkeit.",
      localNote: "Nur lokale Vorschau. IndexedDB wird schreibgeschützt gelesen, Medien werden nicht einbezogen, die Ausrichtung benötigt keine Netzwerkanfrage und Originalbeobachtungen werden nie geschrieben.",
      exported: "Abgeleitete Ausrichtungs-JSON exportiert.",
      stale: "Eingaben geändert. Erstellen Sie vor dem Export eine neue Vorschau.",
      maxAnchors: "Die Oberfläche unterstützt höchstens 20 Anker pro Vorschau.",
      noCrypto: "SHA-256 benötigt einen sicheren Browserkontext.",
      anchorHelp: "Wählen Sie verschiedene Beobachtungen in streng steigender Quellzeit. Referenzzeiten müssen ebenfalls streng steigen.",
      unsupported: "Dieser Browser kann die lokale Beobachtungsdatenbank nicht öffnen."
    },
    it: {
      drift: "Deriva assoluta massima tra intervalli: {value} ppm (solo diagnostica).",
      previewLimit: "La tabella mostra al massimo 100 righe; l’esportazione JSON contiene tutte le osservazioni elaborate.",
      title: "Calibrazione locale degli orologi",
      intro: "Crea una cronologia derivata per una sola sessione associando osservazioni registrate a orari di riferimento noti indipendentemente. Le osservazioni originali non vengono mai modificate.",
      anchor: "Ancora",
      observation: "Osservazione registrata",
      reference: "Timestamp di riferimento (ISO 8601 con Z o ±HH:MM)",
      uncertainty: "Limite assoluto di incertezza dell’ancora (secondi, facoltativo)",
      evidence: "ID della prova di riferimento (facoltativo)",
      evidenceHelp: "È un identificatore fornito dall’utente, non una verifica della prova.",
      add: "Aggiungi ancora",
      remove: "Rimuovi ancora",
      eventBound: "Limite assoluto di incertezza del timestamp dell’evento in secondi (facoltativo; uniforme per la sessione)",
      eventBoundHelp: "Lascia vuoto se sconosciuto. È un limite assoluto, non una deviazione standard o un intervallo di confidenza.",
      build: "Crea anteprima allineata",
      export: "Esporta JSON derivato",
      refresh: "Aggiorna osservazioni",
      noSession: "Seleziona una sessione di registrazione nella cronologia sopra.",
      legacy: "Questo gruppo precedente non ha un identificatore stabile dell’orologio di sessione. L’allineamento è disattivato per evitare di unire registrazioni distinte.",
      loading: "Lettura delle osservazioni locali…",
      noEvents: "Nessuna osservazione disponibile in questa sessione.",
      tooMany: "La sessione supera il limite di 5.000 osservazioni. Nessun dato è stato troncato o modificato.",
      ready: "Sessione caricata. Scegli almeno due osservazioni distinte e inserisci orari di riferimento con fuso orario.",
      needsTwo: "Sono necessarie almeno due ancore.",
      invalid: "Controlla le osservazioni, i timestamp ISO, i limiti di incertezza e i riferimenti delle prove.",
      resultEmpty: "Nessun allineamento derivato è stato generato.",
      resultSummary: "{aligned} di {total} osservazioni allineate; {outside} fuori dall’intervallo delle ancore e senza estrapolazione.",
      aligned: "Allineata entro le ancore",
      outside: "Fuori dall’intervallo delle ancore",
      other: "Sessione o sorgente diversa",
      tableObservation: "Osservazione",
      tableSource: "Ora sorgente",
      tableAligned: "Ora di riferimento derivata",
      tableStatus: "Stato",
      hash: "SHA-256 del modello",
      provenance: "Riferimenti completi delle prove delle ancore: {count}",
      uncertaintyComplete: "Osservazioni con tutti i limiti di incertezza dichiarati: {count}",
      uncertaintyMissing: "Gli inviluppi numerici sono omessi quando manca un limite richiesto.",
      limitation: "L’interpolazione lineare a tratti è un’ipotesi esplicita. La deriva è solo diagnostica. Il browser arrotonda i timestamp derivati a 1 ms; ciò non garantisce l’accuratezza dell’orologio.",
      localNote: "Anteprima solo locale. IndexedDB è letto in sola lettura, i media sono esclusi, l’allineamento non richiede rete e le osservazioni originali non vengono mai scritte.",
      exported: "JSON di allineamento derivato esportato.",
      stale: "Gli input sono cambiati. Crea una nuova anteprima prima di esportare.",
      maxAnchors: "L’interfaccia supporta al massimo 20 ancore per anteprima.",
      noCrypto: "SHA-256 richiede un contesto browser sicuro.",
      anchorHelp: "Scegli osservazioni distinte in ordine crescente di ora sorgente. Anche gli orari di riferimento devono crescere rigorosamente.",
      unsupported: "Questo browser non può aprire il database locale delle osservazioni."
    },
    pt: {
      drift: "Deriva absoluta máxima entre intervalos: {value} ppm (apenas diagnóstico).",
      previewLimit: "A tabela mostra no máximo 100 linhas; o JSON exportado contém todas as observações processadas.",
      title: "Calibração local de relógios",
      intro: "Crie uma linha temporal derivada para uma única sessão associando observações gravadas a horas de referência conhecidas independentemente. As observações originais nunca são alteradas.",
      anchor: "Âncora",
      observation: "Observação gravada",
      reference: "Carimbo de referência (ISO 8601 com Z ou ±HH:MM)",
      uncertainty: "Limite absoluto de incerteza da âncora (segundos, opcional)",
      evidence: "ID da evidência de referência (opcional)",
      evidenceHelp: "É um identificador fornecido pelo utilizador, não uma verificação da evidência.",
      add: "Adicionar âncora",
      remove: "Remover âncora",
      eventBound: "Limite absoluto de incerteza do evento em segundos (opcional; aplicado uniformemente à sessão)",
      eventBoundHelp: "Deixe em branco se desconhecido. É um limite absoluto, não um desvio-padrão nem um intervalo de confiança.",
      build: "Criar pré-visualização alinhada",
      export: "Exportar JSON derivado",
      refresh: "Atualizar observações",
      noSession: "Selecione uma sessão de gravação na linha temporal acima.",
      legacy: "Este grupo antigo não tem um identificador estável do relógio da sessão. O alinhamento está desativado para evitar misturar gravações distintas.",
      loading: "A ler observações locais…",
      noEvents: "Não existem observações nesta sessão.",
      tooMany: "A sessão excede o limite de 5.000 observações. Nenhum dado foi truncado ou alterado.",
      ready: "Sessão carregada. Escolha pelo menos duas observações distintas e introduza horas de referência com fuso horário.",
      needsTwo: "São necessárias pelo menos duas âncoras.",
      invalid: "Verifique as observações, os carimbos ISO, os limites de incerteza e as referências de evidência.",
      resultEmpty: "Não foi criado nenhum alinhamento derivado.",
      resultSummary: "{aligned} de {total} observações alinhadas; {outside} estão fora do intervalo das âncoras e não são extrapoladas.",
      aligned: "Alinhada dentro das âncoras",
      outside: "Fora do intervalo das âncoras",
      other: "Sessão ou origem diferente",
      tableObservation: "Observação",
      tableSource: "Hora de origem",
      tableAligned: "Hora de referência derivada",
      tableStatus: "Estado",
      hash: "SHA-256 do modelo",
      provenance: "Referências de evidência completas: {count}",
      uncertaintyComplete: "Observações com limites de incerteza declarados completos: {count}",
      uncertaintyMissing: "Os envelopes numéricos são omitidos quando falta algum limite necessário.",
      limitation: "A interpolação linear por partes é uma hipótese explícita. A deriva é apenas diagnóstica. O navegador arredonda os tempos derivados a 1 ms; isso não garante a exatidão do relógio.",
      localNote: "Pré-visualização apenas local. IndexedDB é lido em modo só de leitura, os média são excluídos, o alinhamento não usa a rede e as observações originais nunca são escritas.",
      exported: "JSON de alinhamento derivado exportado.",
      stale: "Os dados mudaram. Crie uma nova pré-visualização antes de exportar.",
      maxAnchors: "A interface suporta no máximo 20 âncoras por pré-visualização.",
      noCrypto: "SHA-256 requer um contexto de navegador seguro.",
      anchorHelp: "Escolha observações distintas por ordem crescente da hora de origem. As horas de referência também devem aumentar estritamente.",
      unsupported: "Este navegador não consegue abrir a base de observações local."
    },
    nl: {
      drift: "Maximale absolute intervaldrift: {value} ppm (alleen diagnostisch).",
      previewLimit: "De tabel toont maximaal 100 rijen; de JSON-export bevat alle verwerkte waarnemingen.",
      title: "Lokale klokkalibratie",
      intro: "Maak een afgeleide tijdlijn voor één opnamesessie door opgenomen waarnemingen te koppelen aan onafhankelijk bekende referentietijden. Oorspronkelijke waarnemingen worden nooit gewijzigd.",
      anchor: "Anker",
      observation: "Opgenomen waarneming",
      reference: "Referentietijdstempel (ISO 8601 met Z of ±HH:MM)",
      uncertainty: "Absolute onzekerheidsgrens van anker (seconden, optioneel)",
      evidence: "Referentiebewijs-ID (optioneel)",
      evidenceHelp: "Dit is een door de gebruiker opgegeven identificatie, geen verificatie van bewijs.",
      add: "Anker toevoegen",
      remove: "Anker verwijderen",
      eventBound: "Absolute onzekerheidsgrens van gebeurtenistijd in seconden (optioneel; uniform voor deze sessie)",
      eventBoundHelp: "Laat leeg als onbekend. Een opgegeven waarde is een absolute grens, geen standaardafwijking of betrouwbaarheidsinterval.",
      build: "Uitgelijnde preview maken",
      export: "Afgeleide JSON exporteren",
      refresh: "Waarnemingen vernieuwen",
      noSession: "Selecteer hierboven een opnamesessie in de tijdlijn.",
      legacy: "Deze oude groep heeft geen stabiele sessieklok-ID. Uitlijning is uitgeschakeld om verschillende opnamen niet te mengen.",
      loading: "Lokale waarnemingen lezen…",
      noEvents: "Geen waarnemingen beschikbaar in deze sessie.",
      tooMany: "Deze sessie overschrijdt de limiet van 5.000 waarnemingen. Er zijn geen gegevens afgekapt of gewijzigd.",
      ready: "Sessie geladen. Kies minstens twee verschillende waarnemingen en voer referentietijden met tijdzone in.",
      needsTwo: "Er zijn minstens twee ankers nodig.",
      invalid: "Controleer waarnemingen, ISO-tijdstempels, onzekerheidsgrenzen en bewijsverwijzingen.",
      resultEmpty: "Er is geen afgeleide uitlijning gemaakt.",
      resultSummary: "{aligned} van {total} waarnemingen uitgelijnd; {outside} buiten het ankerbereik en niet geëxtrapoleerd.",
      aligned: "Uitgelijnd binnen ankers",
      outside: "Buiten ankerbereik",
      other: "Andere sessie of bron",
      tableObservation: "Waarneming",
      tableSource: "Brontijd",
      tableAligned: "Afgeleide referentietijd",
      tableStatus: "Status",
      hash: "Model-SHA-256",
      provenance: "Volledige ankerbewijsverwijzingen: {count}",
      uncertaintyComplete: "Waarnemingen met volledig opgegeven onzekerheidsgrenzen: {count}",
      uncertaintyMissing: "Numerieke onzekerheidsenveloppen worden weggelaten als een vereiste grens ontbreekt.",
      limitation: "Stuksgewijze lineaire interpolatie is een expliciete modelaanname. Drift is alleen diagnostisch. De browser rondt afgeleide tijden af op 1 ms; dit garandeert geen kloknauwkeurigheid.",
      localNote: "Alleen lokale preview. IndexedDB wordt alleen gelezen, media worden niet opgenomen, uitlijning gebruikt geen netwerk en oorspronkelijke waarnemingen worden nooit geschreven.",
      exported: "Afgeleide uitlijnings-JSON geëxporteerd.",
      stale: "Invoer gewijzigd. Maak vóór export een nieuwe preview.",
      maxAnchors: "De interface ondersteunt maximaal 20 ankers per preview.",
      noCrypto: "SHA-256 vereist een veilige browsercontext.",
      anchorHelp: "Kies verschillende waarnemingen in strikt oplopende brontijd. Referentietijden moeten ook strikt oplopen.",
      unsupported: "Deze browser kan de lokale waarnemingsdatabase niet openen."
    },
    ru: {
      drift: "Максимальный абсолютный дрейф интервала: {value} ppm (только диагностика).",
      previewLimit: "В таблице отображается не более 100 строк; экспорт JSON содержит все обработанные наблюдения.",
      title: "Локальная калибровка часов",
      intro: "Создайте производную временную шкалу для одного сеанса записи, сопоставив записанные наблюдения с независимо известными опорными моментами времени. Исходные наблюдения не изменяются.",
      anchor: "Опорная точка",
      observation: "Записанное наблюдение",
      reference: "Опорная метка времени (ISO 8601 с Z или ±HH:MM)",
      uncertainty: "Абсолютная граница неопределённости опорной точки (секунды, необязательно)",
      evidence: "Идентификатор опорного свидетельства (необязательно)",
      evidenceHelp: "Это идентификатор, заданный пользователем, а не проверка свидетельства.",
      add: "Добавить точку",
      remove: "Удалить точку",
      eventBound: "Абсолютная граница неопределённости времени события в секундах (необязательно; едина для сеанса)",
      eventBoundHelp: "Оставьте пустым, если значение неизвестно. Это абсолютная граница, а не стандартное отклонение или доверительный интервал.",
      build: "Создать выровненный просмотр",
      export: "Экспортировать производный JSON",
      refresh: "Обновить наблюдения",
      noSession: "Выберите сеанс записи на временной шкале выше.",
      legacy: "У этой старой группы нет стабильного идентификатора часов сеанса. Выравнивание отключено, чтобы не смешивать разные записи.",
      loading: "Чтение локальных наблюдений…",
      noEvents: "В этом сеансе нет доступных наблюдений.",
      tooMany: "Сеанс превышает лимит в 5 000 наблюдений. Данные не обрезались и не изменялись.",
      ready: "Сеанс загружен. Выберите не менее двух разных наблюдений и введите опорное время с часовым поясом.",
      needsTwo: "Требуются как минимум две опорные точки.",
      invalid: "Проверьте выбранные наблюдения, метки ISO, границы неопределённости и ссылки на свидетельства.",
      resultEmpty: "Производное выравнивание ещё не создано.",
      resultSummary: "Выровнено {aligned} из {total} наблюдений; {outside} вне диапазона опорных точек и не экстраполируются.",
      aligned: "Выровнено внутри опорных точек",
      outside: "Вне диапазона опорных точек",
      other: "Другой сеанс или источник",
      tableObservation: "Наблюдение",
      tableSource: "Исходное время",
      tableAligned: "Производное опорное время",
      tableStatus: "Статус",
      hash: "SHA-256 модели",
      provenance: "Полные ссылки на опорные свидетельства: {count}",
      uncertaintyComplete: "Наблюдения с полными заявленными границами неопределённости: {count}",
      uncertaintyMissing: "Численные интервалы неопределённости не показываются, если отсутствует любая необходимая граница.",
      limitation: "Кусочно-линейная интерполяция — явное допущение модели. Дрейф используется только для диагностики. Браузер округляет производное время до 1 мс; это не гарантирует точность часов.",
      localNote: "Только локальный просмотр. IndexedDB читается без записи, медиа не включаются, сетевые запросы для выравнивания не выполняются, исходные наблюдения не изменяются.",
      exported: "Производный JSON выравнивания экспортирован.",
      stale: "Входные данные изменились. Перед экспортом создайте новый просмотр.",
      maxAnchors: "Интерфейс поддерживает не более 20 опорных точек.",
      noCrypto: "Для SHA-256 требуется защищённый контекст браузера.",
      anchorHelp: "Выбирайте разные наблюдения в строго возрастающем порядке исходного времени. Опорное время также должно строго возрастать.",
      unsupported: "Этот браузер не может открыть локальную базу наблюдений."
    },
    uk: {
      drift: "Максимальний абсолютний дрейф інтервалу: {value} ppm (лише діагностика).",
      previewLimit: "У таблиці показано не більше 100 рядків; експорт JSON містить усі оброблені спостереження.",
      title: "Локальне калібрування годинників",
      intro: "Створіть похідну часову шкалу для одного сеансу запису, зіставивши записані спостереження з незалежно відомим опорним часом. Початкові спостереження ніколи не змінюються.",
      anchor: "Опорна точка",
      observation: "Записане спостереження",
      reference: "Опорна часова позначка (ISO 8601 із Z або ±HH:MM)",
      uncertainty: "Абсолютна межа невизначеності опорної точки (секунди, необов’язково)",
      evidence: "Ідентифікатор опорного свідчення (необов’язково)",
      evidenceHelp: "Це ідентифікатор, наданий користувачем, а не перевірка свідчення.",
      add: "Додати точку",
      remove: "Видалити точку",
      eventBound: "Абсолютна межа невизначеності часу події в секундах (необов’язково; однакова для сеансу)",
      eventBoundHelp: "Залиште порожнім, якщо невідомо. Це абсолютна межа, а не стандартне відхилення чи довірчий інтервал.",
      build: "Створити вирівняний перегляд",
      export: "Експортувати похідний JSON",
      refresh: "Оновити спостереження",
      noSession: "Виберіть сеанс запису на часовій шкалі вище.",
      legacy: "Ця стара група не має стабільного ідентифікатора годинника сеансу. Вирівнювання вимкнено, щоб не змішувати різні записи.",
      loading: "Читання локальних спостережень…",
      noEvents: "У цьому сеансі немає доступних спостережень.",
      tooMany: "Сеанс перевищує ліміт у 5 000 спостережень. Дані не обрізано й не змінено.",
      ready: "Сеанс завантажено. Виберіть щонайменше два різні спостереження та введіть опорний час із часовим поясом.",
      needsTwo: "Потрібно щонайменше дві опорні точки.",
      invalid: "Перевірте вибрані спостереження, позначки ISO, межі невизначеності та посилання на свідчення.",
      resultEmpty: "Похідне вирівнювання ще не створено.",
      resultSummary: "Вирівняно {aligned} із {total} спостережень; {outside} поза діапазоном опорних точок і не екстраполюються.",
      aligned: "Вирівняно в межах опорних точок",
      outside: "Поза діапазоном опорних точок",
      other: "Інший сеанс або джерело",
      tableObservation: "Спостереження",
      tableSource: "Вихідний час",
      tableAligned: "Похідний опорний час",
      tableStatus: "Статус",
      hash: "SHA-256 моделі",
      provenance: "Повні посилання на опорні свідчення: {count}",
      uncertaintyComplete: "Спостереження з повними заявленими межами невизначеності: {count}",
      uncertaintyMissing: "Числові межі невизначеності не показуються, якщо бракує будь-якої потрібної межі.",
      limitation: "Кусково-лінійна інтерполяція є явним припущенням моделі. Дрейф використовується лише для діагностики. Браузер округлює похідний час до 1 мс; це не гарантує точності годинника.",
      localNote: "Лише локальний перегляд. IndexedDB читається без запису, медіа не включаються, мережеві запити для вирівнювання не виконуються, початкові спостереження не змінюються.",
      exported: "Похідний JSON вирівнювання експортовано.",
      stale: "Вхідні дані змінилися. Створіть новий перегляд перед експортом.",
      maxAnchors: "Інтерфейс підтримує не більше 20 опорних точок.",
      noCrypto: "Для SHA-256 потрібен захищений контекст браузера.",
      anchorHelp: "Вибирайте різні спостереження у строго зростаючому порядку вихідного часу. Опорний час також має строго зростати.",
      unsupported: "Цей браузер не може відкрити локальну базу спостережень."
    },
    ar: {
      drift: "أقصى انجراف مطلق للفاصل: {value} جزء في المليون (للتشخيص فقط).",
      previewLimit: "يعرض الجدول 100 صف كحد أقصى؛ ويحتوي ملف JSON المُصدّر على جميع الملاحظات المعالجة.",
      title: "معايرة الساعة محليًا",
      intro: "أنشئ خطًا زمنيًا مشتقًا لجلسة تسجيل واحدة بربط الملاحظات المسجلة بأوقات مرجعية معروفة بشكل مستقل. لا تتغير الملاحظات الأصلية مطلقًا.",
      anchor: "مرساة",
      observation: "ملاحظة مسجلة",
      reference: "الطابع الزمني المرجعي (ISO 8601 مع Z أو ±HH:MM)",
      uncertainty: "الحد المطلق لعدم يقين المرساة (بالثواني، اختياري)",
      evidence: "معرّف دليل المرجع (اختياري)",
      evidenceHelp: "هذا معرّف يقدمه المستخدم وليس تحققًا من الدليل.",
      add: "إضافة مرساة",
      remove: "إزالة المرساة",
      eventBound: "الحد المطلق لعدم يقين وقت الحدث بالثواني (اختياري؛ يطبق بالتساوي على الجلسة)",
      eventBoundHelp: "اتركه فارغًا إذا كان غير معروف. القيمة المعلنة حد مطلق وليست انحرافًا معياريًا أو فترة ثقة.",
      build: "إنشاء معاينة محاذاة",
      export: "تصدير JSON مشتق",
      refresh: "تحديث الملاحظات",
      noSession: "اختر جلسة تسجيل من الخط الزمني أعلاه.",
      legacy: "لا تحتوي هذه المجموعة القديمة على معرّف ثابت لساعة الجلسة. تم تعطيل المحاذاة لتجنب دمج تسجيلات غير مرتبطة.",
      loading: "جارٍ قراءة الملاحظات المحلية…",
      noEvents: "لا توجد ملاحظات متاحة في هذه الجلسة.",
      tooMany: "تتجاوز الجلسة حد 5000 ملاحظة. لم يتم اقتطاع أي بيانات أو تعديلها.",
      ready: "تم تحميل الجلسة. اختر ملاحظتين مختلفتين على الأقل وأدخل أوقاتًا مرجعية تتضمن المنطقة الزمنية.",
      needsTwo: "يلزم وجود مرساتين على الأقل.",
      invalid: "تحقق من الملاحظات المختارة وطوابع ISO وحدود عدم اليقين ومراجع الأدلة.",
      resultEmpty: "لم يتم إنشاء محاذاة مشتقة.",
      resultSummary: "تمت محاذاة {aligned} من {total} ملاحظة؛ {outside} خارج نطاق المراسي ولم يتم استقراؤها.",
      aligned: "محاذاة ضمن المراسي",
      outside: "خارج نطاق المراسي",
      other: "جلسة أو مصدر مختلف",
      tableObservation: "الملاحظة",
      tableSource: "وقت المصدر",
      tableAligned: "الوقت المرجعي المشتق",
      tableStatus: "الحالة",
      hash: "SHA-256 للنموذج",
      provenance: "مراجع أدلة المراسي المكتملة: {count}",
      uncertaintyComplete: "الملاحظات ذات مدخلات عدم اليقين المعلنة بالكامل: {count}",
      uncertaintyMissing: "يتم حجب أغلفة عدم اليقين الرقمية عند عدم التصريح بأي حد مطلوب.",
      limitation: "الاستيفاء الخطي المقطعي افتراض نمذجة صريح. الانجراف تشخيصي فقط. يقرّب المتصفح الأوقات المشتقة إلى 1 مللي ثانية؛ وهذا لا يضمن دقة الساعة.",
      localNote: "معاينة محلية فقط. تتم قراءة IndexedDB فقط، ولا تُضمّن الوسائط، ولا تُرسل طلبات شبكة للمحاذاة، ولا تُكتب الملاحظات الأصلية مطلقًا.",
      exported: "تم تصدير JSON للمحاذاة المشتقة.",
      stale: "تغيرت المدخلات. أنشئ معاينة جديدة قبل التصدير.",
      maxAnchors: "تدعم الواجهة 20 مرساة كحد أقصى لكل معاينة.",
      noCrypto: "يتطلب SHA-256 سياق متصفح آمنًا.",
      anchorHelp: "اختر ملاحظات مختلفة بترتيب زمني مصدري متزايد تمامًا. يجب أن تزداد الأوقات المرجعية أيضًا.",
      unsupported: "لا يمكن لهذا المتصفح فتح قاعدة الملاحظات المحلية."
    },
    he: {
      drift: "הסחיפה המוחלטת המרבית במרווח: {value} ppm (לאבחון בלבד).",
      previewLimit: "הטבלה מציגה עד 100 שורות; ייצוא JSON כולל את כל התצפיות שעובדו.",
      title: "כיול שעון מקומי",
      intro: "יצירת ציר זמן נגזר עבור הפעלת הקלטה אחת באמצעות התאמת תצפיות מוקלטות לזמני ייחוס הידועים ממקור עצמאי. התצפיות המקוריות אינן משתנות.",
      anchor: "עוגן",
      observation: "תצפית מוקלטת",
      reference: "חותמת זמן לייחוס (ISO 8601 עם Z או ±HH:MM)",
      uncertainty: "גבול אי-ודאות מוחלט של העוגן (שניות, אופציונלי)",
      evidence: "מזהה ראיית ייחוס (אופציונלי)",
      evidenceHelp: "זהו מזהה שסופק על ידי המשתמש, לא אימות של הראיה.",
      add: "הוספת עוגן",
      remove: "הסרת עוגן",
      eventBound: "גבול אי-ודאות מוחלט של זמן האירוע בשניות (אופציונלי; חל באופן אחיד על ההפעלה)",
      eventBoundHelp: "השאר ריק אם אינו ידוע. ערך מוצהר הוא גבול מוחלט, לא סטיית תקן או רווח סמך.",
      build: "יצירת תצוגה מקדימה מיושרת",
      export: "ייצוא JSON נגזר",
      refresh: "רענון תצפיות",
      noSession: "בחר הפעלת הקלטה בציר הזמן שלמעלה.",
      legacy: "לקבוצה הישנה הזו אין מזהה שעון הפעלה יציב. היישור מושבת כדי למנוע ערבוב הקלטות נפרדות.",
      loading: "קורא תצפיות מקומיות…",
      noEvents: "אין תצפיות זמינות בהפעלה זו.",
      tooMany: "ההפעלה חורגת מהמגבלה של 5,000 תצפיות. לא נחתכו או שונו נתונים.",
      ready: "ההפעלה נטענה. בחר לפחות שתי תצפיות שונות והזן זמני ייחוס עם אזור זמן.",
      needsTwo: "נדרשים לפחות שני עוגנים.",
      invalid: "בדוק את בחירת התצפיות, חותמות ISO, גבולות אי-הוודאות והפניות לראיות.",
      resultEmpty: "לא נוצר יישור נגזר.",
      resultSummary: "{aligned} מתוך {total} תצפיות יושרו; {outside} מחוץ לטווח העוגנים ולא בוצעה עבורן אקסטרפולציה.",
      aligned: "מיושר בתוך העוגנים",
      outside: "מחוץ לטווח העוגנים",
      other: "הפעלה או מקור שונים",
      tableObservation: "תצפית",
      tableSource: "זמן מקור",
      tableAligned: "זמן ייחוס נגזר",
      tableStatus: "מצב",
      hash: "SHA-256 של המודל",
      provenance: "הפניות מלאות לראיות העוגן: {count}",
      uncertaintyComplete: "תצפיות עם גבולות אי-ודאות מוצהרים מלאים: {count}",
      uncertaintyMissing: "מעטפות אי-ודאות מספריות מוסתרות כאשר גבול נדרש כלשהו לא הוצהר.",
      limitation: "אינטרפולציה ליניארית מקטעית היא הנחת מודל מפורשת. הסחיפה משמשת לאבחון בלבד. הדפדפן מעגל זמנים נגזרים ל-1 מילישנייה; אין בכך הבטחה לדיוק השעון.",
      localNote: "תצוגה מקומית בלבד. IndexedDB נקרא לקריאה בלבד, מדיה אינה נכללת, לא נשלחות בקשות רשת ליישור והתצפיות המקוריות לעולם אינן נכתבות.",
      exported: "קובץ JSON של היישור הנגזר יוצא.",
      stale: "הקלט השתנה. צור תצוגה מקדימה חדשה לפני הייצוא.",
      maxAnchors: "הממשק תומך בעד 20 עוגנים לתצוגה מקדימה.",
      noCrypto: "SHA-256 דורש הקשר דפדפן מאובטח.",
      anchorHelp: "בחר תצפיות שונות בסדר עולה של זמן המקור. זמני הייחוס חייבים לעלות גם הם באופן строго.",
      unsupported: "הדפדפן אינו יכול לפתוח את מסד הנתונים המקומי של התצפיות."
    },
    ja: {
      drift: "区間の最大絶対ドリフト: {value} ppm（診断専用）。",
      previewLimit: "表には最大100行を表示します。JSON エクスポートには処理したすべての観測が含まれます。",
      title: "ローカル時計校正",
      intro: "記録済みの観測と独立して確認された基準時刻を対応付け、1つの記録セッションの派生タイムラインを作成します。元の観測データは変更しません。",
      anchor: "アンカー",
      observation: "記録された観測",
      reference: "基準タイムスタンプ（Z または ±HH:MM を含む ISO 8601）",
      uncertainty: "アンカーの絶対不確かさ上限（秒、任意）",
      evidence: "基準証拠 ID（任意）",
      evidenceHelp: "ユーザーが指定する識別子であり、証拠の検証ではありません。",
      add: "アンカーを追加",
      remove: "アンカーを削除",
      eventBound: "イベント時刻の絶対不確かさ上限（秒、任意。このセッション全体に一律適用）",
      eventBoundHelp: "不明な場合は空欄にします。宣言値は絶対上限であり、標準偏差や信頼区間ではありません。",
      build: "整列プレビューを作成",
      export: "派生 JSON をエクスポート",
      refresh: "観測を更新",
      noSession: "上のタイムラインで記録セッションを選択してください。",
      legacy: "この旧データ群には安定したセッション時計 ID がありません。別々の記録を混合しないよう整列を無効にしました。",
      loading: "ローカル観測を読み込み中…",
      noEvents: "このセッションに利用可能な観測はありません。",
      tooMany: "このセッションは 5,000 件の処理上限を超えています。データの切り捨てや変更は行っていません。",
      ready: "セッションを読み込みました。異なる観測を2件以上選び、タイムゾーン付きの基準時刻を入力してください。",
      needsTwo: "アンカーが2件以上必要です。",
      invalid: "観測の選択、ISO 時刻、不確かさ上限、証拠参照を確認してください。",
      resultEmpty: "派生整列はまだ作成されていません。",
      resultSummary: "{total} 件中 {aligned} 件を整列しました。{outside} 件はアンカー範囲外のため外挿していません。",
      aligned: "アンカー範囲内で整列",
      outside: "アンカー範囲外",
      other: "別のセッションまたはソース",
      tableObservation: "観測",
      tableSource: "ソース時刻",
      tableAligned: "派生基準時刻",
      tableStatus: "状態",
      hash: "モデル SHA-256",
      provenance: "参照証拠 ID が揃ったアンカー: {count}",
      uncertaintyComplete: "不確かさ入力がすべて宣言された観測: {count}",
      uncertaintyMissing: "必要な上限が宣言されていない場合、数値の不確かさ範囲は表示しません。",
      limitation: "区分線形補間は明示的なモデル仮定です。ドリフトは診断専用です。ブラウザーは派生時刻を 1 ms 単位に丸めます。時計精度を保証するものではありません。",
      localNote: "ローカルのみのプレビューです。IndexedDB は読み取り専用で、メディアは含まず、整列のためのネットワーク要求は行わず、元の観測を書き換えません。",
      exported: "派生整列 JSON をエクスポートしました。",
      stale: "入力が変更されました。エクスポート前にプレビューを再作成してください。",
      maxAnchors: "プレビューごとに最大20個のアンカーを使用できます。",
      noCrypto: "SHA-256 にはセキュアなブラウザーコンテキストが必要です。",
      anchorHelp: "ソース時刻が厳密に増加するように異なる観測を選択してください。基準時刻も厳密に増加する必要があります。",
      unsupported: "このブラウザーではローカル観測データベースを開けません。"
    },
    ko: {
      drift: "구간 최대 절대 드리프트: {value} ppm(진단 전용).",
      previewLimit: "표에는 최대 100개 행이 표시되며 JSON 내보내기에는 처리된 모든 관측값이 포함됩니다.",
      title: "로컬 시계 보정",
      intro: "기록된 관측값을 독립적으로 확인된 기준 시각과 연결하여 하나의 기록 세션에 대한 파생 타임라인을 만듭니다. 원본 관측값은 변경하지 않습니다.",
      anchor: "기준점",
      observation: "기록된 관측값",
      reference: "기준 타임스탬프(Z 또는 ±HH:MM이 포함된 ISO 8601)",
      uncertainty: "기준점의 절대 불확실성 한계(초, 선택 사항)",
      evidence: "기준 증거 ID(선택 사항)",
      evidenceHelp: "사용자가 제공한 식별자이며 증거를 검증하지 않습니다.",
      add: "기준점 추가",
      remove: "기준점 제거",
      eventBound: "이벤트 시각의 절대 불확실성 한계(초, 선택 사항; 세션 전체에 동일하게 적용)",
      eventBoundHelp: "알 수 없으면 비워 두세요. 선언된 값은 절대 한계이며 표준편차나 신뢰구간이 아닙니다.",
      build: "정렬 미리보기 생성",
      export: "파생 JSON 내보내기",
      refresh: "관측값 새로고침",
      noSession: "위 타임라인에서 기록 세션을 선택하세요.",
      legacy: "이전 그룹에는 안정적인 세션 시계 ID가 없습니다. 서로 다른 기록이 섞이지 않도록 정렬을 비활성화했습니다.",
      loading: "로컬 관측값을 읽는 중…",
      noEvents: "이 세션에 사용할 수 있는 관측값이 없습니다.",
      tooMany: "세션이 5,000개 관측값 처리 한도를 초과합니다. 데이터를 자르거나 변경하지 않았습니다.",
      ready: "세션을 불러왔습니다. 서로 다른 관측값을 두 개 이상 선택하고 시간대가 포함된 기준 시각을 입력하세요.",
      needsTwo: "기준점이 두 개 이상 필요합니다.",
      invalid: "관측 선택, ISO 타임스탬프, 불확실성 한계 및 증거 참조를 확인하세요.",
      resultEmpty: "파생 정렬 결과가 아직 생성되지 않았습니다.",
      resultSummary: "전체 {total}개 중 {aligned}개를 정렬했습니다. {outside}개는 기준점 범위를 벗어나 외삽하지 않았습니다.",
      aligned: "기준점 범위 내 정렬",
      outside: "기준점 범위 밖",
      other: "다른 세션 또는 소스",
      tableObservation: "관측값",
      tableSource: "원본 시각",
      tableAligned: "파생 기준 시각",
      tableStatus: "상태",
      hash: "모델 SHA-256",
      provenance: "기준 증거 참조가 완전한 기준점: {count}",
      uncertaintyComplete: "불확실성 입력이 모두 선언된 관측값: {count}",
      uncertaintyMissing: "필수 한계가 선언되지 않은 경우 수치 불확실성 범위를 표시하지 않습니다.",
      limitation: "구간별 선형 보간은 명시적인 모델 가정입니다. 드리프트는 진단용입니다. 브라우저는 파생 시각을 1ms 단위로 반올림하며 시계 정확도를 보장하지 않습니다.",
      localNote: "로컬 미리보기 전용입니다. IndexedDB는 읽기 전용으로 접근하고 미디어는 포함하지 않으며 정렬을 위한 네트워크 요청이나 원본 관측값 쓰기는 없습니다.",
      exported: "파생 정렬 JSON을 내보냈습니다.",
      stale: "입력이 변경되었습니다. 내보내기 전에 미리보기를 다시 생성하세요.",
      maxAnchors: "미리보기당 최대 20개의 기준점을 지원합니다.",
      noCrypto: "SHA-256에는 보안 브라우저 컨텍스트가 필요합니다.",
      anchorHelp: "원본 시각이 엄격히 증가하도록 서로 다른 관측값을 선택하세요. 기준 시각도 엄격히 증가해야 합니다.",
      unsupported: "이 브라우저는 로컬 관측 데이터베이스를 열 수 없습니다."
    },
    zh: {
      drift: "区间最大绝对漂移：{value} ppm（仅用于诊断）。",
      previewLimit: "表格最多预览 100 行；JSON 导出包含所有已处理观测。",
      title: "本地时钟校准",
      intro: "将已记录的观测与独立确认的参考时间配对，为单个记录会话创建派生时间线。原始观测不会被修改。",
      anchor: "锚点",
      observation: "已记录的观测",
      reference: "参考时间戳（ISO 8601，含 Z 或 ±HH:MM）",
      uncertainty: "锚点绝对不确定性上限（秒，可选）",
      evidence: "参考证据 ID（可选）",
      evidenceHelp: "这是用户提供的标识符，并不代表证据已通过验证。",
      add: "添加锚点",
      remove: "删除锚点",
      eventBound: "事件时间戳绝对不确定性上限（秒，可选；统一应用于本会话）",
      eventBoundHelp: "未知时请留空。声明值是绝对上限，不是标准差或置信区间。",
      build: "生成对齐预览",
      export: "导出派生 JSON",
      refresh: "刷新观测",
      noSession: "请在上方时间线中选择一个记录会话。",
      legacy: "此旧数据组没有稳定的会话时钟标识。为避免混合不同记录，已禁用对齐。",
      loading: "正在读取本地观测…",
      noEvents: "此会话没有可用观测。",
      tooMany: "此会话超过 5,000 条观测的处理上限。没有截断或修改任何数据。",
      ready: "会话已加载。请选择至少两个不同的观测，并输入带时区的参考时间。",
      needsTwo: "至少需要两个锚点。",
      invalid: "请检查观测选择、ISO 时间戳、不确定性上限和证据引用。",
      resultEmpty: "尚未生成派生对齐结果。",
      resultSummary: "已对齐 {total} 条中的 {aligned} 条观测；{outside} 条位于锚点范围之外，未进行外推。",
      aligned: "位于锚点范围内",
      outside: "超出锚点范围",
      other: "不同会话或来源",
      tableObservation: "观测",
      tableSource: "来源时间",
      tableAligned: "派生参考时间",
      tableStatus: "状态",
      hash: "模型 SHA-256",
      provenance: "锚点证据引用完整数：{count}",
      uncertaintyComplete: "不确定性输入完整声明的观测数：{count}",
      uncertaintyMissing: "缺少任何必要上限时，不显示数值不确定性范围。",
      limitation: "分段线性插值是明确的模型假设。漂移仅用于诊断。浏览器将派生时间四舍五入到 1 毫秒；这不保证时钟准确度。",
      localNote: "仅本地预览。IndexedDB 以只读方式访问，不包含媒体，不为对齐发送网络请求，也不会写入原始观测。",
      exported: "已导出派生对齐 JSON。",
      stale: "输入已更改。导出前请重新生成预览。",
      maxAnchors: "每个预览最多支持 20 个锚点。",
      noCrypto: "SHA-256 需要安全的浏览器上下文。",
      anchorHelp: "请选择来源时间严格递增的不同观测。参考时间也必须严格递增。",
      unsupported: "此浏览器无法打开本地观测数据库。"
    },
    hi: {
      drift: "अंतराल का अधिकतम निरपेक्ष ड्रिफ्ट: {value} ppm (केवल निदान)।",
      previewLimit: "तालिका में अधिकतम 100 पंक्तियाँ दिखाई जाती हैं; JSON निर्यात में सभी संसाधित अवलोकन शामिल हैं।",
      title: "स्थानीय घड़ी अंशांकन",
      intro: "रिकॉर्ड किए गए अवलोकनों को स्वतंत्र रूप से ज्ञात संदर्भ समय से जोड़कर एक रिकॉर्डिंग सत्र के लिए व्युत्पन्न समयरेखा बनाएँ। मूल अवलोकन कभी नहीं बदले जाते।",
      anchor: "एंकर",
      observation: "रिकॉर्ड किया गया अवलोकन",
      reference: "संदर्भ टाइमस्टैम्प (Z या ±HH:MM सहित ISO 8601)",
      uncertainty: "एंकर की निरपेक्ष अनिश्चितता सीमा (सेकंड, वैकल्पिक)",
      evidence: "संदर्भ साक्ष्य ID (वैकल्पिक)",
      evidenceHelp: "यह उपयोगकर्ता द्वारा दिया गया पहचानकर्ता है, साक्ष्य का सत्यापन नहीं।",
      add: "एंकर जोड़ें",
      remove: "एंकर हटाएँ",
      eventBound: "इवेंट समय की निरपेक्ष अनिश्चितता सीमा सेकंड में (वैकल्पिक; पूरे सत्र पर समान रूप से लागू)",
      eventBoundHelp: "अज्ञात होने पर खाली छोड़ें। घोषित मान निरपेक्ष सीमा है, मानक विचलन या विश्वास अंतराल नहीं।",
      build: "संरेखित पूर्वावलोकन बनाएँ",
      export: "व्युत्पन्न JSON निर्यात करें",
      refresh: "अवलोकन रीफ़्रेश करें",
      noSession: "ऊपर की समयरेखा में एक रिकॉर्डिंग सत्र चुनें।",
      legacy: "इस पुराने समूह में स्थिर सत्र-घड़ी पहचानकर्ता नहीं है। अलग रिकॉर्डिंग को मिलाने से बचने के लिए संरेखण अक्षम है।",
      loading: "स्थानीय अवलोकन पढ़े जा रहे हैं…",
      noEvents: "इस सत्र में कोई अवलोकन उपलब्ध नहीं है।",
      tooMany: "यह सत्र 5,000 अवलोकनों की सीमा से अधिक है। कोई डेटा काटा या बदला नहीं गया।",
      ready: "सत्र लोड हो गया। कम-से-कम दो अलग अवलोकन चुनें और समय-क्षेत्र सहित संदर्भ समय दर्ज करें।",
      needsTwo: "कम-से-कम दो एंकर आवश्यक हैं।",
      invalid: "अवलोकन चयन, ISO समय, अनिश्चितता सीमाएँ और साक्ष्य संदर्भ जाँचें।",
      resultEmpty: "कोई व्युत्पन्न संरेखण नहीं बनाया गया है।",
      resultSummary: "{total} में से {aligned} अवलोकन संरेखित; {outside} एंकर सीमा के बाहर हैं और उनका एक्सट्रपलेशन नहीं किया गया।",
      aligned: "एंकर सीमा के भीतर संरेखित",
      outside: "एंकर सीमा के बाहर",
      other: "अलग सत्र या स्रोत",
      tableObservation: "अवलोकन",
      tableSource: "स्रोत समय",
      tableAligned: "व्युत्पन्न संदर्भ समय",
      tableStatus: "स्थिति",
      hash: "मॉडल SHA-256",
      provenance: "पूर्ण एंकर साक्ष्य संदर्भ: {count}",
      uncertaintyComplete: "पूर्ण घोषित अनिश्चितता इनपुट वाले अवलोकन: {count}",
      uncertaintyMissing: "किसी आवश्यक सीमा के अघोषित होने पर संख्यात्मक अनिश्चितता आवरण नहीं दिखाया जाता।",
      limitation: "खंडवार रैखिक इंटरपोलेशन एक स्पष्ट मॉडल धारणा है। ड्रिफ्ट केवल निदान के लिए है। ब्राउज़र व्युत्पन्न समय को 1 ms तक गोल करता है; यह घड़ी की सटीकता की गारंटी नहीं है।",
      localNote: "केवल स्थानीय पूर्वावलोकन। IndexedDB केवल पढ़ा जाता है, मीडिया शामिल नहीं है, संरेखण के लिए नेटवर्क अनुरोध नहीं होता और मूल अवलोकन कभी नहीं लिखे जाते।",
      exported: "व्युत्पन्न संरेखण JSON निर्यात किया गया।",
      stale: "इनपुट बदल गए हैं। निर्यात से पहले नया पूर्वावलोकन बनाएँ।",
      maxAnchors: "इंटरफ़ेस प्रति पूर्वावलोकन अधिकतम 20 एंकर का समर्थन करता है।",
      noCrypto: "SHA-256 के लिए सुरक्षित ब्राउज़र संदर्भ आवश्यक है।",
      anchorHelp: "स्रोत समय के सख्ती से बढ़ते क्रम में अलग अवलोकन चुनें। संदर्भ समय भी सख्ती से बढ़ना चाहिए।",
      unsupported: "यह ब्राउज़र स्थानीय अवलोकन डेटाबेस नहीं खोल सकता।"
    }
  };

  function copyFor(locale) {
    return COPY[locale] || COPY.en;
  }

  function interpolate(text, values) {
    return String(text).replace(/\{([a-z]+)\}/g, (_, key) => String(values[key] === undefined ? "" : values[key]));
  }

  function sessionKey(event) {
    const id = event && event.clockSessionId;
    return id === null || id === undefined || String(id) === "" ? "legacy" : "session:" + String(id);
  }

  function openDatabase() {
    return new Promise((resolve, reject) => {
      if (!globalThis.indexedDB) return reject(new Error("IndexedDB unavailable"));
      const request = indexedDB.open(DB_NAME);
      request.onsuccess = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains("events")) {
          db.close();
          reject(new Error("Local observation store unavailable"));
          return;
        }
        resolve(db);
      };
      request.onerror = () => reject(request.error || new Error("IndexedDB open failed"));
      request.onblocked = () => reject(new Error("IndexedDB open blocked"));
    });
  }

  async function readLocalEvents() {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      let settled = false;
      const transaction = db.transaction("events", "readonly");
      const request = transaction.objectStore("events").getAll();
      request.onsuccess = () => {
        if (settled) return;
        settled = true;
        const rows = Array.isArray(request.result) ? request.result : [];
        db.close();
        resolve(rows);
      };
      request.onerror = () => {
        if (settled) return;
        settled = true;
        db.close();
        reject(request.error || new Error("Local observation read failed"));
      };
      transaction.onabort = () => {
        if (settled) return;
        settled = true;
        db.close();
        reject(transaction.error || new Error("Local observation read aborted"));
      };
    });
  }

  function mount() {
    const panel = document.getElementById("vt-clock-workspace");
    if (!panel || panel.dataset.mounted === "true") return;
    panel.dataset.mounted = "true";
    const sessionSelect = document.getElementById("vt-session");
    const languageSelect = document.getElementById("vt-language");
    const anchorRoot = document.getElementById("vt-clock-anchors");
    const status = document.getElementById("vt-clock-status");
    const results = document.getElementById("vt-clock-results");
    const addButton = document.getElementById("vt-clock-add");
    const buildButton = document.getElementById("vt-clock-build");
    const exportButton = document.getElementById("vt-clock-export");
    const refreshButton = document.getElementById("vt-clock-refresh");
    const eventBoundInput = document.getElementById("vt-clock-event-bound");
    if (!sessionSelect || !anchorRoot || !status || !results || !addButton || !buildButton || !exportButton || !refreshButton || !eventBoundInput) return;

    let locale = languageSelect && COPY[languageSelect.value] ? languageSelect.value : "en";
    let rows = [{ eventId: "", referenceTimestamp: "", uncertainty: "", evidenceRef: "" },
      { eventId: "", referenceTimestamp: "", uncertainty: "", evidenceRef: "" }];
    let sessionEvents = [];
    let activeSourceId = null;
    let latest = null;
    let busy = false;
    let loadVersion = 0;
    let selectionVersion = 0;
    let refreshTimer = null;
    let currentStatusKey = null;

    function words() {
      return copyFor(locale);
    }

    function setStatus(message) {
      currentStatusKey = null;
      status.textContent = message;
    }

    function setStatusKey(key) {
      currentStatusKey = key;
      status.textContent = words()[key] || COPY.en[key] || "";
    }

    function markStale() {
      if (!latest) return;
      latest = null;
      exportButton.disabled = true;
      results.replaceChildren();
      setStatusKey("stale");
    }

    function selectedEventLabel(event) {
      const time = Number.isFinite(Number(event.timestamp))
        ? new Date(Number(event.timestamp)).toLocaleString(locale, { dateStyle: "medium", timeStyle: "medium" })
        : "—";
      const kind = String(event.kind || "observation");
      const id = String(event.id || "").slice(0, 12);
      return time + " · " + kind + (id ? " · " + id : "");
    }

    function makeLabel(text, htmlFor) {
      const label = document.createElement("label");
      label.textContent = text;
      if (htmlFor) label.htmlFor = htmlFor;
      return label;
    }

    function makeField(className, labelText, control) {
      const wrapper = document.createElement("div");
      wrapper.className = "vt-clock-field " + className;
      wrapper.append(makeLabel(labelText, control.id), control);
      return wrapper;
    }

    function updateOptionAvailability() {
      const selects = Array.from(anchorRoot.querySelectorAll("select[data-anchor-index]"));
      selects.forEach(select => {
        const ownIndex = Number(select.dataset.anchorIndex);
        const used = new Set(rows.filter((row, index) => index !== ownIndex).map(row => row.eventId).filter(Boolean));
        Array.from(select.options).forEach(option => {
          if (!option.value) return;
          option.disabled = used.has(option.value);
        });
      });
    }

    function renderRows() {
      anchorRoot.replaceChildren();
      rows.forEach((row, index) => {
        const fieldset = document.createElement("fieldset");
        fieldset.className = "vt-clock-anchor";
        const legend = document.createElement("legend");
        legend.textContent = words().anchor + " " + (index + 1);
        fieldset.append(legend);

        const observation = document.createElement("select");
        observation.id = "vt-clock-observation-" + index;
        observation.dataset.anchorIndex = String(index);
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "—";
        observation.append(placeholder);
        sessionEvents.forEach(event => {
          const option = document.createElement("option");
          option.value = String(event.id);
          option.textContent = selectedEventLabel(event);
          observation.append(option);
        });
        observation.value = row.eventId;
        observation.addEventListener("change", () => {
          row.eventId = observation.value;
          updateOptionAvailability();
          markStale();
        });

        const reference = document.createElement("input");
        reference.type = "text";
        reference.id = "vt-clock-reference-" + index;
        reference.autocomplete = "off";
        reference.spellcheck = false;
        reference.placeholder = "2026-11-12T10:00:00+01:00";
        reference.value = row.referenceTimestamp;
        reference.addEventListener("input", () => {
          row.referenceTimestamp = reference.value;
          markStale();
        });

        const uncertainty = document.createElement("input");
        uncertainty.type = "number";
        uncertainty.min = "0";
        uncertainty.max = "31536000";
        uncertainty.step = "any";
        uncertainty.id = "vt-clock-uncertainty-" + index;
        uncertainty.value = row.uncertainty;
        uncertainty.addEventListener("input", () => {
          row.uncertainty = uncertainty.value;
          markStale();
        });

        const evidence = document.createElement("input");
        evidence.type = "text";
        evidence.maxLength = MAX_EVIDENCE_REF_LENGTH;
        evidence.id = "vt-clock-evidence-" + index;
        evidence.autocomplete = "off";
        evidence.value = row.evidenceRef;
        evidence.addEventListener("input", () => {
          row.evidenceRef = evidence.value;
          markStale();
        });

        const grid = document.createElement("div");
        grid.className = "vt-clock-fields";
        grid.append(
          makeField("vt-clock-observation-field", words().observation, observation),
          makeField("vt-clock-reference-field", words().reference, reference),
          makeField("vt-clock-uncertainty-field", words().uncertainty, uncertainty),
          makeField("vt-clock-evidence-field", words().evidence, evidence)
        );
        fieldset.append(grid);

        if (rows.length > 2) {
          const remove = document.createElement("button");
          remove.type = "button";
          remove.className = "secondary vt-clock-remove";
          remove.textContent = words().remove;
          remove.setAttribute("aria-label", words().remove + " " + (index + 1));
          remove.addEventListener("click", () => {
            rows.splice(index, 1);
            renderRows();
            markStale();
          });
          fieldset.append(remove);
        }
        anchorRoot.append(fieldset);
      });
      updateOptionAvailability();
      addButton.disabled = rows.length >= UI_MAX_ANCHORS;
    }

    function applyLocale() {
      locale = languageSelect && COPY[languageSelect.value] ? languageSelect.value : "en";
      panel.dir = locale === "ar" || locale === "he" ? "rtl" : "ltr";
      panel.querySelectorAll("[data-vtcal]").forEach(node => {
        const key = node.dataset.vtcal;
        if (words()[key]) node.textContent = words()[key];
      });
      renderRows();
      if (currentStatusKey) setStatusKey(currentStatusKey);
      if (latest) renderResult();
    }

    function scheduleReload() {
      if (refreshTimer) clearTimeout(refreshTimer);
      refreshTimer = setTimeout(() => {
        refreshTimer = null;
        loadSession();
      }, 250);
    }

    async function loadSession() {
      const thisLoad = ++loadVersion;
      buildButton.disabled = true;
      latest = null;
      exportButton.disabled = true;
      results.replaceChildren();
      setStatusKey("loading");
      try {
        const allEvents = await readLocalEvents();
        if (thisLoad !== loadVersion) return;
        const key = sessionSelect.value;
        if (!key) {
          sessionEvents = [];
          activeSourceId = null;
          rows.forEach(row => { row.eventId = ""; });
          renderRows();
          setStatusKey("noSession");
          return;
        }
        if (key === "legacy") {
          sessionEvents = [];
          activeSourceId = null;
          rows.forEach(row => { row.eventId = ""; });
          renderRows();
          setStatusKey("legacy");
          return;
        }
        const sessionRows = allEvents.filter(event => sessionKey(event) === key);
        if (sessionRows.length > MAX_EVENTS) {
          sessionEvents = [];
          activeSourceId = null;
          renderRows();
          setStatusKey("tooMany");
          return;
        }
        if (sessionRows.some(event => typeof event.timestamp !== "number" || !Number.isFinite(event.timestamp))) {
          sessionEvents = [];
          activeSourceId = null;
          renderRows();
          setStatusKey("invalid");
          return;
        }
        sessionEvents = sessionRows.sort((a, b) => a.timestamp - b.timestamp);
        if (!sessionEvents.length) {
          activeSourceId = null;
          renderRows();
          setStatusKey("noEvents");
          return;
        }
        const eventIds = sessionEvents.map(event => String(event.id || ""));
        if (eventIds.some(id => !id || id.length > MAX_ID_LENGTH) || new Set(eventIds).size !== eventIds.length) {
          sessionEvents = [];
          activeSourceId = null;
          renderRows();
          setStatusKey("invalid");
          return;
        }
        const clockBases = new Set(sessionEvents.map(event =>
          typeof event.monotonicElapsedMs === "number" && Number.isFinite(event.monotonicElapsedMs) ? "monotonic" : "wall"
        ));
        if (clockBases.size !== 1) {
          sessionEvents = [];
          activeSourceId = null;
          renderRows();
          setStatusKey("invalid");
          return;
        }
        activeSourceId = SOURCE_ID + "-" + Array.from(clockBases)[0];
        const clockId = String(sessionEvents[0].clockSessionId || "");
        if (!clockId || sessionEvents.some(event => String(event.clockSessionId || "") !== clockId)) {
          sessionEvents = [];
          activeSourceId = null;
          renderRows();
          setStatusKey("legacy");
          return;
        }
        rows.forEach(row => {
          if (!sessionEvents.some(event => String(event.id) === row.eventId)) row.eventId = "";
        });
        renderRows();
        buildButton.disabled = false;
        setStatusKey("ready");
      } catch (_) {
        if (thisLoad !== loadVersion) return;
        sessionEvents = [];
        renderRows();
        setStatus(words().unsupported);
      }
    }

    function renderResult() {
      if (!latest) return;
      const alignment = latest.alignment;
      const outside = alignment.event_count - alignment.aligned_count;
      const summary = document.createElement("p");
      summary.className = "vt-clock-summary";
      summary.textContent = interpolate(words().resultSummary, {
        aligned: alignment.aligned_count,
        total: alignment.event_count,
        outside: outside
      });
      const provenance = document.createElement("p");
      provenance.textContent = interpolate(words().provenance, { count: alignment.complete_anchor_provenance_count });
      const uncertainty = document.createElement("p");
      uncertainty.textContent = interpolate(words().uncertaintyComplete, { count: alignment.complete_declared_uncertainty_input_count });
      const missing = document.createElement("p");
      missing.textContent = words().uncertaintyMissing;
      const drift = document.createElement("p");
      drift.textContent = interpolate(words().drift, {
        value: Number(latest.model.max_absolute_drift_ppm).toLocaleString(locale, { maximumFractionDigits: 3 })
      });
      const hash = document.createElement("p");
      hash.className = "vt-clock-hash";
      hash.textContent = words().hash + ": " + latest.model.model_sha256;

      const tableWrap = document.createElement("div");
      tableWrap.className = "vt-clock-table-wrap";
      const table = document.createElement("table");
      const caption = document.createElement("caption");
      caption.textContent = words().tableAligned;
      table.append(caption);
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      [words().tableObservation, words().tableSource, words().tableAligned, words().tableStatus].forEach(label => {
        const cell = document.createElement("th");
        cell.scope = "col";
        cell.textContent = label;
        header.append(cell);
      });
      thead.append(header);
      table.append(thead);
      const tbody = document.createElement("tbody");
      const eventById = new Map(latest.observations.map(event => [event.id, event]));
      alignment.events.slice(0, 100).forEach(report => {
        const event = eventById.get(report.event_id);
        const row = document.createElement("tr");
        const observation = document.createElement("td");
        observation.textContent = event ? event.kind + " · " + report.event_id.slice(0, 12) : report.event_id;
        const source = document.createElement("td");
        source.textContent = report.source_timestamp || "—";
        const aligned = document.createElement("td");
        aligned.textContent = report.aligned_at || "—";
        const state = document.createElement("td");
        state.textContent = report.status === "aligned_within_anchors" ? words().aligned :
          report.status === "outside_anchor_range" ? words().outside : words().other;
        row.append(observation, source, aligned, state);
        tbody.append(row);
      });
      table.append(tbody);
      tableWrap.append(table);
      const limitation = document.createElement("p");
      limitation.className = "vt-clock-note";
      limitation.textContent = words().limitation;
      const previewLimit = document.createElement("p");
      previewLimit.textContent = words().previewLimit;
      results.replaceChildren(summary, provenance, uncertainty, missing, drift, hash, tableWrap, previewLimit, limitation);
    }

    function invalidateForInput() {
      markStale();
    }

    async function buildPreview() {
      if (busy) return;
      if (rows.length < 2) {
        setStatusKey("needsTwo");
        return;
      }
      const selectedIds = rows.map(row => row.eventId);
      if (selectedIds.some(value => !value) || new Set(selectedIds).size !== selectedIds.length) {
        setStatusKey("invalid");
        return;
      }
      const buildSessionKey = sessionSelect.value;
      const buildSelectionVersion = selectionVersion;
      const selectedEventsSnapshot = sessionEvents.slice();
      const sourceSnapshotAt = new Date().toISOString();
      const sourceId = activeSourceId;
      const clockId = selectedEventsSnapshot[0] && String(selectedEventsSnapshot[0].clockSessionId || "");
      if (!clockId || !sourceId || !selectedEventsSnapshot.length || selectedEventsSnapshot.length > MAX_EVENTS) {
        setStatusKey("invalid");
        return;
      }
      let eventBound = null;
      if (eventBoundInput.value.trim() !== "") {
        eventBound = Number(eventBoundInput.value);
        if (!Number.isFinite(eventBound) || eventBound < 0 || eventBound > 31536000) {
          setStatusKey("invalid");
          return;
        }
      }
      try {
        const anchors = rows.map(row => {
          const event = selectedEventsSnapshot.find(item => String(item.id) === row.eventId);
          if (!event) fail("Selected observation is no longer available");
          const sourceTimestamp = pythonIsoFromEpochMs(Number(event.timestamp));
          const parsedReference = parseZonedTimestamp(row.referenceTimestamp, "reference_timestamp");
          const uncertainty = row.uncertainty.trim() === "" ? null : Number(row.uncertainty);
          if (uncertainty !== null && (!Number.isFinite(uncertainty) || uncertainty < 0 || uncertainty > 31536000)) {
            fail("uncertainty_seconds must be finite and between 0 and 31536000");
          }
          return {
            session_id: clockId,
            source_id: sourceId,
            source_timestamp: sourceTimestamp,
            reference_timestamp: parsedReference.iso,
            uncertainty_seconds: uncertainty,
            reference_evidence_ref: row.evidenceRef.trim() || null
          };
        });
        busy = true;
        buildButton.disabled = true;
        const model = await buildClockModel(anchors);
        if (sessionSelect.value !== buildSessionKey || selectionVersion !== buildSelectionVersion) fail("Selected session changed during alignment");
        const eventRecords = selectedEventsSnapshot.map(event => ({
          event_id: String(event.id),
          session_id: clockId,
          source_id: sourceId,
          timestamp: pythonIsoFromEpochMs(Number(event.timestamp)),
          uncertainty_seconds: eventBound
        }));
        const alignment = alignEvents(model, eventRecords);
        const verification = await verifyClockModel(model);
        if (!verification.valid) fail("The generated clock model did not pass integrity verification");
        latest = {
          model: model,
          alignment: alignment,
          eventBound: eventBound,
          observationCount: selectedEventsSnapshot.length,
          observationIds: selectedEventsSnapshot.map(event => String(event.id)),
          observations: selectedEventsSnapshot.map(event => ({
            id: String(event.id),
            kind: String(event.kind || "observation"),
            timestamp: pythonIsoFromEpochMs(Number(event.timestamp))
          })),
          sourceSnapshotAt: sourceSnapshotAt
        };
        renderResult();
        exportButton.disabled = false;
        setStatusKey("ready");
      } catch (error) {
        latest = null;
        exportButton.disabled = true;
        results.replaceChildren();
        setStatusKey(error && /SHA-256/.test(error.message || "") ? "noCrypto" : "invalid");
      } finally {
        busy = false;
        buildButton.disabled = !sessionEvents.length || !sessionEvents[0].clockSessionId || sessionEvents.length > MAX_EVENTS;
      }
    }

    function exportDerived() {
      if (!latest) return;
      const eventById = new Map(latest.observations.map(event => [event.id, event]));
      const observations = latest.alignment.events.map(report => ({
        event_id: report.event_id,
        kind: eventById.get(report.event_id) ? eventById.get(report.event_id).kind : "observation",
        source_timestamp: report.source_timestamp || (eventById.get(report.event_id) && eventById.get(report.event_id).timestamp) || null,
        status: report.status,
        aligned_at: report.aligned_at || null
      }));
      const payload = {
        format: "ssswet-local-clock-alignment-export-v1",
        exported_at: new Date().toISOString(),
        source_snapshot_at: latest.sourceSnapshotAt,
        local_only: true,
        source_observations_unchanged: true,
        media_included: false,
        timestamp_resolution_ms: 1,
        event_uncertainty_policy: latest.eventBound === null
          ? "undeclared"
          : { method: "uniform_user_declared_absolute_bound", seconds: latest.eventBound },
        assumptions: [
          CLOCK_MAPPING_ASSUMPTION,
          "piecewise_linear_interpolation_between_reference_anchors",
          "drift_is_diagnostic_only",
          "no_extrapolation",
          "interpolation_fraction_is_not_a_probability",
          "browser_alignment_timestamp_resolution_is_one_millisecond"
        ],
        model: latest.model,
        alignment: latest.alignment,
        observations: observations
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ssswet-local-clock-alignment.json";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatusKey("exported");
    }

    addButton.addEventListener("click", () => {
      if (rows.length >= UI_MAX_ANCHORS) {
        setStatusKey("maxAnchors");
        return;
      }
      rows.push({ eventId: "", referenceTimestamp: "", uncertainty: "", evidenceRef: "" });
      renderRows();
      markStale();
    });
    buildButton.addEventListener("click", buildPreview);
    exportButton.addEventListener("click", exportDerived);
    refreshButton.addEventListener("click", loadSession);
    eventBoundInput.addEventListener("input", invalidateForInput);
    sessionSelect.addEventListener("change", () => {
      selectionVersion += 1;
      loadSession();
    });
    if (languageSelect) languageSelect.addEventListener("change", applyLocale);
    window.addEventListener("ssswet:observations-updated", scheduleReload);
    applyLocale();
    setStatusKey("loading");
    if (window.SSSWETVirtualTimeReady) loadSession();
    else window.addEventListener("ssswet:virtual-time-ready", loadSession, { once: true });
  }

  const api = Object.freeze({
    parseZonedTimestamp: parseZonedTimestamp,
    pythonIsoFromEpochMs: pythonIsoFromEpochMs,
    pythonCanonicalJson: canonicalJson,
    buildClockModel: buildClockModel,
    verifyClockModel: verifyClockModel,
    alignEvents: alignEvents,
    locales: Object.freeze(Object.keys(COPY)),
    constants: Object.freeze({
      MAX_ANCHORS: MAX_ANCHORS,
      MAX_EVENTS: MAX_EVENTS,
      UI_MAX_ANCHORS: UI_MAX_ANCHORS,
      ALIGNMENT_METHOD: ALIGNMENT_METHOD,
      CLOCK_MAPPING_ASSUMPTION: CLOCK_MAPPING_ASSUMPTION
    })
  });
  if (typeof window !== "undefined") {
    window.SSSWETClockAlignmentWorkspace = api;
    if (typeof document !== "undefined") mount();
  }
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})();