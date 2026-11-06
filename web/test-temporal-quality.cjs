const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync(new URL("./temporal-quality.js", `file://${__filename}`), "utf8");
new vm.Script(source);
const sandbox = {
  window: {},
  document: {
    querySelectorAll: () => [],
    getElementById: () => null
  },
  Date,
  Math,
  Number,
  String,
  Array,
  Set
};
vm.runInNewContext(source, sandbox);
const api = sandbox.window.SSSWETTemporalQuality;
assert.ok(api, "Temporal quality helpers must be available");

const coverage = api.analyzeCoverage([
  { timestamp: 0, kind: "gps" },
  { timestamp: 60000, kind: "annotation" },
  { timestamp: 120000, kind: "gps" },
  { timestamp: 1200000, kind: "gps" }
]);
assert.equal(coverage.timestampedCount, 4);
assert.equal(coverage.medianIntervalMs, 60000);
assert.equal(coverage.gapCount, 1);
assert.equal(coverage.longestGapMs, 1080000);
assert.equal(coverage.interpolationPerformed, false);
const missingTimestamp = api.analyzeCoverage([{ timestamp: null }, { timestamp: 1000 }]);
assert.equal(missingTimestamp.timestampedCount, 1, "Missing timestamps must not be coerced to the Unix epoch");

const gps = [
  { id: "a", kind: "gps", timestamp: 0, coords: { latitude: 48.0, longitude: 2.0 }, accuracy: 5 },
  { id: "b", kind: "gps", timestamp: 10000, coords: { latitude: 48.0001, longitude: 2.0001 }, accuracy: 6 },
  { id: "poor", kind: "gps", timestamp: 20000, coords: { latitude: 48.0002, longitude: 2.0002 }, accuracy: 400 },
  { id: "c", kind: "gps", timestamp: 2000000, coords: { latitude: 48.0003, longitude: 2.0003 }, accuracy: 7 },
  { id: "invalid", kind: "gps", timestamp: 2010000, coords: { latitude: 120, longitude: 2 }, accuracy: 7 }
];
const track = api.segmentGpsTrack(gps);
assert.deepEqual(Array.from(track.accepted, item => item.id), ["a", "b", "c"]);
assert.equal(track.segments.length, 1);
assert.equal(track.segments[0].length, 2);
assert.equal(track.diagnostics.lowAccuracy, 1);
assert.equal(track.diagnostics.invalidCoordinates, 1);
assert.equal(track.diagnostics.gapBreaks, 1);
assert.equal(track.diagnostics.rejectedCount, 2);

const original = {
  id: "private-id",
  kind: "gps",
  timestamp: 123456789,
  coords: { latitude: 48.123456, longitude: 2.654321 },
  accuracy: 3.4,
  altitude: 42,
  speed: 12,
  heading: 90,
  description: "Private address and note",
  alpha: 12,
  blob: "not exported"
};
const noLocation = api.createPrivacySafeExport([original]);
assert.equal(noLocation.format, "ssswet-virtual-time-map-privacy-safe-v1");
assert.equal(noLocation.observation_count, 1);
assert.equal(noLocation.observations[0].timestamp, Math.round(original.timestamp / 60000) * 60000);
assert.equal("coords" in noLocation.observations[0], false);
assert.equal("description" in noLocation.observations[0], false);
assert.equal("speed" in noLocation.observations[0], false);
assert.equal("id" in noLocation.observations[0], false);
assert.equal(noLocation.privacy.media_included, false);

const coarse = api.createPrivacySafeExport([original], { includeCoarseLocation: true });
assert.equal(coarse.observations[0].coords.latitude, 48.123);
assert.equal(coarse.observations[0].coords.longitude, 2.654);
assert.equal(original.coords.latitude, 48.123456, "Export must not mutate original local records");
const invalidLocation = api.createPrivacySafeExport([{
  kind: "gps", timestamp: 1000, coords: { latitude: 120, longitude: 2 }
}], { includeCoarseLocation: true });
assert.equal("coords" in invalidLocation.observations[0], false, "Invalid coordinates must not enter the reduced export");

for (const locale of ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]) {
  assert.ok(source.includes(`${locale}: {`), `Missing temporal quality locale ${locale}`);
}
assert.throws(() => api.analyzeCoverage([], { maxGapMs: 0 }), /positive/);
assert.throws(() => api.segmentGpsTrack(new Array(100001)), /100000/);
assert.throws(() => api.createPrivacySafeExport(new Array(100001)), /100000/);

console.log("Validated temporal coverage, GPS track segmentation, privacy-safe export and 15 locales.");
