"use strict";
const api = require("../../web/observation-workbench.js");
const SIZE = 10000;
const observations = Array.from({ length: SIZE }, (_, index) => {
  const session = "bench-" + (index % 5);
  const step = Math.floor(index / 5);
  return {
    id: "bench-" + index,
    kind: "gps",
    timestamp: 1800000000000 + step * 1500,
    clockSessionId: session,
    wallTimestamp: 1800000000000 + step * 1500,
    monotonicElapsedMs: step * 1500,
    clockStatus: "within_tolerance",
    accuracy: 5 + (index % 4),
    coords: { latitude: 48 + step * 0.000001, longitude: 2 + step * 0.000001 }
  };
});
const payload = { format: api.FORMAT, observations };
const samples = [];
for (let trial = 0; trial < 5; trial++) {
  const start = process.hrtime.bigint();
  const report = api.analyze(payload);
  const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
  if (!report.validation.ok || report.provenance.sessionCount !== 5 || report.sessionSummaries.sessions.length !== 5) {
    throw new Error("Synthetic benchmark correctness guard failed");
  }
  samples.push(elapsedMs);
}
samples.sort((a, b) => a - b);
const p95 = samples[Math.min(samples.length - 1, Math.ceil(samples.length * 0.95) - 1)];
const median = samples[Math.floor(samples.length / 2)];
console.log(JSON.stringify({ workload: "10,000 synthetic GPS observations / 5 isolated sessions", trials: samples.length, medianMs: Number(median.toFixed(2)), p95Ms: Number(p95.toFixed(2)), maxMs: Number(samples[samples.length - 1].toFixed(2)), limitMs: 5000, result: p95 < 5000 ? "PASS" : "FAIL", note: "Synthetic Node.js runner measurement; not a browser field-performance guarantee." }, null, 2));
if (p95 >= 5000) process.exitCode = 1;