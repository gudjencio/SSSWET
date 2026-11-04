const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync(new URL("./keyframe-correspondence.js", `file://${__filename}`), "utf8");
new vm.Script(source);

const sandbox = {
  document: { getElementById: () => null },
  window: {}
};
vm.runInNewContext(source, sandbox);
const api = sandbox.window.SSSWETKeyframeCorrespondence;
assert.ok(api, "The pure correspondence API must be available for deterministic tests");

for (const feature of [
  "patchDescriptors",
  "correspondenceDistribution",
  "カメラ姿勢",
  "3D overlap",
  "ctx.getImageData",
  "mutual matches",
  "correspondances réciproques",
  "forward candidates",
  "mutualNote",
  "nearestMatches",
  "nearestMatchDetails",
  "medianDescriptorDistance",
  "medianRatio",
  "diagnosticNote",
  "backwardMatch.index !== i",
  "both directional ratio tests"
]) {
  if (!source.includes(feature)) throw new Error(`Keyframe correspondence feature missing: ${feature}`);
}

const locales = ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"];
for (const locale of locales) {
  const localeLine = source.split("\n").find(line => line.trim().startsWith(`${locale}: {`));
  if (!localeLine ||
      !localeLine.includes("forward:") ||
      !localeLine.includes("mutualNote:") ||
      !localeLine.includes("notAvailable:") ||
      !localeLine.includes("descriptorDistance:") ||
      !localeLine.includes("ratio:") ||
      !localeLine.includes("diagnosticNote:")) {
    throw new Error(`Keyframe correspondence locale is incomplete: ${locale}`);
  }
}

const unique = api.correspondenceDistribution(
  [[0], [10], [20]],
  [[0.01], [10.01], [20.01]]
);
assert.equal(unique.forwardCandidates, 3, "All three distinctive forward candidates should pass");
assert.equal(unique.count, 3, "Distinctive reciprocal matches should be retained");
assert.equal(unique.dx, 0);
assert.equal(unique.dy, 0);
assert.equal(unique.spread, 0);
assert.ok(Math.abs(unique.medianDescriptorDistance - 0.01) < 1e-12,
  "Median descriptor distance must reflect the known synthetic offset");
assert.ok(unique.medianRatio >= 0 && unique.medianRatio < 0.82,
  "Median directional ratio must remain below the acceptance threshold");
assert.equal(
  JSON.stringify(unique),
  JSON.stringify(api.correspondenceDistribution([[0], [10], [20]], [[0.01], [10.01], [20.01]])),
  "Repeated evaluation of the same descriptors must be deterministic"
);

const duplicate = api.correspondenceDistribution(
  [[0], [0.02], [10]],
  [[0.01], [10.01]]
);
assert.equal(duplicate.forwardCandidates, 3, "The fixture should expose three forward candidates");
assert.equal(duplicate.count, 1, "A many-to-one ambiguity must not be counted as reciprocal");
assert.ok(duplicate.count < duplicate.forwardCandidates);
assert.ok(Number.isFinite(duplicate.medianDescriptorDistance));
assert.ok(Number.isFinite(duplicate.medianRatio));

const details = api.nearestMatchDetails([[0]], [[0.1], [0.2]]);
assert.equal(details[0].index, 0);
assert.ok(Math.abs(details[0].bestDistance - 0.1) < 1e-12);
assert.ok(Math.abs(details[0].ratio - 0.5) < 1e-12);
const overDistanceLimit = api.nearestMatchDetails([[0]], [[0.72], [2]]);
assert.equal(overDistanceLimit[0].index, -1, "A best descriptor distance at the exclusive threshold must be rejected");

assert.deepEqual(Array.from(api.nearestMatches([[0]], [[0.1]])), [-1],
  "A single possible target cannot pass a two-neighbour ratio test");
assert.deepEqual(Array.from(api.nearestMatches([[0]], [[0], [0]])), [-1],
  "Equal zero-distance alternatives must be rejected as ambiguous");
const tied = api.correspondenceDistribution([[0], [0]], [[0], [0]]);
assert.equal(tied.count, 0, "Identical descriptors must not create false reciprocal matches");
assert.equal(tied.medianDescriptorDistance, null);
assert.equal(tied.medianRatio, null);

const insufficient = api.correspondenceDistribution([[0]], [[0.1]]);
assert.equal(insufficient.count, 0);
assert.equal(insufficient.dx, null);
assert.equal(insufficient.dy, null);
assert.equal(insufficient.spread, null);
assert.equal(insufficient.medianDescriptorDistance, null);
assert.equal(insufficient.medianRatio, null);
assert.equal(api.median([]), null);
assert.ok(Math.abs(api.distance([0, 0], [3, 4]) - Math.sqrt(12.5)) < 1e-12);
assert.equal(api.distance([0], [0, 1]), Infinity, "Mismatched descriptor dimensions must be treated as invalid");

console.log("Validated deterministic reciprocal matching, descriptor diagnostics, ambiguity rejection, empty-sample handling and 15 locales.");
