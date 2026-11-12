"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const workspace = require("./clock-alignment-workspace.js");

const SESSION = "clock-session-fixture";
const SOURCE = "browser-session-clock";

function anchor(id, source, reference, uncertainty, evidence) {
  return {
    anchor_id: id,
    session_id: SESSION,
    source_id: SOURCE,
    source_timestamp: source,
    reference_timestamp: reference,
    uncertainty_seconds: uncertainty,
    reference_evidence_ref: evidence
  };
}

function event(id, timestamp, uncertainty) {
  return {
    event_id: id,
    session_id: SESSION,
    source_id: SOURCE,
    timestamp: timestamp,
    uncertainty_seconds: uncertainty
  };
}

async function main() {
  assert.deepEqual(workspace.locales, [
    "en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"
  ]);
  assert.equal(workspace.localeCoverage && Object.values(workspace.localeCoverage).every(count => count === workspace.localeKeyCount), true,
    "all 15 locales must contain every workspace translation key");
  assert.equal(workspace.constants.UI_MAX_ANCHORS, 20);
  assert.equal(workspace.constants.MAX_EVENTS, 5000);
  assert.equal(workspace.constants.MAX_LOCAL_EVENTS, 20000);

  const parsed = workspace.parseZonedTimestamp("2026-11-12T10:00:00+01:00");
  assert.equal(parsed.iso, "2026-11-12T09:00:00+00:00");
  assert.equal(workspace.parseZonedTimestamp("2026-11-12T09:00:00Z").epochMs, parsed.epochMs);
  assert.throws(() => workspace.parseZonedTimestamp("2026-11-12T09:00:00"), /explicit.*offset/);
  assert.throws(() => workspace.parseZonedTimestamp("2026-02-30T09:00:00Z"), /invalid calendar/);
  assert.throws(() => workspace.parseZonedTimestamp("2026-11-12T09:00:00.1234Z"), /millisecond precision/);

  assert.equal(
    workspace.pythonCanonicalJson({ uncertainty_seconds: 1, drift_ppm: 0.00001, anchor_count: 2 }),
    '{"anchor_count":2,"drift_ppm":1e-05,"uncertainty_seconds":1.0}'
  );

  const anchors = [
    anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", 2, "ref:later"),
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", 1, "ref:earlier")
  ];
  const originalAnchors = JSON.stringify(anchors);
  const model = await workspace.buildClockModel(anchors);
  const reversedModel = await workspace.buildClockModel(anchors.slice().reverse());
  assert.equal(model.schema_version, 2);
  assert.equal(model.model_sha256, reversedModel.model_sha256, "anchor input order must not change the deterministic digest");
  assert.equal(model.model_sha256.length, 64);
  assert.equal(model.model_sha256, "f945063082a6295e40ef1aa691412385cd20e9c13d26a02b919c5c58261b0b39",
    "browser canonical model digest must match the Python research engine fixture");
  const fractionalModel = await workspace.buildClockModel([
    anchor(null, "2026-11-12T10:10:00.789Z", "2026-11-12T10:11:01.234Z", 0.375, "ref:ms-later"),
    anchor(null, "2026-11-12T10:00:00.123Z", "2026-11-12T10:01:00.456Z", 0.125, "ref:ms-earlier")
  ]);
  assert.equal(fractionalModel.model_sha256, "564b15a95a0ef8e2d0428a733e5769ee7e5a4006e5557dedd66a5e788d4ddc77",
    "fractional timestamps and non-zero drift must preserve Python canonical fingerprint parity");
  assert.ok(Math.abs(fractionalModel.max_absolute_drift_ppm - 186.45969640362915) < 1e-9);
  assert.equal(model.anchors[0].anchor_id, "anchor-0001");
  assert.equal(model.anchor_evidence_ref_count, 2);
  assert.equal(model.all_anchor_uncertainties_declared, true);
  assert.equal(model.extrapolation_permitted, false);
  assert.equal(model.drift_is_diagnostic_only, true);
  assert.equal(JSON.stringify(anchors), originalAnchors, "model building must not mutate anchor inputs");
  assert.equal((await workspace.verifyClockModel(model)).valid, true);

  assert.deepEqual(Object.keys(workspace.snapshotHashLabels).sort(), workspace.locales.slice().sort(),
    "the observation fingerprint label must be translated in all 15 locales");
  assert.equal(Object.values(workspace.snapshotHashLabels).every(label => typeof label === "string" && label.length > 0), true);
  const snapshotInput = [
    {
      event_id: "event-b",
      kind: "gps",
      source_timestamp: "2026-11-12T10:10:00Z",
      latitude: 48.1,
      longitude: 7.2,
      media_blob: "must-not-be-exported"
    },
    {
      event_id: "event-a",
      kind: "annotation",
      source_timestamp: "2026-11-12T10:00:00Z",
      description: "private free text must not enter the fingerprint payload"
    }
  ];
  const snapshot = await workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", snapshotInput);
  const reversedSnapshot = await workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", snapshotInput.slice().reverse());
  assert.equal(snapshot.format, "ssswet-clock-observation-snapshot-v1");
  assert.equal(snapshot.event_count, 2);
  assert.equal(snapshot.sha256.length, 64);
  assert.equal(snapshot.sha256, reversedSnapshot.sha256, "snapshot fingerprint must ignore IndexedDB cursor order");
  assert.deepEqual(snapshot.observations.map(item => item.event_id), ["event-a", "event-b"],
    "snapshot records must use deterministic source-time ordering");
  const tied = await workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", [
    { event_id: "event-z", kind: "gps", source_timestamp: "2026-11-12T10:05:00Z" },
    { event_id: "event-a", kind: "gps", source_timestamp: "2026-11-12T10:05:00Z" }
  ]);
  assert.deepEqual(tied.observations.map(item => item.event_id), ["event-a", "event-z"],
    "equal timestamps must use locale-independent event-ID ordering");
  assert.equal((await workspace.verifyObservationSnapshot(snapshot)).valid, true);
  assert.deepEqual(Object.keys(snapshot.observations[0]).sort(), ["event_id", "kind", "source_timestamp"],
    "snapshot metadata must exclude coordinates, media and free-text annotation content");
  const changedTimestamp = await workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", [
    snapshotInput[0],
    { ...snapshotInput[1], source_timestamp: "2026-11-12T10:00:01Z" }
  ]);
  assert.notEqual(snapshot.sha256, changedTimestamp.sha256, "source timestamp changes must alter the snapshot fingerprint");
  const changedKind = await workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", [
    snapshotInput[0],
    { ...snapshotInput[1], kind: "different-kind" }
  ]);
  assert.notEqual(snapshot.sha256, changedKind.sha256, "event kind changes must alter the snapshot fingerprint");
  const tamperedSnapshot = {
    ...snapshot,
    observations: snapshot.observations.map((item, index) =>
      index === 0 ? { ...item, source_timestamp: "2026-11-12T10:00:02+00:00" } : item
    )
  };
  assert.equal((await workspace.verifyObservationSnapshot(tamperedSnapshot)).valid, false,
    "tampered snapshot content must fail verification");
  const privacyExtendedSnapshot = { ...snapshot, observations: snapshot.observations.map(item => ({ ...item, latitude: 48.1 })) };
  assert.equal((await workspace.verifyObservationSnapshot(privacyExtendedSnapshot)).valid, false,
    "unexpected extra fields must not be accepted as part of a canonical snapshot");
  await assert.rejects(() => workspace.buildObservationSnapshot(SESSION, SOURCE, "monotonic", [
    snapshotInput[0], { ...snapshotInput[1], event_id: "event-b" }
  ]), /unique/);
  await assert.rejects(() => workspace.buildObservationSnapshot(SESSION, SOURCE, "invalid", snapshotInput), /clock_basis/);
  await assert.rejects(() => workspace.buildObservationSnapshot(SESSION, SOURCE, "wall", snapshotInput), /match the declared browser clock source/);

  const observations = [
    event("outside-before", "2026-11-12T09:59:59Z", 0.5),
    event("at-start", "2026-11-12T10:00:00Z", 0.5),
    event("middle", "2026-11-12T10:05:00Z", 0.5),
    event("at-end", "2026-11-12T10:10:00Z", 0.5),
    event("outside-after", "2026-11-12T10:10:01Z", 0.5)
  ];
  const originalEvents = JSON.stringify(observations);
  const result = workspace.alignEvents(model, observations);
  assert.equal(result.event_count, 5);
  assert.equal(result.aligned_count, 3);
  assert.equal(result.extrapolation_permitted, false);
  assert.equal(result.unrecorded_history_recovered, false);
  assert.equal(result.future_prediction_performed, false);
  assert.equal(result.events[0].status, "outside_anchor_range");
  assert.equal(result.events[0].aligned_at, null);
  assert.equal(result.events[1].aligned_at, "2026-11-12T10:01:00+00:00");
  assert.equal(result.events[2].aligned_at, "2026-11-12T10:06:00+00:00");
  assert.equal(result.events[2].interpolation_fraction, 0.5);
  assert.equal(result.events[2].interpolation_fraction_not_a_probability, true);
  assert.equal(result.events[2].declared_uncertainty_envelope_seconds, 2.0);
  assert.equal(result.events[2].anchor_provenance_complete, true);
  assert.equal(result.events[4].status, "outside_anchor_range");
  assert.equal(JSON.stringify(observations), originalEvents, "alignment must not mutate source observations");

  const noBoundsModel = await workspace.buildClockModel([
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", null, null),
    anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", null, null)
  ]);
  const noBounds = workspace.alignEvents(noBoundsModel, [event("no-bounds", "2026-11-12T10:05:00Z", null)]);
  assert.equal(noBounds.events[0].declared_uncertainty_envelope_seconds, null);
  assert.equal(noBounds.events[0].declared_uncertainty_inputs_complete, false);
  assert.equal(noBounds.events[0].anchor_provenance_complete, false);
  assert.equal(noBounds.events[0].anchor_uncertainty_declared, false);

  const differentSession = workspace.alignEvents(model, [{
    event_id: "other-session",
    session_id: "another-session",
    source_id: SOURCE,
    timestamp: "2026-11-12T10:05:00Z"
  }]);
  assert.equal(differentSession.events[0].status, "different_session_or_source");
  assert.equal(differentSession.events[0].aligned_at, null);

  await assert.rejects(() => workspace.buildClockModel([
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:02:00Z", null, null),
    anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:01:00Z", null, null)
  ]), /strictly increasing/);
  await assert.rejects(() => workspace.buildClockModel([
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", -1, null),
    anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", null, null)
  ]), /non-negative/);
  await assert.rejects(() => workspace.buildClockModel([
    anchor("same", "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", null, null),
    anchor("same", "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", null, null)
  ]), /unique/);
  await assert.rejects(() => workspace.buildClockModel([
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", null, "x".repeat(501)),
    anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", null, null)
  ]), /at most 500/);
  await assert.rejects(() => workspace.buildClockModel([
    anchor(null, "2026-11-12T10:00:00Z", "2026-11-12T10:01:00Z", null, null),
    { ...anchor(null, "2026-11-12T10:10:00Z", "2026-11-12T10:11:00Z", null, null), session_id: "other" }
  ]), /only one session/);

  const tampered = { ...model, extrapolation_permitted: true };
  assert.equal((await workspace.verifyClockModel(tampered)).valid, false,
    "semantic flags must be verified independently of the recorded digest");
  const tamperedDigest = { ...model, max_absolute_drift_ppm: model.max_absolute_drift_ppm + 1 };
  assert.equal((await workspace.verifyClockModel(tamperedDigest)).valid, false);

  assert.throws(() => workspace.alignEvents(model, Array.from({ length: 5001 }, (_, index) =>
    event("event-" + index, "2026-11-12T10:05:00Z", null)
  )), /5000/);

  const html = fs.readFileSync(path.join(__dirname, "virtual-time-travel.html"), "utf8");
  const script = fs.readFileSync(path.join(__dirname, "clock-alignment-workspace.js"), "utf8");
  const css = fs.readFileSync(path.join(__dirname, "virtual-time-travel.css"), "utf8");
  assert.match(html, /id="vt-clock-workspace"/);
  assert.match(html, /id="vt-clock-build"[^>]*disabled/);
  assert.match(html, /id="vt-clock-export"[^>]*disabled/);
  assert.match(html, /<script src="clock-alignment-workspace\.js"><\/script>/);
  assert.match(html, /aria-live="polite"/);
  assert.match(script, /indexedDB\.open\(DB_NAME\)/);
  assert.match(script, /db\.transaction\("events", "readonly"\)/);
  assert.match(script, /openCursor\(\)/);
  assert.doesNotMatch(script, /getAll\(\)/);
  assert.doesNotMatch(script, /transaction\("events",\s*"readwrite"\)/);
  assert.match(script, /UI_MAX_ANCHORS = 20/);
  assert.match(script, /clockBases\.size !== 1/);
  assert.match(script, /selectionVersion/);
  assert.match(script, /inputVersion/);
  assert.match(script, /source_observation_snapshot/);
  assert.match(script, /SNAPSHOT_HASH_LABELS/);
  assert.match(script, /ssswet:virtual-time-unavailable/);
  assert.match(css, /:focus-visible/);
  const sw = fs.readFileSync(path.join(__dirname, "sw.js"), "utf8");
  assert.match(sw, /ssswet-web-v199/);
  assert.match(sw, /clock-alignment-workspace\.js/);

  console.log("Clock alignment workspace: deterministic model, strict timestamps, provenance, uncertainty, no-extrapolation, session isolation, local-read-only access and 15 locales verified.");
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
