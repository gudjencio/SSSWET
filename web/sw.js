/* SSSWET public-site service worker.
 * Network-first prevents an old cached shell from masking a published update.
 * The complete offline asset set is retained for disconnected visitors.
 */
"use strict";

const CACHE = "ssswet-web-v191";
const ASSETS = ["./", "./index.html", "./styles.css", "./bot-control-center.js", "./bot-live-room.js", "./bot-personality.js", "./locales.js", "./core-ui-locales.js", "./api-config.js", "./app.js", "./donation-config.js", "./payment-enhancement.js", "./research-equations.js", "./product-purchase-config.js", "./donation.js", "./new-technology-copy.js", "./technology-expansion-ui.js", "./technology-categories.js", "./interface-localization.js", "./evidence-center.js", "./evidence-center.css", "./parameter-sensitivity.js", "./parameter-sensitivity.css", "./lab-statistics.js", "./evidence-graph.js", "./evidence-graph.css", "./lab-discrepancies.js", "./lab-discrepancies.css", "./research-journal.js", "./research-journal.css", "./technology-feasibility.js", "./technology-feasibility.css", "./mobile-repair.css", "./repair-project.js", "./report-project.js", "./manifest.json", "./platform-downloads.js", "./version-center.js", "./service-worker-updates.js", "./language-center.css", "./ui-enhancements.js", "./platform-routing.js", "./catalogue-500-ui.js", "./virtual-time-travel.html", "./virtual-time-travel.css", "./virtual-time-travel.js", "./keyframe-continuity.js", "./keyframe-correspondence.js", "./virtual-time-travel-link.js", "./top-action-links.js", "./read-aloud.js", "./icons/ssswet-icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Keep the full offline asset set, but fetch entries independently so one
    // missing optional file cannot block installation of the new worker.
    await Promise.allSettled(ASSETS.map(async (asset) => {
      const response = await fetch(new Request(asset, { cache: "reload" }));
      if (response.ok) await cache.put(asset, response);
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((key) => key.startsWith("ssswet-web-") && key !== CACHE)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      // Always ask the deployed origin first. Old cached scripts/styles must
      // not silently override a newly published version.
      const response = await fetch(request);
      if (response && response.ok && response.type !== "opaque") {
        await cache.put(request, response.clone());
      }
      return response;
    } catch (error) {
      const cached = await cache.match(request, { ignoreSearch: false });
      if (cached) return cached;
      if (request.mode === "navigate") {
        const shell = await cache.match("./index.html");
        if (shell) return shell;
      }
      throw error;
    }
  })());
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SSSWET_SKIP_WAITING") self.skipWaiting();
});
