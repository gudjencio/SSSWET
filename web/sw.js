const CACHE = "ssswet-web-v52";
const ASSETS = ["./", "./index.html", "./styles.css", "./locales.js", "./app.js", "./donation-config.js", "./product-purchase-config.js", "./donation.js", "./evidence-center.js", "./evidence-center.css", "./parameter-sensitivity.js", "./parameter-sensitivity.css", "./lab-statistics.js", "./evidence-graph.js", "./evidence-graph.css", "./lab-discrepancies.js", "./lab-discrepancies.css", "./research-journal.js", "./research-journal.css", "./technology-feasibility.js", "./technology-feasibility.css", "./mobile-repair.css", "./repair-project.js", "./manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

async function repairIndexResponse(response) {
  if (!response || !response.ok) return response;
  const html = await response.text();
  const stylesheet = '<link rel="stylesheet" href="mobile-repair.css">';
  const repairSlot = '<div class="repair-project-slot"><a id="repair-project-button" class="repair-project-button" href="https://gudjencio.github.io/SSSWET/" target="_blank" rel="noopener noreferrer">Repair project if broken</a></div>';
  const script = '<script src="repair-project.js"></script>';
  const withStyles = html.includes('href="mobile-repair.css"') ? html : html.replace('</head>', `${stylesheet}\n</head>`);
  const withButton = withStyles.includes('id="repair-project-button"')
    ? withStyles
    : withStyles.replace('<header class="topbar">', `<header class="topbar">${repairSlot}`);
  const withScript = withButton.includes('src="repair-project.js"')
    ? withButton
    : withButton.replace('</body>', `${script}\n</body>`);
  const headers = new Headers(response.headers);
  headers.delete("content-length");
  return new Response(withScript, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const requestUrl = new URL(event.request.url);
  const isNavigation = event.request.mode === "navigate" || requestUrl.pathname.endsWith("/index.html");
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const responsePromise = cached || fetch(event.request);
      return isNavigation ? responsePromise.then(repairIndexResponse) : responsePromise;
    })
  );
});
