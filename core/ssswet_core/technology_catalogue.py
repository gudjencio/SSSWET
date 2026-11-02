"""Stable catalogue registry derived from the public SSSWET technology taxonomy.

Catalogue registration creates dossiers only; it does not claim that a
technology has been researched, demonstrated, or validated.
"""
from __future__ import annotations

from .technology_dossier import TechnologyDossierRegistry

# Stable identifiers are shared with web/technology-categories.js.
TECHNOLOGY_CATALOGUE = [
    {
        "technology_id": "spacetime",
        "title": "Spacetime",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "timetravel",
        "title": "Timetravel",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "artificialGravity",
        "title": "Artificial Gravity",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "planetaryMonitoring",
        "title": "Planetary Monitoring",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "blackHoleObservation",
        "title": "Black Hole Observation",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "blackHoleProbeSystems",
        "title": "Black Hole Probe Systems",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "blackHoleResilientVehicles",
        "title": "Black Hole Resilient Vehicles",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "eventHorizonImaging",
        "title": "Event Horizon Imaging",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "gravitationalWaveNavigation",
        "title": "Gravitational Wave Navigation",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "relativisticSpacecraft",
        "title": "Relativistic Spacecraft",
        "domain": "space",
        "subcategory": "astrophysics"
    },
    {
        "technology_id": "jetpack",
        "title": "Jetpack",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "antimatterResearch",
        "title": "Antimatter Research",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "beamedEnergyPropulsion",
        "title": "Beamed Energy Propulsion",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "solarSailNavigation",
        "title": "Solar Sail Navigation",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "plasmaPropulsion",
        "title": "Plasma Propulsion",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "interstellarProbeArchitecture",
        "title": "Interstellar Probe Architecture",
        "domain": "space",
        "subcategory": "propulsion"
    },
    {
        "technology_id": "spaceLifeSupport",
        "title": "Space Life Support",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "deepSpaceRadiationShelters",
        "title": "Deep Space Radiation Shelters",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "cosmicRayShielding",
        "title": "Cosmic Ray Shielding",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "cryogenicHibernation",
        "title": "Cryogenic Hibernation",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "orbitalManufacturing",
        "title": "Orbital Manufacturing",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "lunarResourceSystems",
        "title": "Lunar Resource Systems",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "marsTerraformingAssessment",
        "title": "Mars Terraforming Assessment",
        "domain": "space",
        "subcategory": "spaceHabitats"
    },
    {
        "technology_id": "nuclearBlastResilience",
        "title": "Nuclear Blast Resilience",
        "domain": "protection",
        "subcategory": "nuclearProtection"
    },
    {
        "technology_id": "radiationProtection",
        "title": "Radiation Protection",
        "domain": "protection",
        "subcategory": "nuclearProtection"
    },
    {
        "technology_id": "radiationDosimetryNetworks",
        "title": "Radiation Dosimetry Networks",
        "domain": "protection",
        "subcategory": "nuclearProtection"
    },
    {
        "technology_id": "nuclearFalloutDecontamination",
        "title": "Nuclear Fallout Decontamination",
        "domain": "protection",
        "subcategory": "nuclearProtection"
    },
    {
        "technology_id": "electromagneticPulseResilience",
        "title": "Electromagnetic Pulse Resilience",
        "domain": "protection",
        "subcategory": "nuclearProtection"
    },
    {
        "technology_id": "armor",
        "title": "Armor",
        "domain": "protection",
        "subcategory": "protectiveEngineering"
    },
    {
        "technology_id": "disasterResilience",
        "title": "Disaster Resilience",
        "domain": "protection",
        "subcategory": "protectiveEngineering"
    },
    {
        "technology_id": "extremeThermalProtection",
        "title": "Extreme Thermal Protection",
        "domain": "protection",
        "subcategory": "protectiveEngineering"
    },
    {
        "technology_id": "impactAbsorbingMaterials",
        "title": "Impact Absorbing Materials",
        "domain": "protection",
        "subcategory": "protectiveEngineering"
    },
    {
        "technology_id": "cleanenergy",
        "title": "Cleanenergy",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "fusionEnergy",
        "title": "Fusion Energy",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "superconductingGrid",
        "title": "Superconducting Grid",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "ambientEnergyHarvesting",
        "title": "Ambient Energy Harvesting",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "spaceSolarPower",
        "title": "Space Solar Power",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "zeroCarbonIndustrialHeat",
        "title": "Zero Carbon Industrial Heat",
        "domain": "energy",
        "subcategory": "cleanGeneration"
    },
    {
        "technology_id": "energyStorage",
        "title": "Energy Storage",
        "domain": "energy",
        "subcategory": "energyStorage"
    },
    {
        "technology_id": "thermoelectricSystems",
        "title": "Thermoelectric Systems",
        "domain": "energy",
        "subcategory": "energyStorage"
    },
    {
        "technology_id": "gridScaleThermalStorage",
        "title": "Grid Scale Thermal Storage",
        "domain": "energy",
        "subcategory": "energyStorage"
    },
    {
        "technology_id": "materials",
        "title": "Materials",
        "domain": "materials",
        "subcategory": "adaptiveMaterials"
    },
    {
        "technology_id": "metamaterials",
        "title": "Metamaterials",
        "domain": "materials",
        "subcategory": "adaptiveMaterials"
    },
    {
        "technology_id": "selfHealingMaterials",
        "title": "Self Healing Materials",
        "domain": "materials",
        "subcategory": "adaptiveMaterials"
    },
    {
        "technology_id": "aerogelSystems",
        "title": "Aerogel Systems",
        "domain": "materials",
        "subcategory": "adaptiveMaterials"
    },
    {
        "technology_id": "smartAdaptiveMaterials",
        "title": "Smart Adaptive Materials",
        "domain": "materials",
        "subcategory": "adaptiveMaterials"
    },
    {
        "technology_id": "circularEconomy",
        "title": "Circular Economy",
        "domain": "materials",
        "subcategory": "structuralMaterials"
    },
    {
        "technology_id": "ultraHighTemperatureMaterials",
        "title": "Ultra High Temperature Materials",
        "domain": "materials",
        "subcategory": "structuralMaterials"
    },
    {
        "technology_id": "transparentCeramics",
        "title": "Transparent Ceramics",
        "domain": "materials",
        "subcategory": "structuralMaterials"
    },
    {
        "technology_id": "cellular",
        "title": "Cellular",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "longevity",
        "title": "Longevity",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "medicalNanotechnology",
        "title": "Medical Nanotechnology",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "organRegeneration",
        "title": "Organ Regeneration",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "syntheticBiologyBiosafety",
        "title": "Synthetic Biology Biosafety",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "precisionGeneTherapies",
        "title": "Precision Gene Therapies",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "bioelectronicMedicine",
        "title": "Bioelectronic Medicine",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "artificialOrgans",
        "title": "Artificial Organs",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "medicalDigitalTwins",
        "title": "Medical Digital Twins",
        "domain": "life",
        "subcategory": "regenerativeMedicine"
    },
    {
        "technology_id": "neurointerfaces",
        "title": "Neurointerfaces",
        "domain": "life",
        "subcategory": "humanAugmentation"
    },
    {
        "technology_id": "roboticsExoskeletons",
        "title": "Robotics Exoskeletons",
        "domain": "life",
        "subcategory": "humanAugmentation"
    },
    {
        "technology_id": "sensoryAugmentation",
        "title": "Sensory Augmentation",
        "domain": "life",
        "subcategory": "humanAugmentation"
    },
    {
        "technology_id": "adaptiveExosuits",
        "title": "Adaptive Exosuits",
        "domain": "life",
        "subcategory": "humanAugmentation"
    },
    {
        "technology_id": "closedLoopNeuroprosthetics",
        "title": "Closed Loop Neuroprosthetics",
        "domain": "life",
        "subcategory": "humanAugmentation"
    },
    {
        "technology_id": "animalHealth",
        "title": "Animal Health",
        "domain": "life",
        "subcategory": "animalCare"
    },
    {
        "technology_id": "climate",
        "title": "Climate",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "biodiversity",
        "title": "Biodiversity",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "wildlife",
        "title": "Wildlife",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "oceans",
        "title": "Oceans",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "reforestation",
        "title": "Reforestation",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "agriculture",
        "title": "Agriculture",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "carbonMonitoring",
        "title": "Carbon Monitoring",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "pollinators",
        "title": "Pollinators",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "atmosphericRestoration",
        "title": "Atmospheric Restoration",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "carbonRemoval",
        "title": "Carbon Removal",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "oceanAlkalinityMonitoring",
        "title": "Ocean Alkalinity Monitoring",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "geoengineeringAssessment",
        "title": "Geoengineering Assessment",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "ecosystemDigitalTwins",
        "title": "Ecosystem Digital Twins",
        "domain": "environment",
        "subcategory": "ecosystemRestoration"
    },
    {
        "technology_id": "airQuality",
        "title": "Air Quality",
        "domain": "environment",
        "subcategory": "climateResilience"
    },
    {
        "technology_id": "water",
        "title": "Water",
        "domain": "environment",
        "subcategory": "climateResilience"
    },
    {
        "technology_id": "foodSystems",
        "title": "Food Systems",
        "domain": "environment",
        "subcategory": "climateResilience"
    },
    {
        "technology_id": "sanitation",
        "title": "Sanitation",
        "domain": "environment",
        "subcategory": "climateResilience"
    },
    {
        "technology_id": "wildfirePrediction",
        "title": "Wildfire Prediction",
        "domain": "environment",
        "subcategory": "climateResilience"
    },
    {
        "technology_id": "autonomousLabs",
        "title": "Autonomous Labs",
        "domain": "robotics",
        "subcategory": "autonomousResearch"
    },
    {
        "technology_id": "swarmRobotics",
        "title": "Swarm Robotics",
        "domain": "robotics",
        "subcategory": "autonomousResearch"
    },
    {
        "technology_id": "embodiedAI",
        "title": "Embodied A I",
        "domain": "robotics",
        "subcategory": "autonomousResearch"
    },
    {
        "technology_id": "autonomousDisasterRobots",
        "title": "Autonomous Disaster Robots",
        "domain": "robotics",
        "subcategory": "autonomousResearch"
    },
    {
        "technology_id": "mobility",
        "title": "Mobility",
        "domain": "robotics",
        "subcategory": "assistiveRobotics"
    },
    {
        "technology_id": "accessibility",
        "title": "Accessibility",
        "domain": "robotics",
        "subcategory": "assistiveRobotics"
    },
    {
        "technology_id": "advancedComputing",
        "title": "Advanced Computing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "quantumNetworks",
        "title": "Quantum Networks",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "quantumSensing",
        "title": "Quantum Sensing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "neuromorphicComputing",
        "title": "Neuromorphic Computing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "photonicComputing",
        "title": "Photonic Computing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "faultTolerantQuantumComputing",
        "title": "Fault Tolerant Quantum Computing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "distributedScientificComputing",
        "title": "Distributed Scientific Computing",
        "domain": "society",
        "subcategory": "advancedComputing"
    },
    {
        "technology_id": "translator",
        "title": "Translator",
        "domain": "society",
        "subcategory": "communication"
    },
    {
        "technology_id": "interstellarCommunication",
        "title": "Interstellar Communication",
        "domain": "society",
        "subcategory": "communication"
    },
    {
        "technology_id": "universalTranslationSystems",
        "title": "Universal Translation Systems",
        "domain": "society",
        "subcategory": "communication"
    },
    {
        "technology_id": "publicHealth",
        "title": "Public Health",
        "domain": "society",
        "subcategory": "publicKnowledge"
    },
    {
        "technology_id": "education",
        "title": "Education",
        "domain": "society",
        "subcategory": "publicKnowledge"
    }
]


def register_catalogue(registry: TechnologyDossierRegistry, actor_id: str = "catalogue") -> dict:
    """Idempotently create a dossier for every catalogue entry."""
    created = []
    existing = {item["technology_id"] for item in registry.list_dossiers(limit=500)}
    for item in TECHNOLOGY_CATALOGUE:
        if item["technology_id"] in existing:
            continue
        dossier = registry.create(
            technology_id=item["technology_id"],
            title=item["title"],
            domain=item["domain"],
            actor_id=actor_id,
        )
        registry.append_event(
            technology_id=item["technology_id"],
            event_type="research_note",
            payload={
                "catalogue_subcategory": item["subcategory"],
                "catalogue_registration": True,
                "research_status": "not_assessed",
            },
            actor_id=actor_id,
        )
        created.append(item["technology_id"])
    return {
        "catalogue_size": len(TECHNOLOGY_CATALOGUE),
        "created_count": len(created),
        "already_registered_count": len(TECHNOLOGY_CATALOGUE) - len(created),
        "created_ids": created,
        "research_status": "not_assessed",
    }
