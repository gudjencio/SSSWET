(() => {
  "use strict";

  if (!("serviceWorker" in navigator)) return;

  const banner = document.getElementById("ssswet-update-banner");
  const message = document.getElementById("ssswet-update-message");
  const action = document.getElementById("ssswet-update-action");
  if (!banner || !message || !action) return;

  const isFrench = () => (document.getElementById("language")?.value || document.documentElement.lang || navigator.language || "en").toLowerCase().startsWith("fr");
  const copy = () => isFrench()
    ? { ready: "Une nouvelle version de SSSWET est prête.", button: "Actualiser", updating: "Mise à jour en cours…" }
    : { ready: "A new version of SSSWET is ready.", button: "Refresh now", updating: "Updating…" };

  let waitingWorker = null;
  let refreshing = false;
  let hadController = Boolean(navigator.serviceWorker.controller);

  function showUpdate(worker) {
    waitingWorker = worker;
    const words = copy();
    message.textContent = words.ready;
    action.textContent = words.button;
    action.disabled = false;
    banner.hidden = false;
  }

  action.addEventListener("click", () => {
    if (!waitingWorker) return;
    action.disabled = true;
    message.textContent = copy().updating;
    waitingWorker.postMessage({ type: "SSSWET_SKIP_WAITING" });
  });

  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  async function registerUpdates() {
    try {
      const registration = await navigator.serviceWorker.register("./sw.js");
      if (registration.waiting && navigator.serviceWorker.controller) showUpdate(registration.waiting);

      registration.addEventListener("updatefound", () => {
        const installing = registration.installing;
        if (!installing) return;
        installing.addEventListener("statechange", () => {
          if (installing.state === "installed" && navigator.serviceWorker.controller) {
            showUpdate(registration.waiting || installing);
          }
        });
      });

      window.addEventListener("online", () => registration.update().catch(() => {}));
      document.getElementById("language")?.addEventListener("change", () => {
        if (waitingWorker && !banner.hidden) {
          const words = copy();
          message.textContent = words.ready;
          action.textContent = words.button;
        }
      });
    } catch (_) {
      // The web experience remains usable if offline installation is unavailable.
    }
  }

  if (document.readyState === "complete") registerUpdates();
  else window.addEventListener("load", registerUpdates, { once: true });
})();