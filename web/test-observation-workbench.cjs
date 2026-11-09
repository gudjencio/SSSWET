"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const api = require("./observation-workbench.js");

function gps(id, timestamp, latitude, longitude, session, accuracy = 5) {
  return { id, kind: "gps", timestamp, clockSessionId: session, wallTimestamp: timestamp,
    monotonicElapsedMs: Math.max(0, timestamp - 1000), clockStatus: "within_tolerance",
    coords: { latitude, longitude }, accuracy };
}

const payload = {
  format: api.FORMAT,
  exported_at: "2026-11-09T08:00:00.000Z",
  session_ordering_note: "Sessions are not globally comparable.",
  observations: [
    gps("a", 1000, 48.0000, 2.0000, "A"),
    gps("b", 61000, 48.0005, 2.0000, "A"),
    gps("c", 121000, 48.0010, 2.0000, "A"),
    { id: "note", kind: "annotation", timestamp: 122000, clockSessionId: "A",
      coords: { latitude: 48.001, longitude: 2 }, eventType: "note", description: "Private field note" },
    gps("other", 500, 48.0100, 2.0100, "B")
  ]
};

const validation = api.validateIndex(payload);
assert.equal(validation.ok, true);
assert.equal(validation.observationCount, 5);
assert.equal(api.validateIndex({ ...payload, format: "unknown" }).errors[0], "unsupported_format");
assert.ok(api.validateIndex({ ...payload, observations: [payload.observations[0], payload.observations[0]] }).errors.includes("observations[1]:duplicate_id"));
assert.ok(api.validateIndex({ ...payload, observations: [{ ...payload.observations[0], coords: { latitude: 91, longitude: 0 } }] }).errors.includes("observations[0]:invalid_coordinates"));
assert.ok(api.validateIndex({ ...payload, observations: [{ ...payload.observations[0], clockSessionId: "   " }] }).errors.includes("observations[0]:invalid_session_id"));
assert.ok(api.validateIndex({ ...payload, observations: new Array(api.MAX_OBSERVATIONS + 1).fill(payload.observations[0]) }).errors.includes("observation_limit_exceeded"));
assert.equal(api.parseIndexText("{").errors[0], "invalid_json");
assert.equal(api.parseIndexText("\uFEFF" + JSON.stringify(payload)).ok, true, "a UTF-8 BOM must not break valid JSON imports");
assert.equal(api.parseIndexText(" ".repeat(api.MAX_INPUT_BYTES + 1)).errors[0], "input_size_limit_exceeded");
let deep = { value: true }; for (let i = 0; i < 70; i++) deep = { nested: deep };
assert.ok(api.validateIndex({ ...payload, observations: [{ id: "deep", kind: "annotation", timestamp: 1, extra: deep }] }).errors.includes("structure_limit_exceeded"));
const futureKind = api.validateIndex({ ...payload, observations: [{ id: "future", kind: "future_sensor", timestamp: 1 }] });
assert.equal(futureKind.ok, true, "unknown future kinds must remain forward-compatible");
assert.ok(futureKind.warnings.includes("observations[0]:unknown_kind"));

const provenance = api.auditProvenance(payload.observations);
assert.equal(provenance.sessionCount, 2);
assert.equal(provenance.crossSessionChronologyInferred, false);
assert.equal(provenance.recordsWithClockMetadata, 4);
assert.equal(provenance.recordsMissingClockMetadata, 1);

const quality = api.gpsQuality(payload.observations);
assert.equal(quality.flagCount, 0);
const badQuality = api.gpsQuality([
  gps("q1", 1000, 48, 2, "Q", 200),
  gps("q2", 1000000, 49, 3, "Q", 200)
]);
assert.ok(badQuality.counts.accuracy_above_threshold >= 1);
assert.ok(badQuality.counts.sampling_gap_above_threshold >= 1);
assert.ok(badQuality.counts.segment_distance_above_threshold >= 1);
assert.ok(badQuality.counts.implied_speed_above_threshold >= 1);

