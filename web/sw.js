const CACHE = "ssswet-web-v89";
const ASSETS = ["./", "./index.html", "./styles.css", "./bot-control-center.js", "./bot-live-room.js", "./locales.js", "./app.js", "./donation-config.js", "./payment-enhancement.js", "./research-equations.js", "./product-purchase-config.js", "./donation.js", "./evidence-center.js", "./evidence-center.css", "./parameter-sensitivity.js", "./parameter-sensitivity.css", "./lab-statistics.js", "./evidence-graph.js", "./evidence-graph.css", "./lab-discrepancies.js", "./lab-discrepancies.css", "./research-journal.js", "./research-journal.css", "./technology-feasibility.js", "./technology-feasibility.css", "./mobile-repair.css", "./repair-project.js", "./manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});
