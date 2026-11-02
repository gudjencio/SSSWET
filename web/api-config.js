/* Public API endpoint for the hosted research service. */
window.SSSWET_REMOTE_API_BASE = "https://ssswet-research-api.onrender.com";

// Load the public-facing bot personality layer before the main interface scripts.
(() => {
  const script = document.createElement("script");
  script.src = "bot-personality.js";
  script.defer = false;
  document.head.appendChild(script);
})();
