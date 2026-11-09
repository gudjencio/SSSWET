(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.SSSWETObservationWorkbench = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const FORMAT = "ssswet-virtual-time-map-index-v1";
  const MAX_OBSERVATIONS = 50000;
  const MAX_INPUT_BYTES = 20 * 1024 * 1024;
  const MAX_DUPLICATE_COMPARISONS = 250000;
  const MAX_DUPLICATE_RESULTS = 2000;
  const EARTH_RADIUS_M = 6371008.8;
  const MAX_GPS_ACCURACY_M = 150;
  const MAX_GPS_GAP_MS = 15 * 60 * 1000;
  const MAX_GPS_JUMP_M = 5000;
  const MAX_GPS_SPEED_MPS = 70;

  const KNOWN_KINDS = new Set(["gps", "motion", "orientation", "annotation"]);
  const SENSOR_FIELDS = [
    "x", "y", "z", "alpha", "beta", "gamma", "absolute", "interval",
    "speed", "heading", "altitude", "altitudeAccuracy"
  ];
  const CLOCK_FIELDS = [
    "wallTimestamp", "monotonicElapsedMs", "clockOffsetMs", "clockToleranceMs",
    "clockStatus", "clockSessionId"
  ];

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function byteLength(value) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(value).length;
    return unescape(encodeURIComponent(value)).length;
  }

  function sessionKey(event) {
    const id = event && event.clockSessionId;
    return id === null || id === undefined || String(id) === "" ? "legacy" : "session:" + String(id);
  }

  function withinStructureLimits(value, maxDepth = 64, maxNodes = 1000000) {
    const stack = [[value, 0]];
    let visited = 0;
    while (stack.length) {
      const [current, depth] = stack.pop();
      visited++;
      if (visited > maxNodes || depth > maxDepth) return false;
      if (Array.isArray(current)) {
        for (const item of current) stack.push([item, depth + 1]);
      } else if (isObject(current)) {
        for (const key of Object.keys(current)) stack.push([current[key], depth + 1]);
      }
    }
    return true;
  }

  function validCoords(coords) {
    return isObject(coords) && Number.isFinite(coords.latitude) &&
      Number.isFinite(coords.longitude) && coords.latitude >= -90 &&
      coords.latitude <= 90 && coords.longitude >= -180 && coords.longitude <= 180;
  }

  function validateIndex(payload, options) {
    const opts = options || {};
    const maxObservations = Number.isInteger(opts.maxObservations) && opts.maxObservations > 0
      ? Math.min(opts.maxObservations, MAX_OBSERVATIONS) : MAX_OBSERVATIONS;
    const errors = [];
    const warnings = [];
    if (!isObject(payload)) return { ok: false, errors: ["root_not_object"], warnings, observationCount: 0 };
    if (!withinStructureLimits(payload)) errors.push("structure_limit_exceeded");
    if (payload.format !== FORMAT) errors.push("unsupported_format");
    if (!Array.isArray(payload.observations)) errors.push("observations_not_array");
    const observations = Array.isArray(payload.observations) ? payload.observations : [];
    if (observations.length > maxObservations) errors.push("observation_limit_exceeded");
    const ids = new Set();
    observations.slice(0, maxObservations).forEach((event, index) => {
      const prefix = "observations[" + index + "]";
      if (!isObject(event)) {
        errors.push(prefix + ":not_object");
        return;
      }
      if (typeof event.id !== "string" || !event.id.trim() || event.id.length > 128) {
        errors.push(prefix + ":invalid_id");
      } else if (ids.has(event.id)) {
        errors.push(prefix + ":duplicate_id");
      } else {
        ids.add(event.id);
      }
      if (typeof event.kind !== "string" || !event.kind.trim() || event.kind.length > 64) {
        errors.push(prefix + ":invalid_kind");
      } else if (!KNOWN_KINDS.has(event.kind)) {
        warnings.push(prefix + ":unknown_kind");
      }
      if (!Number.isFinite(event.timestamp) || Math.abs(event.timestamp) > 8640000000000000) {
        errors.push(prefix + ":invalid_timestamp");
      }
      if (event.coords !== undefined && event.coords !== null && !validCoords(event.coords)) {
        errors.push(prefix + ":invalid_coordinates");
      }
      if (event.clockSessionId !== undefined && event.clockSessionId !== null &&
          (typeof event.clockSessionId !== "string" || !event.clockSessionId.trim() || event.clockSessionId.length > 128)) {
        errors.push(prefix + ":invalid_session_id");
      }
      if (event.monotonicElapsedMs !== undefined && event.monotonicElapsedMs !== null &&
          (!Number.isFinite(event.monotonicElapsedMs) || event.monotonicElapsedMs < 0)) {
        errors.push(prefix + ":invalid_monotonic_elapsed");
      }
      if (event.accuracy !== undefined && event.accuracy !== null &&
          (!Number.isFinite(event.accuracy) || event.accuracy < 0)) {
        errors.push(prefix + ":invalid_accuracy");
      }
    });
    return {
      ok: errors.length === 0,
      errors,
      warnings,
      observationCount: observations.length,
      acceptedCount: Math.min(observations.length, maxObservations),
      maxObservations
    };
  }

  function parseIndexText(text) {
    if (typeof text !== "string") return { ok: false, errors: ["input_not_text"] };
    if (byteLength(text) > MAX_INPUT_BYTES) return { ok: false, errors: ["input_size_limit_exceeded"] };
    const normalizedText = text.charCodeAt(0) === 0xFEFF ? text.slice(1) : text;
    let payload;
    try {
      payload = JSON.parse(normalizedText);
    } catch (_) {
      return { ok: false, errors: ["invalid_json"] };
    }
    const validation = validateIndex(payload);
    return { ...validation, payload: validation.ok ? payload : null };
  }

  function groupBySession(observations) {
    const groups = new Map();
    (Array.isArray(observations) ? observations : []).forEach(event => {
      const key = sessionKey(event);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(event);
    });
    return groups;
  }

  function median(values) {
    if (!values.length) return null;
    const sorted = values.slice().sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  }

  function quantile(values, probability) {
    if (!values.length) return null;
    const sorted = values.slice().sort((a, b) => a - b);
    const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(probability * sorted.length) - 1));
    return sorted[index];
  }

  function haversine(a, b) {
    const rad = Math.PI / 180;
    const lat1 = a.latitude * rad;
    const lat2 = b.latitude * rad;
    const dLat = (b.latitude - a.latitude) * rad;
    const dLon = (b.longitude - a.longitude) * rad;
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
    return 2 * EARTH_RADIUS_M * Math.asin(Math.min(1, Math.sqrt(h)));
  }

  function auditProvenance(observations) {
    const groups = groupBySession(observations);
    const sessions = [];
    let withClockMetadata = 0;
    let missingClockMetadata = 0;
    let wallClockDiverged = 0;
    let monotonicUnavailable = 0;
    let monotonicRegressions = 0;
    for (const [key, records] of groups) {
      let previousElapsed = null;
      let previousTimestamp = null;
      let sessionMonotonicRegressions = 0;
      let sessionTimestampRegressions = 0;
      for (const record of records) {
        if (record.clockSessionId && record.clockStatus) withClockMetadata++;
        else missingClockMetadata++;
        if (record.clockStatus === "wall_clock_diverged") wallClockDiverged++;
        if (record.clockStatus === "monotonic_unavailable") monotonicUnavailable++;
        if (Number.isFinite(record.monotonicElapsedMs)) {
          if (previousElapsed !== null && record.monotonicElapsedMs < previousElapsed) { monotonicRegressions++; sessionMonotonicRegressions++; }
          previousElapsed = record.monotonicElapsedMs;
        }
        if (Number.isFinite(record.timestamp)) {
          if (previousTimestamp !== null && record.timestamp < previousTimestamp) { monotonicRegressions++; sessionTimestampRegressions++; }
          previousTimestamp = record.timestamp;
        }
      }
      sessions.push({ sessionKey: key, recordCount: records.length, monotonicRegressions: sessionMonotonicRegressions, timestampRegressions: sessionTimestampRegressions, firstTimestamp: records.reduce((v, e) => Math.min(v, e.timestamp), Infinity), lastTimestamp: records.reduce((v, e) => Math.max(v, e.timestamp), -Infinity) });
    }
    sessions.sort((a, b) => a.sessionKey.localeCompare(b.sessionKey));
    return {
      sessionCount: sessions.length,
      sessions,
      recordsWithClockMetadata: withClockMetadata,
      recordsMissingClockMetadata: missingClockMetadata,
      wallClockDivergedRecords: wallClockDiverged,
      monotonicUnavailableRecords: monotonicUnavailable,
      orderingRegressions: monotonicRegressions,
      crossSessionChronologyInferred: false
    };
  }

  function gpsQuality(observations, options) {
    const opts = options || {};
    const maxAccuracy = Number.isFinite(opts.maxAccuracyM) ? Math.max(0, opts.maxAccuracyM) : MAX_GPS_ACCURACY_M;
    const maxGap = Number.isFinite(opts.maxGapMs) ? Math.max(1, opts.maxGapMs) : MAX_GPS_GAP_MS;
    const maxJump = Number.isFinite(opts.maxJumpM) ? Math.max(1, opts.maxJumpM) : MAX_GPS_JUMP_M;
    const maxSpeed = Number.isFinite(opts.maxSpeedMps) ? Math.max(0, opts.maxSpeedMps) : MAX_GPS_SPEED_MPS;
    const flags = [];
    const bySession = groupBySession((observations || []).filter(event => event && event.kind === "gps"));
    for (const [key, records] of bySession) {
      const sorted = records.slice().sort((a, b) => Number(a.timestamp) - Number(b.timestamp));
      let previous = null;
      for (const event of sorted) {
        const add = code => flags.push({ id: event.id || "", sessionKey: key, code });
        if (!validCoords(event.coords)) add("invalid_coordinates");
        if (!Number.isFinite(event.accuracy)) add("accuracy_missing");
        else if (event.accuracy > maxAccuracy) add("accuracy_above_threshold");
        if (previous && validCoords(event.coords) && validCoords(previous.coords)) {
          const deltaMs = Number(event.timestamp) - Number(previous.timestamp);
          const distanceM = haversine(previous.coords, event.coords);
          if (deltaMs <= 0) add("non_increasing_timestamp");
          else {
            if (deltaMs > maxGap) add("sampling_gap_above_threshold");
            if (distanceM > maxJump) add("segment_distance_above_threshold");
            if (distanceM / (deltaMs / 1000) > maxSpeed) add("implied_speed_above_threshold");
          }
        }
        previous = event;
      }
    }
    const counts = {};
    flags.forEach(flag => { counts[flag.code] = (counts[flag.code] || 0) + 1; });
    return { thresholds: { maxAccuracyM: maxAccuracy, maxGapMs: maxGap, maxJumpM: maxJump, maxSpeedMps: maxSpeed }, flagCount: flags.length, counts, flags };
  }

  function routeMetrics(observations, options) {
    const opts = options || {};
    const maxGap = Number.isFinite(opts.maxGapMs) ? Math.max(1, opts.maxGapMs) : MAX_GPS_GAP_MS;
    const maxJump = Number.isFinite(opts.maxJumpM) ? Math.max(1, opts.maxJumpM) : MAX_GPS_JUMP_M;
    const maxSpeed = Number.isFinite(opts.maxSpeedMps) ? Math.max(0, opts.maxSpeedMps) : MAX_GPS_SPEED_MPS;
    const bySession = groupBySession((observations || []).filter(event => event && event.kind === "gps"));
    const results = [];
    for (const [key, records] of bySession) {
      const sorted = records.slice().sort((a, b) => Number(a.timestamp) - Number(b.timestamp));
      let distanceM = 0, durationMs = 0, movingMs = 0, maxObservedSpeedMps = null, used = 0, excluded = 0, excludedLowAccuracySegments = 0, excludedMissingCoordinateSegments = 0;
      for (let i = 1; i < sorted.length; i++) {
        const a = sorted[i - 1], b = sorted[i];
        if (!validCoords(a.coords) || !validCoords(b.coords)) { excluded++; excludedMissingCoordinateSegments++; continue; }
        const deltaMs = Number(b.timestamp) - Number(a.timestamp);
        const segmentM = haversine(a.coords, b.coords);
        const speed = deltaMs > 0 ? segmentM / (deltaMs / 1000) : Infinity;
        const poorAccuracy = (Number.isFinite(a.accuracy) && a.accuracy > MAX_GPS_ACCURACY_M) || (Number.isFinite(b.accuracy) && b.accuracy > MAX_GPS_ACCURACY_M);
        if (poorAccuracy) { excluded++; excludedLowAccuracySegments++; continue; }
        if (deltaMs <= 0 || deltaMs > maxGap || segmentM > maxJump || speed > maxSpeed) {
          excluded++;
          continue;
        }
        distanceM += segmentM;
        durationMs += deltaMs;
        if (speed >= 0.5) movingMs += deltaMs;
        maxObservedSpeedMps = maxObservedSpeedMps === null ? speed : Math.max(maxObservedSpeedMps, speed);
        used++;
      }
      results.push({ sessionKey: key, gpsRecordCount: sorted.length, gpsFixCount: sorted.filter(event => validCoords(event.coords)).length, acceptedSegments: used, excludedSegments: excluded, excludedLowAccuracySegments, excludedMissingCoordinateSegments, distanceM: Number(distanceM.toFixed(3)), durationMs, movingDurationMs: movingMs, averageSpeedMps: durationMs ? Number((distanceM / (durationMs / 1000)).toFixed(4)) : null, maxObservedSpeedMps: maxObservedSpeedMps === null ? null : Number(maxObservedSpeedMps.toFixed(4)) });
    }
    results.sort((a, b) => a.sessionKey.localeCompare(b.sessionKey));
    return { sessions: results, crossSessionDistanceCalculated: false };
  }

  function temporalCoverage(observations, options) {
    const opts = options || {};
    const gapThresholdMs = Number.isFinite(opts.gapThresholdMs) ? Math.max(1, opts.gapThresholdMs) : MAX_GPS_GAP_MS;
    const bySession = groupBySession((observations || []).filter(event => event && event.kind === "gps" && Number.isFinite(event.timestamp) && validCoords(event.coords)));
    const sessions = [];
    for (const [key, records] of bySession) {
      const times = records.map(event => Number(event.timestamp)).sort((a, b) => a - b);
      const intervals = [];
      for (let i = 1; i < times.length; i++) if (times[i] > times[i - 1]) intervals.push(times[i] - times[i - 1]);
      const gaps = intervals.filter(interval => interval > gapThresholdMs);
      sessions.push({ sessionKey: key, gpsFixCount: times.length, startTimestamp: times.length ? times[0] : null, endTimestamp: times.length ? times[times.length - 1] : null, spanMs: times.length > 1 ? times[times.length - 1] - times[0] : 0, medianIntervalMs: median(intervals), p95IntervalMs: quantile(intervals, 0.95), gapThresholdMs, gapCount: gaps.length, longestGapMs: gaps.length ? gaps.reduce((largest, value) => Math.max(largest, value), 0) : null });
    }
    sessions.sort((a, b) => a.sessionKey.localeCompare(b.sessionKey));
    return { sessions, note: "Sampling gaps describe the recorded cadence only; they do not establish that no event occurred." };
  }

  function canonicalize(value, depth) {
    const level = depth || 0;
    if (level > 64) throw new TypeError("Canonical data exceeds the maximum nesting depth");
    if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
    if (typeof value === "number") {
      if (!Number.isFinite(value)) throw new TypeError("Non-finite values cannot be canonicalized");
      return JSON.stringify(value);
    }
    if (Array.isArray(value)) return "[" + value.map(item => canonicalize(item, level + 1)).join(",") + "]";
    if (!isObject(value)) throw new TypeError("Unsupported canonical value");
    return "{" + Object.keys(value).sort().map(key => JSON.stringify(key) + ":" + canonicalize(value[key], level + 1)).join(",") + "}";
  }

  function withoutId(record) {
    const copy = {};
    Object.keys(record || {}).forEach(key => { if (key !== "id") copy[key] = record[key]; });
    return copy;
  }

  function duplicateCandidates(observations, options) {
    const opts = options || {};
    const maxComparisons = Number.isInteger(opts.maxComparisons) ? Math.min(MAX_DUPLICATE_COMPARISONS, Math.max(1, opts.maxComparisons)) : MAX_DUPLICATE_COMPARISONS;
    const maxResults = Number.isInteger(opts.maxResults) ? Math.min(MAX_DUPLICATE_RESULTS, Math.max(1, opts.maxResults)) : MAX_DUPLICATE_RESULTS;
    const candidates = [];
    let truncated = false;
    const exact = new Map();
    let unhashableRecords = 0;
    for (const event of observations || []) {
      let signature;
      try { signature = canonicalize(withoutId(event)); }
      catch (_) { unhashableRecords++; continue; }
      if (!exact.has(signature)) exact.set(signature, []);
      exact.get(signature).push(event.id || "");
    }
    for (const ids of exact.values()) {
      if (ids.length > 1) {
        if (candidates.length < maxResults) candidates.push({ type: "exact_payload_candidate", recordIds: ids.slice(0, 20), groupSize: ids.length });
        else truncated = true;
      }
    }
    let comparisons = 0;
    const gpsBySession = groupBySession((observations || []).filter(event => event && event.kind === "gps" && validCoords(event.coords)));
    outer: for (const [key, records] of gpsBySession) {
      const sorted = records.slice().sort((a, b) => Number(a.timestamp) - Number(b.timestamp));
      for (let i = 0; i < sorted.length; i++) {
        for (let j = i + 1; j < sorted.length && Number(sorted[j].timestamp) - Number(sorted[i].timestamp) <= 1000; j++) {
          comparisons++;
          if (comparisons > maxComparisons || candidates.length >= maxResults) { truncated = true; break outer; }
          if (haversine(sorted[i].coords, sorted[j].coords) <= 5) {
            candidates.push({ type: "near_duplicate_gps_candidate", sessionKey: key, recordIds: [sorted[i].id || "", sorted[j].id || ""], timeDeltaMs: Number(sorted[j].timestamp) - Number(sorted[i].timestamp), distanceM: Number(haversine(sorted[i].coords, sorted[j].coords).toFixed(3)) });
          }
        }
      }
    }
    return { candidates, comparisonCount: Math.min(comparisons, maxComparisons), unhashableRecords, truncated, destructiveActionTaken: false };
  }

  function summarizeSessions(observations) {
    const bySession = groupBySession(observations || []);
    const summaries = [];
    for (const [key, records] of bySession) {
      const timestamps = records.map(event => Number(event.timestamp)).filter(Number.isFinite);
      const accuracies = records.filter(event => event.kind === "gps" && Number.isFinite(event.accuracy)).map(event => event.accuracy);
      const byKind = {};
      const clockStatuses = {};
      records.forEach(event => {
        byKind[event.kind] = (byKind[event.kind] || 0) + 1;
        const status = event.clockStatus || "missing";
        clockStatuses[status] = (clockStatuses[status] || 0) + 1;
      });
      const start = timestamps.length ? timestamps.reduce((v, n) => Math.min(v, n), Infinity) : null;
      const end = timestamps.length ? timestamps.reduce((v, n) => Math.max(v, n), -Infinity) : null;
      summaries.push({ sessionKey: key, recordCount: records.length, gpsFixCount: byKind.gps || 0, startTimestamp: start, endTimestamp: end, durationMs: start === null ? 0 : end - start, medianGpsAccuracyM: median(accuracies), byKind, clockStatuses });
    }
    summaries.sort((a, b) => a.sessionKey.localeCompare(b.sessionKey));
    return { sessions: summaries, crossSessionChronologyInferred: false };
  }

  function privacyTransform(payload, options) {
    const opts = options || {};
    const decimals = Number.isInteger(opts.coordinateDecimals) ? Math.max(0, Math.min(6, opts.coordinateDecimals)) : 6;
    const timePrecision = ["exact", "minute", "hour", "day"].includes(opts.timePrecision) ? opts.timePrecision : "exact";
    const includeDescriptions = opts.includeDescriptions !== false;
    const includeSensorValues = opts.includeSensorValues !== false;
    const includeClockMetadata = opts.includeClockMetadata !== false;
    const includeSessionIds = opts.includeSessionIds !== false;
    const pseudonymizeIds = opts.pseudonymizeIds === true;
    const observations = (payload.observations || []).map((original, index) => {
      const event = JSON.parse(JSON.stringify(original));
      if (pseudonymizeIds) event.id = "record-" + String(index + 1).padStart(6, "0");
      if (!includeDescriptions) delete event.description;
      if (!includeSensorValues) SENSOR_FIELDS.forEach(field => delete event[field]);
      if (!includeClockMetadata) CLOCK_FIELDS.filter(field => field !== "clockSessionId").forEach(field => delete event[field]);
      if (!includeSessionIds) delete event.clockSessionId;
      if (event.coords && validCoords(event.coords)) {
        const factor = 10 ** decimals;
        event.coords.latitude = Math.round(event.coords.latitude * factor) / factor;
        event.coords.longitude = Math.round(event.coords.longitude * factor) / factor;
        event.coordinatePrecisionDecimals = decimals;
      }
      const unit = timePrecision === "minute" ? 60000 : timePrecision === "hour" ? 3600000 : timePrecision === "day" ? 86400000 : 1;
      if (unit > 1 && Number.isFinite(event.timestamp)) event.timestamp = Math.floor(event.timestamp / unit) * unit;
      if (unit > 1 && Number.isFinite(event.wallTimestamp)) event.wallTimestamp = Math.floor(event.wallTimestamp / unit) * unit;
      if (unit > 1 && Number.isFinite(event.monotonicElapsedMs)) event.monotonicElapsedMs = Math.floor(event.monotonicElapsedMs / unit) * unit;
      if (unit > 1 && Number.isFinite(event.clockOffsetMs)) event.clockOffsetMs = Math.round(event.clockOffsetMs / unit) * unit;
      return event;
    });
    const result = { ...payload, observations, privacyTransform: { coordinateDecimals: decimals, timePrecision, includeDescriptions, includeSensorValues, includeClockMetadata, includeSessionIds, pseudonymizeIds } };
    delete result.integrityManifest;
    delete result.integrity_manifest;
    return result;
  }

  function toGeoJSON(observations, options) {
    const opts = options || {};
    const features = [];
    let skipped = 0;
    for (const event of observations || []) {
      if (!event || !["gps", "annotation"].includes(event.kind) || !validCoords(event.coords)) { skipped++; continue; }
      const properties = { id: event.id || "", kind: event.kind, timestamp: Number.isFinite(event.timestamp) ? event.timestamp : null, accuracy_m: Number.isFinite(event.accuracy) ? event.accuracy : null, clock_status: event.clockStatus || null };
      if (opts.includeSessionIds !== false) properties.session_key = sessionKey(event);
      if (opts.includeDescriptions === true && typeof event.description === "string") properties.description = event.description;
      features.push({ type: "Feature", geometry: { type: "Point", coordinates: [event.coords.longitude, event.coords.latitude] }, properties });
    }
    return { type: "FeatureCollection", features, metadata: { skippedRecordCount: skipped, coordinateOrder: "longitude,latitude", crossSessionChronologyInferred: false } };
  }

  function csvCell(value, numeric) {
    if (value === null || value === undefined) return "";
    let text = String(value);
    if (!numeric && (/^[\s]*[=+\-@]/.test(text) || /^[\t\r]/.test(text))) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
  }

  function toCSV(observations, options) {
    const includeSessionIds = !options || options.includeSessionIds !== false;
    const columns = includeSessionIds
      ? ["id", "session_key", "kind", "timestamp", "latitude", "longitude", "accuracy_m", "clock_status", "event_type", "description"]
      : ["id", "kind", "timestamp", "latitude", "longitude", "accuracy_m", "clock_status", "event_type", "description"];
    const rows = [columns.join(",")];
    for (const event of observations || []) {
      const values = includeSessionIds
        ? [event.id, sessionKey(event), event.kind, event.timestamp, event.coords && event.coords.latitude, event.coords && event.coords.longitude, event.accuracy, event.clockStatus, event.eventType, event.description]
        : [event.id, event.kind, event.timestamp, event.coords && event.coords.latitude, event.coords && event.coords.longitude, event.accuracy, event.clockStatus, event.eventType, event.description];
      rows.push(values.map((value, index) => csvCell(value, [3, 4, 5, 6].includes(index))).join(","));
    }
    return rows.join("\r\n") + "\r\n";
  }

  function sha256Hex(value) {
    if (!globalThis.crypto || !globalThis.crypto.subtle) return Promise.reject(new Error("Web Crypto SHA-256 is unavailable in this context"));
    const bytes = new TextEncoder().encode(value);
    return globalThis.crypto.subtle.digest("SHA-256", bytes).then(buffer =>
      Array.from(new Uint8Array(buffer), byte => byte.toString(16).padStart(2, "0")).join("")
    );
  }

  async function createIntegrityManifest(payload) {
    const validation = validateIndex(payload);
    if (!validation.ok) throw new Error("Cannot create an integrity manifest for an invalid observation index");
    const canonicalPayload = { format: payload.format, observations: payload.observations };
    const canonical = canonicalize(canonicalPayload);
    const digest = await sha256Hex(canonical);
    return { manifestVersion: 1, sourceFormat: FORMAT, observationCount: payload.observations.length, digestAlgorithm: "SHA-256", canonicalization: "json-key-sorted-v1", digest };
  }

  async function verifyIntegrityManifest(payload, manifest) {
    if (!isObject(manifest) || manifest.manifestVersion !== 1 || manifest.sourceFormat !== FORMAT || manifest.digestAlgorithm !== "SHA-256" || manifest.canonicalization !== "json-key-sorted-v1") {
      return { valid: false, reason: "unsupported_manifest" };
    }
    if (!Array.isArray(payload && payload.observations) || manifest.observationCount !== payload.observations.length) {
      return { valid: false, reason: "observation_count_mismatch" };
    }
    const actual = await createIntegrityManifest(payload);
    return { valid: actual.digest === manifest.digest, reason: actual.digest === manifest.digest ? "digest_matches" : "digest_mismatch", expectedDigest: manifest.digest, actualDigest: actual.digest };
  }

  function analyze(payload) {
    const validation = validateIndex(payload);
    if (!validation.ok) throw new Error("Cannot analyze an invalid observation index: " + validation.errors.join(", "));
    return {
      validation,
      provenance: auditProvenance(payload.observations),
      gpsQuality: gpsQuality(payload.observations),
      routeMetrics: routeMetrics(payload.observations),
      temporalCoverage: temporalCoverage(payload.observations),
      duplicates: duplicateCandidates(payload.observations),
      sessionSummaries: summarizeSessions(payload.observations)
    };
  }

  return Object.freeze({
    FORMAT, MAX_OBSERVATIONS, MAX_INPUT_BYTES,
    validateIndex, parseIndexText, auditProvenance, gpsQuality, routeMetrics,
    temporalCoverage, duplicateCandidates, summarizeSessions, privacyTransform,
    toGeoJSON, toCSV, createIntegrityManifest, verifyIntegrityManifest, analyze,
    helpers: Object.freeze({ sessionKey, validCoords, haversine, median, canonicalize })
  });
});