const routes = api.routeMetrics(payload.observations);
assert.equal(routes.crossSessionDistanceCalculated, false);
assert.equal(routes.sessions.length, 2);
assert.ok(routes.sessions.find(s => s.sessionKey === "session:A").distanceM > 100);
assert.equal(routes.sessions.find(s => s.sessionKey === "session:A").excludedLowAccuracySegments, 0);
const poorRoute = api.routeMetrics([gps("poor-a", 1000, 48, 2, "P", 200), gps("poor-b", 2000, 48.0001, 2, "P", 5)]);
assert.equal(poorRoute.sessions[0].excludedLowAccuracySegments, 1, "segments touching low-accuracy fixes must not enter route totals");
const missingFixRoute = api.routeMetrics([gps("m1", 1000, 48, 2, "M"), { id: "m2", kind: "gps", timestamp: 2000, clockSessionId: "M" }, gps("m3", 3000, 48.0002, 2, "M")]);
assert.equal(missingFixRoute.sessions[0].acceptedSegments, 0, "route metrics must not bridge across a GPS record without coordinates");
assert.equal(missingFixRoute.sessions[0].gpsRecordCount, 3);
assert.equal(missingFixRoute.sessions[0].gpsFixCount, 2);
assert.equal(missingFixRoute.sessions[0].excludedMissingCoordinateSegments, 2);
assert.equal(routes.sessions.find(s => s.sessionKey === "session:B").acceptedSegments, 0);

const coverage = api.temporalCoverage([
  gps("t1", 0, 48, 2, "T"), gps("t2", 60000, 48, 2, "T"),
  { id: "t-missing", kind: "gps", timestamp: 600000, clockSessionId: "T" },
  gps("t3", 1200000, 48, 2, "T")
]);
assert.equal(coverage.sessions[0].gapCount, 1);
assert.equal(coverage.sessions[0].longestGapMs, 1140000);
assert.equal(coverage.sessions[0].gpsFixCount, 3, "temporal GPS coverage must count only coordinate-bearing fixes");
assert.match(coverage.note, /do not establish/);

const duplicates = api.duplicateCandidates([
  gps("d1", 1000, 48, 2, "D"),
  gps("d2", 1500, 48.000001, 2, "D"),
  gps("d3", 9000, 48.1, 2.1, "D")
]);
assert.ok(duplicates.candidates.some(c => c.type === "near_duplicate_gps_candidate"));
assert.equal(duplicates.destructiveActionTaken, false);
const exact = api.duplicateCandidates([
  { id: "x1", kind: "annotation", timestamp: 10, description: "same" },
  { id: "x2", kind: "annotation", timestamp: 10, description: "same" }
]);
assert.ok(exact.candidates.some(c => c.type === "exact_payload_candidate"));
const boundedDuplicates = api.duplicateCandidates(Array.from({ length: 30 }, (_, i) => gps("cap-" + i, 1000, 48, 2, "CAP")), { maxComparisons: 20, maxResults: 5 });
assert.ok(boundedDuplicates.comparisonCount <= 20);
assert.equal(boundedDuplicates.truncated, true);
assert.ok(boundedDuplicates.candidates.length <= 5);

const originalDescription = payload.observations[3].description;
payload.observations[3].customProvenance = { source: "field-log" };
const redacted = api.privacyTransform(payload, {
  coordinateDecimals: 2, timePrecision: "hour", includeDescriptions: false,
  includeSensorValues: false, includeClockMetadata: false, includeSessionIds: false, pseudonymizeIds: true
});
assert.equal(redacted.observations[3].description, undefined);
assert.equal(redacted.observations[0].clockSessionId, undefined);
assert.equal(redacted.observations[0].id, "record-000001");
assert.equal(redacted.observations[0].coords.latitude, 48);
assert.equal(redacted.observations[0].timestamp % 3600000, 0);
assert.equal(redacted.observations[0].monotonicElapsedMs, undefined, "disabled clock metadata must be removed");
const sessionOnly = api.privacyTransform(payload, { includeClockMetadata: false, includeSessionIds: true });
assert.equal(sessionOnly.observations[0].clockSessionId, "A", "session identifiers can be retained independently from clock diagnostics");
const coarseClock = api.privacyTransform(payload, { timePrecision: "hour", includeClockMetadata: true });
assert.equal(coarseClock.observations[0].monotonicElapsedMs % 3600000, 0, "coarsened time must also coarsen monotonic metadata");
assert.equal(payload.observations[3].description, originalDescription, "privacy transforms must not mutate source data");
assert.deepEqual(redacted.observations[3].customProvenance, { source: "field-log" }, "unknown metadata must be preserved rather than silently discarded");
assert.equal(redacted.exported_at, payload.exported_at, "export time is preserved and must be reviewed before sharing");

