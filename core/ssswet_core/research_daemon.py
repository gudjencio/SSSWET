"""Continuously run verification-first research passes for the public technology catalogue."""
from __future__ import annotations

import argparse
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from .persistence import SQLiteResearchStore
from .pipeline import ResearchPipeline
from .providers import MultiSourceLiteratureProvider
from .social_research import MultiSourceResearchProvider
from .apps_script_relay import AppsScriptSuccessRelay

TECHNOLOGY_OBJECTIVES = [
    ("cellular", "Cellular enhancement and safe regenerative biology"),
    ("longevity", "Healthy longevity, prevention and cellular maintenance"),
    ("armor", "Advanced protective suits, materials, ergonomics and human safety"),
    ("jetpack", "Personal propulsion, energy efficiency and controlled mobility"),
    ("translator", "Human-alien translation and uncertainty-aware communication"),
    ("spacetime", "Space-warping physics, spacetime geometry and mathematical consistency"),
    ("timetravel", "Time travel, causality, relativity and theoretical temporal models"),
    ("cleanenergy", "Clean energy systems and scalable low-carbon generation"),
    ("energyStorage", "Advanced energy storage, safer batteries and long-duration storage"),
    ("water", "Clean water purification and low-energy desalination"),
    ("foodSystems", "Sustainable food systems, resilient crops and food preservation"),
    ("climate", "Climate adaptation, heat resilience and flood preparedness"),
    ("biodiversity", "Biodiversity protection, habitat connectivity and conservation measurement"),
    ("wildlife", "Wildlife protection, ethical tracking and rescue support"),
    ("oceans", "Ocean observation, marine pollution reduction and ecosystem restoration"),
    ("reforestation", "Reforestation, habitat restoration and ecological corridors"),
    ("agriculture", "Regenerative agriculture, soil health and biodiversity-friendly farming"),
    ("circularEconomy", "Circular economy, repairability and safer material recovery"),
    ("airQuality", "Clean air sensing, filtration and emissions monitoring"),
    ("mobility", "Sustainable mobility, safer cycling and efficient low-emission logistics"),
    ("accessibility", "Assistive and accessibility technology for inclusive independent living"),
    ("disasterResilience", "Disaster prevention, early warning and resilient response systems"),
    ("publicHealth", "Public health prevention, accessible diagnostics and community resilience"),
    ("sanitation", "Safe sanitation, wastewater treatment and water reuse"),
    ("education", "Open science, scientific literacy and accessible research education"),
    ("animalHealth", "Animal health, welfare, non-invasive diagnostics and veterinary access"),
    ("materials", "Sustainable, recyclable and safer non-toxic materials"),
    ("carbonMonitoring", "Carbon and ecosystem monitoring with transparent measurement"),
    ("pollinators", "Pollinator protection, habitat mapping and exposure reduction"),
    ("artificialGravity", "Artificial gravity, inertial management and safe theoretical models"),
    ("medicalNanotechnology", "Medical nanotechnology for diagnostics, monitoring and future therapies"),
    ("atmosphericRestoration", "Atmospheric restoration, pollution reduction and resilient air-quality systems"),
    ("neurointerfaces", "Non-invasive brain-computer interfaces, accessibility, signal quality and neural-data privacy"),
    ("quantumNetworks", "Experimental quantum communication networks, quantum key distribution and physical limits"),
    ("fusionEnergy", "Fusion-energy research, materials, confinement, thermal management and energy-system constraints"),
    ("spaceLifeSupport", "Closed-loop space life-support, air and water recycling, food production and habitat resilience"),
    ("autonomousLabs", "Autonomous research laboratories, automated measurement, traceability and human protocol validation"),
    ("roboticsExoskeletons", "Assistive robotics, exoskeleton ergonomics, mobility and human-machine safety"),
    ("planetaryMonitoring", "Planetary monitoring, astronomical detection, orbital tracking and asteroid-risk assessment"),
    ("advancedComputing", "Advanced computing and scientific AI, interpretability, reproducibility and model limitations"),
    ("blackHoleObservation", "Black-hole astrophysics, observation methods and relativistic evidence"),
    ("blackHoleProbeSystems", "Conceptual black-hole exploration probes, remote sensing and mission limits"),
    ("blackHoleResilientVehicles", "Theoretical spacecraft resilience limits in extreme gravitational fields"),
    ("eventHorizonImaging", "Event-horizon imaging, interferometry and multi-messenger astronomy"),
    ("gravitationalWaveNavigation", "Gravitational-wave detection, source localization and navigation limits"),
    ("relativisticSpacecraft", "Relativistic spacecraft mission models, radiation and communication constraints"),
    ("deepSpaceRadiationShelters", "Deep-space crew radiation shelter concepts and exposure reduction"),
    ("cosmicRayShielding", "Cosmic-ray exposure measurement and shielding trade-offs"),
    ("nuclearBlastResilience", "Civilian nuclear-blast protection, shelter performance and structural resilience"),
    ("radiationProtection", "Radiation protection, shielding materials and exposure reduction"),
    ("radiationDosimetryNetworks", "Calibrated radiation dosimetry networks and exposure mapping"),
    ("nuclearFalloutDecontamination", "Radioactive fallout detection, civil decontamination and waste safeguards"),
    ("electromagneticPulseResilience", "Civil infrastructure resilience to electromagnetic disturbances"),
    ("extremeThermalProtection", "Extreme-heat protection, thermal insulation and fire-safe materials"),
    ("antimatterResearch", "Fundamental antimatter physics, measurement and containment limits"),
    ("beamedEnergyPropulsion", "Beamed-energy propulsion concepts, safety and energy-transfer efficiency"),
    ("solarSailNavigation", "Solar-sail navigation, trajectory planning and attitude control"),
    ("plasmaPropulsion", "Electric and plasma propulsion performance and mission constraints"),
    ("interstellarProbeArchitecture", "Interstellar probe mission architecture, autonomy and communication limits"),
    ("cryogenicHibernation", "Cryobiology, reversible preservation limits and suspended-animation ethics"),
    ("orbitalManufacturing", "Orbital manufacturing, quality assurance and in-space materials processing"),
    ("lunarResourceSystems", "Lunar geology, in-situ resource use and sustainable mission logistics"),
    ("marsTerraformingAssessment", "Planetary habitability, protection and terraforming feasibility constraints"),
    ("metamaterials", "Advanced metamaterials, engineered responses and measured performance limits"),
    ("selfHealingMaterials", "Self-healing materials, fatigue, repair mechanisms and durability"),
    ("aerogelSystems", "Aerogel insulation, filtration, sensing and scale-up constraints"),
    ("ultraHighTemperatureMaterials", "Ultra-high-temperature ceramics, composites and oxidation resistance"),
    ("smartAdaptiveMaterials", "Smart adaptive materials responding to heat, stress, light or fields"),
    ("transparentCeramics", "Transparent structural ceramics, optical performance and impact behaviour"),
    ("impactAbsorbingMaterials", "Impact-absorbing materials and validated protective performance metrics"),
    ("superconductingGrid", "Superconducting power transmission and grid integration constraints"),
    ("ambientEnergyHarvesting", "Ambient energy harvesting from light, heat, vibration and radio-frequency sources"),
    ("spaceSolarPower", "Space-based solar power, safe transmission and lifecycle assessment"),
    ("zeroCarbonIndustrialHeat", "Low-carbon industrial heat, electrification and thermal storage"),
    ("thermoelectricSystems", "Thermoelectric materials and waste-heat recovery efficiency"),
    ("gridScaleThermalStorage", "Grid-scale thermal energy storage and system safety"),
    ("organRegeneration", "Organ regeneration, tissue engineering and preclinical evidence"),
    ("syntheticBiologyBiosafety", "Responsible synthetic biology, containment and biosafety oversight"),
    ("precisionGeneTherapies", "Precision gene therapy evidence, off-target risks and long-term monitoring"),
    ("bioelectronicMedicine", "Bioelectronic medicine, physiology interfaces and device safety"),
    ("artificialOrgans", "Artificial organ systems, biocompatibility and clinical translation"),
    ("medicalDigitalTwins", "Medical digital twins, privacy and validated clinical modelling"),
    ("swarmRobotics", "Cooperative swarm robotics, distributed coordination and safe oversight"),
    ("embodiedAI", "Embodied AI, grounded perception and physical-world safety"),
    ("neuromorphicComputing", "Neuromorphic computing architectures and energy efficiency"),
    ("quantumSensing", "Quantum sensing, calibration and experimentally measured advantages"),
    ("autonomousDisasterRobots", "Autonomous disaster-response robots for search, mapping and logistics"),
    ("carbonRemoval", "Carbon removal pathways, lifecycle accounting and permanence verification"),
    ("oceanAlkalinityMonitoring", "Ocean alkalinity monitoring, chemistry and ecosystem safeguards"),
    ("geoengineeringAssessment", "Independent climate-intervention risk and governance assessment"),
    ("wildfirePrediction", "Wildfire prediction, uncertainty and community early warning"),
    ("ecosystemDigitalTwins", "Ecosystem digital twins and evidence-led conservation planning"),
    ("photonicComputing", "Photonic computing, optical processing and reproducible benchmarks"),
    ("faultTolerantQuantumComputing", "Quantum error correction, hardware scaling and resource estimates"),
    ("distributedScientificComputing", "Distributed scientific computing, provenance and reproducibility"),
    ("interstellarCommunication", "Interstellar communication signals, long-delay protocols and technosignature searches"),
    ("sensoryAugmentation", "Assistive sensory augmentation and human-factors research"),
    ("adaptiveExosuits", "Adaptive soft exosuits, user safety and mobility assistance"),
    ("closedLoopNeuroprosthetics", "Closed-loop neuroprosthetics, neural interfaces and clinical validation"),
    ("universalTranslationSystems", "Universal translation systems, low-resource languages and uncertainty-aware communication"),
]


