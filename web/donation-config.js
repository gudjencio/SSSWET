/* Public payment destinations. No private credentials belong in this file. */
window.SSSWET_DONATION_LINKS = {
  PAYPAL_CLIENT_ID: "ATI2NOt8eqI1RNJFG_s8e1id5ODtJcqJ8WPSgMuASmk6mJqqiUmxSnuNBUGBGA0ZWZw8lJxRfQ-zZ5Qt",
  PAYPAL_SUBSCRIPTION_PLAN_ID: "P-75A66386EX5825057NLTZHII"
};

/* Load small public UI modules without requiring another HTML edit. */
["research-equations.js"].forEach(src => {
  if (document.querySelector('script[src="' + src + '"]')) return;
  const script = document.createElement("script");
  script.src = src;
  script.defer = true;
  document.head.appendChild(script);
});

/* Public portfolio state. Unknown financial figures intentionally remain null. */
const ssswetTechnologyKeys = [
  "cellular","longevity","armor","jetpack","translator","spacetime","timetravel",
  "cleanenergy","energyStorage","water","foodSystems","climate","biodiversity","wildlife",
  "oceans","reforestation","agriculture","circularEconomy","airQuality","mobility","accessibility",
  "disasterResilience","publicHealth","sanitation","education","animalHealth","materials",
  "carbonMonitoring","pollinators","artificialGravity","medicalNanotechnology","atmosphericRestoration","neurointerfaces","quantumNetworks","fusionEnergy","spaceLifeSupport","autonomousLabs","roboticsExoskeletons","planetaryMonitoring","advancedComputing"
];
window.SSSWET_RESEARCH_PORTFOLIO = Object.fromEntries(
  ssswetTechnologyKeys.map(key => [key, {
    funding_goal_eur: null,
    confirmed_contributions_eur: null,
    stage: "planning",
    prototype: false,
    availability: "not_available",
    last_updated: null
  }])
);

document.addEventListener("DOMContentLoaded", () => {
  const projectUrl = "https://gudjencio.github.io/SSSWET/";
  const MIN_CONTRIBUTION_USD = 1;
  const language = () => String(document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const copy = {
    en: {
      repair: "Repair if broken",
      title: "Select and buy any tech",
      intro: "Explore the research directions and choose the technology you want to order.",
      explore: "Select and buy",
    },
    fr: {
      repair: "Relancer le projet, s’il est cassé",
      title: "Choisissez et commandez la technologie de votre choix",
      intro: "Explorez les axes de recherche et choisissez la technologie que vous souhaitez commander.",
      explore: "Choisir et commander",
    }
  };
  const current = () => copy[language()] || copy.en;

  if (!document.getElementById("repair-project-button")) {
    const slot = document.createElement("div");
    slot.className = "repair-project-slot";
    const button = document.createElement("a");
    button.id = "repair-project-button";
    button.className = "repair-project-button";
    button.href = projectUrl;
    button.target = "_blank";
    button.rel = "noopener noreferrer";
    slot.append(button);
    const shell = document.querySelector(".app-shell");
    const topbar = shell?.querySelector(".topbar");
    if (shell && topbar) shell.insertBefore(slot, topbar);
    else document.body.prepend(slot);
  }

  const apply = () => {
    const c = current();
    const repair = document.getElementById("repair-project-button");
    if (repair) {
      repair.textContent = c.repair;
      repair.setAttribute("aria-label", c.repair);
    }
    const title = document.getElementById("technology-title");
    const intro = document.querySelector('.technology-heading [data-tech-copy="intro"]');
    if (title) title.textContent = c.title;
    if (intro) intro.textContent = c.intro;
    document.querySelectorAll("#technology-grid .technology-card").forEach(card => {
      const button = card.querySelector("button[data-tech]");
      if (button && !button.dataset.newTech) button.textContent = c.explore;
    });

    const amount = document.getElementById("donation-amount");
    if (amount) {
      amount.min = String(MIN_CONTRIBUTION_USD);
      amount.value = String(Math.max(MIN_CONTRIBUTION_USD, Number(amount.value) || 0));
      amount.step = "0.01";
    }

    const minimumNote = document.getElementById("donation-minimum-note");
    if (minimumNote) minimumNote.textContent = language() === "fr"
      ? "Contribution minimale : 1 dollar américain. Le montant choisi est transmis à PayPal avant validation."
      : "Minimum contribution: USD 1. The selected amount is sent to PayPal for approval.";
  };

  apply();
  window.addEventListener("ssswet-language-changed", apply);
  document.getElementById("language")?.addEventListener("change", () => window.setTimeout(apply, 0));
});