const geojson = api.toGeoJSON(payload.observations);
assert.equal(geojson.features.length, 5);
assert.deepEqual(geojson.features[0].geometry.coordinates, [2, 48]);
assert.equal(geojson.metadata.coordinateOrder, "longitude,latitude");
const csv = api.toCSV([{ id: "=2+2", kind: "annotation", timestamp: 1, description: "line,\"quoted\"" }]);
assert.match(csv, /'=2\+2/);
assert.match(api.toCSV([{ id: "  =1+1", kind: "annotation", timestamp: 1 }]), /'  =1\+1/, "leading whitespace must not bypass CSV formula neutralization");
assert.match(csv, /"line,""quoted"""/);
const csvWithoutSessions = api.toCSV(redacted.observations, { includeSessionIds: false });
assert.doesNotMatch(csvWithoutSessions, /session_key|legacy/, "CSV export must not reintroduce a synthetic session group after session IDs are removed");

(async () => {
  const manifestA = await api.createIntegrityManifest(payload);
  const manifestB = await api.createIntegrityManifest(payload);
  assert.equal(manifestA.digest, manifestB.digest, "identical payloads must have identical manifests");
  assert.equal((await api.verifyIntegrityManifest(payload, manifestA)).valid, true);
  await assert.rejects(() => api.createIntegrityManifest({ format: "wrong", observations: [] }), /invalid observation index/);
  const changed = { ...payload, observations: payload.observations.map((e, i) => i ? e : { ...e, accuracy: 9 }) };
  assert.equal((await api.verifyIntegrityManifest(changed, manifestA)).valid, false);
  const report = api.analyze(payload);
  assert.equal(report.validation.ok, true);
  assert.equal(report.sessionSummaries.sessions.length, 2);
  assert.equal(report.provenance.crossSessionChronologyInferred, false);
  const source = fs.readFileSync(path.join(__dirname, "observation-workbench.html"), "utf8");
  assert.match(source, /type="file"/);
  assert.match(source, /aria-live="polite"/);
  assert.match(source, /observation-workbench.js/);
  assert.match(source, /autocomplete="off"/);
  const ui = fs.readFileSync(path.join(__dirname, "observation-workbench-ui.js"), "utf8");
  assert.doesNotMatch(ui, /\bfetch\s*\(|XMLHttpRequest|sendBeacon/, "the workbench must not upload local observation files");
  assert.match(source, /for="index-file"/);
  assert.match(source, /role="status" aria-live="polite"/);
  const htmlIds = [...source.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(htmlIds).size, htmlIds.length, "HTML IDs must be unique");
  const uiIds = [...ui.matchAll(/\$\("([^"]+)"\)/g)].map(match => match[1]);
  uiIds.forEach(id => assert.ok(htmlIds.includes(id), "UI references a missing HTML element: " + id));
  assert.ok(source.indexOf("observation-workbench.js") < source.indexOf("observation-workbench-ui.js"), "analysis API must load before UI bindings");
  assert.doesNotMatch(source, /onclick\s*=|<script[^>]+src="https?:/i, "the page must not use inline event handlers or remote scripts");
  console.log("Observation workbench regression tests passed (synthetic records; not a field-accuracy or scientific-validation benchmark).");
})().catch(error => { console.error(error); process.exitCode = 1; });