def run_pass(
    database: str,
    mailto: str = "",
    relay: AppsScriptSuccessRelay | None = None,
    progress_callback=None,
) -> list[dict]:
    store = SQLiteResearchStore(database)
    provider = MultiSourceResearchProvider(
        literature_provider=MultiSourceLiteratureProvider(mailto=mailto),
    )
    pipeline = ResearchPipeline(provider=provider, store=store)
    completed: list[dict] = []
    cycle_started_at = datetime.now(timezone.utc).isoformat()
    def report(state: dict) -> None:
        if progress_callback:
            progress_callback({
                "worker": "autonomous_research",
                "cycle_started_at": cycle_started_at,
                "total_programmes": len(TECHNOLOGY_OBJECTIVES),
                "completed_programmes": len(completed),
                **state,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
    report({"status": "running", "current_technology": None, "active_agents": []})
    for technology, objective in TECHNOLOGY_OBJECTIVES:
        report({
            "status": "running",
            "current_technology": technology,
            "current_objective": objective,
            "active_agents": [],
            "current_task_id": None,
        })
        try:
            task_id, steps = pipeline.start(
                objective,
                domain=technology,
                progress_callback=lambda state, tech=technology: report({
                    "status": "running",
                    "current_technology": tech,
                    "current_objective": objective,
                    **state,
                }),
            )
            evidence_count = sum(len(step.result.evidence) for step in steps)
            summary = " ".join(
                step.result.summary.strip() for step in steps if step.result.summary.strip()
            )[:500]
            completed.append({
                "technology": technology,
                "task_id": task_id,
                "passes": len(steps),
                "evidence_count": evidence_count,
                "summary": summary or "Research workflow completed; outputs remain subject to independent review.",
            })
            print(f"[SSSWET] {technology}: {task_id} · {len(steps)} research-agent passes")
            report({
                "status": "running",
                "current_technology": technology,
                "current_task_id": task_id,
                "active_agents": [],
                "last_completed_technology": technology,
                "completed_programmes": len(completed),
            })
        except Exception as exc:
            # Failures are logged locally only and are never sent to the email relay.
            print(f"[SSSWET] {technology}: research pass blocked ({type(exc).__name__}: {exc})")
            report({
                "status": "running",
                "current_technology": technology,
                "active_agents": [],
                "last_error": f"{technology}: {type(exc).__name__}",
            })

    report({
        "status": "cycle_completed",
        "current_technology": None,
        "active_agents": [],
        "completed_programmes": len(completed),
        "last_cycle_completed_at": datetime.now(timezone.utc).isoformat(),
    })
    if relay and completed:
        try:
            relay.send_cycle_success(completed)
        except Exception as exc:
            # Notification failures do not invalidate or rerun completed research.
            print(f"[SSSWET] Success notification could not be delivered ({type(exc).__name__}).")
    return completed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run continuous SSSWET technology research locally")
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3")
    parser.add_argument("--interval-hours", type=float, default=1.0)
    parser.add_argument("--mailto", default="")
    parser.add_argument("--relay-url", default=os.environ.get("SSSWET_RELAY_URL", ""))
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.interval_hours <= 0:
        parser.error("--interval-hours must be greater than zero")
    database = str(Path(args.database))
    relay = AppsScriptSuccessRelay(endpoint=args.relay_url)
    if relay.configured:
        print("[SSSWET] Apps Script relay enabled: success notifications only.")
    elif args.relay_url or os.environ.get("SSSWET_RELAY_SECRET"):
        print("[SSSWET] Apps Script relay is incomplete; configure both URL and secret.")
    else:
        print("[SSSWET] Apps Script relay is not configured; email notifications are disabled.")
    worker_store = SQLiteResearchStore(database)

    def publish_worker_state(state: dict) -> None:
        worker_store.save_research_worker_state(state)

    while True:
        run_pass(
            database,
            args.mailto,
            relay if relay.configured else None,
            progress_callback=publish_worker_state,
        )
        if args.once:
            return
        time.sleep(args.interval_hours * 3600)


if __name__ == "__main__":
    main()
