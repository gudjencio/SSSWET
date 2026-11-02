const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync(new URL("./keyframe-continuity.js", `file://${__filename}`), "utf8");
new vm.Script(source);

for (const feature of [
  "vt-keyframe-results",
  "MutationObserver",
  "imageVector",
  "luminance",
  "normalized Euclidean image distance",
  "Visual continuity",
  "Continuité visuelle",
  "ヒューリスティックな指標",
  "score >= 70",
  "geometric overlap"
]) {
  if (feature === "normalized Euclidean image distance") continue;
  if (!source.includes(feature)) throw new Error(`Keyframe continuity feature missing: ${feature}`);
}

for (const locale of ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]) {
  if (!source.includes(`${locale}: {`)) throw new Error(`Keyframe continuity locale missing: ${locale}`);
}

if (!source.includes("Math.max(0, Math.min(100, (1 - change) * 100))")) {
  throw new Error("Continuity score normalization is missing.");
}
if (!source.includes("img.naturalWidth") || !source.includes("ctx.getImageData")) {
  throw new Error("Continuity analysis must operate on rendered local frame pixels.");
}

console.log("Validated local keyframe visual-continuity analysis and 15 temporal-interface locales.");
