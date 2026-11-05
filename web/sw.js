/* SSSWET public-site service worker.
 * Network-first prevents an old cached shell from masking a published update.
 * Cached responses remain available as an offline fallback.
 */
"use strict";

const CACHE = "ssswet-web-v191";
const CORE_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./locales.js"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Cache each core asset independently: one optional/transient failure must
    // not strand visitors on the previous worker version.
    await Promise.allSettled(CORE_ASSETS.map(async (asset) => {
      const response = await fetch(new Request(asset, { cache: "reload" }));
      if (response.ok) await cache.put(asset, response);
    }));
    // Activate the tested successor promptly instead of waiting indefinitely
    // for every tab using the previous worker to close.
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
      // Always ask the deployed origin first. This is essential for HTML,
      // scripts and styles: an old cached file must never silently win.
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
  if (event.data && event.data.type === "SSSWET_SKIP_WAITING") {
    self.skipWaiting();
  }
});
