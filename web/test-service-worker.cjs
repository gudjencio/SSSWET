/* Verify the offline shell references real, deployable files. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const root = __dirname;
const sw = fs.readFileSync(path.join(root, "sw.js"), "utf8");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const version = sw.match(/const CACHE = "([^"]+)"/)?.[1];
if (!version || !/^ssswet-web-v\d+$/.test(version)) throw new Error("Invalid service-worker cache version");

function quotedPaths(source, pattern) {
  return [...source.matchAll(pattern)].map((match) => match[1]);
}
const precache = quotedPaths(sw, /"(\.\/(?:[^"\\]+))"/g)
  .filter((value) => value !== "./");
const htmlAssets = quotedPaths(html, /(?:src|href)="(?!https?:|mailto:|#)([^"]+\.(?:js|css))"/g);
const paths = [...new Set([...precache, ...htmlAssets])];
const missing = paths.filter((asset) => !fs.existsSync(path.join(root, asset.replace(/^\.\//, ""))));
if (missing.length) throw new Error("Missing local interface assets: " + missing.join(", "));
if (!sw.includes('request.mode === "navigate"') || !sw.includes('request.destination')) {
  throw new Error("Navigation/script/style network refresh strategy is missing");
}
if (!sw.includes("Promise.allSettled")) throw new Error("Optional precache must tolerate an unavailable enhancement");
console.log(`Service worker ${version}: ${paths.length} local assets verified; no missing references.`);
