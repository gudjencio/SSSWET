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
  "candidate matches",
  "correspondances candidates",
  "カメラ姿勢",
  "3D overlap",
  "ctx.getImageData",
  "mutual matches",
  "correspondances réciproques",
  "one-way candidates",
  "mutualNote",
  "nearestMatches",
  "backward[bestIndex] !== i",
  "both directional ratio tests"
]) {
  if (!source.includes(feature)) throw new Error(`Keyframe correspondence feature missing: ${feature}`);
}

for (const locale of ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]) {
  if (!source.includes(`${locale}: {`)) throw new Error(`Keyframe correspondence locale missing: ${locale}`);
}

const unique = api.correspondenceDistribution(
  [[0], [10], [20]],
  [[0.01], [10.01], [20.01]]
);
assert.equal(unique.candidates, 3, "All three distinctive forward candidates should pass");
assert.equal(unique.count, 3, "Distinctive reciprocal matches should be retained");
assert.equal(unique.dx, 0);
assert.equal(unique.dy, 0);
assert.equal(unique.spread, 0);

const duplicate = api.correspondenceDistribution(
  [[0], [0.02], [10]],
  [[0.01], [10.01]]
);
assert.equal(duplicate.candidates, 3, "The fixture should expose three one-way candidates");
assert.equal(duplicate.count, 1, "A many-to-one ambiguity must not be counted as reciprocal");
assert.ok(duplicate.count < duplicate.candidates);

assert.deepEqual(Array.from(api.nearestMatches([[0]], [[0.1]])), [-1],
  "A single possible target cannot pass a two-neighbour ratio test");
const insufficient = api.correspondenceDistribution([[0]], [[0.1]]);
assert.equal(insufficient.count, 0);
assert.equal(insufficient.dx, null);
assert.equal(insufficient.dy, null);
assert.equal(insufficient.spread, null);
assert.equal(api.median([]), null);
assert.ok(Math.abs(api.distance([0, 0], [3, 4]) - Math.sqrt(12.5)) < 1e-12);

console.log("Validated reciprocal one-to-one keyframe matching, ambiguity rejection, empty-sample handling and 15 locales.");
