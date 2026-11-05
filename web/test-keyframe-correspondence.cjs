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
  "both directional ratio tests",
  "shouldRefreshFromMutations",
  "isRelevantImageLoad",
  "attributeFilter: [\"src\"]",
  "root.addEventListener(\"load\""
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


const makeElement = ({ kind = "other", insideCard = false, descendants = [] } = {}) => ({
  nodeType: 1,
  matches(selector) {
    if (selector === ".vt-keyframe-card") return kind === "card";
    if (selector === ".vt-keyframe-card img") return kind === "image" && insideCard;
    if (selector === "img") return kind === "image";
    return false;
  },
  closest(selector) {
    return selector === ".vt-keyframe-card" && (kind === "card" || insideCard)
      ? { nodeType: 1, matches: value => value === ".vt-keyframe-card" }
      : null;
  },
  querySelector(selector) {
    return descendants.find(node => node.matches(selector)) || null;
  }
});
const cardNode = makeElement({ kind: "card" });
const imageNode = makeElement({ kind: "image", insideCard: true });
const diagnosticNode = makeElement();
assert.equal(api.isRelevantImageLoad(imageNode), true,
  "A loaded keyframe preview image must trigger a refresh");
assert.equal(api.isRelevantImageLoad(diagnosticNode), false,
  "Non-image UI elements must not trigger an image refresh");
assert.equal(api.shouldRefreshFromMutations([
  { type: "childList", target: { nodeType: 1 }, addedNodes: [cardNode], removedNodes: [] }
]), true, "Adding a keyframe card must trigger a refresh");
assert.equal(api.shouldRefreshFromMutations([
  { type: "childList", target: cardNode, addedNodes: [imageNode], removedNodes: [] }
]), true, "Adding an image inside a keyframe card must trigger a refresh");
assert.equal(api.shouldRefreshFromMutations([
  { type: "childList", target: cardNode, addedNodes: [diagnosticNode], removedNodes: [] }
]), false, "Adding the matcher's own diagnostic UI must not trigger another render");
assert.equal(api.shouldRefreshFromMutations([
  { type: "childList", target: { nodeType: 1 }, addedNodes: [diagnosticNode], removedNodes: [] }
]), false, "Adding an explanatory note must not trigger a render");
assert.equal(api.shouldRefreshFromMutations([
  { type: "attributes", target: imageNode, attributeName: "src" }
]), true, "Changing a keyframe image source must trigger a refresh");
assert.equal(api.shouldRefreshFromMutations([
  { type: "attributes", target: imageNode, attributeName: "alt" }
]), false, "Unrelated image attributes must not trigger a refresh");
assert.equal(api.shouldRefreshFromMutations([
  { type: "characterData", target: diagnosticNode }
]), false, "Text-only diagnostic changes must not trigger a refresh");

let observerCallback = null;
let observerOptions = null;
let scheduledFrames = [];
let loadHandler = null;
let staleDiagnosticRemoved = false;
const staleDiagnostic = { nodeType: 1, remove() { staleDiagnosticRemoved = true; } };
const runtimeRoot = {
  querySelectorAll(selector) {
    if (selector === ".vt-keyframe-card img") return [imageNode];
    if (selector.includes(".vt-keyframe-correspondence")) return [staleDiagnostic];
    return [];
  },
  addEventListener(type, handler, capture) {
    if (type === "load" && capture === true) loadHandler = handler;
  }
};
class TestMutationObserver {
  constructor(callback) { observerCallback = callback; }
  observe(target, options) {
    assert.equal(target, runtimeRoot);
    observerOptions = options;
  }
}
const runtimeSandbox = {
  document: { getElementById: id => id === "vt-keyframe-results" ? runtimeRoot : null },
  window: {},
  MutationObserver: TestMutationObserver,
  requestAnimationFrame(callback) {
    scheduledFrames.push(callback);
    return scheduledFrames.length;
  }
};
vm.runInNewContext(source, runtimeSandbox);
assert.ok(observerCallback, "The source observer must be installed");
assert.equal(observerOptions.childList, true);
assert.equal(observerOptions.subtree, true);
assert.equal(observerOptions.attributes, true);
assert.deepEqual(Array.from(observerOptions.attributeFilter), ["src"]);
assert.equal(scheduledFrames.length, 1, "Initial render should be coalesced into one animation frame");
scheduledFrames.shift()();
assert.equal(staleDiagnosticRemoved, true,
  "Stale diagnostics must be cleared even when fewer than two keyframes remain");
observerCallback([{
  type: "childList",
  target: runtimeRoot,
  addedNodes: [diagnosticNode],
  removedNodes: [staleDiagnostic]
}]);
assert.equal(scheduledFrames.length, 0,
  "The observer must ignore its own output and avoid a self-triggered render loop");
observerCallback([{
  type: "childList",
  target: runtimeRoot,
  addedNodes: [cardNode],
  removedNodes: []
}]);
assert.equal(scheduledFrames.length, 1,
  "A new keyframe card should schedule a single refresh");
scheduledFrames.shift()();
loadHandler({ target: imageNode });
assert.equal(scheduledFrames.length, 1,
  "A completed image load should schedule a refresh after pixels become readable");

console.log("Validated deterministic matching, observer lifecycle, bounded refresh scheduling, stale-output cleanup and 15 locales.");
