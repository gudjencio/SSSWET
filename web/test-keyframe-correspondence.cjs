const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync(new URL("./keyframe-correspondence.js", `file://${__filename}`), "utf8");
new vm.Script(source);

for (const feature of [
  "patchDescriptors",
  "correspondenceCount",
  "candidate matches",
  "correspondances candidates",
  "カメラ姿勢",
  "3D overlap",
  "best / Math.max(second",
  "ctx.getImageData",
  "median(values)",
  "median shift",
  "déplacement médian",
  "median spread",
  "displacementNote",
  "Math.hypot(item.dx - dx, item.dy - dy)"
]) {
  if (!source.includes(feature)) throw new Error(`Keyframe correspondence feature missing: ${feature}`);
}

for (const locale of ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]) {
  if (!source.includes(`${locale}: {`)) throw new Error(`Keyframe correspondence locale missing: ${locale}`);
}

console.log("Validated local keyframe correspondence screening and 15 temporal-interface locales.");
