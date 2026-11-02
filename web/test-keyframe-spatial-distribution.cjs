const fs = require("fs");
const vm = require("vm");
const path = require("path");

const source = fs.readFileSync(path.join(__dirname, "keyframe-correspondence.js"), "utf8");
new vm.Script(source, { filename: "keyframe-correspondence.js" });

const required = [
  "correspondenceDistribution",
  "spatial distribution",
  "distribution spatiale",
  "Math.min(3, Math.floor(ax / 3))",
  "occupiedA",
  "occupiedB",
  "coverage",
  "camera poses",
  "3D overlap"
];

for (const marker of required) {
  if (!source.includes(marker)) throw new Error(`Missing spatial-distribution marker: ${marker}`);
}

for (const locale of ["en", "fr", "es", "de", "it", "pt", "nl", "ru", "uk", "ar", "he", "ja", "ko", "zh", "hi"]) {
  const block = source.match(new RegExp(`\\n    ${locale}: \\{[^\\n]+`));
  if (!block) throw new Error(`Missing locale block: ${locale}`);
}

console.log("keyframe spatial distribution source checks passed");
