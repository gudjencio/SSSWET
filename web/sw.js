/* SSSWET web shell: versioned cache, safe partial precache and network-first updates. */
"use strict";

const CACHE = "ssswet-web-v199";
const CORE_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./locales.js",
  "./core-ui-locales.js",
  "./api-config.js"
];
const OPTIONAL_ASSETS = [
  "./mobile-repair.css",
  "./evidence-center.css",
  "./research-journal.css",
  "./parameter-sensitivity.css",
  "./evidence-graph.css",
  "./lab-discrepancies.css",
  "./technology-supercategories.css",
  "./bot-control-center.js",
  "./bot-live-room.js",
  "./bot-personality.js",
  "./service-worker-updates.js",
  "./platform-downloads.js",
  "./version-center.js",
  "./research-equations.js",
  "./product-purchase-config.js",
  "./donation-config.js",
  "./new-technology-copy.js",
  "./technology-expansion-ui.js",
  "./donation.js",
  "./technology-categories.js",
  "./technology-supercategories-data.js",
  "./technology-supercategories.js",
  "./evidence-center.js",
  "./research-journal.js",
  "./technology-feasibility.js",
  "./lab-statistics.js",
  "./parameter-sensitivity.js",
  "./evidence-graph.js",
  "./lab-discrepancies.js",
  "./interface-localization.js",
  "./virtual-time-travel-link.js",
  "./top-action-links.js",
  "./read-aloud.js",
  "./repair-project.js",
  "./report-project.js",
  "./language-center.css",
  "./ui-enhancements.js",
  "./platform-routing.js",
  "./catalogue-500-ui.js",
  "./manifest.json",
  "./virtual-time-travel.html",
  "./virtual-time-travel.css",
  "./virtual-time-travel.js",
  "./clock-alignment-workspace.js",
  "./keyframe-continuity.js",
  "./keyframe-correspondence.js",
  "./temporal-clock.js",
  "./gps-scenario-model.js",
  "./icons/ssswet-icon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Core shell failures must stop installation; optional modules must not
    // make the entire application unavailable because one enhancement is absent.
    await cache.addAll(CORE_ASSETS);
    await Promise.allSettled(OPTIONAL_ASSETS.map((asset) => cache.add(asset)));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((key) => key.startsWith("ssswet-web-") && key !== CACHE)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const refreshable = request.mode === "navigate" ||
    ["script", "style"].includes(request.destination);

  if (refreshable) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request, { cache: "no-store" });
        if (response && response.ok) {
          const cache = await caches.open(CACHE);
          await cache.put(request, response.clone());
        }
        return response;
      } catch (_) {
        const cached = await caches.match(request);
        if (cached) return cached;
        if (request.mode === "navigate") {
          const shell = await caches.match("./index.html");
          if (shell) return shell;
        }
        return Response.error();
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
      const response = await fetch(request);
      if (response && response.ok && response.type === "basic") {
        const cache = await caches.open(CACHE);
        await cache.put(request, response.clone());
      }
      return response;
    } catch (_) {
      return Response.error();
    }
  })());
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SSSWET_SKIP_WAITING") self.skipWaiting();
});
