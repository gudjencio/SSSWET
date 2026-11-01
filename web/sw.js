const CACHE = "ssswet-web-v27";
const ASSETS = ["./", "./index.html", "./styles.css", "./locales.js", "./app.js", "./evidence-center.js", "./evidence-center.css", "./evidence-graph.js", "./evidence-graph.css", "./lab-discrepancies.js", "./lab-discrepancies.css", "./manifest.json"];

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
