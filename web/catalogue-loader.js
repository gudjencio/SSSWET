(() => {
  "use strict";

  const loaderScript = document.currentScript;
  const catalogueUrl = new URL("technology-expansion-ui.js", loaderScript.src);
  const categoryUrl = new URL("technology-categories.js", loaderScript.src);
  const timing = {
    scheduledAt: performance.now(),
    startedAt: null,
    completedAt: null,
    loaded: false
  };
  window.SSSWET_CATALOGUE_TIMING = timing;

  let resolveReady;
  window.SSSWET_CATALOGUE_READY = new Promise(resolve => {
    resolveReady = resolve;
  });

  function finish(loaded) {
    timing.completedAt = performance.now();
    timing.loaded = loaded;
    window.SSSWET_CATALOGUE_LOADED = loaded;
    const detail = { loaded, durationMs: timing.completedAt - timing.startedAt };
    window.dispatchEvent(new CustomEvent("ssswet-catalogue-ready", { detail }));
    resolveReady(detail);
    const categoryScript = document.createElement("script");
    categoryScript.src = categoryUrl.href;
    categoryScript.async = true;
    document.head.appendChild(categoryScript);
  }

  function loadCatalogue() {
    if (timing.startedAt !== null) return;
    timing.startedAt = performance.now();
    const script = document.createElement("script");
    script.src = catalogueUrl.href;
    script.async = true;
    script.onload = () => finish(true);
    script.onerror = () => finish(false);
    document.head.appendChild(script);
  }

  // Let the browser paint the initial interface before parsing the large
  // generated research catalogue. The timeout prevents indefinite idle waits.
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      if (typeof window.requestIdleCallback === "function") {
        window.requestIdleCallback(loadCatalogue, { timeout: 1500 });
      } else {
        window.setTimeout(loadCatalogue, 0);
      }
    });
  });
})();
