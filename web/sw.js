const CACHE = "ssswet-web-v193";
const ASSETS = ["./", "./index.html", "./styles.css", "./bot-control-center.js", "./bot-live-room.js", "./bot-personality.js", "./locales.js", "./core-ui-locales.js", "./api-config.js", "./app.js", "./donation-config.js", "./payment-enhancement.js", "./research-equations.js", "./product-purchase-config.js", "./donation.js", "./new-technology-copy.js", "./technology-expansion-ui.js", "./technology-categories.js", "./interface-localization.js", "./evidence-center.js", "./evidence-center.css", "./parameter-sensitivity.js", "./parameter-sensitivity.css", "./lab-statistics.js", "./evidence-graph.js", "./evidence-graph.css", "./lab-discrepancies.js", "./lab-discrepancies.css", "./research-journal.js", "./research-journal.css", "./technology-feasibility.js", "./technology-feasibility.css", "./mobile-repair.css", "./repair-project.js", "./report-project.js", "./manifest.json", "./platform-downloads.js", "./version-center.js", "./service-worker-updates.js", "./language-center.css", "./ui-enhancements.js", "./platform-routing.js", "./catalogue-500-ui.js", "./virtual-time-travel.html", "./virtual-time-travel.css", "./virtual-time-travel.js", "./keyframe-continuity.js", "./keyframe-correspondence.js", "./temporal-clock.js", "./gps-scenario-model.js", "./virtual-time-travel-link.js", "./top-action-links.js", "./read-aloud.js", "./icons/ssswet-icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SSSWET_SKIP_WAITING") self.skipWaiting();
});
