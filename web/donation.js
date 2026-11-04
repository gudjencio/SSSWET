(() => {
  "use strict";

  const technologies = {
    cellular: {
      en: ["Cellular enhancement", "Research into cell repair, regenerative biology, resilience and safe measurement. This theme is exploratory and does not imply that human enhancement is currently possible."],
      fr: ["Améliorations cellulaires", "Recherche sur la réparation cellulaire, la biologie régénérative, la résilience et leur mesure sûre. Ce thème reste exploratoire et ne signifie pas qu'une amélioration humaine soit actuellement possible."]
    },
    longevity: {
      en: ["Healthy longevity", "Evidence-led research into healthy ageing, prevention, cellular maintenance and quality of life."],
      fr: ["Longévité en bonne santé", "Recherche fondée sur les preuves concernant le vieillissement en bonne santé, la prévention, le maintien cellulaire et la qualité de vie."]
    },
    armor: {
      en: ["Advanced protective suits", "Research into protective materials, ergonomics, mobility, thermal comfort and human safety."],
      fr: ["Armures et équipements de protection", "Recherche sur les matériaux protecteurs, l'ergonomie, la mobilité, le confort thermique et la sécurité humaine."]
    },
    jetpack: {
      en: ["Personal propulsion", "High-level study of propulsion concepts, energy efficiency, control systems and operational safety."],
      fr: ["Jetpacks et propulsion individuelle", "Étude générale des concepts de propulsion, de l'efficacité énergétique, du contrôle et de la sécurité opérationnelle."]
    },
    translator: {
      en: ["Human–alien translation", "Long-term research into bidirectional communication, unknown languages, signal interpretation and uncertainty-aware translation."],
      fr: ["Traducteurs humains–extraterrestres", "Recherche à long terme sur la communication bidirectionnelle, les langues inconnues, l'interprétation des signaux et la traduction tenant compte de l'incertitude."]
    },
    spacetime: {
      en: ["Space-warping physics", "Theoretical and mathematical exploration of spacetime models, with no claim of practical propulsion or controllable warping."],
      fr: ["Physique de la déformation de l'espace-temps", "Exploration théorique et mathématique de modèles d'espace-temps, sans prétendre disposer d'une propulsion pratique ni d'une déformation contrôlable."]
    },
    sentientAI: {
      en: ["Sentient AI", "Research into whether artificial systems could have genuine subjective experience, distinct from behavioural imitation. No current test conclusively establishes AI consciousness; human-like performance or self-reports are not proof."],
      fr: ["IA sentiente", "Recherche sur la possibilité qu’une intelligence artificielle possède une expérience subjective authentique, et non une simple imitation comportementale. Aucun test actuel ne démontre de façon concluante la conscience d’une IA ; des performances ou déclarations d’apparence humaine ne constituent pas une preuve."]
    },
    humanLikeRobots: {
      en: ["Human-like Robots", "Research into human-inspired robots for everyday assistance, accessibility, companionship and collaboration. Robots must clearly disclose that they are artificial systems, protect privacy, avoid physical contact unless safe and consented, and never be designed to injure or kill people or animals."],
      fr: ["Robots humanoïdes", "Recherche sur des robots d’inspiration humaine pour l’aide quotidienne, l’accessibilité, la compagnie et la coopération. Les robots doivent clairement indiquer qu’ils sont des systèmes artificiels, protéger la vie privée, éviter tout contact physique non sûr ou non consenti et ne jamais être conçus pour blesser ou tuer des humains ou des animaux."]
    },
    timetravel: {
      en: ["Time travel research", "Exploratory study of time, causality, relativity, spacetime geometry and the mathematical limits of proposed temporal models. This is a long-term research ambition, not an available capability."],
      fr: ["Voyage dans le temps", "Étude exploratoire du temps, de la causalité, de la relativité, de la géométrie de l'espace-temps et des limites mathématiques des modèles temporels proposés. Il s'agit d'une ambition de recherche à long terme, pas d'une capacité disponible."]
    },
    cleanenergy: {
      en: ["Clean energy systems", "Research into safe, scalable solar, wind, geothermal and other low-carbon energy systems."],
      fr: ["Systèmes d’énergie propre", "Recherche sur des systèmes énergétiques bas carbone sûrs et évolutifs : solaire, éolien, géothermie et autres filières."]
    },
    energyStorage: {
      en: ["Advanced energy storage", "Long-duration storage, safer batteries, grid balancing and responsible materials research."],
      fr: ["Stockage avancé de l’énergie", "Stockage de longue durée, batteries plus sûres, équilibre des réseaux et recherche responsable sur les matériaux."]
    },
    water: {
      en: ["Clean water and desalination", "Affordable water purification, contaminant detection, low-energy desalination and resilient access."],
      fr: ["Eau potable et dessalement", "Purification abordable, détection des contaminants, dessalement sobre en énergie et accès résilient à l’eau."]
    },
    foodSystems: {
      en: ["Sustainable food systems", "Resilient crops, food preservation, reduced waste and equitable access to nutritious food."],
      fr: ["Systèmes alimentaires durables", "Cultures résilientes, conservation des aliments, réduction du gaspillage et accès équitable à une alimentation nutritive."]
    },
    climate: {
      en: ["Climate adaptation", "Monitoring, forecasting, heat resilience, flood preparedness and evidence-led adaptation tools."],
      fr: ["Adaptation climatique", "Surveillance, prévisions, résilience face aux fortes chaleurs, préparation aux inondations et outils d’adaptation fondés sur les preuves."]
    },
    biodiversity: {
      en: ["Biodiversity protection", "Non-invasive monitoring, habitat connectivity and measurable conservation outcomes."],
      fr: ["Protection de la biodiversité", "Suivi non invasif, continuité des habitats et résultats de conservation mesurables."]
    },
    wildlife: {
      en: ["Wildlife protection", "Ethical tracking, rescue support, anti-poaching detection and safer coexistence with wildlife."],
      fr: ["Protection de la faune sauvage", "Suivi éthique, aide au sauvetage, détection du braconnage et coexistence plus sûre avec la faune."]
    },
    oceans: {
      en: ["Ocean and marine restoration", "Ocean observation, marine pollution reduction, reef monitoring and ecosystem recovery."],
      fr: ["Océans et restauration marine", "Observation des océans, réduction de la pollution marine, suivi des récifs et restauration des écosystèmes."]
    },
    reforestation: {
      en: ["Reforestation and habitat restoration", "Native-species restoration, soil recovery, ecological corridors and long-term survival monitoring."],
      fr: ["Reforestation et restauration des habitats", "Restauration d’espèces indigènes, régénération des sols, corridors écologiques et suivi de la survie à long terme."]
    },
    agriculture: {
      en: ["Regenerative agriculture", "Soil health, precision irrigation, biodiversity-friendly farming and lower-impact cultivation."],
      fr: ["Agriculture régénératrice", "Santé des sols, irrigation de précision, agriculture favorable à la biodiversité et cultures à moindre impact."]
    },
    circularEconomy: {
      en: ["Circular economy and recycling", "Repairable products, material recovery, safer recycling and reduced resource extraction."],
      fr: ["Économie circulaire et recyclage", "Produits réparables, récupération des matériaux, recyclage plus sûr et réduction de l’extraction des ressources."]
    },
    airQuality: {
      en: ["Clean air technologies", "Affordable air-quality sensing, filtration, emissions monitoring and exposure reduction."],
      fr: ["Qualité de l’air", "Capteurs abordables, filtration, surveillance des émissions et réduction de l’exposition à la pollution."]
    },
    mobility: {
      en: ["Sustainable mobility", "Accessible public transport, safer cycling, efficient logistics and low-emission mobility research."],
      fr: ["Mobilité durable", "Transports publics accessibles, vélo plus sûr, logistique efficace et mobilité à faibles émissions."]
    },
    accessibility: {
      en: ["Assistive and accessibility technology", "Affordable tools for communication, mobility, independent living and inclusive design."],
      fr: ["Technologies d’assistance et d’accessibilité", "Outils abordables pour la communication, la mobilité, l’autonomie et la conception inclusive."]
    },
    disasterResilience: {
      en: ["Disaster prevention and response", "Early warning, resilient infrastructure, emergency logistics and recovery coordination."],
      fr: ["Prévention et réponse aux catastrophes", "Alertes précoces, infrastructures résilientes, logistique d’urgence et coordination du rétablissement."]
    },
    publicHealth: {
      en: ["Public health and prevention", "Evidence-led prevention, accessible diagnostics, health information and community resilience."],
      fr: ["Santé publique et prévention", "Prévention fondée sur les preuves, diagnostics accessibles, information sanitaire et résilience communautaire."]
    },
    sanitation: {
      en: ["Sanitation and waste-water treatment", "Safe sanitation, decentralized treatment, water reuse and pollution prevention."],
      fr: ["Assainissement et traitement des eaux usées", "Assainissement sûr, traitement décentralisé, réutilisation de l’eau et prévention de la pollution."]
    },
    education: {
      en: ["Open science and education", "Free learning resources, scientific literacy, accessible laboratories and research collaboration."],
      fr: ["Science ouverte et éducation", "Ressources pédagogiques libres, culture scientifique, laboratoires accessibles et collaboration en recherche."]
    },
    animalHealth: {
      en: ["Animal health and welfare", "Non-invasive diagnostics, disease prevention, humane care and improved veterinary access."],
      fr: ["Santé et bien-être animal", "Diagnostics non invasifs, prévention des maladies, soins respectueux et meilleur accès vétérinaire."]
    },
    materials: {
      en: ["Sustainable and safer materials", "Durable, recyclable and non-toxic materials for construction, medicine and everyday products."],
      fr: ["Matériaux durables et plus sûrs", "Matériaux durables, recyclables et non toxiques pour la construction, la médecine et les produits courants."]
    },
    carbonMonitoring: {
      en: ["Carbon and ecosystem monitoring", "Transparent measurement of emissions, carbon storage and ecosystem health."],
      fr: ["Surveillance du carbone et des écosystèmes", "Mesure transparente des émissions, du stockage du carbone et de la santé des écosystèmes."]
    },
    pollinators: {
      en: ["Pollinator protection", "Habitat mapping, pesticide exposure reduction and monitoring of pollinator populations."],
      fr: ["Protection des pollinisateurs", "Cartographie des habitats, réduction de l’exposition aux pesticides et suivi des populations de pollinisateurs."]
    },
    artificialGravity: {
      en: ["Artificial gravity research", "Theoretical research into gravity-like environments, rotational habitats, inertial effects, human adaptation and measurable safety limits. No controllable artificial-gravity technology is currently claimed."],
      fr: ["Recherche sur la gravité artificielle", "Recherche théorique sur les environnements assimilables à la gravité, les habitats rotatifs, les effets inertiels, l’adaptation humaine et les limites de sécurité mesurables. Aucune technologie de gravité artificielle contrôlable n’est présentée comme acquise."]
    },
    medicalNanotechnology: {
      en: ["Medical nanotechnology", "Research into nanoscale diagnostics, targeted sensing, biocompatible materials, delivery constraints, toxicology and independently reviewed medical safety. No clinical capability is implied."],
      fr: ["Nanotechnologies médicales", "Recherche sur le diagnostic à l’échelle nanométrique, la détection ciblée, les matériaux biocompatibles, les contraintes d’administration, la toxicologie et la sécurité médicale évaluée indépendamment. Aucune capacité clinique n’est présumée."]
    },
    atmosphericRestoration: {
      en: ["Atmospheric restoration", "Research into atmospheric pollution monitoring, source reduction, carbon-cycle measurement, ecosystem recovery and validated interventions with transparent environmental safeguards."],
      fr: ["Restauration atmosphérique", "Recherche sur la surveillance de la pollution atmosphérique, la réduction des émissions à la source, la mesure du cycle du carbone, la restauration des écosystèmes et les interventions validées avec des garanties environnementales transparentes."]
    }
  };

  Object.assign(technologies, {
    neurointerfaces: {
      en: ["Interfaces cerveau-machine", "Research into non-invasive brain–computer interfaces, accessibility, signal quality and neural-data privacy."],
      fr: ["Interfaces cerveau-machine", "Recherche non invasive sur les interfaces cerveau-machine, l’accessibilité, la qualité du signal et la protection des données neuronales."]
    },
    quantumNetworks: {
      en: ["Quantum communication networks", "Fundamental research into experimental quantum networks, quantum key distribution and their physical limits."],
      fr: ["Réseaux de communication quantique", "Recherche fondamentale sur les réseaux quantiques expérimentaux, la distribution quantique de clés et leurs limites physiques."]
    },
    fusionEnergy: {
      en: ["Fusion energy", "Research into materials, confinement, thermal management and fusion-related energy systems, without promising net energy production."],
      fr: ["Énergie de fusion", "Recherche sur les matériaux, le confinement, la gestion thermique et les systèmes associés à la fusion, sans promesse de production nette."]
    },
    spaceLifeSupport: {
      en: ["Closed-loop space life-support ecosystems", "Closed-loop life-support systems, water and air recycling, food production and resilient space habitats."],
      fr: ["Écosystèmes spatiaux en boucle fermée", "Systèmes de support-vie, recyclage de l’eau et de l’air, production alimentaire et résilience des habitats spatiaux."]
    },
    autonomousLabs: {
      en: ["Autonomous research laboratories", "Automated measurements, experimental traceability, quality control and human validation of research protocols."],
      fr: ["Laboratoires scientifiques autonomes", "Automatisation des mesures, traçabilité expérimentale, contrôle qualité et validation humaine des protocoles."]
    },
    roboticsExoskeletons: {
      en: ["Advanced robotics and exoskeletons", "Assistive robotics, ergonomics, mobility, human–machine interaction and user safety."],
      fr: ["Robotique avancée et exosquelettes", "Robotique d’assistance, ergonomie, mobilité, interaction humain-machine et sécurité des utilisateurs."]
    },
    planetaryMonitoring: {
      en: ["Planetary monitoring and asteroid-risk assessment", "Astronomical detection, orbital tracking, uncertainty estimation and scientific risk assessment."],
      fr: ["Surveillance planétaire et risques astéroïdaux", "Détection astronomique, suivi orbital, estimation des incertitudes et évaluation scientifique des risques."]
    },
    advancedComputing: {
      en: ["Advanced computing and scientific AI", "Computational tools, interpretable scientific models, reproducibility and evaluation of AI-system limitations."],
      fr: ["Calcul avancé et intelligence artificielle scientifique", "Outils de calcul, modèles scientifiques interprétables, reproductibilité et évaluation des limites des systèmes d’IA."]
    },
    modularProtectiveArmor: {
      en: ["Modular protective armor", "Research into modular, repairable personal protection, ergonomic fit, mobility and independently tested performance for defined hazards."],
      fr: ["Armure de protection modulaire", "Recherche sur la protection individuelle modulaire et réparable, l’ergonomie, la mobilité et les performances testées indépendamment pour des risques définis."]
    },
    blastAndImpactProtection: {
      en: ["Blast and impact injury protection", "Research into passive injury reduction, impact protection, safe removal and independently validated performance limits."],
      fr: ["Protection contre les impacts", "Recherche sur la réduction passive des blessures, la protection contre les impacts, le retrait sécurisé et les limites validées indépendamment."]
    },
    environmentalProtectionSuit: {
      en: ["Advanced environmental protection suits", "Research into certified components for thermal, particulate and defined chemical exposure protection, with safe emergency removal."],
      fr: ["Combinaisons de protection environnementale", "Recherche sur des composants certifiés contre les expositions thermiques, particulaires et chimiques définies, avec retrait d’urgence sécurisé."]
    },
    protectivePhysiologicalMonitoring: {
      en: ["Protective physiological monitoring", "Non-diagnostic monitoring of environmental exposure and selected strain indicators, with privacy and reliability safeguards."],
      fr: ["Surveillance physiologique de protection", "Surveillance non diagnostique de l’exposition environnementale et de certains indicateurs de fatigue, avec garanties de confidentialité et de fiabilité."]
    },
    poweredLoadAssistExoskeletons: {
      en: ["Powered load-assist exoskeletons", "Research into ergonomic lifting and carrying assistance, safe disengagement, power-loss behavior and human-factors validation."],
      fr: ["Exosquelettes motorisés d’assistance au port de charges", "Recherche sur l’assistance ergonomique au levage et au transport, le désengagement sécurisé, les pannes d’alimentation et la validation ergonomique."]
    },
    rescueMobilityExoskeletons: {
      en: ["Rescue and mobility exoskeletons", "Research into safe mobility assistance for rescue, evacuation and accessibility, with manual override and fail-safe operation."],
      fr: ["Exosquelettes de secours et de mobilité", "Recherche sur l’assistance à la mobilité pour le secours, l’évacuation et l’accessibilité, avec commande manuelle et fonctionnement sécurisé."]
    }
  });

  Object.assign(technologies, {
    blackHoleObservation: {
      en: ["Black hole observation and physics", "Study black-hole environments through established astrophysical observations, relativistic models and uncertainty-aware interpretation."],
      fr: ["Observation et physique des trous noirs", "Étude des environnements de trous noirs à partir d’observations astrophysiques, de modèles relativistes et d’interprétations tenant compte des incertitudes."]
    },
    blackHoleProbeSystems: {
      en: ["Black-hole exploration probes", "Conceptual study of remote sensing, autonomous probes and mission constraints near extreme gravitational environments; no survivable close approach is assumed."],
      fr: ["Sondes d’exploration des trous noirs", "Étude conceptuelle de la télédétection, des sondes autonomes et des contraintes de mission près d’environnements gravitationnels extrêmes ; aucune survie à proximité n’est présumée."]
    },
    blackHoleResilientVehicles: {
      en: ["Black-hole-resilient craft concepts", "Theoretical limits on spacecraft structures, shielding, communication and survivability in strong gravitational fields, including explicit limits imposed by tidal forces and horizons."],
      fr: ["Concepts d’engins résistants aux trous noirs", "Limites théoriques des structures, protections, communications et de la survivabilité des engins en champs gravitationnels intenses, notamment les forces de marée et les horizons."]
    },
    eventHorizonImaging: {
      en: ["Event-horizon imaging", "Research into interferometry, computational imaging and multi-messenger observations of black-hole environments."],
      fr: ["Imagerie des horizons des événements", "Recherche sur l’interférométrie, l’imagerie computationnelle et les observations multimessagers des environnements de trous noirs."]
    },
    gravitationalWaveNavigation: {
      en: ["Gravitational-wave astronomy and navigation", "Explore gravitational-wave detection, source localization and possible future navigation applications within known physical limits."],
      fr: ["Astronomie et navigation par ondes gravitationnelles", "Étude de la détection des ondes gravitationnelles, de la localisation des sources et d’éventuelles applications futures à la navigation, dans les limites physiques connues."]
    },
    relativisticSpacecraft: {
      en: ["Relativistic spacecraft systems", "Model long-duration relativistic missions, radiation exposure, propulsion constraints, time dilation and mission communication limits."],
      fr: ["Systèmes de véhicules spatiaux relativistes", "Modélisation de missions relativistes de longue durée, de l’exposition aux rayonnements, des contraintes de propulsion, de la dilatation du temps et des communications."]
    },
    deepSpaceRadiationShelters: {
      en: ["Deep-space radiation shelters", "Assess habitat layouts, passive shielding concepts, storm shelters and exposure monitoring for crewed deep-space missions."],
      fr: ["Abris contre les rayonnements de l’espace profond", "Évaluation de l’aménagement des habitats, des protections passives, des abris de tempête solaire et du suivi de l’exposition lors de missions habitées dans l’espace profond."]
    },
    cosmicRayShielding: {
      en: ["Cosmic-ray exposure mitigation", "Study realistic exposure measurement, shielding trade-offs and operational risk reduction for space missions."],
      fr: ["Réduction de l’exposition aux rayons cosmiques", "Étude de la mesure de l’exposition, des compromis de blindage et de la réduction des risques opérationnels lors des missions spatiales."]
    },
    nuclearBlastResilience: {
      en: ["Nuclear-blast protection and resilience", "Civilian life-safety research on blast effects, structural resilience, shelter performance, emergency planning and protection standards. No weapon design or optimization."],
      fr: ["Protection et résistance aux explosions nucléaires", "Recherche de protection civile portant sur les effets de souffle, la résilience des structures, les abris, la planification d’urgence et les normes de protection. Aucune conception ni optimisation d’arme."]
    },
    radiationProtection: {
      en: ["Radiation protection and shielding", "Research into radiation measurement, shielding materials, exposure reduction, protective equipment and validated safety thresholds."],
      fr: ["Protection et blindage contre les rayonnements", "Recherche sur la mesure des rayonnements, les matériaux de blindage, la réduction de l’exposition, les équipements de protection et les seuils de sécurité validés."]
    },
    radiationDosimetryNetworks: {
      en: ["Distributed radiation dosimetry", "Develop monitoring concepts for calibrated sensors, exposure mapping, uncertainty reporting and emergency information sharing."],
      fr: ["Réseaux distribués de dosimétrie", "Développement de concepts de surveillance par capteurs étalonnés, cartographie des expositions, déclaration des incertitudes et partage d’informations d’urgence."]
    },
    nuclearFalloutDecontamination: {
      en: ["Radioactive fallout detection and decontamination", "Civil protection research into contamination mapping, safe decontamination workflows, waste handling and public-health safeguards."],
      fr: ["Détection et décontamination des retombées radioactives", "Recherche en protection civile sur la cartographie de la contamination, les procédures sûres de décontamination, la gestion des déchets et les garanties sanitaires."]
    },
    electromagneticPulseResilience: {
      en: ["Electromagnetic-pulse resilience", "Assess civilian infrastructure resilience, equipment hardening standards, backup systems and continuity planning against electromagnetic disturbances."],
      fr: ["Résilience aux impulsions électromagnétiques", "Évaluation de la résilience des infrastructures civiles, des normes de protection des équipements, des systèmes de secours et de la continuité d’activité face aux perturbations électromagnétiques."]
    },
    extremeThermalProtection: {
      en: ["Extreme-heat and thermal-shock protection", "Study thermal insulation, fire-resistant materials, heat transfer and safe evacuation environments under extreme heat exposure."],
      fr: ["Protection contre les chaleurs extrêmes et chocs thermiques", "Étude de l’isolation thermique, des matériaux résistants au feu, des transferts de chaleur et des environnements d’évacuation sûrs en cas d’exposition thermique extrême."]
    },
    antimatterResearch: {
      en: ["Antimatter physics and containment research", "Fundamental study of antimatter production, measurement, storage limits and fundamental physics; no practical energy or propulsion system is implied."],
      fr: ["Physique de l’antimatière et recherche sur son confinement", "Étude fondamentale de la production, de la mesure, des limites de stockage de l’antimatière et de la physique fondamentale ; aucun système énergétique ou propulsif pratique n’est présumé."]
    },
    beamedEnergyPropulsion: {
      en: ["Beamed-energy propulsion concepts", "Evaluate high-level feasibility of externally powered propulsion, beam safety, pointing constraints and energy-transfer efficiency."],
      fr: ["Concepts de propulsion par énergie dirigée", "Évaluation générale de la faisabilité d’une propulsion alimentée à distance, de la sécurité des faisceaux, des contraintes de pointage et du rendement du transfert d’énergie."]
    },
    solarSailNavigation: {
      en: ["Advanced solar-sail navigation", "Research trajectory planning, sail materials, attitude control and mission design using solar or externally supplied photon pressure."],
      fr: ["Navigation avancée par voiles solaires", "Recherche sur la planification des trajectoires, les matériaux de voile, le contrôle d’attitude et les missions utilisant la pression photonique solaire ou externe."]
    },
    plasmaPropulsion: {
      en: ["Advanced plasma propulsion", "Study electric and plasma propulsion performance, power requirements, erosion, thermal management and mission suitability."],
      fr: ["Propulsion avancée par plasma", "Étude des performances de la propulsion électrique et plasma, des besoins énergétiques, de l’érosion, de la gestion thermique et de l’adéquation aux missions."]
    },
    interstellarProbeArchitecture: {
      en: ["Interstellar probe architecture", "Explore mission architectures, autonomy, communication delay, radiation, reliability and realistic propulsion constraints for interstellar precursor concepts."],
      fr: ["Architecture de sondes interstellaires", "Étude d’architectures de mission, d’autonomie, de délais de communication, de rayonnements, de fiabilité et de contraintes réalistes de propulsion pour des sondes précurseurs interstellaires."]
    },
    cryogenicHibernation: {
      en: ["Cryogenic preservation and torpor research", "Investigate biological limits, cryobiology, reversible preservation research, ethical constraints and the distinction between current medicine and speculative suspended animation."],
      fr: ["Recherche sur la conservation cryogénique et la torpeur", "Étude des limites biologiques, de la cryobiologie, de la conservation réversible, des contraintes éthiques et de la distinction entre médecine actuelle et animation suspendue spéculative."]
    },
    orbitalManufacturing: {
      en: ["Orbital manufacturing systems", "Study in-space manufacturing, quality assurance, material processing, maintenance and the economics of orbital production."],
      fr: ["Systèmes de fabrication en orbite", "Étude de la fabrication en orbite, de l’assurance qualité, du traitement des matériaux, de la maintenance et de l’économie de la production spatiale."]
    },
    lunarResourceSystems: {
      en: ["Lunar resource utilization", "Assess lunar geology, in-situ resource utilization, environmental protection, energy needs and sustainable mission logistics."],
      fr: ["Utilisation des ressources lunaires", "Évaluation de la géologie lunaire, de l’utilisation des ressources in situ, de la protection environnementale, des besoins énergétiques et de la logistique durable des missions."]
    },
    marsTerraformingAssessment: {
      en: ["Planetary habitability and terraforming assessment", "Scientific assessment of planetary environments, planetary protection, atmospheric constraints and ethical limits; no practical terraforming capability is claimed."],
      fr: ["Évaluation de l’habitabilité planétaire et de la terraformation", "Évaluation scientifique des environnements planétaires, de la protection planétaire, des contraintes atmosphériques et des limites éthiques ; aucune capacité pratique de terraformation n’est revendiquée."]
    },
    metamaterials: {
      en: ["Advanced metamaterials", "Research into engineered material responses, wave interaction, sensing, manufacturability and experimentally verified performance boundaries."],
      fr: ["Métamatériaux avancés", "Recherche sur les réponses des matériaux architecturés, l’interaction avec les ondes, la détection, la fabricabilité et les limites de performances vérifiées expérimentalement."]
    },
    selfHealingMaterials: {
      en: ["Self-healing materials", "Study reversible damage responses, fatigue, repair mechanisms, durability and lifecycle impacts in structural materials."],
      fr: ["Matériaux autoréparants", "Étude des réponses réversibles aux dommages, de la fatigue, des mécanismes de réparation, de la durabilité et des impacts sur le cycle de vie des matériaux structurels."]
    },
    aerogelSystems: {
      en: ["Advanced aerogel systems", "Explore lightweight porous materials for insulation, filtration, sensing and space applications, including mechanical fragility and scale-up."],
      fr: ["Systèmes avancés d’aérogel", "Étude des matériaux poreux légers pour l’isolation, la filtration, la détection et les applications spatiales, y compris leur fragilité mécanique et leur changement d’échelle."]
    },
    ultraHighTemperatureMaterials: {
      en: ["Ultra-high-temperature materials", "Evaluate ceramics, composites, oxidation, thermal cycling and test methods for extreme-temperature environments."],
      fr: ["Matériaux à très haute température", "Évaluation des céramiques, composites, de l’oxydation, des cycles thermiques et des méthodes d’essai pour les environnements à très haute température."]
    },
    smartAdaptiveMaterials: {
      en: ["Smart and adaptive materials", "Study materials that respond to temperature, stress, light or fields, with emphasis on repeatability, failure modes and safe applications."],
      fr: ["Matériaux intelligents et adaptatifs", "Étude de matériaux réagissant à la température, aux contraintes, à la lumière ou aux champs, avec une attention portée à la répétabilité, aux défaillances et aux usages sûrs."]
    },
    transparentCeramics: {
      en: ["Transparent structural ceramics", "Research transparent ceramic materials, optical performance, impact behaviour, manufacturing and protective-use limits."],
      fr: ["Céramiques structurelles transparentes", "Recherche sur les céramiques transparentes, leurs performances optiques, leur comportement aux impacts, leur fabrication et les limites de leurs usages protecteurs."]
    },
    impactAbsorbingMaterials: {
      en: ["Advanced impact-absorbing materials", "Assess energy absorption, cushioning, protective structures, repeated loading and validated injury-reduction metrics."],
      fr: ["Matériaux avancés absorbant les impacts", "Évaluation de l’absorption d’énergie, de l’amortissement, des structures protectrices, des charges répétées et des mesures validées de réduction des blessures."]
    },
    superconductingGrid: {
      en: ["High-temperature superconducting grids", "Research superconducting power transmission, cryogenic requirements, fault protection, materials supply and grid integration."],
      fr: ["Réseaux supraconducteurs à haute température", "Recherche sur le transport électrique supraconducteur, les besoins cryogéniques, la protection contre les défauts, l’approvisionnement en matériaux et l’intégration au réseau."]
    },
    ambientEnergyHarvesting: {
      en: ["Ambient energy harvesting", "Evaluate low-power energy harvesting from vibration, heat, light and radio-frequency environments with realistic efficiency accounting."],
      fr: ["Récupération de l’énergie ambiante", "Évaluation de la récupération de faibles puissances à partir des vibrations, de la chaleur, de la lumière et des radiofréquences avec un bilan réaliste des rendements."]
    },
    spaceSolarPower: {
      en: ["Space-based solar power systems", "Study orbital solar collection, power transmission safety, conversion efficiency, orbital debris and comparative lifecycle impacts."],
      fr: ["Systèmes solaires spatiaux", "Étude de la collecte solaire en orbite, de la sécurité du transfert d’énergie, du rendement de conversion, des débris orbitaux et des impacts comparés sur le cycle de vie."]
    },
    zeroCarbonIndustrialHeat: {
      en: ["Low-carbon industrial heat", "Research electrification, thermal storage, high-temperature heat pumps and low-carbon process heat for industrial applications."],
      fr: ["Chaleur industrielle bas carbone", "Recherche sur l’électrification, le stockage thermique, les pompes à chaleur haute température et la chaleur de procédé bas carbone pour l’industrie."]
    },
    thermoelectricSystems: {
      en: ["Advanced thermoelectric systems", "Investigate thermoelectric materials, waste-heat recovery, device reliability and practical system-level efficiency."],
      fr: ["Systèmes thermoélectriques avancés", "Étude des matériaux thermoélectriques, de la récupération de chaleur fatale, de la fiabilité des dispositifs et du rendement pratique à l’échelle du système."]
    },
    gridScaleThermalStorage: {
      en: ["Grid-scale thermal energy storage", "Assess sensible, latent and thermochemical storage for resilient energy systems, including safety and lifecycle performance."],
      fr: ["Stockage thermique à l’échelle des réseaux", "Évaluation du stockage sensible, latent et thermochimique pour des systèmes énergétiques résilients, y compris la sécurité et les performances sur le cycle de vie."]
    },
    organRegeneration: {
      en: ["Organ regeneration research", "Explore regenerative medicine, tissue engineering, vascularization, immune compatibility and rigorous preclinical evidence requirements."],
      fr: ["Recherche sur la régénération des organes", "Étude de la médecine régénérative, de l’ingénierie tissulaire, de la vascularisation, de la compatibilité immunitaire et des exigences de preuves précliniques."]
    },
    syntheticBiologyBiosafety: {
      en: ["Synthetic biology and biosafety", "Research responsible synthetic biology, containment, risk assessment, ecological safeguards and transparent oversight."],
      fr: ["Biologie synthétique et biosécurité", "Recherche sur la biologie synthétique responsable, le confinement, l’évaluation des risques, les garanties écologiques et la supervision transparente."]
    },
    precisionGeneTherapies: {
      en: ["Precision gene-therapy research", "Assess gene-therapy evidence, delivery limitations, off-target risks, long-term monitoring and equitable access under qualified oversight."],
      fr: ["Recherche sur les thérapies géniques de précision", "Évaluation des preuves en thérapie génique, des limites d’administration, des risques hors cible, du suivi à long terme et de l’accès équitable sous supervision qualifiée."]
    },
    bioelectronicMedicine: {
      en: ["Bioelectronic medicine", "Study interfaces between electrical systems and physiology, measurement quality, clinical evidence and device safety."],
      fr: ["Médecine bioélectronique", "Étude des interfaces entre systèmes électriques et physiologie, de la qualité des mesures, des preuves cliniques et de la sécurité des dispositifs."]
    },
    artificialOrgans: {
      en: ["Next-generation artificial organs", "Research biocompatibility, reliability, sensing, power, maintenance and clinical translation requirements for artificial organ systems."],
      fr: ["Organes artificiels de nouvelle génération", "Recherche sur la biocompatibilité, la fiabilité, la détection, l’alimentation, la maintenance et les exigences de transfert clinique des systèmes d’organes artificiels."]
    },
    medicalDigitalTwins: {
      en: ["Medical digital twins", "Explore validated patient-specific modelling, privacy, uncertainty communication and clinical decision-support evaluation."],
      fr: ["Jumeaux numériques médicaux", "Étude de la modélisation personnalisée validée, de la confidentialité, de la communication des incertitudes et de l’évaluation de l’aide à la décision clinique."]
    },
    swarmRobotics: {
      en: ["Cooperative swarm robotics", "Study distributed coordination, fault tolerance, human oversight and safe applications in inspection, rescue and environmental monitoring."],
      fr: ["Robotique coopérative en essaim", "Étude de la coordination distribuée, de la tolérance aux pannes, de la supervision humaine et des usages sûrs en inspection, sauvetage et surveillance environnementale."]
    },
    embodiedAI: {
      en: ["Embodied artificial intelligence", "Research grounded perception and action, robust evaluation, human interaction, transparency and safety in physical environments."],
      fr: ["Intelligence artificielle incarnée", "Recherche sur la perception et l’action en environnement réel, l’évaluation robuste, l’interaction humaine, la transparence et la sécurité."]
    },
    neuromorphicComputing: {
      en: ["Neuromorphic computing", "Explore brain-inspired computing architectures, energy use, learning behaviour, reproducibility and application-specific limits."],
      fr: ["Calcul neuromorphique", "Étude d’architectures informatiques inspirées du cerveau, de leur consommation énergétique, de leur apprentissage, de leur reproductibilité et de leurs limites selon les applications."]
    },
    quantumSensing: {
      en: ["Quantum sensing technologies", "Assess quantum-enhanced measurement concepts, calibration, noise, environmental robustness and realistic performance advantages."],
      fr: ["Technologies de détection quantique", "Évaluation des concepts de mesure améliorée par le quantique, de l’étalonnage, du bruit, de la robustesse environnementale et des avantages réels de performance."]
    },
    autonomousDisasterRobots: {
      en: ["Autonomous disaster-response robotics", "Develop safety-centred research for search, mapping and logistics robots with human supervision and reliable fail-safe behaviour."],
      fr: ["Robotique autonome d’intervention en catastrophe", "Développement de recherches centrées sur la sécurité pour des robots de recherche, cartographie et logistique, sous supervision humaine et avec des comportements de repli fiables."]
    },
    carbonRemoval: {
      en: ["Carbon removal measurement and verification", "Study durable carbon removal pathways, lifecycle accounting, monitoring, permanence and independent verification."],
      fr: ["Mesure et vérification de l’élimination du carbone", "Étude des voies durables d’élimination du carbone, du bilan de cycle de vie, du suivi, de la permanence et de la vérification indépendante."]
    },
    oceanAlkalinityMonitoring: {
      en: ["Ocean alkalinity and carbon monitoring", "Research ocean chemistry observation, ecosystem safeguards, measurement uncertainty and independent assessment of proposed interventions."],
      fr: ["Surveillance de l’alcalinité océanique et du carbone", "Recherche sur l’observation de la chimie océanique, les garanties écosystémiques, l’incertitude des mesures et l’évaluation indépendante des interventions proposées."]
    },
    geoengineeringAssessment: {
      en: ["Climate intervention risk assessment", "Independent assessment of proposed climate interventions, governance, reversibility, distributional effects and environmental monitoring; not an implementation programme."],
      fr: ["Évaluation des risques des interventions climatiques", "Évaluation indépendante des interventions climatiques proposées, de leur gouvernance, réversibilité, effets distributifs et surveillance environnementale ; ce programme ne vise pas leur mise en œuvre."]
    },
    wildfirePrediction: {
      en: ["Wildfire prediction and early warning", "Combine environmental observations, forecasting uncertainty, community alerts and decision-support evaluation for wildfire risk reduction."],
      fr: ["Prévision des incendies et alerte précoce", "Combinaison d’observations environnementales, d’incertitudes de prévision, d’alertes communautaires et d’évaluation d’outils d’aide à la décision pour réduire les risques d’incendie."]
    },
    ecosystemDigitalTwins: {
      en: ["Ecosystem digital twins", "Build transparent ecosystem models integrating observations, uncertainty, scenario testing and community-accessible conservation planning."],
      fr: ["Jumeaux numériques des écosystèmes", "Construction de modèles écosystémiques transparents intégrant observations, incertitudes, scénarios et planification de la conservation accessible aux communautés."]
    },
    photonicComputing: {
      en: ["Photonic computing systems", "Research optical information processing, energy efficiency, device integration, noise and benchmark reproducibility."],
      fr: ["Systèmes de calcul photonique", "Recherche sur le traitement optique de l’information, l’efficacité énergétique, l’intégration des dispositifs, le bruit et la reproductibilité des évaluations."]
    },
    faultTolerantQuantumComputing: {
      en: ["Fault-tolerant quantum computing", "Study error correction, coherence limits, hardware scaling, resource estimates and independently reproducible benchmarks."],
      fr: ["Calcul quantique tolérant aux erreurs", "Étude de la correction d’erreurs, des limites de cohérence, du changement d’échelle matériel, des estimations de ressources et de bancs d’essai reproductibles."]
    },
    distributedScientificComputing: {
      en: ["Distributed scientific computing", "Improve reproducible distributed workflows, secure collaboration, data provenance and efficient use of heterogeneous computing resources."],
      fr: ["Calcul scientifique distribué", "Amélioration des flux de calcul distribué reproductibles, de la collaboration sécurisée, de la provenance des données et de l’utilisation efficace de ressources hétérogènes."]
    },
    interstellarCommunication: {
      en: ["Interstellar communication research", "Explore signal detection, encoding constraints, long-delay protocols, astronomical interference and uncertainty in searches for technosignatures."],
      fr: ["Recherche sur les communications interstellaires", "Étude de la détection de signaux, des contraintes de codage, des protocoles à long délai, des interférences astronomiques et des incertitudes dans la recherche de technosignatures."]
    },
    sensoryAugmentation: {
      en: ["Human sensory augmentation", "Research assistive sensory interfaces, perceptual limits, accessibility, informed consent and long-term human factors."],
      fr: ["Augmentation sensorielle humaine", "Recherche sur les interfaces sensorielles d’assistance, les limites perceptives, l’accessibilité, le consentement éclairé et les facteurs humains à long terme."]
    },
    adaptiveExosuits: {
      en: ["Adaptive soft exosuits", "Study wearable assistance, comfort, mobility, control, user diversity and independently assessed safety."],
      fr: ["Exocombinaisons souples adaptatives", "Étude de l’assistance portable, du confort, de la mobilité, du contrôle, de la diversité des utilisateurs et de la sécurité évaluée indépendamment."]
    },
    closedLoopNeuroprosthetics: {
      en: ["Closed-loop neuroprosthetics", "Research bidirectional neural interfaces, adaptive control, biocompatibility, privacy and clinical validation requirements."],
      fr: ["Neuroprothèses en boucle fermée", "Recherche sur les interfaces neuronales bidirectionnelles, le contrôle adaptatif, la biocompatibilité, la confidentialité et les exigences de validation clinique."]
    },
    universalTranslationSystems: {
      en: ["Universal translation systems", "Explore multilingual speech and text translation, low-resource languages, context preservation, accessibility and transparent uncertainty."],
      fr: ["Systèmes de traduction universelle", "Étude de la traduction multilingue de la parole et du texte, des langues peu dotées, de la préservation du contexte, de l’accessibilité et de l’incertitude transparente."]
    }
  });

  // Preserve the expanded research catalogue loaded before this file.
  Object.assign(technologies, window.SSSWET_TECHNOLOGIES || {});
  window.SSSWET_TECHNOLOGIES = technologies;

  const catalogueCountLabels = {
    en: "research programmes", fr: "programmes de recherche", es: "programas de investigación",
    de: "Forschungsprogramme", it: "programmi di ricerca", pt: "programas de pesquisa",
    nl: "onderzoeksprogramma's", ru: "исследовательских программ", uk: "дослідницьких програм",
    ar: "برنامجًا بحثيًا", he: "תוכניות מחקר", ja: "件の研究プログラム", ko: "개 연구 프로그램",
    zh: "项研究计划", hi: "अनुसंधान कार्यक्रम"
  };
  function updateCatalogueCount() {
    const element = document.getElementById("technology-catalogue-count");
    if (!element) return;
    const grid = document.getElementById("technology-grid");
    const total = Object.keys(technologies).length;
    const lang = (document.documentElement.lang || document.getElementById("language")?.value || "en").toLowerCase().split("-")[0];
    element.textContent = total + " " + (catalogueCountLabels[lang] || catalogueCountLabels.en);
    element.dataset.catalogueCount = String(total);
  }
  // Configure only official, verified payment links here. No payment credentials belong in this public file.
  const paymentLinks = window.SSSWET_DONATION_LINKS || {};
  const portfolio = window.SSSWET_RESEARCH_PORTFOLIO || {};
  const currencyByRegion = {
    US:"USD", CA:"CAD", GB:"GBP", CH:"CHF", JP:"JPY", CN:"CNY", IN:"INR", AU:"AUD", NZ:"NZD",
    BR:"BRL", MX:"MXN", SG:"SGD", HK:"HKD", KR:"KRW", ZA:"ZAR", NG:"NGN", KE:"KES",
    SE:"SEK", NO:"NOK", DK:"DKK", PL:"PLN", CZ:"CZK", HU:"HUF", RO:"RON", BG:"BGN",
    TR:"TRY", IL:"ILS", AE:"AED", SA:"SAR", TH:"THB", ID:"IDR", MY:"MYR", PH:"PHP",
    VN:"VND", UA:"UAH", IS:"ISK", FR:"EUR", DE:"EUR", ES:"EUR", IT:"EUR", PT:"EUR",
    NL:"EUR", BE:"EUR", IE:"EUR", AT:"EUR", FI:"EUR", GR:"EUR", LU:"EUR", EE:"EUR",
    LV:"EUR", LT:"EUR", SK:"EUR", SI:"EUR", CY:"EUR", MT:"EUR"
  };
  const rates = { EUR: 1 };
  const modal = document.getElementById("technology-dialog");
  const grid = document.getElementById("technology-grid");
  if (!modal || !grid) return;
  // Render only a small first batch. The catalogue navigator creates subsequent pages on demand.
  grid.replaceChildren();
  const initialBatch = Object.entries(technologies).slice(0, 24);
  const cardFragment = document.createDocumentFragment();
  initialBatch.forEach(([key, item], index) => {
    const card = document.createElement("article");
    card.className = "technology-card";
    const number = document.createElement("span");
    number.className = "technology-number";
    number.textContent = String(index + 1).padStart(3, "0");
    const heading = document.createElement("h3");
    heading.textContent = item.en?.[0] || key;
    const summary = document.createElement("p");
    summary.textContent = item.en?.[1] || "";
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.tech = key;
    button.textContent = "Explore & contribute";
    card.append(number, heading, summary, button);
    cardFragment.append(card);
  });
  grid.append(cardFragment);
  updateCatalogueCount();
  document.getElementById("language")?.addEventListener("change", updateCatalogueCount);
  window.addEventListener("ssswet-language-changed", updateCatalogueCount);

  const title = document.getElementById("technology-dialog-title");
  const description = document.getElementById("technology-dialog-description");
  const amountInput = document.getElementById("donation-amount");
  const currencyLabel = document.getElementById("donation-currency");
  const perOutput = document.getElementById("donation-per");
  const totalOutput = document.getElementById("donation-total");
  const currencyNote = document.getElementById("donation-currency-note");
  const paymentStatus = document.getElementById("donation-payment-status");
  const checkout = document.getElementById("donation-checkout");
  const copyButton = document.getElementById("donation-copy");
  const translations = {
    en: { eyebrow:"FUTURE TECHNOLOGIES · RESEARCH PRIORITIES", title:"Choose a technology to support", intro:"Explore the research directions and open a contribution window for the technology you want to encourage.", disclaimer:"These are research themes, not claims that the technologies exist or are currently achievable. The project will keep exploring, testing and refining ideas in an ongoing effort to make them possible. Contributions fund research and development; they are not a purchase or a guarantee of results. If a technology becomes feasible and a product is actually developed, a future offer and delivery terms will be communicated separately.", explore:"Explore & contribute", dialogEyebrow:"FUND RESEARCH & DEVELOPMENT", amountLabel:"Monthly contribution amount (USD)", repeatLabel:"Number of separate contributions", perContribution:"Monthly contribution", totalLabel:"Annual equivalent", currencyNote:"Choose a monthly amount in USD. PayPal will display the subscription terms before approval.", paymentMissing:"The PayPal subscription is not configured.", paymentReady:"Choose your monthly amount, then approve the recurring subscription securely with PayPal.", checkout:"Continue to PayPal", copySummary:"Copy research contribution summary", paymentDisclaimer:"This is a recurring monthly contribution. The amount selected is billed monthly through PayPal until the subscriber cancels. Contributions support ongoing research and do not purchase an existing product or guarantee a result. Any future product offer and delivery terms will be communicated separately if a technology is developed and becomes available.", invalid:"Enter a monthly amount between USD 1 and USD 100,000.", copied:"Contribution summary copied.", copyError:"Unable to copy automatically. Please select and copy the summary." },
    fr: { eyebrow:"TECHNOLOGIES DU FUTUR · PRIORITÉS DE RECHERCHE", title:"Choisissez une technologie à soutenir", intro:"Découvrez les axes de recherche et ouvrez une fenêtre de contribution pour la technologie que vous souhaitez encourager.", disclaimer:"Ces axes ne signifient pas que les technologies existent ou soient réalisables aujourd'hui. Le projet poursuivra continuellement les recherches, les essais et les améliorations pour tenter de les rendre possibles. Les contributions financent la recherche et le développement ; elles ne constituent pas un achat et ne garantissent aucun résultat. Si une technologie devient réalisable et qu'un produit est effectivement développé, une offre et des conditions de livraison seront communiquées séparément.", explore:"Découvrir et contribuer", dialogEyebrow:"FINANCER LA RECHERCHE ET LE DÉVELOPPEMENT", amountLabel:"Montant mensuel en dollars américains · équivalent en euros", repeatLabel:"Nombre de contributions distinctes", perContribution:"Contribution mensuelle", totalLabel:"Équivalent annuel", currencyNote:"Le montant est facturé en dollars américains. Son équivalent en euros est affiché à titre indicatif selon le taux de change de référence le plus récent. PayPal affichera les conditions avant validation.", paymentMissing:"L’abonnement PayPal n’est pas configuré.", paymentReady:"Choisissez votre montant mensuel, puis approuvez l’abonnement récurrent en toute sécurité avec PayPal.", checkout:"Continuer vers PayPal", copySummary:"Copier le récapitulatif du financement", paymentDisclaimer:"Il s’agit d’une contribution mensuelle récurrente. Le montant choisi est facturé chaque mois par PayPal jusqu’à l’annulation de l’abonnement. Les contributions financent la recherche en cours et ne constituent pas l’achat d’un produit existant ni une garantie de résultat. Toute future offre de produit et de livraison sera communiquée séparément si une technologie est développée et devient disponible.", invalid:"Saisissez un montant mensuel compris entre 1 et 100 000 dollars américains.", copied:"Récapitulatif copié.", copyError:"Copie automatique impossible. Veuillez sélectionner et copier le récapitulatif." },
    ja: { eyebrow:"未来技術・研究の優先分野", title:"支援する技術分野を選択", intro:"研究テーマを確認し、応援したい分野への研究支援を選択できます。", disclaimer:"これらは研究テーマであり、技術の実在や実現可能性を保証するものではありません。寄付は研究開発を支援するもので、製品の購入や成果を保証するものではありません。", explore:"詳細を見る・支援する", dialogEyebrow:"研究開発を支援", amountLabel:"毎月の支援額（米ドル）", repeatLabel:"個別の支援回数", perContribution:"毎月の支援額", totalLabel:"年間換算額", currencyNote:"現地通貨での換算額は参考表示です。実際の請求通貨は米ドルです。", paymentMissing:"PayPalの定期支払いは設定されていません。", paymentReady:"毎月の支援額を選び、PayPalで定期支払いの内容を確認してください。", checkout:"PayPalに進む", copySummary:"支援内容をコピー", paymentDisclaimer:"これは毎月の継続的な研究支援です。解約するまでPayPalを通じて毎月請求されます。既存製品の購入や成果を保証するものではありません。", invalid:"毎月の支援額は米ドルで1ドル以上100,000ドル以下にしてください。", copied:"支援内容をコピーしました。", copyError:"自動コピーできませんでした。内容を選択してコピーしてください。" },
  };
  const copy = () => translations[uiLanguage()] || translations.en;

  function populateTechnologySelectors() {
    const language = copy() === translations.fr ? "fr" : "en";
    const definitions = [
      { selector: '#priority-assessment-form select[name="programme_id"]' },
      { selector: '#research-journal-filter', includeAll: true },
      { selector: '#research-journal-form select[name="technology"]' }
    ];
    for (const definition of definitions) {
      const select = document.querySelector(definition.selector);
      if (!select) continue;
      const previous = select.value;
      select.replaceChildren();
      const optionFragment = document.createDocumentFragment();
      if (definition.includeAll) {
        const all = document.createElement("option");
        all.value = "";
        all.textContent = language === "fr" ? "Toutes les technologies" : "All technologies";
        optionFragment.append(all);
      }
      Object.entries(technologies).forEach(([key, item]) => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = item[language][0];
        optionFragment.append(option);
      });
      select.append(optionFragment);
      if ([...select.options].some(option => option.value === previous)) select.value = previous;
    }
  }
  function applyPaymentLanguage() {
    const fr = copy() === translations.fr;
    const ja = uiLanguage() === "ja";
    const labels = {
      mode: ja ? "お支払い方法" : fr ? "Modalité de paiement" : "Payment plan",
      single: ja ? "一括払い" : fr ? "Paiement unique" : "One-time payment",
      installments: ja ? "米ドル1ドル以上の任意分割払い" : fr ? "Fractionner en échéances volontaires d’au moins 1 dollar américain" : "Split into voluntary instalments of at least USD 1",
      reminderTitle: ja ? "支払いリマインダー" : fr ? "Rappels de paiement" : "Payment reminders",
      reminderDescription: ja ? "初回支払い後、次回分のメール通知を希望できます。自動請求は行われません。" : fr ? "Après le premier paiement, vous pouvez demander des rappels volontaires par e-mail pour la prochaine échéance. Aucun prélèvement automatique ne sera effectué." : "After completing the first payment, you may request voluntary email reminders for the next instalment. No automatic charge will be made.",
      email: ja ? "メールアドレス" : fr ? "Adresse e-mail" : "Email address",
      frequency: ja ? "通知頻度" : fr ? "Fréquence des rappels" : "Reminder frequency",
      weekly: ja ? "毎週" : fr ? "Une fois par semaine" : "Once a week",
      monthly: ja ? "毎月" : fr ? "Une fois par mois" : "Once a month",
      yearly: ja ? "毎年" : fr ? "Une fois par an" : "Once a year",
      confirmation: ja ? "初回支払いが完了したことを確認します。" : fr ? "Je confirme avoir effectué le premier paiement." : "I confirm that I have completed the first payment.",
      save: ja ? "メール通知を申し込む" : fr ? "Demander les rappels par e-mail" : "Request email reminders"
    };
    const set = (id, value) => { const element = document.getElementById(id); if (element) element.textContent = value; };
    set("donation-mode-label", labels.mode); set("donation-mode-single", labels.single); set("donation-mode-installments", labels.installments);
    set("payment-reminder-title", labels.reminderTitle); set("payment-reminder-description", labels.reminderDescription);
    set("payment-reminder-email-label", labels.email); set("payment-reminder-frequency-label", labels.frequency);
    set("payment-reminder-weekly", labels.weekly); set("payment-reminder-monthly", labels.monthly); set("payment-reminder-yearly", labels.yearly);
    set("payment-reminder-confirm-label", labels.confirmation); set("payment-reminder-save-label", labels.save);
  }
  let selectedTechnology = null;
  let currency = "USD";
  let minimumLocal = 1;
  let usdToLocalRate = 1;
  let rateReady = false;
  let exchangeRateDate = "";
  const uiLanguage = () => (document.documentElement.lang || document.getElementById("language")?.value || "en").toLowerCase().split("-")[0];
  const regionByLanguage = { ja:"JP", fr:"FR", de:"DE", es:"ES", it:"IT", pt:"PT", nl:"NL", ko:"KR", zh:"CN", hi:"IN", en:"US" };
  const regionByTimezone = { "Asia/Tokyo":"JP", "Europe/Paris":"FR", "Europe/Berlin":"DE", "Europe/London":"GB", "America/New_York":"US", "America/Los_Angeles":"US", "America/Toronto":"CA", "Asia/Seoul":"KR", "Asia/Shanghai":"CN", "Asia/Kolkata":"IN", "Australia/Sydney":"AU", "Pacific/Auckland":"NZ" };
  const portfolioLabels = {
    en: { stage:"Research stage", goal:"Funding goal", confirmed:"Confirmed contributions", availability:"Availability", prototypeLabel:"Prototype status", unknown:"Not published", notSet:"Not set", planning:"Research planning", literature:"Literature review", feasibility:"Feasibility study", prototype:"Prototype development", validation:"Testing and validation", available:"Available for separate purchase", prototypeYes:"Prototype recorded", prototypeNo:"No prototype recorded", unavailable:"Not available", updated:"Last updated", progress:"Funding progress", manual:"Public figures are updated manually after payment confirmation. PayPal.Me does not synchronize payments with this website." },
    fr: { stage:"Étape de recherche", goal:"Objectif de financement", confirmed:"Contributions confirmées", availability:"Disponibilité", prototypeLabel:"Statut du prototype", unknown:"Non publié", notSet:"Non défini", planning:"Planification de la recherche", literature:"Revue de la littérature", feasibility:"Étude de faisabilité", prototype:"Développement d’un prototype", validation:"Essais et validation", available:"Disponible à l’achat séparément", prototypeYes:"Prototype déclaré", prototypeNo:"Aucun prototype déclaré", unavailable:"Non disponible", updated:"Dernière mise à jour", progress:"Progression du financement", manual:"Les chiffres publics sont actualisés manuellement après confirmation des paiements. PayPal.Me ne synchronise pas les paiements avec ce site." }
  };

  function localeRegion() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    if (regionByTimezone[timezone]) return regionByTimezone[timezone];
    try {
      const explicit = new Intl.Locale(navigator.language || "en").region || "";
      if (explicit) return explicit;
    } catch (_) {}
    return regionByLanguage[uiLanguage()] || "";
  }
  function formatLocal(value) {
    const language = uiLanguage();
    const formatLocale = language === "ja" ? "ja-JP" : language === "fr" ? "fr-FR" : (navigator.language || "en");
    try { return new Intl.NumberFormat(formatLocale, { style:"currency", currency, minimumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2, maximumFractionDigits: currency === "JPY" || currency === "KRW" ? 0 : 2 }).format(value); }
    catch (_) { return value.toFixed(currency === "JPY" || currency === "KRW" ? 0 : 2) + " " + currency; }
  }
  function formatUsd(value, french) {
    const language = uiLanguage();
    const formatLocale = language === "ja" ? "ja-JP" : french ? "fr-FR" : "en-US";
    return new Intl.NumberFormat(formatLocale, {style:"currency",currency:"USD",minimumFractionDigits:2,maximumFractionDigits:2}).format(value);
  }
  function updateAmounts() {
    const amount = Number(amountInput.value);
    const valid = Number.isFinite(amount) && amount >= 1 && amount <= 100000;
    const french = copy() === translations.fr;
    const japanese = uiLanguage() === "ja";
    const monthlyLocal = valid && Number.isFinite(usdToLocalRate) ? " · ≈ " + formatLocal(amount * usdToLocalRate) : valid && currency !== "USD" ? (japanese ? " · 現地通貨換算を取得できません" : french ? " · conversion locale indisponible" : " · local conversion unavailable") : "";
    const annualLocal = valid && Number.isFinite(usdToLocalRate) ? " · ≈ " + formatLocal(amount * 12 * usdToLocalRate) : valid && currency !== "USD" ? (japanese ? " · 現地通貨換算を取得できません" : french ? " · conversion locale indisponible" : " · local conversion unavailable") : "";
    perOutput.textContent = valid ? formatUsd(amount,french) + (japanese ? " / 月" : french ? " / mois" : " / month") + monthlyLocal : "—";
    totalOutput.textContent = valid ? formatUsd(amount*12,french) + (japanese ? " / 年" : french ? " / an" : " / year") + annualLocal : "—";
    currencyLabel.textContent = japanese ? "米ドル / 月 · 現地通貨換算" : french ? "Dollars américains / mois · équivalent en devise locale" : "USD / month · local currency equivalent";
    const configured = Boolean(paymentLinks.PAYPAL_CLIENT_ID && paymentLinks.PAYPAL_SUBSCRIPTION_PLAN_ID);
    paymentStatus.textContent = !valid ? copy().invalid : configured ? copy().paymentReady : copy().paymentMissing;
  }
  async function loadLocalExchangeRate() {
    if (currency === "USD") {
      usdToLocalRate = 1;
      exchangeRateDate = new Date().toISOString().slice(0,10);
    } else {
      try {
        const controller = new AbortController();
        const timeout = window.setTimeout(() => controller.abort(), 12000);
        let response;
        try {
          response = await fetch("https://api.frankfurter.dev/v2/rate/usd/" + encodeURIComponent(currency.toLowerCase()), {
            cache:"no-store", headers:{Accept:"application/json"}, signal:controller.signal
          });
        } finally {
          window.clearTimeout(timeout);
        }
        if (!response.ok) throw new Error("Exchange-rate service returned HTTP " + response.status);
        const data = await response.json();
        const rate = Number(data && data.rate);
        if (!Number.isFinite(rate) || rate <= 0 || data.base?.toUpperCase() !== "USD" || data.quote?.toUpperCase() !== currency) {
          throw new Error("Invalid USD/" + currency + " exchange-rate response");
        }
        usdToLocalRate = rate;
        exchangeRateDate = typeof data.date === "string" ? data.date : "";
      } catch (error) {
        usdToLocalRate = null;
        exchangeRateDate = "";
        console.warn("[SSSWET] USD/" + currency + " conversion unavailable:", error);
      }
    }
    updateAmounts();
    updateCurrencyNote();
  }
  function updateCurrencyNote() {
    if (!currencyNote) return;
    const french = copy() === translations.fr;
    const japanese = uiLanguage() === "ja";
    const dateText = exchangeRateDate ? new Intl.DateTimeFormat(japanese ? "ja-JP" : french ? "fr-FR" : "en", {dateStyle:"medium"}).format(new Date(exchangeRateDate + "T12:00:00Z")) : "";
    const currencyName = new Intl.DisplayNames([japanese ? "ja-JP" : french ? "fr-FR" : "en"], {type:"currency"}).of(currency);
    const fallback = japanese
      ? "支払額は米ドルで請求されます。現地通貨の金額は参考換算であり、実際の請求通貨ではありません。"
      : french
        ? "Le paiement reste facturé en dollars américains. L’équivalent local est indicatif et ne modifie pas la devise réellement débitée."
        : "Payment remains charged in US dollars. The local-currency equivalent is indicative and does not change the actual billing currency.";
    const unavailable = japanese ? "為替換算を取得できません。推定レートは表示しません。" : french ? "La conversion est temporairement indisponible ; aucun taux n’est inventé." : "Currency conversion is temporarily unavailable; no rate is guessed.";
    currencyNote.textContent = fallback + (usdToLocalRate === null ? " " + unavailable : dateText ? " " + (japanese ? "参考レート：" : french ? "Taux de référence du " : "Reference rate dated ") + dateText + " · " + currencyName + "." : "");
  }

  function chooseCurrency() {
    amountInput.min = "1";
    amountInput.max = "100000";
    amountInput.step = "0.01";
    amountInput.value = String(Math.max(1, Math.round((Number(amountInput.value) || 1) * 100) / 100));
    const region = localeRegion();
    currency = currencyByRegion[region] || "USD";
    usdToLocalRate = currency === "USD" ? 1 : null;
    updateCurrencyNote();
    updateAmounts();
  }

  let paypalButtonsRendered = false;
  let paypalSdkPromise = null;
  function loadPayPalSdk() {
    if (window.paypal && window.paypal.Buttons) return Promise.resolve(window.paypal);
    if (paypalSdkPromise) return paypalSdkPromise;
    paypalSdkPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-ssswet-paypal-sdk="true"]');
      if (existing) {
        existing.addEventListener("load", () => resolve(window.paypal), {once:true});
        existing.addEventListener("error", reject, {once:true});
        return;
      }
      const script = document.createElement("script");
      script.src = "https://www.paypal.com/sdk/js?client-id=" + encodeURIComponent(paymentLinks.PAYPAL_CLIENT_ID) + "&vault=true&intent=subscription";
      script.dataset.sdkIntegrationSource = "button-factory";
      script.dataset.ssswetPaypalSdk = "true";
      script.onload = () => window.paypal && window.paypal.Buttons ? resolve(window.paypal) : reject(new Error("PayPal SDK did not initialize."));
      script.onerror = () => reject(new Error("Unable to load PayPal SDK."));
      document.head.appendChild(script);
    });
    return paypalSdkPromise;
  }
  async function renderPayPalSubscriptionButton() {
    const container = document.getElementById("paypal-button-container-P-75A66386EX5825057NLTZHII");
    if (!container || paypalButtonsRendered) return;
    try {
      const paypal = await loadPayPalSdk();
      if (!paypal || !paypal.Buttons) throw new Error("PayPal Buttons are unavailable.");
      paypal.Buttons({
        style: {shape:"pill", color:"gold", layout:"vertical", label:"paypal"},
        createSubscription: function(data, actions) {
          const amount = Number(amountInput.value);
          if (!Number.isFinite(amount) || amount < 1 || amount > 100000) {
            paymentStatus.textContent = copy() === translations.fr ? "Saisissez un montant mensuel d’au moins 1 dollar américain." : "Enter a monthly amount of at least USD 1.";
            return Promise.reject(new Error("Invalid monthly contribution amount."));
          }
          return actions.subscription.create({
            plan_id: paymentLinks.PAYPAL_SUBSCRIPTION_PLAN_ID,
            quantity: String(amount)
          });
        },
        onApprove: function(data) {
          paymentStatus.textContent = copy() === translations.fr
            ? "Abonnement PayPal approuvé. Vous pouvez gérer ou annuler vos paiements récurrents depuis votre compte PayPal. Référence : " + data.subscriptionID
            : "PayPal subscription approved. You can manage or cancel recurring payments from your PayPal account. Reference: " + data.subscriptionID;
        },
        onCancel: function() {
          paymentStatus.textContent = copy() === translations.fr ? "Création de l’abonnement annulée." : "Subscription setup was cancelled.";
        },
        onError: function(error) {
          console.error("[SSSWET] PayPal subscription error:", error);
          paymentStatus.textContent = copy() === translations.fr
            ? "PayPal n’a pas pu créer l’abonnement. Vérifiez que le plan autorise les quantités personnalisées et réessayez."
            : "PayPal could not create the subscription. Check that the plan supports custom quantities, then try again.";
        }
      }).render("#paypal-button-container-P-75A66386EX5825057NLTZHII");
      paypalButtonsRendered = true;
    } catch (error) {
      console.error("[SSSWET] PayPal SDK error:", error);
      paymentStatus.textContent = copy() === translations.fr ? "Impossible de charger PayPal pour le moment. Actualisez la page et réessayez." : "PayPal could not be loaded right now. Refresh the page and try again.";
    }
  }

  function renderPortfolio() {
    const language = copy() === translations.fr ? "fr" : "en";
    const labels = portfolioLabels[language];
    document.querySelectorAll(".technology-card").forEach(card => {
      const button = card.querySelector("button[data-tech]");
      if (!button) return;
      const record = portfolio[button.dataset.tech] || {};
      let panel = card.querySelector(".technology-progress");
      if (!panel) { panel = document.createElement("div"); panel.className = "technology-progress"; card.insertBefore(panel, button); }
      const goalKnown = Number.isFinite(record.funding_goal_eur) && record.funding_goal_eur > 0;
      const totalKnown = Number.isFinite(record.confirmed_contributions_eur) && record.confirmed_contributions_eur >= 0;
      const money = value => new Intl.NumberFormat(language, { style:"currency", currency:"EUR" }).format(value);
      const amount = totalKnown ? money(record.confirmed_contributions_eur) : labels.unknown;
      const goal = goalKnown ? money(record.funding_goal_eur) : labels.notSet;
      const stages = { planning:labels.planning, literature_review:labels.literature, feasibility:labels.feasibility, prototype:labels.prototype, validation:labels.validation, available:labels.available };
      const stage = stages[record.stage] || labels.unknown;
      const percent = goalKnown && totalKnown ? Math.min(100, Math.round(record.confirmed_contributions_eur / record.funding_goal_eur * 100)) : null;
      panel.replaceChildren();
      const lines = [[labels.stage,stage],[labels.confirmed,amount],[labels.goal,goal],[labels.prototypeLabel,record.prototype === true ? labels.prototypeYes : labels.prototypeNo],[labels.availability,record.availability === "available" ? labels.available : labels.unavailable]];
      for (const pair of lines) { const line=document.createElement("div"); line.className="technology-progress-line"; const left=document.createElement("span"); left.textContent=pair[0]; const right=document.createElement("strong"); right.textContent=pair[1]; line.append(left,right); panel.append(line); }
      if (percent !== null) { const track=document.createElement("div"); track.className="technology-progress-track"; const fill=document.createElement("span"); fill.style.width=percent+"%"; track.append(fill); const caption=document.createElement("small"); caption.textContent=labels.progress+" · "+percent+"%"; panel.append(track,caption); }
      if (record.last_updated) { const updated=document.createElement("small"); updated.textContent=labels.updated+" · "+record.last_updated; panel.append(updated); }
    });
    const note=document.getElementById("portfolio-manual-note"); if(note) note.textContent=labels.manual;
  }
  window.SSSWET_RENDER_PORTFOLIO = renderPortfolio;

  function openTechnology(key) {
    const item = technologies[key] || window.SSSWET_TECHNOLOGIES?.[key];
    if (!item) return;
    selectedTechnology = key;
    const selectedLanguage = (document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
    const language = item[selectedLanguage] ? selectedLanguage : (selectedLanguage === "fr" ? "fr" : "en");
    const localized = item[language] || item.en;
    title.textContent = localized[0];
    description.textContent = localized[1];
    const record = portfolio[key] || {};
    const detail = document.getElementById("technology-dialog-progress");
    if (detail) { const labels=portfolioLabels[language==="fr"?"fr":"en"]; const stages={planning:labels.planning,literature_review:labels.literature,feasibility:labels.feasibility,prototype:labels.prototype,validation:labels.validation,available:labels.available}; const money=value=>new Intl.NumberFormat(language,{style:"currency",currency:"EUR"}).format(value); const goal=Number.isFinite(record.funding_goal_eur)&&record.funding_goal_eur>0?money(record.funding_goal_eur):labels.notSet; const total=Number.isFinite(record.confirmed_contributions_eur)&&record.confirmed_contributions_eur>=0?money(record.confirmed_contributions_eur):labels.unknown; detail.textContent=labels.stage+": "+(stages[record.stage]||labels.unknown)+" · "+labels.confirmed+": "+total+" · "+labels.goal+": "+goal; }
    amountInput.value = "1";
    updateAmounts();
    if (typeof modal.showModal === "function") modal.showModal();
    else modal.setAttribute("open", "");
    renderPayPalSubscriptionButton();
  }
  grid.addEventListener("click", event => {
    const button = event.target.closest("button[data-tech]");
    if (button) openTechnology(button.dataset.tech);
  });
  amountInput.addEventListener("input", updateAmounts);
  amountInput.addEventListener("change", updateAmounts);
  document.querySelectorAll("[data-tech-copy]").forEach(element => {
    const key = element.dataset.techCopy;
    if (key === "eyebrow") element.textContent = copy().eyebrow;
    if (key === "title") element.textContent = copy().title;
    if (key === "intro") element.textContent = copy().intro;
    if (key === "disclaimer") element.textContent = copy().disclaimer;
    if (key === "dialogEyebrow") element.textContent = copy().dialogEyebrow;
    if (key === "amountLabel") element.textContent = copy().amountLabel;
    if (key === "repeatLabel") element.textContent = copy().repeatLabel;
    if (key === "perContribution") element.textContent = copy().perContribution;
    if (key === "totalLabel") element.textContent = copy().totalLabel;
    if (key === "checkout") element.textContent = copy().checkout;
    if (key === "copySummary") element.textContent = copy().copySummary;
    if (key === "paymentDisclaimer") element.textContent = copy().paymentDisclaimer;
  });
  document.querySelectorAll(".technology-card").forEach((card, index) => {
    const keys = Object.keys(technologies);
    const button = card.querySelector("button[data-tech]");
    if (button) button.textContent = copy().explore;
    const names = Object.values(technologies);
    if (names[index]) {
      card.querySelector("h3").textContent = names[index][copy() === translations.fr ? "fr" : "en"][0];
      card.querySelector("p").textContent = names[index][copy() === translations.fr ? "fr" : "en"][1];
    }
  });
  currencyNote.textContent = copy().currencyNote;
  applyPaymentLanguage();
  renderPortfolio();
  populateTechnologySelectors();
  chooseCurrency();
  loadLocalExchangeRate();
  window.addEventListener("languagechange", () => window.location.reload());
  document.getElementById("language")?.addEventListener("change", () => {
    const language = copy() === translations.fr ? "fr" : "en";
    updateCatalogueCount();
    document.querySelectorAll("[data-tech-copy]").forEach(element => {
      const key = element.dataset.techCopy;
      const value = copy()[key === "dialogEyebrow" ? "dialogEyebrow" : key];
      if (value) element.textContent = value;
    });
    // The paginated catalogue owns visible card localization.
    if (selectedTechnology) {
      const item = technologies[selectedTechnology];
      title.textContent = item[language][0]; description.textContent = item[language][1];
    }
    applyPaymentLanguage();
    updateCurrencyNote();
    renderPortfolio();
    populateTechnologySelectors();
    chooseCurrency();
    loadLocalExchangeRate();
  });
})();
