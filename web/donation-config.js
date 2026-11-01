/* Public payment destination. No private credentials belong in this file. */
window.SSSWET_DONATION_LINKS = {
  PAYPAL: "https://www.paypal.com/paypalme/gudjencio"
};

/* Public portfolio state. Unknown financial figures intentionally remain null. */
const ssswetTechnologyKeys = [
  "cellular","longevity","armor","jetpack","translator","spacetime","timetravel",
  "cleanenergy","energyStorage","water","foodSystems","climate","biodiversity","wildlife",
  "oceans","reforestation","agriculture","circularEconomy","airQuality","mobility","accessibility",
  "disasterResilience","publicHealth","sanitation","education","animalHealth","materials",
  "carbonMonitoring","pollinators","artificialGravity","medicalNanotechnology","atmosphericRestoration"
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
  const language = () => String(document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const copy = {
    en: {
      repair: "Repair if broken",
      title: "Select and buy any tech",
      intro: "Explore the research directions and choose the technology you want to order.",
      explore: "Select and buy",
      newTechs: [
        ["artificialGravity", "Artificial gravity research", "Research into controllable gravity-like effects, inertial management and safe theoretical models."],
        ["medicalNanotechnology", "Medical nanotechnology", "Research into nanoscale medical tools for targeted diagnostics, monitoring and future therapeutic applications."],
        ["atmosphericRestoration", "Atmospheric restoration", "Research into measurable atmospheric recovery, pollution reduction and resilient air-quality systems."]
      ]
    },
    fr: {
      repair: "Relancer le projet, s’il est cassé",
      title: "Choisissez et commandez la technologie de votre choix",
      intro: "Explorez les axes de recherche et choisissez la technologie que vous souhaitez commander.",
      explore: "Choisir et commander",
      newTechs: [
        ["artificialGravity", "Recherche sur la gravité artificielle", "Recherche sur des effets assimilables à la gravité contrôlée, la gestion de l’inertie et des modèles théoriques sûrs."],
        ["medicalNanotechnology", "Nanotechnologies médicales", "Recherche sur des outils médicaux à l’échelle nanométrique pour le diagnostic ciblé, le suivi et de futures applications thérapeutiques."],
        ["atmosphericRestoration", "Restauration atmosphérique", "Recherche sur la restauration mesurable de l’atmosphère, la réduction de la pollution et des systèmes résilients de qualité de l’air."]
      ]
    }
  };
  const current = () => copy[language()] || copy.en;

  /* Recovery button: always visible, always opens the canonical public project. */
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

    c.newTechs.forEach(item => {
      let card = document.querySelector('#technology-grid .technology-card[data-extension-tech="' + item[0] + '"]');
      if (!card) {
        card = document.createElement("article");
        card.className = "technology-card";
        card.dataset.extensionTech = item[0];
        const number = document.createElement("span");
        number.className = "technology-number";
        number.textContent = String(document.querySelectorAll("#technology-grid .technology-card").length + 1).padStart(2, "0");
        const heading = document.createElement("h3");
        const description = document.createElement("p");
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.newTech = item[0];
        button.addEventListener("click", () => {
          const dialog = document.getElementById("technology-dialog");
          const dialogTitle = document.getElementById("technology-dialog-title");
          const dialogDescription = document.getElementById("technology-dialog-description");
          if (!dialog || !dialogTitle || !dialogDescription) return;
          dialogTitle.textContent = item[1];
          dialogDescription.textContent = item[2];
          if (typeof dialog.showModal === "function") dialog.showModal();
          else dialog.setAttribute("open", "");
        });
        card.append(number, heading, description, button);
        document.getElementById("technology-grid")?.append(card);
      }
      card.querySelector("h3").textContent = item[1];
      card.querySelector("p").textContent = item[2];
      card.querySelector("button[data-new-tech]").textContent = c.explore;
    });
  };

  apply();
  window.addEventListener("ssswet-language-changed", apply);
  document.getElementById("language")?.addEventListener("change", () => window.setTimeout(apply, 0));
});
