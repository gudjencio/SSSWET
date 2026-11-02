(() => {
  "use strict";
  const exact = {
    "Spacetime":"Espace-temps","Timetravel":"Voyage temporel","Artificial Gravity":"Gravité artificielle","Planetary Monitoring":"Surveillance planétaire","Black Hole Observation":"Observation des trous noirs","Event Horizon Imaging":"Imagerie des horizons des événements","Gravitational Wave Navigation":"Navigation par ondes gravitationnelles","Relativistic Spacecraft":"Vaisseaux spatiaux relativistes","Jetpack":"Système de propulsion individuel","Antimatter Research":"Recherche sur l'antimatière","Beamed Energy Propulsion":"Propulsion par énergie dirigée","Solar Sail Navigation":"Navigation par voile solaire","Plasma Propulsion":"Propulsion plasma","Space Life Support":"Support-vie spatial","Cosmic Ray Shielding":"Blindage contre les rayons cosmiques","Cryogenic Hibernation":"Hibernation cryogénique","Orbital Manufacturing":"Fabrication orbitale","Lunar Resource Systems":"Systèmes de ressources lunaires","Radiation Protection":"Protection contre les rayonnements","Armor":"Protection corporelle","Disaster Resilience":"Résilience aux catastrophes","Extreme Thermal Protection":"Protection thermique extrême","Impact Absorbing Materials":"Matériaux absorbant les impacts","Cleanenergy":"Énergie propre","Fusion Energy":"Énergie de fusion","Superconducting Grid":"Réseau supraconducteur","Energy Storage":"Stockage de l'énergie","Metamaterials":"Métamatériaux","Self Healing Materials":"Matériaux autoréparants","Smart Adaptive Materials":"Matériaux adaptatifs intelligents","Longevity":"Longévité en bonne santé","Medical Nanotechnology":"Nanotechnologies médicales","Organ Regeneration":"Régénération des organes","Precision Gene Therapies":"Thérapies géniques de précision","Artificial Organs":"Organes artificiels","Neurointerfaces":"Neurointerfaces","Robotics Exoskeletons":"Exosquelettes robotiques","Sensory Augmentation":"Augmentation sensorielle","Animal Health":"Santé animale","Climate":"Climat","Biodiversity":"Biodiversité","Wildlife":"Protection de la faune","Oceans":"Océans","Reforestation":"Reboisement","Agriculture":"Agriculture","Carbon Monitoring":"Surveillance du carbone","Pollinators":"Protection des pollinisateurs","Air Quality":"Qualité de l'air","Water":"Eau","Food Systems":"Systèmes alimentaires","Sanitation":"Assainissement","Wildfire Prediction":"Prévision des incendies de forêt","Autonomous Labs":"Laboratoires autonomes","Swarm Robotics":"Robotique en essaim","Autonomous Disaster Robots":"Robots autonomes pour les catastrophes","Mobility":"Mobilité","Accessibility":"Accessibilité","Advanced Computing":"Calcul avancé","Quantum Networks":"Réseaux quantiques","Quantum Sensing":"Capteurs quantiques","Neuromorphic Computing":"Calcul neuromorphique","Photonic Computing":"Calcul photonique","Distributed Scientific Computing":"Calcul scientifique distribué","Translator":"Traduction humain-machine","Interstellar Communication":"Communication interstellaire","Universal Translation Systems":"Systèmes de traduction universelle","Public Health":"Santé publique","Education":"Éducation"
  };
  const phrases = {
    "resource mapping":"cartographie des ressources","radiation monitoring":"surveillance des rayonnements",
    "autonomous operations":"opérations autonomes","precision landing":"atterrissage de précision",
    "life support":"support-vie","hazard detection":"détection des risques","impact mitigation":"atténuation des impacts",
    "thermal protection":"protection thermique","structural monitoring":"surveillance structurelle",
    "evacuation support":"assistance à l’évacuation","wearable safety":"sécurité portable",
    "emergency power":"alimentation de secours","environmental sensing":"capteurs environnementaux",
    "thermal management":"gestion thermique","power quality":"qualité de l’alimentation",
    "load balancing":"équilibrage de charge","energy recovery":"récupération d’énergie",
    "fault detection":"détection des défaillances","demand forecasting":"prévision de la demande",
    "microgrid control":"contrôle des micro-réseaux","self-healing":"autoréparateur",
    "damage detection":"détection des dommages","surface engineering":"ingénierie des surfaces",
    "fatigue monitoring":"surveillance de la fatigue","manufacturing control":"contrôle de fabrication",
    "durability prediction":"prédiction de durabilité","drug delivery":"administration de médicaments",
    "prosthetic control":"contrôle prothétique","physiological sensing":"capteurs physiologiques",
    "clinical data":"données cliniques","safety monitoring":"surveillance de la sécurité",
    "water quality":"qualité de l’eau","soil sensing":"capteurs des sols",
    "biodiversity mapping":"cartographie de la biodiversité","carbon accounting":"comptabilité carbone",
    "pollution detection":"détection de la pollution","wildfire detection":"détection des incendies",
    "resilience planning":"planification de la résilience","human interaction":"interaction humaine",
    "fault recovery":"récupération après défaillance","energy management":"gestion énergétique",
    "safe autonomy":"autonomie sûre","data provenance":"provenance des données",
    "knowledge discovery":"découverte des connaissances","privacy protection":"protection de la vie privée",
    "health information":"informations de santé","decision support":"aide à la décision",
    "research coordination":"coordination de la recherche"
  };
  const words = {"orbital":"orbital","deep-space":"espace profond","planetary":"planétaire","lunar":"lunaire","interstellar":"interstellaire","civil":"civile","industrial":"industrielle","rescue":"de secours","extreme-environment":"en environnement extrême","infrastructure":"d'infrastructure","renewable":"renouvelable","grid":"réseau","portable":"portable","space":"spatiale","advanced":"avancée","bioinspired":"bio-inspirée","structural":"structurelle","functional":"fonctionnelle","recyclable":"recyclable","cellular":"cellulaire","tissue":"tissulaire","organ":"organique","neural":"neuronale","assistive":"assistive","ecosystem":"écosystémique","climate":"climatique","marine":"marine","agricultural":"agricole","atmospheric":"atmosphérique","field":"de terrain","scientific":"scientifique","public":"publique","distributed":"distribuée","secure":"sécurisée","accessible":"accessible","navigation":"navigation","robotics":"robotique","habitats":"habitats","monitoring":"surveillance","restoration":"restauration","forecasting":"prévision","mapping":"cartographie","detection":"détection","protection":"protection","research":"recherche","computing":"calcul","communication":"communication","translation":"traduction","coordination":"coordination","support":"assistance"};
  const lang = () => (document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const frenchTitle = text => {
    const raw = String(text || "").trim();
    if (!raw || exact[raw]) return exact[raw] || raw;
    let value = raw;
    for (const [en, fr] of Object.entries(phrases)) value = value.replace(new RegExp(en.replace(/[.*+?^${}()|[\\]\\]/g,"\\    let value = raw;
    for (const [en, fr] of Object.entries(words))"),"gi"), fr);
    for (const [en, fr] of Object.entries(words)) value = value.replace(new RegExp(en.replace(/[.*+?^${}()|[\\]\\]/g,"\\$&"),"gi"), fr);
    return value;
  };
  function apply() {
    const isFr = lang() === "fr";
    const count = document.getElementById("technology-catalogue-count");
    const note = document.querySelector(".technology-catalogue-note");
    const heading = document.getElementById("platform-downloads-title");
    const countText = isFr ? "500 programmes de recherche enregistrés · 100 thèmes de contribution" : "500 registered research programmes · 100 contribution themes";
    const noteText = isFr ? "500 programmes de recherche, organisés en huit domaines et avec des filtres traduits." : "500 research programmes, organised into eight domains with translated filters.";
    const headingText = isFr ? "Emportez SSSWET partout" : "Take SSSWET with you";
    if (count && count.textContent !== countText) count.textContent = countText;
    if (note && note.textContent !== noteText) note.textContent = noteText;
    if (heading && heading.textContent !== headingText) heading.textContent = headingText;
    document.querySelectorAll("#bot-current-technology-title,.technology-card h3,[data-technology-title]").forEach(el => {
      const original = el.dataset.ssswetOriginalTitle || el.textContent.trim();
      if (!el.dataset.ssswetOriginalTitle) el.dataset.ssswetOriginalTitle = original;
      const target = isFr ? frenchTitle(original) : original;
      if (el.textContent !== target) el.textContent = target;
    });
    document.querySelectorAll("body *:not(script):not(style)").forEach(el => {
      if (el.children.length) return;
      const text = el.textContent || "";
      const next = text.replace(/64\s*\/\s*100/g, "64 / 500").replace(/\/\s*100(\s+programmes?\b)/gi, "/ 500$1");
      if (next !== text) el.textContent = next;
    });
  }
  const start = () => {
    apply();
    document.getElementById("language")?.addEventListener("change", () => setTimeout(apply, 0));
    window.addEventListener("ssswet-language-changed", () => setTimeout(apply, 0));
    const observer = new MutationObserver(() => apply());
    observer.observe(document.body, {childList:true, subtree:true});
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start, {once:true});
})();
