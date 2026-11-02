(() => {
  "use strict";

  const FR_TECH = {
    "Spacetime": "Espace-temps", "Timetravel": "Voyage temporel", "Artificial Gravity": "Gravité artificielle",
    "Planetary Monitoring": "Surveillance planétaire", "Black Hole Observation": "Observation des trous noirs", "Black Hole Probe Systems": "Systèmes de sondes pour trous noirs",
    "Black Hole Resilient Vehicles": "Véhicules résistants aux environnements de trous noirs", "Event Horizon Imaging": "Imagerie des horizons des événements",
    "Gravitational Wave Navigation": "Navigation par ondes gravitationnelles", "Relativistic Spacecraft": "Vaisseaux spatiaux relativistes",
    "Jetpack": "Système de propulsion individuel", "Antimatter Research": "Recherche sur l'antimatière", "Beamed Energy Propulsion": "Propulsion par énergie dirigée",
    "Solar Sail Navigation": "Navigation par voile solaire", "Plasma Propulsion": "Propulsion plasma", "Interstellar Probe Architecture": "Architecture de sondes interstellaires",
    "Space Life Support": "Support-vie spatial", "Deep Space Radiation Shelters": "Abris contre les rayonnements de l'espace profond", "Cosmic Ray Shielding": "Blindage contre les rayons cosmiques",
    "Cryogenic Hibernation": "Hibernation cryogénique", "Orbital Manufacturing": "Fabrication orbitale", "Lunar Resource Systems": "Systèmes de ressources lunaires",
    "Mars Terraforming Assessment": "Évaluation de la terraformation de Mars", "Nuclear Blast Resilience": "Résilience aux effets d'une explosion nucléaire", "Radiation Protection": "Protection contre les rayonnements",
    "Radiation Dosimetry Networks": "Réseaux de dosimétrie des rayonnements", "Nuclear Fallout Decontamination": "Décontamination des retombées nucléaires",
    "Electromagnetic Pulse Resilience": "Résilience aux impulsions électromagnétiques", "Armor": "Protection corporelle", "Disaster Resilience": "Résilience aux catastrophes",
    "Extreme Thermal Protection": "Protection thermique extrême", "Impact Absorbing Materials": "Matériaux absorbant les impacts", "Cleanenergy": "Énergie propre", "Fusion Energy": "Énergie de fusion",
    "Superconducting Grid": "Réseau supraconducteur", "Ambient Energy Harvesting": "Récupération d'énergie ambiante", "Space Solar Power": "Énergie solaire spatiale",
    "Zero Carbon Industrial Heat": "Chaleur industrielle sans carbone", "Energy Storage": "Stockage de l'énergie", "Thermoelectric Systems": "Systèmes thermoélectriques",
    "Grid Scale Thermal Storage": "Stockage thermique à l'échelle du réseau", "Materials": "Matériaux avancés", "Metamaterials": "Métamatériaux", "Self Healing Materials": "Matériaux autoréparants",
    "Aerogel Systems": "Systèmes à base d'aérogel", "Smart Adaptive Materials": "Matériaux adaptatifs intelligents", "Circular Economy": "Économie circulaire",
    "Ultra High Temperature Materials": "Matériaux à ultra-haute température", "Transparent Ceramics": "Céramiques transparentes", "Cellular Reinforcement, Repair and Recovery": "Renforcement, réparation et récupération cellulaires",
    "Longevity": "Longévité en bonne santé", "Medical Nanotechnology": "Nanotechnologies médicales", "Organ Regeneration": "Régénération des organes",
    "Synthetic Biology Biosafety": "Biosécurité de la biologie synthétique", "Precision Gene Therapies": "Thérapies géniques de précision", "Bioelectronic Medicine": "Médecine bioélectronique",
    "Artificial Organs": "Organes artificiels", "Medical Digital Twins": "Jumeaux numériques médicaux", "Neurointerfaces": "Neurointerfaces", "Robotics Exoskeletons": "Exosquelettes robotiques",
    "Sensory Augmentation": "Augmentation sensorielle", "Adaptive Exosuits": "Exosuits adaptatifs", "Animal Health": "Santé animale", "Climate": "Climat", "Biodiversity": "Biodiversité",
    "Wildlife": "Protection de la faune", "Oceans": "Océans", "Reforestation": "Reboisement", "Agriculture": "Agriculture", "Carbon Monitoring": "Surveillance du carbone",
    "Pollinators": "Protection des pollinisateurs", "Atmospheric Restoration": "Restauration atmosphérique", "Carbon Removal": "Élimination du carbone", "Ocean Alkalinity Monitoring": "Surveillance de l'alcalinité des océans",
    "Geoengineering Assessment": "Évaluation de la géo-ingénierie", "Ecosystem Digital Twins": "Jumeaux numériques des écosystèmes", "Air Quality": "Qualité de l'air", "Water": "Eau",
    "Food Systems": "Systèmes alimentaires", "Sanitation": "Assainissement", "Wildfire Prediction": "Prévision des incendies de forêt", "Autonomous Labs": "Laboratoires autonomes",
    "Swarm Robotics": "Robotique en essaim", "Embodied A I": "IA incarnée", "Autonomous Disaster Robots": "Robots autonomes pour les catastrophes", "Mobility": "Mobilité", "Accessibility": "Accessibilité",
    "Advanced Computing": "Calcul avancé", "Quantum Networks": "Réseaux quantiques", "Quantum Sensing": "Capteurs quantiques", "Neuromorphic Computing": "Calcul neuromorphique",
    "Photonic Computing": "Calcul photonique", "Fault Tolerant Quantum Computing": "Calcul quantique tolérant aux fautes", "Distributed Scientific Computing": "Calcul scientifique distribué",
    "Translator": "Traduction humain-machine", "Interstellar Communication": "Communication interstellaire", "Universal Translation Systems": "Systèmes de traduction universelle",
    "Public Health": "Santé publique", "Education": "Éducation"
  };

  const WORDS = {
    "orbital": "orbital", "deep-space": "espace profond", "planetary": "planétaire", "lunar": "lunaire", "interstellar": "interstellaire",
    "civil": "civile", "industrial": "industrielle", "rescue": "de secours", "extreme-environment": "en environnement extrême", "infrastructure": "d'infrastructure",
    "renewable": "renouvelable", "grid": "réseau", "portable": "portable", "space": "spatiale", "advanced": "avancée", "bioinspired": "bio-inspirée",
    "structural": "structurelle", "functional": "fonctionnelle", "recyclable": "recyclable", "cellular": "cellulaire", "tissue": "tissulaire", "organ": "organique",
    "neural": "neuronale", "assistive": "assistive", "ecosystem": "écosystémique", "climate": "climatique", "marine": "marine", "agricultural": "agricole", "atmospheric": "atmosphérique",
    "field": "de terrain", "scientific": "scientifique", "public": "publique", "distributed": "distribuée", "secure": "sécurisée", "accessible": "accessible",
    "navigation": "navigation", "robotics": "robotique", "habitats": "habitats", "resource mapping": "cartographie des ressources", "radiation monitoring": "surveillance des rayonnements",
    "communications": "communications", "autonomous operations": "opérations autonomes", "precision landing": "atterrissage de précision", "thermal control": "contrôle thermique", "life support": "support-vie",
    "monitoring": "surveillance", "restoration": "restauration", "forecasting": "prévision", "water quality": "qualité de l'eau", "soil sensing": "capteurs des sols",
    "biodiversity mapping": "cartographie de la biodiversité", "carbon accounting": "comptabilité carbone", "pollution detection": "détection de la pollution", "wildfire detection": "détection des incendies",
    "resilience planning": "planification de la résilience", "safe autonomy": "autonomie sûre", "decision support": "aide à la décision", "research coordination": "coordination de la recherche"
  };

  function frTitle(text) {
    const raw = String(text || "").trim();
    if (!raw) return raw;
    if (FR_TECH[raw]) return FR_TECH[raw];
    let result = raw;
    Object.entries(WORDS).forEach(([en, fr]) => {
      result = result.replace(new RegExp("\\b" + en.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&") + "\\b", "gi"), fr);
    });
    result = result.replace(/\s+Research$/i, " — recherche");
    return result === raw ? raw : result;
  }

  function language() {
    return (document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
  }

  function applyCatalogueCopy() {
    const lang = language();
    const total = document.getElementById("technology-catalogue-count");
    const note = document.querySelector(".technology-catalogue-note");
    if (total) total.textContent = lang === "fr" ? "500 programmes de recherche" : "500 research programmes";
    if (note) note.textContent = lang === "fr" ? "500 programmes de recherche, organisés en huit domaines et avec des filtres traduits." : "500 research programmes, organised into eight domains with translated filters.";

    const heading = document.getElementById("platform-downloads-title");
    if (heading) heading.textContent = lang === "fr" ? "Emportez ETDESS partout" : "Take SSSWET with you";

    document.querySelectorAll("#bot-current-technology-title, .technology-card h3, [data-technology-title]").forEach(el => {
      if (lang === "fr") {
        const original = el.dataset.ssswetOriginalTitle || el.textContent.trim();
        el.dataset.ssswetOriginalTitle = original;
        el.textContent = frTitle(original);
      }
    });

    document.querySelectorAll("* ").forEach(el => {
      if (el.children.length || !el.textContent) return;
      const text = el.textContent;
      if (/64\s*\/\s*100/.test(text)) el.textContent = text.replace(/64\s*\/\s*100/, "64 / 500");
      else if (/\/\s*100\s+programmes/i.test(text)) el.textContent = text.replace(/\/\s*100/, "/ 500");
    });
  }

  function start() {
    applyCatalogueCopy();
    const observer = new MutationObserver(() => applyCatalogueCopy());
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    document.getElementById("language")?.addEventListener("change", () => setTimeout(applyCatalogueCopy, 0));
    window.addEventListener("ssswet-language-changed", () => setTimeout(applyCatalogueCopy, 0));
  }
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start, { once: true });
})();
